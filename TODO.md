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
| 6 | **Rank requirement history** | ✅ `rank` + `requirement-set` (`subject: rank:*`) | 🌱 **SEEDED (0.8.0-0.10.0); ALL PROGRAMS (0.15.0); CUB ADVENTURES (0.43.0); AREAS (0.44.0); PRE-2024 LINE-UP (0.45.0):** 21 rank entities (7 Scouts BSA + 6 Cub + 4 Venturing + 4 Sea Scout) + 47 requirement-sets. Scouts BSA: 2024 (No. 33216) + 26 historical editions (2016-2023) via usscouts.org with `supersedes` chains. Cub/Venturing/Sea Scout: current requirements from official scouting.org pages + 2026 Sea Scout PDFs (verbatim-verified). **Cub adventure detail DONE in 0.43.0** — 139 entities + 131 requirement-sets; the six Cub rank trees are two groups of `ref`s into them. **The six requirement areas DONE in 0.44.0.** **The pre-2024 line-up DONE in 0.45.0** — 38 retired adventures, 121 historical editions, 38 lifecycle events, from the USSSP archive. Follow-ups: pre-2016 Scouts BSA editions; historical editions for Venturing/Sea Scout; the pre-2024 **rank** structure ("6 core + 1 elective", and Bobcat as a *rank* before 2024 — it is an adventure only since then, so it is deliberately absent from `data/adventures/`); the ~24 pre-2024 "preview" adventures (Protect Yourself Rules / Yo-Yo / Modular Design, on their own source pages); the 2018 Tiger elective edition, which usscouts does not archive. | 2024 Scouts BSA Requirements; usscouts.org; scouting.org; seascout.org PDFs |
| 7 | **OA lodges** | ✅ `oa-lodge` | 🌱 **SEEDED (0.13.0):** 238 lodges from the official OA lodge locator feed (oa-bsa.org), all linked to their chartering `council` + OA section/region + HQ/coords + website; officer/contact PII excluded. Follow-ups: lodge numbers (not in feed), merger/rename history + events (track council mergers), totem. | oa-bsa.org lodge locator feed; ScoutWiki/Fandom (numbers/history) |
| 8 | **Merit badge popularity by year** | ✅ `merit-badge-ranking` | 🌱 **SEEDED (0.47.0):** 5 years (2021-2025), 692 badge-year ranks, every year a complete 1..N, from On Scouting's annual recap. ⚠ **Renamed from "earned-counts": Scouting America publishes RANKS ONLY** — no absolute number appears in any post — so `metric` is `earned_rank` and the schema rejects `earned_count`. Prior-year columns recover 2021 and corroborate 2022/2024; one 2022 typo corrected from the 2023 restatement. The three 2025 badges (Artificial Intelligence, Cybersecurity, Multisport) were dated to 2025 in 0.47.1, which makes the ranked-before-it-existed gate load-bearing against real data. Follow-ups: pre-2021 years (older posts exist and were not walked). | On Scouting (onscouting.org) annual merit badge rankings |
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

**Remaining 1.0 blocker (owner decision): the permanent home / `$id` base URL.** All 2,311 entity
files carry `$schema: https://sethmay.github.io/open-scout-api/schema/v1/…`, `build.py` hardcodes
that base, and it is both the documented API root and the jsDelivr pin path. It also gates the
Zenodo DOI, which binds to the final GitHub location.

**The mechanics are no longer the hard part — `tools/restamp_identity.py` (0.42.1) makes it one
command.** It moves the two identities *independently*, reads today's values out of `build.py`
rather than hardcoding them, dry-runs by default, and after `--apply` verifies that zero stale
references survive:

- `--api-base` — the published root that every schema `$id` and documented URL hangs off.
- `--repo owner/name` — source links, tool User-Agent strings, the Zenodo related_identifier.

Scoped so unrelated things do not move: `.zenodo.json` `creators` stays (authorship is a person,
not a host) and `github.com/<owner>/camp-finder` in the README stays (different project). Proven by
a full round trip — re-stamped to a throwaway identity, `validate_data` + `build` + `build_sqlite`
+ `validate_examples` all passed, every published surface moved (`meta.base_url`, every `$schema`,
the SQLite `source` row), then re-stamped back **byte-identical** to HEAD.

