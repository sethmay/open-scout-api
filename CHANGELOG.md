# Changelog

One section per merge into `main`; newest first. Conventions: `skill://semver`.
Version anchors: this file only (no package manifests yet; add here when one appears).

- `PENDING` Triage 2 WLACC council-staff corrections: Camp Emerald Bay (pin relocated to the island's West End OSM node — prior coords mis-geocoded the Avalon mailing address — + website + 16 program/facility features; submission mis-prefilled the HESR Big Horn id, retargeted by content) and Camp Whitsett (+21 features incl. featured whitewater_rafting). Both staff removal requests held (camps' own pages still confirm the features); backfilled the triage ledger.

## 0.58.13 (patch) — 2026-08-15

- `6a2603e` Triage 2 council-staff corrections → not_operating: Montana Outdoor High Adventure Base (MOHAB) (council-announced pause after the 2026 season) and Arcola Scout Camp. Triage skill: document pulling the inbox live via the sheet's CSV export and add a `processed.json` ledger so held/rejected submissions are tracked too.

## 0.58.12 (patch) — 2026-08-15

- `18f989e` Triage 4 Camp Finder corrections: Resica Falls (+first-year/high-adventure/webelos), Baiting Hollow (website + cub programs + provisional), Forestburg (+hiking), Hinckley → not_operating (post-merger delisting; sale unverified). Plus council lineage: Theodore Roosevelt + Suffolk County merged 2026 into Scouting America Long Island (BSA 386).

## 0.58.11 (patch) — 2026-08-14

- `0fc07cd` Add 78 coverage-gap camps across 40 states (scout-camp-map sweep, batch 3; 21 parallel workers, councils re-verified); 29 held (sold/dupe/non-BSA/OCONUS). Camps 472 → 550. Completes the state-by-state sweep.

## 0.58.10 (patch) — 2026-08-14

- `c61692c` Add 18 coverage-gap camps across 8 councils (parallel-curated from scout-camp-map, councils re-verified); 6 held (sold/dupe/divesting).

## 0.58.9 (patch) — 2026-08-14

- `e41fe0f` Fill 5 coverage gaps from the scout-camp-map cross-reference (Alafia, Brorein, Flying Eagle, Nobscot, New England Base Camp), with councils re-verified.

## 0.58.8 (patch) — 2026-08-14

- `f72dade` Add Camp Warren Levis (Greater St. Louis Area Council); file a scout-camp-map coverage cross-reference in TODO.

## 0.58.7 (patch) — 2026-08-14

- `dc2f64f` Triage 2 more camp corrections: Camp Baldwin program-guide features; Camp Clark → not_operating (family camping), relocated, features pruned.

## 0.58.6 (patch) — 2026-08-14

- `074aa4a` Add the camp-correction-triage skill (v1) and file the two location-fix tooling tasks.

## 0.58.5 (patch) — 2026-08-14

- `a474cfc` Fill July normals for the 6 relocated camps from WorldClim.

## 0.58.4 (patch) — 2026-08-14

- `da68f52` Re-geocode Camp Baldwin (Dufur, OR) and Hanna Venture Base (CLSR) from the location batch.

## 0.58.3 (patch) — 2026-08-14

- `447e834` Triage 18 community camp corrections: 5 closures, 4 feature/program fixes, 6 relocation fixes.

## 0.58.2 (patch) — 2026-08-13

- `85da46c` Enrich Camp Emerald Bay features from a community correction (submission KpW95L8).

## 0.58.1 (patch) — 2026-07-31

- `3e44e4d` Follow-up corrections from a review of 0.58.0, before it shipped.
  - Kept imported_at present on every current camp rather than allowing null. A camp has always
    been imported, and the staleness examples read the field directly, so the build now fails
    with a clear message if a camp ever lacks it instead of publishing a null that breaks them.
  - The new build check now also confirms each listing kind actually pins its item shape, not
    just that a branch for it exists, so it cannot be hollowed out later.
  - Documented operating_status in the endpoint and dataset references, next to the other camp
    completeness qualifiers.
  - Smaller consistency fixes: the vocabulary file now also declares its schema, a rejection test
    was restored to its single intended defect, and two field descriptions and two roadmap notes
    were corrected.

## 0.58.0 (minor) — 2026-07-31

- `23e82e5` Added a camp field and closed several gaps a schema review found.
  - current/camps.json now includes operating_status (active, not_operating, or closed). A camp
    can be current but run no program, so this tells an operating camp from a dormant one, which
    the current flag alone cannot.
  - The three adult-training listings were being published without their item shape actually
    being checked. Their schemas now describe them fully, and a build check refuses any published
    listing whose kind has no matching shape, so the gap cannot reopen.
  - More of the rules the data already follows are now written into the schemas themselves, not
    just enforced by our build: a camp survey date requires its source tier, a required Cub
    adventure fills exactly one area, a "choose N" requirement must list its options, dates must
    be real calendar dates, and every record declares which schema it follows.
  - Dropped training-requirement from the current-projection kind list, since no current file is
    published for it (its index listing is unaffected). A consumer regenerating types sees that
    kind leave the current union.

## 0.57.1 (patch) — 2026-07-29

- `f232321` Follow-up corrections from a review of 0.57.0.
  - Four surviving councils still carried notes saying the predecessors added in 0.57.0 were not
    yet recorded. Updated each to point at the new record.
  - Added council number 573 to Yucca Council, taken from the same defunct-councils list already
    cited on the record.
  - The sources disagree on Carlsbad Council's end year, 1923 in one and 1924 in the other. Kept
    1924, noted the disagreement on the record, and lowered its confidence.

## 0.57.0 (minor) — 2026-07-29

- `2f658d9` Recorded eight councils that had merged into ones already in the data, so the
  histories now connect on both sides.
  - Each is a historical council that no longer operates: Yucca, Carlsbad, Forty Niner, Tar Heel
    Area, Pamlico, Neuse, Mill Valley, and Sausalito. They join as retired records, and a new
    event ties each to the council that took it in.
  - A lineage lookup can now walk backward from a current council to the ones it absorbed. High
    Desert Council links to Yucca, East Carolina Council to the three councils that merged into
    it, and Greater Yosemite Council to Forty Niner.
  - The absorbing councils were already correct; this fills in the other side of the relationship.

## 0.56.6 (patch) — 2026-07-29

- `4d52f7c` Corrected the previous release note for the new build check, which overstated what it
  catches.
  - The check catches the 0.56.3 error, where several councils were given the same copied history.
    It does not catch a history copied onto a single council, which was the separate error fixed in
    0.56.2. The 0.56.4 note now describes only what the check actually does.

## 0.56.5 (patch) — 2026-07-29

- `a46bf02` Hardened the TypeScript and C# type generator so it refuses a schema shape it cannot
  represent instead of emitting code that will not compile.
  - The generator turns the published schemas into typed definitions. A few shapes it did not
    handle would have produced a broken or missing type without any warning. It now stops with a
    clear message naming the shape, so the problem surfaces at build time rather than in a
    consumer's editor.
  - No published schema uses any of those shapes today, so the generated types are unchanged. This
    only guards the next schema edit.

## 0.56.4 (patch) — 2026-07-29

- `d522d63` Added a build check for the error corrected in 0.56.3, where several councils were
  given the same early names because one council's history had been copied onto them.
  - A rename history is unique to a council, so no two councils can share the same first two
    names. The build now fails if any do, and would have failed the day that error was introduced.

## 0.56.3 (patch) — 2026-07-29

- `51c0d4d` Fixed sixteen more councils that had the wrong history attached, the same problem found
  in Conquistador Council last release.
  - Five North Carolina councils all listed the same three early names (Wilmington Council, New
    Hanover County Council, Cape Fear Area Council). That history belongs only to Cape Fear Council.
    The other four now carry their own: Daniel Boone traces to the 1919 Asheville Council, East
    Carolina to the 1924 Wilson County Council, Old Hickory to the 1917 Winston-Salem Area Council,
    and Tuscarora was founded in 1923 with no earlier name.
  - Four California councils shared a Santa Barbara start that belongs only to Los Padres Council.
    Greater Yosemite now traces to the 1920 Modesto Council, Verdugo Hills to the 1920 Glendale
    Council, and Marin, formed in 1910, has no earlier name.
  - The same fix was applied to three Washington councils (only Inland Northwest kept the Spokane
    start), two Colorado councils (only Greater Colorado kept the Denver start), and two Maine
    councils (only Katahdin Area kept the Bangor start).
  - Every council still resolves to the same present-day council, number, and website as before.
    Only the historical names changed. Each new name history is drawn from the state Scouting
    article and the list of defunct councils, both already cited on these records.

## 0.56.2 (patch) — 2026-07-29

- `727b5a9` Corrected Conquistador Council's history, which had another council's past attached to
  it.
  - Conquistador Council in Roswell was recorded as having been named Albuquerque Council, Bemalillo
    County Council, Rio Grande Area Council, Northern New Mexico Council, Kit Carson Council, and
    Great Southwest Area Council. None of those are its names. They belong to the Albuquerque
    council that is now High Desert Council, and both sources agree on that.
  - Conquistador's real history is now recorded: it began as Roswell Council in 1920, merged with
    Carlsbad Council to become Pecos Valley Council in 1924, became Eastern New Mexico Council in
    1925, and took its present name in 1953. The old record dated that last change to 1982.
  - The council was also listed as serving New Mexico, Arizona, Utah, and Colorado. That is the
    other council's territory. Conquistador serves southeast New Mexico.
  - High Desert Council now carries all eight of its own names, from Albuquerque Council in 1918
    through the 2024 merger that created it.
  - The 1926 name is now spelled Bernalillo, after the New Mexico county whose seat is Albuquerque.
    The source spells it both ways in the same table, so the value is recorded at lower confidence
    with the disagreement noted.
  - Camps were never affected. Every camp was already attached to the right council.
  - Sixteen councils in five groups still share the start of a name history the same way, which is
    now written down for a later pass.

