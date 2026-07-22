# TODO

Active queue and deferred work. Every item written to survive a clean context — see
`PLAN.md` for the model/conventions and §8 for pickup notes.

## Dataset catalog (the product backlog)

Ranked by value ÷ effort. Schema status: ✅ drafted in `schema/v1/`, ⬜ not yet designed.
No official machine-readable source exists for ANY of these (verified 2026-07-21; see
PLAN.md §1).

| # | Dataset | Schema | Why / notes | Primary sources |
|---|---|---|---|---|
| 1 | **Councils + historical lineage** | ✅ `council` | 🌱 **SEEDED (0.2.0); LINEAGE (0.14.0):** 419 councils — 229 current (assigned to CSTs) + 190 historical. Founding dates (141), rename chains (57), merger/absorption events (112) + 184 predecessor councils extracted from Wikipedia (`llm_extraction`); `states_served` for 208. Follow-ups (8 live-council merger claims to review; predecessor numbers/HQ; 7 article-less recent mergers; deeper lineage) in Queue. | camp-finder; official CST maps (territory); English Wikipedia (lineage) |
| 2 | **Territories / regions / areas** | ✅ `territory` | 🌱 **SEEDED (0.2.0):** 14 CSTs (2021 NST→2024 CST history), 4 regions, 2 merged NSTs, reorg events. Follow-up: 2/11 merge targets. | Wikipedia CST; official CST maps |
| 3 | **Merit badge catalog** | ✅ `merit-badge` | 🌱 **SEEDED (0.4.0):** 142 badges (140 current, 17 Eagle-required incl. alternatives), CiS lifecycle (2021→2022 Eagle→2026 discontinued), Computers→Digital-Technology supersession. Follow-ups (requirement content, historical discontinued badges, descriptions/tags) in Queue. | OpenScouting/workbooks MANIFEST; scouting.org eagle-required; Wikipedia discontinued-badges |
| 4 | **Requirement sets (badges)** | ✅ `requirement-set` | 🌱 **SEEDED (0.5.0):** 141 docs, full requirement tree (numbering/nesting/choose-N/options) + effective date + source links + verbatim text marked © Scouting America (`text_rights`). Follow-ups: historical revisions, plant-science deep-structure, per-badge summaries. | OpenScouting/workbooks `badges/<slug>/<year>.md`; scouting.org |
| 5 | **Camps (registry + history)** | ✅ `camp` | 🌱 **SEEDED (0.7.0); PARITY (0.17.0):** 487 camps imported from camp-finder (376 resident / 69 day / 42 high-adventure; 483 council + 4 national). 0.17.0 added the 4 Pacific-Northwest councils' camps (492/606/609/697) the initial import held back as demo data (now real, verified). Follow-ups: reclassify/dedupe ~6 session/event-shaped entries (camp-finder LLM artifact, e.g. `*-full-week`/`*-half-week`/`*-2026-new`); reservation `parent` nesting; `camp_type` refinement; historical "lost camps". | camp-finder dataset; scouting.org (national bases) |
| 6 | **Rank requirement history** | ✅ `rank` + `requirement-set` (`subject: rank:*`) | 🌱 **SEEDED (0.8.0-0.10.0); ALL PROGRAMS (0.15.0):** 21 rank entities (7 Scouts BSA + 6 Cub + 4 Venturing + 4 Sea Scout) + 47 requirement-sets. Scouts BSA: 2024 (No. 33216) + 26 historical editions (2016-2023) via usscouts.org with `supersedes` chains. Cub/Venturing/Sea Scout: current requirements from official scouting.org pages + 2026 Sea Scout PDFs (verbatim-verified). Follow-ups: pre-2016 Scouts BSA editions; Cub adventure-level requirement detail (each adventure's own requirements); historical editions for the new programs. | 2024 Scouts BSA Requirements; usscouts.org; scouting.org; seascout.org PDFs |
| 7 | **OA lodges** | ✅ `oa-lodge` | 🌱 **SEEDED (0.13.0):** 238 lodges from the official OA lodge locator feed (oa-bsa.org), all linked to their chartering `council` + OA section/region + HQ/coords + website; officer/contact PII excluded. Follow-ups: lodge numbers (not in feed), merger/rename history + events (track council mergers), totem. | oa-bsa.org lodge locator feed; ScoutWiki/Fandom (numbers/history) |
| 8 | **Merit badge earned-counts by year** | ⬜ (simple fact table, not temporal-entity) | BSA publishes annually; longitudinal series exists nowhere machine-readable. Tiny. | Scouting magazine / Bryan on Scouting annual posts |
| 9 | **High adventure bases + council HA programs** | ⬜ likely `camp` with program tags | camp-finder TODO already wants this vertical. | Council sites; scouting.org |
| 10 | **Awards catalog** (knots, honors, training awards) | ✅ `award` | 🌱 **SEEDED (0.9.0):** 52 earned awards & recognitions from the Guide to Awards and Insignia (No. 33066) — facts only (category, audience, square-knot + insignia numbers, wear), `method: llm_extraction` conf 0.85, numbers source-verified. Follow-ups: per-faith religious emblems (separate large dataset), NOVA/STEM awards, uniform insignia. | Guide to Awards and Insignia (No. 33066); scouting.org/awards |
| 11 | **Membership/financial stats by council/year** | ⬜ fact table | Councils are separate 501(c)(3)s; 990s public via ProPublica API. Sensitive framing post-bankruptcy. | ProPublica Nonprofit Explorer API; BSA annual reports |

**Deliberately avoided:** unit (troop/pack) rosters / BeAScout pin data — PII-adjacent,
ToS-hostile, staleness = liability. **Districts:** extreme churn, anecdotal sourcing; only
as best-effort attributes of council history, never a standalone dataset.

## Queue

### Camp-finder cutover — API-side requests (reviewed 2026-07-21)

camp-finder is migrating to consume this API as its core data — **durable reference data
only** (no sessions/fees/dates/availability back; that split is the whole point). Requests
reviewed + sequenced below; all additive/backward-compatible under `v1` (minor bumps).

1. **Projection contract v1.1 - DONE (0.16.0).** Pure `build.py` + `published-current`
   schema, additive: (a) add `verified_at` + `method` to **all** `current/*.json` projections
   (not just camps) — freshness is the most-used provenance field, keep the contract uniform;
   (b) denormalize council into `current/camps.json` (`council_name`, `council_website`,
   `council_number`) resolved against the **canonical** council (so defunct-council camps still
   get a name; the 4 national-base camps with `council:null` get nulls); (c) emit a resolved
   `url` (camp website → council website) so the "visit official page" CTA is a guaranteed
   contract. Plus a README note that `v1` projection fields are **additive-only** (stability
   promise — also satisfies request #7's API side).
2. **Coverage reconciliation - DONE (0.17.0).** Councils 229 vs 238: explained, no loss (API
   drops 3 non-geographic/dup - 272->780, 800 Direct Service, 999 National holder - and
   excludes 6 defunct councils from `current`). Camps: root cause was `import_camps.py`
   deliberately skipping the 4 Pacific-Northwest demo councils; that data is now real and
   verified, so the exclusion was removed and their 18 camps imported. API camps 469 -> 487;
   0 camp-finder camps now missing (the API is a superset - it also carries a national base
   and camps the camp-finder site itself filters out).
3. **Camp `summary` (evergreen prose).** Add `summary` to `CampVersion` (original prose; MUST
   NOT contain dates/fees/session schedules) + surface in the projection. Do NOT scrub
   camp-finder's contaminated descriptions — regenerate clean, and add a `validate_data` guard
   rejecting 4-digit years / `$` / month names / "session" so evergreen is an enforced gate.
4. **Vocab-as-data - DONE (0.19.0).** Published `v1/vocab/{camp-types,camp-program-types,camp-features}.json`
   as `{code,label,description}` (+ `vocab.schema.json`, listed in `meta.vocab`). `camp-program-types` is
   namespaced apart from the rank `program` vocab. `validate_data` cross-checks that every code used in camp
   data is defined, so the labels fail visibly on drift. `features` is populated (13 codes) from the import.
5. **Later / consumer-side.** #8 populate `parent`/reservation grouping (schema ready; data
   sourcing) — after cutover. #7 TS codegen is the **site's** task (json-schema-to-typescript on
   `published-current.schema.json`); the API only owes the additive-only stability promise (1a).

