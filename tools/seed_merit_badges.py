"""One-time seed generator for the merit-badge catalog.

Input (extraction intermediate, not committed): the factual catalogue table in
the OpenScouting/workbooks repo at
  .workbench/workbooks-main/badges/MANIFEST.md
(name | slug | status | latest rev | versions | requirements URL). That repo's
requirement *text* is Scouting America's property and is NOT copied here — only
the catalogue facts (name/slug/status/URL) plus curated Eagle-required flags and
two sourced lifecycle cases (Citizenship in Society, Computers→Digital Technology).

Output: data/merit-badges/*.json + data/merit-badges/_events.json

Requirement CONTENT (the requirement tree) is a separate later pass under the
summaries-only-until-licensed policy (see TODO.md); this is the catalog layer only.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".workbench" / "workbooks-main" / "badges" / "MANIFEST.md"
OUT = ROOT / "data" / "merit-badges"
TODAY = "2026-07-21"
MANIFEST_CITE = "OpenScouting/workbooks badges/MANIFEST.md (catalogue facts)"
EAGLE_URL = "https://www.scouting.org/skills/merit-badges/eagle-required/"

# Badges that satisfy an Eagle-required slot, INCLUDING listed alternatives (schema
# semantics). 13 slots as of 2026-02-27 (Citizenship in Society removed); the OR-options
# (Emergency Preparedness/Lifesaving, Environmental Science/Sustainability,
# Swimming/Hiking/Cycling) each count. Source: scouting.org eagle-required list.
EAGLE_REQUIRED = {
    "first-aid", "citizenship-in-the-community", "citizenship-in-the-nation",
    "citizenship-in-the-world", "communication", "cooking", "personal-fitness",
    "emergency-preparedness", "lifesaving", "environmental-science", "sustainability",
    "personal-management", "camping", "family-life", "swimming", "hiking", "cycling",
}


def prov(sources, conf, notes=None):
    p = {"sources": sources, "method": "curated", "verified_at": TODAY, "confidence": conf}
    if notes:
        p["notes"] = notes
    return p


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


# Badges whose non-active status the generator handles explicitly (below). Any OTHER
# non-active manifest row must fail loudly rather than be emitted as a current badge.
HANDLED_NONACTIVE = {"citizenship-in-society"}


def parse_manifest() -> list[dict]:
    out = []
    for line in MANIFEST.read_text("utf-8").splitlines():
        # a data row: "| Name | `slug` | status | ... |" — tolerate any later columns
        m = re.match(r"\|\s*(.+?)\s*\|\s*`(.+?)`\s*\|\s*(\w+)\s*\|.*\|\s*(https?://\S+)\s*\|", line)
        if not m or m.group(2) == "Slug":
            continue
        out.append({"name": m.group(1), "slug": m.group(2), "status": m.group(3), "url": m.group(4)})
    if not out:
        raise SystemExit("parse_manifest: no rows parsed — MANIFEST format changed")
    unhandled = [r["slug"] for r in out if r["status"] != "active" and r["slug"] not in HANDLED_NONACTIVE]
    if unhandled:
        raise SystemExit(f"parse_manifest: non-active badges with no lifecycle handling: {unhandled}")
    return out


def catalog_version(name, slug, url, eagle):
    src = [{"citation": MANIFEST_CITE}, {"url": url}]
    if eagle:
        src.append({"url": EAGLE_URL})
    return {"valid_from": None, "valid_to": None, "name": name, "eagle_required": eagle,
            "tags": [], "description": None, "url": url, "provenance": prov(src, 0.9)}


def main() -> None:
    rows = parse_manifest()
    events = []

    for r in rows:
        slug, name, url = r["slug"], r["name"], r["url"]
        if slug == "citizenship-in-society":
            continue  # handled below with full lifecycle
        entity = {"id": slug, "kind": "merit-badge",
                  "versions": [catalog_version(name, slug, url, slug in EAGLE_REQUIRED)],
                  "notes": None}
        write_json(OUT / f"{slug}.json", entity)

    # --- Citizenship in Society: introduced 2021, Eagle-required 2022-07-01,
    #     discontinued 2026-02-27 (Eagle-required went 14 -> 13). ---
    cis_url = "https://www.scouting.org/merit-badges/citizenship-in-society/"
    disc = "https://www.scouting.org/program-updates/citizenship-in-society-merit-badge-discontinuance/"
    write_json(OUT / "citizenship-in-society.json", {
        "id": "citizenship-in-society", "kind": "merit-badge",
        "versions": [
            {"valid_from": "2021", "valid_to": "2022-07-01", "name": "Citizenship in Society",
             "eagle_required": False, "tags": [], "description": None, "url": cis_url,
             "provenance": prov([{"citation": MANIFEST_CITE}, {"url": cis_url}], 0.85,
                                "Introduced 2021 as an elective; intro month approximate.")},
            {"valid_from": "2022-07-01", "valid_to": "2026-02-27", "name": "Citizenship in Society",
             "eagle_required": True, "tags": [], "description": None, "url": cis_url,
             "provenance": prov([{"url": EAGLE_URL}, {"url": disc}], 0.9,
                                "Eagle-required 2022-07-01 until discontinuance 2026-02-27.")},
        ],
        "notes": "Discontinued 2026-02-27; Eagle-required merit badges went from 14 to 13.",
    })
    events.append({
        "id": "discontinue-citizenship-in-society-2026", "type": "discontinued", "date": "2026-02-27",
        "participants": [{"ref": "merit-badge:citizenship-in-society", "role": "subject"}],
        "notes": "Scouting America discontinued the badge effective 2026-02-27; grace period through 2026 for Scouts who had started it.",
        "provenance": prov([{"url": disc}], 0.95),
    })

    # --- Computers -> Digital Technology (Digital Technology replaced Computers, 2014). ---
    write_json(OUT / "computers.json", {
        "id": "computers", "kind": "merit-badge",
        "versions": [
            {"valid_from": None, "valid_to": "2014", "name": "Computers",
             "eagle_required": False, "tags": [], "description": None, "url": None,
             "provenance": prov([{"citation": "Discontinued merit badges (Boy Scouts of America), Wikipedia"}], 0.7,
                                "Historical badge, not in the current catalogue; replaced by Digital Technology. Dates approximate.")},
        ],
        "notes": "Superseded by Digital Technology in 2014.",
    })
    events.append({
        "id": "supersede-computers-by-digital-technology-2014", "type": "superseded", "date": "2014",
        "participants": [{"ref": "merit-badge:computers", "role": "predecessor"},
                         {"ref": "merit-badge:digital-technology", "role": "successor"}],
        "notes": "Digital Technology replaced the Computers merit badge in 2014.",
        "provenance": prov([{"citation": "Discontinued merit badges (Boy Scouts of America), Wikipedia"}], 0.7),
    })

    write_json(OUT / "_events.json", {"events": events})
    n = len(list(OUT.glob("*.json"))) - 1
    print(f"merit-badges: {n} badges ({len(EAGLE_REQUIRED)} Eagle-required, "
          f"1 retired, 1 historical) + _events ({len(events)})")


if __name__ == "__main__":
    main()
