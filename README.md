# Open Scout API

Open, versioned, machine-readable reference data for **Scouting America (BSA)** — councils,
Council Service Territories, and (planned) camps, merit badges, and requirements — published
as static JSON with JSON Schemas, so anyone can build on it without scraping or running a
server.

> [!IMPORTANT]
> **Unofficial community project.** Not affiliated with, endorsed by, or sponsored by
> Scouting America / Boy Scouts of America. Data is aggregated from public sources with
> per-fact provenance; always confirm against each council's own site. No trademark claim
> or endorsement is implied.

## What makes this different

No official machine-readable BSA structural data exists. The hard part is **history** —
councils merge and rename, regions became territories (2021→2024), badges get retired,
requirements are revised. This dataset models change as first-class data:

- **Identity is permanent and separate from state.** Each entity has a stable slug id that is
  never reused; names, numbers, ownership, and status live in effective-dated **versions**.
- **Change is an explicit event.** Mergers, splits, renames, and reorganizations are records
  linking predecessor/successor entities — not silent overwrites.
- **Every fact carries provenance** — source, method, verification date, and a confidence
  score (unverified inferences are flagged, never fabricated).

See [`PLAN.md`](./PLAN.md) §3 for the full model.

## Live API

Base URL: **`https://sethmay.github.io/open-scout-api/`** (path-versioned under `/v1/`).

