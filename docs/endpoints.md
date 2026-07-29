# Endpoints

Every published URL, the contract the `current/` projections promise, how to pin a version, and the
SQLite artifact. [← README](../README.md) · siblings: [datasets](./datasets.md) ·
[data model](./model.md)

Base URL: **`https://sethmay.github.io/open-scout-api/`**, path-versioned under `/v1/`.

> [!IMPORTANT]
> **Pre-1.0: the host is not final.** Field shapes are already stable and build-gated: every
> published file names its contract in `$schema` and the build fails on drift. But the **base URL
> itself** (`sethmay.github.io/open-scout-api`, which is also the schema `$id` prefix) is still
> provisional while a permanent home is settled. Cutting `1.0` is what freezes it.
>
> So: resolve endpoints from
> [`v1/meta.json`](https://sethmay.github.io/open-scout-api/v1/meta.json) (`base_url`, `schemas`,
> `endpoints`) instead of hardcoding the host, and pin data files by git tag via jsDelivr. Tags are
> immutable regardless of where the repo ends up.

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

## Endpoint reference

46 endpoints, all enumerated in `meta.json`'s `endpoints` array.

### Discovery

| Endpoint | Returns |
|---|---|
| [`v1/meta.json`](https://sethmay.github.io/open-scout-api/v1/meta.json) | version, per-dataset counts, license, endpoint list |

`meta.json` is the only URL worth hardcoding. It carries `base_url`, `schemas` (the schema
directory prefix), `endpoints` (every path below), `vocab` (the vocabulary paths), `license`, and
`text_rights`, plus `datasets` (a `{total, current}` pair per dataset), so a consumer can sanity-check
a fetch against the count the build published rather than trusting its own pagination.

### `current/`: denormalized projections

The flat, joined, filterable surface. One file per dataset, current entities only.

| Endpoint | Returns |
|---|---|
| [`v1/current/councils.json`](https://sethmay.github.io/open-scout-api/v1/current/councils.json) | current councils |
| [`v1/current/territories.json`](https://sethmay.github.io/open-scout-api/v1/current/territories.json) | current Council Service Territories |
| [`v1/current/merit-badges.json`](https://sethmay.github.io/open-scout-api/v1/current/merit-badges.json) | current merit badges, with `eagle_required` |
| [`v1/current/requirement-sets.json`](https://sethmay.github.io/open-scout-api/v1/current/requirement-sets.json) | requirement sets in force (`effective_to: null`) |
| [`v1/current/camps.json`](https://sethmay.github.io/open-scout-api/v1/current/camps.json) | camps with council, coordinates, and features inlined |
| [`v1/current/ranks.json`](https://sethmay.github.io/open-scout-api/v1/current/ranks.json) | all ranks across the four programs |
| [`v1/current/awards.json`](https://sethmay.github.io/open-scout-api/v1/current/awards.json) | current awards & recognitions |
| [`v1/current/oa-lodges.json`](https://sethmay.github.io/open-scout-api/v1/current/oa-lodges.json) | current OA lodges, by chartering council |
| [`v1/current/adventures.json`](https://sethmay.github.io/open-scout-api/v1/current/adventures.json) | current Cub Scout adventures |
| [`v1/current/positions.json`](https://sethmay.github.io/open-scout-api/v1/current/positions.json) | youth leadership positions of responsibility |
| [`v1/current/training.json`](https://sethmay.github.io/open-scout-api/v1/current/training.json) | adult training courses by code |

Each `current/adventures.json` item names the rank(s) offering it, its `category`, and the required
`area` it fills. Each `current/training.json` item carries the course code (`Y01`, `S11`, `WS10`),
its delivery mode, and its renewal interval. See [datasets](./datasets.md) for what each dataset
actually contains.

Two datasets have no `current/` projection, because "current" is not a meaningful filter on them:
**merit-badge-rankings** (each document *is* a year) and **training-requirements** (each document is
a `(position, unit type)` pair, not an entity with a lifecycle).

### Per-dataset `index.json` + `{id}.json`

`index.json` lists every entity including historical ones, each with a `current` flag; `{id}.json`
is the full entity document: version history plus its lifecycle events. See
[data model](./model.md) for what a version and an event are.

| Endpoint | Returns |
|---|---|
| [`v1/councils/index.json`](https://sethmay.github.io/open-scout-api/v1/councils/index.json) · `v1/councils/{id}.json` | councils incl. merged/renamed/defunct |
| [`v1/territories/index.json`](https://sethmay.github.io/open-scout-api/v1/territories/index.json) · `v1/territories/{id}.json` | CSTs, legacy regions, merged NSTs |
| [`v1/merit-badges/index.json`](https://sethmay.github.io/open-scout-api/v1/merit-badges/index.json) · `v1/merit-badges/{id}.json` | merit badges incl. retired |
| [`v1/requirement-sets/index.json`](https://sethmay.github.io/open-scout-api/v1/requirement-sets/index.json) · `v1/requirement-sets/{id}.json` | one requirement tree per subject revision |
| [`v1/camps/index.json`](https://sethmay.github.io/open-scout-api/v1/camps/index.json) · `v1/camps/{id}.json` | camps: resident, day, high-adventure, short-term |
| [`v1/ranks/index.json`](https://sethmay.github.io/open-scout-api/v1/ranks/index.json) · `v1/ranks/{id}.json` | ranks, with their `requirement_sets` ids |
| [`v1/awards/index.json`](https://sethmay.github.io/open-scout-api/v1/awards/index.json) · `v1/awards/{id}.json` | awards: category, audience, insignia numbers |
| [`v1/oa-lodges/index.json`](https://sethmay.github.io/open-scout-api/v1/oa-lodges/index.json) · `v1/oa-lodges/{id}.json` | OA lodges: chartering council, section, HQ |
| [`v1/adventures/index.json`](https://sethmay.github.io/open-scout-api/v1/adventures/index.json) · `v1/adventures/{id}.json` | Cub adventures, with their `requirement_sets` ids |
| [`v1/positions/index.json`](https://sethmay.github.io/open-scout-api/v1/positions/index.json) · `v1/positions/{id}.json` | positions of responsibility |
| [`v1/training/index.json`](https://sethmay.github.io/open-scout-api/v1/training/index.json) · `v1/training/{id}.json` | adult training courses |
| [`v1/training-requirements/index.json`](https://sethmay.github.io/open-scout-api/v1/training-requirements/index.json) · `v1/training-requirements/{id}.json` | what a position must complete to be Position Trained |
| [`v1/merit-badge-rankings/index.json`](https://sethmay.github.io/open-scout-api/v1/merit-badge-rankings/index.json) · `v1/merit-badge-rankings/{year}.json` | merit badge popularity per year |

Three of these break the pattern:

- **`requirement-sets/index.json`** has no `current` flag. Requirement sets are effective-dated
  documents, so "in force" is `effective_to: null`.
- **`merit-badge-rankings`** is keyed by `{year}`, not `{id}`, and reports **ranks, not counts**.
  Scouting America publishes each badge's position and no absolute number anywhere.
- **`training-requirements`** is keyed by **(position, unit type)**, because code `CC` needs a
  different course in a pack, a troop, a team, a crew, and a ship.

### Alias maps

| Endpoint | Returns |
|---|---|
| [`v1/camps/aliases.json`](https://sethmay.github.io/open-scout-api/v1/camps/aliases.json) | retired camp id → surviving id |

Camps is the only dataset with an alias map today, because it is the only one seeded from a source
that contained duplicate and program-variant listings for one property. A retired id resolves to the
camp it was folded into. The file is deliberately a bare `{retired-id: surviving-id}` object with no
envelope. See [schema pinning](#schema-pinning-and-the-build-gate) for what that costs it.

### Vocabularies

Controlled vocabularies: every code with a human `label` and `description`, under an envelope
carrying `applies_to` and an `open` flag.

| Endpoint | Vocabulary |
|---|---|
| [`v1/vocab/camp-types.json`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-types.json) | `camp_type` values |
| [`v1/vocab/camp-program-types.json`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-program-types.json) | `program_types` values |
| [`v1/vocab/camp-features.json`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-features.json) | 128 camp feature codes, hierarchical via `broader` |
| [`v1/vocab/merit-badge-tags.json`](https://sethmay.github.io/open-scout-api/v1/vocab/merit-badge-tags.json) | merit badge subject tags |
| [`v1/vocab/adventure-categories.json`](https://sethmay.github.io/open-scout-api/v1/vocab/adventure-categories.json) | Cub adventure categories |
| [`v1/vocab/adventure-areas.json`](https://sethmay.github.io/open-scout-api/v1/vocab/adventure-areas.json) | the six required Cub adventure areas |
| [`v1/vocab/position-unit-types.json`](https://sethmay.github.io/open-scout-api/v1/vocab/position-unit-types.json) | unit types a position or training requirement is scoped to |

### Schemas

| Endpoint | Returns |
|---|---|
| [`schema/v1/`](https://sethmay.github.io/open-scout-api/schema/v1/council.schema.json) | 21 JSON Schemas (draft 2020-12) |

Sixteen canonical schemas (one per entity kind, plus `common`, `event`, and `vocab`) and five
`published-*` contracts that pin the published surface. Resolve the directory from `meta.json`'s
`schemas` key rather than assembling the URL yourself.

## The projection contract

### `current/*.json` is the consumer surface

The `v1/current/*.json` files are the stable, denormalized consumer surface. They exist so that the
common questions (*which councils exist*, *which camps have a lake*, *which badges are
Eagle-required*) are one fetch and a `filter`, with no cross-file joins.

Envelope on every collection: `$schema`, `version`, `generated_at`, `kind`, `count`, `items`. The
item shape is selected by `kind`, not by the URL.

### Provenance travels with every item

Every item in every `current/*.json` carries its own `verified_at`, `method`, and `confidence`,
verified across all 11 files with no item missing any of the three. Provenance is per-fact, not
per-file: two camps in the same response can disagree about how much they should be trusted.

For camps specifically:

- `verified_at` is the **source's** own confirmation date. For imported camps that is camp-finder's
  confirmation date, not our ingest date, so a "stale after 12 months" check actually fires.
  `imported_at` is our ingest date, kept separate for exactly that reason.
- `method` is `curated` or `imported`; `confidence` runs `0.9` (a handful of curated entries and the
  national bases) / `0.8` (higher-confidence import) / `0.6` (default import). Other datasets sit
  below `1.0` for LLM-extracted facts.

> [!NOTE]
> `method` and `confidence` are independent axes, not two names for one thing: as of v0.54.0 the
> `curated` camps span all three confidence tiers, and three `imported` camps sit at `0.9`. Read
> both.

### `current/camps.json` inlines its council

Each camp inlines `council_name`, `council_website`, and `council_number` alongside the `council`
ref, plus a resolved, durable `url`: the camp's own page where that is stable, otherwise the council
site. Per-season registration deep-links are deliberately dropped because they 404 by August.

### Coordinates: `geo_precision`

`geo_precision` qualifies the `lat`/`lon` pair:

- `exact`: a camp-specific point.
- `approximate`: a city or state-centroid backfill. Soft-plot or bucket these.
- `null`: could not be placed.

> [!WARNING]
> `map.pin(camp.lat, camp.lon)` without checking `geo_precision` plots state centroids as if they
> were real camps. As of v0.54.0 that is 111 of 448 camps rendered as confident lies.

### Camp features: read the date with the array

Each camp carries **`features`**: what it actually offers, as sorted codes from the open
[`camp-features`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-features.json) vocabulary
(128 terms). It also carries `features_signature` and `features_verified_at`.

> [!WARNING]
> **Read the date with the array, always.** The pair is a tri-state, and three of the four
> combinations mean different things:
>
> | `features` | `features_verified_at` | Means |
> |---|---|---|
> | empty | `null` | never surveyed, so nothing is known |
> | empty | a date | surveyed; its page described no offerings |
> | non-empty | a date | a real survey |
> | non-empty | `null` | codes came from a bulk import nobody verified |
>
> Collapsing the first two (treating "we never looked" as "it has none") is the failure this field
> exists to prevent.

A date means a survey happened; it does **not** mean the list is exhaustive. Camp pages rarely are.

Codes form a shallow hierarchy through each term's `broader`, so a filter on a coarse code must
expand it to its descendants first. `aquatics` expands to 22 codes; matching the literal code alone
finds 61 camps, while the expanded set finds 321. A camp offering only `kayaking` is in the second
number and not the first.

> [!NOTE]
> `features_signature` is the subset the camp presents as a headline draw. Use it for ranking and
> badges, **never for filtering**: a camp that has a lake but does not lead with it is still a camp
> with a lake.

The prose `note` attached to some features is deliberately **not** in this projection: it lives in
the per-camp `v1/camps/{id}.json` document, keeping the flat list filterable rather than 40% larger.
It is also in the SQLite artifact's [`camp_features`](#tables) table.

### `features_source_tier`: how complete the survey was

Each survey also carries `features_source_tier`, a completeness qualifier in the same spirit as
`geo_precision`:

| Tier | Source read | Camps (v0.54.0) | Mean features |
|---|---|---|---|
| `guide` | a camp-specific document: leader's or program guide, schedule, labelled map | 129 | 25.1 |
| `camp_page` | a descriptive page | 237 | 13.2 |
| `portal` | only a registration blurb existed | 0 | n/a |
| `null` | never surveyed | 82 | 0 |

Rank and trust completeness by it: a `portal` list is a floor, not a description. `portal` is defined
by the schema and reserved; no camp carries it as of v0.54.0.

### `reservation.id` is an opaque grouping key

41 co-located distinct camps carry a `reservation` object so consumers can render one pin per
property. Its `id` is a stable opaque grouping key: a bare slug, deliberately *not* a `kind:slug`
entity ref, because a reservation is not an entity in this dataset. Group by it; do not parse it.

### Additive-only under `v1`

Fields are **additive-only under `v1`**: new optional fields may appear, but existing ones are never
renamed or removed. Pinning your code to a field set is safe; a removal would require `v2`.

### Schema pinning and the build gate

Every published surface is schema-pinned and build-gated, covering **2,473 JSON files under `v1/`,
nothing left unpinned**:

| Surface | Files | Contract |
|---|---|---|
| `v1/current/*.json` | 11 | [`published-current`](https://sethmay.github.io/open-scout-api/schema/v1/published-current.schema.json) |
| `v1/{dataset}/index.json` | 13 | [`published-index`](https://sethmay.github.io/open-scout-api/schema/v1/published-index.schema.json) |
| `v1/{dataset}/{id}.json` | 2,440 | [`published-entity`](https://sethmay.github.io/open-scout-api/schema/v1/published-entity.schema.json) |
| `v1/vocab/*.json` | 7 | [`vocab`](https://sethmay.github.io/open-scout-api/schema/v1/vocab.schema.json) |
| `v1/meta.json` | 1 | [`published-meta`](https://sethmay.github.io/open-scout-api/schema/v1/published-meta.schema.json) |
| `v1/camps/aliases.json` | 1 | [`published-aliases`](https://sethmay.github.io/open-scout-api/schema/v1/published-aliases.schema.json) |

Every file names its own contract in `$schema`, except the alias map, which is a bare
`{retired-id: surviving-id}` lookup with no room for one, and so is the single published file whose
contract you have to know rather than read. `build.py` fails the build if any projection drifts.

The per-entity contract pins both the envelope and the projection: `versions` non-empty, lifecycle
`events` folded in under that key, `requirement_sets` listing every edition of a subject. The
*interior* of each `version` is validated against its canonical schema by `validate_data.py` before
the build runs. Two gates, on two different things.

### Generate your types

Generate consumer types from the published schemas rather than hand-mirroring them.
`python tools/gen_types.py` emits `cookbook/ts/src/generated/v1.ts` and
`cookbook/csharp/Generated/V1.cs` from the five `published-*` contracts, and `--check` fails CI on
drift, so the checked-in output cannot fall behind the contracts.

## Pinning & releases

Every version is a git tag (`vMAJOR.MINOR.PATCH`) at that release's CHANGELOG sha, so `git bisect`
can identify which build a regression first appeared in.

Pin **canonical** files immutably via jsDelivr:

```
https://cdn.jsdelivr.net/gh/sethmay/open-scout-api@v0.53.0/data/councils/cascade-pacific.json
```

`@main` tracks latest. The denormalized `v1/` projections are not in the repo. They are built by CI
and served from GitHub Pages, so a pin gets you `data/`, not `dist/`. For a pinned copy of the
built tree, use a release asset.

Pushing a `v*` tag runs [`release.yml`](../.github/workflows/release.yml), which validates, builds,
and publishes a GitHub Release with two assets:

| Asset | Contents |
|---|---|
| `open-scout-api-<tag>-json.tar.gz` | the whole built JSON tree, minus the SQLite file |
| `open-scout-api-<tag>.sqlite` | the queryable SQLite artifact |

Release notes are extracted from that version's `CHANGELOG.md` section, so the release text and the
changelog cannot drift apart. Tagged releases can be archived to Zenodo for a citable DOI: enable
the GitHub↔Zenodo integration once; metadata lives in `.zenodo.json`.

## The SQLite artifact

`open-scout-api-<tag>.sqlite` (~7.8 MB), built by `tools/build_sqlite.py` from `data/`, ships as an
asset on every [tagged release](https://github.com/sethmay/open-scout-api/releases). That is the
immutable copy, and the one to pin.

> [!NOTE]
> It is also served alongside the API at `v1/open-scout-api.sqlite` **from 0.55.0 onward**. Earlier
> deploys did not include it: the Pages job built only the JSON tree, so that path 404'd while this
> document claimed otherwise. If you need a copy that is guaranteed present for a specific version,
> take the release asset rather than the Pages path.

The entity tables go beyond the `current/` projections: they hold **every** entity, historical
included, with a `current` flag. The same query answers "today" or "ever" by adding or dropping
`WHERE current = 1`. Each entity row also carries the full canonical JSON in a `data` column for
`json_extract`, so anything the typed columns omit is still reachable without a second fetch.

### Tables

22 tables, 25 indexes, no views. Row counts are v0.54.0.

| Table | Rows | Contents |
|---|---|---|
| `meta` | 24 | build key/value pairs: version, `generated_at`, per-dataset counts |
| `councils` | 420 | id, name, `current`, `bsa_number`, HQ city/state, `data` |
| `territories` | 20 | id, name, `current`, number, `division_type`, `data` |
| `merit_badges` | 268 | id, name, `current`, `eagle_required`, `data` |
| `requirement_sets` | 667 | subject, `effective_from`/`effective_to`, `supersedes`, `includes_official_text` |
| `merit_badge_rankings` | 692 | year, `earned_rank`, badge id, whether the year is complete |
| `camps` | 448 | id, name, `camp_type`, `operator`, council, state, `data` |
| `camp_features` | 6,379 | camp × feature: `code`, `signature`, `note`, `verified_at` |
| `feature_vocab` | 128 | `code`, `label`, `category`, `broader`, `description` |
| `ranks` | 21 | id, name, program, `rank_order`, `data` |
| `rank_advancement` | 16 | per-rank advancement rule: tenure, badge counts |
| `rank_positions` | 104 | rank × position × unit type |
| `positions` | 29 | youth leadership positions, `audience`, `data` |
| `adventures` | 177 | id, name, `current`, program, `category`, `area`, `data` |
| `adventure_ranks` | 196 | adventure × rank, with the `category`/`area` it fills there |
| `awards` | 52 | id, name, category, audience, `square_knot_no`, `data` |
| `oa_lodges` | 238 | lodge, chartering council, section, region, HQ, coordinates |
| `training` | 28 | course id, name, `code`, `delivery`, `renew_months`, `data` |
| `training_requirements` | 67 | one row per (position, unit type) |
| `training_requirement_courses` | 194 | requirement × course, with `alternative` grouping |
| `training_requirement_codes` | 68 | requirement × position code |
| `events` | 288 | every lifecycle event, all datasets: `dataset`, `id`, `type`, `date`, `data` |

The junction tables are the point. `camp_features` and `adventure_ranks` unroll many-to-many
relationships that the flat JSON has to either nest or drop, and `camp_features` **includes the
prose `note`** that `current/camps.json` deliberately omits.

### The feature hierarchy in one recursive CTE

`feature_vocab.broader` makes the code hierarchy a join, so a coarse query resolves it in one
recursive CTE instead of expanding the tree in application code:

```sql
WITH RECURSIVE sub(code) AS (
  SELECT 'aquatics'
  UNION SELECT v.code FROM feature_vocab v JOIN sub ON v.broader = sub.code)
SELECT COUNT(DISTINCT camp_id) FROM camp_features WHERE code IN (SELECT code FROM sub);  -- 321
```

The same query without the CTE (`WHERE code = 'aquatics'`) returns **61**. The 260-camp gap
between those two numbers is the trap: a camp tagged `kayaking` and nothing coarser is a camp with
aquatics, and a literal match silently drops it.

---

Requirement text reached through these endpoints (`requirement-sets`, and the rank and adventure
trees that reference them) is **© Scouting America**, reproduced with attribution for non-commercial
use and **not** covered by this dataset's CC BY-NC-SA license. `meta.json` restates this in
`text_rights`. See [`NOTICE.md`](../NOTICE.md).
