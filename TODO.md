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

## v1.0 readiness — contract freeze

1.0 means the `v1` surface is frozen: additive-only forever, no renames or removals. Everything in
the dataset catalog above is additive (new files / new optional fields = MINOR), so **data
completeness does not gate 1.0** — only changes that would become *breaking* once stability is
promised do.

Cleared in 0.28.0:

- **Every published *collection* projection is schema-pinned + build-gated** — 16 files: 8
  `current/*.json` against `published-current.schema.json` and 8 `{dataset}/index.json` against the
  new `published-index.schema.json`. Each names its own contract in `$schema`; `build.py` exits
  nonzero if any projection drifts. The item shape is selected BY the envelope `kind` (`allOf` of
  `if kind then items.$ref`), not a bare `oneOf`, so a mis-wired listing cannot publish another
  dataset's items at a right-looking URL. (Verified non-vacuous: unknown fields, missing required
  fields, a bad `kind`, a malformed `council:` ref, a non-slug `reservation.id`, and kind/item
  mis-pairings are all rejected.)
- **`current/requirement-sets.json` was the one unpinned `current/` surface** — now pinned, and it
  gained `verified_at`/`method`/`confidence` (it was the lone holdout among the 8, so provenance is
  now uniform) plus `includes_official_text` (the licensing flag its own index already carried).
- **`reservation.id` is now contractually a stable opaque grouping key** (a bare slug, never a
  `kind:slug` EntityRef). A future reservation entity reuses these exact slugs and adds a *new* ref
  field rather than changing this one — so first-classing reservations stays additive.
- **`territories/index.json` now exposes `number` + `division_type`** — that listing mixes CSTs,
  closed NSTs, and pre-2021 regions, and consumers had no way to tell them apart without parsing
  names or ids.

**Remaining 1.0 blocker (owner decision): the permanent home / `$id` base URL.** All 1,340 entity
files carry `$schema: https://sethmay.github.io/open-scout-api/schema/v1/…`, `build.py` hardcodes
that base, and it is both the documented API root and the jsDelivr pin path. Moving the repo to an
org afterwards would change every schema URL and every published URL — maximally breaking. Settle
org + name, re-stamp `data/` once, update the README/CDN docs, then cut 1.0. This also unblocks the
Zenodo DOI (below), which binds to the final GitHub location.

**Remaining 1.0 consideration: 10 published endpoints are still unpinned.** The 16 collection
projections are gated, but `v1/meta.json` (the discovery document), `v1/camps/aliases.json`, and all
8 per-entity `v1/{dataset}/{id}.json` endpoints (~1,528 files) have no published contract — their
shape (canonical entity + a projected `events` array, plus `requirement_sets` for
merit-badges/ranks/awards) exists only inside `build.py`, so renaming `events` is a one-line edit no
gate would catch. Either add `published-entity` + `published-meta` schemas or state in the README
that only the collection projections are covered by the stability promise. (The README now says
which surfaces are unpinned; deciding whether to pin them is the open part.)

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
5. **Reservation grouping - DONE (0.20.0).** Populated the camp `parent` ref on 29 sub-camps
   (derived deterministically from the camp set: slug-prefix or "... at X" name match within a
   council; no external data), surfaced in `current/camps.json`. #7 (TS codegen) is the site's
   task, satisfied API-side by the additive-only `v1` stability promise (step 1a).

**Camp-finder cutover: all API-side requests delivered (steps 1-5, v0.16.0-v0.20.0).** Remaining
is the site's own cutover work + the optional deeper follow-ups (Cub adventure-level requirements,
reservation modeling as its own `camp_type`, historical "lost camps").

### Camp data-quality follow-ups (camp-finder review, 2026-07-22)

Shipped: freshness dates (0.21.0); coordinate-integrity gate + geocode backfill + `geo_precision`
(0.22.0); duplicate-listing merge + `aliases.json` (0.23.0); reservation-centroid relabel (0.23.1);
non-prefix same-camp merges + `reservation` grouping (0.24.0); reservation names + Goshen unify +
same-council grouping (0.25.0); Pipsico rename from a scraped event title (0.25.1). The `parent`
approach from step 5 was superseded — those were duplicates (now merged); `reservation` groups
co-located *distinct* camps.

**Source model (2026-07-22):** camp-finder has flipped to *consuming* this API and retired its
per-council source data. `data/` is now the authoritative source; stamp/validate/build run on it
directly. `import_camps.py` and `geocode_camps.py` are historical one-time tools (they need the
archived camp-finder source to run) — go-forward corrections are direct edits to `data/`, validated
by the pipeline (as the Pipsico fix was).