- **Reconcile council name/HQ to official CST maps (follow-up to councils seed).** The
  seed uses camp-finder (unofficial) names/HQ with official CST-map *territory*
  assignment + a few observed name overrides (303 Mississippi Riverlands, 780 Michigan
  Crossroads). The map is authoritative for name/HQ — do a full reconciliation pass
  (extractors flagged many HQ granularity diffs, e.g. metro vs suburb). `states_served` is
  now populated for 208 current councils from Wikipedia (0.14.0); the rest (and historical
  versions) remain `[]`.
- **Verify defunct-council dispositions + 2/11 merge targets.** 6 councils absent from
  2026 maps (30 Southern Sierra, 41 Redwood Empire, 302 Choctaw→303, 405 Rip Van Winkle,
  694 South Plains, 695 Black Hills→733 Sioux): confirm successors + dates (302/695 have
  sourced successors; 30/41/405/694 are `discontinued` with date=null). Territories 2 & 11
  (merged 2024) need their absorbing-territory targets. Add events once sourced.
- **Council rename/founding history — DONE (0.14.0).** Current councils carry founding
  `valid_from`, prior-name versions, and merger/absorption events; 184 named predecessor
  councils added as defunct entities (Wikipedia facts, `llm_extraction`, conf 0.7–0.8).
  Remaining: review the 8 skipped live-council merger claims (`.workbench/council-history/
  council_history_conflicts.json` — e.g. Baden-Powell / Daniel Boone claimed by multiple
  survivors); predecessor `bsa_number`/HQ are unsourced stubs; 7 recent-merger councils lack
  Wikipedia articles (Mississippi Riverlands, Natural State, Pacific Crest, San Diego-Imperial,
  High Desert, Natchez Trace, Simon Kenton) so still have no founding/lineage; deeper
  multi-level (predecessor-of-predecessor) lineage.
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
- **⚠ Zenodo DOI — deferred (owner decision).** Enable the GitHub↔Zenodo integration
  (zenodo.org account → GitHub → toggle the repo on) so pushed `v*` tags mint a citable DOI
  using `.zenodo.json`. Deferred until the repo's final/permanent home (org + name) is settled,
  since the DOI + Zenodo record bind to that GitHub location.
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
