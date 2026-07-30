"""Generate TypeScript and C# consumer types from the published JSON Schemas.

The README has always told consumers to "generate consumer types from those schemas rather
than hand-mirroring". This makes that real: the generated files are committed, and CI runs
``--check`` so a schema change that nobody regenerated fails the build instead of silently
leaving downstream types wrong.

Sources are the five *published* contracts only -- the shapes a consumer actually receives:

  published-current.schema.json   the denormalized v1/current/*.json views
  published-index.schema.json     the v1/{dataset}/index.json listings
  published-entity.schema.json    the per-entity v1/{dataset}/{id}.json documents
  published-meta.schema.json      v1/meta.json
  published-aliases.schema.json   v1/{dataset}/aliases.json -- no envelope, so no $defs for the
                                  generic walk to pick up; `alias_type()` derives it separately
                                  from `additionalProperties`. It IS covered by --check.

The canonical ``*.schema.json`` files are deliberately NOT emitted: they describe what lives
in ``data/``, which is not a consumer surface.

Usage:
  python tools/gen_types.py            write the generated files
  python tools/gen_types.py --check    exit 1 if what is on disk differs (the CI gate)
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIR = ROOT / "schema" / "v1"
TS_OUT = ROOT / "cookbook" / "ts" / "src" / "generated" / "v1.ts"
CS_OUT = ROOT / "cookbook" / "csharp" / "Generated" / "V1.cs"

# (file stem, envelope type name). Order fixes the order of the generated output.
SCHEMAS = [
    ("published-current", "CurrentCollection"),
    ("published-index", "IndexCollection"),
    ("published-entity", "EntityDocument"),
    ("published-meta", "Meta"),
]

BANNER = (
    "GENERATED FILE -- DO NOT EDIT.\n"
    "Regenerate with `python tools/gen_types.py`; CI fails on drift (`--check`).\n"
    "Source of truth: schema/v1/published-*.schema.json\n"
)


def load(stem: str) -> dict[str, Any]:
    return json.loads((SCHEMA_DIR / f"{stem}.schema.json").read_text(encoding="utf-8"))


def pascal(name: str) -> str:
    # Split on anything that cannot appear in an identifier, so the wire name `$schema` becomes
    # `Schema`. The `[JsonPropertyName]` attribute carries the real key, so nothing is lost.
    return "".join(p[:1].upper() + p[1:] for p in re.split(r"[^0-9A-Za-z]+", name) if p)


def doc_of(schema: dict[str, Any], limit: int = 300) -> str | None:
    """A one-paragraph doc comment. Schema descriptions here run to hundreds of words; the
    long-form rationale belongs in the schema, not repeated into every generated language."""
    d = schema.get("description")
    if not d:
        return None
    d = " ".join(d.split())
    return d if len(d) <= limit else d[: limit - 1].rstrip() + "\u2026"


def enum_values(schema: dict[str, Any]) -> list[Any] | None:
    if "enum" in schema:
        return schema["enum"]
    if "const" in schema:
        return [schema["const"]]
    return None


class Emitter:
    """Walks a schema and collects named types. Subclasses render one target language."""

    def __init__(self) -> None:
        self.blocks: list[str] = []
        self.seen: dict[str, str] = {}  # type name -> rendered block, for dedupe
        # $defs that are constrained scalars (Slug, EntityRef, HistoricalDate) rather than
        # objects. A $ref to one must not emit a bare undeclared type name, so each language
        # decides: TypeScript names them (free, and `readonly id: Slug` documents itself),
        # C# inlines the underlying scalar (no `global using` noise at every ref site).
        self.scalars: dict[str, dict[str, Any]] = {}

    def note_scalar(self, name: str, schema: dict[str, Any]) -> None:
        self.scalars[name] = schema

    # --- to override -------------------------------------------------------------------
    def scalar(self, kinds: list[str], schema: dict[str, Any]) -> str: ...
    def array(self, inner: str) -> str: ...
    def nullable(self, inner: str) -> str: ...
    def literal_union(self, values: list[Any]) -> str: ...
    def free_map(self) -> str: ...
    def unknown(self) -> str: ...
    def render_object(
        self, name: str, schema: dict[str, Any], fields: list[tuple[str, str, bool, str | None]]
    ) -> str: ...
    def ref_scalar(self, name: str) -> str: ...

    # --- shared walk -------------------------------------------------------------------
    def type_of(self, schema: dict[str, Any], hint: str) -> str:
        """Render the type of ``schema``. ``hint`` names any anonymous object it contains."""
        if "$ref" in schema:
            name = schema["$ref"].rsplit("/", 1)[-1]
            return self.ref_scalar(name) if name in self.scalars else name

        vals = enum_values(schema)
        if vals is not None:
            nullable = None in vals
            rendered = self.literal_union([v for v in vals if v is not None])
            return self.nullable(rendered) if nullable else rendered

        # `anyOf`/`oneOf` is how the published schemas spell a nullable $ref:
        # {"anyOf": [{"$ref": "#/$defs/HistoricalDate"}, {"type": "null"}]}. Falling through to
        # the `type` lookup left `kinds` empty and emitted `unknown`/`JsonElement` for SEVEN
        # shipped fields -- including Version.valid_from and valid_to, the two the entire
        # half-open-window story rests on. SystemExit rather than a silent degrade on a shape
        # this cannot model: a codegen that refuses beats one that ships a wrong type.
        if branches := (schema.get("anyOf") or schema.get("oneOf")):
            real = [b for b in branches if b != {"type": "null"}]
            if len(real) != 1:
                kind = "anyOf" if "anyOf" in schema else "oneOf"
                raise SystemExit(f"gen_types: unmodelled {kind} at {hint} ({len(real)} branches)")
            out = self.type_of(real[0], hint)
            return self.nullable(out) if len(real) != len(branches) else out

        t = schema.get("type")
        kinds = [t] if isinstance(t, str) else list(t or [])
        nullable = "null" in kinds
        kinds = [k for k in kinds if k != "null"]

        if not kinds:
            out = self.unknown()
        elif "array" in kinds:
            out = self.array(self.type_of(schema.get("items") or {}, hint + "Item"))
        elif "object" in kinds:
            if schema.get("properties"):
                out = self.declare(hint, schema)
            else:
                out = self.free_map()
        else:
            out = self.scalar(kinds, schema)

        return self.nullable(out) if nullable else out

    def declare(self, name: str, schema: dict[str, Any]) -> str:
        """Emit a named object type, deduping by name and rejecting inconsistent reuse."""
        required = set(schema.get("required") or [])
        props = schema.get("properties") or {}
        # A name in `required` with no `properties` entry is unrepresentable, and silently
        # dropping it shipped an `EntityDocument` with no `Id` member at all -- the schema says the
        # field is mandatory and the generated type does not mention it. That is a schema bug worth
        # surfacing here, because this is the only pass that reads both halves together.
        if orphans := sorted(required - set(props)):
            raise SystemExit(
                f"gen_types: {name} marks {', '.join(orphans)} required with no `properties` "
                f"entry; fix the schema (a required field that cannot be typed is unusable)"
            )
        fields = [
            (prop, self.type_of(sub, name + pascal(prop)), prop in required, doc_of(sub))
            for prop, sub in props.items()
        ]
        block = self.render_object(name, schema, fields)
        prior = self.seen.get(name)
        if prior is not None:
            if prior != block:
                raise SystemExit(f"gen_types: {name} defined twice with different shapes")
            return name
        self.seen[name] = block
        self.blocks.append(block)
        return name


class TsEmitter(Emitter):
    def scalar(self, kinds: list[str], schema: dict[str, Any]) -> str:
        m = {"string": "string", "integer": "number", "number": "number", "boolean": "boolean"}
        return " | ".join(dict.fromkeys(m.get(k, "unknown") for k in kinds))

    def array(self, inner: str) -> str:
        return f"readonly {inner}[]" if inner.isidentifier() else f"readonly ({inner})[]"

    def nullable(self, inner: str) -> str:
        return f"{inner} | null"

    def literal_union(self, values: list[Any]) -> str:
        return " | ".join(json.dumps(v) for v in values)

    def free_map(self) -> str:
        return "Readonly<Record<string, unknown>>"

    def unknown(self) -> str:
        return "unknown"

    def ref_scalar(self, name: str) -> str:
        """Declare the constrained scalar as a named alias, once, then reference it by name."""
        if name not in self.seen:
            schema = self.scalars[name]
            underlying = self.scalar(
                [k for k in ([schema["type"]] if isinstance(schema.get("type"), str)
                             else list(schema.get("type") or [])) if k != "null"],
                schema,
            )
            block = []
            if d := doc_of(schema):
                block.append(f"/** {d} */")
            block.append(f"export type {name} = {underlying};")
            self.seen[name] = "\n".join(block)
            self.blocks.append(self.seen[name])
        return name

    def render_object(self, name, schema, fields) -> str:
        lines: list[str] = []
        if d := doc_of(schema):
            lines.append(f"/** {d} */")
        lines.append(f"export interface {name} {{")
        for prop, ts, required, fdoc in fields:
            if fdoc:
                lines.append(f"  /** {fdoc} */")
            key = prop if re.fullmatch(r"[A-Za-z_$][\w$]*", prop) else json.dumps(prop)
            lines.append(f"  readonly {key}{'' if required else '?'}: {ts};")
        if schema.get("additionalProperties") is not False:
            lines.append("  readonly [extra: string]: unknown;")
        lines.append("}")
        return "\n".join(lines)


class CsEmitter(Emitter):
    def scalar(self, kinds: list[str], schema: dict[str, Any]) -> str:
        m = {"string": "string", "integer": "int", "number": "double", "boolean": "bool"}
        if len(kinds) != 1:
            return "JsonElement"
        return m.get(kinds[0], "JsonElement")

    def array(self, inner: str) -> str:
        return f"IReadOnlyList<{inner}>"

    def nullable(self, inner: str) -> str:
        return inner if inner.endswith("?") else f"{inner}?"

    def literal_union(self, values: list[Any]) -> str:
        # Closed STRING sets stay `string`: several include null, and a C# enum would reject an
        # additively-introduced member, which `v1` explicitly permits. Homogeneous bool/int sets
        # do narrow though -- `unofficial` is `const: true`, and forcing a consumer through
        # JsonElement.GetBoolean() to read a required flag is a worse contract than `bool`.
        if all(isinstance(v, bool) for v in values):
            return "bool"
        if all(isinstance(v, str) for v in values):
            return "string"
        if all(isinstance(v, int) for v in values):
            return "int"
        return "JsonElement"

    def free_map(self) -> str:
        return "IReadOnlyDictionary<string, JsonElement>"

    def unknown(self) -> str:
        return "JsonElement"

    def ref_scalar(self, name: str) -> str:
        # No alias declared: a `Slug` is a string and C# gains nothing from restating that at
        # ~15 property sites, whereas a file-level alias would leak into consumer code.
        schema = self.scalars[name]
        kinds = ([schema["type"]] if isinstance(schema.get("type"), str)
                 else list(schema.get("type") or []))
        return self.scalar([k for k in kinds if k != "null"], schema)

    def render_object(self, name, schema, fields) -> str:
        lines: list[str] = []
        if d := doc_of(schema):
            lines.append(f"/// <summary>{d.replace('&', '&amp;').replace('<', '&lt;')}</summary>")
        lines.append(f"public sealed record {name}")
        lines.append("{")
        for i, (prop, cs, required, fdoc) in enumerate(fields):
            if i:
                lines.append("")
            if fdoc:
                esc = fdoc.replace("&", "&amp;").replace("<", "&lt;")
                lines.append(f"    /// <summary>{esc}</summary>")
            if not required and not cs.endswith("?"):
                cs = f"{cs}?"
            lines.append(f'    [JsonPropertyName("{prop}")]')
            # A non-nullable reference-typed auto-property with no initializer is CS8618 under
            # `<Nullable>enable</Nullable>`, and these are records a consumer only ever gets from
            # the deserializer. `required` both silences that correctly and makes System.Text.Json
            # throw when the schema says a field is mandatory and the payload omits it.
            #
            # Keyed on `required` ALONE, never on nullability: `required T?` is legal C# and means
            # exactly the contract -- presence enforced, value may be null. Excluding nullable
            # members dropped the modifier from all 41 required-and-nullable properties, so a
            # payload omitting `bsa_number` deserialised silently to null, indistinguishable from
            # an explicit null, and the C# and TypeScript files described different wire formats.
            modifier = "required " if required else ""
            lines.append(f"    public {modifier}{cs} {pascal(prop)} {{ get; init; }}")
        lines.append("}")
        return "\n".join(lines)


def kind_map(schema: dict[str, Any]) -> dict[str, str]:
    """Extract the ``if kind == X then items/... : $ref`` discrimination as a plain mapping.

    The published contracts select the item shape BY the envelope ``kind`` so a listing cannot
    publish another dataset's items at a right-looking URL. Consumers deserve that mapping as a
    type, not as prose.
    """
    out: dict[str, str] = {}
    for branch in schema.get("allOf") or []:
        cond = ((branch.get("if") or {}).get("properties") or {}).get("kind") or {}
        # published-current/-index discriminate one kind per branch with `const`; the entity
        # contract groups kinds that share a projection under an `enum` (every versioned entity
        # is one VersionedEntity). Both forms must land in the map or a consumer's switch on
        # `kind` silently loses the six most common document types.
        kinds = [cond["const"]] if "const" in cond else list(cond.get("enum") or [])
        if not kinds:
            continue
        m = re.search(r'"\$ref":\s*"#/\$defs/(\w+)"', json.dumps(branch.get("then") or {}))
        if m:
            for kind in kinds:
                out[kind] = m.group(1)
    return out


def build(emitter_cls: type[Emitter]) -> tuple[Emitter, dict[str, dict[str, str]]]:
    em = emitter_cls()
    maps: dict[str, dict[str, str]] = {}
    # Constrained-scalar $defs are collected across EVERY schema before anything is declared:
    # published-entity's Version/Event reference EntityRef from the same $defs block, so a
    # single forward pass would emit the bare name before it was known to be a scalar.
    loaded = [(stem, envelope, load(stem)) for stem, envelope in SCHEMAS]
    for _, _, schema in loaded:
        for def_name, sub in (schema.get("$defs") or {}).items():
            if sub.get("type") == "object" and sub.get("properties"):
                continue  # an object record -- declared in the second pass below
            # A constrained scalar is a PRIMITIVE type only. `array` and `object` are also plain
            # `type` strings, so testing `isinstance(type, str)` alone would mis-file a bare
            # `{"type": "array"}` or `{"type": "object"}` $def as a scalar and drop it silently.
            t = sub.get("type")
            if enum_values(sub) is None and t in ("string", "number", "integer", "boolean"):
                em.note_scalar(def_name, sub)
                continue
            # Neither an object record nor a constrained scalar, so no bucket renders it: a $ref
            # would emit a bare, undeclared type name (does not compile) and an unref'd def would
            # vanish silently. Refuse -- the same stance type_of takes on an unmodellable anyOf.
            # The shapes that land here are an `enum` $def, a `["string","null"]` union, an
            # `allOf`, an `array`, and a bare `object` with no properties. None exists in
            # schema/v1/ today; model it in note_scalar/type_of before adding one to a schema.
            raise SystemExit(
                f"gen_types: $def {def_name!r} has an unmodelled shape (type={t!r}, "
                f"keys={sorted(k for k in sub if k not in ('title', 'description'))}); a $ref to it "
                f"would emit an undeclared type name -- model it in build()/type_of first"
            )
    for _, envelope, schema in loaded:
        for def_name, sub in (schema.get("$defs") or {}).items():
            if sub.get("type") == "object" and sub.get("properties"):
                em.declare(def_name, sub)
        em.declare(envelope, schema)
        if km := kind_map(schema):
            maps[envelope] = km
    return em, maps


# Unqualified C# type names that a `using` alias cannot see, because a using alias is resolved
# before the file's own using directives. Value types and `string` need no entry.
QUALIFY = {
    "JsonElement": "System.Text.Json.JsonElement",
    "IReadOnlyDictionary<string, JsonElement>":
        "System.Collections.Generic.IReadOnlyDictionary<string, System.Text.Json.JsonElement>",
}


def alias_type(em: Emitter) -> str:
    """The alias map, DERIVED from published-aliases.schema.json rather than hand-written.

    This file is the one published surface with no envelope, so it has no ``$defs`` for the
    generic walk to pick up -- which is why it was previously a hardcoded string literal that
    ``--check`` could not see. Widening ``additionalProperties`` in the schema would then have
    left both languages silently wrong while the drift gate stayed green.
    """
    schema = load("published-aliases")
    value = em.type_of(schema.get("additionalProperties") or {}, "AliasValue")
    # A JSON object key is always a string; `propertyNames` constrains its FORMAT (slug pattern),
    # not its type, so deriving the key type from it would yield `unknown`/`JsonElement`.
    key = em.scalar(["string"], {})
    doc = (
        "The bare `{retired-id: surviving-id}` map published at v1/{dataset}/aliases.json.\n"
        "Deliberately unenveloped and carrying no `$schema`: its only sane use is a direct\n"
        "lookup, and a `$schema` key in a bare map would read as an alias."
    )
    if isinstance(em, TsEmitter):
        body = "\n".join(f" * {ln}" for ln in doc.splitlines())
        return f"/**\n{body}\n */\nexport type AliasMap = Readonly<Record<{key}, {value}>>;"
    # C# has no structural type alias, so the honest equivalent is a `global using` alias rather
    # than a wrapper class with nothing in it. A `using` alias resolves BEFORE the file's own
    # `using` directives, so every name in it must be fully qualified -- an unqualified
    # `JsonElement` (what a widened `additionalProperties` yields) would be CS0246.
    key, value = (QUALIFY.get(t, t) for t in (key, value))
    return (
        f"// {' '.join(doc.split())}\n"
        f"global using AliasMap = "
        f"System.Collections.Generic.IReadOnlyDictionary<{key}, {value}>;"
    )


def ts_source() -> str:
    em, maps = build(TsEmitter)
    parts = ["/**\n * " + BANNER.strip().replace("\n", "\n * ") + "\n */\n"]
    parts.extend(em.blocks)
    for envelope, km in maps.items():
        name = envelope.replace("Collection", "") + "ByKind"
        # Kind values are hyphenated ("merit-badge"), so the key MUST stay quoted -- an
        # identifier-ised key would not match any envelope the API actually publishes.
        rows = "\n".join(f"  readonly {json.dumps(k)}: {v};" for k, v in sorted(km.items()))
        parts.append(
            f"/** Item shape selected by the envelope `kind` of a {envelope}. */\n"
            f"export interface {name} {{\n{rows}\n}}"
        )
    parts.append(alias_type(TsEmitter()))
    return "\n\n".join(parts) + "\n"


def cs_source() -> str:
    em, maps = build(CsEmitter)
    body = "\n\n".join(em.blocks)
    lines = [
        "// " + BANNER.strip().replace("\n", "\n// "),
        "",
        # A `global using` alias is a using directive, so it MUST precede the namespace.
        alias_type(CsEmitter()),
        "",
        "using System.Text.Json;",
        "using System.Text.Json.Serialization;",
        "",
        "namespace OpenScoutApi.Generated;",
        "",
    ]
    for envelope, km in maps.items():
        pairs = ", ".join(f'["{k}"] = "{v}"' for k, v in sorted(km.items()))
        name = envelope.replace("Collection", "") + "ByKind"
        lines += [
            f"/// <summary>Item record name selected by the envelope kind of a {envelope}."
            "</summary>",
            f"public static class {name}",
            "{",
            "    public static readonly IReadOnlyDictionary<string, string> Map =",
            f"        new Dictionary<string, string> {{ {pairs} }};",
            "}",
            "",
        ]
    # File-scoped namespace, so record declarations sit at column 0 unindented.
    return "\n".join(lines) + "\n" + body + "\n"


def main() -> int:
    check = "--check" in sys.argv
    targets = {TS_OUT: ts_source(), CS_OUT: cs_source()}
    drift = []
    for path, src in targets.items():
        if check:
            have = path.read_text(encoding="utf-8") if path.exists() else None
            if have != src:
                drift.append(path.relative_to(ROOT).as_posix())
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(src, encoding="utf-8", newline="\n")
    if check:
        if drift:
            print("gen_types: generated types are stale: " + ", ".join(drift))
            print("           run `python tools/gen_types.py` and commit the result")
            return 1
        print(f"gen_types: OK, {len(targets)} generated files match schema/v1/")
        return 0
    for path in targets:
        print(f"gen_types: wrote {path.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
