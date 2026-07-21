"""Validate schema/v1/examples against the canonical schemas.

Positive fixtures (examples/*.json) MUST validate; negative fixtures
(examples/invalid/*.json) MUST be rejected. Every strictness/conditional
keyword in the schemas needs at least one expected-fail case, or a schema
regression stays green (camp-finder LESSONS: make every guard bite; a CI
gate must be non-vacuous).

Seed of the future CI validation gate (see TODO.md "Pipeline validator" for
the cross-file rules JSON Schema cannot express). Exits nonzero on any failure.

Usage:  python tools/validate_examples.py
Deps :  pip install jsonschema  (>= 4.18, for referencing.Registry)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v1"
EXAMPLES_DIR = SCHEMA_DIR / "examples"
INVALID_DIR = EXAMPLES_DIR / "invalid"

# Example filename prefix -> schema file. Prefixes MUST be mutually unambiguous:
# schema_for() REJECTS a filename matching more than one prefix (no longest-match
# fallback), so keep new prefixes non-overlapping.
PREFIX_TO_SCHEMA = {
    "council-": "council.schema.json",
    "territory-": "territory.schema.json",
    "camp-": "camp.schema.json",
    "merit-badge-": "merit-badge.schema.json",
    "requirement-set-": "requirement-set.schema.json",
    "events-": "event.schema.json",
    "award-": "award.schema.json",
    "oa-lodge-": "oa-lodge.schema.json",
}


def load_schemas() -> dict[str, dict]:
    return {
        p.name: json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(SCHEMA_DIR.glob("*.schema.json"))
    }


def build_registry(schemas: dict[str, dict]) -> Registry:
    resources = [
        (schema["$id"], Resource.from_contents(schema)) for schema in schemas.values()
    ]
    return Registry().with_resources(resources)


def schema_for(example_name: str) -> str | None:
    matches = [s for p, s in PREFIX_TO_SCHEMA.items() if example_name.startswith(p)]
    if not matches:
        return None
    if len(matches) > 1:
        raise ValueError(f"ambiguous schema mapping for {example_name}: {matches}")
    return matches[0]


def errors_for(
    path: Path, schemas: dict[str, dict], registry: Registry
) -> tuple[str, list] | None:
    """Returns (schema_name, sorted validation errors), or None if no mapping."""
    schema_name = schema_for(path.name)
    if schema_name is None:
        return None
    validator = Draft202012Validator(
        schemas[schema_name],
        registry=registry,
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    instance = json.loads(path.read_text(encoding="utf-8"))
    return schema_name, sorted(validator.iter_errors(instance), key=lambda e: e.json_path)


def main() -> int:
    schemas = load_schemas()
    registry = build_registry(schemas)
    positives = sorted(EXAMPLES_DIR.glob("*.json"))  # non-recursive: excludes invalid/
    negatives = sorted(INVALID_DIR.glob("*.json"))
    if not positives:
        print("no positive examples found — refusing to pass vacuously", file=sys.stderr)
        return 1
    if not negatives:
        print("no negative fixtures found — refusing to pass vacuously", file=sys.stderr)
        return 1

    failures = 0

    for example in positives:
        result = errors_for(example, schemas, registry)
        if result is None:
            print(f"FAIL {example.name}: no schema mapping (add to PREFIX_TO_SCHEMA)")
            failures += 1
            continue
        schema_name, errors = result
        if errors:
            failures += 1
            print(f"FAIL {example.name} ({schema_name}):")
            for err in errors:
                print(f"  {err.json_path}: {err.message}")
        else:
            print(f"ok   {example.name} ({schema_name})")

    for fixture in negatives:
        result = errors_for(fixture, schemas, registry)
        if result is None:
            print(f"FAIL invalid/{fixture.name}: no schema mapping (add to PREFIX_TO_SCHEMA)")
            failures += 1
            continue
        schema_name, errors = result
        if errors:
            print(f"ok   invalid/{fixture.name} rejected by {schema_name} ({len(errors)} error(s))")
        else:
            failures += 1
            print(
                f"FAIL invalid/{fixture.name} ({schema_name}): expected rejection, validated clean"
            )

    if failures:
        print(f"\n{failures} failing fixture(s)", file=sys.stderr)
        return 1
    print(
        f"\nall {len(positives)} examples valid, all {len(negatives)} negative fixtures "
        f"rejected, against {len(schemas)} schemas"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