## 0.56.1 (patch) — 2026-07-29

- `ed702f4` Rewrote the README section that warns you about the five easiest ways to misread this
  data, because a reader who knows databases well could not tell what it was warning about.
  - Each warning now gives the wrong answer you get, the reason the data produces it, and what to
    write instead. The old version was five code comments that only made sense if you already knew
    the answer, and only one of the five had any explanation at all.
  - Every warning links to the recipes that fix it, so you can go straight to working code instead
    of searching the cookbook for the right one.
  - Corrected a count while checking the text: 58 councils have changed name, not 57. The old
    figure counted only the councils whose old name is visible in their version history and missed
    the one whose rename is recorded as an event.
- `45c02b4` Made the same warnings agree across the three reference documents that repeat them.
  - The cookbook guide said that mergers and renames are both recorded as events. Renames are
    recorded as a new version instead, which is what the model reference and every recipe in the
    cookbook already said.
  - The rename figure now reads the same everywhere: 57 councils show the change in their version
    history, one more records it as an event, and 58 have changed name in all.
  - A heading in the model reference now states both rules directly, that mergers are events and
    renames are version boundaries, and the link pointing at it was updated to match.

## 0.56.0 (minor) — 2026-07-29

- `d93dbfa` You can now query the whole dataset in your browser, with nothing to install.
  - One link opens the published SQLite copy in Datasette Lite, which runs a full SQL environment in the browser. All 22 tables are browsable and the query box accepts anything SQLite understands.
  - The endpoint docs include three ready-made queries, including the one that shows why a plain search for "aquatics" finds 61 camps when the real answer is 321.
  - The first load pulls in the browser runtime and a 7.8 MB database, so give it a few seconds. Queries after that come back in a few milliseconds.
- `811c28d` Edited every published page to read less like it was written by a machine.
  - Removed 174 em dashes from running prose and rewrote each sentence around them, rather than swapping in a different dash.
  - Also cut the negate-then-reframe habit ("this is not X, it is Y"), the phrases that announce their own importance, and stray bold.
- `8f5e49c` Settled on American spellings throughout, and fixed a few phrases that described things as honest or genuine when a plain word was clearer.

## 0.55.0 (minor) — 2026-07-29

- `ab9c500` Rewrote the front page and moved the reference material onto its own pages, so the project now explains itself in a couple of minutes instead of seventeen.
  - The README opens with the questions this data can answer, a picture of the live camp map, and an example you can paste into a terminal.
  - Endpoint details, per-dataset notes, and an explanation of how the data records change over time each moved to their own page under `docs/`.
  - Corrected about a dozen counts that had quietly drifted as the data grew, including the number of councils and the number of camp features.
  - The opening sentence had described camps, merit badges, and requirements as planned. All three have been published for months.
  - Added a link checker to the build, so a broken link or a wrong heading reference fails the build instead of shipping.
  - The queryable SQLite copy is now served alongside the API. The docs had promised that for a while, but the publish step was only building the JSON.
- `7478904` Fixed the shell examples for anyone working on Windows, where they failed on the first line.

## 0.54.0 (minor) — 2026-07-29

- `07cd555` Added a cookbook of runnable examples, so you can copy working code instead of working it out from the reference docs.
  - 42 recipes across Python, TypeScript, C#, SQL, and shell, plus three small starter programs: a camp map, an advancement checker, and a council history walker.
  - Each recipe fixes one specific way this data can mislead you. Searching camps for "aquatics" finds 61 of the 321 that offer it, because the feature codes are arranged in a hierarchy. Retired merit badges have no answer recorded for "is this Eagle-required", which reads as "no" unless you check. Badge popularity is published as rankings, so averaging it means nothing.
  - Every recipe runs during our build checks against a fresh copy of the data, so an example that has quietly stopped being true fails the build rather than teaching you the wrong thing.
  - TypeScript and C# type definitions are generated from the published schemas, so they cannot drift from what the API actually sends.
  - Two dates in the data turned out to be wrong and are now fixed: one council's name history ran backwards, and one merit badge was recorded as existing for no time at all.

## 0.53.0 (minor) — 2026-07-27

- `dfd5b73` **First corpus-wide camp feature audit: 366 camps swept — and the headline finding was
  the auditor.** The first run reported **1,377** features with "no lexical trace". **949 of those
  were the tool's own bugs**; the honest number is **428**. Nine fixes to
  `tools/audit_camp_features.py`, each traced to a specific camp.
- **A 4 MB read cap silently emptied 45 leaders' guides.** A truncated PDF has no EOF marker, pypdf
  rejects the whole file, and the empty result was cached as a page that simply says nothing — so
  every feature the guide attests looked unsupported. `ga-camp-sidney-dew` went 24 flags → 0.
- **A `.docx` guide was scored as 594 KB of XML noise.** `.docx` is a ZIP; decoding it as UTF-8
  yields something shaped like text, containing the camp's name 72 times and no prose.
  `oh-muskingum-valley-scout-reservation` went 24 flags → 1.
- **Council navigation attests features on every page of a site.** Chief Seattle's chrome names its
  "Trading Post" and "National Youth Leadership Training", which made both appear attested for every
  camp that council owns — a page-level bleed that URL scoping cannot see, because the page really
  is the camp's. The council homepage is now a per-host chrome control, fetched once and reused.
- **Evidence is per source and cited.** Findings carry the URL that produced them, and the crawl no
  longer wanders from a camp page onto the council's `/donate/` and `/advancement/` pages.
- **An audit may never report a defect on evidence it failed to fetch** — flags on camps with an
  unreadable cited source are now a separate `unverified` bucket, not a finding.
- **Three vocabulary alias gaps, each confirmed against the surveyors' own notes:** `sports_field`
  gains `ball_field`/`playing_field`, `pavilion` gains `picnic_shelter`/`shade_shelter` (our own
  feature notes say "shade shelters at every program area"), and `atv` — whose 3-letter code was
  being dropped by a `len > 3` token filter — can now match a page that says "ATV". 41 false flags
  removed. Bare `shelter` was deliberately NOT aliased: `adirondack_shelters` is a different code.
- **No features were removed.** Every remaining flag is a lead needing a human, and the largest
  cluster (`stem`, 45 camps) turns on a vocabulary question — those guides name Robotics and Space
  Exploration but never "STEM" — that must be decided before any sweep. Recorded in `TODO.md`.

## 0.52.0 (minor) — 2026-07-27

- `483e3ea` **Adult training: 28 courses and 67 position-trained requirements.** Parsed from
  Scouting America's own `TRAINED LEADER REQUIREMENTS` chart, which is a PDF and the only place the
  mapping exists. Two new datasets — `v1/training/{id}.json` (course code, delivery, renewal) and
  `v1/training-requirements/{id}.json` — plus three SQLite tables, 20 in all.
- **The key is (position, unit type), not position.** Registration code `CC` requires `C60` in a
  pack, `WS10` in a troop, `WS11` in a team, `WS12` in a crew and `P44` in a ship; a Chartered
  Organization Representative takes `Y01` in a pack and `Y02` in a crew. One record per position
  would have to pick one of those and be wrong five times. Same shape as the youth positions in
  0.49.0: the requirement is an edge.
- **Adult roles are deliberately NOT added to `data/positions/`.** That dataset's gate requires
  every position to be offered by some rank requirement — true of youth positions, false of every
  adult one. Reusing the kind would have meant deleting a correct gate.
- **`filestore.scouting.org` is reachable** where `www.scouting.org` returns 403, which is what had
  blocked this dataset. The chart PDF and the Guide to Leader Training both download cleanly.
- **Youth Protection renews every 24 months, read from the chart's own header sentence** rather
  than typed — the same derive-don't-transcribe rule as the rank counts.
