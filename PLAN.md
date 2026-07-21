# Open Scout API — Plan

Open, versioned, machine-readable datasets for Scouting America (BSA) reference data —
councils, territories, camps, merit badges, requirements, and related entities — published
as static JSON with published JSON Schemas, so anyone can build tools on top without
scraping or a server.

**Spin-off of [`camp-finder`](../camp-finder)** (`D:\repos\claude\personal\camp-finder`).
Camp-finder proved the model (data-as-code, provenance-first, validation gate, static
distribution) for one vertical (summer camp sessions). This project generalizes the
*reference* layer — the slowly-changing structural data — and adds the temporal dimension
camp-finder deliberately skipped. Camp-finder is intended to become the first downstream
consumer (its council registry would read this dataset instead of Wikipedia).

> **Unofficial community project.** Not affiliated with, endorsed by, or sponsored by
> Scouting America. Aggregates public information with per-fact provenance.

---

## 1. Problem

No official machine-readable data exists for any BSA structural data (verified 2026-07-21:
scouting.org offers only an HTML council locator and HTML badge lists). The community
relies on Wikipedia tables, usscouts.org (robots.txt forbids scraping its camp database),
and stale wikis. Everyone building scouting software re-scrapes or hand-copies the same
facts.

The hard part is **history**: councils merge and rename, regions became territories (2021),
badges get introduced/retired/renamed, requirements are revised. A snapshot dataset rots;
a temporal dataset answers both "what is true now" and "what was true then."

## 2. Design principles (inherited from camp-finder, plus temporal)

1. **Data-as-code.** Canonical data lives in this repo as human-reviewable JSON. Writes
   happen via PRs; a validation gate (schema + referential + sanity) blocks bad merges.
2. **Provenance on every fact.** Every version record and event carries
   `sources[] + method + verified_at + confidence`. LLM-extracted facts must declare
   `confidence < 1.0`. Curated > community > scraped > LLM precedence when merging
   (camp-finder LESSONS: encode method precedence *before* automated passes overlap
   curated data).
3. **Identity is permanent and separate from state.** Entity IDs are opaque slugs, never
   reused, never deleted. Names, numbers, ownership, and status are *versioned attributes*.
4. **Change is an explicit event.** Mergers, splits, renames, reorganizations,
   introductions, and retirements are first-class records linking predecessor/successor
   entities — not silent field overwrites.
5. **Canonical vs published.** The normalized canonical tree is authoritative; a build
   step later emits denormalized consumer projections (`current/` snapshot + per-entity
   history). Consumers never need to reassemble the temporal model to get "the current
   council list."
6. **Idempotent, non-clobbering enrichment.** Any future automated pass fills blanks by
   default; destructive refills require an explicit flag; an `unknown` result never
   overwrites a known value.
7. **Open vocabularies where growth is expected.** Program types, features, tags are
   string codes with a committed registry file — adding one is a data change, not a
   schema change. Closed enums only where the domain is genuinely closed (event types,
   provenance methods).

## 3. Core temporal model

Valid-time only (when a fact was true in the world). We deliberately skip full
bitemporality; provenance `verified_at` covers "when we learned it" informally. Nothing
in the ID scheme precludes adding record-time later.

### 3.1 Entity file (one JSON file per entity)

```jsonc
// data/councils/cascade-pacific.json
{
  "id": "cascade-pacific",           // dataset-scoped slug, permanent
  "kind": "council",
  "versions": [                       // record-level snapshots, ordered, non-overlapping
    {
      "valid_from": "1993",           // HistoricalDate: YYYY | YYYY-MM | YYYY-MM-DD; null = unknown
      "valid_to": null,               // null = current
      "name": "Cascade Pacific Council",
      "bsa_number": 492,
      // ...dataset-specific attributes...
      "provenance": { "sources": [...], "method": "curated", "verified_at": "2026-07-21", "confidence": 1.0 }
    }
  ],
  "notes": null
}
```

- **Record-level SCD-2**, not attribute-level: each version is a full snapshot of the
  attributes during its validity window. Changes are rare (a council renames a few times
  per century); full snapshots diff cleanly and are simple to consume.
- Validity windows are **half-open `[valid_from, valid_to)`**: a successor's `valid_from`
  equals its predecessor's `valid_to` (see the Citizenship in Society example — the
  2022-07-01 boundary appears in both windows). Non-overlap checks MUST compare half-open.
- Non-overlap and ordering of versions is a **pipeline validator** rule (not expressible
  in JSON Schema).
- "Current" = the version with `valid_to: null`. Retired entities have no null-`valid_to`
  version; their fate is in the events file.

### 3.2 Events file (one per dataset)

```jsonc
// data/councils/_events.json  (underscore cannot collide with entity slugs)
{
  "events": [
    {
      "id": "cascade-pacific-formation-1993",
      "type": "merged",               // closed enum, see schema/v1/common.schema.json
      "date": "1993",
      "participants": [
        { "ref": "council:columbia-pacific", "role": "predecessor" },
        { "ref": "council:portland-area",    "role": "predecessor" },
        { "ref": "council:cascade-pacific",  "role": "successor" }
      ],
      "notes": null,
      "provenance": { ... }
    }
  ]
}
```

