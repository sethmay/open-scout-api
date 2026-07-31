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
# The browser starter is deployed alongside the API so the landing page can link a live demo
# that exercises the real published surface (geo_precision, reservation grouping, the feature
# hierarchy) from a browser. It has no build step, so publishing is a directory copy.
CAMP_MAP = ROOT / "cookbook" / "ts" / "starters" / "camp-map"
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

    PUB_ENTITY = "https://sethmay.github.io/open-scout-api/schema/v1/published-entity.schema.json"
    PUB_META = "https://sethmay.github.io/open-scout-api/schema/v1/published-meta.schema.json"
    pub = read_json(SCHEMA_DIR / "published-current.schema.json")
    collection_validator = Draft202012Validator(pub, format_checker=Draft202012Validator.FORMAT_CHECKER)
    pubidx = read_json(SCHEMA_DIR / "published-index.schema.json")
    index_validator = Draft202012Validator(pubidx, format_checker=Draft202012Validator.FORMAT_CHECKER)
    # Gate: every kind in a published enum must be selected by exactly one allOf item branch, or
    # its items fall through to the permissive base {"type":"object"} and the surface is validated
    # in name only. This is how `training`/`training-requirement` shipped fake-validated before
    # 0.58.0. A missing branch is caught here at build time, not by a consumer hitting a bad item.
    for _label, _sch in (("published-current", pub), ("published-index", pubidx)):
        _enum = set(_sch["properties"]["kind"]["enum"])
        _defs = _sch.get("$defs", {})
        _branched: dict[str, int] = {}
        _hollow: list[str] = []
        for _b in _sch.get("allOf", []):
            _k = (((_b.get("if") or {}).get("properties") or {}).get("kind") or {}).get("const")
            if _k is None:
                continue
            _branched[_k] = _branched.get(_k, 0) + 1
            # existence is not enough: the branch's `then` must actually pin the item shape
            # (then -> items -> items -> $ref) to a closed $def, or a hollowed-out branch would
            # pass this gate while the surface still validated any object.
            _ref = ((((_b.get("then") or {}).get("properties") or {}).get("items") or {})
                    .get("items") or {}).get("$ref")
            _dn = _ref.rsplit("/", 1)[-1] if _ref else None
            if not _dn or _dn not in _defs or _defs[_dn].get("additionalProperties") is not False:
                _hollow.append(_k)
        _missing = sorted(_enum - _branched.keys())
        _dupes = sorted(k for k, n in _branched.items() if n > 1)
        _orphan = sorted(_branched.keys() - _enum)
        if _missing or _dupes or _orphan or _hollow:
            raise SystemExit(
                f"{_label}.schema.json: every kind needs exactly one allOf branch that pins "
                f"items.items.$ref to a closed (additionalProperties:false) $def. "
                f"no branch: {_missing or 'none'}; more than one: {_dupes or 'none'}; "
                f"non-enum kind: {_orphan or 'none'}; branch does not constrain items: {_hollow or 'none'}")
    entity_validator = Draft202012Validator(read_json(SCHEMA_DIR / "published-entity.schema.json"),
                                            format_checker=Draft202012Validator.FORMAT_CHECKER)
    meta_validator = Draft202012Validator(read_json(SCHEMA_DIR / "published-meta.schema.json"),
                                          format_checker=Draft202012Validator.FORMAT_CHECKER)
    alias_validator = Draft202012Validator(read_json(SCHEMA_DIR / "published-aliases.schema.json"),
                                           format_checker=Draft202012Validator.FORMAT_CHECKER)
    errs: list[str] = []

    def write_entity(path: Path, obj: dict) -> None:
        """Stamp the published contract onto a per-entity document, validate, then write.

        The per-entity endpoints are the deep surface (canonical entity + projected events +
        requirement-set ids) and were the last unpinned published promise: renaming `events`
        or emitting an entity with no versions used to be a one-line edit no gate would catch.
        """
        obj = {"$schema": PUB_ENTITY, **obj}
        errs.extend(f"{path.relative_to(DIST).as_posix()}: {er.json_path}: {er.message}"
                    for er in entity_validator.iter_errors(obj))
        write_json(path, obj)

    councils, cevents = load_dataset("councils")
    territories, tevents = load_dataset("territories")
    merit_badges, mbevents = load_dataset("merit-badges")
    camps, campevents = load_dataset("camps")
    ranks, rankevents = load_dataset("ranks")
    awards, awardevents = load_dataset("awards")
    oa_lodges, oalodgeevents = load_dataset("oa-lodges")
    adventures, advevents = load_dataset("adventures")
    positions, posevents = load_dataset("positions")
    training, trainevents = load_dataset("training")
    training_reqs = sorted((read_json(q) for q in (DATA / "training-requirements").glob("*.json")),
                           key=lambda d: d["id"]) if (DATA / "training-requirements").exists() else []
    rs_dir = DATA / "requirement-sets"
    requirement_sets = sorted((read_json(p) for p in rs_dir.glob("*.json")),
                              key=lambda d: d["id"]) if rs_dir.exists() else []
    rs_by_subject: dict[str, list[str]] = {}
    for d in requirement_sets:
        rs_by_subject.setdefault(d["subject"], []).append(d["id"])   # keyed by full ref (kind:slug)
    rank_dir = DATA / "merit-badge-rankings"
    badge_rankings = sorted((read_json(p) for p in rank_dir.glob("*.json")),
                            key=lambda d: d["year"]) if rank_dir.exists() else []

    def _prov(ov):
        p = ov["provenance"]
        # confidence is optional in common.schema.json with `default: 1` — honour that default
        # rather than KeyError'ing on a record that legitimately omits it.
        return {"verified_at": p["verified_at"], "method": p["method"],
                "confidence": p.get("confidence", 1)}

    _TRANSIENT_URL = re.compile(r"20\d\d|scoutingevent\.com")

    def _durable_url(website, council_website):
        # A year-stamped or scoutingevent.com link is a per-season registration deep-link that
        # 404s next year; prefer the council's durable page, but never return nothing.
        if website and not _TRANSIENT_URL.search(website):
            return website
        return council_website or website

    # --- territories: per-entity + index + current -------------------------
    current_terr_ids: set[str] = set()
    terr_index = []
    current_territories = []
    for e in territories:
        ref = f"territory:{e['id']}"
        write_entity(DIST / "v1" / "territories" / f"{e['id']}.json", {**e, "events": events_for(ref, tevents)})
        ov = open_version(e)
        _tv = ov or e["versions"][-1]
        terr_index.append({"id": e["id"], "name": _tv["name"], "number": _tv.get("number"),
                           "division_type": _tv["division_type"], "current": ov is not None})
        if ov is not None:
            current_terr_ids.add(e["id"])
            current_territories.append({"id": e["id"], "number": ov.get("number"),
                                        "name": ov["name"], "division_type": ov["division_type"],
                                        **_prov(ov)})
    terr_number = {t["id"]: t["number"] for t in current_territories}

    # --- councils: per-entity + index + current ----------------------------
    council_index = []
    current_councils = []
    for e in councils:
        ref = f"council:{e['id']}"
        write_entity(DIST / "v1" / "councils" / f"{e['id']}.json", {**e, "events": events_for(ref, cevents)})
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
                                 "territory_number": tnum, **_prov(ov)})

    # --- merit badges: per-entity + index + current ------------------------
    mb_index = []
    current_badges = []
    for e in merit_badges:
        ref = f"merit-badge:{e['id']}"
        write_entity(DIST / "v1" / "merit-badges" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, mbevents),
                    "requirement_sets": rs_by_subject.get(f"merit-badge:{e['id']}", [])})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        mb_index.append({"id": e["id"], "name": last["name"],
                         "eagle_required": last["eagle_required"], "current": ov is not None})
        if ov is not None:
            current_badges.append({"id": e["id"], "name": ov["name"],
                                   "eagle_required": ov["eagle_required"], "tags": ov.get("tags", []),
                                   "description": ov.get("description"),
                                   "url": ov.get("url"), **_prov(ov)})

    council_meta = {}
    for _c in councils:
        _v = open_version(_c) or _c["versions"][-1]
        council_meta[_c["id"]] = {"name": _v["name"], "website": _v.get("website"), "number": _v.get("bsa_number")}

    # --- camps: per-entity + index + current -------------------------------
    camp_index = []
    current_camps = []
    camp_aliases: dict[str, str] = {}
    for e in camps:
        ref = f"camp:{e['id']}"
        write_entity(DIST / "v1" / "camps" / f"{e['id']}.json", {**e, "events": events_for(ref, campevents)})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        for _mid in sorted({m for _v in e["versions"] for m in _v.get("merged_from", [])}):
            camp_aliases[_mid] = e["id"]
        camp_index.append({"id": e["id"], "name": last["name"], "camp_type": last["camp_type"],
                           "operator": last["operator"], "council": last.get("council"),
                           "state": last.get("state"), "current": ov is not None})
        if ov is not None:
            _cslug = ov["council"].split(":", 1)[1] if ov.get("council") else None
            _cm = council_meta.get(_cslug) if _cslug else None
            if ov["provenance"].get("imported_at") is None:
                errs.append(f"camps/{e['id']}.json: current version has no provenance.imported_at; "
                            f"the current projection requires it and the cookbook staleness recipes "
                            f"read it unguarded")
            current_camps.append({"id": e["id"], "name": ov["name"], "camp_type": ov["camp_type"],
                                  "operator": ov["operator"], "operating_status": ov["operating_status"],
                                  "council": ov.get("council"),
                                  "state": ov.get("state"), "city": ov.get("city"),
                                  "lat": ov.get("lat"), "lon": ov.get("lon"),
                                  "geo_precision": ov.get("geo_precision"), "website": ov.get("website"),
                                  "elevation_ft": ov.get("elevation_ft"),
                                  "july_high_f": ov.get("july_high_f"), "july_low_f": ov.get("july_low_f"),
                                  "program_types": ov.get("program_types", []), "summary": ov.get("summary"),
                                  "features": sorted(f["code"] for f in (ov.get("features") or [])),
                                  "features_signature": sorted(f["code"] for f in (ov.get("features") or [])
                                                               if f.get("signature")),
                                  "features_verified_at": ov.get("features_verified_at"),
                                  "features_source_tier": ov.get("features_source_tier"),
                                  "parent": ov.get("parent"), "reservation": ov.get("reservation"),
                                  "council_name": _cm["name"] if _cm else None,
                                  "council_website": _cm["website"] if _cm else None,
                                  "council_number": _cm["number"] if _cm else None,
                                  "url": _durable_url(ov.get("website"), _cm["website"] if _cm else None),
                                  "imported_at": ov["provenance"].get("imported_at"),
                                  **_prov(ov)})
    errs.extend(f"camps/aliases.json: {er.json_path}: {er.message}"
                for er in alias_validator.iter_errors(camp_aliases))
    write_json(DIST / "v1" / "camps" / "aliases.json", camp_aliases)

    # --- ranks: per-entity + index + current -------------------------------
    rank_index = []
    current_ranks = []
    for e in ranks:
        ref = f"rank:{e['id']}"
        write_entity(DIST / "v1" / "ranks" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, rankevents),
                    "requirement_sets": rs_by_subject.get(ref, [])})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        rank_index.append({"id": e["id"], "name": last["name"], "program": last["program"],
                           "order": last["order"], "current": ov is not None})
        if ov is not None:
            current_ranks.append({"id": e["id"], "name": ov["name"], "program": ov["program"],
                                  "order": ov["order"], "url": ov.get("url"),
                                  **_prov(ov)})

    # --- awards: per-entity + index + current ------------------------------
    award_index = []
    current_awards = []
    for e in awards:
        ref = f"award:{e['id']}"
        write_entity(DIST / "v1" / "awards" / f"{e['id']}.json",
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
                                   **_prov(ov)})

    # --- oa-lodges: per-entity + index + current ---------------------------
    lodge_index = []
    current_lodges = []
    for e in oa_lodges:
        ref = f"oa-lodge:{e['id']}"
        write_entity(DIST / "v1" / "oa-lodges" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, oalodgeevents)})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        lodge_index.append({"id": e["id"], "name": last["name"], "council": last.get("council"),
                            "section": last.get("section"), "current": ov is not None})
        if ov is not None:
            current_lodges.append({"id": e["id"], "name": ov["name"], "council": ov.get("council"),
                                   "section": ov.get("section"), "hq_state": ov.get("hq_state"),
                                   "lat": ov.get("lat"), "lon": ov.get("lon"),
                                   **_prov(ov)})

    # --- adventures: per-entity + index + current --------------------------
    adv_index = []
    current_adventures = []
    for e in adventures:
        ref = f"adventure:{e['id']}"
        write_entity(DIST / "v1" / "adventures" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, advevents),
                    "requirement_sets": rs_by_subject.get(ref, [])})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        adv_index.append({"id": e["id"], "name": last["name"], "program": last["program"],
                          "category": last["category"], "current": ov is not None})
        if ov is not None:
            current_adventures.append({"id": e["id"], "name": ov["name"], "program": ov["program"],
                                       "ranks": ov["ranks"], "category": ov["category"],
                                       "area": ov.get("area"),
                                       "url": ov.get("url"), **_prov(ov)})

    # --- positions: per-entity + index + current ---------------------------
    pos_index, current_positions = [], []
    for e in positions:
        ref = f"position:{e['id']}"
        write_entity(DIST / "v1" / "positions" / f"{e['id']}.json",
                   {**e, "events": events_for(ref, posevents)})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        pos_index.append({"id": e["id"], "name": last["name"], "audience": last["audience"],
                          "current": ov is not None})
        if ov is not None:
            current_positions.append({"id": e["id"], "name": ov["name"], "audience": ov["audience"],
                                      "unit_types": ov["unit_types"], **_prov(ov)})

    # --- adult training: course entities + the position-trained requirement rows -------------
    train_index, current_training = [], []
    for e in training:
        ref = f"training:{e['id']}"
        write_entity(DIST / "v1" / "training" / f"{e['id']}.json",
                     {**e, "events": events_for(ref, trainevents)})
        ov = open_version(e)
        last = ov or e["versions"][-1]
        train_index.append({"id": e["id"], "name": last["name"], "code": last.get("code"),
                            "current": ov is not None})
        if ov is not None:
            current_training.append({"id": e["id"], "name": ov["name"], "code": ov.get("code"),
                                     "delivery": ov["delivery"],
                                     "renew_months": ov.get("renew_months"), **_prov(ov)})
    # Requirements are flat documents, not versioned entities: one per chart row, keyed by
    # (position, unit_type). Published whole, plus an index carrying the registration codes,
    # because the code is what a consumer holds from my.scouting and the name is not stable.
    treq_index = []
    for d in training_reqs:
        write_entity(DIST / "v1" / "training-requirements" / f"{d['id']}.json", d)
        treq_index.append({"id": d["id"], "position_name": d["position_name"],
                           "registration_codes": d["registration_codes"],
                           "unit_type": d["unit_type"]})

    coll = lambda kind, items: {"version": version, "generated_at": now, "kind": kind,
                                "count": len(items), "items": items}
    PUB_CURRENT = "https://sethmay.github.io/open-scout-api/schema/v1/published-current.schema.json"
    PUB_INDEX = "https://sethmay.github.io/open-scout-api/schema/v1/published-index.schema.json"
    cur = lambda kind, items: {"$schema": PUB_CURRENT, **coll(kind, items)}
    idx = lambda kind, items: {"$schema": PUB_INDEX, **coll(kind, items)}
    rs_index = [{"id": d["id"], "subject": d["subject"], "effective_from": d["effective_from"],
                 "effective_to": d.get("effective_to"), "includes_official_text": d["includes_official_text"]}
                for d in requirement_sets]
    current_rs = [{"id": d["id"], "subject": d["subject"], "effective_from": d["effective_from"],
                   "includes_official_text": d["includes_official_text"], **_prov(d)}
                  for d in requirement_sets if d.get("effective_to") is None]
    current_council_coll = cur("council", current_councils)
    current_terr_coll = cur("territory", current_territories)
    current_badge_coll = cur("merit-badge", current_badges)
    current_camp_coll = cur("camp", current_camps)
    current_rank_coll = cur("rank", current_ranks)
    current_award_coll = cur("award", current_awards)
    current_lodge_coll = cur("oa-lodge", current_lodges)
    current_rs_coll = cur("requirement-set", current_rs)
    current_adv_coll = cur("adventure", current_adventures)
    current_pos_coll = cur("position", current_positions)
    current_train_coll = cur("training", current_training)
    index_colls = [("councils", idx("council", council_index)),
                   ("territories", idx("territory", terr_index)),
                   ("merit-badges", idx("merit-badge", mb_index)),
                   ("camps", idx("camp", camp_index)),
                   ("ranks", idx("rank", rank_index)),
                   ("awards", idx("award", award_index)),
                   ("oa-lodges", idx("oa-lodge", lodge_index)),
                   ("requirement-sets", idx("requirement-set", rs_index)),
                   ("adventures", idx("adventure", adv_index)),
                   ("positions", idx("position", pos_index)),
                   ("training", idx("training", train_index)),
                   ("training-requirements", idx("training-requirement", treq_index)),
                   ("merit-badge-rankings", idx("merit-badge-ranking",
                       [{"id": d["id"], "year": d["year"], "metric": d["metric"],
                         "complete": d["complete"], "count": len(d["rankings"])}
                        for d in badge_rankings]))]
    # Every published projection is validated against its consumer contract (fail-fast): the
    # current/* denormalized views against published-current, the */index.json listings against
    # published-index. A published surface without a schema is an unpinned promise.
    for fname, c in [("councils", current_council_coll), ("territories", current_terr_coll),
                     ("merit-badges", current_badge_coll), ("camps", current_camp_coll),
                     ("ranks", current_rank_coll), ("awards", current_award_coll),
                     ("oa-lodges", current_lodge_coll), ("requirement-sets", current_rs_coll),
                     ("adventures", current_adv_coll), ("positions", current_pos_coll),
                     ("training", current_train_coll)]:
        errs += [f"current/{fname}.json: {er.json_path}: {er.message}"
                 for er in collection_validator.iter_errors(c)]
    for ds, c in index_colls:
        errs += [f"{ds}/index.json: {er.json_path}: {er.message}"
                 for er in index_validator.iter_errors(c)]
    if errs:
        raise SystemExit("build failed:\n  " + "\n  ".join(errs[:50]))

    write_json(DIST / "v1" / "current" / "councils.json", current_council_coll)
    write_json(DIST / "v1" / "current" / "territories.json", current_terr_coll)
    write_json(DIST / "v1" / "current" / "merit-badges.json", current_badge_coll)
    write_json(DIST / "v1" / "current" / "camps.json", current_camp_coll)
    write_json(DIST / "v1" / "current" / "ranks.json", current_rank_coll)
    write_json(DIST / "v1" / "current" / "awards.json", current_award_coll)
    write_json(DIST / "v1" / "current" / "oa-lodges.json", current_lodge_coll)
    write_json(DIST / "v1" / "current" / "requirement-sets.json", current_rs_coll)
    write_json(DIST / "v1" / "current" / "adventures.json", current_adv_coll)
    write_json(DIST / "v1" / "current" / "positions.json", current_pos_coll)
    write_json(DIST / "v1" / "current" / "training.json", current_train_coll)
    for ds, c in index_colls:
        write_json(DIST / "v1" / ds / "index.json", c)
    for d in requirement_sets:
        write_entity(DIST / "v1" / "requirement-sets" / f"{d['id']}.json", d)
    for d in badge_rankings:
        write_entity(DIST / "v1" / "merit-badge-rankings" / f"{d['id']}.json", d)

    for p in sorted((DATA / "vocab").glob("*.json")):
        write_json(DIST / "v1" / "vocab" / p.name, json.loads(p.read_text("utf-8")))
    vocab_ids = sorted(p.stem for p in (DATA / "vocab").glob("*.json"))

    meta_doc = {
        "$schema": PUB_META,
        "name": "Open Scout API", "version": version, "generated_at": now,
        "base_url": BASE_URL, "license": LICENSE, "unofficial": True, "disclaimer": DISCLAIMER,
        "schemas": f"{BASE_URL}/schema/v1/",
        "datasets": {
            "councils": {"total": len(councils), "current": len(current_councils)},
            "territories": {"total": len(territories), "current": len(current_territories)},
            "merit-badges": {"total": len(merit_badges), "current": len(current_badges)},
            "requirement-sets": {"total": len(requirement_sets), "current": len(current_rs)},
            "merit-badge-rankings": {"total": len(badge_rankings)},
            "camps": {"total": len(camps), "current": len(current_camps), "merged": len(camp_aliases)},
            "ranks": {"total": len(ranks), "current": len(current_ranks)},
            "awards": {"total": len(awards), "current": len(current_awards)},
            "oa-lodges": {"total": len(oa_lodges), "current": len(current_lodges)},
            "adventures": {"total": len(adventures), "current": len(current_adventures)},
            "positions": {"total": len(positions), "current": len(current_positions)},
            "training": {"total": len(training), "current": len(current_training)},
            "training-requirements": {"total": len(training_reqs)},
        },
        "vocab": [f"v1/vocab/{v}.json" for v in vocab_ids],
        "text_rights": ("Merit-badge, rank and Cub adventure requirement text is \u00a9 Scouting America, reproduced with "
                        "attribution for non-commercial use and NOT covered by this dataset's CC BY-NC-SA license. See NOTICE.md."),
        "endpoints": ["v1/meta.json", "v1/councils/index.json", "v1/councils/{id}.json",
                      "v1/territories/index.json", "v1/territories/{id}.json",
                      "v1/merit-badges/index.json", "v1/merit-badges/{id}.json",
                      "v1/requirement-sets/index.json", "v1/requirement-sets/{id}.json",
                      "v1/merit-badge-rankings/index.json", "v1/merit-badge-rankings/{year}.json",
                      "v1/camps/index.json", "v1/camps/{id}.json", "v1/camps/aliases.json",
                      "v1/ranks/index.json", "v1/ranks/{id}.json",
                      "v1/awards/index.json", "v1/awards/{id}.json",
                      "v1/oa-lodges/index.json", "v1/oa-lodges/{id}.json",
                      "v1/current/councils.json", "v1/current/territories.json",
                      "v1/current/merit-badges.json", "v1/current/requirement-sets.json",
                      "v1/current/camps.json", "v1/current/ranks.json", "v1/current/awards.json",
                      "v1/current/oa-lodges.json",
                      "v1/adventures/index.json", "v1/adventures/{id}.json",
                      "v1/current/adventures.json",
                      "v1/positions/index.json", "v1/positions/{id}.json",
                      "v1/current/positions.json",
                      "v1/training/index.json", "v1/training/{id}.json",
                      "v1/current/training.json",
                      "v1/training-requirements/index.json",
                      "v1/training-requirements/{id}.json",
                      *[f"v1/vocab/{v}.json" for v in vocab_ids]],
    }
    errs.extend(f"meta.json: {er.json_path}: {er.message}"
                for er in meta_validator.iter_errors(meta_doc))
    if errs:
        raise SystemExit("build failed:\n  " + "\n  ".join(errs[:50]))
    write_json(DIST / "v1" / "meta.json", meta_doc)

    if CAMP_MAP.is_dir():
        shutil.copytree(CAMP_MAP, DIST / "starters" / "camp-map")

    (DIST / "index.html").write_text(
        _landing(version, now, len(current_councils), len(current_territories), len(current_badges),
                 len(current_rs), len(current_camps), len(current_ranks), len(current_awards),
                 len(current_lodges), len(current_adventures), CAMP_MAP.is_dir()),
        encoding="utf-8", newline="\n")
    print(f"built dist/ v{version}: {len(councils)} councils, {len(territories)} territories, "
          f"{len(merit_badges)} merit badges, {len(requirement_sets)} requirement sets, "
          f"{len(camps)} camps, {len(ranks)} ranks, {len(awards)} awards, {len(oa_lodges)} oa-lodges, "
          f"{len(adventures)} adventures, {len(positions)} positions, "
          f"{len(training)} training courses, {len(training_reqs)} training requirements, "
          f"{len(badge_rankings)} badge-ranking years")


