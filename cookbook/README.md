# Open Scout API cookbook

Runnable example code for consuming the [Open Scout API](../README.md). Every file here is
executed by CI against a freshly built `dist/`, and asserts its own invariants, so a recipe
that has quietly stopped being true fails the build instead of teaching you the wrong thing.

```bash
python tools/build.py && python tools/build_sqlite.py   # the API the recipes run against
python tools/validate_cookbook.py                       # run every recipe, gate on the result
python tools/validate_cookbook.py --only python,sql     # one suite at a time
```

By default a recipe talks to the published host. Point it anywhere with `OSA_BASE`:

```bash
OSA_BASE=http://127.0.0.1:8000 python cookbook/python/05-feature-hierarchy.py
```

## These recipes are not "how to call fetch"

This dataset models **change and uncertainty** as first-class data: identity is permanent and
separate from state, mergers and renames are events, and every fact carries provenance and a
confidence score. That design is the reason the data is worth having, and it is also why a
consumer who assumes a flat snapshot gets a **plausible wrong answer** rather than an error:

```js
camps.filter(c => c.features.includes("aquatics"))  // 61 of 321; codes are hierarchical
if (!badge.eagle_required) { /* not required */ }   // historical badges are null = UNKNOWN
average(ranks)                                      // earned_rank is ORDINAL. Meaningless.
council.versions[0].name                            // not necessarily the current name
events.filter(e => e.type === "renamed")            // finds 1 council; 57 renamed
```

Each recipe kills exactly one of those. Every file states the trap it prevents in a `TRAP:`
line in its header, and the gate rejects any file that lacks one.

## Recipes by trap

| Recipe | The wrong answer it prevents |
|---|---|
| `python/01-resolve-endpoints.py` | Hardcoding the provisional host, and discovering endpoints by 404 |
| `python/02-as-of.py` | Reading `versions[0]` as the current state |
| `python/03-lineage.py` | Looking for renames in `events`; only 1 council has one, yet 57 were renamed. Mergers *are* events |
| `python/04-camp-aliases.py` | A stored camp id silently 404s after duplicate listings merged |
| `python/05-feature-hierarchy.py` | Filtering on `aquatics` misses every kayaking-only camp |
| `python/06-feature-tristate.py` | Empty `features` read as "has none" instead of "never surveyed" |
| `python/07-source-tier.py` | Trusting a `portal`-sourced feature list as a description |
| `python/08-geo-precision.py` | Pinning city/state-centroid backfills as real camp locations |
| `python/09-reservation-grouping.py` | 41 co-located camps rendered as 41 overlapping pins |
| `python/10-eagle-slots.py` | Confusing the 18-badge Eagle-required list with req 3's 14 slots |
| `python/11-positions-for-rank.py` | Assuming Star, Life and Eagle accept the same positions |
| `python/12-requirement-tree.py` | Treating choose-N and option groups as all-required |
| `python/13-cub-rank-refs.py` | Looking for requirement text in a Cub rank tree |
| `python/14-badge-trends.py` | Averaging or summing an ordinal rank |
| `python/15-staleness.py` | Trusting `verified_at` forever, or confusing it with `imported_at` |
| `python/16-trained-for.py` | Keying adult training by position alone, ignoring unit type |
| `sql/*.sql` | The same traps in SQL, against the release SQLite artifact |
| `shell/*.sh` | `curl` + `jq` first contact, with the same footguns |
| `ts/src/recipes/*.test.ts` | The web consumer's path, typed from the published schemas |
| `csharp/Program.cs` | `bool?` makes the `eagle_required` tri-state trap especially easy to hit |

## Starter applications

Small but real programs, not snippets. Each supports `--selftest`, which is what CI runs.

- **`starters/advancement-check/`**: given earned badges, positions, and tenure, reports progress
  toward the next rank, including which of Eagle requirement 3's 14 slots are filled.
- **`starters/council-lineage/`**: walks versions and events to answer "my council merged, what is
  it now?", showing `method` and `confidence` rather than presenting an unverified merger as settled.
- **`ts/starters/camp-map/`**: a no-build browser map. Plots `exact` coordinates as pins and
  `approximate` ones as areas, collapses co-located camps to one reservation marker, and expands
  feature filters over the vocabulary hierarchy. Deployed with the API, so it is also live at
  [`starters/camp-map/`](https://sethmay.github.io/open-scout-api/starters/camp-map/) on the site.

## Layout

```
cookbook/
  python/     osa.py (shared plumbing) + NN-*.py recipes; stdlib only
  sql/        *.sql against dist/v1/open-scout-api.sqlite; `-- @assert` blocks are the gate
  shell/      curl + jq; portable jq features only
  ts/         one npm workspace: typed client, recipes-as-tests, no-build browser starter
  csharp/     console app, zero NuGet dependencies
  starters/   Python CLIs that support --selftest
```

Generated consumer types are committed and CI-gated. `python tools/gen_types.py --check` fails
the build if `cookbook/ts/src/generated/v1.ts` or `cookbook/csharp/Generated/V1.cs` has drifted
from `schema/v1/published-*.schema.json`. Regenerate with `python tools/gen_types.py`; never
hand-edit them.

## Conventions, if you are adding a recipe

- **Never hardcode the base URL.** Read it from the shared helper, which reads `OSA_BASE` first.
  The published host is provisional pre-1.0 and is expected to move.
- **Assert invariants, not counts.** The dataset grows weekly, so `len(camps) == 448` is a time
  bomb. Assert relationships instead: closure supersets, ordinal completeness, tri-state
  exhaustiveness, referential integrity, lower bounds.
- **A failed assertion must exit nonzero**, and a recipe must print a real result. Running the
  recipe is the test; there is no separate test file.
- **The shared helper holds only plumbing.** Trap logic stays inline in each recipe, duplicated
  across recipes on purpose: that logic is the thing you are meant to copy, so a recipe must
  stand alone apart from the helper import.
- **Zero third-party dependencies** in Python and shell.

## Licensing

Cookbook code is **MIT**, like `tools/`. The data it fetches is **CC BY-NC-SA 4.0**.

Merit-badge, rank and Cub adventure **requirement text is © Scouting America** and is *not*
under this dataset's license. Recipes that walk requirement trees therefore print structure,
numbering, refs, and counts (never verbatim requirement text), and surface the document's own
`text_rights` string. Keep it that way in anything you add. See [`NOTICE.md`](../NOTICE.md).
