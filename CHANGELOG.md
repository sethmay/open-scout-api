# Changelog

One section per merge into `main`; newest first. Conventions: `skill://semver`.
Version anchors: this file only (no package manifests yet — add here when one appears).

## 0.32.0 (minor) — 2026-07-25

- `8ee339d` **Repaired the portal links: camps pointing at a registration platform fell 132 → 62.** These were the blocker on feature population — a registration link has nothing to survey. New `tools/find_camp_pages.py` exploits the fact that all 132 belonged to just **85 councils**, every one of which already had a `council_website` stored: it walks each council's own site (homepage plus its camping-index pages, one level down), finds a link whose anchor text or slug names the camp, then fetches the candidate and confirms the page really names it. 74 of 132 produced a confirmed candidate and **70 were applied** after a second pass through the link classifier, each recorded in provenance alongside the portal URL it replaced.
  - Ranking the candidates needed one non-obvious rule: **prefer the council's own domain, decisively.** An earlier "shallowest path wins" tiebreak looked sensible and was actively wrong — a bare root domain always wins on depth, so it picked the Illinek *OA lodge* and the Buffalo Bill *museum* over the councils' real camp pages. Host now dominates, with depth only breaking ties within a host. Candidate links to PDFs and images are skipped outright.
  - A merely **stale** candidate was still applied (7 of the 70): a 2023-dated council page still describes the camp, and this dataset deliberately carries no sessions, dates, or fees, so staleness costs nothing for the purpose. Three were rejected by hand — a council homepage (no better than the portal), a "Yellowstone High Adventure Outpost" page that may be a different programme from Yellowstone Anglers Basecamp, and a candidate that was itself a portal.
  - Candidates are written to a review file rather than applied automatically, and the tool is checkpointed and resumable. The remaining 62 have no findable camp page on their council's own site, so they need the open web or a leader's guide — diminishing returns next to the first 70.

## 0.31.0 (minor) — 2026-07-25

- `7dd595d` **Audited every camp's stored website and canonicalised the redirects.** New `tools/check_urls.py` fetches each non-day-camp `website`, follows redirects, and classifies what is actually there (`ok` / `portal` / `redirect` / `no_name` / `stale` / `http_error` / `unreachable`). Day camps (64) are out of scope on purpose: a day camp often runs at a rented site, so its property link is weak by nature. Across the remaining **384 camps**: 180 ok, 132 portal, 25 http_error, 22 stale, 11 redirect, 9 no_name, 5 unreachable.
  - **8 of the 11 redirects applied**, nearly all council rebrands — `cpcbsa.org` → `cpcscouting.org`, `seattlebsa.org` → `scoutingseattle.org`, `otcbsa.org` → `pccscouting.org`, `bsaseabase.org` → `seabaseha.org` — each re-verified as `ok` afterwards. The other **3 were deliberately kept**, because the redirect target is worse than the stored URL: La-No-Che lands on a temporary host (`temp.`), Gardner Dam's camp page is gone and dumps to the council homepage, and Fire Mountain's target is a Cub-only carousel item. Those are "page removed", not "page moved", and are queued as repairs instead.
  - **Corrects two claims from 0.30.0.** That entry reported Camp Yawgoog's website as the BSA health-record PDF and Chawanakee's as a dead calendar link. Both are wrong: each returns real HTML that names its camp, and the earlier readings were artifacts of how those pages were *fetched* during the spike, not properties of the stored URLs. Both are ordinary `portal` pages — thin for feature surveying, but not broken. The spike's honest count is 3 of 10 stored URLs genuinely wrong, not 5 of 10.
  - **The first audit pass libelled 35 councils and had to be redone.** It reported 65 hard failures; running politely (backing off on 429 with `Retry-After`, retrying transient failures, 3 workers instead of 10) cut that to **30**. The other 35 were this audit rate-limiting whole councils into 429s and tripping its own timeouts. The checker now backs off, retries, and checkpoints so an interrupted run resumes rather than discarding hours of work.
  - Remaining worklist in `TODO.md`: the 132 `portal` camps are the real blocker on feature population (a registration link has nothing to survey), 30 are genuinely broken (only 4 hosts affect more than one camp, so it is largely per-camp research), and the 9 `no_name` results need human eyes — some are real (Elk Lick points at a different camp) and some are false positives (Lost Valley encodes its name in the domain, not the page text).