**DECIDED 2026-07-27 (owner): keep `https://sethmay.github.io/open-scout-api` for now. A permanent
home is still being negotiated, so 1.0 stays UNCUT — deliberately, not for want of work.**

⚠ **Do not cut 1.0 until the home lands.** 1.0 is the promise that `v1` is additive-only forever:
no renames, no removals, safe to pin. Freezing that promise onto a URL we already intend to move
would break it on purpose the first time the move happens — which is worse than having no promise
yet. Everything else on this list is cleared, so the tag is waiting on one external decision and
nothing more.

What that means concretely, and what is already true:

- **Consumers can use the API today**, and everything published is schema-pinned and build-gated
  (0.41.0). What they cannot yet rely on is the *permanence of the host*, so the README should keep
  saying so until 1.0.
- **The move itself is cheap and rehearsed** — `tools/restamp_identity.py --api-base … --repo …`,
  round-trip verified byte-identical (0.42.1). Whichever home is negotiated, it is one command plus
  a rebuild, a CHANGELOG entry and a tag.
- **Zenodo DOI stays deferred** for the same reason: the record binds to the final GitHub location.
  `.zenodo.json` is already written and correct, so enabling it later is a toggle at zenodo.org.
- **Strong preference when the choice reopens: a custom domain.** It is the only option that makes
  the published identity independent of GitHub, so a later account-or-org move becomes invisible to
  consumers rather than another breaking event. The trade is a registration plus auto-renew, and the
  live risk is letting it lapse, which would 404 every `$id` in the wild — register long and lock it.
  Second choice is a GitHub org; staying on a personal account is the option that keeps this exact
  decision open indefinitely.

**Every published endpoint is now pinned — CLEARED IN 0.41.0.** The last 10 unpinned surfaces were
`v1/meta.json`, `v1/{dataset}/aliases.json`, and the 8 per-entity `v1/{dataset}/{id}.json` families,
whose shape existed only inside `build.py` — so renaming `events` was a one-line edit no gate would
catch. Three new contracts close it, and `build.py` fail-fast-validates **1,774 published files**
(1,756 per-entity + 16 collections + meta + aliases):

- **`published-entity.schema.json`** — the deep surface, kind-selected: versioned entities
  (`versions` non-empty, `events` folded in under that exact key, resolved participant refs),
  versioned entities that also carry `requirement_sets` (merit-badges/ranks/awards/adventures), and
  requirement-set documents (effective-dated, no versions, no events). Scope is deliberate: it pins
  the **envelope and the projection**, because each `version`'s interior is already validated against
  its canonical schema by `validate_data.py` before the build runs. It also enforces a licensing
  invariant the canonical layer only checked indirectly: **a document with
  `includes_official_text: true` MUST carry `text_rights`**, so verbatim © Scouting America text can
  never be published without its carve-out stated on the document itself.
- **`published-meta.schema.json`** — the discovery document. `endpoints` and `vocab` are the
  machine-readable index of the whole API, and `unofficial` is `const: true` and required, so a
  consumer cannot lose the no-affiliation fact by reading a subset.
- **`published-aliases.schema.json`** — the `{retired-id: surviving-id}` map, pinned as a bare
  lookup via `propertyNames` + `additionalProperties` rather than being wrapped in an envelope,
  which would have been a breaking shape change for the one file whose only sane use is a direct
  lookup. It is therefore also the one published file that carries no `$schema` key: a `$schema`
  entry in a bare map would read as an alias, and the contract rejects it.

Per-entity documents and `meta.json` now stamp `$schema` like every other published file, which
realises the intent already commented in `build.py` ("dist files reference published schemas").
Verified non-vacuous by injection — renaming `events`, dropping or ref-prefixing
`requirement_sets`, emitting an entity with zero versions, removing `unofficial` from meta, a
non-slug alias value, and stripping `text_rights` from a document with official text are all
rejected.

## Queue

### Requirement-set `effective_to`: two abutment styles in one dataset

Found while adding the pre-2024 Cub editions (0.45.0). Merit-badge editions close on the **last
day they applied** (`chemistry-2020` ends `2023-12-31`, `chemistry-2024` starts `2024-01-01`);
adventure editions close on the **day the successor took effect** (`…-2018` ends `2024`, `…-2024`
starts `2024`) — the half-open convention entity `versions` already use and `validate_data.py`
already enforces there. The schema never stated which, which is exactly how they diverged, and a
consumer asking "which edition applied on date D" cannot write one predicate.