- **Nothing invented.** The chart titles `D16`–`D26` only as a group ("Any Basic Commissioner
  Training"), and neither it nor the Guide to Leader Training names them individually, so all six
  carry the group's name and say so in their provenance. Source typos are preserved verbatim
  (`Neigborhood Chairman`, `Supernova Mentor Traning`), as is `91U` keeping `Y01` inside the Crew
  and Ship sections where every sibling row takes `Y02`.
- **Wood Badge, BALOO and NYLT are absent because no position requires them.** The Guide to Leader
  Training classes Wood Badge and Powder Horn as *advanced* and BALOO as *supplemental*; NYLT is
  youth training. Only YPT and IOLS (`S11`) from the original request are position-trained
  requirements, and both are here.
- **6 gates proven by injection**: a dangling course ref, a position with no Youth Protection
  course, two rows claiming one registration code in a unit type, a `choose` demanding more
  alternatives than exist, an id disagreeing with its filename, and a course no position requires.

## 0.51.0 (minor) — 2026-07-27

- `151a4ea` **Tenure and merit-badge counts are countable: 13 + 3 facts lifted out of prose.**
  `tenure_months` on any requirement demanding months of activity or service, `badge_count` on the
  ones stating merit-badge totals. Both derived from each requirement's own verbatim text at apply
  time, so a reissued book moves the numbers with it. New `rank_advancement` SQLite table answers
  "what does each rank demand" in one query.
- **Star and Life are a different rule from Eagle, and the source says so in its own wording.**
  Star's "any four **from the required list** for Eagle" is *list membership* — all 18 badges
  interchangeable, so Swimming and Hiking count as two (confirmed by the project owner). Eagle's
  "including **these 14** merit badges" is a slot tree, where Swimming and Hiking share slot (l) and
  count once. The extractor keys on exactly that difference, so Eagle gets no
  `badge_count.from_eagle_required`: publishing a bare count beside a stricter tree would invite
  consumers to check the weaker rule.
- **The chain is self-checking, because the source states the running total twice.** Star says six,
  Life says "five more (so that you have 11 in all)", Eagle says "a total of 21 (10 more than
  required for the Life rank)" — so `6 + 5 == 11` and `11 + 10 == 21` are gates, not assumptions.
- **Tenure turned out to be cross-program.** Not a Scouts BSA field: 13 facts across Scouts BSA,
  Sea Scout (Apprentice/Ordinary/Able/Quartermaster) and Venturing (Pathfinder/Summit) ranks,
  phrased three ways. Star carries it *twice* — four months being active, four months serving in a
  position — which are two obligations sharing a number, so they are two records.
- **5 gates proven by injection**: a tenure figure absent from its own sentence, a badge count
  absent from its own sentence, more required from the list than are earned, more required than the
  list held on that date, and a cumulative chain that does not add up.

## 0.50.0 (minor) — 2026-07-27

- `4b7185f` **`effective_to` is half-open everywhere: 253 published editions re-dated.** An edition
  applied when `effective_from <= D < effective_to`, so the field holds the date its *successor*
  took effect — not the last day it applied. Merit-badge and rank editions had been closing on the
  last day (`2023-12-31` before a `2024-01-01`) while adventure editions closed on the successor's
  start (`2024` before a `2024`): 253 abutments in the old style against 83 in the new. Owner
  decision; consumers can now write one `which edition applied on date D` predicate against every
  subject.
- **The schema never said which, which is how two conventions grew in one dataset.** It says so now,
  and `tools/requirement_windows.py` holds the rule as a single function both history generators
  apply to the documents they own — so the fix survives regeneration rather than being a one-time
  sweep over data.
- **The loose gate is what let them coexist.** `validate_data.py` demanded only "no overlaps, no
  multi-year gaps", which both styles satisfied. It now requires exact abutment; proven by
  injection against the old style, a gap and an overlap.
- Checked the 2025 printing of *Scouts BSA Requirements* (No. 33216) against our in-force 2024 rank
  sets: Eagle requirement 3 is substantively identical (`must choose only one` → `may choose only
  one`, one comma), so the 2024 editions stand and no 2025 edition is seeded.

## 0.49.0 (minor) — 2026-07-27

- `665a843` **Positions of responsibility are entities: 29 of them, and the rank requirements now
  resolve to them.** Star, Life and Eagle each listed ~35 positions across three unit types inside a
  single sentence. Those sentences are now `choose: 1` trees — pick a unit type, then a position —
  with **104 `position:` refs** across the three ranks, a `positions` dataset at
  `v1/positions/{id}.json`, and a `rank_positions` SQLite junction.
- **The edge is the point, because it is not symmetric.** Bugler counts for Star and Life and *not*
  for Eagle, which is exactly the kind of rule a flat list cannot express. Acceptance therefore
  lives on the rank's requirement-set, never on the position, and "counts for Star but not Eagle"
  is now one query returning `['Bugler']`. The gate is deliberately one-directional for the same
  reason: demanding every rank list every position would forbid the real rule.
- Derived from the requirement text itself rather than hand-typed, so a reissued requirements book
  changes the catalog by re-running the tool. That is how the Bugler asymmetry was found — by
  diffing the three lists, not by knowing it in advance — and it also caught that Star and Life
  offer a Scoutmaster-approved leadership project as a fourth alternative where Eagle does not.
- New `position` schema and `position-unit-types` vocab. **`crew_or_ship` is deliberately one code:**
  the requirement prints a single "Venturing crew/Sea Scout ship" heading over one list, and
  splitting it would assert a distinction the source does not make. Six positions (Den Chief,
  Quartermaster, Historian, Chaplain Aide, Outdoor Ethics Guide, Webmaster) appear under both
  headings. `audience` is `youth` throughout and exists so adult roles can be added later without a
  breaking change; they are a separate unpublished catalog and are not here.
- Lone Scout stays prose. The requirement offers "leadership responsibility in your school,
  religious organization, club, or elsewhere in your community" — that is one alternative described
  in words, not a list of positions, and splitting it on commas would have invented four.
- 4 gates proven by injection: a position listed under a unit type it does not claim, a position no
  rank offers, a dangling `position:` ref, and an unregistered unit-type code.

## 0.48.0 (minor) — 2026-07-27

- `5f1caf4` **The Eagle merit-badge requirement is a graph now, not a paragraph.** Requirement 3
  named its 14 lettered slots — three of them either/or — inside one 600-character string, so the
  only countable thing in the dataset was the 18 badges flagged `eagle_required`. A tracker
  therefore reported **"6 of 18"** where a Scout owes **6 of 14 slots**. Requirement 3 now carries
  14 children: eleven leaves with a `ref` to a merit badge, and three `choose: 1` option groups
  (Emergency Preparedness/Lifesaving, Environmental Science/Sustainability,
  Swimming/Hiking/Cycling), using the same `ref` mechanism the Cub rank trees use for adventures.
- ⚠ **`eagle_required` was not wrong, it was underspecified — so it is untouched.** The flag marks
  membership of the required *list*, and 18 is the number Scouting America itself uses: Star and
  Life requirement 3 both say "any of the **18** merit badges on the required list for Eagle." The
  slot count is 14. Both facts are real and a tracker needs both, so this adds structure rather than
  redefining a published field.
- New `tools/seed_advancement_graph.py` + `tools/advancement_graph.json`. Idempotent, and hooked
  into `seed_rank_requirements.py` so regenerating from the source PDF — which contains only the
  flat prose — cannot silently drop the structure. Every badge name placed in the tree is verified
  to appear in the verbatim requirement text it claims to structure, so a drifting slot table
  refuses to apply.
- New gates, all proven by injection: the slot tree must exist at all; its slot count must equal the
  number requirement 3's own text states ("these **14** merit badges"); every badge it refs must be
  flagged; and every flagged badge must occupy a slot.
- **The flag check had to be made temporal, and that is not a technicality.** Comparing against
  today's flags failed immediately on Citizenship in Society: it is slot (d) of the in-force 2024
  requirements and was Eagle-required from 2022 until Scouting America discontinued it on
  2026-02-27, so it carries no open version to flag. The comparison now runs **as of the
  requirement-set's own effective date**, which is the only reading under which the two records
  agree.
- ⚠ Which surfaces a real gap, recorded in `TODO.md`: **our in-force Eagle requirements still
  require a badge that no longer exists.** Scouting America has presumably reissued them; we do not
  have that edition.

## 0.47.1 (patch) — 2026-07-27

- `4730af3` **The three 2025 merit badges now carry their introduction year.** Artificial
  Intelligence, Cybersecurity and Multisport had `valid_from: null` — unknown — and are now dated
  **2025**, confirmed by the project owner and corroborated by the ranking series shipped hours
  earlier: each appears in 2025 and in no earlier year, and Scouting America's 2025 recap gives all
  three the 999 "no prior rank" sentinel for 2024.
- **This closes a gate that could not previously bite.** 0.47.0 noted that "a badge ranked before it
  existed" needed a synthetic two-file injection to prove, because no badge in the dataset started
  after 2021. With real start years present, ranking Cybersecurity in 2024 is now caught by a
  single-file injection against unmodified data — the check went from provable to load-bearing.
- Recorded as `curated` with the basis stated on the record rather than left as a bare date, since
  the source that suggested the year (a sentinel meaning "no rank") implies a first-offered year
  without stating one.

## 0.47.0 (minor) — 2026-07-27

- `458f3c2` **Merit badge popularity by year: 5 years, 692 badge-year ranks, every year a complete
  1..N.** New `merit-badge-ranking` dataset — one immutable document per year at
  `v1/merit-badge-rankings/{year}.json` — covering **2021-2025**, plus a `merit_badge_rankings`
  SQLite table shaped one row per badge per year so a trend query is a single join. The longitudinal
  series existed nowhere machine-readable.
- ⚠ **The backlog asked for earned-COUNTS. Scouting America does not publish them.** Its annual
  recap (On Scouting, from the national Scouts BSA director) gives each badge a *position* and no
  absolute number anywhere. So the dataset says what it is — `metric: "earned_rank"` — and the
  schema pins that: a document claiming `earned_count` is rejected by contract, with a negative
  fixture, because a consumer who mistook a rank for a volume would invent conclusions the source
  never supports. The gap between rank 1 and rank 2 is unknowable from this source.
  - (A false lead worth recording: the posts *do* contain strings like `124,186`. They are CSS
    values — `--wp-admin-theme-color--rgb:0,124,186`. Grepping raw HTML for comma-numbers finds a
    stylesheet, not data.)
