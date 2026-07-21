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
- **Add a README.** Repo is now public; PLAN deferred it until publication. Should cover:
  what it is, the `v1/` API endpoints + example fetch, CC BY-NC-SA, unofficial disclaimer,
  how to contribute. (Not written yet — was not part of the build slice.)
- **Release automation + CDN docs.** Tag releases; ship the JSON tree + a generated
  SQLite artifact (PLAN §6); document jsDelivr pinning; consider Zenodo DOI.
- **Pipeline validator (remaining rules).** `tools/validate_data.py` covers schema +
  refs + half-open windows + retired-entity + unique event ids. Still TODO when the
  relevant data lands: event-date ↔ version-boundary consistency; `includes_official_text`
  ⇔ any `Requirement.text`; `HistoricalDate` month/day range; `StateCode` closed USPS set.
- **Requirement-text licensing research.** Determine what verbatim requirement text can
  be published (usscouts.org precedent). Until resolved: `includes_official_text: false`,
  summaries only.