## 0.30.0 (minor) — 2026-07-25

- `a8f2fb1` **Ran the program-features sourcing spike and expanded the vocabulary from its evidence** (TODO "Camp program features", Phase 0). 10 camps sampled deterministically across the two real source tiers, then surveyed by reading each council's own page. Yield is starkly tier-dependent: a **durable camp page was usable 5 times in 6** (Meriwether 21 features / 3 signature, Bowers 17 / 3, Emerald Bay 7 / 1, Chilkoot 4, Tunnel Mill 4), while a **registration portal was usable 0 times in 4**. Those five camps are now genuinely surveyed in `data/` — the first real `features` population — and carry `features_verified_at`.
  - **`camp-features` grew 13 → 46 terms**, every one observed on a real council page rather than invented: aquatics leaves (`sailing`, `kayaking`, `canoeing`, `surfing`, `fishing`, `floating_obstacle_course`), shooting-sports leaves (`archery`, `rifle`, `shotgun`, `bb_guns`, `black_powder`, `hunter_safety`), climbing leaves (`climbing_tower`, `alpine_tower`), genuine long-tail draws (`land_sailing`, `sandboarding`, `blacksmithing`, `living_history`, `gaga_ball`, `bike_park`, `marine_science`), facilities (`trading_post`, `bathhouse`, `pavilion`), accommodation (`platform_tents`, `cabins`, `flush_toilets`, `campsite_electricity`, `air_conditioning`, `boat_access`), and `provisional_attendance`. 16 terms carry `broader`, so the rollup promise is now exercised: a consumer asking the coarse "climbing?" question reaches Bowers through `alpine_tower → climbing`, and "aquatics?" through `kayaking → aquatics`.
  - **The binding constraint turned out to be broken URLs, not thin pages.** 5 of the 10 stored websites do not describe their camp at all: Elk Lick → a near-empty index for a *different* camp, Yawgoog → the BSA health-record PDF, Chawanakee → a dead calendar link, Verdugo Oaks → a registration page whose map is a church, Kanza → a 2020 event closed six years ago. A URL-health/repair pass is therefore a prerequisite for population rather than a side quest, and it is recorded as such.
  - Those five unsourceable camps deliberately keep `features_verified_at: null` — they certainly *have* features, we just could not source them, which is a different fact from "surveyed, offers none". The four-state field earned its place on its first real use.
  - The new alias guard caught a vocabulary incoherence introduced in 0.29.0: `climbing_tower` was both an alias of `climbing` and (per the spike) a term in its own right. A climbing tower is a specific thing *under* climbing, so it is now a code with `broader: climbing` and the alias is gone.

## 0.29.0 (minor) — 2026-07-25

- `f1bcd68` **Reshaped camp `features` for the program-features model** (PLAN §5.1) — the shape only; population follows. `features[]` is now an array of `{code, signature?, note?}` instead of bare codes, so one filterable namespace carries both widely-shared features and long-tail differentiators: `code` is the only filterable key, `signature` marks a headline draw (per camp-feature pair, because the same feature is table stakes in one region and a differentiator in another), and `note` adds a short factual phrase where a code alone under-describes the offering. All 448 camps were migrated (8 had features; codes are byte-for-byte preserved). Nothing published changed — `features` still appears only in the per-entity documents, and joins `current/camps.json` later once coverage is meaningful.
  - Added **`features_verified_at`**, the field that makes `features` interpretable. Four distinct states rather than a boolean: `null` + `[]` = never surveyed, nothing known (440 camps today); `null` + entries = incidental data from a bulk import, not a survey (the 8); a date + entries = surveyed; a date + `[]` = surveyed and the camp genuinely offers none. Without it an unsurveyed camp is indistinguishable from an empty one, every "has X" filter silently under-reports, and "camps *without* X" is unanswerable — the same discipline `geo_precision` already applies to coordinates.
  - Vocabulary terms may now carry **`category`** (`facility` / `activity` / `program_model` / `accommodation` / `subject` — the 13 existing codes were four different kinds of thing in one flat list), **`broader`** (a coarser parent so specific leaves answer general queries), and **`aliases`** (synonyms absorbed during curation, never valid data values). All 13 `camp-features` terms are categorized; 6 carry aliases (`atv` ← quads/four_wheeling, `cope` ← ropes_course/challenge_course, …).
  - Six new validator guards, each proven to bite by injection: a duplicate feature `code` within one version (schema `uniqueItems` stops catching this the moment two entries differ in `note`/`signature`), a `note` carrying transitory text (reuses the evergreen `summary` guard), `broader` naming an undefined term, a `broader` cycle, an alias colliding with a real code, and one alias claimed by two terms. Two negative fixtures cover the new item-level strictness (unknown property, missing `code`), so the fixture suite is now 8 positive / 10 negative.