- Each post also publishes every badge's **previous-year** rank, which is what makes 2021
  recoverable and gives 2022 and 2024 a second independent source. Those overlaps are compared at
  extract time: **2024's 135 shared badges agree exactly**, and 2022 has four discrepancies where
  the year's own post — its primary publication — wins and the disagreement is recorded on the
  document itself.
- **One source typo repaired on evidence, not preference.** The 2022 post prints rank 130 twice
  (Composite Materials, Journalism) and omits 135; the 2023 post puts Journalism at exactly 135. A
  duplicate plus a gap that a second source resolves precisely is a typo, so the correction is
  applied and recorded in `provenance.notes`. Without it, 2022 would have shipped a knowingly broken
  ranking.
- Three traps in the source, all handled: **999 is a sentinel**, not a rank — the 2025 post gives
  Artificial Intelligence, Cybersecurity and Multisport a "2024 rank" of 999 because they did not
  exist, and importing it literally would rank them below every real badge; **footnote markers ride
  in names** ("Hiking\*\*"); and **renames appear mid-transition**, so names map to slugs through an
  explicit alias table.
- **The temporal gate earned its place immediately.** Requiring that a ranked badge existed that
  year caught three silent mis-mappings: normalising names collapses "Leather Work" (1911-1951) into
  today's "Leatherwork", "Life Saving" (ended 1959) into "Lifesaving", and the 1911 "Aviation" into
  the modern one, so a retired badge won on glob order. Current badges now win a normalised-name
  collision. It also caught the 2022 post still printing "Medicine" two years after that badge
  became Health Care Professions.
- 8 gates proven by injection: duplicate rank, duplicate badge, a gap while claiming `complete`,
  dangling ref, ranked-before-it-existed (needed a two-file injection — no badge in the data starts
  after 2021), ranked-after-retirement, year/id mismatch, and `metric` claiming counts.
- Sanity check against the source's own headlines: **golf +48 and sustainability +36 from 2021 to
  2025** are exactly the climbs the 2024 post led with; public-health falls 63 places as the
  2020-21 spike recedes.

## 0.46.1 (patch) — 2026-07-27

- `bd07760` **Swept the rest of the population 0.46.0's spot-check pointed at.** Exactly **7 camps**
  carried the provenance marker *"Some codes are retained from the original camp-finder import and
  were not re-confirmed by this survey"* — Baker and Parsons (fixed last release) plus Baldwin,
  Melakwa, Sheppard, Fire Mountain and Camp Kenya. They are the Pacific-Northwest set camp-finder
  built first, and camp-finder's own notes say what they were: **"Fixture data for frontend
  development; not a live scrape"** (Baldwin) and **"Deliberately stale verified_at to exercise the
  StaleBadge UI state"** (Melakwa) — recorded as `method: manual, confidence: 1.0`, which reads
  authoritative and was never meant to.
- **5 unsourced codes removed**, each absent from every reachable page: `cope` + `stem` from Baldwin
  (checked across ~45 KB of Cascade Pacific content including `/summercamp/`), `cope` + `stem` from
  Sheppard (~69 KB of Chief Seattle content), `cope` from Melakwa. Feature entries 6,385 -> 6,379.
  Generic amenities were deliberately **kept**: these pages are stubs, so silence about a dining hall
  is not evidence, while silence about a COPE course on a page that lists facilities is.
- ⚠ **I removed a real feature and put it back the same day.** Fire Mountain lost
  `mountain_biking` because I read the council's stub landing page — one step after writing the
  lesson that *"I read a camp page" is not "I read the right camp page"*. Its resident-camp page,
  **already cited in its own provenance**, states the programme outright: "COPE/Climbing (newer High
  COPE and 1000+ foot tandem zipline) ... Mountain Boarding and Mountain Biking". Only `stem` was
  genuinely unsupported there. That page also vindicates the survey: `cope`'s note ("A high COPE
  course") was accurate, and `aquatics`/`cowboy_action_shooting`/`paddleboarding`/`zip_line` all
  trace to that one sentence.
  - The audit tool caught my error because it reports **omissions as well as unsupported claims** —
    it flagged `mountain_biking` as a candidate miss immediately after I deleted it. An audit that
    only hunts false positives manufactures false negatives.
- **Two broken source URLs fixed**, both of which explain thin surveys: Melakwa's
  `otcbsa.org/camp-melakwa` is dead (the camp is still live — Pacific Crest's camping index
  describes it), now `pccscouting.org/camping/`; Fire Mountain's `mountbakerbsa.org/fire-mountain`
  redirects to an unrelated *Cub-and-Me* carousel, now `mountbakerscouting.org/firemountain/`.
- **Camp Kenya's provenance contradicted itself** — the same note said camp-finder "never captured
  this overseas camp" *and* that codes were retained from the camp-finder import. The retention
  sentence was pasted boilerplate; removed. Its features are hand-curated, so no codes were touched.
- Baker's and Parsons' stale retention boilerplate replaced with what actually happened to them, so
  the marker now appears on **zero** camps and means something when it reappears.

## 0.46.0 (minor) — 2026-07-27

- `687e7c4` **Two camp feature defects found by a user spot-check, traced to their origin, and
  fixed — plus `tools/audit_camp_features.py`, which would have caught both.** Camp Baker loses
  `mountain_biking` and `pool`; Camp Parsons gains its ATV program and 10 more features (11 -> 22).
  Feature entries 6,373 -> **6,385**.
- **Camp Baker's `mountain_biking` was never sourced — it was an LLM guess that got laundered into
  looking verified.** camp-finder's record for Baker was `method: llm_extraction`, confidence 0.82,
  with a provenance note saying in as many words: *"features inferred"*. It is the **only camp in
  camp-finder's entire 486-camp dataset with a speculative feature claim** — of its 391
  `llm_extraction` camps, 390 carried no features at all. That single record was imported verbatim;
  the 2026-07-25 camp-page survey then rewrote Baker's list, added 23 page-attested features, and
  stamped the whole record `features_source_tier: camp_page` / `features_verified_at: 2026-07-25`
  — so an admitted inference ended up indistinguishable from page-verified fact. **A survey that
  only adds cannot re-verify what it inherited.**
  - The same inferred record also gave Baker a `pool`. The spot-check caught the biking; checking
    the rest of that record caught the pool. The camp is on a Siltcoos Lake peninsula and its page
    never says "pool" — swimming, Mile Swim and lifesaving all happen at the waterfront.
  - Also dropped the `otcbsa.org/camp-baker` source: it 301s to the `pccscouting.org` page already
    cited, so two "independent" sources were one page. Added `pioneering`, `orienteering` and
    `wilderness_survival`, which that page names and the record omitted.
- **Camp Parsons' missing ATV program was a survey that stopped at the front door.** Every source
  ever consulted for this camp was an index page — camp-finder used the council page
  (`seattlebsa.org`, `method: manual`), and our survey added `scoutingseattle.org/camp-parsons/`
  and `campparsons.org/` — none of which mention ATVs. The programme lives at
  **`campparsons.org/program/`**, 10 KB with its own `<h3>` per activity, never fetched. Added from
  it: `atv` (signature — a BSA ATV Safety Program with rider-course certification),
  `snorkeling`, `kayaking`, `scuba`, `rappelling`, `bouldering`, `hiking`, `museum`,
  `first_year_program`, `scoutcraft`, `nature_study`. `features_source_tier: camp_page` was true and
  useless: it records that *a* camp page was read, not that the right one was.
  - Not added: `golf`. The page's "Parsons Open Whiffle Ball Golf Tournament" is a whiffle-ball
    game, and `trading_post`/`leadership_training` matched only the council-wide page, not this
    camp's.
- **New `tools/audit_camp_features.py`** — fetches each camp's cited sources plus program pages they
  link to, and reports features with no lexical trace, vocabulary terms the pages name but the
  record omits, and program pages provenance never cites. Uses the vocabulary's own `aliases` (it
  already knew `muzzleloading` -> `black_powder`) and its `broader` hierarchy, so a page saying
  "Climbing" over a tower already recorded as `climbing_tower` is not reported as an omission.
- ⚠ **Report-only by design, and the tool proves why on its own test cases:** it flags `rappelling`
  where the page says "the final rappel", cannot confirm or deny all-generic terms like
  "Older Scout Program" (reported as *not lexically checkable*, never as a defect), and would
  cheerfully "find" `golf` in a whiffle-ball tournament. It also concatenates a camp's sources, so a
  council-wide page can appear to attest something true of a different camp — the same
  source-to-subject slippage that produced both defects. Every line is a lead for a human.

## 0.45.0 (minor) — 2026-07-27

- `49f70b0` **The pre-2024 Cub adventure line-up is recorded: 38 retired adventures added, 121
  historical requirement editions, 951 requirement nodes.** The 2024 program replaced the line-up
  wholesale and until now none of that was in the dataset. Of the 92 adventures the 2015-2024
  program ended with, **50 carried into 2024 unchanged, 4 under a tidied name, 3 were renamed
  substantively, and 35 were dropped.** `v1/adventures/index.json` goes 139 -> **177** (139 current
  + 38 historical) and requirement-sets 546 -> **667**.