| Endpoint | What |
|---|---|
| [`v1/meta.json`](https://sethmay.github.io/open-scout-api/v1/meta.json) | version, counts, license, endpoint list |
| [`v1/current/councils.json`](https://sethmay.github.io/open-scout-api/v1/current/councils.json) | flat list of **current** councils (denormalized) |
| [`v1/current/territories.json`](https://sethmay.github.io/open-scout-api/v1/current/territories.json) | flat list of current Council Service Territories |
| [`v1/councils/index.json`](https://sethmay.github.io/open-scout-api/v1/councils/index.json) | every council, incl. historical (with a `current` flag) |
| `v1/councils/{id}.json` | one council: full version history + its lifecycle events |
| [`v1/territories/index.json`](https://sethmay.github.io/open-scout-api/v1/territories/index.json) | every territory (CSTs, legacy regions, merged NSTs) |
| `v1/territories/{id}.json` | one territory: version history + events |
| [`v1/current/merit-badges.json`](https://sethmay.github.io/open-scout-api/v1/current/merit-badges.json) | flat list of current merit badges (with `eagle_required`) |
| [`v1/merit-badges/index.json`](https://sethmay.github.io/open-scout-api/v1/merit-badges/index.json) | every merit badge, incl. retired/historical |
| `v1/merit-badges/{id}.json` | one merit badge: version history + events |
| [`v1/requirement-sets/index.json`](https://sethmay.github.io/open-scout-api/v1/requirement-sets/index.json) | every requirement set (one per badge revision) |
| `v1/requirement-sets/{id}.json` | one requirement set: the full requirement tree (`<slug>-<year>`) |
| [`v1/camps/index.json`](https://sethmay.github.io/open-scout-api/v1/camps/index.json) | every camp (resident / high-adventure / day / short-term / reservation) |
| `v1/camps/{id}.json` | one camp: version history + events |
| [`v1/camps/aliases.json`](https://sethmay.github.io/open-scout-api/v1/camps/aliases.json) | retired camp id → surviving id (merged duplicate listings) |
| [`v1/current/ranks.json`](https://sethmay.github.io/open-scout-api/v1/current/ranks.json) | flat list of all 21 ranks across the 4 programs (Cub, Scouts BSA, Venturing, Sea Scout) |
| [`v1/ranks/index.json`](https://sethmay.github.io/open-scout-api/v1/ranks/index.json) | every rank |
| `v1/ranks/{id}.json` | one rank: version history + events + its `requirement_sets` ids |
| [`v1/current/awards.json`](https://sethmay.github.io/open-scout-api/v1/current/awards.json) | flat list of current awards & recognitions |
| [`v1/awards/index.json`](https://sethmay.github.io/open-scout-api/v1/awards/index.json) · `v1/awards/{id}.json` | one award: category, audience, square-knot + insignia numbers |
| [`v1/current/oa-lodges.json`](https://sethmay.github.io/open-scout-api/v1/current/oa-lodges.json) | flat list of current OA lodges (by council) |
| [`v1/oa-lodges/index.json`](https://sethmay.github.io/open-scout-api/v1/oa-lodges/index.json) · `v1/oa-lodges/{id}.json` | one OA lodge: chartering council, section, HQ |
| [`v1/current/adventures.json`](https://sethmay.github.io/open-scout-api/v1/current/adventures.json) | flat list of Cub Scout adventures, with the rank(s) offering each, its `category`, and the required `area` it fills |
| [`v1/adventures/index.json`](https://sethmay.github.io/open-scout-api/v1/adventures/index.json) · `v1/adventures/{id}.json` | one adventure: version history + events + its `requirement_sets` ids |
| [`v1/vocab/camp-program-types.json`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-program-types.json) · `camp-types` · `camp-features` · `merit-badge-tags` · `adventure-categories` · `adventure-areas` | controlled vocabularies: every code with a human `label` + `description` |
| [`schema/v1/`](https://sethmay.github.io/open-scout-api/schema/v1/council.schema.json) | JSON Schemas (canonical + the published `current` and `index` contracts) |

```bash
# the current council list
curl -s https://sethmay.github.io/open-scout-api/v1/current/councils.json | jq '.count, .items[0]'

# one council's history + events (e.g. a merged/renamed council)
curl -s https://sethmay.github.io/open-scout-api/v1/councils/mississippi-riverlands.json
```

```js
const { items } = await (await fetch(
  "https://sethmay.github.io/open-scout-api/v1/current/councils.json")).json();
```
**Projection contract.** The `v1/current/*.json` files are the stable, denormalized consumer
surface: every item carries its own `verified_at` / `method` / `confidence`, and
`current/camps.json` inlines its council (`council_name`, `council_website`, `council_number`)
plus a resolved, durable `url` (the camp's own page when stable, else the council site;
per-season registration deep-links are dropped) so consumers need no cross-file joins. For
imported camps `verified_at` is camp-finder's own source-confirmation date (so a "stale after
12 months" check actually fires) and `imported_at` is our ingest date; `confidence` runs 0.9
(curated / national bases) / 0.8 (higher-confidence import) / 0.6 (default import), and below 1.0 for
LLM-extracted facts in other datasets.
Each camp's `geo_precision` marks its coordinate `exact` (camp-specific point), `approximate`
(city or state-centroid backfill — soft-plot or bucket these), or `null` (could not be placed).
Fields are **additive-only under `v1`** — new optional fields may appear, but existing ones are
never renamed or removed — so pinning to a field set is safe. **Every published surface is now
schema-pinned and build-gated — all 2,172 files, with nothing left unpinned:** the denormalized
`v1/current/*.json` views against
[`published-current.schema.json`](https://sethmay.github.io/open-scout-api/schema/v1/published-current.schema.json),
the lighter `v1/{dataset}/index.json` listings (every entity incl. historical, with a `current`
flag — except requirement-sets, which are effective-dated documents and use `effective_to: null`
for "in force") against
[`published-index.schema.json`](https://sethmay.github.io/open-scout-api/schema/v1/published-index.schema.json),
the **2,152 per-entity `v1/{dataset}/{id}.json` documents** against
[`published-entity.schema.json`](https://sethmay.github.io/open-scout-api/schema/v1/published-entity.schema.json),
the discovery document against
[`published-meta.schema.json`](https://sethmay.github.io/open-scout-api/schema/v1/published-meta.schema.json),
and `v1/{dataset}/aliases.json` against
[`published-aliases.schema.json`](https://sethmay.github.io/open-scout-api/schema/v1/published-aliases.schema.json).
Every file names its own contract in `$schema` — except the alias map, which is deliberately a bare
`{retired-id: surviving-id}` lookup with no room for one — the item shape is selected by the
envelope `kind`, and `build.py` fails the build if any projection drifts. Generate consumer types
from those schemas rather than hand-mirroring. The per-entity contract pins the envelope and the
projection (`versions` non-empty, lifecycle `events` folded in under that key, `requirement_sets`
listing every edition of a subject); the interior of each `version` is validated against its
canonical schema by `validate_data.py` before the build runs.
A camp's `reservation.id` is a stable opaque grouping key (a bare slug, deliberately not a
`kind:slug` entity ref): group by it, don't parse it.
Each camp also carries **`features`** — what it actually offers, as sorted codes from the open
[`camp-features`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-features.json) vocabulary
(128 terms) — plus `features_signature` (the subset the camp presents as a headline draw, for
ranking and badges, never for filtering) and `features_verified_at`. **Read the date with the
array, always:** `null` + empty means *never surveyed, nothing known*, which is a different fact
from a date + empty (*surveyed, its page described no offerings*); a date + non-empty is a real
survey, and `null` + non-empty means the codes came from a bulk import nobody verified. A date
means a survey happened, **not** that the list is exhaustive — camp pages rarely are. Codes form a
shallow hierarchy through each term's `broader`, so a filter on a coarse code must expand it to its
descendants: a camp offering only `kayaking` should match a search for `aquatics`. The prose `note`
attached to some features is deliberately **not** in this projection — it lives in the per-camp
`v1/camps/{id}.json` document, keeping the flat list filterable rather than 40% larger. Each survey also carries **`features_source_tier`** (`guide` / `camp_page` / `portal`), a completeness qualifier in the same spirit as `geo_precision`: `guide` means a camp-specific document was read and averages 21 features per camp, `camp_page` a descriptive page (13), and `portal` that only a registration blurb existed. Rank and trust completeness by it — a `portal` list is a floor, not a description.


> **Pre-1.0: the host is not final.** Field shapes are already stable and build-gated — every
> published file names its contract in `$schema` and the build fails on drift — but the **base URL
> itself** (`sethmay.github.io/open-scout-api`, which is also the schema `$id` prefix) is still
> provisional while a permanent home is settled. Cutting `1.0` is what freezes it. Until then,
> prefer resolving endpoints from [`v1/meta.json`](https://sethmay.github.io/open-scout-api/v1/meta.json)
> (`base_url`, `schemas`, `endpoints`) over hardcoding the host, and pin data files by git tag via
> jsDelivr — tags are immutable regardless of where the repo ends up.

**Pinning & releases.** Every version is a git tag (`vMAJOR.MINOR.PATCH`) at that release's
CHANGELOG sha. Pin canonical files immutably via jsDelivr —
`https://cdn.jsdelivr.net/gh/sethmay/open-scout-api@v0.11.0/data/councils/cascade-pacific.json`
(`@main` tracks latest; the denormalized `v1/` projections are served from GitHub Pages). Pushing
a `v*` tag runs [`release.yml`](./.github/workflows/release.yml), which publishes a GitHub Release
with the built JSON tree (`open-scout-api-<tag>-json.tar.gz`) and a queryable **SQLite** artifact
(`open-scout-api-<tag>.sqlite` — typed tables mirroring the `current` projections, plus the full
canonical JSON per row for `json_extract`). Camp program features are unrolled into a
`camp_features` junction table (`camp_id`, `code`, `signature`, `note`, `verified_at` — the prose
`note` *is* included here, unlike the flat JSON projection) alongside `feature_vocab`
(`code`, `label`, `category`, `broader`), so a coarse query resolves the hierarchy in one recursive
CTE:

```sql
WITH RECURSIVE sub(code) AS (
  SELECT 'aquatics'
  UNION SELECT v.code FROM feature_vocab v JOIN sub ON v.broader = sub.code)
SELECT COUNT(DISTINCT camp_id) FROM camp_features WHERE code IN (SELECT code FROM sub);  -- 254
```

Tagged releases can be archived to Zenodo for a citable
DOI (enable the GitHub↔Zenodo integration once; metadata lives in `.zenodo.json`).

## Datasets & status

| Dataset | Status |
|---|---|
| **Councils** | ✅ 419 entities — **229 current** (assigned to the 14 Council Service Territories) + **190 historical** (merged/renamed/defunct) with lifecycle events. Current councils carry founding dates, prior-name (rename) history, and merger/absorption events extracted as facts from each council's Wikipedia article (`llm_extraction`, conf 0.7–0.8) — 141 founding years, 57 rename chains, 112 merger/absorption events. |
| **Territories** | ✅ 20 entities — 14 current CSTs (each carrying 2021 National Service Territory → 2024 Council Service Territory history), 4 legacy regions, 2 merged NSTs |
| **Merit badges** | ✅ **268 entities — 140 current (17 Eagle-required incl. alternatives) plus 128 historical**, going back to the 1910 originals (Signaller, Ambulance, Angling). Every badge carries its introduction year, its BSA recordkeeping number where one was ever assigned, and its retirement year, and **61 `superseded` events chain the renames**, so lineages are walkable: `clerk → business → american-business`, `mining → rocks-and-minerals → geology`, `seaman → seamanship → small-boat-sailing`, `ambulance → first-aid`. ⚠ `eagle_required` is **`null` for historical badges — unknown, not false**: it cannot be sourced for badges retired before the modern published Eagle list. Every badge in `current/merit-badges.json` still carries a real boolean. Every current badge carries an **original-prose `description`** (24-38 words, written from its own requirements) and 1-3 **`tags`** from the 16-facet [`merit-badge-tags`](https://sethmay.github.io/open-scout-api/v1/vocab/merit-badge-tags.json) vocabulary, so a catalog can be browsed and filtered by subject. A build gate rejects any description that shares 8+ consecutive words with its badge's requirement text — that text is © Scouting America, and descriptions are deliberately ours. |
| **Requirement sets** | ✅ 546 documents (368 merit-badge + 131 Cub adventure + 47 rank across programs/editions) — full requirement tree (numbering, nesting, choose-N/option groups, and `ref`s to the entity a node stands for) + effective date/`supersedes` chains + source links per revision. ⚠ Requirement **text is © Scouting America** (see below), not under this dataset's license. **Historical editions ship too:** 131 of 141 badges carry more than one edition (96 carry three), spanning 1995-2026 with effective windows and `supersedes` chains, so you can answer which requirements applied when a Scout started. `v1/current/requirement-sets.json` lists only the in-force edition per subject; `v1/requirement-sets/index.json` lists every edition. |
| **Camps** | ✅ 448 entities — seeded from [camp-finder](https://github.com/sethmay/camp-finder), classified by `camp_type` (349 resident, 64 day, 35 high-adventure) and `operator` (444 council + 4 national bases: Philmont, Florida Sea Base, Northern Tier, Summit/James C. Justice). Duplicate and program/session-variant listings are merged into their base camp and scraped-artifact names corrected to the real property name; retired ids (50) resolve to the surviving camp via [`v1/camps/aliases.json`](https://sethmay.github.io/open-scout-api/v1/camps/aliases.json). 41 co-located distinct camps carry a `reservation` grouping (18 reservations, 17 named — e.g. Goshen Scout Reservation) so consumers render one pin per property. Every camp with coordinates also carries `elevation_ft` (ground elevation from a 90 m DEM) and July climate normals `july_high_f` / `july_low_f` (WorldClim 1 km, 1970-2000), all inheriting `geo_precision`. Most carry an evergreen `summary` (371 of 448; durable prose, no dates/fees/sessions). Coordinates carry `geo_precision` (336 `exact`, 111 `approximate`, 1 unplaceable) — a point shared by several camps is a reservation centroid, so it is `approximate`, not `exact` — and a build gate rejects any point outside its state box. Covers every camp the camp-finder site lists; sessions/fees stay at the council site. **Program `features`** — what each camp offers, as codes from the open 128-term [`camp-features`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-features.json) vocabulary — are surveyed from each camp's own page: **366 camps carry 6,373 feature entries (95% of the 384 non-day-camps)**, each with a `features_verified_at` date, and 147 marked `signature` where the camp presents them as a headline draw. Day camps are out of scope (they often run at rented sites). An empty array never means "offers nothing" — read it with the date. |
| **Ranks** | ✅ 21 across 4 programs — 7 Scouts BSA (Scout→Eagle) + 6 Cub Scout (Lion→Arrow of Light), 4 Venturing (Venturing→Summit), 4 Sea Scout (Apprentice→Quartermaster). Requirement content in 47 rank `requirement-set` docs: Scouts BSA current (2024, No. 33216) + 26 historical editions (2016-2023) via usscouts.org; Cub/Venturing/Sea Scout current from official scouting.org pages + 2026 Sea Scout PDFs. Full verbatim tree © Scouting America. The six **Cub** rank trees are pure structure — the rule they state is "six required Adventures and any two elective" — so each is two groups of `ref`s into the adventures dataset rather than inlined text. |
| **Awards** | ✅ 52 earned awards & recognitions (knots, scouting honors, training awards, religious-emblem knot) from the Guide to Awards and Insignia (No. 33066) — facts only (category, audience, square-knot/insignia numbers, wear); catalog numbers source-verified (`llm_extraction`, conf 0.85). Excludes uniform insignia and per-faith emblems. |
| **OA lodges** | ✅ 238 entities — Order of the Arrow lodges from the official OA lodge locator feed (oa-bsa.org), each linked to its chartering council, with OA section/region, HQ + coordinates, and website. Officer/contact PII excluded. |
| **Cub adventures** | ✅ **139 entities (36 required, 95 elective, 8 special elective) with 611 requirements in 131 requirement-sets** — the unit of Cub advancement, and the Cub-side analogue of merit badges: a rank is earned by completing six required adventures plus any two electives. Ids are Scouting America's own canonical slugs (`pick-my-path-lion`, `bobcat-aol`), and each adventure carries the rank(s) offering it — only `slingshot` and `bb-guns` span more than one. Requirement-set ids are prefixed `adventure-` because five adventures share a name with a merit badge. **Every required adventure carries the `area` it fills** — one of the six in [`adventure-areas`](https://sethmay.github.io/open-scout-api/v1/vocab/adventure-areas.json) (Character & Leadership, Personal Fitness, Personal Safety, Family & Reverence, Citizenship, Outdoors) — and a build gate proves each rank fills all six exactly once, so "which of my six required slots are still open" is a group-by, not a list diff. Electives carry `area: null`. ⚠ The 8 shooting-sports adventures (Archery ×6, BB Guns, Slingshot) have **no published requirements** — they are completed "only at approved events with qualified instructors" and have no page of their own — so they exist as entities with a null `url` and no requirement-set. |

Roadmap and the full dataset catalog: [`TODO.md`](./TODO.md).

## Repository layout

```
data/                 authoritative source: canonical JSON, one file per entity + _events.json per dataset
  councils/ territories/ merit-badges/ requirement-sets/ camps/ ranks/ awards/ oa-lodges/ vocab/
schema/v1/            JSON Schemas (draft 2020-12); *.schema.json canonical + published-current/-index
tools/                live pipeline: stamp_schema.py, validate_data.py, validate_examples.py,
                      build.py (data/ -> dist/), build_sqlite.py, us_geo.py
                      enrichment (run manually): geocode_addresses.py (coords from street addresses), elevation.py (elevation_ft), july_temp.py (July normals; needs rasterio)
                      maintenance: check_urls.py (audit camp website health), restamp_identity.py (move the API base URL / repo slug), find_camp_pages.py (find a camp page on the council site), maintenance.py (re-verification queue + standing health check)
                      historical seed (one-time camp-finder import; see file headers): import_camps.py, geocode_camps.py
dist/                 generated static API (git-ignored; built + deployed by CI)
PLAN.md TODO.md CHANGELOG.md LESSONS.md NOTICE.md
```

The repo **is** the database: writes happen via pull requests, a CI validation gate blocks bad
merges, and GitHub Pages serves the built API. There is no runtime backend.

## Local development

Requires Python 3.11+.

```bash
pip install "jsonschema[format]"
python tools/validate_examples.py   # schemas + example fixtures (positive & negative)
python tools/validate_data.py       # data/: schema + referential + version-window invariants
python tools/build.py               # compile data/ -> dist/  (open dist/index.html)
python tools/build_sqlite.py         # compile data/ -> dist/v1/open-scout-api.sqlite (run after build.py)
python tools/stamp_schema.py         # (re)stamp data/ $schema refs after regenerating; validate_data enforces them
```

The **enrichment** and maintenance tools (`geocode_addresses.py`, `elevation.py`, `july_temp.py`, `check_urls.py`, `find_camp_pages.py`, `maintenance.py`) are run manually,
never by CI, and carry the only extra requirements: `july_temp.py` needs `rasterio`
(`pip install rasterio`) plus the WorldClim rasters (~8 GB, git-ignored `tools/worldclim/`; fetch
URLs are in the tool's docstring). Their derived caches are committed, so validating or building the
API needs neither the dependency nor the rasters.

CI ([`.github/workflows/pages.yml`](./.github/workflows/pages.yml)) runs the validators as a
required gate on every push/PR and deploys `dist/` to GitHub Pages on `main`; pushing a `v*` tag
runs [`release.yml`](./.github/workflows/release.yml) to publish a GitHub Release with assets.

## Contributing

`data/` is the authoritative source — edit the canonical JSON directly (there is no upstream to
re-import; the camp-finder seed pipeline is historical, see below). To add or fix an entity: edit
`data/<dataset>/<id>.json`, then run `stamp_schema.py` → `validate_data.py` → `validate_examples.py`
→ `build.py`, and open a PR (the same validators gate CI). A camp rename, or a duplicate/variant
folded into another camp, uses `merged_from` — the retired id then resolves via `v1/camps/aliases.json`.
Every fact needs a checkable source in its `provenance` block (no bare high confidence without a
citation). New entities follow the id/versioning/event conventions in [`PLAN.md`](./PLAN.md) §3.

`tools/import_camps.py` and `tools/geocode_camps.py` are the one-time camp-finder **seed** tools;
camp-finder now consumes this API and its source data is retired, so they are not part of the live
pipeline (kept for provenance).

## License & attribution

- **Data** (`data/` and the published projections): **[CC BY-NC-SA 4.0](./LICENSE)** — reuse
  with attribution, non-commercial, share-alike.
- **Merit badge requirement text** in `requirement-set` documents is **© Scouting America**
  (marked `includes_official_text: true` + `text_rights`), reproduced with attribution for
  non-commercial use and **not** under this dataset's license — don't relicense it. Only the
  requirement structure/numbering/metadata is the project's CC BY-NC-SA contribution.
- **Code** (`tools/`): MIT.

Seed sources and how to attribute are in [`NOTICE.md`](./NOTICE.md). In brief: territory
assignments come from official Scouting America Council Service Territory maps (facts extracted;
the proprietary map images are **not** redistributed); council websites/names are cross-checked
against the unofficial [camp-finder](https://github.com/sethmay/camp-finder) dataset.
