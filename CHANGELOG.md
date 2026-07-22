# Changelog

One section per merge into `main`; newest first. Conventions: `skill://semver`.
Version anchors: this file only (no package manifests yet — add here when one appears).

## 0.19.0 (minor) — 2026-07-21

- `07e9e3a` Published the camp vocabularies as data, so a consumer can show a human label for every code and fail visibly on codes it does not recognize.
  - New endpoints `v1/vocab/camp-types.json`, `v1/vocab/camp-program-types.json`, and `v1/vocab/camp-features.json` list every code with a label and a short description.
  - A validation check now rejects any camp whose type, program, or feature code is missing from its vocabulary, so the published labels can never fall behind the data.
  - `camp-program-types` is named apart from the rank `program` vocabulary to avoid confusion.

## 0.18.0 (minor) — 2026-07-21

- `b9334c4` Camps now carry a short, evergreen description, so a site has real copy for camp pages at cutover.
  - Added a `summary` to most camps (405 of 487 have one): what the camp is, its setting and size, and the kinds of programs it offers.
  - Summaries are original prose that leaves out anything that changes year to year (no dates, fees, or session schedules). A validation check rejects any summary that slips in a year, price, or month.
  - Surfaced in `current/camps.json`, so a site needs no extra lookup.

## 0.17.0 (minor) — 2026-07-21

- `4d4a381` Added the Pacific-Northwest councils' camps, so the API no longer trails the camp-finder site.
  - Imported 18 camps from the Cascade Pacific, Chief Seattle, Mount Baker, and Pacific Crest councils (Camp Meriwether, Camp Parsons, Fire Mountain Scout Camp, and others) that an earlier import had held back as demo data.
  - They carry real, verified details from official council sites, so they belong in the reference set. The camp list grew from 469 to 487.
  - The API now lists every camp the camp-finder site shows, plus a few it filters out (a national base and camps with no current program).

## 0.16.1 (patch) — 2026-07-21

- `a48bd3c` Rewrote the release notes to be easier to read.
  - Each release's notes (the matching CHANGELOG entry) now lead with what changed and why it matters, in plain language and point form.
  - Recorded that style in `CLAUDE.md` so future notes stay consistent.
  - Notes only; no data or code changed.

## 0.16.0 (minor) — 2026-07-21

- `54c610a` Richer camp data for sites building on this API: the published "current" camp list now stands on its own, with no extra lookups.
  - Every current record now shows when it was last verified, and how, so an app can flag listings that are due for a fresh check.
  - Each camp carries its council's name, website, and number, plus a ready-to-use link to the official page.
  - The "current" files are a stable promise for consumers: new fields may be added, but existing ones are never renamed or removed.

## 0.15.0 (minor) — 2026-07-21

- `9e353b8` Advancement ranks now cover every Scouting America program, not just Scouts BSA. The rank list grew from 7 to 21.
  - Added 6 Cub Scout ranks (Lion, Tiger, Wolf, Bear, Webelos, Arrow of Light), 4 Venturing ranks (Venturing, Discovery, Pathfinder, Summit), and 4 Sea Scout ranks (Apprentice, Ordinary, Able, Quartermaster).
  - Each new rank ships its current requirements, so the requirement-set count grew from 174 to 188.
  - Requirements come from official sources (scouting.org pages and the 2026 Sea Scout PDFs), and every line was checked word for word against its source. Requirement text remains © Scouting America.

## 0.14.0 (minor) — 2026-07-21

- `f9f6e33` Councils now carry their history, not just a current snapshot. The council list grew from 235 to 419 (229 current, 190 historical).
  - Added founding dates for 141 councils and former-name history for 57.
  - Added 184 predecessor councils that merged or closed over the years, with 112 merger and absorption events so you can trace how today's councils came to be.
  - History is drawn from each council's Wikipedia article and cross-checked by council number. Facts only; no article text is copied.

## 0.13.0 (minor) — 2026-07-21

- `970ea2c` Added Order of the Arrow lodges: 238 lodges from the official OA lodge locator.
  - Each lodge links to the council that charters it, with its OA section and region, headquarters city and state, map coordinates, and website.
  - Lodge officer names and contact emails are left out on purpose to protect youth privacy.

## 0.12.0 (minor) — 2026-07-21

- `f0a5f29` Made the data easy to download and cite, and set up automatic releases.
  - Every release now publishes a downloadable bundle: the full dataset as JSON, plus a ready-to-query SQLite database.
  - Pushing a version tag now builds and publishes that release on its own.
  - Added Zenodo details for a citable archive and documented CDN pinning in the README.
  - No data changed in this release.

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