def _landing(version, now, ncouncils, nterr, nbadges, nrs, ncamps, nranks, nawards, nlodges, nadv,
             has_demo=False) -> str:
    repo = "https://github.com/sethmay/open-scout-api"
    demo = (f'<li><a href="starters/camp-map/">Live camp map</a> \u2014 every camp, plotted honestly:'
            f' <code>approximate</code> coordinates are drawn as areas rather than pins, co-located'
            f' camps collapse to one reservation marker, and the feature filter expands a coarse'
            f' code over its hierarchy.</li>\n ' if has_demo else "")
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
<h2>Start here</h2>
<p>The <a href="{repo}/tree/main/cookbook">cookbook</a> is runnable, CI-gated example code in
Python, TypeScript, C#, SQL and shell. Each recipe kills one specific way this data misleads a
consumer who assumes it is a flat snapshot &mdash; because the interesting part is that it is not.</p>
<ul>
 {demo}<li>Feature codes are <strong>hierarchical</strong>: a camp offering kayaking is never tagged
 <code>aquatics</code>, so a filter must expand the coarse code over its children.</li>
 <li><code>eagle_required</code> is <strong>null for historical badges</strong> &mdash; unknown, not
 false. A falsy test quietly reclassifies them.</li>
 <li>Merit badge popularity is <strong>ordinal</strong>: no absolute count is published anywhere, so
 averaging or summing a rank is meaningless.</li>
 <li>An empty <code>features</code> array means nothing without <code>features_verified_at</code>
 beside it &mdash; never surveyed and surveyed-found-nothing are different facts.</li>
 <li>Names, numbers and ownership live in <strong>effective-dated versions</strong>, and mergers and
 renames are <strong>events</strong>; <code>versions[0]</code> is not &ldquo;current&rdquo;.</li>
