# Open Scout API

[![API](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fsethmay.github.io%2Fopen-scout-api%2Fv1%2Fmeta.json&query=%24.version&label=api&color=2f6b2f)](https://sethmay.github.io/open-scout-api/v1/meta.json)
[![Build](https://github.com/sethmay/open-scout-api/actions/workflows/pages.yml/badge.svg)](https://github.com/sethmay/open-scout-api/actions/workflows/pages.yml)
[![Councils](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fsethmay.github.io%2Fopen-scout-api%2Fv1%2Fmeta.json&query=%24.datasets.councils.total&label=councils&color=555)](https://sethmay.github.io/open-scout-api/v1/councils/index.json)
[![Camps](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fsethmay.github.io%2Fopen-scout-api%2Fv1%2Fmeta.json&query=%24.datasets.camps.total&label=camps&color=555)](https://sethmay.github.io/open-scout-api/v1/camps/index.json)
[![Data license: CC BY-NC-SA 4.0](https://img.shields.io/badge/data-CC%20BY--NC--SA%204.0-555)](./LICENSE)
[![Code license: MIT](https://img.shields.io/badge/code-MIT-555)](./NOTICE.md)

**Open, versioned, machine-readable reference data for Scouting America (BSA):** councils, Council
Service Territories, camps, merit badges, ranks, requirements, awards, OA lodges, and more. Published
as static JSON with JSON Schemas, so you can build on it without scraping and without running a
server.

> [!IMPORTANT]
> **Unofficial community project.** Not affiliated with, endorsed by, or sponsored by Scouting
> America / Boy Scouts of America. No trademark claim or endorsement is implied. Facts are
> aggregated from public sources with per-fact provenance. Always confirm against each council's
> own site.

## Why this exists

No official machine-readable BSA structural data exists. Scraping gets you today's snapshot; the
hard part is **history**. Councils merge and rename, regions became territories, badges get retired
and revised. So this dataset models change and uncertainty as first-class data. Every fact carries its
source, method, verification date, and a confidence score, and nothing unverified is presented as
settled.

That means it can answer questions a snapshot cannot:

- *Which council serves this camp, and what was it called in 1998?*
- *How many of Eagle's 14 merit-badge slots has this Scout filled?* (14 slots, 18 flagged badges, and
  21 cumulative are three different numbers.)
- *Which camps offer aquatics?* (Filtering on `aquatics` finds 61 camps. The right answer is 321.)
- *This badge was renamed twice. What's the lineage?* (`clerk → business → american-business`)
- *Is this fact still trustworthy, and who says so?*

## See it working

The [**live camp map**](https://sethmay.github.io/open-scout-api/starters/camp-map/) plots all 448
camps straight from the API, and it distinguishes what it knows from what it guessed. The 336
surveyed coordinates are pins; the 111 city- or state-centroid backfills are dashed areas, because
rendering those as pins would put camps miles from the gate. Camps sharing a reservation collapse
into one marker, so the 447 placeable camps render as 336 pins and 88 areas. The one camp with no
coordinate at all is named rather than silently dropped.

[![The live camp map: 336 surveyed coordinates as pins, 111 approximate coordinates collapsed into 88 dashed areas, and a legend explaining the difference](./docs/img/camp-map.png)](https://sethmay.github.io/open-scout-api/starters/camp-map/)

It's a single HTML file with no build step: [`cookbook/ts/starters/camp-map/`](./cookbook/ts/starters/camp-map/).

You can also **[query the whole dataset in your browser](https://lite.datasette.io/?url=https://sethmay.github.io/open-scout-api/v1/open-scout-api.sqlite)**. That link opens the released
SQLite artifact in [Datasette Lite](https://lite.datasette.io/), which runs Datasette under
Pyodide, so all 22 tables are queryable with nothing installed. The
[SQL cookbook](./docs/endpoints.md#query-it-in-your-browser) has one-click versions of three
queries, including the one that shows why filtering on `aquatics` finds 61 camps when the right
answer is 321.

## Try it in 30 seconds

```bash
# every current council, denormalized and ready to use
curl -s https://sethmay.github.io/open-scout-api/v1/current/councils.json | jq '.count'
# 229

# a council that was renamed and absorbed another, with history included
curl -s https://sethmay.github.io/open-scout-api/v1/councils/mississippi-riverlands.json \
  | jq '{id, versions: (.versions|length), events: [.events[].type]}'
# { "id": "mississippi-riverlands", "versions": 1, "events": ["absorbed", "renamed"] }
```

```js
const { items } = await (await fetch(
  "https://sethmay.github.io/open-scout-api/v1/current/camps.json")).json();
```

Base URL: `https://sethmay.github.io/open-scout-api/`, path-versioned under `/v1/`. Resolve
endpoints from [`v1/meta.json`](https://sethmay.github.io/open-scout-api/v1/meta.json) rather than
hardcoding them. See the caveat in [`docs/endpoints.md`](./docs/endpoints.md).

## What's in it

| Dataset | Total | Current | What it is |
|---|---:|---:|---|
| [Councils](./docs/datasets.md#councils) | 420 | 229 | Councils incl. merged/renamed/defunct, with lineage |
| [Territories](./docs/datasets.md#territories) | 20 | 14 | Council Service Territories + legacy regions |
| [Camps](./docs/datasets.md#camps) | 448 | 448 | Resident, day, high-adventure + the 4 national bases |
| [Merit badges](./docs/datasets.md#merit-badges) | 268 | 140 | Back to the 1910 originals, with rename chains |
| [Requirement sets](./docs/datasets.md#requirement-sets) | 667 | 292 | Full requirement trees, effective-dated |
| [Cub adventures](./docs/datasets.md#cub-adventures) | 177 | 139 | The unit of Cub advancement |
| [Ranks](./docs/datasets.md#ranks) | 21 | 21 | All four programs, Lion through Quartermaster |
| [OA lodges](./docs/datasets.md#oa-lodges) | 238 | 238 | Order of the Arrow, linked to chartering council |
| [Awards](./docs/datasets.md#awards) | 52 | 52 | Knots, honors, and training awards |
| [Positions](./docs/datasets.md#positions-of-responsibility) | 29 | 29 | Youth leadership positions of responsibility |
| [Adult training](./docs/datasets.md#adult-training) | 28 | 28 | Courses by code, plus 67 position-trained rules |
| [Badge popularity](./docs/datasets.md#merit-badge-popularity) | 5 yrs | n/a | 2021-2025 rankings; **ranks, not counts** |

Full detail, sourcing, and caveats per dataset: [**`docs/datasets.md`**](./docs/datasets.md).

## Five ways this data will fool you

Each of these returns a confident wrong answer instead of an error. Every one links to a recipe
that fixes it.

**An exact match on a feature code finds 61 camps with water activities, out of 321 that have them.**
`c.features.includes("aquatics")` under-counts because feature codes form a tree, and each camp
carries the most specific codes that apply (`kayaking`, `fishing`, `canoeing`) without also
carrying the parent. Expand a code to its descendants before you match:
[`05-feature-hierarchy.py`](./cookbook/python/05-feature-hierarchy.py),
[`01-feature-hierarchy.sql`](./cookbook/sql/01-feature-hierarchy.sql).

**`eagle_required` has three states, and a falsy test collapses two of them.**
`if (!badge.eagle_required)` reads 126 of the 268 badges as "not Eagle-required" when the value is
`null`, which means nobody has researched that era. Only 18 badges are `true`, 124 are `false`,
and all 126 nulls are retired badges. Compare against `false` when you mean confirmed:
[`04-eagle-required.sql`](./cookbook/sql/04-eagle-required.sql),
[`02-eagle-required.sh`](./cookbook/shell/02-eagle-required.sh).

**`earned_rank` is a finishing position, so averaging it returns a number that means nothing.**
Scouting America publishes the order badges were earned in and never the counts, so rank 5 is not
twice as popular as rank 10, and the distance from 1 to 2 is not the distance from 40 to 41.
Compare positions inside one year, or track how a badge moved between years:
[`14-badge-trends.py`](./cookbook/python/14-badge-trends.py),
[`05-badge-trend-deltas.sql`](./cookbook/sql/05-badge-trend-deltas.sql).

**A quarter of camp coordinates are placeholders that plot exactly like surveyed ones.**
`map.pin(camp.lat, camp.lon)` across all 448 camps drops 111 pins on a city or state centroid,
which can sit many miles from the property. Read `geo_precision` first, `exact` on 336 camps and
`approximate` on 111, then style or drop the approximate ones:
[`08-geo-precision.py`](./cookbook/python/08-geo-precision.py),
[`10-geo-precision-audit.sql`](./cookbook/sql/10-geo-precision-audit.sql).

**Scanning `events` for renames finds 1 of the 57 councils that changed name.**
`events.filter(e => e.type === "renamed")` matches a single council because a rename is a new
entry in `versions[]`, with the old name still readable in the entry before it. The `events` array
carries lifecycle changes between entities instead (175 mergers, 128 absorptions). No council
records a rename both ways. Walk versions for names and events for lineage:
[`03-lineage.py`](./cookbook/python/03-lineage.py),
[`09-lineage-events.sql`](./cookbook/sql/09-lineage-events.sql). The model is described in
[`docs/model.md`](./docs/model.md).

## Cookbook

[**`cookbook/`**](./cookbook) is runnable example code in **Python, TypeScript, C#, SQL, and shell**:
42 recipes plus three starter apps. Every recipe is executed by CI against a freshly built dataset
and asserts its own invariants, so an example that has quietly stopped being true fails the build
instead of teaching you the wrong thing.

```bash
python tools/validate_cookbook.py     # 36 checks over all 42 recipes, against a local build
```

Each recipe kills one specific trap and names it in a `TRAP:` line. Real output:

```
$ python cookbook/python/05-feature-hierarchy.py
vocabulary      camp-features: 128 terms, 8 with children
aquatics        expands to 22 codes (20 direct)
deepest chain   ice_fishing -> fishing -> aquatics
bare code       61 camps carry "aquatics" itself
closure match   321 camps carry something in the closure
top codes       swimming=218, fishing=189, canoeing=183, kayaking=143, sailing=102
missed by trap  260 camps a bare `in features` check drops
```

Consumer types for TypeScript and C# are generated from the published schemas and CI-gated against
drift, via `python tools/gen_types.py --check`.

## Documentation

| Document | Covers |
|---|---|
| [**`docs/endpoints.md`**](./docs/endpoints.md) | Every endpoint, the projection contract, pinning, the SQLite artifact |
| [**`docs/datasets.md`**](./docs/datasets.md) | What is in each dataset, how it was sourced, and its caveats |
| [**`docs/model.md`**](./docs/model.md) | Identity, effective-dated versions, events, provenance, refs |
| [**`cookbook/README.md`**](./cookbook/README.md) | Every recipe mapped to the trap it prevents |
| [`PLAN.md`](./PLAN.md) · [`TODO.md`](./TODO.md) | Design rationale · roadmap and open questions |

## Status

**Pre-1.0.** Field shapes are stable and build-gated: every published file names its contract in
`$schema`, and the build fails on drift. `v1` fields are **additive-only**, so pinning to a
field set is safe. What is *not* yet frozen is the **host**: the base URL is provisional while a
permanent home is settled, which is exactly what cutting `1.0` will freeze. Until then, resolve
endpoints from `v1/meta.json` and pin data files by git tag via jsDelivr, because tags are immutable
wherever the repo ends up.

[camp-finder](https://github.com/sethmay/camp-finder) consumes this API as its core data.

## Repository layout

```
data/       authoritative source: canonical JSON, one file per entity
schema/v1/  JSON Schemas (draft 2020-12), canonical + published contracts
tools/      validate, build, and the cookbook/codegen gates
cookbook/   consumer examples in five languages + starter apps
docs/       endpoint, dataset and data-model reference
dist/       the generated static API (git-ignored; built and deployed by CI)
```

The repo **is** the database: writes happen via pull request, a CI validation gate blocks bad
merges, and GitHub Pages serves the built API. There is no runtime backend.

## Local development

Requires Python 3.11+.

```bash
pip install "jsonschema[format]"
python tools/validate_data.py        # schema + referential + version-window invariants
python tools/build.py                # compile data/ -> dist/  (open dist/index.html)
python tools/build_sqlite.py         # + a queryable SQLite artifact
python tools/validate_cookbook.py    # run every cookbook recipe against it
```

The enrichment and maintenance tools are run manually, never by CI: geocoding, elevation, July
temperature normals, camp link health, base-URL restamping (`restamp_identity.py`) and the
re-verification queue (`maintenance.py`). They carry the only extra dependencies: `july_temp.py`
needs `rasterio` plus the WorldClim rasters (~8 GB, git-ignored). **Their derived caches are
committed, so a normal validate or build needs neither the dependency nor the rasters.**

## Contributing

`data/` is the authoritative source, so edit the canonical JSON directly. There is no upstream to
re-import: `tools/import_camps.py` and `tools/geocode_camps.py` were one-time camp-finder seed
tools, kept for provenance, and `data/` has been hand-corrected since, so don't re-run them. To add
or fix an entity: edit `data/<dataset>/<id>.json`, then run `stamp_schema.py` →
`validate_data.py` → `validate_examples.py` → `build.py`, and open a PR. The same validators gate CI.

A camp rename, or a duplicate/variant folded into another camp, uses **`merged_from`**. The retired
id then resolves via [`v1/camps/aliases.json`](https://sethmay.github.io/open-scout-api/v1/camps/aliases.json),
and `validate_data.py` fails the build if a `merged_from` id is claimed twice or is still a live camp.

Every fact needs a checkable source in its `provenance` block; no bare high confidence without a
citation. New entities follow the id, versioning, and event conventions in
[`docs/model.md`](./docs/model.md) and [`PLAN.md`](./PLAN.md) §3.

## License & attribution

- **Data** (`data/` and the published projections): **[CC BY-NC-SA 4.0](./LICENSE)**: reuse with
  attribution, non-commercial, share-alike.
- **Code** (`tools/` and `cookbook/`): **MIT**, so you can lift a recipe into your own app whatever its
  license.

> [!WARNING]
> **Merit badge, rank, and Cub adventure requirement text is © Scouting America.** It is reproduced
> with attribution for non-commercial use, is marked `includes_official_text` + `text_rights` on the
> documents that carry it, and is **not** covered by this dataset's license, so don't relicense it.
> Only the requirement structure, numbering, and metadata are this project's contribution.

Seed sources and how to attribute: [`NOTICE.md`](./NOTICE.md).
