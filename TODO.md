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
| 3 | **Merit badge catalog** | ✅ `merit-badge` | Most-wanted dataset. Include 100+ discontinued badges (pure metadata, no copyright risk). Supersession events (computers→digital-technology). Eagle-required is time-varying (Citizenship in Society, 2022-07). | scouting.org badge list; Wikipedia; usscouts.org change logs; The Badge Archive |
| 4 | **Requirement sets (badges)** | ✅ `requirement-set` | Requirement diffs by effective year — gold for advancement tools. ⚠ summaries only until license decision (see queue). | Scouts BSA Requirements book editions; usscouts.org change logs; Internet Archive |
| 5 | **Camps (registry + history)** | ✅ `camp` | Import from camp-finder (keep IDs, `method: imported`). Historical/"lost camps" have a passionate community. Sessions/fees stay in camp-finder. | camp-finder dataset; usscouts.org OCD (robots-blocked — ask admin for dump); council sites |
| 6 | **Rank requirement history** | ⬜ reuse `requirement-set` (`subject: rank:*`) + new `rank` entity schema | Same machinery as badges. 2016/2022 Scouts BSA revisions; 2024 Cub Scouts overhaul. | Requirements book editions; usscouts.org |
| 7 | **OA lodges** | ⬜ (council pattern fits: versions + merge events + `council` ref) | Lodge↔council mapping, merges track council merges, totem/name history. Patch-collector community curates this by hand today. | OA/lodge sites; Wikipedia; patch DBs |
| 8 | **Merit badge earned-counts by year** | ⬜ (simple fact table, not temporal-entity) | BSA publishes annually; longitudinal series exists nowhere machine-readable. Tiny. | Scouting magazine / Bryan on Scouting annual posts |
| 9 | **High adventure bases + council HA programs** | ⬜ likely `camp` with program tags | camp-finder TODO already wants this vertical. | Council sites; scouting.org |
| 10 | **Awards catalog** (knots, religious emblems, NOVA/STEM†) | ⬜ merit-badge pattern generalizes | †NOVA discontinued 2025 — another retirement test case. | scouting.org; usscouts.org |
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
- **Finalize schema `$id` base URL.** Placeholder is
  `https://sethmay.github.io/open-scout-api/schema/v1/`; confirm when Pages deployment
  exists, then re-emit schemas (only the `$id`/`$ref` prefixes change).
- **Pipeline validator (PLAN §7 phase 5 prereq).** Beyond JSON Schema: version windows
  non-overlapping + ordered, compared **half-open `[valid_from, valid_to)`** (PLAN §3.1);
  every `EntityRef` resolves; event participants exist; event dates consistent with
  version boundaries; slug ↔ filename match; `_events.json` ids unique;
  `includes_official_text` ⇔ any `Requirement.text` present (the copyright lever — the
  boolean is untrustworthy alone); `HistoricalDate` month/day in range (schema pattern
  admits `2021-13-45`); `StateCode` in the closed USPS set. Extend
  `tools/validate_examples.py` or start `pipeline/` (Python 3.11+, camp-finder
  conventions — see its `validate.py`).
- **Build step: published projections.** `current/` flat snapshot per dataset (+
  `index.json`), per-entity history with events projected in. Schemas for published
  shapes are separate from canonical schemas. Then: GH Pages deploy, jsDelivr docs,
  release automation w/ SQLite artifact (PLAN §6).
- **Requirement-text licensing research.** Determine what verbatim requirement text can
  be published (usscouts.org precedent). Until resolved: `includes_official_text: false`,
  summaries only.
- **CI.** Validate gate on PR (schema + pipeline rules); deploy on merge to main.
  camp-finder LESSONS: gate must be non-vacuous — nonzero exit, wired, `needs:`-chained.