`validate_data.py` now forbids overlaps, multi-year gaps and mid-chain open editions under *either*
style, so nothing is broken — but this should be unified and stated in
`requirement-set.schema.json`. Half-open matches the schema's own wording ("when a later revision
superseded this one") and the rest of the dataset; adopting it means re-dating ~400 published
merit-badge/rank editions, which is a data migration deliberately not bundled into a Cub-adventure
release. Decide, migrate, and document before 1.0 freezes the shape.

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
3. **Camp `summary` (evergreen prose) — DONE (0.26.x).** `summary` is on `CampVersion` and in the
   projection; **371 of 448 camps carry one**, regenerated as original prose rather than scrubbing
   camp-finder's contaminated descriptions, and `validate_data.py` rejects 4-digit years, `$`, and
   month names so evergreen is an enforced gate rather than a convention. (The same guard now
   covers merit-badge descriptions and camp feature notes.)
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
  - **Known under-recording — mostly repaired in 0.35.0.** The 294 camps were surveyed against the
    95-term vocabulary and so could not carry the 26 terms added afterwards. Publishing made the
    damage visible and unacceptable: `whitewater_rafting` matched **0 camps** despite 15 surveyed
    pages describing it. 182 of the wave's 226 proposals were recovered and 103 entries applied
    across 68 camps, cutting zero-camp vocabulary terms 30 → 6. The 6 that remain
    (`coral_restoration`, `fossil_dig`, `maple_sugaring`, `surfing`, `automotive`,
    `performing_arts`) are genuine rarities, not artefacts. Residual gap: ~44 proposals from four
    agents were unrecoverable, so a handful of camps still under-record.
- **Phase 4 — publish — DONE (0.35.0).** `features`, `features_signature`, and
  `features_verified_at` are in `current/camps.json` and pinned in the `published-current` contract
  (additive; all three required, so the build fails if the projection ever silently drops them).
  Deliberately **codes only** — the prose `note` stays in the per-entity `v1/camps/{id}.json`,
  because this projection is the filterable one and republishing notes cost +43% file size for text
  no filter reads (+12% for codes: 466 → 605 KB). `{dataset}/index.json` listings stay light.
  `features_signature` is published separately for ranking and badges, never for filtering. If
  consumers ever want the notes inline, they arrive as a new additive `features_detail` field.
