"""Validate the data/ tree: JSON Schema + referential integrity + version windows.

Seed of the CI gate (TODO.md "Pipeline validator"). Exits nonzero on any error.
Checks JSON Schema cannot express:
  - id == filename stem
  - every EntityRef (council.territory, event participants) resolves to an entity
  - version windows are ordered and non-overlapping under half-open [from, to)
Usage: python tools/validate_data.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

from stamp_schema import check_tree
import us_geo

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v1"
DATA = ROOT / "data"

# transitory text that must never appear in an evergreen camp `summary`:
# 4-digit years, dollar amounts, or month names.
_TRANSITORY = re.compile(
    r"\b(18|19|20)\d{2}\b|\$|\b(Jan(uary)?|Feb(ruary)?|Mar(ch)?|Apr(il)?|May|Jun(e)?|"
    r"Jul(y)?|Aug(ust)?|Sep(t|tember)?|Oct(ober)?|Nov(ember)?|Dec(ember)?)\b", re.I)

DATASETS = {"councils": "council.schema.json", "territories": "territory.schema.json",
            "merit-badges": "merit-badge.schema.json", "camps": "camp.schema.json",
            "ranks": "rank.schema.json", "awards": "award.schema.json",
            "oa-lodges": "oa-lodge.schema.json"}


def load_schemas():
    return {p.name: json.loads(p.read_text("utf-8")) for p in SCHEMA_DIR.glob("*.schema.json")}


def registry(schemas):
    return Registry().with_resources([(s["$id"], Resource.from_contents(s)) for s in schemas.values()])



def main() -> int:
    schemas = load_schemas()
    reg = registry(schemas)
    errs: list[str] = []
    entities: set[str] = set()          # "kind:slug"
    open_ended: set[str] = set()        # entities with a valid_to:null version
    camp_merged: dict[str, str] = {}    # retired id -> surviving camp file that absorbed it
    entity_validator = {ds: Draft202012Validator(schemas[s], registry=reg,
                        format_checker=Draft202012Validator.FORMAT_CHECKER) for ds, s in DATASETS.items()}
    event_validator = Draft202012Validator(schemas["event.schema.json"], registry=reg,
                                            format_checker=Draft202012Validator.FORMAT_CHECKER)

    # pass 1: entity files (schema + id/filename + version windows) and collect ids
    for ds, schema_name in DATASETS.items():
        for p in sorted((DATA / ds).glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            for e in entity_validator[ds].iter_errors(obj):
                errs.append(f"{p.name}: schema: {e.json_path}: {e.message}")
            if obj.get("id") != p.stem:
                errs.append(f"{p.name}: id {obj.get('id')!r} != filename stem {p.stem!r}")
            entities.add(f"{obj.get('kind')}:{obj.get('id')}")
            if any(v.get("valid_to") is None for v in obj.get("versions", [])):
                open_ended.add(f"{obj.get('kind')}:{obj.get('id')}")
            vs = obj.get("versions", [])
            # ordered + non-overlapping half-open: successor from == predecessor to
            for a, b in zip(vs, vs[1:]):
                at, bf = a.get("valid_to"), b.get("valid_from")
                if at is None or bf is None or bf < at:
                    errs.append(f"{p.name}: version windows not ordered/half-open at {a.get('valid_from')}..{at} -> {bf}..")
            # only the LAST version may be open-ended
            for v in vs[:-1]:
                if v.get("valid_to") is None:
                    errs.append(f"{p.name}: non-final version has valid_to=null")
            if ds == "camps":  # operator<->council coupling + evergreen summary (schema can't express these)
                for v in vs:
                    op, coun = v.get("operator"), v.get("council")
                    if op == "council" and coun is None:
                        errs.append(f"{p.name}: operator=council but council is null")
                    elif op in ("national", "other", "unknown") and coun is not None:
                        errs.append(f"{p.name}: operator={op} but council is set ({coun})")
                    s = v.get("summary")
                    if s and _TRANSITORY.search(s):
                        errs.append(f"{p.name}: summary has transitory text ({_TRANSITORY.search(s).group(0)!r}); "
                                    f"must be evergreen (no dates/fees/months)")
                    # a survey date and a source tier describe the same act: neither is
                    # meaningful alone, so they must appear and disappear together.
                    fva, tier = v.get("features_verified_at"), v.get("features_source_tier")
                    if bool(fva) != bool(tier):
                        errs.append(f"{p.name}: features_verified_at={fva!r} but "
                                    f"features_source_tier={tier!r}; both are set or both are null")
                    seen_f: set[str] = set()
                    for ft in (v.get("features") or []):
                        c = ft.get("code")
                        if c in seen_f:
                            # uniqueItems compares whole objects, so it stops catching this the
                            # moment two entries for one code differ in `note`/`signature`.
                            errs.append(f"{p.name}: duplicate feature code {c!r}")
                        seen_f.add(c)
                        n = ft.get("note")
                        if n and _TRANSITORY.search(n):
                            errs.append(f"{p.name}: feature {c!r} note has transitory text "
                                        f"({_TRANSITORY.search(n).group(0)!r}); must be evergreen")
                    lat, lon, st = v.get("lat"), v.get("lon"), v.get("state")
                    if lat is not None and lon is not None and us_geo.known(st) and not us_geo.in_state(st, lat, lon):
                        errs.append(f"{p.name}: coord ({lat}, {lon}) is outside {st} bounds "
                                    f"(mislocated; null it or backfill via tools/geocode_camps.py)")
                for _mid in {m for _v in vs for m in _v.get("merged_from", [])}:
                    if _mid in camp_merged:
                        errs.append(f"{p.name}: merged_from id {_mid!r} also claimed by {camp_merged[_mid]}")
                    camp_merged[_mid] = p.name

    for _mid, _src in camp_merged.items():
        if f"camp:{_mid}" in entities:
            errs.append(f"{_src}: merged_from id {_mid!r} is still a live camp (must be retired)")

    # pass 2: referential integrity
    def check_ref(ref, src):
        if ref is not None and ref not in entities:
            errs.append(f"{src}: dangling ref {ref!r}")

    for ds in DATASETS:
        for p in sorted((DATA / ds).glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            for v in obj.get("versions", []):
                check_ref(v.get("territory"), f"{p.name} territory")
                check_ref(v.get("parent"), f"{p.name} parent")
                check_ref(v.get("council"), f"{p.name} council")

    # pass 3: event files (schema + participant refs + unique ids)
    for ds in DATASETS:
        ep = DATA / ds / "_events.json"
        if not ep.exists():
            continue
        obj = json.loads(ep.read_text("utf-8"))
        for e in event_validator.iter_errors(obj):
            errs.append(f"{ds}/_events.json: schema: {e.json_path}: {e.message}")
        seen = set()
        ENDED_AS_PRED = {"merged", "absorbed", "split", "superseded"}
        for ev in obj.get("events", []):
            eid = ev.get("id")
            if eid in seen:
                errs.append(f"{ds}/_events.json: duplicate event id {eid!r}")
            seen.add(eid)
            etype = ev.get("type")
            for part in ev.get("participants", []):
                ref, role = part.get("ref"), part.get("role")
                check_ref(ref, f"{ds}/_events.json event {eid}")
                # retired-entity invariant (PLAN §3.1): an entity ended by an event
                # must not still have an open (valid_to:null) version.
                ended = (etype == "discontinued" and role == "subject") or \
                        (etype in ENDED_AS_PRED and role == "predecessor")
                if ended and ref in open_ended:
                    errs.append(f"{ds}/_events.json event {eid}: {ref} ended by '{etype}' "
                                f"but still has a valid_to:null (current) version")

    # pass 3b: a CURRENT camp must not hang off a council that no longer exists. `check_ref`
    # only proves the ref resolves, and a merged-away council still resolves, so six active
    # camps were sitting on dissolved councils undetected. Hard-fail only where the successor
    # is knowable from our own event graph (the fix is unambiguous); councils that were
    # `discontinued` with no continuing party need research and are reported by
    # tools/maintenance.py instead of blocking the build.
    successor: dict[str, str] = {}
    cev = DATA / "councils" / "_events.json"
    if cev.exists():
        for ev in json.loads(cev.read_text("utf-8")).get("events", []):
            parts = ev.get("participants", [])
            gone = [p["ref"] for p in parts if p.get("role") in ("predecessor", "subject")]
            cont = [p["ref"] for p in parts if p.get("role") in ("continuing", "successor")]
            for g in gone:
                if cont:
                    successor[g] = cont[0]
    for p in sorted((DATA / "camps").glob("*.json")):
        if p.name == "_events.json":
            continue
        obj = json.loads(p.read_text("utf-8"))
        for v in obj.get("versions", []):
            if v.get("valid_to") is not None:
                continue                      # historical camp version: a dead council is correct
            ref = v.get("council")
            if ref and ref not in open_ended and ref in successor:
                errs.append(f"{p.name}: current camp references non-current council {ref!r}; "
                            f"it was succeeded by {successor[ref]!r} — repoint it")

    # pass 4: requirement-sets (immutable documents, not versioned entities)
    rs_dir = DATA / "requirement-sets"
    nrs = 0
    if rs_dir.exists():
        rs_validator = Draft202012Validator(schemas["requirement-set.schema.json"], registry=reg,
                                             format_checker=Draft202012Validator.FORMAT_CHECKER)
        docs = []
        for p in sorted(rs_dir.glob("*.json")):
            obj = json.loads(p.read_text("utf-8"))
            for e in rs_validator.iter_errors(obj):
                errs.append(f"requirement-sets/{p.name}: schema: {e.json_path}: {e.message}")
            if obj.get("id") != p.stem:
                errs.append(f"requirement-sets/{p.name}: id {obj.get('id')!r} != filename stem {p.stem!r}")
            docs.append((p.name, obj))
        rs_ids = {f"requirement-set:{o['id']}" for _, o in docs}

        def _has_text(node) -> bool:
            return node.get("text") is not None or any(_has_text(c) for c in node.get("children", []))

        def _walk_choose(node, where):
            if node.get("choose") is not None and not node.get("children"):
                errs.append(f"{where}: requirement {node.get('number')!r} has choose but no children")
            for c in node.get("children", []):
                _walk_choose(c, where)

        for name, obj in docs:
            check_ref(obj.get("subject"), f"requirement-sets/{name} subject")
            sup = obj.get("supersedes")
            if sup is not None and sup not in rs_ids:
                errs.append(f"requirement-sets/{name}: dangling supersedes {sup!r}")
            has_text = any(_has_text(r) for r in obj.get("requirements", []))
            if bool(obj.get("includes_official_text")) != has_text:
                errs.append(f"requirement-sets/{name}: includes_official_text={obj.get('includes_official_text')} "
                            f"but text-present={has_text}")
            for r in obj.get("requirements", []):
                _walk_choose(r, f"requirement-sets/{name}")

        # Revision-chain invariants. Editions of one subject form a single ordered history,
        # so: no edition supersedes itself, two editions never claim the same effective_from
        # (ids are <subject>-<year>, so a collision silently overwrites one), and a subject
        # has exactly one open edition unless the subject itself is retired.
        by_subject: dict[str, list[dict]] = {}
        for _n, obj in docs:
            by_subject.setdefault(obj.get("subject"), []).append(obj)
        for subj, sets in sorted(by_subject.items()):
            for obj in sets:
                if obj.get("supersedes") == f"requirement-set:{obj['id']}":
                    errs.append(f"requirement-sets/{obj['id']}: supersedes itself")
            froms = [o["effective_from"] for o in sets]
            dupe = next((f for f in froms if froms.count(f) > 1), None)
            if dupe:
                errs.append(f"requirement-sets: subject {subj!r} has two editions effective {dupe} "
                            f"(ids collide on year; one would overwrite the other)")
            opens = [o for o in sets if o.get("effective_to") is None]
            subject_open = subj in open_ended
            if len(opens) > 1:
                errs.append(f"requirement-sets: subject {subj!r} has {len(opens)} open editions "
                            f"({', '.join(o['id'] for o in opens)}); at most one may be current")
            elif not opens and subject_open:
                errs.append(f"requirement-sets: subject {subj!r} is current but has no open edition")
        nrs = len(docs)

    # pass 5: controlled vocabularies + every code used in camp data must be defined
    vocab_dir = DATA / "vocab"
    nvocab = 0
    if vocab_dir.exists():
        v_validator = Draft202012Validator(schemas["vocab.schema.json"], registry=reg,
                                            format_checker=Draft202012Validator.FORMAT_CHECKER)
        codes_for: dict[str, set] = {}
        for p in sorted(vocab_dir.glob("*.json")):
            obj = json.loads(p.read_text("utf-8"))
            for e in v_validator.iter_errors(obj):
                errs.append(f"vocab/{p.name}: schema: {e.json_path}: {e.message}")
            if obj.get("id") != p.stem:
                errs.append(f"vocab/{p.name}: id {obj.get('id')!r} != filename stem {p.stem!r}")
            cs = {t["code"] for t in obj.get("terms", [])}
            by_code = {t["code"]: t for t in obj.get("terms", [])}
            claimed: dict[str, str] = {}
            for t in obj.get("terms", []):
                b = t.get("broader")
                if b is not None and b not in cs:
                    errs.append(f"vocab/{p.name}: term {t['code']!r} has broader {b!r}, "
                                f"which is not a term in this vocabulary")
                for a in t.get("aliases", []):
                    if a in cs:
                        errs.append(f"vocab/{p.name}: alias {a!r} on {t['code']!r} collides with a real code")
                    elif a in claimed:
                        errs.append(f"vocab/{p.name}: alias {a!r} claimed by both "
                                    f"{claimed[a]!r} and {t['code']!r}")
                    else:
                        claimed[a] = t["code"]
                walked, cur = set(), t["code"]          # a `broader` chain must terminate
                while cur is not None:
                    if cur in walked:
                        errs.append(f"vocab/{p.name}: `broader` cycle reachable from {t['code']!r}")
                        break
                    walked.add(cur)
                    cur = by_code.get(cur, {}).get("broader")
            for field in obj.get("applies_to", []):
                codes_for[field] = cs
            nvocab += 1
        getters = {"camp.camp_type": lambda v: ([v["camp_type"]] if v.get("camp_type") else []),
                   "camp.program_types": lambda v: v.get("program_types", []),
                   "camp.features": lambda v: [f["code"] for f in v.get("features", [])]}
        for p in sorted((DATA / "camps").glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            for v in obj.get("versions", []):
                for field, get in getters.items():
                    known = codes_for.get(field)
                    if known is None:
                        continue
                    for code in get(v):
                        if code not in known:
                            errs.append(f"camps/{p.name}: {field} value {code!r} not in vocab "
                                        f"(add it to data/vocab/)")

        # merit-badge tags use the same discipline as camp vocab fields
        known_tags = codes_for.get("merit-badge.tags")
        for p in sorted((DATA / "merit-badges").glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            for v in obj.get("versions", []):
                if known_tags is not None:
                    for code in v.get("tags", []):
                        if code not in known_tags:
                            errs.append(f"merit-badges/{p.name}: tag {code!r} not in vocab "
                                        f"(add it to data/vocab/merit-badge-tags.json)")

    # pass 5b: merit-badge `description` must be original evergreen prose, never pamphlet or
    # requirement text. The requirement text IS Scouting America's copyright and is published
    # only under the `text_rights` carve-out; a description that quoted it would silently drag
    # copyrighted wording into the CC-licensed part of the dataset. So this checks for lifted
    # runs of words against the badge's own requirement sets rather than trusting the author.
    def _words(s: str) -> list[str]:
        return re.findall(r"[a-z0-9]+", (s or "").lower())

    RUN = 8      # 8 consecutive words in common is plagiarism, not coincidence
    rs_text: dict[str, set[tuple]] = {}
    if (DATA / "requirement-sets").exists():
        for p in sorted((DATA / "requirement-sets").glob("*.json")):
            doc = json.loads(p.read_text("utf-8"))
            subj = doc.get("subject")
            if not (subj or "").startswith("merit-badge:"):
                continue
            buf: list[str] = []

            def _walk(rqs):
                for r in rqs:
                    buf.extend(_words(r.get("text")))
                    _walk(r.get("children") or [])
            _walk(doc.get("requirements", []))
            grams = rs_text.setdefault(subj.split(":", 1)[1], set())
            grams.update(tuple(buf[i:i + RUN]) for i in range(max(0, len(buf) - RUN + 1)))

    for p in sorted((DATA / "merit-badges").glob("*.json")):
        if p.name == "_events.json":
            continue
        obj = json.loads(p.read_text("utf-8"))
        for v in obj.get("versions", []):
            d = v.get("description")
            if not d:
                continue
            if _TRANSITORY.search(d):
                errs.append(f"merit-badges/{p.name}: description has transitory text "
                            f"({_TRANSITORY.search(d).group(0)!r}); must be evergreen")
            w = _words(d)
            grams = rs_text.get(obj["id"], set())
            lifted = next((w[i:i + RUN] for i in range(max(0, len(w) - RUN + 1))
                           if tuple(w[i:i + RUN]) in grams), None)
            if lifted:
                errs.append(f"merit-badges/{p.name}: description reuses {RUN}+ consecutive words "
                            f"from its requirement text ({' '.join(lifted)!r}) — must be original "
                            f"prose, not Scouting America's wording")

    errs += check_tree()   # every data file must carry the correct $schema ref

    def _count(ds):
        return len([p for p in (DATA / ds).glob("*.json") if p.name != "_events.json"])
    ncouncils, nterr, nmb, ncamps, nranks, nawards, nlodges = (_count("councils"), _count("territories"),
                                                      _count("merit-badges"), _count("camps"),
                                                      _count("ranks"), _count("awards"), _count("oa-lodges"))
    if errs:
        print(f"{len(errs)} error(s):")
        for e in errs[:100]:
            print("  " + e)
        return 1
    print(f"OK: {ncouncils} councils + {nterr} territories + {nmb} merit-badges + "
          f"{nrs} requirement-sets + {ncamps} camps + {nranks} ranks + {nawards} awards + {nlodges} oa-lodges "
          f"valid (schema + referential + windows + text-rights + camp coupling + coord bounds + vocab), {len(entities)} entities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
