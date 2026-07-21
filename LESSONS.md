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