- **Phase 5 — maintenance — MACHINERY DONE (0.36.0), the queue itself is ongoing.**
  `tools/maintenance.py` encodes the re-verification policy and is the standing health check.
  Different facts decay at different rates, so one "last verified" date cannot drive planning:
  **signature features 12 months** (the most perishable thing here — a camp trials land sailing for
  two seasons and drops it), **ordinary features 24**, **website 6** (`check_urls.py` does the
  fetching; this only ages it), **provenance 24** (identity and coordinates are close to inert).
  - **Every clock reads zero today**, because the whole corpus was verified in the 0.33–0.35 waves.
    That is exactly why the tool also reports what a clock cannot see: 154 never surveyed, 2 with no
    website, and the zero-use vocabulary count promised in `LESSONS.md`. A report that only aged
    dates would have looked healthy and said nothing.
  - **First real find: 445 entities carried duplicated provenance sources** (535 redundant entries,
    16% of all 3,425), left by successive passes appending the same url — sometimes bare, sometimes
    with an `accessed` date. `--fix-sources` collapses them keeping the richest entry; verified zero
    urls and zero `accessed` dates lost. Repairs stay behind an explicit flag, per the
    `--overwrite` convention.
  - **Coverage recovery (0.37.0): 90 unsurveyed non-day camps triaged, 10 surveyed, 79% coverage.**
    The 90 split into 62 registration-portal camps, 26 with their own page, and 2 with none. Running
    the link classifier over the 26 found **14 genuinely surveyable** — and five of them
    (`va-blue-ridge-scout-reservation`, `va-camp-bowman`, `va-camp-marriott`, `va-camp-pmi`,
    `va-camp-rock-enon`) were exactly the "final five payloads" an agent announced writing
    immediately before it exited non-zero in the main wave. **The wave did lose work** — not
    corrupted, just never written. Verifying that what landed on disk was valid did not prove that
    everything assigned had landed at all; check both next time.
    - Two agents surveyed the 14: **10 usable, 280 features, 16 signature, zero invented codes**;
      4 correctly left untouched with `features_verified_at: null`. Non-day coverage 77% -> **79%**
      (304/384), feature entries 4,329 -> **4,609**.
  - ~~**Negative result worth keeping: the guide-PDF lever does NOT rescue the 62 portal camps.**~~
    **RETRACTED IN 0.38.0 — the spike was measuring a tool bug, not the data.** It reported 0 hits
    across 12 camps and I concluded "cheap automation is exhausted for the 62". Wrong. Reading a
    `scoutingevent.com` URL without a selector follows a redirect to an empty "you have not selected
    a calendar" shell; **the same URL read with `:raw` returns the real page, blurb and all.** Two
    earlier passes and my spike all mistook that shell for the camps' actual content. With `:raw`
    plus the Black Pug per-camp facility pages, **all 62 proved surveyable.** Lesson recorded: when
    a whole population looks uniformly empty, suspect the instrument before the population.
  - **Portal wave (0.38.0): 62/62 surveyed, non-day coverage 79% -> 95%.** Four agents,
    **1,752 features, 49 `guide` + 13 `camp_page`, ZERO `portal` tier, zero untouched, zero invented
    codes.** Feature entries 4,609 -> **6,361**; median surveyed camp now carries ~15 features.
    The three techniques that did it, all reusable:
    - `scoutingevent.com/<key>:raw` — mandatory, see above.
    - `campreservation.com/<councilOrgId>/Camps/<campId>` — Black Pug's council-authored per-camp
      facility inventories stay live long after the matching event key expires.
    - Guidebooks behind vanity subdomains redirecting into Google Drive: curl to a temp `.pdf`
      (append `&confirm=t` to the `drive.usercontent.google.com/download` URL).
  - **Why these camps looked orphaned, and the test that settles it.** A council with no page for a
    camp it demonstrably operates often does not *own* it: Camp Coker belongs to the Camp Coker
    Trust and is leased to Indian Waters Council, Floodwood is run with an alumni association. Look
    for a trust, foundation, or "Friends of" with its own domain. **Refinement that keeps this from
    being over-applied: asymmetric silence is the signal** (a council promoting a sibling camp while
    silent on this one); uniform silence just means the council's whole site is unreadable, and
    there is no separate owner to find.
  - **Poisoned domains are a live hazard.** `baitinghollowscoutcamp.org` resolves, carries the
    exactly-correct camp title, and is squatted SEO spam with a paid backlink to a termite company;
    two other camp domains in this project are squats, one a gambling site. **Test: a genuine camp
    site names its council or owning body in its own prose.** Perfect name + no council named = walk
    away.
  - Held-back vocabulary proposals, recorded here because the files are not kept. From the recovery
    batch: `ocean_beachfront`, `tabletop_gaming`, `eagle_advancement_intensive`, `outdoor_cooking`,
    `skilled_trades`, `heater_stack_dining`, `live_animal_exhibit`, `cascading`, `day_camp_option`,
    `whitewater_canoeing`. From the portal wave: `air_rifle`, `paintball`, `log_rolling`,
    `cultural_excursion`, `historic_mine_tour`, `rc_vehicles`, `sauna`, `mini_golf`, `pedal_boats`,
    `free_fall_jump`, `observation_tower`, `game_room`, `windsurfing`, `drone_racing`, `fire_tower`.
    Re-rejected again: `family_camp` (an audience, already in `camp-program-types`) and `waterfall`
    (a landscape feature). `giant_swing` was on this list last release, recurred, and is now a code —
    the second-sighting rule works, keep using it.
  - Still open: the 18 non-day camps that remain unsurveyed, the 43 thin surveys queued for review
    (below), and the 4 zero-use vocabulary terms (genuine rarities — watch, do not prune).

### Advancement graph — Eagle slots DONE (0.48.0); positions of responsibility open

Eagle requirement 3 is structured: 14 slots, three either/or, every badge `ref`-resolved, gate-tied
to `eagle_required` (which marks the 18-badge list, not the slot count). Remaining:

- **Positions of responsibility.** Eagle requirement 4 and Star/Life requirement 5 list ~40
  positions across three unit types (Scout troop / Venturing crew + Sea Scout ship / Lone Scout) in
  one prose blob each. Structuring them as `choose: 1` groups of text nodes is cheap; making
  positions first-class entities is the larger question, and nothing else in the dataset references
  a position yet.
