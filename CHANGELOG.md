# Changelog

One section per merge into `main`; newest first. Conventions: `skill://semver`.
Version anchors: this file only (no package manifests yet — add here when one appears).

## 0.16.0 (minor) — 2026-07-21

- `PENDING` Enrich the published **`current/*.json` projection contract** for downstream
  consumers (camp-finder cutover, tier 1). Every current item now carries `verified_at` +
  `method` (not just `confidence`) — powers freshness/staleness UX. `current/camps.json`
  additionally inlines its council (`council_name`, `council_website`, `council_number`,
  resolved against the canonical council so defunct-council camps still resolve; the 4
  national-base camps with no council get nulls) and a guaranteed resolved `url` (camp site →
  else council site) so consumers need zero cross-file joins. Documented the projection as an
  **additive-only `v1` contract** (README + schema `description`) — also covers the
  codegen-from-schema request. Pure `build.py` + `published-current.schema.json`; additive and
  backward-compatible. 1361 entities validate.

## 0.15.0 (minor) — 2026-07-21

- `9e353b8` Add **Cub Scout, Venturing, and Sea Scout advancement ranks** — completing the
  rank vertical across every BSA program. Ranks grew 7 → **21** (6 Cub: Lion, Tiger, Wolf,
  Bear, Webelos, Arrow of Light; 4 Venturing: Venturing, Discovery, Pathfinder, Summit; 4 Sea
  Scout: Apprentice, Ordinary, Able, Quartermaster), each with a current `requirement-set`
  (requirement-sets 174 → **188**; 579 requirement-text nodes). Structured from OFFICIAL
  sources — scouting.org Cub adventure + Venturing rank pages and the official 2026 Sea Scout
  rank PDFs (Venturing rank via usscouts.org) — with every requirement `text` verified verbatim
  (whitespace-insensitive substring) against its source before baking; tree structure organized
  with LLM assistance (`method: scraped`, conf 0.9). Cub ranks model required Adventures (Bobcat
  folded in with its sub-requirements) + elective Adventures (`choose`). Requirement text ©
  Scouting America (`text_rights`). New `seed_program_ranks.py` + `seed_program_rank_requirements.py`
  + committed `tools/program_rank_requirements.json`. 1361 entities validate.

## 0.14.0 (minor) — 2026-07-21

- `f9f6e33` Add **council historical lineage**. Councils grew 235 → **419** (229 current +
  190 historical) and council events 7 → **119**. Extracted as facts (`method:
  llm_extraction`, conf 0.7–0.8) from each current council's English Wikipedia article and
  reconciled by rule: **141** founding dates (earliest-version `valid_from`), **57** prior-name
  rename chains (dated `versions`), **112** new merger/absorption events, **184** named
  predecessor councils added as defunct (retired) entities, and `states_served` filled for
  **208** councils. bsa-number continuity decides rename-vs-merge; a predecessor whose slug
  matches a still-live council is skipped (never retired) and logged; each predecessor is
  retired once. Facts only — no article prose is reproduced. New `seed_council_history.py` +
  committed `tools/council_history_facts.json`, layered idempotently onto the existing council
  files. 1347 entities validate.

## 0.13.0 (minor) — 2026-07-21

- `970ea2c` Add the Order of the Arrow lodges dataset: 238 `oa-lodge` entities from the
  official OA lodge locator feed (oa-bsa.org), each linked to its chartering `council`
  (238/238) with OA section/region, HQ city/state + coordinates, and website. Lodge officer
  names and contact emails from the feed are excluded as PII. New `oa-lodge` schema +
  `CurrentOALodge` published contract; wired through stamp_schema / validate_data / build /
  build_sqlite. 1163 entities validate.

## 0.12.0 (minor) — 2026-07-21

- `f0a5f29` Release automation + durability: `tools/build_sqlite.py` compiles the data into a
  queryable SQLite artifact (typed tables mirroring the `current` projections + full JSON per
  row for `json_extract`); `.github/workflows/release.yml` publishes a GitHub Release (JSON
  tarball + SQLite) on any `v*` tag; created `v*` git tags for all shipped versions at their
  CHANGELOG shas; added `.zenodo.json` for DOI archiving; documented jsDelivr pinning + SQLite
  in the README. No data content changed.

## 0.11.0 (minor) — 2026-07-21