- **The dataset can now answer "what did a Wolf have to complete in 2019?"** — Call of the Wild,
  Council Fire (Duty to Country), Duty to God Footsteps, Howling at the Moon, Paws on the Path,
  Running With the Pack — versus 2025's Bobcat Wolf, Council Fire, Footsteps, Paws on the Path,
  Running With the Pack, Safety in Numbers. Editions per adventure: 110 carry one, 35 two, 24 three,
  every chain contiguous and `supersedes`-linked.
- Source is the U.S. Scouting Service Project archive (usscouts.org), which still serves the old
  program including two archived elective editions. Dates come from each page's own
  `revision-date` region, never inferred: core adventures and all Lion revised **2018-09-01**,
  Tiger/Wolf/Bear/Webelos-AOL electives **2022-06-01**. **15 adventures were retired in 2022 rather
  than 2024** — present in the archived 2018 elective edition, absent from the 2022 one — and their
  windows close accordingly; several pages say "To be retired on May 31, 2022" outright.
- 38 lifecycle events: 35 `discontinued`, and 3 `superseded` for the substantive renames
  (`duty-to-god-footsteps -> footsteps`, `duty-to-god-in-action -> duty-to-god`,
  `fellowship-and-duty-to-god -> fellowship`). Modelled as separate entities plus an event rather
  than one renamed entity, exactly as merit badges record `computers -> digital-technology`:
  asserting a single identity would fabricate continuity the source never states. Only pure
  annotation drops (`Council Fire (Duty to Country)` -> `Council Fire`) become a version window on
  one entity.
- New optional **`requirement-set.completion_rule`** (additive), on 66 of 252 adventure editions:
  the source's own statement of how many requirements are needed, verbatim — "Complete Requirements
  1-4 plus at least one other". ⚠ Deliberately prose, not structure: the old pages phrase this **44
  different ways**, and converting them into `choose` trees would risk publishing requirements
  Scouting America never demanded. Publishing the list *without* the rule would be worse — six
  listed requirements would read as six obligations. A gate checks every number the rule cites
  actually exists, which is what would catch a truncated requirement list.
- Two gates were rescoped rather than weakened, because both describe the **current** program: the
  area pairing rule (the six areas are a 2024 construct, so pre-2024 required adventures correctly
  have none) and the rank-tree reachability rule (a rank's requirement-set is today's structure; a
  retired adventure carries its own rank association). Version windows now record only *attribute*
  changes — where an adventure's name, rank and category never moved, its single window simply
  starts in 2018 and the requirement editions carry the revision history, instead of a second
  window asserting a change that never happened.
- ⚠ **Fixed a fidelity bug in the extraction before shipping it:** the heading normaliser was also
  applied to requirement text, stripping sentence-final periods — only 7% of historical nodes ended
  in punctuation against 100% of the 2024 ones. Text published as verbatim © Scouting America must
  be exactly that; now 95%, with footnote asterisks and tag-removal gaps ("Whittling Chip ." )
  repaired. Zero of 1,562 nodes carry markup residue and zero colon-terminated nodes are missing
  their sub-list.
- New gate: **requirement-set editions of one subject must form an unbroken line** — no overlaps,
  no multi-year gaps, no open edition mid-chain. This was verified by hand for the merit-badge
  history and never enforced; a hole would silently answer "which requirements applied in 2020?"
  with nothing. 12 gates proven by injection this release.

## 0.44.0 (minor) — 2026-07-27

- `81b7181` **The six Cub requirement areas are now data: every rank's six required adventures
  carry the area they fill, and the pipeline proves each rank fills all six exactly once.** This is
  what turns the adventure list into an advancement tracker — "which of your six required slots are
  still open" becomes a group-by instead of a list diff. The same set of areas exists at every rank
  while the adventure filling it changes: Citizenship is `King of the Jungle` for a Lion and
  `Council Fire` for a Wolf.
- New optional `adventure.area` (additive) + `data/vocab/adventure-areas.json` (6 terms):
  `character_leadership`, `personal_fitness`, `personal_safety`, `family_reverence`, `citizenship`,
  `outdoors`. `null` for electives — an elective fills no area — and published in
  `v1/current/adventures.json`, the per-entity docs, and the SQLite `adventures` +
  `adventure_ranks` tables, so the whole question is one `GROUP BY`.
- **Areas come from the CMS, not from reading the page layout.** Each required adventure renders as
  a loop-item whose class list carries `cs-adv-rank-<rank> cs-adv-type-required
  cs-adv-topic-<area>`, so the pairing is read off the card the heading lives inside. Pairing by
  print order would have been guesswork — Bear prints its areas in a different order than Wolf —
  and 5 of the 6 areas come straight from those classes. The sixth is Bobcat's
  (`character_leadership`), a hand-built callout on all six rank pages, read from its label.
- **This closes the loop on the 0.43.0 Arrow of Light bug.** Two AOL adventures are *named* after
  areas — "Personal Fitness" and "Citizenship" — which is exactly why an earlier seed captured
  printed area labels as adventures and shipped seven required entries covering five areas. The
  real mapping is now explicit: `personal_safety → First Aid`, `family_reverence → Duty to God`,
  `outdoors → Outdoor Adventurer`.
- 9 new gates, each proven by injecting the drift it catches: area code not in vocab; a required
  adventure with no area; an elective claiming one; two required adventures claiming the same area;
  an area moved onto a rank that already fills it; and four published-contract probes. The
  published `category`/`area` fields are now **pattern-constrained to vocabulary codes**, which
  closed a real hole — `current/adventures.json` would previously have published the label
  `"Personal Fitness"` where a code belongs, re-creating the very confusion above. A negative
  fixture pins that shape.

## 0.43.0 (minor) — 2026-07-27

- `eb963cd` **Cub Scout adventures are a first-class dataset: 139 entities and 611 requirements,
  the unit of Cub advancement.** Adventures are to Cub Scouts what merit badges are to Scouts BSA —
  a rank is earned by completing six required adventures plus any two electives, and each adventure
  carries its own requirements — so they get identity (`data/adventures/<slug>.json`), their own
  requirement-set editions, and `v1/adventures/{id}.json` endpoints. Requirement content now lives
  once, on the adventure.