- Events are stored **once**, normalized, in the dataset's `_events.json` — never
  duplicated into entity files (dual-write hazard). The future build step projects
  relevant events into each entity's *published* JSON.
- Roles: `subject` (single-entity events like `renamed`), `predecessor`, `successor`,
  `continuing` (an absorption where one side keeps its identity).
- A cross-file validator rule (pipeline, later) checks every participant ref resolves and
  that event dates are consistent with version boundaries.

### 3.3 Conventions

| Concern | Rule |
|---|---|
| Entity ID | slug `^[a-z0-9][a-z0-9-]*$`, unique within dataset, permanent. Name-derived; disambiguate historical collisions with an era suffix (`-1935`). Never encode mutable facts (council number) in the ID. |
| Cross-dataset ref | `"{kind}:{slug}"` string, e.g. `council:cascade-pacific`, `territory:western-region` |
| Dates (historical) | `HistoricalDate` string: `YYYY`, `YYYY-MM`, or `YYYY-MM-DD` — real history is often year-precision only |
| Dates (bookkeeping) | full ISO dates (`verified_at`, `accessed`) |
| File layout | `data/<dataset-plural>/<slug>.json` + `data/<dataset-plural>/_events.json` |
| Schemas | JSON Schema draft 2020-12 in `schema/v1/`, `$id` base `https://sethmay.github.io/open-scout-api/schema/v1/` (placeholder until publication URL is final — see TODO) |
| Canonical serialization | UTF-8, LF, 2-space indent, keys as authored (schemas use `additionalProperties`/`unevaluatedProperties: false` to keep canonical files strict) |
| Camp IDs | keep camp-finder's state-prefixed slugs (`or-camp-meriwether`) for painless import |

## 4. Repository layout

```
open-scout-api/
  PLAN.md                     # this file
  TODO.md                     # dataset catalog + active queue (WORKFLOW.md conventions)
  CHANGELOG.md                # per-merge, semver skill conventions
  WORKFLOW.md                 # agent workflow (worktrees, review gate)
  schema/v1/
    common.schema.json        # shared $defs: Slug, EntityRef, HistoricalDate, StateCode,
                              #   Source, Provenance, VersionBase, Event
    council.schema.json       # data/councils/<slug>.json
    territory.schema.json     # data/territories/<slug>.json (territories, regions, areas)
    camp.schema.json          # data/camps/<slug>.json
    merit-badge.schema.json   # data/merit-badges/<slug>.json
    requirement-set.schema.json  # data/requirement-sets/<slug>.json (immutable documents)
    event.schema.json         # data/<dataset>/_events.json
    examples/                 # ILLUSTRATIVE instances — not verified data, never published
  tools/
    validate_examples.py      # validates examples against schemas (CI gate seed)
  data/                       # EMPTY until population phase (separate agent/session)
```

## 5. Dataset-specific schema notes

- **council** — versions carry `name`, `bsa_number` (nullable; numbers are attributes,
  not identity), `hq_city`/`hq_state`, `website`, `states_served[]`, `territory` (ref;
  time-varying membership falls out of versioning). Mergers/absorptions/renames are events.
- **territory** — one dataset for all national geographic subdivisions across eras:
  `division_type: council_service_territory | national_service_territory | region | area`
  on each version, `parent` ref for areas-within-regions. Lineage of the 16 numbered
  territories: 4 regions (pre-2021) → 16 National Service Territories (2021) → renamed
  Council Service Territories with 2 merged into neighbors → 14 CSTs (2024). This full
  chain is the model's acceptance test.
- **camp** — one entity for every kind of scout camp, classified on three orthogonal
  facets: `camp_type` (single: reservation / resident_camp / high_adventure_base /
  short_term_camp / day_camp / program_center / other), `program_types[]` (what it offers,
  multi), and `operator` (council / national / other / unknown) + `council` ref (national
  bases like Philmont have operator=national, council=null). `parent` (camp ref) nests a
  sub-camp under a reservation (children populated later). Plus `operating_status`,
  location, `website`, `features[]`. **Sessions/fees/dates stay in camp-finder / the
  council site** — this dataset is the registry + classification + history layer, joined by
  camp id, not the operational layer.
- **merit-badge** — versions carry `name`, `eagle_required` (denormalized convenience;
  purist source is the Eagle rank requirement set), `tags[]`, `description`.
  Introduction/discontinuation/supersession (`computers` → `digital-technology`) are
  events; "status" is derivable (published projection will materialize it).
- **requirement-set** — immutable dated documents, not versioned entities:
  `subject` ref (merit badge and rank reuse one schema), `effective_from/to`,
  `supersedes` chain, `source_document`, recursive `requirements[]` tree (`number`,
  optional verbatim `text`, optional paraphrased `summary`, `choose` N-of-children).
  ⚠ **Copyright**: requirement *text* is Scouting America's. Structure, numbering,
  effective dates, and paraphrased summaries are safe; every set carries
  `includes_official_text` so a publish step can strip/withhold verbatim text. Default
  policy: **populate summaries, not text** until the licensing question is resolved.
