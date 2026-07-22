"""Enrichment generator: layers historical lineage onto the council dataset.

Input (committed): tools/council_history_facts.json — facts extracted from each
current council's English Wikipedia article (founding year, former names with the
year each ended, formation by merger/rename, later absorptions, states served,
plus the source article title/url). Facts only (dates + council names); no article
prose is reproduced. method=llm_extraction, confidence<1, cross-checked by rule.

This runs AFTER seed_councils_territories.py and MUTATES the existing council
files in place (adds founding valid_from, prior-name versions, states_served) and
APPENDS to data/councils/_events.json. Named predecessor councils become defunct
(retired) council entities one level deep. Idempotent: rebuilds each council's
version timeline from its current open version + the baked facts on every run.

Conservative rules:
  * A former name only becomes its own dated version when its end-year is known
    (version windows must be dated + half-open).
  * A council with prior names (or an explicit 'absorbed'/'renamed' formation, or
    whose formation lists itself) is a CONTINUATION: the *other* councils named in
    its formation are modeled as `absorbed`, not as a new-entity `merged`.
  * A predecessor whose slug matches a still-LIVE council is skipped (never retire
    a current council on an LLM claim); logged to council_history_conflicts.json.
  * Each predecessor is retired exactly once, at the earliest year that references
    it; duplicate/contradictory later merger events are dropped.
  * Existing curated events and existing entity files are never overwritten.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / "tools" / "council_history_facts.json"
CDIR = ROOT / "data" / "councils"
EVENTS = CDIR / "_events.json"
TODAY = "2026-07-21"

US_STATES = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR", "california": "CA",
    "colorado": "CO", "connecticut": "CT", "delaware": "DE", "florida": "FL", "georgia": "GA",
    "hawaii": "HI", "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM", "new york": "NY",
    "north carolina": "NC", "north dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI", "south carolina": "SC",
    "south dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT", "vermont": "VT",
    "virginia": "VA", "washington": "WA", "west virginia": "WV", "wisconsin": "WI",
    "wyoming": "WY", "district of columbia": "DC",
}


def slugify(name: str) -> str:
    s = name.strip()
    s = re.sub(r"\s+Councils?$", "", s, flags=re.I)
    s = s.lower()
    s = s.replace("&", " and ").replace(".", " ").replace("'", "")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def norm_state(x: str):
    x = x.strip()
    if len(x) == 2 and x.isalpha():
        return x.upper()
    return US_STATES.get(x.lower())


def prov(sources, method, conf, notes=None):
    p = {"sources": sources, "method": method, "verified_at": TODAY, "confidence": conf}
    if notes:
        p["notes"] = notes
    return p


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def load_council(cid: str):
    p = CDIR / f"{cid}.json"
    return json.loads(p.read_text("utf-8")) if p.exists() else None


def main() -> None:
    facts = json.loads(FACTS.read_text("utf-8"))

    # index all existing councils; identify which are LIVE (have an open version)
    existing = {}
    live = set()
    for p in CDIR.glob("*.json"):
        if p.name == "_events.json":
            continue
        d = json.loads(p.read_text("utf-8"))
        existing[d["id"]] = d
        if any(v.get("valid_to") is None for v in d["versions"]):
            live.add(d["id"])

    name2live = {}
    for cid in live:
        cur = next(v for v in existing[cid]["versions"] if v.get("valid_to") is None)
        name2live[slugify(cur["name"])] = cid

    def resolve(name: str) -> str:
        return name2live.get(slugify(name), slugify(name))

    WIKI = "Wikipedia"
    # predecessor registry: slug -> {name, year, source_cid, source_url}  (earliest year wins)
    predecessors: dict[str, dict] = {}
    new_events: list[dict] = []
    conflicts: list[dict] = []
    stats = dict(founding=0, renamed=0, merged=0, absorbed=0, states=0, preds=0, skipped_live=0, skipped_noyear=0)

    def register_pred(name, year, src_cid, src_url):
        """Return resolved slug for a predecessor to be retired, or None to skip."""
        sg = resolve(name)
        if sg in live:
            conflicts.append({"survivor": src_cid, "predecessor": name, "slug": sg,
                              "reason": "matches a live council; not retired"})
            stats["skipped_live"] += 1
            return None
        if year is None:
            stats["skipped_noyear"] += 1
            return None
        y = str(year)
        cur = predecessors.get(sg)
        if cur is None or y < cur["year"]:
            predecessors[sg] = {"name": name, "year": y, "src_cid": src_cid, "src_url": src_url}
        return sg

    for cid, r in facts.items():
        d = existing.get(cid)
        if d is None:
            continue
        cur_v = next((v for v in d["versions"] if v.get("valid_to") is None), None)
        if cur_v is None:
            continue  # already-retired entity; skip
        wiki_url = r.get("wiki_url")
        wiki_title = r.get("wiki_title") or cid
        wsrc = [{"url": wiki_url}] if wiki_url else [{"citation": f"Wikipedia: {wiki_title}"}]
        cur_name = cur_v["name"]
        cur_slugs = {slugify(cur_name)} | {slugify(f["name"]) for f in r.get("former_names", [])}

        # --- former-name (rename) versions: only those with a known end year ------
        fns = sorted((f for f in r.get("former_names", []) if f.get("until_year")),
                     key=lambda f: f["until_year"])
        # drop any former name equal to the current name
        fns = [f for f in fns if slugify(f["name"]) != slugify(cur_name)]

        founded = r.get("founded_year")
        form = r.get("formation")
        preds = list(form["predecessors"]) if form and form.get("predecessors") else []
        others = [p for p in preds if slugify(p) not in cur_slugs]
        self_match = len(others) < len(preds)
        is_continuation = bool(fns) or (form and form["type"] in ("absorbed", "renamed")) or self_match

        # states on the current version
        states = []
        for s in r.get("states_served", []):
            ab = norm_state(s)
            if ab and ab not in states:
                states.append(ab)
        if states:
            cur_v["states_served"] = states
            stats["states"] += 1

        # add Wikipedia as a corroborating source on the current version (once)
        if wiki_url and not any(src.get("url") == wiki_url for src in cur_v["provenance"]["sources"]):
            cur_v["provenance"]["sources"].append({"url": wiki_url})

        # --- assemble the version timeline ---------------------------------------
        pure_merged = bool(form) and form["type"] == "merged" and not is_continuation and others
        versions = []
        if pure_merged:
            # genuinely new entity born from a union; single version from the merger year
            yr = form.get("year")
            cur_v["valid_from"] = str(yr) if yr else cur_v.get("valid_from")
            versions = [cur_v]
        else:
            prev_from = str(founded) if founded else None
            for f in fns:
                versions.append({
                    "valid_from": prev_from,
                    "valid_to": str(f["until_year"]),
                    "name": f["name"],
                    "bsa_number": cur_v.get("bsa_number"),
                    "hq_city": None, "hq_state": None, "website": None,
                    "states_served": [],
                    "territory": None,
                    "provenance": prov(wsrc, "llm_extraction", 0.8,
                                       f"Prior name of {cur_name}; changed {f['until_year']}. "
                                       f"Source: {wiki_title} (Wikipedia)."),
                })
                prev_from = str(f["until_year"])
            cur_v["valid_from"] = prev_from if prev_from else (str(founded) if founded else None)
            versions = versions + [cur_v]

        if founded:
            stats["founding"] += 1
        if len(versions) > 1:
            stats["renamed"] += 1
        d["versions"] = versions
        write_json(CDIR / f"{cid}.json", d)

        # --- events ---------------------------------------------------------------
        ev_note = None
        if pure_merged:
            yr = form.get("year")
            parts = [{"ref": f"council:{cid}", "role": "successor"}]
            for nm in others:
                sg = register_pred(nm, yr, cid, wiki_url)
                if sg:
                    parts.append({"ref": f"council:{sg}", "role": "predecessor"})
            if len(parts) > 1:
                new_events.append({
                    "id": f"merge-into-{cid}" + (f"-{yr}" if yr else ""),
                    "type": "merged", "date": str(yr) if yr else None,
                    "participants": parts, "notes": ev_note,
                    "provenance": prov(wsrc, "llm_extraction", 0.8),
                })
        else:
            # continuation absorbing the other formation councils
            yr = form.get("year") if form else None
            for nm in others:
                sg = register_pred(nm, yr, cid, wiki_url)
                if sg:
                    new_events.append({
                        "id": f"absorb-{sg}-into-{cid}",
                        "type": "absorbed", "date": str(yr) if yr else None,
                        "participants": [{"ref": f"council:{sg}", "role": "predecessor"},
                                         {"ref": f"council:{cid}", "role": "continuing"}],
                        "notes": ev_note, "provenance": prov(wsrc, "llm_extraction", 0.8),
                    })

        for la in r.get("later_absorbed", []):
            yr = la.get("year")
            for nm in la.get("councils", []):
                if slugify(nm) in cur_slugs:
                    continue
                sg = register_pred(nm, yr, cid, wiki_url)
                if sg:
                    new_events.append({
                        "id": f"absorb-{sg}-into-{cid}",
                        "type": "absorbed", "date": str(yr) if yr else None,
                        "participants": [{"ref": f"council:{sg}", "role": "predecessor"},
                                         {"ref": f"council:{cid}", "role": "continuing"}],
                        "notes": None, "provenance": prov(wsrc, "llm_extraction", 0.75),
                    })

    # --- write predecessor (defunct) entities; never overwrite existing files ----
    for sg, info in predecessors.items():
        fp = CDIR / f"{sg}.json"
        if fp.exists():
            continue
        wsrc = [{"url": info["src_url"]}] if info["src_url"] else [{"citation": "Wikipedia"}]
        write_json(fp, {
            "$schema": "https://sethmay.github.io/open-scout-api/schema/v1/council.schema.json",
            "id": sg, "kind": "council",
            "versions": [{
                "valid_from": None, "valid_to": info["year"],
                "name": info["name"], "bsa_number": None,
                "hq_city": None, "hq_state": None, "website": None,
                "states_served": [], "territory": None,
                "provenance": prov(wsrc, "llm_extraction", 0.7,
                                   f"Predecessor council recorded via a successor's Wikipedia article; "
                                   f"retired ~{info['year']}. Details (number/HQ) not sourced."),
            }],
            "notes": None,
        })
        stats["preds"] += 1

    # --- merge events: keep existing curated ones; dedupe by id; retire each pred once
    existing_events = json.loads(EVENTS.read_text("utf-8"))["events"] if EVENTS.exists() else []
    by_id = {e["id"]: e for e in existing_events}
    retired = set()  # council slug already retired-as-predecessor by some event
    # existing events already retire some predecessors — record them
    ENDED = {"merged", "absorbed", "split", "superseded"}
    for e in existing_events:
        if e["type"] in ENDED:
            for p in e["participants"]:
                if p["role"] == "predecessor":
                    retired.add(p["ref"])
    kept = list(existing_events)
    for e in sorted(new_events, key=lambda e: (e.get("date") or "9999")):
        if e["id"] in by_id:
            continue
        # ensure no predecessor is retired twice (contradiction) across all events
        preds_here = [p["ref"] for p in e["participants"] if p["role"] == "predecessor"]
        if any(pr in retired for pr in preds_here):
            continue
        for pr in preds_here:
            retired.add(pr)
        by_id[e["id"]] = e
        kept.append(e)
        if e["type"] == "merged":
            stats["merged"] += 1
        elif e["type"] == "absorbed":
            stats["absorbed"] += 1

    write_json(EVENTS, {
        "$schema": "https://sethmay.github.io/open-scout-api/schema/v1/event.schema.json",
        "events": kept,
    })
    write_json(ROOT / ".workbench" / "council-history" / "council_history_conflicts.json", conflicts)

    print("council history enrichment:")
    for k, v in stats.items():
        print(f"  {k}: {v}")
    print(f"  events total now: {len(kept)} (was {len(existing_events)}); live-council conflicts logged: {len(conflicts)}")


if __name__ == "__main__":
    main()
