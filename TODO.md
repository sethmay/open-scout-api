# TODO

Active queue and deferred work. Every item written to survive a clean context — see
`PLAN.md` for the model/conventions and §8 for pickup notes.

## Dataset catalog (the product backlog)

Ranked by value ÷ effort. Schema status: ✅ drafted in `schema/v1/`, ⬜ not yet designed.
No official machine-readable source exists for ANY of these (verified 2026-07-21; see
PLAN.md §1).

| # | Dataset | Schema | Why / notes | Primary sources |
|---|---|---|---|---|
| 1 | **Councils + historical lineage** | ✅ `council` | 🌱 **SEEDED (0.2.0):** 235 councils, 229 assigned to CSTs. Follow-ups (name/HQ reconcile, defunct dispositions, rename/founding history) in Queue. | camp-finder `data/councils/*.json`; official CST maps (territory); Wikipedia council list |
| 2 | **Territories / regions / areas** | ✅ `territory` | 🌱 **SEEDED (0.2.0):** 14 CSTs (2021 NST→2024 CST history), 4 regions, 2 merged NSTs, reorg events. Follow-up: 2/11 merge targets. | Wikipedia CST; official CST maps |
| 3 | **Merit badge catalog** | ✅ `merit-badge` | 🌱 **SEEDED (0.4.0):** 142 badges (140 current, 17 Eagle-required incl. alternatives), CiS lifecycle (2021→2022 Eagle→2026 discontinued), Computers→Digital-Technology supersession. Follow-ups (requirement content, historical discontinued badges, descriptions/tags) in Queue. | OpenScouting/workbooks MANIFEST; scouting.org eagle-required; Wikipedia discontinued-badges |
| 4 | **Requirement sets (badges)** | ✅ `requirement-set` | 🌱 **SEEDED (0.5.0):** 141 docs, full requirement tree (numbering/nesting/choose-N/options) + effective date + source links + verbatim text marked © Scouting America (`text_rights`). Follow-ups: historical revisions, plant-science deep-structure, per-badge summaries. | OpenScouting/workbooks `badges/<slug>/<year>.md`; scouting.org |
| 5 | **Camps (registry + history)** | ✅ `camp` | 🌱 **SEEDED (0.7.0):** 469 camps imported from camp-finder (361 resident / 68 day / 40 high-adventure; 465 council + 4 national). Follow-ups: reclassify/dedupe ~6 session/event-shaped entries (camp-finder LLM artifact, e.g. `*-full-week`/`*-half-week`/`*-2026-new`); reservation `parent` nesting; `camp_type` refinement; historical "lost camps". | camp-finder dataset; scouting.org (national bases) |
| 6 | **Rank requirement history** | ✅ `rank` + `requirement-set` (`subject: rank:*`) | 🌱 **SEEDED (0.8.0-0.10.0):** 7 rank entities + 33 requirement-sets — current from the 2024 Scouts BSA Requirements (No. 33216) + 26 historical editions (2016-2023, all 7 ranks) scraped from usscouts.org, deduped to distinct revisions with `supersedes` chains + effective windows. Follow-ups: pre-2016 editions (legacy markup); Cub Scout / Venturing / Sea Scout rank entities. | 2024 Scouts BSA Requirements (No. 33216); usscouts.org archive |
| 7 | **OA lodges** | ⬜ (council pattern fits: versions + merge events + `council` ref) | Lodge↔council mapping, merges track council merges, totem/name history. Patch-collector community curates this by hand today. | OA/lodge sites; Wikipedia; patch DBs |
| 8 | **Merit badge earned-counts by year** | ⬜ (simple fact table, not temporal-entity) | BSA publishes annually; longitudinal series exists nowhere machine-readable. Tiny. | Scouting magazine / Bryan on Scouting annual posts |
| 9 | **High adventure bases + council HA programs** | ⬜ likely `camp` with program tags | camp-finder TODO already wants this vertical. | Council sites; scouting.org |
| 10 | **Awards catalog** (knots, honors, training awards) | ✅ `award` | 🌱 **SEEDED (0.9.0):** 52 earned awards & recognitions from the Guide to Awards and Insignia (No. 33066) — facts only (category, audience, square-knot + insignia numbers, wear), `method: llm_extraction` conf 0.85, numbers source-verified. Follow-ups: per-faith religious emblems (separate large dataset), NOVA/STEM awards, uniform insignia. | Guide to Awards and Insignia (No. 33066); scouting.org/awards |
| 11 | **Membership/financial stats by council/year** | ⬜ fact table | Councils are separate 501(c)(3)s; 990s public via ProPublica API. Sensitive framing post-bankruptcy. | ProPublica Nonprofit Explorer API; BSA annual reports |