</ul>
<h2>Datasets</h2>
<p>{ncouncils} current councils across {nterr} Council Service Territories; {ncamps} current camps; {nbadges} current merit badges; {nadv} Cub Scout adventures; {nrs} current requirement sets; {nranks} ranks; {nawards} awards; {nlodges} OA lodges.</p>
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
 <li><a href="v1/current/camps.json"><code>v1/current/camps.json</code></a> — flat current camp list, with program <code>features</code></li>
 <li><a href="v1/ranks/index.json"><code>v1/ranks/index.json</code></a> · <code>v1/ranks/&lt;id&gt;.json</code> — Scouts BSA ranks</li>
 <li><a href="v1/awards/index.json"><code>v1/awards/index.json</code></a> · <code>v1/awards/&lt;id&gt;.json</code> — awards &amp; recognitions (knots, honors, training)</li>
 <li><a href="v1/oa-lodges/index.json"><code>v1/oa-lodges/index.json</code></a> · <code>v1/oa-lodges/&lt;id&gt;.json</code> — Order of the Arrow lodges (by council)</li>
 <li><a href="v1/merit-badge-rankings/index.json"><code>v1/merit-badge-rankings/index.json</code></a> · <code>v1/merit-badge-rankings/&lt;year&gt;.json</code> — merit badge popularity by year (ranks, not counts)</li>
 <li><a href="v1/adventures/index.json"><code>v1/adventures/index.json</code></a> · <code>v1/adventures/&lt;id&gt;.json</code> — Cub Scout adventures (the unit of Cub advancement)</li>
 <li><a href="schema/v1/council.schema.json"><code>schema/v1/</code></a> — JSON Schemas</li>
</ul>
<p class="muted">Merit-badge, rank and Cub adventure requirement text is © Scouting America, reproduced with attribution for
non-commercial use and not covered by the dataset license (see NOTICE).</p>
<p class="muted">Source &amp; issues: <a href="https://github.com/sethmay/open-scout-api">github.com/sethmay/open-scout-api</a></p>
</body></html>
"""


if __name__ == "__main__":
    main()