## 0.28.1 (patch) — 2026-07-25

- `4630d2b` Documented the **camp program-features model** (design + implementation/population plan; no data, schema, or code change yet). `PLAN.md` gains §5.1: standard features and long-tail differentiators are the *same* axis at different granularity, so they share one coded, filterable namespace (`land_sailing` is as legitimate a term as `dining_hall`) with vocabulary hierarchy for coarse rollup — rather than a second "highlights" field that consumers would never filter, which would make differentiators invisible. `features[]` becomes `{code, signature?, note?}` (`signature` is per camp-feature pair, since the same feature is table stakes in one region and a draw in another), plus a mandatory `features_verified_at` so an unsurveyed camp stops being indistinguishable from one that has nothing. Vocabulary terms gain `category` / `broader` / `aliases`.
  - Grounded in two measurements: `features` is populated on only **8 of 448 camps** and is published in **no** projection, so the reshape is free until `v1` freezes at 1.0; and of 448 camps, **159 publish `url == council_website`** (no camp-specific page), which makes sourcing — not modelling — the risk. `TODO.md` gains a phased plan that starts with a 12-15 camp sourcing spike to measure yield per source tier before committing.
  - Recorded a **retraction**: inferring features from per-camp merit-badge offerings cannot work as proposed — no per-camp offerings exist in `data/`, and their only source is the scoutingevent registration layer this dataset deliberately excludes. The council's own page proved richer (Camp Meriwether headlines "Land Sailing … unique to Camp Meriwether", which our 13-code vocabulary had no way to represent — while our own `summary` prose already mentioned sailing and surfing).

## 0.28.0 (minor) — 2026-07-25

- `d93d31b` **Contract-freeze prep for 1.0: every published collection projection is now schema-pinned and build-gated.** `build.py` fail-fast-validates all 16 collection projections — the 8 `current/*.json` denormalized views against `published-current.schema.json`, and all 8 `v1/{dataset}/index.json` listings against a new **`published-index.schema.json`** — and each of those 16 files advertises its contract in `$schema`. Previously only 7 of the 16 were validated, so 9 published surfaces were unpinned promises. In both schemas the item shape is now selected BY the envelope `kind` (an `allOf` of `if kind then items.$ref`) rather than a bare `oneOf`, so a listing cannot publish another dataset's item shape at a right-looking URL. Verified non-vacuous: unknown fields, missing required fields, a bad `kind`, a malformed `council:` ref, a non-slug `reservation.id`, and kind/item mis-pairings are each rejected, and the build exits nonzero rather than warning. (Still unpinned, tracked for 1.0: `v1/meta.json`, `v1/camps/aliases.json`, and the per-entity documents.)
  - **`current/requirement-sets.json` is pinned** via a new `CurrentRequirementSet` def (it was the one `current/` file with no contract and no `$schema`). It also gained `includes_official_text` — the licensing flag its own index already carried — plus `verified_at` / `method` / `confidence`, making provenance uniform across all 8 current projections (it was the lone holdout). Additive; nothing renamed or removed.
  - **`reservation.id` is now contractually a stable opaque grouping key** — a bare slug, deliberately *not* a `kind:slug` EntityRef, since no reservation entity exists. Documented in both the canonical `camp` schema and the published contract, and the slug shape is now enforced. This keeps first-classing reservations later strictly additive: a future entity reuses these exact slugs and any reference arrives as a NEW field rather than changing this one.
  - **`v1/territories/index.json` now carries `number` + `division_type`.** That listing mixes current Council Service Territories, closed National Service Territories, and pre-2021 regions; without these a consumer had to parse the display name or the id to tell them apart. Both already existed canonically and in `current/territories.json`.
  - Tightened three latent inconsistencies found in review: `oa-lodge.council` is now `^council:`-patterned in the canonical *and* published layers (all 238 comply; previously the index enforced it while the canonical and current layers did not, so one field had three answers); `_prov()` honours `provenance.confidence`'s declared `default: 1` instead of raising `KeyError` on a record that legitimately omits it; and `camps/aliases.json` key order is now deterministic (`sorted()` over a set — it previously varied with `PYTHONHASHSEED`).
  - `TODO.md` gains a **v1.0 readiness** section recording what the freeze cleared and the one remaining blocker (the permanent home / `$id` base URL, an owner decision that also gates the Zenodo DOI). Also corrected a stale claim that camp `operator`↔`council` coupling was unimplemented — it has been running in `validate_data.py`.

