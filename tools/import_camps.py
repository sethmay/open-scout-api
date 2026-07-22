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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "camps"
TODAY = "2026-07-21"
NATIONAL_COUNCIL = 999
REMAP = {272: 780}  # camp-finder Michigan Crossroads dup -> the number we kept


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


def version(c: dict, *, camp_type: str, operator: str, council: str | None, conf: float, extra_src=None) -> dict:
    prov = c.get("provenance", {})
    sources = [{"citation": f"camp-finder {c.get('council_id')}/{c['id']} (unofficial community dataset)"}]
    if prov.get("source_url"):
        sources.append({"url": prov["source_url"]})
    if c.get("website_url"):
        sources.append({"url": c["website_url"]})
    if extra_src:
        sources.append(extra_src)
    return {
        "valid_from": None, "valid_to": None,
        "name": c["name"], "camp_type": camp_type, "operator": operator, "council": council,
        "parent": None, "operating_status": c.get("status", "active"),
        "address": c.get("address"), "city": c.get("city"), "state": c.get("state"),
        "lat": c.get("lat"), "lon": c.get("lon"), "website": c.get("website_url"),
        "program_types": c.get("program_types", []), "features": c.get("features", []),
        "provenance": {"sources": sources, "method": "imported", "verified_at": TODAY,
                       "confidence": conf,
                       "notes": "Imported from camp-finder; description/sessions dropped (operational data stays at the council site). camp_type classified from program_types."},
    }


def main() -> None:
    cf = find_camp_finder()
    num2slug = council_num_to_slug()
    OUT.mkdir(parents=True, exist_ok=True)
    n_local = n_natl = 0
    unresolved = []

    for p in sorted(cf.glob("council-*.json")):
        d = json.loads(p.read_text("utf-8"))
        cnum = d.get("number")
        for c in d.get("camps", []):
            if cnum == NATIONAL_COUNCIL:
                ct = classify(c.get("program_types", []))
                v = version(c, camp_type=ct, operator="national", council=None, conf=0.9)
                n_natl += 1
            else:
                slug = num2slug.get(REMAP.get(cnum, cnum))
                if slug is None:
                    unresolved.append((cnum, c["id"]))
                    continue
                cf_conf = c.get("provenance", {}).get("confidence", 0.6) or 0.6
                v = version(c, camp_type=classify(c.get("program_types", [])),
                            operator="council", council=f"council:{slug}", conf=min(cf_conf, 0.8))
                n_local += 1
            write_json(OUT / f"{c['id']}.json", {"id": c["id"], "kind": "camp", "versions": [v], "notes": None})

    # Northern Tier — the 4th National HA base, absent from camp-finder.
    nt = {"id": "mn-northern-tier", "kind": "camp", "versions": [{
        "valid_from": None, "valid_to": None, "name": "Northern Tier National High Adventure Bases",
        "camp_type": "high_adventure_base", "operator": "national", "council": None, "parent": None,
        "operating_status": "active", "address": None, "city": "Ely", "state": "MN",
        "lat": 47.9418, "lon": -91.7273, "website": "https://www.ntier.org/",
        "program_types": ["high_adventure"], "features": [],
        "provenance": {"sources": [{"url": "https://www.ntier.org/"},
                                   {"url": "https://www.scouting.org/high-adventure/northern-tier/"}],
                       "method": "curated", "verified_at": TODAY, "confidence": 0.9,
                       "notes": "National High Adventure base (canoe country, Ely MN + Canada); coordinates approximate (Sommers base)."}}],
        "notes": None}
    write_json(OUT / "mn-northern-tier.json", nt)
    n_natl += 1

    if unresolved:
        raise SystemExit(f"unresolved council refs: {unresolved}")
    print(f"camps: {n_local} council + {n_natl} national = {n_local + n_natl} written")


if __name__ == "__main__":
    main()
