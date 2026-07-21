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
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v1"
DATA = ROOT / "data"

DATASETS = {"councils": "council.schema.json", "territories": "territory.schema.json",
            "merit-badges": "merit-badge.schema.json"}


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

    ncouncils = len(list((DATA / "councils").glob("*.json"))) - 1
    nterr = len(list((DATA / "territories").glob("*.json"))) - 1
    if errs:
        print(f"{len(errs)} error(s):")
        for e in errs[:100]:
            print("  " + e)
        return 1
    print(f"OK: {ncouncils} councils + {nterr} territories + events valid "
          f"(schema + referential + version windows), {len(entities)} entities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