## 0.27.0 (minor) — 2026-07-25

- `5fa923c` Added **`july_high_f` / `july_low_f`** to every camp — the average July daily high and overnight low in °F, a WorldClim v2.1 1970-2000 climate normal sampled at 30 arc-seconds (~1 km) from each camp's own coordinate. Set on 447 of 448 camps (the lone null is the overseas Malaysia camp, which has no coordinate). Both are new optional additive fields on the canonical `CampVersion` and the `v1/current/camps.json` projection, and inherit `geo_precision`; a coastal camp whose 1 km cell is open water falls back to the nearest land cell (4 camps). Values span 64-105°F, median 84°F — Heard Scout Pueblo (Phoenix) 105°F, Tahosa at 9,160 ft 72°F, Camp Gorsuch AK 65°F.
  - Added `tools/july_temp.py`, a run-manually enrichment that samples the WorldClim rasters (cached per coordinate in `tools/july_temp.json`; re-runs are offline and deterministic). It is the first tool with a non-stdlib dependency (`rasterio`) and a bulk source download (~8 GB, git-ignored) — both strictly tool-only: because the derived cache is committed, CI, validation, and consumers need neither. WorldClim is free for non-commercial use and its rasters may not be redistributed without permission, so only derived point values are published, under this project's existing CC BY-NC-SA 4.0; attribution and the Fick & Hijmans (2017) citation added to `NOTICE.md`.

## 0.26.1 (patch) — 2026-07-22

- `d7249c2` Added **Camp Kenya** (`ae-camp-kenya`) — Transatlantic Council's (#802) winter resident camp held at the Savage Wilderness Adventure Camp near Sagana, Kenya (~3 hours from Nairobi). camp-finder never captured this overseas camp, so it was missing from the map; added by hand from the council's [camp page](https://tacscouting.org/camps/campkenya/), coordinates geocoded to the Savage Wilderness property (`exact`, 3700 ft). Classified `resident_camp` with Cub, Scouts BSA, high-adventure, Mount Kenya trek, Sea Scout, family, and adult-training programs. Camp count is now 448; this is the first `curated` (non-imported) camp in the dataset.

## 0.26.0 (minor) — 2026-07-22

- `d0a36c7` Added `elevation_ft` to every camp — ground elevation in feet above sea level, from the Copernicus 90 m DEM via the open-meteo elevation API, rounded to the nearest 10 ft. Set on 446 of 447 camps (the lone null is the overseas Malaysia camp, which has no coordinate). It is a new optional additive field on both the canonical `CampVersion` and the `v1/current/camps.json` projection, and inherits `geo_precision` — an `approximate` point yields a city/reservation-centroid elevation, not the camp's exact ground.
  - Added `tools/elevation.py`, a live run-manually enrichment that fills `elevation_ft` from each camp's coordinate (cached by coordinate in `tools/elevation.json`; re-runs are offline and deterministic).

## 0.25.5 (patch) — 2026-07-22

- `d62f1d5` Resolved the flagged `wi-adventure-camp`: it was Twin Valley Council's (Mankato, MN) Scouts BSA session held at Tomahawk Scout Reservation (Northern Star's camp, Birchwood WI) — the same physical property as `wi-tomahawk-scout-camp`, not a distinct camp, a mislocation, or a Camp Decorah duplicate. Merged in; the old id resolves via `aliases.json`. Camp count is now 447.