- **Star and Life badge counts.** "Six merit badges, including any four from the required list"
  (Star) and "five more ... including any three additional" (Life) are countable rules still living
  in prose. They reference Eagle's list rather than restating it, so structuring them means a
  cross-rank reference the schema has no shape for yet.
- ⚠ **The in-force Eagle requirements require a discontinued badge.** `eagle-2024` (effective
  2024-01-01, `effective_to: null`) lists Citizenship in Society at slot (d); Scouting America
  discontinued that badge on 2026-02-27. A newer Eagle edition presumably exists and we do not have
  it — until then the dataset faithfully reports a rule that reality has moved past.

### Camp feature accuracy audit — `python tools/audit_camp_features.py --all`

Added 0.46.0 after a user spot-check found two defects `validate_data.py` structurally cannot see:
a feature no source attests (Camp Baker's `mountain_biking`, an inherited LLM guess) and a survey
that stopped at an index page (Camp Parsons' unread `/program/`, holding its ATV program). The tool
re-fetches each camp's cited sources plus the program pages they link to and reports three lead
types: no lexical trace, page-names-record-omits, and uncited program pages.

**Not yet run across the corpus** — only the two camps in this release. Running `--all` over the 366
surveyed camps is the obvious next sweep, and the two leads it already surfaces are worth designing
for first:

- **Match per source, not against the concatenation.** A camp's council-wide page can attest a
  feature belonging to a *different* camp of that council (it suggested `trading_post` and
  `leadership_training` for Parsons on that basis). Keeping the hit's source URL would both cut the
  noise and let a real finding cite its evidence.
- **Uncited PDFs.** Baker's remaining lead is a merit-badge schedule PDF the survey never read;
  guidebook PDFs were the richest source in the 0.38.0 wave (`guide` camps average 21 features
  against 13), so PDF-aware fetching is likely where the next real coverage lives.
- Terms whose every word is generic (`older_scout_program`, `high_adventure_option`) are reported as
  *not lexically checkable* and will need a human or a different signal entirely.

### Manual review queue — `python tools/maintenance.py --out FILE.json`

`features_source_tier` (`guide` / `camp_page` / `portal`) ranks how good the source behind each
survey was; `guide` camps average 21 features against 13 for `camp_page`. **No camp currently sits
at `portal`** — every one that looked portal-only turned out to have something better once the
`:raw` bug was understood — so the practical review queue is the thin tail plus the specific defects
agents flagged and refused to guess at:

- **43 surveyed camps with <= 5 features** against a ~15 median. Some are honestly small
  (`va-claytor-lake-aquatics-base` is a day-trip aquatics site with exactly 4 attested activities;
  `mi-great-lakes-sailing-adventure-the-retriever` is a boat), but most are under-served.
- **18 non-day camps still unsurveyed** — mostly whole-council outages (`nhscouting.org` 500s
  site-wide) and the two `website: null` identity cases.
- **`az-r-c-scout-ranch` — record identity defect, do not fix by guessing.** The record's address,
  coordinates, elevation and stored website all point at **Camp Raymond** (7709 S Boy Scout Camp
  Road, Parks AZ) while only `name` says R-C Scout Ranch, and its own `summary` calls R-C the
  "Raymond-Cragin Scout Reservation". Grand Canyon Council's Black Pug appears to list R-C Scout
  Ranch (Payson) and Camp Raymond (Parks) as separate properties ~150 miles apart, but GCC's camp
  nav shows Camp Raymond and no R-C. Three live readings: mislabelled Camp Raymond / R-C is the
  reservation and Raymond a camp in it / two properties and we are missing one. The features are
  correct for the property the record locates; `name`, `website` and `summary` were left untouched.
- **`ok-camp-george-thomas`** — its 19-page Leaders Guide is an image-only scan the reader cannot
  currently mine (its own image selectors fail), so the camp sits at 14 codes from a facility
  inventory. Unmined, not empty.
- **`ar-camp-preston-hunt`** — the pool is attested only by a 2021 guide line saying it would *not*
  be in use that season. Verify before trusting.
- **Camps on councils that no longer exist — guard added 0.37.0.** Six *active* camps were hanging
  off dissolved councils, undetected because `check_ref` only proves a ref resolves and a
  merged-away council still resolves. `validate_data.py` now hard-fails a current camp whose council
  is non-current **when our own event graph names a successor**, since the repair is then
  unambiguous; the three Black Hills Area camps were repointed to Sioux Council (their websites were
  already on `siouxcouncil.org`, which corroborates it). The other three sit on councils recorded as
  `discontinued` with no continuing party — `ca-camp-noyo` (Redwood Empire), `nm-camp-tres-ritos`
  and `tx-c-w-post-memorial-scout-camp` (South Plains) — so nobody knows where they went. Those are
  reported by `tools/maintenance.py` rather than blocking the build, and need research. Note both
  South Plains camps still register under council #694 and `southplainscouncil.org` still resolves,
  so verify the *council* record before assuming the camps are wrong.

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

- **Entity-identity questions — ALL FOUR ADJUDICATED IN 0.36.0, and two of the four claims below
  did not survive verification.** Left here in corrected form because the *error pattern* is the
  reusable lesson.
  - `nc-lumpkin-adventure-base` — **the rename claim was WRONG, and this entry asserted it.** The
    reasoning was that "Lumpkin Adventure Base" appears only in meta keywords while the council
    markets "Harrison High Adventure Base", so one must be the other. The council's own 2017 High
    Adventure Guide disproves it: crews "will be housed between the Harrison High Adventure Outpost
    **and** Lumpkin Adventure Base" — two facilities at once. Lumpkin is a distinct Macon County
    property (Lumpkin family trust 1937, Tessentee Valley purchase 1957, local press covering an
    open house and family day in the 2010s). It is absent from the current guide, which houses crews
    at "The Outpost" a quarter mile from base camp. Absence from a programme guide is not proof of
    closure, so `operating_status` stays `active`; the wrong `website` was cleared and the evidence
    is recorded in the camp's `notes`. **Still needs a human or a council contact.**
  - `ut-hinckley-scout-ranch` — **confirmed.** `saltlakescouts.org` fails DNS outright (not an HTTP
    error), the successor council 404s on `/hinckley`, and its camps listing never names Hinckley.
    Same treatment: website cleared, status untouched, evidence in `notes`, needs a human.
  - MOHAB — **confirmed and sourced**, but *not yet in effect*: the pause starts after the 2026
    season, which is in progress, so the camp is operating today and `operating_status` stays
    `active`. Recorded in `notes` with the instruction to set `not_operating` (property exists,
    programme stops) — never `closed` — after the season. Watch out: the same page still advertises
    2027 dates and fees beside the pause announcement.
  - `nm-gorham-scout-ranch` — **NOT a status change; no edit made.** The page reads "closed for the
    2026 summer camp sessions – But ONLY for 2026. Weekend camping, Wood Badge, NYLT, and BrownSea
    will all be offered". The property operates; only summer resident sessions stop. `operating_status`
    describes the *property*, and this dataset deliberately holds no sessions, so there is nothing
    here to record. Do not re-raise it.
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
  structure per current revision (marked © SA). (b) **Historical requirement revisions — DONE
  (0.40.0).** Requirement-sets 188 → **415**; **131 of 141 badges now carry more than one edition**
  (96 carry three), spanning **1995–2026**, with full verbatim trees, effective windows and
  `supersedes` chains. Source: usscouts.org mirrors each badge at `/mb/mbNNN.asp` **and keeps the
  preceding edition at `/mb/Old/mbNNN-YY.asp`**, with the revision type and effective date declared
  in the page's own editable region — so editions are dated from the source, not inferred. Two
  editions per badge are usually recoverable because usscouts' "current" page trails the newest
  booklet workbooks tracks. Generator: `tools/seed_merit_badge_history.py` (caches fetches; polite
  to a volunteer-run site). Editions are deduped **by text, never by claimed date**.
  - Three chain invariants are now build-gated and each caught a real bug on the first pass: no
    edition supersedes itself, no two editions of one subject share an `effective_from` (ids are
    `<subject>-<year>`, so a year collision silently overwrites), and a subject has at most one open
    edition — and must have one unless the subject itself is retired.
  - **Remaining here:** Geology's archived page 404s (1 badge); 10 badges still have a single
    edition, mostly ones created too recently to have a prior; and **30 scraped editions were dropped
    because they claimed a year another edition already occupied** — same year, different text means
    one label is wrong and the source cannot say which, so those want a human. Going deeper than one
    prior edition needs Wayback (86 distinct-content snapshots exist for a single badge page, so the
    depth is there if anyone wants pre-2000 history).
  - (c) **plant-science deep-structure**: its 5-level "alternatives" nesting was flattened (conf 0.75, flagged in
  notes) — parse properly if it recurs. (d) **Historical discontinued badges — DONE (0.42.0).**
  Badges **142 → 268**: 126 retired badges added from `usscouts.org/mb/history.asp`, back to the
  1910 originals. Generator: `tools/seed_discontinued_badges.py`.
    - **The parse validates itself before writing anything:** the page's non-red rows must equal the
      140 current badges we already hold (after normalising `&`/`and` and hyphens), and a count
      mismatch aborts, because it means the table shape moved. It matched exactly.
    - **Lineage became an event graph:** 61 `superseded` events from the table's own notes
      ("Became Fishing", "Formerly Business"), each emitted once though the table states it from both
      sides, plus 67 plain `discontinued` events for badges that simply ended. Chains walk:
      `clerk → business → american-business`, `first-aid-to-animals → veterinary-science →
      veterinary-medicine`, `mining → rocks-and-minerals → geology`. Badge events 2 → 128.
    - **`eagle_required` is now `boolean | null`** in `merit-badge.schema.json` and
      `published-index.schema.json`, null meaning UNKNOWN. It cannot be sourced for badges retired
      before the modern published Eagle list, and 126 fabricated booleans would be worse than an
      honest gap. `published-current` is untouched: only entities with an open version reach it, and
      all 140 of those carry a real boolean. This is a type widening, so consumers doing strict
      boolean checks on the *index* must handle null; truthiness checks are unaffected.
    - Bonus enrichments from the same table: new `bsa_number` on badge versions (BSA's internal
      number, only assigned from ~1986), and **introduction years backfilled onto 136 current
      badges** whose `valid_from` was null — and for a renamed badge that year is when THAT name took
      effect (American Business: 1967, formerly Business), which is exactly the version-window
      semantic.
    - **Deliberately not modelled:** 17 rows saying "Formerly part of X" (Aerodynamics et al. carved
      out of the 1911 Aviation badge) are kept as prose only — a `split` event needs the predecessor
      closed, and X is usually still live. The 1911 Aviation badge itself IS captured, as
      `aviation-1911`, since the name was reused by a new badge in 1952; its note records the
      four-way split for whoever wants to model it.
    - Source caveat: the page predates Artificial Intelligence, Cybersecurity and Multisport, and
      still lists Citizenship in Society and Computers as current. Ours are right; do not "correct"
      them from this table.
  - (e) **Badge `description` + `tags` — DONE (0.39.0).** All 140 current badges carry an original-prose description (24-38 words,
  median 33) and 1-3 tags from the new 16-facet `merit-badge-tags` vocabulary (218 applications,
  every code in use). Written from the requirement trees, which are local, so no scraping was
  needed. **Two build gates now protect this**, both proven by injection: a description sharing 8+
  consecutive words with its own badge's requirement text is REJECTED (that text is © Scouting
  America and lives under the `text_rights` carve-out; a lifted description would drag copyrighted
  wording into the CC-licensed part of the dataset), and the evergreen guard applies as it does to
  camp summaries. Regenerating the *catalog* still needs the workbooks repo at
  `.workbench/workbooks-main/`; the descriptions are hand-written and need nothing.
- **Finalize schema `$id` base URL. — DONE (0.3.0).** Confirmed
  `https://sethmay.github.io/open-scout-api/schema/v1/` (owner `sethmay`); build serves
  schemas at that path, no re-emit needed.
- **Build step: published projections. — DONE (0.3.0).** `tools/build.py` → `dist/`
  (`v1/meta.json`, per-dataset `index.json` + per-entity `<id>.json` with folded events,
  `v1/current/*.json`, `schema/v1/*`); validates `current/` against
  `published-current.schema.json`. `.github/workflows/pages.yml` gates (validators) +
  builds on push/PR, deploys to Pages on `main`.
- **One-time manual: enable GitHub Pages — DONE.** Verified live 2026-07-26:
  `https://sethmay.github.io/open-scout-api/v1/meta.json` returns 200 and reports the current
  release, all 48 `v*` tags are on the remote, and `main` has no unpushed commits. The API is
  serving.
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