- `f590059` Add a `$schema` reference to every canonical `data/**.json` file (absolute
  published URL per dataset) so contributors get live editor validation + autocomplete in
  the PR-based workflow. Permitted `$schema` in the 8 canonical schemas; new
  `tools/stamp_schema.py` normalizer stamps (and `--check`s) all 1102 files; `validate_data.py`
  now enforces the ref. `build.py` strips it from the per-entity/doc dist files (they carry
  `events`/join fields and aren't canonical-shaped) and points `dist/v1/current/*.json` at
  `published-current.schema.json`. No entity/data content changed.

## 0.10.0 (minor) — 2026-07-21

- `e8422e7` Add historical rank requirement revisions: 26 requirement-sets for the 2016-2023
  editions of all 7 Scouts BSA ranks, scraped from the U.S. Scouting Service Project archive
  (usscouts.org). One doc per distinct edition (same-year editorial + org-rename-only diffs
  collapsed), with effective windows + `supersedes` chains flowing into the current 2024 sets.
  Verbatim requirement text © Scouting America (`text_rights`); structure/numbering from the
  pages' `<ol>` markup (stdlib parser); all 647 requirement texts verified verbatim against
  source. `method: scraped`, confidence 0.8. Requirement-sets: 148 → 174. Current 2024 rank
  sets now carry `supersedes`. 925 entities validate.

## 0.9.0 (minor) — 2026-07-21

- `e986843` Add the awards catalog: new `award` entity schema + 52 earned awards &
  recognitions (religious emblems, training awards, scouting honors / special recognitions)
  extracted from the official Guide to Awards and Insignia (No. 33066). Facts only (name,
  category, audience, square-knot + insignia catalog numbers, wear); no verbatim Guide prose.
  Every catalog number was verified against the source and knot→award pairings anchor-checked
  (`method: llm_extraction`, confidence 0.85). Wired through validate_data + build (per-entity
  / index / `current/awards.json` + `CurrentAward` published contract). Excludes plain uniform
  insignia, tenure pins, and the per-faith religious-emblem programs (deferred). 925 entities validate.

## 0.8.0 (minor) — 2026-07-21

- `73c3363` Add the advancement-rank layer: new `rank` entity schema + the 7 Scouts BSA
  ranks (Scout→Eagle, one version each; `program`/`order`, requirement CONTENT kept out of
  the entity). Plus 7 rank `requirement-set` documents parsed from the official 2024 Scouts
  BSA Requirements (No. 33216) — full verbatim requirement tree marked © Scouting America
  (`text_rights`), `subject: rank:<slug>`. Wired through validate_data + build (per-entity /
  index / `current/ranks.json` + `CurrentRank` published contract; requirement_sets join now
  keyed by full `kind:slug` ref). 148 requirement-sets, 873 entities validate.

## 0.7.0 (minor) — 2026-07-21

- `8de3faa` Import 469 camps from camp-finder into the camp dataset: classified by
  `camp_type` (361 resident / 68 day / 40 high-adventure) and `operator` (465 council +
  4 national HA bases — Philmont, Florida Sea Base, Northern Tier, Summit); Michigan
  Crossroads camps remapped to the kept council; demo councils excluded; description +
  sessions dropped (operational data stays at the council site). validate_data gains the
  camps dataset + council-ref + operator↔council coupling checks; build emits camp
  per-entity/index/current + a `CurrentCamp` published contract.

## 0.6.0 (minor) — 2026-07-21

- `919c1e8` Enrich the camp schema to handle every kind of scout camp: add `camp_type`
  (reservation / resident_camp / high_adventure_base / short_term_camp / day_camp /
  program_center / other), `operator` (council / national / other / unknown — represents
  national HA bases like Philmont with council=null), and a `parent` camp ref for
  reservation nesting; broaden `program_types` vocab. Example + negative fixture updated.

## 0.5.0 (minor) — 2026-07-21

- `36f4896` Seed 141 merit-badge requirement sets from OpenScouting/workbooks: full
  requirement tree (numbering, nesting, choose-N / option groups) + effective date +
  source links, with verbatim requirement text marked © Scouting America
  (`includes_official_text` + new `text_rights` field, excluded from the data license).
  validate_data + build extended (per-doc, index, current, badge join, `includes_official_text`
  ⇔ text invariant); NOTICE/README document the requirement-text rights boundary

## 0.4.0 (minor) — 2026-07-21

- `50b0844` Seed merit badge catalog: 142 badges (140 current, 17 Eagle-required incl.
  alternatives) from the OpenScouting/workbooks manifest + scouting.org; Citizenship in
  Society lifecycle (2021 → Eagle-required 2022 → discontinued 2026) and Computers→Digital
  Technology supersession as events; `url` added to merit-badge schema; build + validators
  + published `current` projection extended to the merit-badges dataset

## 0.3.1 (patch) — 2026-07-21

- `82c1ca5` Add README (repo is public): what it is, unofficial disclaimer, live `v1/` API
  endpoints + fetch examples, temporal data model, dataset status, local dev, contributing,
  CC BY-NC-SA/MIT licensing

## 0.3.0 (minor) — 2026-07-21

- `c8dab5d` Publish static API: `tools/build.py` compiles `data/` → `dist/` (path-versioned
  `v1/` — meta, per-dataset index + per-entity files with folded events, flat `current/`
  projections, schemas) with a published-projection schema + fail-fast contract check;
  `.github/workflows/pages.yml` gates (validators) and deploys to GitHub Pages on `main`

## 0.2.0 (minor) — 2026-07-21

- `8e7ec9b` Populate councils + territories: 235 council entities (229 assigned to
  the 14 Council Service Territories from official Scouting America maps, 6 defunct)
  + 20 territory entities (14 CSTs with 2021 NST→2024 CST history, 4 regions, 2 merged
  NSTs) + lifecycle events; CC BY-NC-SA data license; `tools/seed_councils_territories.py`
  generator and `tools/validate_data.py` gate (schema + referential + version windows)

## 0.1.0 (minor) — 2026-07-21

- `4a45757` Add project plan, dataset catalog (TODO.md), and v1 canonical schemas
  (common temporal core; council, territory, camp, merit-badge, requirement-set, events)
  with validated example instances and `tools/validate_examples.py`
