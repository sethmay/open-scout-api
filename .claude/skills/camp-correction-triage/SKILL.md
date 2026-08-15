---
name: camp-correction-triage
description: >
  Triage community data-correction submissions from Camp Finder's "Suggest a Correction"
  form into source-verified, human-mergeable edits to data/camps/<id>.json in open-scout-api.
  Use whenever processing camp corrections: a corrections CSV / Google Sheet export, a single
  "Suggest a Correction" submission, or a request to "process the camp corrections". The agent
  drafts and validates; a human always makes the truth-call and the merge. Covers feature
  add/remove, closures, website, and program-type fixes fully; location/coordinate fixes are
  semi-manual (known tooling gaps, see the end); name/council/operator changes escalate.
---

# Camp correction triage

Camp/council data lives in this repo (`data/`). Camp Finder only consumes a published release and
cannot edit it, but users meet the data on Camp Finder, so the correction entry point lives there
and the queue plus the edits live here. **No backend anywhere.** Latency is days-to-weeks by
design — this is a reviewed correction pipeline, not a live wiki.

```
visitor on a Camp Finder page
  → prefilled Tally form → Google Sheet (the inbox) → CSV export
  → YOU (agent) draft + a human reviews        ← this skill
  → edit data/camps/<id>.json → PR + human merge → cut a release (semver skill)
  → Camp Finder bumps EXPECTED_VERSION + re-runs `npm run data` → deploy
```

Origin: `.workbench/camp-finder-corrections-handoff.md` (the first-submission worked example).

## Pulling the inbox (live — no manual download)

The inbox is a Google Sheet (Tally form responses). Pull it **live** rather than waiting for a CSV
to be handed over: the read-only share link exposes a CSV export at `<sheet-url>/export?format=csv`
(append `&gid=<n>` for a non-default tab). Fetch that, then parse with a real CSV reader — cells
contain embedded newlines (multi-line submissions), so a naïve line split is wrong.

> [!IMPORTANT]
> The export includes submitter **contact info (email) — PII**. Do **not** put the sheet URL or id
> in this repo (it is tracked and published to Pages). The current sheet URL lives in the agent's
> long-term memory (ask the maintainer if missing). Only the *method* is documented here.

### Tracking what's new (old vs. new submissions)

The sheet is **cumulative** — every export holds all submissions ever — so diff against what you've
already handled. Two signals:
1. **Accepted** edits are self-recording: the citation you append carries `(submission <ID>)`, so
   `grep -r "submission <ID>" data/camps` finds any accepted change.
2. **All dispositions** live in [`processed.json`](./processed.json) beside this skill:
   `{ "<id>": { "camp", "submitted", "disposition": accepted|held|rejected, "release", "note" } }`.
   A submission is **new** iff its `Submission ID` is absent from that ledger. **Append every
   submission you triage — including held/rejected ones**, which otherwise leave no trace in the data.

## Invariants — never break these

- **Never auto-merge user-originated data.** A rival can lie, a parent can misremember. The
  truth-call and the merge are the human's, always. You draft; you stop at the merge.
- **Verify before you edit.** Fetch the submitter's source URL (or web-search for corroboration)
  and confirm the claim. If you cannot verify, make no change — record it as HELD with the reason.
- **Vocab-only feature adds.** Only add a `code` that exists in
  `data/vocab/camp-features.json`. A term not in the vocab is a taxonomy decision (the
  additive-only guarantee) — HOLD it for a human, never invent a code.
