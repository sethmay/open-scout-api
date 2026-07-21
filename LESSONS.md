# Lessons

Curated, durable, project-specific engineering lessons distilled from review-gate
`...-lessons.md` files under `.workbench/reviews/` (WORKFLOW.md step 4). Dedupe and
fold; read before similar work.

## Schemas / validation

- **Schema fixtures MUST include expected-fail cases for every strictness/conditional
  keyword** (`additionalProperties`/`unevaluatedProperties: false`, `anyOf`, `if/then`).
  A positive-only validator stays green when the guard is deleted. Inherited from
  camp-finder ("make every guard bite"; "a CI gate must be non-vacuous"); encoded in
  `schema/v1/examples/invalid/` + the negative pass in `tools/validate_examples.py`.
- **Every temporal/structural invariant stated in PLAN or schema prose MUST have a
  validator rule that bites**, or it silently rots. Data-level invariants JSON Schema
  can't express live in `tools/validate_data.py`: id==filename, refs resolve, half-open
  non-overlapping windows, only-final-version-open, unique event ids, and the
  retired-entity rule below. Verify each with a deliberate failing case.
- **Draft 2020-12 composition for entity versions:** sibling `allOf: [{$ref: VersionBase}]`
  + local `properties` + `unevaluatedProperties: false`. The `$ref`'d base's properties
  count as evaluated, so unknowns are rejected while base fields pass. NEVER switch the
  sub-def to `additionalProperties: false` — it would reject the base fields.
- **`format`/`pattern`/bounds keywords are type-scoped**, so `type: ["string","null"] +
  format: "uri"` is safe (no-ops on null). `anyOf: [{$ref: X}, {type: null}]` is only
  *required* when the constraint is a `$ref` (can't inline a $ref into a type array).
  Both idioms coexist deliberately in these schemas — don't "normalize" one into the other.

## Temporal model

- **Validity windows are half-open `[valid_from, valid_to)`** — a successor's `valid_from`
  equals its predecessor's `valid_to`. Any non-overlap validator MUST compare half-open or
  it false-positives on every adjacent pair (PLAN §3.1; Citizenship in Society example).
- **A retired entity MUST NOT keep a `valid_to: null` version** — null means "current"
  and it leaks into the current-list projection. If the end date is unverified, do NOT
  default to null; use a documented coarse bound from the evidence (e.g. `2026` = the year
  first observed absent from official maps) + a note, never a fabricated exact date.
  `validate_data.py` enforces this: an entity that is the `subject` of a `discontinued`
  event or a `predecessor` in `merged`/`absorbed`/`split` must have no open version.
- **Inference-honesty discipline for seeded data:** unverified facts get `date: null` +
  confidence 0.4–0.6 + an explicit "unverified/presumed" note; sourced facts get real
  dates + citations at 0.8+. Never fabricate a date or a merge target to look complete.

## Data safety / licensing

- **`includes_official_text` ⇔ any `Requirement.text` present is a cross-node invariant
  JSON Schema cannot express.** It is a pipeline rule (TODO.md "Pipeline validator") and
  the publish-time lever for withholding Scouting America's copyrighted requirement text.
  Never trust the boolean alone.
- **Illustrative examples carry realistic names/URLs/high confidence; the "do not import"
  marker is prose in `notes`.** The real safety boundary is the `schema/v1/examples/`
  directory being never-published and never globbed with `data/`. If examples ever move or
  a pass globs them alongside data, add a structural sentinel or cap their confidence first.
- **Keep a documented safeguard and its mechanism in sync, in the same commit.** NOTICE.md
  claimed `maps/` (proprietary source images) was git-ignored while the committed
  `.gitignore` had no such entry — a doc-vs-repo drift that defeats the protection.
  Gotcha: a `printf >> .gitignore` run in the MAIN checkout does not touch the feature
  worktree's file; edit the worktree copy. When a doc asserts "X is git-ignored", add/verify
  the `.gitignore` line in the same change (proprietary map images are facts-only sources —
  extract facts, never redistribute the images).

## Build / publish (dist/ + GitHub Pages)

- **Deploy-on-every-push + the semver PENDING→backfill two-step makes the build's version
  lag one commit.** `build.py` reads the newest `## X.Y.Z` CHANGELOG heading, but at
  feature-merge time the entry is still `PENDING` (newest heading is the *previous*
  version). Fix used: if a `PENDING` line exists, stamp `X.Y.Z+unreleased` so the deployed
  version is honest during the lag; it self-clears when the bump commit lands. For exact
  version pinning, consumers use git tags / jsDelivr, not `meta.json`.
- **A published JSON Schema shipped as a consumer contract MUST have a root
  (`type`/`properties`/`$ref`), not just `$defs`.** A `$defs`-only file validates nothing
  when a consumer points a validator at it (vacuous pass); it "worked" only via the
  producer's inline `{**schema,"$ref":"#/$defs/X"}`. Give it a real root and delete/wire
  every `$def` (`published-current.schema.json`).
- **`format` (uri/date/date-time) is a silent no-op unless the format extra is installed.**
  CI must `pip install "jsonschema[format]"` (pulls rfc3987 etc.) for those to bite;
  patterns/`required`/`additionalProperties`/bounds always bite. (Corollary of the
  type-scoped-format note above — a `format` keyword that neither applies to the type nor
  has its checker installed guards nothing.)
- **Derive a denormalized cross-entity field from the referenced entity, not from a slug
  regex.** `territory_number` now comes from the referenced territory's canonical `number`,
  not `cst-(\d+)` on the slug — the regex silently yields null for any future current
  entity whose slug breaks the convention while the canonical number is right there.

## Datasets / catalog seeding

- **`validate_data.py`'s `ENDED_AS_PRED` must stay in lockstep with the `EventType`
  enum.** The retired-entity invariant only fires for an entity ended as a `predecessor`
  if its event type is in that set (`merged`/`absorbed`/`split`/`superseded`). Add any new
  ending event type there or a retired entity can silently keep an open (current) version.
- **The published `items` `oneOf` union is safe only while every current-projection type
  has disjoint `required` fields under `additionalProperties:false`.** CurrentCouncil /
  CurrentTerritory / CurrentMeritBadge don't overlap, so exactly one matches. A future
  current type that isn't disjoint makes `oneOf` reject valid items (0 or 2 matches) — keep
  them disjoint or switch to a discriminated union on `kind`.
- **A retired entity's `index.json` row reflects its LAST version** (e.g. Citizenship in
  Society shows `eagle_required:true, current:false`), so a raw count of a boolean facet in
  `*/index.json` exceeds the `current/*.json` count. Intentional + consistent across
  datasets; consumers filter `current:true` for current facts.
- **Catalog-layer house style for copyright-sensitive data:** publish only catalogue facts
  + curated flags, keep `description` null, cite the source + authoritative URL, and set
  `confidence < 1` + a note when dates are approximate. Requirement/verbatim TEXT stays out
  of scope until licensing is resolved (merit-badge catalog: facts only, no requirement text).