- New `schema/v1/adventure.schema.json`, `data/vocab/adventure-categories.json` (3 terms) and
  `tools/seed_cub_adventures.py`. Slugs are each page's own `rel=canonical` slug rather than a
  slugified name, so they match Scouting America (`pick-my-path-lion`, `bobcat-aol` — whose rank-page
  link redirects, which is why the page's canonical wins). Requirement-set ids are prefixed
  `adventure-` because five adventures share a name with a merit badge (Swimming, First Aid, Cycling,
  Fishing, Personal Fitness) and requirement-set ids are one flat namespace: `swimming-2024` was
  already taken.
- **131 of 139 adventures carry published requirements.** The 8 that do not are the shooting sports
  (Archery ×6, BB Guns, Slingshot), which are listed on every rank page but have no page of their
  own — "only ... at approved events with qualified instructors". They exist as entities with a null
  `url` and no requirement-set, which is the honest shape; join
  `v1/requirement-sets/index.json` on `subject` to find the ones with requirements.
- **Three corrections to already-published Cub rank data**, all caught by diffing our trees against
  the official rank pages:
  - Arrow of Light listed **three adventures that do not exist** — `Personal Safety`,
    `Family & Reverence` and `Outdoors`. Those are the page's *area* labels, captured as if they were
    adventures; the real required adventures are `Duty to God` and `Outdoor Adventurer`. AOL had 7
    required where the rule says six.
  - The rank rule is "**six** required Adventures and any two elective" — so Bobcat genuinely is the
    sixth required adventure, not an extra. (An earlier read of the page, which lists only five under
    the heading and links Bobcat separately, suggested our data was wrong here. It was right.)
  - Shooting sports were folded into the ordinary elective list; they are now in the elective pool
    with `category: special_elective` carrying the constraint.
- Requirement nodes gain an optional **`ref`** (additive): a node standing for another entity now
  points at it (`adventure:paws-on-the-path`) instead of being matched on name. The Cub rank trees
  are pure structure — two groups, `choose: 2` over 20 electives, every adventure a ref — and
  Bobcat's requirements are no longer duplicated into all six ranks.
- ⚠ **Deliberately did not model the elective split as a third rank group.** The page shows
  "Special Elective Adventures" as a peer heading, but a peer group here needs `choose: null`, which
  this schema reads as *all children required* — i.e. every Cub must earn BB Guns to rank up. The
  split is a property of the adventure, so it lives on `adventure.category`, and the rank states the
  two groups its own rule states.
- New gates, each proven to fire by injecting the drift it is meant to catch (13 injections, 13
  caught): adventure↔rank agreement in both directions, category-versus-group, orphan adventures,
  dangling `ranks` and node `ref`s, category vocab, and the four published-projection contracts.
  `adventure_ranks` junction table in the SQLite artifact answers "which adventures does a Wolf
  need" in one query.

## 0.42.2 (patch) — 2026-07-27

- `9057232` **Identity decision recorded: the base URL stays `sethmay.github.io/open-scout-api` for
  now, and 1.0 stays deliberately UNCUT while a permanent home is negotiated.** Docs only.
- ⚠ **Why 1.0 is not being tagged even though everything else is cleared.** 1.0 is the promise that
  `v1` is additive-only forever — no renames, no removals, safe to pin. That promise attaches to the
  base URL, which is also the schema `$id` prefix. Freezing it onto a host we already intend to move
  would break the promise on purpose the first time the move happens, which is strictly worse than
  not having made it yet. The tag is now waiting on one external decision and nothing else.
- README gains an explicit pre-1.0 caveat, because consumers read it before deciding how to pin:
  field shapes are stable and build-gated, but the **host is provisional**; resolve endpoints from
  `v1/meta.json` (`base_url`, `schemas`, `endpoints`) rather than hardcoding the host, and pin data
  files by git tag via jsDelivr, since tags stay immutable wherever the repo ends up.
- The move remains cheap and rehearsed whenever the home lands: one
  `tools/restamp_identity.py --api-base … --repo …`, a rebuild, a CHANGELOG entry and a tag. Zenodo
  stays deferred for the same reason — the DOI record binds to the final GitHub location, and
  `.zenodo.json` is already written and correct.
- Recorded preference for when the choice reopens: a **custom domain**, the only option that makes
  the published identity independent of GitHub so a later account-or-org move is invisible to
  consumers rather than another breaking change.

## 0.42.1 (patch) — 2026-07-27

- `87c7a51` **New `tools/restamp_identity.py`: the last 1.0 blocker is no longer a one-way door.**
  The API base URL is the schema `$id` prefix, the documented API root and the jsDelivr pin path, and
  it appears in ~1,900 files — which is what made "decide the permanent home" feel irreversible. It
  is one command, and the tool proves it rather than asserting it. No data or schema changes.
- Moves the two identities **independently**, which is the point: `--api-base` (the published root
  every `$id` hangs off — make it a custom domain and it need never change again, even if the repo
  moves) and `--repo owner/name` (source links, tool User-Agent strings, the Zenodo
  related_identifier). Reads today's values out of `build.py` instead of hardcoding them, dry-runs by
  default, and after `--apply` verifies zero stale references survive.
- Deliberately scoped so unrelated things stay put: `.zenodo.json` `creators` is untouched
  (authorship is a person, not a host), and the README's link to `github.com/<owner>/camp-finder`
  does not follow this repo's move — the substitution matches the full `owner/repo` string, not the
  bare owner name.
- **Verified by a full round trip, not by inspection:** re-stamped to a throwaway identity;
  `validate_data`, `build`, `build_sqlite` and `validate_examples` all passed; every published
  surface moved (`meta.base_url`, `meta.schemas`, every collection and per-entity `$schema`, the
  SQLite `source` row); then re-stamped back and confirmed **byte-identical to HEAD** across all
  1,919 files.
- `TODO.md` now frames the remaining decision as the durable-vs-convenient choice it actually is —
  custom domain (identity stops depending on GitHub), GitHub org (free, still coupled), or stay put
  — rather than as a naming question.

## 0.42.0 (minor) — 2026-07-27

- `10ae3ff` **Discontinued merit badges: the catalog goes 142 → 268 entities**, adding 126 retired
  badges back to the 1910 originals — Signaller, Ambulance, Angling — from the USSSP merit badge
  history table. Until now the catalog held 140 current badges and exactly two historical ones, so
  "what happened to the Signaling merit badge" was unanswerable. New
  `tools/seed_discontinued_badges.py`.
- **The parse validates itself before writing anything.** The source marks retired badges in its own
  markup (`class="red"`), so status is read rather than inferred from dates; and the page's *non*-red
  rows must equal the 140 current badges we already hold, after normalising `&`/`and` and hyphen
  spelling. A count mismatch aborts the run, because it means the table shape moved. It matched
  exactly, which is what made the other 126 rows trustworthy.
- **Badge lineage is now an event graph — 61 `superseded` events, badge events 2 → 128.** Built from
  the table's own notes ("Became Fishing", "Formerly Business"), each link emitted once though the
  table states it from both sides, using the event vocabulary's documented mapping for this domain
  ("badge replaced by a new badge → superseded"). Chains walk end to end:
  `clerk → business → american-business`, `first-aid-to-animals → veterinary-science →
  veterinary-medicine`, `mining → rocks-and-minerals → geology`, `seaman → seamanship →
  small-boat-sailing`. Badges that simply ended get a plain `discontinued` event (67 of them).
- ⚠ **`eagle_required` is now `boolean | null`** in `merit-badge.schema.json` and
  `published-index.schema.json`, where **null means UNKNOWN, not false**. It cannot be sourced for
  badges retired before the modern published Eagle list, and 126 fabricated booleans would have been
  worse than an honest gap. `published-current.schema.json` is deliberately **untouched**: only
  entities with an open version reach `current/merit-badges.json`, and all 140 of those carry a real
  boolean. This is a type widening on the *index*, so a consumer doing a strict boolean check there
  must handle null; truthiness checks are unaffected.
- Two enrichments fell out of the same table: a new **`bsa_number`** on badge versions (BSA's
  internal recordkeeping number, only assigned from around 1986, so early badges have none), and
  **introduction years backfilled onto 136 current badges** whose `valid_from` was null. For a
  renamed badge that year is when THAT name took effect — American Business 1967, formerly Business
  — which is exactly the version-window semantic rather than the start of the lineage.
- Deliberately not modelled: the 17 "Formerly part of X" rows (Aerodynamics and friends carved out of
  the 1911 Aviation badge) stay as prose, because a `split` event requires the predecessor closed and
  X is usually still a live badge. The 1911 Aviation badge itself IS captured, as `aviation-1911`,
  since a *new* Aviation badge reused the name in 1952 — the generator disambiguates a reused name by
  start year rather than dropping the row.
- Source caveat recorded in `TODO.md`: the page predates Artificial Intelligence, Cybersecurity and
  Multisport, and still lists Citizenship in Society and Computers as current. Our records are right
  on all five; they must not be "corrected" from this table.

## 0.41.0 (minor) — 2026-07-27

- `f49b219` **Every published endpoint is now schema-pinned and build-gated — 1,774 files, nothing
  left unpinned.** The last 10 surfaces had no contract at all: `v1/meta.json`,
  `v1/{dataset}/aliases.json`, and the 8 per-entity `v1/{dataset}/{id}.json` families (**1,756
  files**). Their shape existed only inside `build.py`, so renaming `events` was a one-line edit no
  gate would catch — on the surface that just became the richest, since per-entity documents are the
  only place a camp feature's prose `note` and a badge's full requirement history appear.
- Three new contracts:
  - **`published-entity.schema.json`** — kind-selected across versioned entities, versioned entities
    that also carry `requirement_sets`, and effective-dated requirement documents. It pins the
    **envelope and the projection** — `versions` non-empty, lifecycle `events` folded in under that
    exact key with resolved participant refs, `requirement_sets` listing every edition of a subject
    as bare slugs — and deliberately does not restate each `version`'s interior, which
    `validate_data.py` already validates against its canonical schema before the build runs.
  - **`published-meta.schema.json`** — the discovery document, where `endpoints` and `vocab` are the
    machine-readable index of the whole API. `unofficial` is `const: true` and required, so a
    consumer cannot lose the no-affiliation fact by reading a subset of the document.
  - **`published-aliases.schema.json`** — the `{retired-id: surviving-id}` map, pinned as a bare
    lookup via `propertyNames` rather than wrapped in an envelope, which would have been a breaking
    shape change to the one file whose only sane use is a direct lookup.
- **A licensing invariant is now enforced on the published surface, not just inferred:** a document
  with `includes_official_text: true` MUST carry `text_rights`. Verbatim requirement text is
  © Scouting America and sits outside this dataset's CC licence, so it can no longer be published
  without the carve-out recorded on the document itself.
- Per-entity documents and `meta.json` now stamp `$schema` like every other published file, which
  realises an intent already commented in `build.py` ("dist files reference published schemas") but
  never achievable while no such schema existed. The alias map is the one exception and stays a bare
  map: a `$schema` key there would read as an alias entry, and its contract rejects it.
- Verified non-vacuous by injecting seven kinds of drift into the build, all rejected: renaming
  `events`, dropping `requirement_sets`, emitting `requirement_sets` as `kind:slug` refs instead of
  slugs, an entity with zero versions, `meta.json` losing `unofficial`, a non-slug alias value, and
  stripping `text_rights` from a document carrying official text.

## 0.40.0 (minor) — 2026-07-26

- `b7829b5` **Merit badge requirement history: requirement-sets go 188 -> 415, and 131 of 141 badges
  now have more than one edition** (96 have three). Before this, `supersedes` chains existed for
  ranks but not badges, so "which requirements applied when my Scout started" was unanswerable for
  the entire badge catalog. Editions now span **1995 to 2026**, with full verbatim requirement trees,
  effective windows, and `supersedes` chains. New `tools/seed_merit_badge_history.py`.
- **The source is better than scraping archives.** usscouts.org mirrors official requirements per
  badge at `/mb/mbNNN.asp` *and* keeps the preceding edition at `/mb/Old/mbNNN-YY.asp`, each page
  declaring its own revision type and effective date in a Dreamweaver editable region — so editions
  are dated from the source, not inferred. Two recoverable historical editions per badge, because
  usscouts' "current" page usually trails the newest booklet that OpenScouting/workbooks tracks
  (Chemistry: our 2025 edition, usscouts' 2024, and its archived 2020).
- **Editions are identified by TEXT, never by claimed date.** 30 scraped editions were dropped as
  duplicates of something already held, and the label a page gives itself is not trusted: where a
  scraped edition claimed a year another edition already occupied, the older claimant was dropped
  rather than given an invented date, since same-year-different-text means one of the two labels is
  wrong and the source cannot say which.
- Three revision-chain invariants are now build-gated, all proven by injection: **no edition
  supersedes itself**, **two editions of one subject cannot share an `effective_from`** (ids are
  `<subject>-<year>`, so a collision would silently overwrite one), and **a subject has at most one
  open edition** — and must have one unless the subject itself is retired. All three caught real
  bugs in the first generation pass: Cycling emitted a set that superseded itself and left two open
  editions, because both of its scraped editions claimed 2023.
- Requirement text remains © Scouting America under the existing `text_rights` carve-out
  (`includes_official_text: true`), exactly as for ranks and the current sets. `method: scraped`,
  confidence 0.8; the generator caches fetches so re-runs are deterministic and polite to a
  volunteer-run site.
- Known gaps: Geology's archived page 404s, 10 badges still have a single edition (mostly badges
  created recently enough to have no prior edition), and the 30 same-year drops are worth a manual
  look — recorded in `TODO.md`.

## 0.39.0 (minor) — 2026-07-26

- `d0cf809` **Every merit badge now has a description and subject tags** — they were `null` and `[]`
  on all 140, which was the most visible hole in the dataset: any app listing badges had nothing to
  show and no way to filter. Descriptions are original prose, 24-38 words (median 33), written from
  each badge's own requirement tree; `tags` carry 1-3 facets from a new **16-term
  `merit-badge-tags` vocabulary** (218 applications, every code in use). `description` is now
  emitted in `current/merit-badges.json` and **required** in `published-current.schema.json`;
  `tags` already was.
- **The copyright gate is the interesting part.** Requirement text is © Scouting America and is
  published only under the narrow `text_rights` carve-out on requirement-sets, so a description that
  quoted it would silently drag copyrighted wording into the CC-licensed part of the dataset.
  `validate_data.py` now **rejects any description sharing 8+ consecutive words with its own badge's
  requirement text**, building the n-gram corpus from the union of every requirement set for that
  badge. Proven by injection alongside two companion guards: badge `tags` must exist in the
  vocabulary, and descriptions must pass the same evergreen check as camp summaries.
  - The four writing agents went further than asked and probed at 7 and 6 words as a *margin* check.
    That caught five descriptions that passed at 8 but had tracked a requirement's clause and
    swapped a word — the exact failure the rule aims at. Worst shared run in the shipped set is 5,
    and every one of those is unavoidable domain vocabulary ("plaited coiled ribbed and wicker").
- Four descriptions were rewritten by hand after the wave: they were the worked examples in the
  authoring brief, and one agent honestly flagged that it had shipped the brief's sentence rather
  than writing its own. Replaced with prose derived from the requirements.
- Housekeeping: `TODO.md` had two entries stale for several releases — GitHub Pages is enabled and
  the API verified live (`v1/meta.json` returns 200 at the current release, all 48 tags on the
  remote), and camp `summary` shipped long ago on 371 of 448 camps.

## 0.38.0 (minor) — 2026-07-26

- `cae518b` **The "unsurveyable" 62 were an instrument error, not a data limit. All 62 surveyed;
  non-day coverage 79% -> 95%** (366 of 384), feature entries 4,609 -> **6,373**. Four agents,
  **1,752 features, 49 `guide` + 13 `camp_page`, zero `portal`, zero untouched, zero invented
  codes.**
  - **I retract 0.37.0's "cheap automation is exhausted for the 62".** Reading a
    `scoutingevent.com` URL without a selector follows a redirect to an empty "you have not selected
    a calendar" shell; **the same URL with `:raw` returns the real page including the camp's prose.**
    Two automated passes and my own 12-camp spike all mistook that shell for the camps' content.
    When an entire population looks uniformly empty, suspect the instrument first.
  - Also decisive: Black Pug's council-authored per-camp facility inventories at
    `campreservation.com/<org>/Camps/<id>` outlive their registration event keys, and guidebooks
    hidden behind Google Drive redirects yield to a curl-to-temp-`.pdf`.
- **New `features_source_tier` on every camp (`guide` / `camp_page` / `portal`, null iff
  `features_verified_at` is null)** — a completeness qualifier in the same spirit as
  `geo_precision`, published in `current/camps.json` and pinned in `published-current.schema.json`.
  It earns its place: `guide` camps average **21 features against 13** for `camp_page`. Derived
  mechanically for the 304 pre-existing surveys from which provenance sources carry an `accessed`
  date, biased so `guide` is never over-claimed. `validate_data.py` enforces the coupling.
- **Two 2026 council mergers resolved, replacing placeholder dead-ends.** South Plains + Golden
  Spread merged on 2026-06-01 into the new **Prairie Sky Council** (created; `bsa_number` left null
  because no source states the merged council's number, and `hq_city` null because the sources
  record it as undecided). Redwood Empire was **absorbed** by Golden Gate Area Council, which kept
  its identity and runs it as the Redwood Empire Service Area. Both were previously `discontinued`
  with no successor. Five camps repointed; the orphaned-council count is now **0**.
- Vocabulary **121 -> 128**, admitting only codes seen at 2+ independent camps: `escape_room`,
  `lumberjack`, `golf`, `giant_swing`, `trade_skills`, `archaeology`, plus a `wifi` parent for the
  two orphaned wifi leaves. All seven were applied to the camps that evidenced them, so none ship
  dead — the mistake 0.35.0 made with `whitewater_rafting`. `giant_swing` was on last release's
  held-back list, recurred, and got in: the second-sighting rule works. 25 singletons stay held.
- **Manual review queue** via `tools/maintenance.py`: no camp sits at `portal` tier, so the queue is
  **43 surveyed camps with <= 5 features** against a ~15 median, **18 non-day camps still
  unsurveyed**, and three specific defects the agents refused to guess at — `az-r-c-scout-ranch`
  (address, coordinates and website all say Camp Raymond while only `name` says R-C),
  `ok-camp-george-thomas` (image-only guide the reader cannot mine), and `ar-camp-preston-hunt`
  (pool attested only by a line saying it was *out* of use).
- Field hazard worth keeping: **poisoned domains.** `baitinghollowscoutcamp.org` resolves, carries
  the exactly-correct camp title, and is squatted SEO spam. Test — a genuine camp site names its
  council or owning body in its own prose.

## 0.37.0 (minor) — 2026-07-26

- `26ba36a` **Coverage recovery: 10 more camps surveyed, non-day coverage 77% -> 79%** (304 of 384),
  feature entries 4,329 -> **4,609**, 16 new signature entries, **zero invented codes**. Two agents
  worked the 14 surveyable camps found by triaging the 90 that were still unsurveyed; 4 were
  correctly left untouched with `features_verified_at: null`.
- **The main wave did lose work, and this found it.** Five of the recovered camps
  (`va-blue-ridge-scout-reservation`, `va-camp-bowman`, `va-camp-marriott`, `va-camp-pmi`,
  `va-camp-rock-enon`) were precisely the "final five payloads" an agent announced writing in its
  last message before exiting non-zero in 0.34.0. Verifying that everything *on disk* was valid did
  not prove that everything *assigned* had been written — a distinction now in `LESSONS.md`.
- **Six active camps were hanging off councils that no longer exist**, undetected for several
  releases because `check_ref` only proves a reference resolves and a merged-away council still
  resolves. `validate_data.py` gains a guard that hard-fails a current camp whose council is
  non-current **when our own event graph names a successor** (the repair is then unambiguous);
  proven by injection. The three Black Hills Area camps were repointed to Sioux Council — their
  websites were already on `siouxcouncil.org`, which corroborates it. The other three sit on
  councils recorded as `discontinued` with no continuing party, so they are reported by
  `tools/maintenance.py` for research rather than blocking the build.
- **Negative result, recorded so nobody rebuilds it:** the guide-PDF lever that transformed the main
  wave gets **0 hits across 12 camps** on the remaining 62 portal-linked councils. Those councils
  publish neither a camp page nor a camp guide — the only guide-shaped links are Cub den-leader
  advancement booklets. Cheap automation is exhausted for the 62; they need per-camp research.
- `tools/maintenance.py` immediately paid for itself again, catching **7 duplicated provenance
  sources** introduced by this wave.
- Two techniques worth reusing, both from the surveying agents: **image-only PDFs are readable** if
  you rasterize and look at them (the main wave had written off a scanned guide as needing OCR —
  two thin camps became 16-feature records this way), and a page's `meta-description` can be a
  **site-wide CMS default** advertising activities the camp does not offer, caught only by noticing
  it was byte-identical on a sibling camp's page.

## 0.36.0 (minor) — 2026-07-26

- `1898c3f` **Phase 5 maintenance machinery: new `tools/maintenance.py`,** the standing health check
  and re-verification queue. Facts decay at different rates, so one "last verified" date cannot
  drive planning; the policy is now encoded — **signature features 12 months** (the most perishable
  thing in the dataset), ordinary features 24, website 6, provenance 24.
  - **Every clock reads zero today** because the whole corpus was verified across 0.33–0.35. That is
    the reason the tool also reports what a clock cannot see — 154 camps never surveyed, 2 with no
    website, and the zero-use vocabulary count promised in `LESSONS.md`. A pure staleness report
    would have looked healthy and said nothing.
  - **First real find: 445 entities carried duplicated provenance sources** — 535 redundant entries,
    16% of all 3,425 — left by successive passes appending the same url, sometimes bare and
    sometimes with an `accessed` date. `--fix-sources` collapses them keeping the richest entry;
    verified against HEAD that **zero urls and zero `accessed` dates were lost**. Repair stays
    behind an explicit flag, matching the `--overwrite` convention.
- **Adjudicated all four lifecycle findings from the survey wave — and two of the four claims did
  not survive verification.** This is why they were held for a research pass instead of applied.
  - `nc-lumpkin-adventure-base`: the **rename hypothesis was wrong**, and 0.34.0's `TODO.md` had
    already recorded it as "almost certainly a rename" of Harrison High Adventure Base. The
    council's own 2017 guide disproves it in one line — crews housed "between the Harrison High
    Adventure Outpost **and** Lumpkin Adventure Base". Lumpkin is a distinct Macon County property
    (Lumpkin family trust 1937, Tessentee Valley 1957) that is absent from the current guide.
    Retracted and corrected in `TODO.md`.
  - `nm-gorham-scout-ranch`: **not a status change, no edit made.** "Closed for the 2026 summer camp
    sessions" is a season fact; the same page offers weekend camping, Wood Badge, NYLT and BrownSea
    at the property. `operating_status` describes the property, and this dataset holds no sessions.
  - MOHAB: **confirmed and sourced**, but the pause begins after the 2026 season, which is in
    progress — so the camp is operating today, `operating_status` stays `active`, and the trigger
    plus the exact value to set later (`not_operating`, never `closed`) is recorded in `notes`.
  - `ut-hinckley-scout-ranch`: **confirmed.** `saltlakescouts.org` now fails DNS outright and the
    successor council never names the camp.
- **Two camps get `website: null`, the first in the dataset** (Lumpkin, Hinckley). A wrong link is
  worse than none: `_durable_url` falls back to the council's own site, so the published `url` went
  from a page about the four national bases and a dead pre-merger domain to
  `danielboonecouncil.org` and `utahscouts.org`. `operating_status` was left `active` in both cases
  — absence of a page is not proof of closure, and guessing is what this dataset refuses to do.

## 0.35.0 (minor) — 2026-07-25

- `81b02b5` **Published camp program features.** `current/camps.json` now carries `features`
  (sorted codes from the 121-term open `camp-features` vocabulary), `features_signature` (the subset
  a camp presents as a headline draw), and `features_verified_at`. All three are pinned as
  **required** in `published-current.schema.json`, so the build fails if the projection ever
  silently drops them; nine injection probes confirm the new keywords bite (missing field, duplicate
  code, non-string code, wrong type, bad date, stray property).
- **Codes only, deliberately.** The prose `note` on ~40% of feature entries stays in the per-entity
  `v1/camps/{id}.json` document. Republishing it inline would have grown the flat list 43%
  (466 → 664 KB) with text no filter reads; codes alone cost 12% (466 → 605 KB). This projection is
  the filterable one. Notes can still arrive later as an additive `features_detail` field.
  `{dataset}/index.json` listings stay light (107 KB, unchanged).
- **Publishing exposed a false-negative bug and it is now fixed.** Because the vocabulary was
  curated *after* the survey wave, 30 of 121 terms matched zero camps — including
  `whitewater_rafting`, the single most-requested term, which 15 surveyed camp pages described. A
  consumer filtering it got an empty result reading as "nobody offers this". 182 of the wave's 226
  proposals were recovered from the agents' session transcripts (the files had been deleted as
  scaffolding before being committed — see `LESSONS.md`) and **103 entries applied across 68 camps**
  against the accepted vocabulary only; rejected and held-back codes stayed dropped. Zero-camp terms
  **30 → 6**, and the six that remain (`coral_restoration`, `fossil_dig`, `maple_sugaring`,
  `surfing`, `automotive`, `performing_arts`) are genuine rarities. Published feature entries:
  4,226 → **4,329**.
