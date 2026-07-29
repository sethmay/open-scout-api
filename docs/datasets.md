# Datasets

What is actually in here, one section per dataset: counts, how each was sourced, and the caveats
that change how you use it.

[← README](../README.md) · [Endpoints & projections](./endpoints.md) · [Data model](./model.md)

Every number below is read from `dist/v1/meta.json` or computed from the published data at
**v0.54.0**. Everything listed ships today; the not-yet-built backlog is in
[`TODO.md`](../TODO.md).

## Inventory

| Dataset | Total | Current | What it is |
|---|---|---|---|
| [Councils](#councils) | 420 | 229 | Chartered local organizations, with merger and rename lineage |
| [Territories](#territories) | 20 | 14 | The service territories councils are grouped into |
| [Camps](#camps) | 448 | 448 | Council and national camp properties, placed and described |
| [Merit badges](#merit-badges) | 268 | 140 | The badge catalog back to 1910, rename lineage included |
| [Requirement sets](#requirement-sets) | 667 | 292 | Requirement trees for badges, adventures, and ranks |
| [Cub adventures](#cub-adventures) | 177 | 139 | The unit of Cub Scout advancement |
| [Ranks](#ranks) | 21 | 21 | Advancement ranks across all four programs |
| [OA lodges](#oa-lodges) | 238 | 238 | Order of the Arrow lodges, each tied to its council |
| [Awards](#awards) | 52 | 52 | Earned awards and recognitions: knots, honors, and training awards |
| [Positions of responsibility](#positions-of-responsibility) | 29 | 29 | Youth leadership positions that satisfy rank requirements |
| [Adult training](#adult-training) | 28 + 67 | 28 + n/a | Courses, and what each position must complete |
| [Merit badge popularity](#merit-badge-popularity) | 5 years, 692 ranks | n/a | Badge popularity 2021–2025, as ranks |
| [Controlled vocabularies](#controlled-vocabularies) | 7 lists, 172 terms | n/a | Every coded value with a label and a description |

`n/a` means the dataset has no `current` projection: a rankings year and a training rule are not
things that expire, so there is nothing to filter. Do not expect a `current` count for them.

### Councils

The chartered local organizations that own the camps, charter the units, and are the join key most
consumers actually need.

- **420 total: 229 current, 191 historical** (merged, renamed, or defunct).
- All 229 current councils carry a `territory` ref, and those refs cover all 14 live territories.
- 209 carry `states_served`; 157 carry a founding year, which is the `valid_from` of the council's
  earliest version rather than a field of its own.
- **57 councils carry more than one version.** That is the rename history: a council that changed
  name has one version per name, with half-open validity windows.
- **119 events:** 64 `absorbed`, 52 `merged`, 2 `discontinued`, 1 `renamed`. The 116
  merger/absorption events are the lineage graph; 112 of them were extracted from Wikipedia.

**Sourcing.** Version facts are `imported` (camp-finder, plus the official Council Service
Territory maps for the territory assignment) and `llm_extraction` from each council's English
Wikipedia article, confidence 0.5–0.8 with most at 0.7–0.8. The merger and absorption events are
`llm_extraction` at 0.75–0.8.

> [!NOTE]
> A rename is **not** an event here. It is a new version. Only mergers, absorptions, and
> dissolutions are events, because those involve a second party. See
> [change is an explicit event, but renames are not](./model.md#3-change-is-an-explicit-event-but-renames-are-not).

Endpoints: `v1/current/councils.json`, `v1/councils/index.json`, `v1/councils/{id}.json`. See the
[endpoint reference](./endpoints.md#endpoint-reference).

### Territories

The 14 Council Service Territories every current council belongs to, plus the structures they
replaced, so a 2019-era document is still resolvable.

- **20 total: 14 current CSTs, 2 merged National Service Territories, 4 legacy regions.**
- `division_type` tells them apart: `council_service_territory` (14, current),
  `national_service_territory` (2, historical), `region` (4, historical).
- **Numbering is not contiguous.** NSTs 2 and 11 were merged away in 2024, so the live set is
  1, 3–10, and 12–16.
- 3 events carry the reorganization: `reorganized` (2021, regions → NSTs), `renamed` (2024,
  NST → CST), `discontinued` (2024, the merged pair).

**Sourcing.** All `curated` from the Wikipedia CST article and the official territory maps,
confidence 0.5–0.85.

> [!NOTE]
> The two historical NSTs keep their `cst-` ids (`cst-2`, `cst-11`) even though their names say
> "National Service Territory". Ids are permanent; names are versioned. Never parse an id for
> meaning. See [identity is permanent](./model.md#1-identity-is-permanent-and-separate-from-state).

Endpoints: `v1/current/territories.json`, `v1/territories/index.json`,
`v1/territories/{id}.json`. The index also exposes `number` and `division_type` so a consumer can
split the mixed listing without fetching each entity.

### Camps

Every camp property the camp-finder site lists, deduplicated, placed on a map, and described in
evergreen prose. This is the dataset most people arrive for.

- **448 camps**, all current, seeded from [camp-finder](https://github.com/sethmay/camp-finder).
- `camp_type`: **349 resident, 64 day, 35 high-adventure.**
- `operator`: **444 council, 4 national** (Philmont Scout Ranch, Florida Sea Base, Northern Tier,
  and James C. Justice National Scout Camp at the Summit).
- **50 retired ids** resolve to the surviving camp through
  [`v1/camps/aliases.json`](https://sethmay.github.io/open-scout-api/v1/camps/aliases.json).
  Duplicate and session-variant listings were merged into their base camp, and scraped-artifact
  names corrected to the real property name.
- **41 co-located distinct camps carry a `reservation` grouping** across 18 reservations, 17 of
  them named (Goshen Scout Reservation holds 6), so a consumer can render one pin per property.
- **447 camps have coordinates**, each with `elevation_ft` (90 m DEM) and July climate normals
  `july_high_f` / `july_low_f` (WorldClim 1 km, 1970–2000). One camp is unplaceable.
- **371 carry an evergreen `summary`**, durable prose with no dates, fees, or sessions in it.
- **366 camps carry 6,379 `features` entries** from the 128-term
  [`camp-features`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-features.json)
  vocabulary. That is 95% of the 384 non-day camps. 205 entries across 170 camps are marked
  `signature`, where the camp presents them as a headline draw. 2,823 entries carry a prose `note`,
  which lives only in the per-entity file.

**Sourcing.** 436 versions `imported` from camp-finder, 12 `curated`, confidence 0.6–0.9. Features
were surveyed per camp and each entry records a `features_source_tier` saying how good the source
was. Sessions, fees, and schedules are deliberately absent: they belong at the council site and go
stale in weeks.

> [!WARNING]
> **`features` must be read together with `features_verified_at`.** An empty array with a date
> means *surveyed, nothing found*. An empty array with a null date means *never surveyed, nothing
> known*. Those are different facts and collapsing them turns "we don't know" into "offers
> nothing". See [read the date with the array](./endpoints.md#camp-features-read-the-date-with-the-array).

> [!WARNING]
> **`geo_precision` gates plotting: 336 `exact`, 111 `approximate`, 1 null.** A point shared by
> several camps is a reservation centroid, so it is `approximate`, not `exact`. Plot those as an
> area, never as a pin claiming a street address. A build gate rejects any point outside its state
> box. `elevation_ft` and the July normals are sampled at the stored point, so they inherit its
> precision. See [the projection contract](./endpoints.md#the-projection-contract) for how
> `geo_precision` qualifies the `lat`/`lon` pair.

> [!NOTE]
> Day camps are out of scope for the feature survey. A day camp often runs at a rented site, so
> its own page describes a program rather than a property.

Endpoints: `v1/current/camps.json` (council inlined), `v1/camps/index.json`, `v1/camps/{id}.json`,
`v1/camps/aliases.json`. See [alias maps](./endpoints.md#alias-maps).

### Merit badges

The full badge catalog, current and discontinued, with the rename chains that connect a 1910 badge
to the one it became.

- **268 total: 140 current, 128 historical**, going back to the **13 badges of 1910** (Ambulance,
  Clerk, Cyclist, Electrician, Gardener, Horseman, Marksman, Master-at-Arms, Musician, Pioneer,
  Seaman, Signaller, Stalker).
- Each version carries the badge's name, its introduction year (`valid_from`), its retirement year
  (`valid_to`), its BSA recordkeeping number where one was ever assigned (167 badges), and
  `eagle_required`.
- **61 `superseded` events chain the renames** and 67 `discontinued` events close the rest.
  That is 128 events for 128 historical badges, so nothing retires without a record. Lineages are
  walkable: `clerk → business → american-business`, `mining → rocks-and-minerals → geology`,
  `seaman → seamanship → small-boat-sailing`, `ambulance → first-aid`.
- **All 140 current badges carry an original-prose `description`** of 24–38 words, written from the
  badge's own requirements, plus one or two `tags` from the 16-term
  [`merit-badge-tags`](https://sethmay.github.io/open-scout-api/v1/vocab/merit-badge-tags.json)
  vocabulary (218 tag applications, every code in use). So a catalog can be browsed and filtered
  by subject without touching requirement text.

**Sourcing.** 143 versions `curated`, 126 `scraped` (usscouts.org badge history), confidence
0.7–0.9. A build gate rejects any description sharing 8+ consecutive words with its own badge's
requirement text: that text is © Scouting America, and these descriptions are deliberately ours.

> [!WARNING]
> **`eagle_required` is `null` for 126 of the 128 historical badges: unknown, not false.** It
> cannot be sourced for a badge retired before the modern published Eagle list, and a consumer that
> reads null as false will quietly assert a fact nobody has. Every badge in
> `v1/current/merit-badges.json` carries a real boolean.

> [!NOTE]
> **17 current badges are `eagle_required: true`, but the in-force Eagle requirement text names
> 18.** The eighteenth is Citizenship in Society, which was Eagle-required from 2022-07-01 and then
> discontinued as a badge on 2026-02-27. It is one of the two historical badges with a non-null
> flag (the other is Computers, false). Count from the requirement tree if you want the list Star
> and Life cite; count from `current/merit-badges.json` if you want badges a Scout can still earn.

Endpoints: `v1/current/merit-badges.json`, `v1/merit-badges/index.json`,
`v1/merit-badges/{id}.json`.

### Requirement sets

The requirement trees themselves (for badges, Cub adventures, and ranks) as structure rather than
a wall of text, with every historical edition kept.

- **667 documents: 368 merit-badge, 252 adventure, 47 rank**, covering 141 badges, 169 adventures,
  and 21 ranks.
- **292 are in force** (140 badge, 131 adventure, 21 rank); 375 are superseded (228, 121, 26).
  `effective_from` spans **1995-09-01 to 2026-01-01**, and 336 documents name what they `supersedes`.
- **131 of 141 badges carry more than one edition; 96 carry three.** So "which requirements applied
  when this Scout started" is answerable, not a guess. Effective windows are gate-checked for gaps
  and overlaps.
- Every tree carries numbering, nesting, `choose`-N and option groups, and a `ref` to the entity a
  node stands for. **Eagle requirement 3 resolves to a 14-slot graph** (3a–3n) in which three slots
  (3i, 3j, and 3l) are `choose: 1` groups, so it names **18 distinct badges across 14 slots**.
  "How many Eagle slots are filled" is therefore computable instead of a paragraph to parse. Star
  and Life requirement 3 both say *"any of the 18 merit badges on the required list for Eagle"*
  verbatim, which is why both numbers are real and neither is a typo.
- **66 adventure editions carry a `completion_rule`**: where a source states how many requirements
  are needed rather than "all of them", that sentence is published verbatim instead of being
  guessed into structure.

**Sourcing.** 519 documents `scraped`, 148 `curated`, confidence 0.75–0.9. Each edition links its
own source revision.

> [!WARNING]
> **Requirement text is © Scouting America and is NOT under this dataset's license.** All 667
> documents set `includes_official_text: true` and carry a `text_rights` statement; that carve-out
> travels with the text wherever you put it. Reproduced non-commercially with attribution, subject
> to takedown. Everything else in the repo (ids, structure, refs, descriptions) is the dataset's
> own license.

Endpoints: `v1/current/requirement-sets.json` lists only the in-force edition per subject;
`v1/requirement-sets/index.json` lists all 667. That split is deliberate, and the reasoning is in
[the projection contract](./endpoints.md#the-projection-contract).

### Cub adventures

The unit of Cub Scout advancement and the Cub-side analogue of a merit badge: a rank is earned by
completing six required adventures plus any two electives.

- **177 total: 139 current (36 required, 95 elective, 8 special elective) and 38 retired** by the
  2024 program.
- Ids are Scouting America's own canonical slugs (`pick-my-path-lion`, `bobcat-aol`). Each
  adventure names the rank or ranks offering it; among current adventures only `slingshot` (6
  ranks) and `bb-guns` (5) span more than one, though ten retired adventures do as well.
- Requirement-set ids are prefixed `adventure-` because **five current adventures share a name with
  a current merit badge**: Cycling, First Aid, Fishing, Personal Fitness, Swimming (nine if
  retired entities on both sides are counted).
- **Every current required adventure carries the `area` it fills**, one of six in
  [`adventure-areas`](https://sethmay.github.io/open-scout-api/v1/vocab/adventure-areas.json):
  Character & Leadership, Personal Fitness, Personal Safety, Family & Reverence, Citizenship,
  Outdoors. 36 required adventures over 6 ranks, and a build gate proves each rank fills all six
  exactly once, so "which of my six required slots are still open" is a group-by, not a list diff.
  The 103 electives and special electives carry `area: null`.
- **The pre-2024 line-up is recorded too**, from the USSSP archive: **121 historical editions** (83
  effective 2018-09-01, 38 effective 2022-06-01) and 38 events (15 `discontinued` on 2022-06-01,
  20 `discontinued` and 3 `superseded` in 2024). A Wolf's 2019 requirements and a Wolf's 2025
  requirements are both answerable.

**Sourcing.** All 204 versions `scraped`, confidence 0.8–0.9.

> [!WARNING]
> **The 8 shooting-sports adventures have no published requirements**: Archery at all six ranks,
> plus BB Guns and Slingshot. They are completed "only at approved events with qualified
> instructors" and have no page of their own, so they ship as entities with no requirement-set
> document at all, and a null `url`. Code that assumes every adventure resolves to a requirement
> set (or that dereferences `url`) will fault on exactly these eight.

> [!NOTE]
> **Areas are a 2024 construct and are `null` on pre-2024 windows.** Reading `area` off a
> historical edition tells you nothing about that edition; it tells you the field did not exist yet.

Endpoints: `v1/current/adventures.json`, `v1/adventures/index.json`, `v1/adventures/{id}.json`,
plus the `adventure-` prefixed documents in `v1/requirement-sets/`.

### Ranks

Every advancement rank in every program, with the requirement history behind the Scouts BSA ladder.

- **21 ranks across 4 programs:** 7 Scouts BSA (Scout → Eagle), 6 Cub Scout (Lion → Arrow of
  Light), 4 Venturing (Venturing → Summit), 4 Sea Scout (Apprentice → Quartermaster). All current.
- Requirement content lives in **47 rank requirement-set documents**: 21 in force, plus **26
  historical Scouts BSA editions spanning 2016–2023** with `supersedes` chains.
- The current Scouts BSA set is the 2024 edition (No. 33216) via usscouts.org; Cub, Venturing, and
  Sea Scout come from official scouting.org pages plus the 2026 Sea Scout PDFs.
- **The six Cub rank trees are pure structure.** The rule they state is "six required Adventures and
  any two elective", so each tree is two groups of `ref`s into
  [Cub adventures](#cub-adventures) rather than inlined text.
- Star, Life, and Eagle trees resolve into
  [positions of responsibility](#positions-of-responsibility) and, for Eagle requirement 3, into
  [merit badges](#merit-badges).

**Sourcing.** All 21 rank entities `curated` at confidence 0.9; the requirement documents carry
their own provenance.

> [!WARNING]
> The full verbatim rank requirement tree is © Scouting America, the same carve-out described
> under [requirement sets](#requirement-sets).

Endpoints: `v1/current/ranks.json`, `v1/ranks/index.json`, `v1/ranks/{id}.json`.

### OA lodges

Order of the Arrow lodges, each linked to the council that charters it.

- **238 lodges**, all current, from the official OA lodge locator feed (oa-bsa.org).
- **All 238 carry a `council` ref** and HQ city, state, and coordinates. 41 OA sections across 2
  regions (E: 125, G: 113). Website where the feed gives one.
- Officer and contact PII is excluded on purpose.

**Sourcing.** All 238 `official_publication` at confidence **1.0**, the only dataset here sourced
from an official machine-readable feed, and the only one that reaches 1.0.

> [!NOTE]
> Lodges carry **no `geo_precision`** field; that gate exists on camps only. These coordinates are
> the feed's own and are not independently classified, so treat them as lodge HQ rather than as a
> surveyed property location.

Endpoints: `v1/current/oa-lodges.json`, `v1/oa-lodges/index.json`, `v1/oa-lodges/{id}.json`.

### Awards

Earned awards and recognitions: the things that hang on a uniform because someone did something,
not the things sewn on because of a role.

- **52 awards**, all current, from the Guide to Awards and Insignia (No. 33066).
- Categories: 19 scouting honors, 16 special recognitions, 14 training awards, 3 religious-emblem
  knots. Audience: 36 adult, 15 both, 1 youth.
- Facts only: `category`, `audience`, `programs`, `square_knot_no`, `insignia_nos`, `wear`,
  `restricted`, and a `summary`.
- Excludes uniform insignia and per-faith religious emblems, both of which are separate problems.

**Sourcing.** All 52 `llm_extraction` at confidence 0.85, with catalog numbers source-verified
against the Guide.

Endpoints: `v1/current/awards.json`, `v1/awards/index.json`, `v1/awards/{id}.json`.

### Positions of responsibility

The youth leadership positions that satisfy the Star, Life, and Eagle service-in-a-position
requirement, so "which positions count for this rank" is a lookup rather than a reading exercise.

- **29 youth positions:** 16 in a Scout troop, 19 under the requirements' combined "Venturing crew /
  Sea Scout ship" heading; 10 troop-only, 13 crew-or-ship-only, 6 in both.
- **104 rank-to-position refs:** 35 for Star, 35 for Life, 34 for Eagle.
- `audience` is `youth` on all 29. Adult leadership roles are a separate catalog, covered under
  [adult training](#adult-training).

**Sourcing.** All 29 `curated` at confidence 0.9, from the rank requirement text itself.

> [!WARNING]
> **Acceptance is asymmetric, and it lives on the rank, not on the position.** Bugler is the single
> difference in the whole set: it counts for Star and Life but **not** for Eagle. Star and Life also
> accept a Scoutmaster-approved leadership project in place of a position; Eagle does not. A
> consumer that stores "counts for advancement" as a flag on the position will get Bugler wrong.
> The relationship is rank × position × unit type, which is exactly why the refs live on the rank.

Endpoints: `v1/current/positions.json`, `v1/positions/index.json`, `v1/positions/{id}.json`.

### Adult training

The adult side of the same question: which courses exist, and what a given adult position must
complete to be Position Trained.

**Courses: 28, all current.**

- Each carries a `code` where the BSA assigns one (25 of 28: Y01, S11, WS10, C40 …), a `delivery`
  channel, and a `renew_months` interval.
- `delivery`: 20 `unknown`, 3 `online`, 3 `classroom`, 2 `both`.
- Only 2 courses renew, both at 24 months. The rest do not expire.

**Requirements: 67 rules.**

- Keyed by **(position, unit type)** across 52 distinct position names and 6 unit types: 20 other,
  14 pack, 9 troop, 8 team, 8 ship, 8 crew.
- 68 (rule, BSA position code) pairs over 45 distinct codes, and **194 course links, 86 of them
  alternatives**, because a rule can be satisfied more than one way.
- **The compound key is the whole point.** Code `CC` (Committee Chairman) appears five times, once
  per unit type, and each one demands a different course set: `WS10` in a troop, `C60` plus pack
  position-specific in a pack, `WS11` in a team, `WS12` in a crew, `P44` in a ship. A single lookup
  keyed on position alone would be wrong four times out of five.

**Sourcing.** All `curated` at confidence 0.9 from the official Trained Leader Requirements PDF on
`filestore.scouting.org`.

> [!NOTE]
> **`delivery: unknown` on 20 of 28 courses means the source does not say.** It is not a third
> delivery mode and not an assertion that the course has no delivery channel. Same rule as
> `eagle_required`: absent is absent.

Endpoints: `v1/current/training.json`, `v1/training/index.json`, `v1/training/{id}.json`,
`v1/training-requirements/index.json`, `v1/training-requirements/{id}.json`. There is no
`current/` projection for training requirements.

### Merit badge popularity

How popular each badge was, year over year: a longitudinal series that exists nowhere else in
machine-readable form.

- **5 documents, one per year 2021–2025, 692 badge-year ranks:** 137 for 2021, then 138, 138, 138,
  and 141 for 2025.
- **Every year is a complete 1..N** over every badge offered that year, with `complete: true`. No
  partial years, no gaps to interpolate.
- 2025 grew to 141 because Artificial Intelligence, Cybersecurity, and Multisport were introduced
  that year; nothing dropped out.

**Sourcing.** All 5 `scraped` at confidence 0.9 from On Scouting's annual recap posts. 2021 has no
post of its own, so it is recovered from the prior-year column the 2022 post publishes, which is
recorded in that document's `provenance.notes`.

> [!WARNING]
> **These are ranks, not counts.** Scouting America publishes each badge's *position* and no
> absolute number anywhere, so `metric` is `earned_rank` and the schema rejects a document claiming
> counts. Do not sum them, average them, or difference them as though they were volumes: a badge
> moving from rank 40 to rank 30 tells you nothing about how many Scouts earned it.

> [!NOTE]
> Each post also restates the prior year's ranks, which corroborates the year before it
> independently. Where the two sources disagree, the disagreement is recorded in the document's own
> `provenance.notes` and the year's own post wins. The 2022 document records three such badges
> (mining-in-society, programming, skating). One outright source typo is corrected there too: the
> 2022 post printed rank 130 twice and omitted 135, which the 2023 restatement resolves exactly
> (journalism 130 → 135). 2024 is the clean case: its document records no discrepancies at all, and
> is `complete` over 138 badges. Corroboration leaves no positive trace (only *disagreements* land
> in `provenance.notes`), so "no discrepancies recorded" is the strongest claim the data supports,
> not a count of agreeing badges. A build gate rejects a badge ranked in a year it did not exist,
> which is what caught "Leather Work" (1928–1951) being mapped where today's "Leatherwork"
> belonged.

Endpoints: `v1/merit-badge-rankings/index.json`, `v1/merit-badge-rankings/{year}.json`. There is no
`current/` projection, because a rankings year does not expire.

### Controlled vocabularies

Every coded value in the dataset, published as data with a human label and a description, so a
consumer never has to hard-code a display string.

| Vocabulary | Terms | Applies to |
|---|---|---|
| [`camp-features`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-features.json) | 128 | `camp.features` |
| [`merit-badge-tags`](https://sethmay.github.io/open-scout-api/v1/vocab/merit-badge-tags.json) | 16 | `merit-badge.tags` |
| [`camp-program-types`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-program-types.json) | 10 | `camp.program_types` |
| [`camp-types`](https://sethmay.github.io/open-scout-api/v1/vocab/camp-types.json) | 7 | `camp.camp_type` |
| [`adventure-areas`](https://sethmay.github.io/open-scout-api/v1/vocab/adventure-areas.json) | 6 | `adventure.area` |
| [`adventure-categories`](https://sethmay.github.io/open-scout-api/v1/vocab/adventure-categories.json) | 3 | `adventure.category` |
| [`position-unit-types`](https://sethmay.github.io/open-scout-api/v1/vocab/position-unit-types.json) | 2 | `position.unit_types` |

**7 vocabularies, 172 terms.** Each file declares its own `applies_to` field paths, so the binding
between a code and the field it governs is machine-readable rather than documentation.

`camp-features` is the only hierarchical one: 46 of its 128 terms name a `broader` parent across 5
categories (activity, accommodation, facility, program model, subject), which is what lets a coarse
query like "has aquatics" resolve the whole subtree. That query is
[worked as a recursive CTE](./endpoints.md#the-feature-hierarchy-in-one-recursive-cte). Terms also
carry `aliases`, so a scraped synonym maps to the canonical code.

> [!WARNING]
> **Every vocabulary is `open: true`.** New terms can be added within `v1` (that is additive, not
> breaking), so a consumer must degrade gracefully on a code it has never seen rather than throw.
> Render the raw code and move on. See
> [additive-only under `v1`](./endpoints.md#additive-only-under-v1).

Endpoints: [vocabularies](./endpoints.md#vocabularies).

## Roadmap, and what is deliberately excluded

The full dataset catalog (shipped, designed, and not-yet-built, ranked by value ÷ effort) is in
[`TODO.md`](../TODO.md). No official machine-readable source exists for any of it, which is why
this project exists at all.

Two things are excluded on purpose, and will stay excluded:

- **Unit (troop/pack) rosters and BeAScout pin data.** PII-adjacent, ToS-hostile, and staleness
  equals liability: a wrong meeting location for a youth-serving organization is worse than no
  meeting location. BeAScout is used as a *council* lookup by ZIP, never as a unit source.
- **Districts.** Extreme churn and anecdotal sourcing. They appear only as best-effort attributes
  of council history, never as a standalone dataset.
