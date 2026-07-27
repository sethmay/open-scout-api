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
            "oa-lodges": "oa-lodge.schema.json", "adventures": "adventure.schema.json",
            "positions": "position.schema.json", "training": "training.schema.json"}


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
                for r in (v.get("ranks") or []):     # adventure.ranks (list-valued)
                    check_ref(r, f"{p.name} ranks")

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
            # a node standing for another entity must resolve, or the advancement graph is broken
            check_ref(node.get("ref"), f"{where} requirement {node.get('number')!r} ref")
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
            # `completion_rule` is prose that narrows the list ("Complete Requirements 1-4 plus at
            # least one other"), so it is only trustworthy if the numbers it cites exist. A rule
            # naming requirement 7 on a five-requirement document means the requirement list was
            # mis-parsed, which is the failure mode this whole extraction risks.
            rule = obj.get("completion_rule")
            if rule is not None:
                if not rule.strip():
                    errs.append(f"requirement-sets/{name}: completion_rule is blank; use null when "
                                f"every requirement is required")
                tops = {r.get("number") for r in obj.get("requirements", [])}
                nmax = max((int(n) for n in tops if str(n).isdigit()), default=0)
                cited = [int(x) for x in re.findall(r"\b(\d+)\b", rule)]
                over = sorted({c for c in cited if c > nmax})
                if over:
                    errs.append(f"requirement-sets/{name}: completion_rule cites requirement(s) "
                                f"{over} but the document only has {nmax} ({rule!r})")

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
            # Editions must form ONE unbroken half-open line: an effective-dated document history
            # with a hole in it silently answers "which requirements applied in 2020?" with
            # nothing, and one with an overlap answers it twice. Requiring exact abutment —
            # rather than merely forbidding overlaps and multi-year gaps — is what lets a consumer
            # write a single `effective_from <= D < effective_to` predicate across every subject.
            # Two styles were in use until 2026-07-27 (see tools/requirement_windows.py); the
            # looser gate is what allowed them to coexist, so it is now exact.
            ordered = sorted(sets, key=lambda o: o["effective_from"])
            for prev, nxt in zip(ordered, ordered[1:]):
                pt = prev.get("effective_to")
                if pt is None:
                    errs.append(f"requirement-sets/{prev['id']}: open edition sits before "
                                f"{nxt['id']} in the chain; only the newest may be open")
                elif pt != nxt["effective_from"]:
                    rel = "an overlap" if pt > nxt["effective_from"] else "a gap"
                    errs.append(f"requirement-sets: subject {subj!r} has {rel} — {prev['id']} "
                                f"ends {pt} but {nxt['id']} starts {nxt['effective_from']}; "
                                f"windows are half-open, so they must be equal")
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

        # position unit types, same discipline
        known_units = codes_for.get("position.unit_types")
        for p in sorted((DATA / "positions").glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            for v in obj.get("versions", []):
                for code in v.get("unit_types", []):
                    if known_units is not None and code not in known_units:
                        errs.append(f"positions/{p.name}: unit_type {code!r} not in vocab "
                                    f"(add it to data/vocab/position-unit-types.json)")

        # adventure categories and areas, same discipline
        known_cats = codes_for.get("adventure.category")
        known_areas = codes_for.get("adventure.area")
        for p in sorted((DATA / "adventures").glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            for v in obj.get("versions", []):
                if known_cats is not None and v.get("category") not in known_cats:
                    errs.append(f"adventures/{p.name}: category {v.get('category')!r} not in vocab "
                                f"(add it to data/vocab/adventure-categories.json)")
                area = v.get("area")
                if area is not None and known_areas is not None and area not in known_areas:
                    errs.append(f"adventures/{p.name}: area {area!r} not in vocab "
                                f"(add it to data/vocab/adventure-areas.json)")
                # An area IS the required slot it fills, so the two facts are one fact: a required
                # adventure filling nothing, or an elective claiming a slot, is incoherent. Scoped
                # to OPEN windows: the six areas are a 2024-program construct, and the pre-2024
                # line-up had required adventures with no area to fill.
                if v.get("valid_to") is None and (v.get("category") == "required") != (area is not None):
                    errs.append(f"adventures/{p.name}: category={v.get('category')!r} but "
                                f"area={area!r}; area is set exactly for current required adventures")

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

    # pass 5c: a Cub rank's requirement-set and its adventures must tell the same story.
    # The rank tree is authoritative (which adventures, in which group); `adventure.ranks` and
    # `adventure.category` are the reverse index consumers actually read. Nothing stops the two
    # drifting apart -- an adventure moved between ranks upstream, or a category edited by hand --
    # so both directions are checked: every ref'd adventure claims that rank back, every
    # adventure's claimed ranks really list it, and its category matches the group it sits in.
    # A rank states two groups; the page's further split of electives into ordinary and
    # "special" (shooting sports, approved events only) is a property of the adventure, so the
    # elective group legitimately holds both categories. Mirrors tools/seed_cub_adventures.py.
    GROUP_CATEGORIES = {"Required Adventures": {"required"},
                        "Elective Adventures": {"elective", "special_elective"}}
    from_ranks: dict[str, set[str]] = {}        # adventure slug -> rank slugs listing it
    cat_from_ranks: dict[str, set[str]] = {}    # adventure slug -> categories it is grouped under
    if (DATA / "requirement-sets").exists():
        for p in sorted((DATA / "requirement-sets").glob("*.json")):
            doc = json.loads(p.read_text("utf-8"))
            subj = doc.get("subject") or ""
            if not subj.startswith("rank:"):
                continue
            for g in doc.get("requirements", []):
                allowed = GROUP_CATEGORIES.get(g.get("text"))
                for child in (g.get("children") or []):
                    ref = child.get("ref") or ""
                    if not ref.startswith("adventure:"):
                        continue
                    slug = ref.split(":", 1)[1]
                    from_ranks.setdefault(slug, set()).add(subj.split(":", 1)[1])
                    if allowed is None:
                        errs.append(f"requirement-sets/{p.name}: adventure {slug!r} sits under group "
                                    f"{g.get('text')!r}, which maps to no adventure category")
                    else:
                        cat_from_ranks.setdefault(slug, set()).update(allowed)
    for p in sorted((DATA / "adventures").glob("*.json")):
        if p.name == "_events.json":
            continue
        obj = json.loads(p.read_text("utf-8"))
        slug = obj.get("id")
        listed = from_ranks.get(slug, set())
        # A rank's requirement-set is the CURRENT advancement structure, so only a currently
        # offered adventure has to appear in one. A retired adventure is reachable through
        # v1/adventures/index.json and carries its own rank association on its closed windows;
        # requiring a ref would force inventing historical rank trees to hold them.
        current_adv = any(v.get("valid_to") is None for v in obj.get("versions", []))
        if current_adv and not listed:
            errs.append(f"adventures/{p.name}: no rank requirement-set refs {slug!r}; an adventure "
                        f"no rank offers is unreachable (retire it, or add the ref)")
        for v in obj.get("versions", []):
            if v.get("valid_to") is not None:
                continue                      # historical window: the current tree can't speak for it
            claimed = {r.split(":", 1)[1] for r in (v.get("ranks") or [])}
            if listed and claimed != listed:
                errs.append(f"adventures/{p.name}: ranks {sorted(claimed)} but the rank "
                            f"requirement-sets list it under {sorted(listed)}")
            cats = cat_from_ranks.get(slug, set())
            if cats and v.get("category") not in cats:
                errs.append(f"adventures/{p.name}: category {v.get('category')!r} but the group it "
                            f"sits in under the rank requirement-sets allows {sorted(cats)}")

    # pass 5d: every Cub rank fills all six requirement areas, exactly once each. This is the check
    # that would have caught the original Arrow of Light error at write time: two AOL adventures are
    # *named* after areas ("Personal Fitness", "Citizenship"), so a parser that read printed labels
    # as adventures produced seven required entries covering five areas, and it shipped. Coverage is
    # arithmetic; eyeballing a list is not.
    all_areas: set[str] = set()
    area_by_rank: dict[str, list[tuple[str, str]]] = {}   # rank -> [(area, adventure slug)]
    for p in sorted((DATA / "adventures").glob("*.json")):
        if p.name == "_events.json":
            continue
        obj = json.loads(p.read_text("utf-8"))
        for v in obj.get("versions", []):
            if v.get("valid_to") is not None or not v.get("area"):
                continue
            all_areas.add(v["area"])
            for r in (v.get("ranks") or []):
                area_by_rank.setdefault(r.split(":", 1)[1], []).append((v["area"], obj["id"]))
    for rank in sorted(area_by_rank):
        filled = [a for a, _ in area_by_rank[rank]]
        for area in sorted(all_areas):
            n = filled.count(area)
            if n != 1:
                who = sorted(s for a, s in area_by_rank[rank] if a == area)
                errs.append(f"rank {rank!r}: area {area!r} filled by {n} required adventures "
                            f"({', '.join(who) or 'none'}); each rank fills every area exactly once")

    # pass 6: merit badge popularity rankings (immutable per-year documents, like requirement-sets).
    # The gates that matter are arithmetic and temporal: a rank printed twice or a gap in a year
    # claiming completeness means the source table was mis-transcribed, and a badge ranked in a year
    # it did not exist means a pre-rename name slipped through the slug mapping (the 2022 source post
    # still prints "Medicine" two years after it became Health Care Professions).
    rank_dir = DATA / "merit-badge-rankings"
    nrank_docs = 0
    if rank_dir.exists():
        rk_validator = Draft202012Validator(schemas["merit-badge-ranking.schema.json"], registry=reg,
                                            format_checker=Draft202012Validator.FORMAT_CHECKER)
        # a badge's life span, from its own version windows
        span: dict[str, tuple[str | None, str | None]] = {}
        for p in sorted((DATA / "merit-badges").glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            vs = obj.get("versions") or [{}]
            span[obj["id"]] = (vs[0].get("valid_from"),
                               None if any(v.get("valid_to") is None for v in vs) else vs[-1].get("valid_to"))
        for p in sorted(rank_dir.glob("*.json")):
            obj = json.loads(p.read_text("utf-8"))
            for e in rk_validator.iter_errors(obj):
                errs.append(f"merit-badge-rankings/{p.name}: schema: {e.json_path}: {e.message}")
            if obj.get("id") != p.stem:
                errs.append(f"merit-badge-rankings/{p.name}: id {obj.get('id')!r} != filename stem {p.stem!r}")
            if str(obj.get("year")) != obj.get("id"):
                errs.append(f"merit-badge-rankings/{p.name}: year {obj.get('year')} disagrees with id {obj.get('id')!r}")
            year = obj.get("year")
            ranks = [r.get("rank") for r in obj.get("rankings", [])]
            subs = [r.get("subject") for r in obj.get("rankings", [])]
            dupe_r = sorted({r for r in ranks if ranks.count(r) > 1})
            if dupe_r:
                errs.append(f"merit-badge-rankings/{p.name}: rank(s) {dupe_r} used more than once")
            dupe_s = sorted({s for s in subs if subs.count(s) > 1})
            if dupe_s:
                errs.append(f"merit-badge-rankings/{p.name}: badge(s) {dupe_s} ranked more than once")
            if obj.get("complete") and sorted(ranks) != list(range(1, len(ranks) + 1)):
                gaps = [n for n in range(1, (max(ranks) if ranks else 0) + 1) if n not in ranks]
                errs.append(f"merit-badge-rankings/{p.name}: complete=true but ranks are not 1..{len(ranks)} "
                            f"(missing {gaps[:6]})")
            for s in subs:
                check_ref(s, f"merit-badge-rankings/{p.name}")
                slug = (s or "").split(":", 1)[-1]
                if slug in span and year is not None:
                    lo, hi = span[slug]
                    if lo and int(str(lo)[:4]) > year:
                        errs.append(f"merit-badge-rankings/{p.name}: {s} is ranked but the badge only "
                                    f"begins {lo}")
                    if hi and int(str(hi)[:4]) < year:
                        errs.append(f"merit-badge-rankings/{p.name}: {s} is ranked but the badge ended "
                                    f"{hi} (a pre-rename name may have been mapped)")
            nrank_docs += 1

    # pass 7: the Eagle merit-badge slot tree and the `eagle_required` flag describe the same fact
    # from two directions and must not drift. The flag marks LIST membership (18 badges, the number
    # Star and Life requirement 3 themselves cite); the tree carries the SLOTS (14, three of them
    # either/or). A tracker needs both, so both are published — and every badge the tree refs must
    # carry the flag, every flagged badge must appear in the tree, and the slot count must match the
    # number the requirement's own verbatim text states.
    eagle_sets = [p for p in sorted((DATA / "requirement-sets").glob("eagle-*.json"))
                  if json.loads(p.read_text("utf-8")).get("effective_to") is None]
    # Compared AS OF the requirement-set's own effective date, not today. Citizenship in Society is
    # slot (d) of the in-force 2024 requirements and was Eagle-required from 2022 until Scouting
    # America discontinued it in Feb 2026 — the two records agree for the window the requirement
    # took effect in, and only a same-date comparison sees that.
    def flagged_at(when: str) -> set[str]:
        out = set()
        for q in sorted((DATA / "merit-badges").glob("*.json")):
            if q.name == "_events.json":
                continue
            obj = json.loads(q.read_text("utf-8"))
            for v in obj["versions"]:
                lo, hi = v.get("valid_from"), v.get("valid_to")
                if (lo is None or lo <= when) and (hi is None or hi > when):
                    if v.get("eagle_required"):
                        out.add(f"merit-badge:{obj['id']}")
                    break
        return out

    for p in eagle_sets:
        doc = json.loads(p.read_text("utf-8"))
        flagged = flagged_at(doc["effective_from"])
        req3 = next((r for r in doc["requirements"] if r["number"] == "3"), None)
        if req3 is None or not req3.get("children"):
            errs.append(f"requirement-sets/{p.name}: Eagle requirement 3 carries no slot tree; run "
                        f"tools/seed_advancement_graph.py (a prose-only list cannot be counted)")
            continue
        refs = set()

        def _refs(nodes):
            for n in nodes:
                if (n.get("ref") or "").startswith("merit-badge:"):
                    refs.add(n["ref"])
                _refs(n.get("children") or [])
        _refs(req3["children"])
        if refs - flagged:
            errs.append(f"requirement-sets/{p.name}: Eagle slot tree refs {sorted(refs - flagged)} "
                        f"which are not flagged eagle_required")
        if flagged - refs:
            errs.append(f"requirement-sets/{p.name}: {sorted(flagged - refs)} are flagged "
                        f"eagle_required but appear in no Eagle slot")
        stated = re.search(r"these\s+(\d+)\s+merit badges", req3.get("text") or "", re.I)
        if stated and int(stated.group(1)) != len(req3["children"]):
            errs.append(f"requirement-sets/{p.name}: requirement 3 says 'these {stated.group(1)} "
                        f"merit badges' but the slot tree has {len(req3['children'])}")

    # pass 8: positions of responsibility. The ranks decide which positions they accept, so unlike
    # adventures there is NO symmetric agreement to enforce — Bugler is genuinely a troop position
    # that Star and Life accept and Eagle does not, and a gate demanding every rank list every
    # position would forbid the real rule. What must hold is weaker and still useful: a position
    # offered under a unit-type heading really claims that unit type, and no position sits in the
    # catalog that no rank will accept.
    pos_dir = DATA / "positions"
    if pos_dir.exists():
        GROUP_UNIT = {"Scout troop": "scout_troop",
                      "Venturing crew/Sea Scout ship": "crew_or_ship"}
        unit_types: dict[str, set[str]] = {}
        for p in sorted(pos_dir.glob("*.json")):
            if p.name == "_events.json":
                continue
            obj = json.loads(p.read_text("utf-8"))
            ov = next((v for v in obj["versions"] if v.get("valid_to") is None), obj["versions"][-1])
            unit_types[obj["id"]] = set(ov.get("unit_types") or [])
        offered: set[str] = set()
        for p in sorted((DATA / "requirement-sets").glob("*.json")):
            doc = json.loads(p.read_text("utf-8"))
            if not (doc.get("subject") or "").startswith("rank:"):
                continue
            for req in doc.get("requirements", []):
                for grp in (req.get("children") or []):
                    want = GROUP_UNIT.get((grp.get("text") or "").strip())
                    for child in (grp.get("children") or []):
                        ref = child.get("ref") or ""
                        if not ref.startswith("position:"):
                            continue
                        slug = ref.split(":", 1)[1]
                        offered.add(slug)
                        if want and slug in unit_types and want not in unit_types[slug]:
                            errs.append(f"requirement-sets/{p.name}: {ref} is listed under "
                                        f"{grp.get('text')!r} but its unit_types are "
                                        f"{sorted(unit_types[slug])}")
        for slug in sorted(set(unit_types) - offered):
            errs.append(f"positions/{slug}.json: no rank requirement offers this position; a "
                        f"position no rank accepts cannot be earned toward anything")

    # pass 9: the countable facts derived from requirement prose (tenure_months, badge_count).
    # Both are transcriptions of a number the requirement itself prints, so both are checked back
    # against that verbatim text: a figure that no longer appears in the sentence it claims to
    # summarise is drift, whichever side moved. The badge chain is also checked arithmetically —
    # Star's 6 plus Life's 5 must be Life's stated "11 in all" — because the source states the
    # running total independently at each rank, which makes the chain self-checking.
    WORDS = {i: w for i, w in enumerate(
        "zero one two three four five six seven eight nine ten eleven twelve".split())}

    def _says(text: str, n: int) -> bool:
        return bool(re.search(rf"\b({n}|{WORDS.get(n, chr(0))})\b", text or "", re.I))

    def _nodes(reqs):
        for r in reqs:
            yield r
            yield from _nodes(r.get("children") or [])

    rank_order, badge_chain = {}, {}
    for p in sorted((DATA / "ranks").glob("*.json")):
        if p.name == "_events.json":
            continue
        rd = json.loads(p.read_text("utf-8"))
        cur = next((v for v in rd["versions"] if v.get("valid_to") is None), None)
        if cur:
            rank_order[rd["id"]] = (cur.get("program"), cur.get("order"))
    for p in sorted((DATA / "requirement-sets").glob("*.json")):
        doc = json.loads(p.read_text("utf-8"))
        if not doc.get("subject", "").startswith("rank:") or doc.get("effective_to") is not None:
            continue
        slug = doc["subject"].split(":", 1)[1]
        for req in _nodes(doc.get("requirements", [])):
            text = req.get("text") or ""
            if (mo := req.get("tenure_months")) is not None and not _says(text, mo):
                errs.append(f"requirement-sets/{p.name}: requirement {req['number']} claims "
                            f"tenure_months={mo} but its own text never says {mo}")
            bc = req.get("badge_count")
            if not bc:
                continue
            for key in ("earn", "cumulative", "from_eagle_required"):
                if (v := bc.get(key)) is not None and not _says(text, v):
                    errs.append(f"requirement-sets/{p.name}: requirement {req['number']} claims "
                                f"badge_count.{key}={v} but its own text never says {v}")
            if (fer := bc.get("from_eagle_required")) is not None:
                if fer > bc["earn"]:
                    errs.append(f"requirement-sets/{p.name}: badge_count requires {fer} from the "
                                f"Eagle-required list but only {bc['earn']} badges are earned")
                # The list is the eagle_required flag read as of this edition's own effective date,
                # the same temporal rule pass 7 uses.
                listed = len(flagged_at(doc["effective_from"]))
                if fer > listed:
                    errs.append(f"requirement-sets/{p.name}: badge_count requires {fer} from the "
                                f"Eagle-required list, which held only {listed} badges on "
                                f"{doc['effective_from']}")
            if slug in rank_order:
                badge_chain[slug] = (rank_order[slug], bc)
    prev_cum = {}
    for slug, ((program, order), bc) in sorted(badge_chain.items(), key=lambda kv: kv[1][0]):
        base = prev_cum.get(program, 0)
        if bc["cumulative"] != base + bc["earn"]:
            errs.append(f"requirement-sets: rank {slug!r} says {bc['earn']} badges earned and "
                        f"{bc['cumulative']} in all, but the rank before it left {base}; "
                        f"{base} + {bc['earn']} != {bc['cumulative']}")
        prev_cum[program] = bc["cumulative"]

    # pass 10: adult training requirements. These are flat documents rather than versioned
    # entities — one per row of the TRAINED LEADER REQUIREMENTS chart, keyed by (position,
    # unit_type) — so pass 1 does not see them and they need their own schema + integrity pass.
    treq_dir = DATA / "training-requirements"
    ntreq = 0
    if treq_dir.exists():
        treq_validator = Draft202012Validator(schemas["training-requirement.schema.json"],
                                              registry=reg,
                                              format_checker=Draft202012Validator.FORMAT_CHECKER)
        course_refs: set[str] = set()
        by_code: dict[tuple[str, str], str] = {}
        course_code: dict[str, str | None] = {}
        for q in sorted((DATA / "training").glob("*.json")):
            if q.name == "_events.json":
                continue
            cd = json.loads(q.read_text("utf-8"))
            cur_v = next((v for v in cd["versions"] if v.get("valid_to") is None), cd["versions"][-1])
            course_code[f"training:{cd['id']}"] = cur_v.get("code")

        def _refs(items):
            for it in items:
                if "ref" in it:
                    yield it
                kids = it.get("children") or []
                if kids and it.get("choose", 0) > len(kids):
                    yield {"_overchoose": it}
                yield from _refs(kids)

        for p in sorted(treq_dir.glob("*.json")):
            doc = json.loads(p.read_text("utf-8"))
            ntreq += 1
            for e in treq_validator.iter_errors(doc):
                errs.append(f"training-requirements/{p.name}: {'/'.join(str(x) for x in e.path)} "
                            f"{e.message}")
            if doc.get("id") != p.stem:
                errs.append(f"training-requirements/{p.name}: id {doc.get('id')!r} != filename")
            ypt = False
            for node in _refs(doc.get("requires", [])):
                if "_overchoose" in node:
                    it = node["_overchoose"]
                    errs.append(f"training-requirements/{p.name}: choose {it['choose']} of only "
                                f"{len(it['children'])} alternatives")
                    continue
                ref = node["ref"]
                course_refs.add(ref)
                if ref not in entities:
                    errs.append(f"training-requirements/{p.name}: {ref} does not resolve")
                elif (code := course_code.get(ref, "") or "").startswith("Y"):
                    ypt = True
            # The chart states it outright: "Youth Protection Training is a joining requirement for
            # all registered adults." A row without it is a transcription that dropped a column.
            if not ypt:
                errs.append(f"training-requirements/{p.name}: requires no Youth Protection course; "
                            f"YPT is a joining requirement for every registered adult")
            for code in doc.get("registration_codes", []):
                key = (doc.get("unit_type"), code)
                if key in by_code:
                    errs.append(f"training-requirements/{p.name}: registration code {code!r} in "
                                f"{doc.get('unit_type')!r} already claimed by {by_code[key]}")
                by_code[key] = p.name
        # A course nothing requires is either a parse artefact or a row we failed to transcribe.
        for ref in sorted(set(course_code) - course_refs):
            errs.append(f"training/{ref.split(':', 1)[1]}.json: no position requires this course")

    errs += check_tree()   # every data file must carry the correct $schema ref

    def _count(ds):
        return len([p for p in (DATA / ds).glob("*.json") if p.name != "_events.json"])
    ncouncils, nterr, nmb, ncamps, nranks, nawards, nlodges, nadv = (_count("councils"), _count("territories"),
                                                      _count("merit-badges"), _count("camps"),
                                                      _count("ranks"), _count("awards"), _count("oa-lodges"),
                                                      _count("adventures"))
    npos = _count("positions")
    if errs:
        print(f"{len(errs)} error(s):")
        for e in errs[:100]:
            print("  " + e)
        return 1
    print(f"OK: {ncouncils} councils + {nterr} territories + {nmb} merit-badges + "
          f"{nrs} requirement-sets + {ncamps} camps + {nranks} ranks + {nawards} awards + {nlodges} oa-lodges + "
          f"{nadv} adventures + {npos} positions + {ntreq} training requirements + "
          f"{nrank_docs} badge-ranking years "
          f"valid (schema + referential + windows + text-rights + camp coupling + coord bounds + vocab "
          f"+ rank/adventure agreement + area coverage), {len(entities)} entities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