- **Never publish the submitter's contact.** Not in provenance, not in a commit, not anywhere in
  git. Honor "Keep me anonymous" (don't name them). For "Credit me" with only an email given,
  withhold it and note "submitter requested credit but provided only an email, which is withheld."
- **Evergreen only.** `features[].note` and `summary` carry no dates, fees, sessions, or
  schedules. `tools/validate_data.py` enforces this and also reads month names as dates — write
  "can register", not "may register" (`may` = the month May → rejected).

## The pipeline (per submission)

1. **Normalize.** Resolve `camp_id` → `data/camps/<id>.json`; confirm name + state match. Watch for
   retired-id aliases (`data/camps/aliases.json`). If `camp_id` is blank (form `src` was `about` or
   `compare`), resolve the camp by name via `glob data/camps/*<slug>*`.
2. **Vet.** Is the source URL live (`tools/check_links.py`) and on the council/camp domain? Do the
   claimed feature codes exist in the vocab? Is any claim a no-op (already in the record)? Does the
   affiliation plus the source actually support the claim? Distrust and dig on any claim that a
   source contradicts (see Robert L. Cole below).
3. **Map** coarse "Which areas" labels → precise vocab codes (table at the end). Prefer specific
   child codes over a broad parent when the source names them (`snorkeling`/`kayaking` over a bare
   `aquatics`); use the parent only when the specifics are genuinely unknown.
4. **Draft** the edit to `versions[0]` (see per-category playbooks), append provenance, and run
   `tools/validate_data.py` + `tools/build.py`.
5. **Stop at the merge.** Open a PR or present the diff for a human. Present HELD items separately.

## Trust tiers (the `What's your connection to this camp?` column)

- **High** — `director` / `camp staff` / `council staff` confirming their own camp. Accept on their
  word when the camp's own pages are consistent; raise `provenance.confidence` toward `0.8`–`0.9`.
- **Lower** — `attended with a unit` / `parent` / `visitor`. Corroborate against an on-domain
  source before accepting; if only their word and nothing backs it, HOLD.

`features_source_tier` stays what the *source you read* justifies: `camp_page` for a web page,
`guide` only if you actually read a leader's/program guide document, `portal` for a registration
blurb. High submitter trust raises `confidence`, not the tier.

## Per-category playbooks

### A. Feature add
Map label(s) → vocab code(s), verify each against the camp's own pages (the page is not an
exhaustive list, so absence ≠ absent, but presence must be confirmed — do not bulk-add on the
submitter's word alone unless high-trust). Add `{ "code": "…" }`, with `"note"` for useful evergreen
texture and `"signature": true` only when the camp presents it as a headline draw. Bump
`features_verified_at` to today and raise `confidence` for a high-trust confirmation.

### B. Feature remove
Remove a code only if the source contradicts it, or a high-trust submitter says it's plainly gone
(e.g. council staff: "we cut welding"). Otherwise HOLD.

### C. Taxonomy hold (term not in the vocab)
Report it as HELD; never add it. Seen: `tomahawks`, `adult camper programming`, `volunteer staff`,
`Beast Feast` (an event, not a property feature). If a term recurs across camps, that's a signal to
propose a new vocab term — a separate, human taxonomy decision.

### D. Closure / operating status
`operating_status` is a plain enum on the version: `active | not_operating | closed`. **Camps have
no events array** — just set the field. Semantics (from the schema):
- **`closed`** — property gone/**sold**. Verify the sale (council news, area4history.com, a
  diocese/buyer announcement). Raise confidence to ~0.9 when the sale is independently documented.
- **`not_operating`** — property exists but runs no program (dormant / mothballed / moved to a
  sister camp). Verify via the council's own page.
- **Reject** — if evidence contradicts the claim, make no change and HELD it. *Robert L. Cole*:
  a parent reported "sold", but it's leased from PG&E/USFS, still council-scheduled, with recent OA
  ordeals — left `active`. The vet step exists precisely to catch this.
Keep features/summary as-is; the status field carries the change.

### E. Website fix
Confirm the proposed URL is live and is the camp's/council's own page for *this* camp, then set
`website`. This is not a feature change — do not bump `features_verified_at`. Append provenance.

### F. Program-type fix
`program_types[]` and `camp_type` use the `camp-program-types` / `camp-types` vocabs. Verify the
real program mix against the council site. *Camp Falling Rock*: was `cub_resident`, but the Cub
program there is a **day** camp → corrected to `cub_day` (it is primarily a Scouts BSA resident
camp). A "wrong program / mislabeled" complaint usually maps to a `program_types` correction.

### G. Location / map-pin fix  — SEMI-MANUAL, read the gaps
A wrong pin is an upstream coordinate problem, not a free-text field. Procedure:
1. Record the corrected `address`/`city` from the submission (the durable fact).
2. Re-place the point. `tools/geocode_addresses.py` only *refines camps that still have a point*
   (it skips null `lat` and guards within 60 km of the prior point), so for a camp whose pin is
   being corrected it does **not** help yet (see tooling gap #1). Until that's fixed, geocode the
   corrected street address directly and set `lat`/`lon`/`geo_precision`:
   - US Census (best for street addresses, no key):
     `https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?benchmark=Public_AR_Current&format=json&address=<enc>`
     → a TIGER match is `geo_precision: "exact"`.
   - Fallback OpenStreetMap Nominatim:
     `https://nominatim.openstreetmap.org/search?format=json&limit=1&q=<enc>`
     → a road/name match is `geo_precision: "approximate"`.
   - Validate the result is inside the state box (`tools/us_geo.py` `in_state`). The build gate
     rejects out-of-state points.
   - Elevation from open-meteo: `https://api.open-meteo.com/v1/elevation?latitude=<lat>&longitude=<lon>`
     → metres × 3.28084, round to nearest 10 → `elevation_ft`.
3. `july_high_f`/`july_low_f` are WorldClim-sampled at the point and **cannot be recomputed without
   the rasters** (tooling gap #2). If you cannot run `tools/july_temp.py` with `WORLDCLIM_DIR` set,
   leave them `null` and flag a follow-up; do not leave stale normals from the old point.
4. If you have no usable address (only "it's on the other side of the mountain"), source the real
   address from the council's camp page; if still unknown, null the coords + derived fields and
   HELD it for a human. Better unplaced than confidently wrong.

Every coord/derived field is nullable and not required — nulling a disputed pin (with the corrected
address recorded) is a valid interim state; the geocode pipeline re-places it.

### H. Name / council / operator change  — ESCALATE
No codified pattern yet (zero real submissions). Present to a human with the evidence; do not guess.

## Provenance & attribution convention

On acceptance, append to `versions[0].provenance.sources[]`:
- the submitter's source URL (when given and confirmed live):
  `{ "url": "https://…", "accessed": "<today>" }`, plus any source you verified against, and
- a `citation` recording the submission, e.g.:
  `{ "citation": "Community correction via Camp Finder Suggest-a-Correction form; submitted by <connection> <date> (submission <ID>), <kept anonymous at submitter request | credited to <handle>>. <what was verified / decided>." }`

Also: bump `features_verified_at` for feature changes; raise `provenance.confidence` per trust tier;
add `features[].note` for evergreen texture. When you geocode a coordinate, add a citation naming the
source (Census/OSM) and the DEM (open-meteo), matching the `geocode_addresses.py` convention.

## "Which areas does this involve?" label → vocab code

The form's optional multi-select uses Camp Finder's ~20 coarse filter labels, **not** exact codes.
Translate deterministically, then verify; prefer children of the broad parents when the source names
them.

| Form label | Vocab code |
|---|---|
| Aquatics | `aquatics` (prefer `swimming`/`sailing`/`canoeing`/`kayaking`/`snorkeling`/`rowing`/`paddleboarding`) |
| Shooting sports | `shooting_sports` (prefer `rifle`/`shotgun`/`archery`/`pistol`/`black_powder`/`cowboy_action_shooting`) |
| Climbing | `climbing` (prefer `rock_climbing`/`climbing_tower`/`rappelling`/`bouldering`) |
| COPE | `cope` |
| Horseback riding | `horseback` |
| Mountain biking | `mountain_biking` |
| ATV | `atv` |
| Scuba | `scuba` |
| Handicraft | `handicraft` |
| Zip line | `zip_line` |
| STEM | `stem` |
| Nature study | `nature_study` |
| High-adventure option | `high_adventure_option` |
| Older-scout program | `older_scout_program` |
| First-year program | `first_year_program` |
| Provisional attendance | `provisional_attendance` |
| Waterfront | `waterfront` |
| Pool | `pool` |
| Dining hall | `dining_hall` |
| Cabins | `cabins` |

Free-text adds (not in the multi-select) map the same way: confirm the exact code exists in
`data/vocab/camp-features.json` before adding; if it doesn't, HOLD (category C).

## Gates & finish

Run `python tools/validate_data.py` (schema + referential + windows + coord bounds + vocab + evergreen)
then `python tools/build.py`. Both must pass. Then present the diff + HELD items for a human. Do not
commit or merge user-originated data yourself unless the human explicitly approves.

## Known tooling gaps (blockers to automating category G — tracked in TODO.md)

1. **Geocode of corrected / null-coord camps.** `geocode_addresses.py` only upgrades camps that
   already have an approximate point; it can't place a camp whose pin was just cleared. Until it
   grows a "geocode from `address` where `lat` is null" path, location fixes are hand-geocoded
   (Census/OSM as above).
2. **July normals for relocated camps.** `july_temp.py` needs the WorldClim v2.1 rasters
   (`wc2.1_30s_tmax.zip`, `wc2.1_30s_tmin.zip`), absent from a normal checkout, so a moved camp's
   `july_high_f`/`july_low_f` stay null until someone runs it with `WORLDCLIM_DIR` set. Provision
   these in the pipeline/CI to close the loop.

Name/council/operator corrections (category H) also need real examples before they can be codified.