## 0.25.4 (patch) — 2026-07-22

- `84125e0` Refined 16 camp coordinates from `approximate` (a city/reservation centroid) to `exact` by geocoding each camp's own street address. Several were also grossly mislocated and are now correctly placed — e.g. Camp Cris Dobbins to Peaceful Valley near Elbert CO, Camp Horseshoe to Rising Sun MD, Big Four Camp to Minot ND. `geo_precision` is now 336 exact / 111 approximate / 1 null.
  - Added `tools/geocode_addresses.py`, a live enrichment that upgrades any approximate camp with a unique street address (cached in `tools/geocode_addresses.json`). Camps with only a zip/city or a shared reservation-gate address stay `approximate` — an honest signal that the point is not camp-specific.

## 0.25.3 (patch) — 2026-07-22

- `131aecf` Maintainability: documented the go-forward edit model now that camp-finder consumes this API instead of sourcing it (no data or schema change).
  - `data/` is the authoritative source. The README "Contributing" section now describes editing the canonical JSON directly, the `stamp` → `validate` → `build` steps, and how camp renames/merges use `merged_from` + `aliases.json`.
  - Marked `tools/import_camps.py` and `tools/geocode_camps.py` as HISTORICAL one-time camp-finder seed tools (they run only if the retired source is restored); kept for provenance. Repo-layout now separates the live pipeline from the seed tools.

## 0.25.2 (patch) — 2026-07-22

- `f09d471` Data-quality sweep: corrected scraped-artifact camp names and a coordinate error (community-report follow-through).
  - Renamed 9 camps whose names were scraped registration-event titles to their real property names, each verified against the council's own camp listing: Krupp Scout Hollow, Camp Loud Thunder, Camp May, Camp Durant, Camp Manatoc, Seven Mountains Scout Camp, Camp Independence, Mount Norris Scout Reservation, and Bear Paw Scout Camp. Ids are now clean slugs; prior ids resolve via `aliases.json`.
  - Merged a duplicate: "Scouts BSA Weekend Camp 2026 - New" was the existing Camp Lawton (Catalina Council). Camp count is now 448.
  - Corrected Chilkoot High Adventure Base's coordinate — it was stamped on Denali High Adventure Scout Base's point about 600 km away, and is now at Haines; the two are no longer grouped as one reservation.

## 0.25.1 (patch) — 2026-07-22

- `fd360b8` Renamed the Virginia camp shown as "Scouts BSA Long-Term" to **Pipsico Scout Reservation** (Tidewater Council, Spring Grove, near Williamsburg). The old label was a scraped registration-event title; the camp's own address (57 Pipsico Road) confirms the property. Its id is now `va-pipsico-scout-reservation` with the prior id resolving through `aliases.json`, and its city (Spring Grove) is filled in. Community-reported.

## 0.25.0 (minor) — 2026-07-21

- `b80dc45` Named the reservations that group co-located camps, so a map pin reads "Goshen Scout Reservation" instead of an unlabeled cluster.
  - Added verified names to 13 reservations (Goshen, Warner, Peaceful Valley, Ben Delatour, Beaumont, S-F, Griswold, Mount Allamuchy, Ten Mile River, Heritage, Musser, Heart of Virginia, Tomahawk). 17 of 19 reservations now carry a name, and a named reservation's `reservation.id` is now its name slug (for example `va-goshen-scout-reservation`).
  - Unified Goshen Scout Reservation: its 6 camps sat on two nearby points as two groups and are now one reservation.
  - Reservation grouping now requires the same council, which drops a false group where two camps in different councils shared a backfilled coordinate (Camp John Mensinger / Camp Verdugo Oaks — now ungrouped).
  - Two reservations stay unnamed on purpose: an Alaska pair whose shared point is a known coordinate error, and a Wyoming pair with no distinct reservation name.

## 0.24.0 (minor) — 2026-07-21