- Verified end to end as a consumer would: building the `broader` rollup from the published vocab
  file alone and filtering the published camp list — `aquatics` → 254 camps, and a camp offering
  only `kayaking` correctly matches it.
- **The SQLite artifact carries features relationally**, not just inside its opaque `data` blob: a
  new `camp_features` junction table (4,329 rows; `camp_id`, `code`, `signature`, `note`,
  `verified_at` — the prose `note` *is* kept here, since bandwidth is not a constraint for a
  download) plus `feature_vocab` (121 rows, with `broader`), so a coarse query resolves the
  hierarchy in one recursive CTE. Verified the SQL answers match the JSON exactly (`aquatics` → 254
  camps either way). The artifact goes 9 → 11 tables, 1,652 → 6,102 rows.

## 0.34.0 (minor) — 2026-07-25

- `4866d96` **Main survey wave: 285 camps surveyed in parallel by 16 agents; camps with program
  features go 37 → 294 (77% of the 384 non-day-camps), feature entries 416 → 4,226.** Signature
  entries 20 → 147, across 91 distinct codes. Integrity held exactly as the calibration predicted:
  **zero unknown codes, zero duplicate codes, zero notes breaking the evergreen rule, zero
  unparseable files**, and no camp outside an agent's assigned batch was modified.
