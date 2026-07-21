"""Build the published static API into dist/ for GitHub Pages.

Layout (served at https://sethmay.github.io/open-scout-api/):
  dist/
    index.html                     landing page
    schema/v1/*.schema.json        copied canonical + published schemas (matches $id)
    v1/
      meta.json                    version, counts, license, disclaimer
      councils/index.json          lightweight listing of all council entities
      councils/<slug>.json         per-entity: canonical entity + folded lifecycle events
      territories/index.json
      territories/<slug>.json
      current/councils.json        denormalized, current-only (open valid_to) councils
      current/territories.json

Canonical data stays normalized in data/; this build denormalizes for consumers.
The build validates its own current/ projections against
schema/v1/published-current.schema.json (fail-fast) and checks referential
integrity of the projected territory refs. Run after validate_data.py.

Usage: python tools/build.py   ->   writes dist/
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMA_DIR = ROOT / "schema" / "v1"
DIST = ROOT / "dist"
BASE_URL = "https://sethmay.github.io/open-scout-api"
LICENSE = "CC-BY-NC-SA-4.0"
DISCLAIMER = ("Unofficial community project. Not affiliated with, endorsed by, or "
              "sponsored by Scouting America. Confirm facts against each council's own site.")


def read_json(p: Path):
    d = json.loads(p.read_text("utf-8"))
    if isinstance(d, dict):
        d.pop("$schema", None)   # editor-only ref on canonical files; dist files reference published schemas
    return d


def write_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def current_version() -> str:
    text = (ROOT / "CHANGELOG.md").read_text("utf-8")
    version = None
    for line in text.splitlines():
        m = re.match(r"##\s+(\d+\.\d+\.\d+)\b", line)
        if m:
            version = m.group(1)
            break
    if version is None:
        raise RuntimeError("no version heading in CHANGELOG.md")
    # Unreleased changes sit above the newest heading as a `PENDING` line until the semver
    # bump commit backfills them; mark the build so the deployed version stays honest during
    # the one-commit lag (self-clears once the bump lands).
    if re.search(r"^-\s+`PENDING`", text, re.M):
        version += "+unreleased"
    return version


def open_version(entity: dict) -> dict | None:
    """The current (valid_to:null) version, or None if the entity is retired."""
    for v in entity.get("versions", []):
        if v.get("valid_to") is None:
            return v
    return None


def load_dataset(name: str) -> tuple[list[dict], list[dict]]:
    d = DATA / name
    entities = [read_json(p) for p in sorted(d.glob("*.json")) if p.name != "_events.json"]
    events = read_json(d / "_events.json")["events"] if (d / "_events.json").exists() else []
    return entities, events


def events_for(ref: str, events: list[dict]) -> list[dict]:
    return [e for e in events if any(p.get("ref") == ref for p in e.get("participants", []))]


def main() -> None:
    version = current_version()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if DIST.exists():
        shutil.rmtree(DIST)

    # schemas (served at /schema/v1/ to match every schema's $id)
    schema_out = DIST / "schema" / "v1"
    schema_out.mkdir(parents=True, exist_ok=True)
    for p in SCHEMA_DIR.glob("*.schema.json"):
        shutil.copyfile(p, schema_out / p.name)

    pub = read_json(SCHEMA_DIR / "published-current.schema.json")
    collection_validator = Draft202012Validator(pub, format_checker=Draft202012Validator.FORMAT_CHECKER)

    councils, cevents = load_dataset("councils")
    territories, tevents = load_dataset("territories")
    merit_badges, mbevents = load_dataset("merit-badges")
    camps, campevents = load_dataset("camps")
    ranks, rankevents = load_dataset("ranks")
    awards, awardevents = load_dataset("awards")
    rs_dir = DATA / "requirement-sets"
    requirement_sets = sorted((read_json(p) for p in rs_dir.glob("*.json")),
                              key=lambda d: d["id"]) if rs_dir.exists() else []
    rs_by_subject: dict[str, list[str]] = {}
    for d in requirement_sets:
        rs_by_subject.setdefault(d["subject"], []).append(d["id"])   # keyed by full ref (kind:slug)

    # --- territories: per-entity + index + current -------------------------
    current_terr_ids: set[str] = set()
    terr_index = []
    current_territories = []
    for e in territories:
        ref = f"territory:{e['id']}"
        write_json(DIST / "v1" / "territories" / f"{e['id']}.json", {**e, "events": events_for(ref, tevents)})
        ov = open_version(e)
        terr_index.append({"id": e["id"], "name": (ov or e["versions"][-1])["name"],
                           "current": ov is not None})
        if ov is not None:
            current_terr_ids.add(e["id"])
            current_territories.append({"id": e["id"], "number": ov.get("number"),
                                        "name": ov["name"], "division_type": ov["division_type"],
                                        "confidence": ov["provenance"]["confidence"]})
    terr_number = {t["id"]: t["number"] for t in current_territories}

    # --- councils: per-entity + index + current ----------------------------
    council_index = []
    current_councils = []
    errs: list[str] = []
    for e in councils:
        ref = f"council:{e['id']}"
        write_json(DIST / "v1" / "councils" / f"{e['id']}.json", {**e, "events": events_for(ref, cevents)})
        ov = open_version(e)
        council_index.append({"id": e["id"], "name": (ov or e["versions"][-1])["name"],
                              "bsa_number": (ov or e["versions"][-1]).get("bsa_number"),
                              "hq_state": (ov or e["versions"][-1]).get("hq_state"),
                              "territory": (ov or e["versions"][-1]).get("territory"),
                              "current": ov is not None})
        if ov is None:
            continue
        terr_ref = ov.get("territory")
        tnum = None
        if terr_ref is not None:
            tslug = terr_ref.split(":", 1)[1]
            if tslug not in current_terr_ids:
                errs.append(f"council {e['id']}: territory {terr_ref} is not a current territory")
            tnum = terr_number.get(tslug)   # canonical number of the referenced territory
        current_councils.append({"id": e["id"], "name": ov["name"], "bsa_number": ov.get("bsa_number"),
                                 "hq_city": ov.get("hq_city"), "hq_state": ov.get("hq_state"),
                                 "website": ov.get("website"), "territory": terr_ref,
                                 "territory_number": tnum, "confidence": ov["provenance"]["confidence"]})

    # --- merit badges: per-entity + index + current ------------------------
    mb_index = []
    current_badges = []
    for e in merit_badges:
        ref = f"merit-badge:{e['id']}"
        write_json(DIST / "v1" / "merit-badges" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, mbevents),
                    "requirement_sets": rs_by_subject.get(f"merit-badge:{e['id']}", [])})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        mb_index.append({"id": e["id"], "name": last["name"],
                         "eagle_required": last["eagle_required"], "current": ov is not None})
        if ov is not None:
            current_badges.append({"id": e["id"], "name": ov["name"],
                                   "eagle_required": ov["eagle_required"], "tags": ov.get("tags", []),
                                   "url": ov.get("url"), "confidence": ov["provenance"]["confidence"]})

    # --- camps: per-entity + index + current -------------------------------
    camp_index = []
    current_camps = []
    for e in camps:
        ref = f"camp:{e['id']}"
        write_json(DIST / "v1" / "camps" / f"{e['id']}.json", {**e, "events": events_for(ref, campevents)})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        camp_index.append({"id": e["id"], "name": last["name"], "camp_type": last["camp_type"],
                           "operator": last["operator"], "council": last.get("council"),
                           "state": last.get("state"), "current": ov is not None})
        if ov is not None:
            current_camps.append({"id": e["id"], "name": ov["name"], "camp_type": ov["camp_type"],
                                  "operator": ov["operator"], "council": ov.get("council"),
                                  "state": ov.get("state"), "city": ov.get("city"),
                                  "lat": ov.get("lat"), "lon": ov.get("lon"), "website": ov.get("website"),
                                  "program_types": ov.get("program_types", []),
                                  "confidence": ov["provenance"]["confidence"]})

    # --- ranks: per-entity + index + current -------------------------------
    rank_index = []
    current_ranks = []
    for e in ranks:
        ref = f"rank:{e['id']}"
        write_json(DIST / "v1" / "ranks" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, rankevents),
                    "requirement_sets": rs_by_subject.get(ref, [])})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        rank_index.append({"id": e["id"], "name": last["name"], "program": last["program"],
                           "order": last["order"], "current": ov is not None})
        if ov is not None:
            current_ranks.append({"id": e["id"], "name": ov["name"], "program": ov["program"],
                                  "order": ov["order"], "url": ov.get("url"),
                                  "confidence": ov["provenance"]["confidence"]})

    # --- awards: per-entity + index + current ------------------------------
    award_index = []
    current_awards = []
    for e in awards:
        ref = f"award:{e['id']}"
        write_json(DIST / "v1" / "awards" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, awardevents),
                    "requirement_sets": rs_by_subject.get(ref, [])})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        award_index.append({"id": e["id"], "name": last["name"], "category": last["category"],
                            "audience": last["audience"], "current": ov is not None})
        if ov is not None:
            current_awards.append({"id": e["id"], "name": ov["name"], "category": ov["category"],
                                   "audience": ov["audience"], "programs": ov.get("programs", []),
                                   "square_knot_no": ov.get("square_knot_no"), "url": ov.get("url"),
                                   "confidence": ov["provenance"]["confidence"]})

    coll = lambda kind, items: {"version": version, "generated_at": now, "kind": kind,
                                "count": len(items), "items": items}
    PUB_CURRENT = "https://sethmay.github.io/open-scout-api/schema/v1/published-current.schema.json"
    cur = lambda kind, items: {"$schema": PUB_CURRENT, **coll(kind, items)}
    current_council_coll = cur("council", current_councils)
    current_terr_coll = cur("territory", current_territories)
    current_badge_coll = cur("merit-badge", current_badges)
    current_camp_coll = cur("camp", current_camps)
    current_rank_coll = cur("rank", current_ranks)
    current_award_coll = cur("award", current_awards)
    # validate the current collections against the published consumer contract (fail-fast)
    for fname, c in [("councils", current_council_coll), ("territories", current_terr_coll),
                     ("merit-badges", current_badge_coll), ("camps", current_camp_coll),
                     ("ranks", current_rank_coll), ("awards", current_award_coll)]:
        errs += [f"current/{fname}.json: {er.json_path}: {er.message}"
                 for er in collection_validator.iter_errors(c)]
    if errs:
        raise SystemExit("build failed:\n  " + "\n  ".join(errs[:50]))

    write_json(DIST / "v1" / "current" / "councils.json", current_council_coll)
    write_json(DIST / "v1" / "current" / "territories.json", current_terr_coll)
    write_json(DIST / "v1" / "current" / "merit-badges.json", current_badge_coll)
    write_json(DIST / "v1" / "councils" / "index.json", coll("council", council_index))
    write_json(DIST / "v1" / "territories" / "index.json", coll("territory", terr_index))
    write_json(DIST / "v1" / "merit-badges" / "index.json", coll("merit-badge", mb_index))
    write_json(DIST / "v1" / "current" / "camps.json", current_camp_coll)
    write_json(DIST / "v1" / "camps" / "index.json", coll("camp", camp_index))
    write_json(DIST / "v1" / "current" / "ranks.json", current_rank_coll)
    write_json(DIST / "v1" / "ranks" / "index.json", coll("rank", rank_index))
    write_json(DIST / "v1" / "current" / "awards.json", current_award_coll)
    write_json(DIST / "v1" / "awards" / "index.json", coll("award", award_index))
    for d in requirement_sets:
        write_json(DIST / "v1" / "requirement-sets" / f"{d['id']}.json", d)
    rs_index = [{"id": d["id"], "subject": d["subject"], "effective_from": d["effective_from"],
                 "effective_to": d.get("effective_to"), "includes_official_text": d["includes_official_text"]}
                for d in requirement_sets]
    current_rs = [{"id": d["id"], "subject": d["subject"], "effective_from": d["effective_from"]}
                  for d in requirement_sets if d.get("effective_to") is None]
    write_json(DIST / "v1" / "requirement-sets" / "index.json", coll("requirement-set", rs_index))
    write_json(DIST / "v1" / "current" / "requirement-sets.json", cur("requirement-set", current_rs))

    write_json(DIST / "v1" / "meta.json", {
        "name": "Open Scout API", "version": version, "generated_at": now,
        "base_url": BASE_URL, "license": LICENSE, "unofficial": True, "disclaimer": DISCLAIMER,
        "schemas": f"{BASE_URL}/schema/v1/",
        "datasets": {
            "councils": {"total": len(councils), "current": len(current_councils)},
            "territories": {"total": len(territories), "current": len(current_territories)},
            "merit-badges": {"total": len(merit_badges), "current": len(current_badges)},
            "requirement-sets": {"total": len(requirement_sets), "current": len(current_rs)},
            "camps": {"total": len(camps), "current": len(current_camps)},
            "ranks": {"total": len(ranks), "current": len(current_ranks)},
            "awards": {"total": len(awards), "current": len(current_awards)},
        },
        "text_rights": ("Merit-badge and rank requirement text is \u00a9 Scouting America, reproduced with "
                        "attribution for non-commercial use and NOT covered by this dataset's CC BY-NC-SA license. See NOTICE.md."),
        "endpoints": ["v1/meta.json", "v1/councils/index.json", "v1/councils/{id}.json",
                      "v1/territories/index.json", "v1/territories/{id}.json",
                      "v1/merit-badges/index.json", "v1/merit-badges/{id}.json",
                      "v1/requirement-sets/index.json", "v1/requirement-sets/{id}.json",
                      "v1/camps/index.json", "v1/camps/{id}.json",
                      "v1/ranks/index.json", "v1/ranks/{id}.json",
                      "v1/awards/index.json", "v1/awards/{id}.json",
                      "v1/current/councils.json", "v1/current/territories.json",
                      "v1/current/merit-badges.json", "v1/current/requirement-sets.json",
                      "v1/current/camps.json", "v1/current/ranks.json", "v1/current/awards.json"],
    })

    (DIST / "index.html").write_text(
        _landing(version, now, len(current_councils), len(current_territories), len(current_badges),
                 len(current_rs), len(current_camps), len(current_ranks), len(current_awards)),
        encoding="utf-8", newline="\n")
    print(f"built dist/ v{version}: {len(councils)} councils, {len(territories)} territories, "
          f"{len(merit_badges)} merit badges, {len(requirement_sets)} requirement sets, "
          f"{len(camps)} camps, {len(ranks)} ranks, {len(awards)} awards")


def _landing(version, now, ncouncils, nterr, nbadges, nrs, ncamps, nranks, nawards) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Open Scout API</title>
<style>
 body{{font:16px/1.6 system-ui,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem;color:#1b2a1b}}
 code{{background:#eef2ee;padding:.1em .35em;border-radius:.25em}}
 a{{color:#2f6b2f}} h1{{margin-bottom:.2em}} .muted{{color:#5a6b5a}}
 li{{margin:.25em 0}}
</style></head><body>
<h1>Open Scout API</h1>
<p class="muted">Open, versioned, machine-readable Scouting America reference data. v{version} &middot; built {now}</p>
<p><strong>Unofficial community project.</strong> Not affiliated with, endorsed by, or sponsored by
Scouting America. Data licensed <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>.</p>
<h2>Datasets</h2>
<p>{ncouncils} current councils across {nterr} Council Service Territories; {ncamps} current camps; {nbadges} current merit badges; {nrs} current requirement sets; {nranks} ranks; {nawards} awards.</p>
<h2>Endpoints</h2>
<ul>
 <li><a href="v1/meta.json"><code>v1/meta.json</code></a> — version, counts, license</li>
 <li><a href="v1/current/councils.json"><code>v1/current/councils.json</code></a> — flat current council list</li>
 <li><a href="v1/current/territories.json"><code>v1/current/territories.json</code></a></li>
 <li><a href="v1/current/merit-badges.json"><code>v1/current/merit-badges.json</code></a> — flat current merit badge list</li>
 <li><a href="v1/councils/index.json"><code>v1/councils/index.json</code></a> — all councils (incl. historical)</li>
 <li><code>v1/councils/&lt;id&gt;.json</code> — one council with its lifecycle events</li>
 <li><a href="v1/territories/index.json"><code>v1/territories/index.json</code></a> · <code>v1/territories/&lt;id&gt;.json</code></li>
 <li><a href="v1/merit-badges/index.json"><code>v1/merit-badges/index.json</code></a> · <code>v1/merit-badges/&lt;id&gt;.json</code></li>
 <li><a href="v1/requirement-sets/index.json"><code>v1/requirement-sets/index.json</code></a> · <code>v1/requirement-sets/&lt;id&gt;.json</code> — requirement trees</li>
 <li><a href="v1/camps/index.json"><code>v1/camps/index.json</code></a> · <code>v1/camps/&lt;id&gt;.json</code> — resident/HA/day/short-term camps</li>
 <li><a href="v1/current/camps.json"><code>v1/current/camps.json</code></a> — flat current camp list</li>
 <li><a href="v1/ranks/index.json"><code>v1/ranks/index.json</code></a> · <code>v1/ranks/&lt;id&gt;.json</code> — Scouts BSA ranks</li>
 <li><a href="v1/awards/index.json"><code>v1/awards/index.json</code></a> · <code>v1/awards/&lt;id&gt;.json</code> — awards &amp; recognitions (knots, honors, training)</li>
 <li><a href="schema/v1/council.schema.json"><code>schema/v1/</code></a> — JSON Schemas</li>
</ul>
<p class="muted">Merit-badge and rank requirement text is © Scouting America, reproduced with attribution for
non-commercial use and not covered by the dataset license (see NOTICE).</p>
<p class="muted">Source &amp; issues: <a href="https://github.com/sethmay/open-scout-api">github.com/sethmay/open-scout-api</a></p>
</body></html>
"""


if __name__ == "__main__":
    main()