- `b7f4d54` Finished collapsing duplicate camp listings and grouped the co-located rest under their reservation, so the map shows one pin per real place.
  - Merged 9 more same-camp splits whose slugs did not share a prefix: Yellowstone Anglers' Basecamp (Full + Half Week), Camp Workcoeman (cub day + resident), Camp Carpenter, Camp Potomac, Camp Fiesta Island (+ its Webelos program), Camp Mitigwa, Rhodes France, Alpine Scout Camp, and Parker Scout Reservation. Camp count is now 449; retired ids resolve through `aliases.json` (38 total).
  - Added `reservation` (`{id, name}`) to camps that share a location with other distinct camps, so a site can render one reservation pin that expands to its camps. 21 reservations group 45 camps; 4 carry a derived name (Falley, Owasippe, Massawepie, Ma-Ka-Ja-Wan) and the rest are unnamed where the camps share no common name (for example Goshen's four camps).
  - Kept Camp Dexter C. Hobbs and the Heart of Virginia cub camp as distinct camps (proper names / own site), grouped under their reservation rather than merged.

## 0.23.1 (patch) — 2026-07-21

- `aaf7fc9` Fixed `geo_precision` on 49 camps that share a coordinate with another camp. A point shared by two or more distinct camps is the reservation's center, not an exact fix for any one of them, so those are now labeled `approximate`. A site can trust `exact` for precise pin placement and soft-plot or cluster the `approximate` ones (for example the four camps at Goshen).

## 0.23.0 (minor) — 2026-07-21

- `4e93f00` Collapsed duplicate camp listings so each physical property is one entity (one map pin) instead of one row per program.
  - Merged 29 program and session variants (for example "Camp C.S. Klaus - Cub Scout Day Camp" and three more Klaus rows) into their base camp, unioning the program types. The camp count is now 458, down from 487.
  - Published `v1/camps/aliases.json`, a map from each retired id to its surviving camp id, so a site can redirect old links.
  - A survivor records the ids it absorbed in `merged_from`, and a build check keeps those ids retired and unique.
  - The `parent` reservation link is empty for now: once coordinates were corrected (0.22.0), every one of these proved to be the same physical camp, not a distinct sub-camp. `parent` stays in the schema for genuinely separate sub-camps (distinct location) later.

## 0.22.0 (minor) — 2026-07-21

- `1ad634b` Fixed camp map coordinates so a distance search does not silently lose or misplace camps.
  - Backfilled 99 camps that had no coordinates or sat in the wrong state (75 were missing, 24 were mislocated, one a Colorado camp plotted in Alaska), using city-level geocoding from the council's own town.
  - Added `geo_precision` on every camp (`exact`, `approximate`, or `null`) so a site can soft-plot or bucket the approximate points instead of trusting them as precise.
  - Added a build check that rejects any camp coordinate outside its state box, so this class of error cannot return.
  - Only one camp (an overseas base with no US state) is still unplaceable, down from 75.

## 0.21.0 (minor) — 2026-07-21

- `4e6c480` Camp listings now carry a real "last verified" date instead of the import date, so a site can flag the ones due for a fresh check.
  - `verified_at` now carries camp-finder's own source-confirmation date (it spans 2025 to 2026 instead of a single import day), which makes a "confirm if older than 12 months" badge actually fire.
  - Added `imported_at` for the date we ingested the record, kept separate from `verified_at`.
- `4e6c480` The camp `url` is now a durable link. The 168 per-season registration deep-links (10 year-stamped pages and 158 scoutingevent.com registration portals) fall back to the council's own page, so the primary "visit camp" link does not 404 next season.
  - Also documented the confidence bands (0.9 / 0.8 / 0.6) alongside the projection contract in the README.

## 0.20.0 (minor) — 2026-07-21

- `3d8b517` Camps are now grouped under their reservation, so a site can nest sub-camps instead of listing them flat.
  - Set the `parent` link on 29 camps that are a sub-camp or sub-program of a larger property (for example, "Camp Tukabatchee Webelos/AOL Resident Camp" now points to Camp Tukabatchee).
  - Links are derived from the camp set itself (a camp whose slug, or whose "... at X" name, sits under another camp in the same council), so no outside data is needed and it stays in sync.
  - `parent` is now included in `current/camps.json`.

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