- Vocabulary **95 → 121 terms**, curated from 226 proposals covering 116 distinct codes. Additions
  were chosen by independent demand, not taste: `whitewater_rafting` was requested by 18 separate
  camps and had no code at all, and an entire missing season arrived as snowshoeing, cross-country
  skiing, sledding, ice fishing, and winter camping. `scoutcraft` was added as the parent the
  vocabulary lacked for orienteering, pioneering, and wilderness survival — standard BSA programme
  areas. Merged `hiking_trails` → `hiking`, `waterslide` → `water_slide`, `stargazing` → `astronomy`.
  Rejected `trade_skills`, `bike_friendly`, `waterfall`, and `family_camp`. **83 singletons were held
  back**: a code used once is not yet a category.
- Four hazards of wide parallel execution were found and fixed mid-wave, and are worth stating up
  front in any future brief: relative edit paths resolve against the session cwd and leak into the
  main checkout; the eval kernel is **shared between agents**, so a generic global can silently
  redirect one agent's write to another agent's file; the evergreen-text guard is case-insensitive
  and so rejects the ordinary English word "may" and month abbreviations; and eight camps carried
  bulk-imported features that a blind write would have deleted (the ruling: merge, never replace,
  and only refine a parent to a leaf when the page confirms the leaf).
- Highest-yield technique found: councils link Leader's/Program Guide PDFs **without a file
  extension** (the Tentaroo `/files/NNNNN/name` pattern), which the reader refuses. Fetching the
  bytes and reading them via a temp `.pdf` path took individual camps from 3 → 36, 8 → 21, 5 → 23,
  and 4 → 22 features.
- Survey reading also produced a worklist of things automation cannot settle, recorded in `TODO.md`:
  two probable camp **renames** (Lumpkin → Harrison, Hinckley's pre-merger domain), two **operating
  status** announcements (MOHAB pausing after 2026, Gorham closed for 2026), wrong-camp links, and
  two stored domains that are now **squatted**.
- `features` are still **not** in `current/camps.json` — publishing them is Phase 4, next up now that
  coverage is meaningful. They are visible today in the per-entity `v1/camps/{id}.json` documents.

## 0.33.0 (minor) — 2026-07-25

- `05915bc` **Calibration wave for feature population: 40 camps surveyed in parallel, vocabulary 46 → 95.** Two agents worked simultaneously against a frozen vocabulary contract, each on 20 camps. Result: **33 usable (82.5%), 322 feature entries, 13 signature entries** — and the numbers that decide whether the main wave is safe to run wide: **zero invented codes, and zero of 100 notes violating the evergreen rule.** Camps surveyed rose 5 → 37; the dataset now carries 416 feature entries across 45 distinct codes.
  - **The 0.32.0 portal repair paid for itself, measurably.** The sample was deliberately half camps whose link had just been repaired and half whose link was already clean. Repaired-cohort camps yielded **10.5 features each against 9.0** for the clean cohort — repairing a link does not merely unblock a camp, it produces a better-than-average survey.
  - **Vocabulary completed from evidence, not speculation:** 65 proposals covering 54 distinct codes were curated to 49 additions (→ 95 terms; 33 with `broader`, 34 with `aliases`). Merges collapsed `nature_ecology` into `nature_study`, two spellings of the first-year-camper programme, and `wheelchair_accessible` + `accessible_campsite` into `accessible_facilities`; `jet_ski` became an alias of `personal_watercraft`. `family_camp` was rejected outright — it is an audience already carried by the `camp-program-types` vocabulary, not a camp feature. The additions fill real gaps the pilot could not express: wilderness trekking, natural-rock climbing, accessibility, patrol cooking, first-year and counsellor-in-training programmes.
  - **One camp was re-queued rather than left misleading.** MOHAB's page is rich, but with no trekking codes available the agent could record nothing, and `features: []` plus a survey date reads as "we looked, it offers none". Its `features_verified_at` is back to `null` now that `backpacking` / `mountaineering` / `caving` / `packrafting` exist. This is exactly the distinction the four-state marker was designed to keep visible.
  - Method note for the main wave: freeze the vocabulary before dispatching, have agents raise unmapped observations as proposals instead of editing `data/vocab/`, and curate between waves. Agents self-coordinated on one ambiguity (how far "read one extra source when the page is thin" extends) and the ruling was broadcast to both mid-flight.

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
