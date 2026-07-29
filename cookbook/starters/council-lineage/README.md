# council-lineage

"My council merged -- what is it now?" Give it any council id, current or long defunct, and it
prints a lineage timeline (first record, renames, mergers and absorptions), who serves that area
today, what the council absorbed, and how certain any of it is.

## Usage

    export OSA_BASE=../../../dist          # a built dist/, or the published base from meta.json
    export PYTHONPATH=../../python         # the shared osa.py helper

    python main.py mississippi-riverlands   # current: shows what it absorbed and its rename
    python main.py choctaw-area             # defunct: resolves forward to whoever serves it now
    python main.py conquistador             # seven renames, zero `renamed` events
    python main.py llano-estacado           # two hops: -> golden-spread -> prairie-sky

    python main.py --selftest               # canned council, asserts the invariants

`--base <url-or-directory>` works instead of `OSA_BASE`. A directory (a built `dist/`) is a valid
base, so the tool runs offline against a checkout.

## Traps it demonstrates

**A defunct council is not a missing council.** Roughly half of the published councils are
historical. Looking one up in `v1/current/councils.json` and reporting "not found" throws away a
full identity spread across `versions` and `events`.

**Most renames are not events.** Exactly one council in the dataset has a `renamed` event; every
other rename is visible only as the `name` changing between two consecutive `versions`.
`conquistador` shows seven of them. Reading `events` alone loses all of it; reading
`versions[-1].name` alone loses the name the user is actually searching for.

**Events are published on every participant, so the walk goes both ways.** `participants[].role`
is `predecessor`/`subject` for the side that ends and `continuing`/`successor` for the side that
carries the area forward. Hopping successor to successor resolves a defunct id to a council that
exists today (`llano-estacado -> golden-spread -> prairie-sky`); reading the same events from the
other side lists what a current council absorbed. The walk is cycle-guarded, because an event
recorded from both ends can point back.

**`date` is frequently null and `confidence` runs 0.4-0.8.** These are the least certain facts in
the dataset. Printing "merged in 2026" when `date` is null is fabrication, so undated rows are
printed as `?` in their own section rather than being interleaved into a sequence the source does
not claim, and `method` and `confidence` are shown per row.

**`valid_to` is a coarse bound, not an end date.** For councils absent from the current maps it is
the first year they were observed missing, which the timeline says out loud.

**Territories are versioned too.** `territory:cst-16` was "National Service Territory 16" before
the 2024 reorganisation, so the name in force comes from the version with `valid_to: null` -- not
from `versions[0]`. A defunct council usually has no territory of its own, so the tool resolves
its successor's and labels it `(via <successor>)`.

## What `--selftest` asserts

`mississippi-riverlands` has both a merger and a rename, and both are undated. The selftest
asserts the dated rows are ordered, that every `participants[].ref` resolves in the council index,
that every event publishes `method` and a `confidence` in (0, 1], that at least one row is below
confidence 1.0 and at least one stays undated, that walking forward from each predecessor reaches
a *current* council and that the predecessor's own document names the same successor, that a
current council ends the forward walk at itself, and that the territory ref resolves to a name.