**Deliberately avoided:** unit (troop/pack) rosters / BeAScout pin data — PII-adjacent,
ToS-hostile, staleness = liability. **Districts:** extreme churn, anecdotal sourcing; only
as best-effort attributes of council history, never a standalone dataset.

## Queue

- **Reconcile council name/HQ to official CST maps (follow-up to councils seed).** The
  seed uses camp-finder (unofficial) names/HQ with official CST-map *territory*
  assignment + a few observed name overrides (303 Mississippi Riverlands, 780 Michigan
  Crossroads). The map is authoritative for name/HQ — do a full reconciliation pass
  (extractors flagged many HQ granularity diffs, e.g. metro vs suburb). Also populate
  `states_served` (currently `[]`; camp-finder only gave HQ state).
- **Verify defunct-council dispositions + 2/11 merge targets.** 6 councils absent from
  2026 maps (30 Southern Sierra, 41 Redwood Empire, 302 Choctaw→303, 405 Rip Van Winkle,
  694 South Plains, 695 Black Hills→733 Sioux): confirm successors + dates (302/695 have
  sourced successors; 30/41/405/694 are `discontinued` with date=null). Territories 2 & 11
  (merged 2024) need their absorbing-territory targets. Add events once sourced.
- **Council rename/founding history.** Councils currently have a single version
  (valid_from/to = null) — camp-finder is a current snapshot. Add historical versions +
  rename/merger events as sourced (the temporal model already supports it).
- **Merit badge follow-ups.** (a) **Requirement content — DONE (0.5.0):** verbatim text +
  structure per current revision (marked © SA). (b) **Historical requirement revisions**:
  only the current revision per badge is seeded (workbooks ships one `<year>.md` each);
  backfill older revisions with `supersedes` chains when sourced. (c) **plant-science
  deep-structure**: its 5-level "alternatives" nesting was flattened (conf 0.75, flagged in
  notes) — parse properly if it recurs. (d) **Historical discontinued badges**: catalog
  carries only CiS + Computers; add the 100+ discontinued set. (e) **Enrich** badge
  `description`/`tags` (empty). Regenerating needs the workbooks repo at
  `.workbench/workbooks-main/`.
- **Finalize schema `$id` base URL. — DONE (0.3.0).** Confirmed
  `https://sethmay.github.io/open-scout-api/schema/v1/` (owner `sethmay`); build serves
  schemas at that path, no re-emit needed.
- **Build step: published projections. — DONE (0.3.0).** `tools/build.py` → `dist/`
  (`v1/meta.json`, per-dataset `index.json` + per-entity `<id>.json` with folded events,
  `v1/current/*.json`, `schema/v1/*`); validates `current/` against
  `published-current.schema.json`. `.github/workflows/pages.yml` gates (validators) +
  builds on push/PR, deploys to Pages on `main`.
- **⚠ One-time manual: enable GitHub Pages.** Repo Settings → Pages → Source = "GitHub
  Actions". Until done, the deploy job has nothing to publish to (build still runs/gates).
- **Add a README. — DONE (0.3.1).**
- **Release automation + CDN docs. — DONE (0.12.0).** `v*` git tags at CHANGELOG shas;
  `.github/workflows/release.yml` publishes GitHub Releases with the JSON tree +
  `tools/build_sqlite.py` SQLite artifact; jsDelivr pinning + SQLite documented in README.
  ⚠ One-time manual (owner): `git push --tags`, and enable the GitHub↔Zenodo integration for DOIs.
- **Pipeline validator (remaining rules).** `tools/validate_data.py` covers schema + refs +
  half-open windows + retired-entity + unique event ids + `includes_official_text` ⇔ text +
  choose-needs-children. Still TODO when relevant data lands: event-date ↔ version-boundary
  consistency; `HistoricalDate` month/day range; `StateCode` closed USPS set; camp
  `operator`↔`council` coupling (operator=council ⇒ council set; national/other/unknown ⇒
  council null) — convention-only in the schema, assert in the camp import pipeline.
- **Published-projection schema for requirement-sets.** `build.py` fail-fast-validates
  current/{councils,territories,merit-badges}.json against `published-current.schema.json`,
  but `current/requirement-sets.json` + `requirement-sets/index.json` have no
  published-contract schema (per-doc canonical validation covers content). Add one when the
  requirement-set listing contract stabilizes.
- **Requirement-text licensing — DECIDED (0.5.0).** Verbatim requirement text IS published,
  marked © Scouting America (`includes_official_text: true` + `text_rights`), excluded from
  CC BY-NC-SA, reproduced non-commercially with attribution + takedown. Revisit if SA
  objects or a cleaner permission path opens.