- **rank** — advancement ranks as versioned entities (like merit-badge): `name`,
  `program` (`scouts_bsa`), `order` (1–7). Requirement CONTENT lives in `requirement-set`
  docs (`subject: rank:<slug>`), not the entity. Seeded with the 7 Scouts BSA ranks; their
  requirement history is populated across editions (2016-2023 from usscouts.org + current
  2024) with `supersedes` chains + effective windows. The same schema will hold
  Cub/Venturing/Sea Scout ranks later.
- **award** — earned awards & recognitions (religious emblems, training awards, scouting
  honors / special recognitions) as versioned entities. FACTS only: `name`, `category`
  (religious_emblem | training_award | scouting_honor | special_recognition), `audience`,
  `square_knot_no` + `insignia_nos[]` (catalog numbers), `wear`. The optional `summary`
  field is left null (strictly facts); no verbatim Guide to Awards & Insignia text (© Scouting America). Excludes plain uniform
  insignia and per-faith religious-emblem programs; earning requirements (where a source
  exists) would reuse `requirement-set` with `subject: award:<slug>`.

## 6. Distribution (LIVE as of 0.3.0)

- **GitHub repo = database; GitHub Pages = read API.** `tools/build.py` denormalizes the
  canonical `data/` tree into `dist/` (git-ignored; built in CI): `v1/meta.json`,
  `v1/{councils,territories}/index.json` + per-entity `<id>.json` (canonical entity +
  folded lifecycle events), `v1/current/{councils,territories}.json` (flat, current-only
  projections), and `schema/v1/*` (served at the path matching every schema's `$id`,
  `https://sethmay.github.io/open-scout-api/schema/v1/`). Build validates its `current/`
  output against `schema/v1/published-current.schema.json` (fail-fast).
- **CI:** `.github/workflows/pages.yml` runs the validators (gate) + build on every
  push/PR and deploys to Pages only on `main` (deploy `needs:` the gate). One-time manual
  step: repo Settings → Pages → Source = GitHub Actions.
- **jsDelivr over git tags** for a CDN of the raw canonical files + immutable pinning
  (`cdn.jsdelivr.net/gh/sethmay/open-scout-api@<tag>/...`).
- **Releases = immutable snapshots** (future): ship the JSON tree + a generated SQLite
  artifact (and optionally Parquet); archive tagged releases to Zenodo for a DOI.
- **License: CC BY-NC-SA 4.0** for data (`LICENSE`/`NOTICE.md`); pipeline code MIT.

## 7. Phases

1. **Schemas (this phase).** Core temporal model + the five dataset schemas + examples +
   example validator. Gate: every example validates; review gate passed.
2. **Population — councils + territories** (planned for a separate agent/session, likely
   Opus). Smallest datasets; forces the temporal model to be right first. Seed sources:
   camp-finder `data/councils/*.json` (235 stubs, 100% websites, curated seed
   `data/council-websites.json`), Wikipedia council list + council histories. Include the
   known mergers already surfaced by camp-finder (302/303 → Mississippi Riverlands,
   695 → Sioux) as proper events. Gate: full current council list matches camp-finder's;
   ≥ a handful of historically-verified merger events with sources.
3. **Population — merit badges + requirement sets.** ✅ Seeded: catalog (0.4.0) = 142
   badges w/ Eagle flags + CiS/Computers lifecycles; requirement sets (0.5.0) = 141 docs
   with the full requirement tree (numbering/nesting/choose-N/options) + verbatim text
   marked © Scouting America (`text_rights`, excluded from the data license). Pending:
   historical requirement revisions + discontinued-badge backfill.
4. **Camps import.** ✅ Done (0.7.0): 469 camps imported from camp-finder keeping ids
   (`method: imported`), classified by camp_type + operator; 4 national HA bases added.
   Reservation `parent` nesting + historical camps pending.
5. **Build + publish.** Pipeline emitting `current/` + per-entity history projections,
   `index.json` per dataset, CI validation gate, GitHub Pages deploy, first tagged
   release.
6. **Automation + community.** Refresh passes, correction intake (issue forms → PR),
   camp-finder consumes the published council dataset.

## 8. Session-restart pickup notes

- **Workflow:** WORKFLOW.md is binding — feature worktrees under `.claude/worktrees/`,
  commit before review, `reviewer` agent gate writes to `.workbench/reviews/`, merge
  `--no-ff`, then semver bump + CHANGELOG sha backfill (see `skill://semver`).
- **Where things stand:** see CHANGELOG.md (shipped) and TODO.md (queue + full dataset
  catalog with sources/priorities).
- **Key reference:** camp-finder's `LESSONS.md` and `models.py` — the provenance shape,
  validator discipline, and merge-precedence warnings there directly inform this repo's
  pipeline phase.
- **Population brief (for the future data agent):** work one dataset per worktree; every
  record needs real sources (no bare `confidence: 1.0` without a checkable citation);
  examples under `schema/v1/examples/` are *illustrative only* — do not import them as
  data; run `python tools/validate_examples.py` (extend it to validate `data/` once data
  exists).
