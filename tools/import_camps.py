"""One-time importer: camp-finder camps -> open-scout-api camp entities.

Reads the sibling camp-finder repo (data/councils/council-*.json, camps nested per
council) and this repo's data/councils/*.json (for council number -> slug), and writes
data/camps/<id>.json. camp-finder camp ids (state-prefixed slugs) are preserved.

Transforms:
- council number -> `council:<slug>` ref (272 Michigan Crossroads dup -> 780).
- classify camp_type from program_types (day_camp / high_adventure_base / resident_camp).
- operator=council + council ref for local camps; council-999 holds the National bases
  (operator=national, council=null); Northern Tier added as the 4th national HA base.
- DROP description (carries transient 'payment due' text + editorial) and sessions
  (operational data stays in camp-finder / the council site). method=imported.

Includes every council's camps. The 4 original Pacific-Northwest demo councils
{492,606,609,697} now carry real, verified camp-finder data (official council-site
sources), so they are imported like any other council rather than skipped.
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import us_geo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "camps"
TODAY = "2026-07-21"
NATIONAL_COUNCIL = 999
REMAP = {272: 780}  # camp-finder Michigan Crossroads dup -> the number we kept
SUMMARIES = (json.loads((ROOT / "tools" / "camp_summaries.json").read_text("utf-8"))
             if (ROOT / "tools" / "camp_summaries.json").exists() else {})

GEO = (json.loads((ROOT / "tools" / "geocode.json").read_text("utf-8"))
       if (ROOT / "tools" / "geocode.json").exists() else {})


def find_camp_finder() -> Path:
    for p in [ROOT, *ROOT.parents]:
        cand = p.parent / "camp-finder" / "data" / "councils"
        if cand.exists():
            return cand
    raise SystemExit("camp-finder repo not found (expected sibling ../camp-finder)")


def council_num_to_slug() -> dict[int, str]:
    out = {}
    for p in (ROOT / "data" / "councils").glob("*.json"):
        if p.name == "_events.json":
            continue
        d = json.loads(p.read_text("utf-8"))
        vs = d["versions"]
        ov = next((v for v in vs if v.get("valid_to") is None), vs[-1])  # current number, not versions[0]
        n = ov.get("bsa_number")
        if n is not None:
            out[n] = d["id"]
    return out


def classify(program_types: list[str]) -> str:
    s = set(program_types)
    if s == {"cub_day"}:
        return "day_camp"
    if s == {"high_adventure"}:
        return "high_adventure_base"
    return "resident_camp"


def write_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def _resolve_coords(c: dict):
    """Return (lat, lon, geo_precision). Source coords are 'exact' when present and inside the
    camp's state box (or the state is non-US and uncheckable). A missing or out-of-state coord
    falls back to the committed city geocode, then the state centroid, both 'approximate'. A
    camp we cannot place at all -> (None, None, None)."""
    lat, lon, st = c.get("lat"), c.get("lon"), c.get("state")
    if lat is not None and lon is not None and (not us_geo.known(st) or us_geo.in_state(st, lat, lon)):
        return lat, lon, "exact"
    bf = GEO.get(c["id"])
    if bf:
        return bf[0], bf[1], "approximate"
    cen = us_geo.state_centroid(st) if us_geo.known(st) else None
    if cen:
        return cen[0], cen[1], "approximate"
    return None, None, None


def version(c: dict, *, camp_type: str, operator: str, council: str | None, conf: float, extra_src=None) -> dict:
    prov = c.get("provenance", {})
    sources = [{"citation": f"camp-finder {c.get('council_id')}/{c['id']} (unofficial community dataset)"}]
    if prov.get("source_url"):
        sources.append({"url": prov["source_url"]})
    if c.get("website_url"):
        sources.append({"url": c["website_url"]})
    if extra_src:
        sources.append(extra_src)
    lat, lon, geo_precision = _resolve_coords(c)
    return {
        "valid_from": None, "valid_to": None,
        "name": c["name"], "camp_type": camp_type, "operator": operator, "council": council,
        "parent": None, "operating_status": c.get("status", "active"),
        "address": c.get("address"), "city": c.get("city"), "state": c.get("state"),
        "lat": lat, "lon": lon, "geo_precision": geo_precision, "website": c.get("website_url"),
        "program_types": c.get("program_types", []), "features": c.get("features", []),
        "summary": SUMMARIES.get(c["id"]),
        "provenance": {"sources": sources, "method": "imported",
                       "verified_at": prov.get("verified_at") or TODAY, "imported_at": TODAY,
                       "confidence": conf,
                       "notes": "Imported from camp-finder; raw description and sessions dropped (operational data stays at the council site). verified_at is camp-finder's own source-confirmation date; imported_at is when open-scout-api ingested it. The evergreen summary is original prose regenerated from that description, excluding dates/fees/schedules. camp_type classified from program_types."},
    }


def compute_parents(items):
    """Derive one-level reservation parents from the camp set (deterministic): a camp is a
    child of another camp in the SAME council when its slug extends that camp's slug
    ('<parent>-...') or its name is 'X at <parent name>'. No external data required."""
    ids_by_c, names_by_c = {}, {}
    for cid, cref, name in items:
        ids_by_c.setdefault(cref, []).append(cid)
        names_by_c.setdefault(cref, {})[cid] = name
    parents = {}
    for cid, cref, name in items:
        if not cref:
            continue
        cands = [a for a in ids_by_c[cref] if a != cid and cid.startswith(a + "-")]
        if cands:
            parents[cid] = max(cands, key=len)
            continue
        m = re.search(r"\bat\s+(.+)$", name)
        if m:
            tgt = re.sub(r"\s+", " ", m.group(1)).strip().lower()
            for a, an in names_by_c[cref].items():
                if a != cid and an.strip().lower() == tgt:
                    parents[cid] = a
                    break
    return parents


def _km(a_lat, a_lon, b_lat, b_lon):
    if None in (a_lat, a_lon, b_lat, b_lon):
        return None
    r = 6371.0
    dlat = math.radians(b_lat - a_lat)
    dlon = math.radians(b_lon - a_lon)
    x = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(a_lat)) * math.cos(math.radians(b_lat)) * math.sin(dlon / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(x))


def _distinct_location(cv: dict, bv: dict) -> bool:
    """True only when both camps are precisely placed ('exact') and more than 5 km apart — a
    genuine sub-camp of a multi-camp reservation, not a program variant of the same property."""
    if cv.get("geo_precision") == "exact" and bv.get("geo_precision") == "exact":
        d = _km(cv.get("lat"), cv.get("lon"), bv.get("lat"), bv.get("lon"))
        return d is not None and d > 5.0
    return False


# Reviewed same-physical-camp splits whose slugs share no prefix (camp-finder program/session
# variants of one property). survivor id -> (name override or None, [absorbed ids]).
CURATED_MERGES = {
    "ca-camp-fiesta-island": (None, ["ca-webelos-and-aol-resident-camp"]),
    "ct-camp-workcoeman-cub-scout-resident-camp": ("Camp Workcoeman", ["ct-camp-workcoeman-cub-scout-day-camp"]),
    "ia-camp-mitigwa-mitigwa-scout-reservation": ("Camp Mitigwa", ["ia-camp-mitigwa-cub-experience-summer-camp"]),
    "il-rhodes-france-scout-reservation": (None, ["il-rfsr-cub-scout-adventure-camp"]),
    "md-camp-potomac-river-base": ("Camp Potomac", ["md-camp-potomac-scouts-at-work-camp"]),
    "mn-parker-scout-reservation-voyageurs-camp-for-new-scouts": ("Parker Scout Reservation", ["mn-parker-scout-reservation-cub-scout-summer-camp"]),
    "nh-camp-carpenter-overnight-camp": ("Camp Carpenter", ["nh-camp-carpenter-half-week-camp"]),
    "nj-john-e-reeves-cub-world-at-alpine-scout-camp": ("Alpine Scout Camp", ["nj-alpine-day-camp"]),
    "wy-yellowstone-anglers-basecamp-full-week": ("Yellowstone Anglers' Basecamp", ["wy-yellowstone-anglers-basecamp-half-week"]),
}

# Curated reservation names for co-located distinct camps, verified against council sites/addresses.
# id -> (name, [member camp ids]). A reservation may span more than one coordinate point (e.g.
# Goshen); listing its members here unifies those points into one named reservation.
RESERVATIONS = {
    "va-goshen-scout-reservation": ("Goshen Scout Reservation",
        ["va-camp-bowman", "va-camp-marriott", "va-camp-pmi", "va-lenhoksin-high-adventure",
         "va-camp-olmsted", "va-camp-ross"]),
    "al-warner-scout-reservation": ("Warner Scout Reservation",
        ["al-camp-tukabatchee", "al-camp-dexter-c-hobbs-cub-scout-adventure-camp"]),
    "co-peaceful-valley-scout-ranch": ("Peaceful Valley Scout Ranch",
        ["co-camp-cortlandt-dietler", "co-camp-cris-dobbins", "co-magness-adventure-camp"]),
    "co-ben-delatour-scout-ranch": ("Ben Delatour Scout Ranch",
        ["co-elkhorn-high-adventure-base", "co-jack-nicol-cub-scout-camp"]),
    "mo-beaumont-scout-reservation": ("Beaumont Scout Reservation",
        ["mo-camp-may", "mo-grizzly-day-camp"]),
    "mo-s-f-scout-ranch": ("S-F Scout Ranch",
        ["mo-s-f-ranger-program", "mo-swift-high-adventure-base"]),
    "nh-griswold-scout-reservation": ("Griswold Scout Reservation",
        ["nh-camp-bell", "nh-hidden-valley-scout-camp"]),
    "nj-mount-allamuchy-scout-reservation": ("Mount Allamuchy Scout Reservation",
        ["nj-camp-somers", "nj-camp-wheeler"]),
    "ny-ten-mile-river-scout-camps": ("Ten Mile River Scout Camps",
        ["ny-camp-aquehonga", "ny-camp-keowa"]),
    "pa-heritage-reservation": ("Heritage Reservation",
        ["pa-camp-freedom", "pa-eagle-base-heritage-reservation"]),
    "pa-musser-scout-reservation": ("Musser Scout Reservation",
        ["pa-camp-garrison", "pa-camp-hart"]),
    "va-heart-of-virginia-scout-reservation": ("Heart of Virginia Scout Reservation",
        ["va-camp-t-brady-saunders", "va-cub-and-webelos-adventure-camp"]),
    "wi-tomahawk-scout-reservation": ("Tomahawk Scout Reservation",
        ["wi-discovery-adventure-camp", "wi-tomahawk-scout-camp"]),
}
_MEMBER_RES = {mid: (rid, name) for rid, (name, members) in RESERVATIONS.items() for mid in members}


def _slug(s: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def _reservation_name(names: list[str]) -> str | None:
    """A shared reservation label = the common leading words across ALL co-located camp names
    (a single member's own '... Base/Reservation' name is not the group's name). None if the
    camps share no meaningful prefix (e.g. Goshen's Bowman/Marriott/PMI/Lenhok'sin)."""
    common = []
    for col in zip(*(n.split() for n in names)):
        if len(set(col)) == 1:
            common.append(col[0])
        else:
            break
    phrase = re.sub(r"[\s\-–—:()]+$", "", " ".join(common))   # trailing separators
    phrase = re.sub(r"\s*\(?Camp$", "", phrase)               # trailing "(Camp" / "Camp"
    phrase = re.sub(r"[\s\-–—:()]+$", "", phrase).strip()     # separators re-exposed by the strip
    return phrase if len(phrase) >= 3 and phrase.lower() not in ("camp", "the", "scout") else None


def main() -> None:
    cf = find_camp_finder()
    num2slug = council_num_to_slug()
    OUT.mkdir(parents=True, exist_ok=True)
    n_local = n_natl = 0
    unresolved = []
    built = []   # (id, council_ref, name, version_dict)

    for p in sorted(cf.glob("council-*.json")):
        d = json.loads(p.read_text("utf-8"))
        cnum = d.get("number")
        for c in d.get("camps", []):
            if cnum == NATIONAL_COUNCIL:
                v = version(c, camp_type=classify(c.get("program_types", [])),
                            operator="national", council=None, conf=0.9)
                cref = None
                n_natl += 1
            else:
                slug = num2slug.get(REMAP.get(cnum, cnum))
                if slug is None:
                    unresolved.append((cnum, c["id"]))
                    continue
                cref = f"council:{slug}"
                cf_conf = c.get("provenance", {}).get("confidence", 0.6) or 0.6
                v = version(c, camp_type=classify(c.get("program_types", [])),
                            operator="council", council=cref, conf=min(cf_conf, 0.8))
                n_local += 1
            built.append((c["id"], cref, c["name"], v))

    # Northern Tier — the 4th National HA base, absent from camp-finder.
    nt_v = {
        "valid_from": None, "valid_to": None, "name": "Northern Tier National High Adventure Bases",
        "camp_type": "high_adventure_base", "operator": "national", "council": None, "parent": None,
        "operating_status": "active", "address": None, "city": "Ely", "state": "MN",
        "lat": 47.9418, "lon": -91.7273, "geo_precision": "approximate", "website": "https://www.ntier.org/",
        "program_types": ["high_adventure"], "features": [], "summary": None,
        "provenance": {"sources": [{"url": "https://www.ntier.org/"},
                                   {"url": "https://www.scouting.org/high-adventure/northern-tier/"}],
                       "method": "curated", "verified_at": TODAY, "imported_at": TODAY, "confidence": 0.9,
                       "notes": "National High Adventure base (canoe country, Ely MN + Canada); coordinates approximate (Sommers base)."}}
    built.append(("mn-northern-tier", None, nt_v["name"], nt_v))
    n_natl += 1

    if unresolved:
        raise SystemExit(f"unresolved council refs: {unresolved}")

    # A slug/name "child" of a base camp is a program or session variant of the SAME physical
    # property unless both are precisely placed and genuinely far apart (a real sub-camp of a
    # reservation). Merge variants into the base (union programs/features); keep a distinct-
    # location child as a reservation `parent`. Chains (a < a-b < a-b-c) collapse to one terminal
    # survivor so no id is ever orphaned.
    links = compute_parents([(cid, cref, name) for cid, cref, name, _ in built])
    by_id = {cid: v for cid, cref, name, v in built}
    merge_edge: dict[str, str] = {}   # child -> immediate base to merge into
    keep: dict[str, str] = {}         # child -> immediate base, kept as a distinct sub-camp
    for child, base in links.items():
        (keep if _distinct_location(by_id[child], by_id[base]) else merge_edge)[child] = base
    # Reviewed same-camp splits whose slugs share no prefix: merge each absorbed id into its
    # survivor and normalize the survivor's name to the property name.
    for _surv, (_rename, _absorbed) in CURATED_MERGES.items():
        if _rename:
            by_id[_surv]["name"] = _rename
        for _a in _absorbed:
            merge_edge[_a] = _surv

    def terminal(x: str) -> str:
        seen: set[str] = set()
        while x in merge_edge and x not in seen:
            seen.add(x)
            x = merge_edge[x]
        return x

    for child in merge_edge:
        base = terminal(child)
        bv, cv = by_id[base], by_id[child]
        bv["program_types"] = sorted(set(bv["program_types"]) | set(cv["program_types"]))
        bv["features"] = sorted(set(bv["features"]) | set(cv["features"]))
        bv.setdefault("merged_from", []).append(child)
    for child, base in keep.items():   # a kept sub-camp whose base merged must follow to the survivor
        by_id[child]["parent"] = f"camp:{terminal(base)}"

    bad_res = sorted(m for m in _MEMBER_RES if m not in by_id or m in merge_edge)
    if bad_res:
        raise SystemExit(f"RESERVATIONS references unknown or merged camp ids: {bad_res}")

    # A coordinate shared by >=2 surviving camps is a reservation centroid, not an exact fix for
    # any one of them. Relabel it 'approximate' (Type-A duplicates are already merged, so the
    # co-located survivors are distinct camps) and tag them with a shared `reservation` so a
    # consumer can render one pin per reservation that expands to its camps.
    coord_groups: dict[tuple, list] = {}
    for cid, cref, name, v in built:
        if cid in merge_edge or v.get("lat") is None:
            continue
        coord_groups.setdefault((cref, round(v["lat"], 5), round(v["lon"], 5)), []).append((cid, v))
    stacked = 0
    reservations: set[str] = set()
    used_auto: set[str] = set()
    for members in coord_groups.values():
        if len(members) < 2:
            continue
        curated = next((_MEMBER_RES[cid] for cid, _ in members if cid in _MEMBER_RES), None)
        if curated:
            rid, rname = curated
        else:
            rname = _reservation_name([v["name"] for _, v in members])
            rstate = next((v.get("state") for _, v in members if v.get("state")), None)
            rid = _slug(f"{rstate or 'us'}-{rname}") if rname else f"{min(cid for cid, _ in members)}-reservation"
            if rid in used_auto:   # two same-state auto groups deriving one name -> disambiguate
                base, n = rid, 2
                while f"{base}-{n}" in used_auto:
                    n += 1
                rid = f"{base}-{n}"
            used_auto.add(rid)
        reservations.add(rid)
        for _, v in members:
            if v.get("geo_precision") == "exact":
                v["geo_precision"] = "approximate"
                stacked += 1
            v["reservation"] = {"id": rid, "name": rname}
    n_res = len(reservations)

    written = 0
    for cid, cref, name, v in built:
        if cid in merge_edge:
            (OUT / f"{cid}.json").unlink(missing_ok=True)
            continue
        if v.get("merged_from"):
            v["merged_from"] = sorted(v["merged_from"])
            v["camp_type"] = classify(v["program_types"])
        write_json(OUT / f"{cid}.json", {"id": cid, "kind": "camp", "versions": [v], "notes": None})
        written += 1
    aliased = {m for _, _, _, v in built if v.get("merged_from") for m in v["merged_from"]}
    lost = set(merge_edge) - aliased
    if lost:
        raise SystemExit(f"merge dropped listings with no surviving alias: {sorted(lost)}")
    print(f"camps: {written} written; {len(merge_edge)} program/session variants merged; "
          f"{n_res} reservations grouping co-located camps; {stacked} coords relabeled approximate")


if __name__ == "__main__":
    main()
