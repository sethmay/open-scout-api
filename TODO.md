# TODO

Active queue and deferred work. Every item written to survive a clean context — see
`PLAN.md` for the model/conventions and §8 for pickup notes.

## Dataset catalog (the product backlog)

Ranked by value ÷ effort. Schema status: ✅ drafted in `schema/v1/`, ⬜ not yet designed.
No official machine-readable source exists for ANY of these (verified 2026-07-21; see
PLAN.md §1).

| # | Dataset | Schema | Why / notes | Primary sources |
|---|---|---|---|---|
| 1 | **Councils + historical lineage** | ✅ `council` | Foundation everything references. Mergers/renames as events. First population target. | camp-finder `data/councils/*.json` + `data/council-websites.json`; Wikipedia "List of councils (Scouting America)"; council sites |
| 2 | **Territories / regions / areas** | ✅ `territory` | Small + finite; the 2021 regions→16 NST reorganization is the temporal model's acceptance test. Populate with #1. | Wikipedia; BSA announcements |
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

- **Populate councils + territories (PLAN §7 phase 2) — hand to data agent (likely Opus).**
  Brief in PLAN.md §8. Seed from camp-finder; encode known mergers (302/303 →
  Mississippi Riverlands, 695 → Sioux — details in camp-finder `TODO.md` "Website
  enrichment" section) as events with sources. Examples in `schema/v1/examples/` are
  illustrative, NOT importable data.
- **Decide data license before first data publication.** CC0 (max reuse, standard for
  open data) vs CC-BY 4.0 (attribution). Code: MIT. Add LICENSE + README when decided.
  README deferred until repo goes public.
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
