"""Validate schema/v1/examples/*.json against the canonical schemas.

Seed of the future CI validation gate (see TODO.md "Pipeline validator" for the
cross-file rules JSON Schema cannot express). Exits nonzero on any failure.

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

# Example filename prefix -> schema file. Longest-prefix wins ("merit-badge-" before "camp-" is
# irrelevant today, but keep prefixes unambiguous when adding datasets).
PREFIX_TO_SCHEMA = {
    "council-": "council.schema.json",
    "territory-": "territory.schema.json",
    "camp-": "camp.schema.json",
    "merit-badge-": "merit-badge.schema.json",
    "requirement-set-": "requirement-set.schema.json",
    "events-": "event.schema.json",
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


def main() -> int:
    schemas = load_schemas()
    registry = build_registry(schemas)
    examples = sorted(EXAMPLES_DIR.glob("*.json"))
    if not examples:
        print("no examples found — refusing to pass vacuously", file=sys.stderr)
        return 1

    failures = 0
    for example in examples:
        schema_name = schema_for(example.name)
        if schema_name is None:
            print(f"FAIL {example.name}: no schema mapping (add to PREFIX_TO_SCHEMA)")
            failures += 1
            continue
        validator = Draft202012Validator(
            schemas[schema_name],
            registry=registry,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        )
        instance = json.loads(example.read_text(encoding="utf-8"))
        errors = sorted(validator.iter_errors(instance), key=lambda e: e.json_path)
        if errors:
            failures += 1
            print(f"FAIL {example.name} ({schema_name}):")
            for err in errors:
                print(f"  {err.json_path}: {err.message}")
        else:
            print(f"ok   {example.name} ({schema_name})")

    if failures:
        print(f"\n{failures} failing example(s)", file=sys.stderr)
        return 1
    print(f"\nall {len(examples)} examples valid against {len(schemas)} schemas")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
