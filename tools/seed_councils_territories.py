"""One-time seed generator for the council + territory datasets.

Inputs (extraction intermediates under .workbench/extraction/, not committed —
derived from the unofficial camp-finder dataset and the proprietary Scouting
America CST map images, neither of which is redistributed here):
  - campfinder-councils.json : {number: {name,state,hq_city,website,platform}}
  - assignment.json          : {territory_number: [council_number,...]}  (from map extraction)

Output: data/councils/*.json, data/councils/_events.json,
        data/territories/*.json, data/territories/_events.json

Council name/HQ/website are seeded from camp-finder (unofficial) with the official
CST map as the authoritative source for territory assignment (and a few observed
name corrections). Founding/rename history beyond what is sourced here is left for
a later pass (councils get a single current version). Territory history (regions ->
NSTs 2021 -> CSTs 2024) is curated from Wikipedia + the maps.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EX = ROOT / ".workbench" / "extraction"
TODAY = "2026-07-21"

# --- resolutions from reconciliation (see session notes / NOTICE.md) -----------
DROP = {272, 800, 999}          # 272 = camp-finder dup of 780; 800 Direct Service & 999 National = non-geographic
DEFUNCT = {30, 41, 302, 405, 694, 695}   # present in camp-finder, absent from 2026 official CST maps
NAME_OVERRIDE = {               # official map name supersedes camp-finder
    303: "Mississippi Riverlands Council",   # camp-finder: "Andrew Jackson Council"
    780: "Michigan Crossroads Council",
}
CF_MAP_DATE = "2026-06"

def slugify(name: str) -> str:
    s = name.strip()
    s = re.sub(r"\s+Councils?$", "", s, flags=re.I)   # drop trailing "Council(s)"
    s = s.lower()
    s = s.replace("&", " and ").replace(".", " ").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s

def prov(sources, method, conf, notes=None):
    p = {"sources": sources, "method": method, "verified_at": TODAY, "confidence": conf}
    if notes:
        p["notes"] = notes
    return p

def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

def main() -> None:
    councils = {int(k): v for k, v in json.loads((EX / "campfinder-councils.json").read_text("utf-8")).items()}
    assignment = {int(k): v for k, v in json.loads((EX / "assignment.json").read_text("utf-8")).items()}
    num_to_terr = {n: t for t, ns in assignment.items() for n in ns}

    in_data = sorted(set(councils) - DROP)
    slug_of: dict[int, str] = {}
    used: dict[str, int] = {}
    for n in in_data:
        name = NAME_OVERRIDE.get(n, councils[n]["name"])
        s = slugify(name)
        if s in used:                      # collision -> disambiguate by number
            s = f"{s}-{n}"
        used[s] = n
        slug_of[n] = s

    # --- councils ------------------------------------------------------------
    cdir = ROOT / "data" / "councils"
    for n in in_data:
        cf = councils[n]
        name = NAME_OVERRIDE.get(n, cf["name"])
        terr = num_to_terr.get(n)
        defunct = n in DEFUNCT
        srcs = [{"citation": f"camp-finder council-{n:03d} (unofficial community dataset)"}]
        if terr is not None:
            srcs.append({"citation": f"Scouting America Council Service Territory {terr} map (production {CF_MAP_DATE})"})
        notes = None
        end = None
        if defunct:
            end = "2026"   # coarse upper bound: first observed absent on 2026 CST maps (exact end date unverified)
            notes = ("Present in camp-finder but absent from the 2026 official CST maps; merged/renamed/discontinued. "
                     "valid_to is a coarse bound (2026 = first observed absent); exact end date and successor "
                     "unverified where no event records them.")
        ver = {
            "valid_from": None, "valid_to": end,
            "name": name,
            "bsa_number": n,
            "hq_city": cf["hq_city"],
            "hq_state": cf["state"],
            "website": cf["website"],
            "states_served": [],           # camp-finder only gives HQ state; true service area not yet sourced
            "territory": (f"territory:cst-{terr}" if terr is not None else None),
            "provenance": prov(srcs, "imported", 0.5 if defunct else 0.8, notes),
        }
        entity = {"id": slug_of[n], "kind": "council", "versions": [ver],
                  "notes": ("Former name per camp-finder: 'Andrew Jackson Council'." if n == 303 else None)}
        write_json(cdir / f"{slug_of[n]}.json", entity)

    # council events (sourced mergers/renames; others discontinued w/ unknown date)
    def cref(n): return f"council:{slug_of[n]}"
    cevents = [
        {"id": "absorb-choctaw-area-into-mississippi-riverlands", "type": "absorbed", "date": None,
         "participants": [{"ref": cref(302), "role": "predecessor"}, {"ref": cref(303), "role": "continuing"}],
         "notes": "camp-finder records councils 302/303 consolidating into Mississippi Riverlands (303). Date unverified.",
         "provenance": prov([{"citation": "camp-finder TODO (302/303 -> Mississippi Riverlands)"}], "imported", 0.5)},
        {"id": "absorb-black-hills-area-into-sioux", "type": "absorbed", "date": None,
         "participants": [{"ref": cref(695), "role": "predecessor"}, {"ref": cref(733), "role": "continuing"}],
         "notes": "camp-finder records Black Hills Area (695) merging into Sioux Council (733). Date unverified.",
         "provenance": prov([{"citation": "camp-finder TODO (695 -> Sioux)"}], "imported", 0.5)},
        {"id": "rename-andrew-jackson-to-mississippi-riverlands", "type": "renamed", "date": None,
         "participants": [{"ref": cref(303), "role": "subject"}],
         "notes": "Council 303 shown as 'Mississippi Riverlands' on 2026 CST maps; camp-finder lists former name 'Andrew Jackson Council'. Date unverified.",
         "provenance": prov([{"citation": f"Scouting America CST map (production {CF_MAP_DATE})"}], "curated", 0.6)},
    ]
    for n in (30, 41, 405, 694):
        cevents.append({
            "id": f"discontinued-{slug_of[n]}", "type": "discontinued", "date": None,
            "participants": [{"ref": cref(n), "role": "subject"}],
            "notes": "Absent from 2026 official CST maps; presumed merged/discontinued. Successor and date unverified.",
            "provenance": prov([{"citation": f"Absent from Scouting America CST maps (production {CF_MAP_DATE})"}], "curated", 0.4),
        })
    write_json(cdir / "_events.json", {"events": cevents})

    # --- territories ---------------------------------------------------------
    tdir = ROOT / "data" / "territories"
    wiki = {"url": "https://en.wikipedia.org/wiki/Council_Service_Territories", "accessed": TODAY}
    mapc = {"citation": f"Scouting America Council Service Territory maps (production {CF_MAP_DATE})"}
    tprov = lambda c=0.85: prov([wiki, mapc], "curated", c)

    surviving = [1, 3, 4, 5, 6, 7, 8, 9, 10, 12, 13, 14, 15, 16]
    merged = [2, 11]
    for N in surviving:
        versions = [
            {"valid_from": "2021", "valid_to": "2024", "name": f"National Service Territory {N}",
             "division_type": "national_service_territory", "number": N, "parent": None,
             "description": None, "provenance": tprov()},
            {"valid_from": "2024", "valid_to": None, "name": f"Council Service Territory {N}",
             "division_type": "council_service_territory", "number": N, "parent": None,
             "description": None, "provenance": tprov()},
        ]
        write_json(tdir / f"cst-{N}.json", {"id": f"cst-{N}", "kind": "territory", "versions": versions, "notes": None})
    for N in merged:
        versions = [
            {"valid_from": "2021", "valid_to": "2024", "name": f"National Service Territory {N}",
             "division_type": "national_service_territory", "number": N, "parent": None,
             "description": None, "provenance": tprov(0.5)},
        ]
        write_json(tdir / f"cst-{N}.json", {"id": f"cst-{N}", "kind": "territory", "versions": versions,
                   "notes": "One of two NSTs merged into adjacent territories in the 2024 CST reorganization (16 NSTs -> 14 CSTs); absent from 2024+ maps. Merge target unverified."})

    regions = [("region-northeast", "Northeast Region"), ("region-central", "Central Region"),
               ("region-southern", "Southern Region"), ("region-western", "Western Region")]
    rprov = prov([{"url": "https://en.wikipedia.org/wiki/Council_Service_Territories", "accessed": TODAY}], "curated", 0.6)
    for slug, name in regions:
        versions = [{"valid_from": None, "valid_to": "2021", "name": name, "division_type": "region",
                     "number": None, "parent": None,
                     "description": "One of BSA's four regions until the 2021 reorganization into 16 National Service Territories.",
                     "provenance": rprov}]
        write_json(tdir / f"{slug}.json", {"id": slug, "kind": "territory", "versions": versions, "notes": None})

    tevents = [
        {"id": "reorganize-2021-regions-to-nst", "type": "reorganized", "date": "2021",
         "participants": [{"ref": f"territory:{s}", "role": "predecessor"} for s, _ in regions]
                         + [{"ref": f"territory:cst-{N}", "role": "successor"} for N in range(1, 17)],
         "notes": "In June 2021 BSA replaced its 4 regions and 27 areas with 16 numbered National Service Territories.",
         "provenance": tprov(0.85)},
        {"id": "rename-2024-nst-to-cst", "type": "renamed", "date": "2024",
         "participants": [{"ref": f"territory:cst-{N}", "role": "subject"} for N in surviving],
         "notes": "In 2024 the National Service Territories were renamed Council Service Territories and several boundaries were updated.",
         "provenance": tprov(0.8)},
        {"id": "discontinue-2024-merged-territories", "type": "discontinued", "date": "2024",
         "participants": [{"ref": f"territory:cst-{N}", "role": "subject"} for N in merged],
         "notes": "In the 2024 reorganization two territories (numbers 2 and 11) were merged into adjacent territories, reducing 16 NSTs to 14 CSTs. Merge targets unverified.",
         "provenance": tprov(0.5)},
    ]
    write_json(tdir / "_events.json", {"events": tevents})

    print(f"councils: {len(in_data)} files + _events ({len(cevents)})")
    print(f"territories: {len(surviving)+len(merged)+len(regions)} files + _events ({len(tevents)})")
    print("sample slugs:", {n: slug_of[n] for n in (303, 780, 695, 733, 492)})

if __name__ == "__main__":
    main()