- **Program-level tracking (future — camp-finder dev flagged).** Merging program/session variants
  into one camp unions `program_types` but drops per-offering detail (e.g. "Webelos resident" vs
  "Cub day" as separately described programs; dates/fees stay out by design). A `programs` array on a
  camp — or a first-class reservation entity with child camps and programs — would restore it. Ties
  into modeling a reservation as its own entity and the co-located `reservation` groups now in-data.
- **True sub-camp coordinates (reservation names DONE 0.25.0; AK coord fixed 0.25.2).** 17 of 18
  `reservation` groups are named; only the WY Camp Buffalo Bill / Yellowstone Anglers pair is unnamed
  (no distinct reservation name). Remaining coord work: geocode co-located camps to their own points so
  one-pin clustering can become distinct, correctly-placed pins. (The AK Chilkoot/Denali coordinate
  error is fixed — Chilkoot moved to Haines, un-grouping the pair.)
- **`wi-adventure-camp` — RESOLVED (0.25.5).** Not Camp Decorah and not a mislocation: it was Twin
  Valley Council (#283, Mankato MN) running a Scouts BSA session AT Tomahawk Scout Reservation
  (Northern Star's camp, Birchwood WI) — the same physical property as `wi-tomahawk-scout-camp`, so it
  was merged in (a guest-council session is not a distinct physical camp). (`oh-cub-world` and
  `va-cub-and-webelos-adventure-camp` were reviewed and kept — generic-looking, but the councils' real names.)
- **Coverage: overseas/OCONUS councils under-scraped (camp-finder gap; Camp Kenya added 0.26.1).**
  Camp Kenya (Transatlantic #802) was absent entirely — camp-finder's scrape favored US councils. Sweep
  Transatlantic, Far East / Direct Service, and other overseas councils against their own camp pages for
  camps the import missed, and add them by hand (`method: curated`) like Camp Kenya.
- **Average summer temperatures — DONE (0.27.0).** `july_high_f` / `july_low_f` ship on every camp
  with a coordinate (447 of 448), sampled from WorldClim v2.1 1 km normals by `tools/july_temp.py`.
  (`elevation_ft` shipped in 0.26.0.) Open, if ever wanted: other months / a seasonal curve, and a
  present-day baseline — WorldClim's window is 1970-2000, ~1°F cooler than a current normal.

### Camp program features — implementation + population plan

Design: [`PLAN.md`](./PLAN.md) §5.1. Status: **design only, nothing implemented.** `features[]` is
populated on 8 of 448 camps and published in no projection. The schema reshape is free until `v1`
freezes at 1.0; population is the long pole.

**Source reality (measured 2026-07-25).** Of 448 camps: 292 have a durable camp/council page, 146
point at a scoutingevent/247 registration portal, 10 are year-stamped — and **159 publish
`url == council_website`**, i.e. no camp-specific page at all. Roughly a third of camps have no
obvious page to read features off, and *that*, not the model, is the risk.

⚠ **Retraction:** the idea of inferring features from per-camp merit-badge offerings (Climbing MB ⇒
tower, Small-Boat Sailing ⇒ sailing) does **not** work as stated — no per-camp badge offerings exist
anywhere in `data/`, and their only source is the scoutingevent registration layer this dataset
deliberately excludes. Salvageable only as a *derivation-only* input (ingest to derive a feature,
cite the source, never store the offerings). Deprioritized anyway: the council page proved a richer
source (see the Meriwether evidence in PLAN §5.1).

- **Phase 0 — sourcing spike — DONE (0.30.0).** 10 camps sampled deterministically across the two
  real source tiers (the planned `C_no_page` tier is empty: every camp has *some* stored website, and
  the "159 with no camp page" figure was the published `url` falling back to the council site). The
  5th portal camp was dropped as redundant once that tier was 0-for-4.

  | tier | sampled | usable | rich | zero |
  |---|--:|--:|--:|--:|
  | durable camp/council page (292 camps) | 6 | 5 | 2 | 1 |
  | registration portal (156 camps) | 4 | 0 | 0 | 4 |

  Yield: Meriwether 21 features / 3 signature, Bowers 17 / 3, Emerald Bay 7 / 1, Chilkoot 4, Tunnel
  Mill 4. All five are now surveyed in `data/`. Findings:
  - **Source tier is the dominant predictor.** A durable camp page is usable 5 times in 6; a
    registration portal was usable 0 times in 4.
  - **Councils flag their own differentiators**, so `signature` is populatable from sources rather
    than guesswork: Meriwether has a literal "Featured Experiences … unique to Camp Meriwether"
    section; Bowers names "Rippy World" and a 50-foot alpine tower. 7 signature entries from 5 camps.
  - **Stored URLs are often not descriptive pages** — though the original wording of this finding
    overstated it, and is corrected here. Verified by the 0.31.0 link audit: Elk Lick really does
    point at a near-empty Wix index for a *different* camp (Merz); Kanza's page really is a 2020
    event, six years closed; Verdugo Oaks really is a registration page whose map is a *church*;
    Meriwether's `cpcbsa.org` really did silently redirect. But **Yawgoog and Chawanakee were wrongly
    called broken** — both return real HTML that names the camp. The "health-record PDF" and "dead
    calendar link" were artifacts of how the page was *fetched* during the spike (an attachment link
    followed, and a `.md`-suffix variant), not properties of the stored URL. Both are ordinary
    `portal` pages: thin for feature-surveying, but not broken. So the honest count is 3 of 10
    genuinely wrong, not 5 of 10 — and a link audit is still a prerequisite for population.
  - **Pages are explicitly non-exhaustive** ("For a complete list of activities … check the Program
    Guide"), so `features_verified_at` means *a survey happened*, not *the list is complete*; that
    caveat is recorded in each surveyed camp's provenance. Leader's/Program Guide PDFs are linked
    from most usable pages and are the natural second wave.
  - **`features_verified_at` earned its place immediately.** The 5 zero-yield camps must stay `null`:
    they certainly *have* features, we simply could not source them — which is a different fact from
    "surveyed, offers none". Without the field they would be indistinguishable.
  - **Day camps may not be surveyable in principle.** Verdugo Oaks' day camp runs at a rented church,
    so for `day_camp` the camp↔property relationship is weak and features may be meaningless.
    Consider excluding day camps from population rather than recording nulls forever.
  - **Vocabulary sizing:** 5 usable camps produced **33 new codes** (13 → 46). Growth should be
    sublinear as later camps reuse terms, but expect roughly 100-150 codes at full coverage.
  - Cost estimate from observed effort: ~10-15 min per camp for a careful survey including notes, so
    the ~240 reachable durable-page camps are ~40-60 hours of extraction. Prioritise resident and
    high-adventure properties (biggest out-of-council draw) over day camps.
- **Phase 1 — schema + vocab reshape — DONE (0.29.0).** `features[]` is now an array of
  `{code, signature?, note?}`; `features_verified_at` added; vocabulary terms may carry
  `category`/`broader`/`aliases` and all 13 existing terms are categorized (6 with aliases).
  Validator guards, each proven to bite: duplicate feature `code` in one version (`uniqueItems`
  stops catching this once two entries differ), a `note` containing transitory text (reuses the
  evergreen `summary` guard), `broader` naming an undefined term, a `broader` cycle, and an alias
  colliding with a real code or with another term's alias. Two negative fixtures added.
  *Design change during implementation:* `features_verified_at` is deliberately NOT required when
  `features` is non-empty. That rule would have forbidden the honest state the 8 imported camps are
  actually in — features present from a bulk import, never deliberately surveyed — so the field
  instead carries four meaningful states (see the schema description).
- **Phase 2 — vocabulary v1 — DONE (0.34.0).** 13 codes → 46 (spike) → 95 (calibration) → **121**
  (main wave). Round two curated 226 proposals covering 116 distinct codes down to 26 additions,
  driven by how many independent camps asked for each: **whitewater_rafting was requested by 18
  camps** and had no code at all, `hiking` by 17 (counting the `hiking_trails` spelling), and a whole
  missing season showed up as snowshoeing / cross-country skiing / sledding / ice fishing / winter
  camping. `scoutcraft` was added as the parent the vocabulary had been missing for orienteering,
  pioneering, and wilderness survival — all standard BSA programme areas. Merges: `hiking_trails` →
  `hiking`, `waterslide` → `water_slide`, `stargazing` → `astronomy`. Rejected: `trade_skills` and
  `bike_friendly` (too vague to filter on), `waterfall` (a landscape feature, not an offering), and
  `family_camp` again. **83 singletons were deliberately held back** — a code used once is not yet a
  category; they get in on a second sighting. 42 of 121 terms carry `broader`, 51 carry `aliases`.
  Still open: whether `older_scout_program` / `high_adventure_option` belong in `program_types`, and
  whether housing type deserves its own field.
- **Phase 3 — population — MAIN WAVE DONE (0.34.0).** 16 agents surveyed 285 camps in parallel
  against the frozen 95-term contract. **294 of 448 camps are now surveyed (77% of the 384
  non-day-camps), carrying 4,226 feature entries and 147 signature entries across 91 distinct codes**
  — up from 37 camps and 416 entries. Integrity held completely: **zero unknown codes, zero duplicate
  codes, zero notes violating the evergreen rule, zero unparseable files**, and no camp outside a
  batch was touched.
  - **Parallel execution worked, but only because the contract was frozen first.** The agents also
    caught four hazards I had not anticipated and fixed them mid-flight: edits leaking into the main
    checkout via relative paths; the eval kernel being SHARED between agents, so a generic global
    could silently redirect one agent's write to another's file; the evergreen guard rejecting the
    ordinary word "may" (case-insensitively) and month abbreviations; and eight camps arriving with
    imported features already present, where a blind write would have deleted data. All four are
    worth stating up front in any future brief.
  - **Biggest yield lever found: extensionless guide PDFs.** Councils commonly link a Leader's or
    Program Guide with no file extension (the Tentaroo `/files/NNNNN/name` pattern), which the reader
    refuses. Fetching the bytes and reading them from a temp `.pdf` path unlocked them — one camp went
    from 3 features to 36, another 8 → 21, another 5 → 23, another 4 → 22. Use it from the start next
    time rather than as a retry.
  - **~90 non-day-camps remain unsurveyed**, mostly the 62 registration-portal camps (nothing to
    survey) plus genuinely dead or wrong-camp links. These need link repair before survey, not more
    survey effort.
  - **Known under-recording:** the 294 surveyed camps were surveyed against the 95-term vocabulary, so
    they systematically miss the 26 codes added afterwards — rafting above all. This is within the
    documented contract (`features_verified_at` means a survey happened, explicitly not that the list
    is complete, and every surveyed camp says so in provenance), so nothing was re-queued. A cheap
    enrichment pass could add the new codes without re-surveying from scratch.
- **Phase 4 — publish — NEXT.** Coverage is now meaningful (77% of non-day-camps), so add `features` +
  `features_verified_at` to `current/camps.json` and the `published-current` contract (additive,
  MINOR). Keep them out of `{dataset}/index.json` — listings stay light. Until this ships, the
  features are only visible in the per-entity `v1/camps/{id}.json` documents.
- **Phase 5 — maintenance.** `signature` and long-tail entries decay fastest (a camp trials land
  sailing for two seasons), so they need a shorter re-verification cycle than facilities. Link health
  is now audited separately — see below.

### Camp link health (audit DONE 0.31.0; portal repair DONE 0.32.0)

`tools/check_urls.py` audits every non-day-camp `website` and classifies what is actually there.
Day camps (64) are deliberately out of scope: a day camp often runs at a rented site, so its property
link is weak by nature. Full run over the remaining **384 camps**:

| verdict | n | meaning |
|---|--:|---|
| `ok` | 180 | loads and names the camp |
| `portal` | 132 | a registration platform, not a descriptive page |
| `http_error` | 25 | 4xx/5xx |
| `stale` | 22 | loads, but newest content year is pre-2025 |
| `redirect` | 11 | loads and names the camp at a different final URL |
| `no_name` | 9 | loads but never names the camp |
| `unreachable` | 5 | DNS/TLS/timeout |

Done in 0.31.0: **8 of the 11 redirects canonicalised** — mostly council rebrands (`cpcbsa.org` →
`cpcscouting.org`, `seattlebsa.org` → `scoutingseattle.org`, `otcbsa.org` → `pccscouting.org`,
`bsaseabase.org` → `seabaseha.org`). The other 3 were deliberately *kept*, because the redirect
target is worse than the stored URL: La-No-Che redirects to a temporary host (`temp.`), Gardner Dam's
camp page is gone and lands on the council homepage, and Fire Mountain's target is a Cub-only
carousel item. Those three are really "page removed", not "page moved".

Done in 0.32.0: **portal-linked camps cut 132 → 62.** `tools/find_camp_pages.py` walks each
council's own website (homepage plus its camping-index pages, one level down) and looks for a link
whose anchor text or slug names the camp, then fetches the candidate and confirms it. Work is grouped
by council, so a council with four portal camps is crawled once — 132 camps live under just 85
councils, and every one of those councils already had a `council_website` stored. 74 of 132 produced
a confirmed candidate; **70 were applied** after a second classifier pass, each recorded in
provenance with the portal URL it replaced.

Judgement calls worth knowing: a candidate that is merely *stale* was still applied (7 of the 70) —
a 2023-dated council page still describes the camp, and this dataset deliberately holds no sessions
or fees, so staleness costs nothing here. Three were rejected by hand: a council homepage (no better
than the portal for surveying), a "Yellowstone High Adventure Outpost" page that may be a different
programme from Yellowstone Anglers Basecamp, and one candidate that was itself a portal.

Outstanding, in value order:

- **`portal` (62 left).** The council site had no findable camp page for these, so they need the open
  web or a leader's guide. Diminishing returns compared with the first 70.
- **Genuinely broken (30).** Only 4 hosts affect more than one camp (`utahscouts.org` ×5 and
  `okscouts.org` ×3, both still 429 even when polite; `scoutingcolorado.org` ×2 404; `nhscouting.org`
  ×2 500), so this is largely per-camp research.
- **`no_name` (9) needs eyes, not automation.** Some are real findings (Elk Lick points at a Wix
  index for a *different* camp; Camp Freedom at the TAC camps index), some are false positives (Lost
  Valley's page is on `ssrlv.org`, which encodes the name in the domain rather than the text), and two
  Colorado camps legitimately share their parent reservation's page (McNeil Scout Ranch).
- **`stale` (22)** is lowest priority: the page exists and names the camp, it is just not maintained.

**Findings from the 0.34.0 survey wave — human judgement needed, not automation.** Sixteen agents
read 285 camp pages by hand, which surfaced link problems the automated classifier cannot see:

- **Entity-identity questions, the highest-value class.** `nc-lumpkin-adventure-base`: the name
  "Lumpkin Adventure Base" appears *only* in meta keywords on the council's own domain and never in
  body copy, while the council markets the same facility as "Harrison High Adventure Base" — almost
  certainly a rename, and if so it wants a `renamed` lifecycle event, not a URL edit.
  `ut-camp-hinckley`: the stored `saltlakescouts.org` is a pre-merger domain that no longer resolves
  and `utahscouts.org/hinckley` 404s — mergers routinely retire camp pages along with the domain.
  Neither was guessed at; both files are untouched.
- **Lifecycle findings, from camps' own announcements.** MOHAB announces "MOHAB to Pause Following
  2026 Season" (no operation 2027–28, decision due 2029); Gorham announces closure "for the 2026
  summer sessions". Both are `operating_status` changes with a source, deliberately left for a
  lifecycle pass rather than folded into a features survey.
- **Wrong-camp links are worse than dead links** — they silently misinform instead of failing.
  Confirmed: `ia-little-sioux-scout-ranch` and `ga-camp-dani…` point at a different camp; two
  California camps' stored domains are now **squatted** (one is a gambling site), as is Tahosa's
  legacy domain.
- **Whole-council outages, not per-camp faults.** `nhscouting.org` 500s site-wide (`nh-camp-bell`,
  `nh-hidden-valley-scout-camp`); `alincolnscouting.org/camping` 404s (`il-camp-illinek`, left at 1
  feature). Re-test the host before spending research on the camp.
- **Sources that exist but cannot be read.** `wi-camp-rokilio`'s programme PDF is a scanned graphic —
  cheap for anyone with OCR, impossible without it. `ks-camp-mandan`'s guide attachment is gone.
  `ks-camp-kanza` remains the clearest dead end: a 2020 event page, registration closed six years ago.

⚠ **Method note for whoever re-runs this.** The first pass reported 65 hard failures; 35 of those
were self-inflicted — 10 concurrent workers rate-limited whole councils into 429s and tripped
timeouts. The checker now backs off on 429 (honouring `Retry-After`), retries transient failures, and
checkpoints so an interrupted run resumes. Re-run politely or you will libel a council's website.

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
  choose-needs-children + camp `operator`↔`council` coupling + coordinate bounds + vocab codes.
  Still TODO when relevant data lands: event-date ↔ version-boundary consistency;
  `HistoricalDate` month/day range; `StateCode` closed USPS set.
- **Published-projection schemas — DONE (0.28.0).** `build.py` now fail-fast-validates *every*
  published projection: all 8 `current/*.json` against `published-current.schema.json` (adding
  `CurrentRequirementSet`, previously the one unpinned surface) and all 8 `{dataset}/index.json`
  against the new `published-index.schema.json`. Each emitted file advertises its contract in
  `$schema`. See the v1.0 readiness section above.
- **Requirement-text licensing — DECIDED (0.5.0).** Verbatim requirement text IS published,
  marked © Scouting America (`includes_official_text: true` + `text_rights`), excluded from
  CC BY-NC-SA, reproduced non-commercially with attribution + takedown. Revisit if SA
  objects or a cleaner permission path opens.
