# Lessons

Curated, durable, project-specific engineering lessons distilled from review-gate
`...-lessons.md` files under `.workbench/reviews/` (WORKFLOW.md step 4). Dedupe and
fold; read before similar work.

## Schemas / validation

- **A sentinel that means "all" cannot also mean "none".** `choose: null` on a requirement node
  reads as *complete every child*. Modelling the Cub "Special Elective Adventures" heading as a
  peer group therefore asserted that every Cub must earn BB Guns to rank up — a page heading
  copied faithfully into a false requirement. When a source's visual grouping has no truthful
  encoding in the requirement tree, it is an attribute of the member (`adventure.category`), not a
  sibling requirement. Ask what the node *claims*, not what the page *looks like*.
- **A rendered list interleaves labels with items, and a naive parser cannot tell them apart.**
  Each Cub rank page pairs its required adventures with six *area* names (Character & Leadership,
  Personal Fitness, Personal Safety, Family & Reverence, Citizenship, Outdoors). An earlier seed
  captured three of those areas as if they were Arrow of Light adventures, and they shipped for
  months — AOL published seven required adventures where the page's own rule says six. Parse by
  element role (the adventures are the `<h2>`s), and check the count the source states in prose
  against the count you extracted; that sentence is the cheapest available oracle.
- **Prose stating a total is a stronger source than the list you can see.** "Complete six required
  Adventures and any two elective" is what proved Bobcat is genuinely the sixth required adventure
  even though it sits outside the required heading — and it is what would have caught the Arrow of
  Light error at write time. Look for the sentence that counts before modelling the list.
- **A link's href is not the target's identity.** The Arrow of Light page links
  `/cub-scout-adventures/bobcat-arrow-of-light/`, which redirects to a page whose `rel=canonical`
  is `bobcat-aol`. Derive ids from the destination's own canonical URL, never from the referring
  link — and never from a slugified display name, which would also have missed
  `pick-my-path-lion`.
- **Schema fixtures MUST include expected-fail cases for every strictness/conditional
  keyword** (`additionalProperties`/`unevaluatedProperties: false`, `anyOf`, `if/then`).
  A positive-only validator stays green when the guard is deleted. Inherited from
  camp-finder ("make every guard bite"; "a CI gate must be non-vacuous"); encoded in
  `schema/v1/examples/invalid/` + the negative pass in `tools/validate_examples.py`.
- **Every temporal/structural invariant stated in PLAN or schema prose MUST have a
  validator rule that bites**, or it silently rots. Data-level invariants JSON Schema
  can't express live in `tools/validate_data.py`: id==filename, refs resolve, half-open
  non-overlapping windows, only-final-version-open, unique event ids, and the
  retired-entity rule below. Verify each with a deliberate failing case.
- **Draft 2020-12 composition for entity versions:** sibling `allOf: [{$ref: VersionBase}]`
  + local `properties` + `unevaluatedProperties: false`. The `$ref`'d base's properties
  count as evaluated, so unknowns are rejected while base fields pass. NEVER switch the
  sub-def to `additionalProperties: false` — it would reject the base fields.
- **`format`/`pattern`/bounds keywords are type-scoped**, so `type: ["string","null"] +
  format: "uri"` is safe (no-ops on null). `anyOf: [{$ref: X}, {type: null}]` is only
  *required* when the constraint is a `$ref` (can't inline a $ref into a type array).
  Both idioms coexist deliberately in these schemas — don't "normalize" one into the other.

## Temporal model

- **Validity windows are half-open `[valid_from, valid_to)`** — a successor's `valid_from`
  equals its predecessor's `valid_to`. Any non-overlap validator MUST compare half-open or
  it false-positives on every adjacent pair (PLAN §3.1; Citizenship in Society example).
- **A retired entity MUST NOT keep a `valid_to: null` version** — null means "current"
  and it leaks into the current-list projection. If the end date is unverified, do NOT
  default to null; use a documented coarse bound from the evidence (e.g. `2026` = the year
  first observed absent from official maps) + a note, never a fabricated exact date.
  `validate_data.py` enforces this: an entity that is the `subject` of a `discontinued`
  event or a `predecessor` in `merged`/`absorbed`/`split` must have no open version.
- **Inference-honesty discipline for seeded data:** unverified facts get `date: null` +
  confidence 0.4–0.6 + an explicit "unverified/presumed" note; sourced facts get real
  dates + citations at 0.8+. Never fabricate a date or a merge target to look complete.

## Data safety / licensing

- **`includes_official_text` ⇔ any `Requirement.text` present is a cross-node invariant
  JSON Schema cannot express.** It is a pipeline rule (TODO.md "Pipeline validator") and
  the publish-time lever for withholding Scouting America's copyrighted requirement text.
  Never trust the boolean alone.
- **Illustrative examples carry realistic names/URLs/high confidence; the "do not import"
  marker is prose in `notes`.** The real safety boundary is the `schema/v1/examples/`
  directory being never-published and never globbed with `data/`. If examples ever move or
  a pass globs them alongside data, add a structural sentinel or cap their confidence first.
- **Keep a documented safeguard and its mechanism in sync, in the same commit.** NOTICE.md
  claimed `maps/` (proprietary source images) was git-ignored while the committed
  `.gitignore` had no such entry — a doc-vs-repo drift that defeats the protection.
  Gotcha: a `printf >> .gitignore` run in the MAIN checkout does not touch the feature
  worktree's file; edit the worktree copy. When a doc asserts "X is git-ignored", add/verify
  the `.gitignore` line in the same change (proprietary map images are facts-only sources —
  extract facts, never redistribute the images).

## Build / publish (dist/ + GitHub Pages)

- **Deploy-on-every-push + the semver PENDING→backfill two-step makes the build's version
  lag one commit.** `build.py` reads the newest `## X.Y.Z` CHANGELOG heading, but at
  feature-merge time the entry is still `PENDING` (newest heading is the *previous*
  version). Fix used: if a `PENDING` line exists, stamp `X.Y.Z+unreleased` so the deployed
  version is honest during the lag; it self-clears when the bump commit lands. For exact
  version pinning, consumers use git tags / jsDelivr, not `meta.json`.
- **A published JSON Schema shipped as a consumer contract MUST have a root
  (`type`/`properties`/`$ref`), not just `$defs`.** A `$defs`-only file validates nothing
  when a consumer points a validator at it (vacuous pass); it "worked" only via the
  producer's inline `{**schema,"$ref":"#/$defs/X"}`. Give it a real root and delete/wire
  every `$def` (`published-current.schema.json`).
- **`format` (uri/date/date-time) is a silent no-op unless the format extra is installed.**
  CI must `pip install "jsonschema[format]"` (pulls rfc3987 etc.) for those to bite;
  patterns/`required`/`additionalProperties`/bounds always bite. (Corollary of the
  type-scoped-format note above — a `format` keyword that neither applies to the type nor
  has its checker installed guards nothing.)
- **Derive a denormalized cross-entity field from the referenced entity, not from a slug
  regex.** `territory_number` now comes from the referenced territory's canonical `number`,
  not `cst-(\d+)` on the slug — the regex silently yields null for any future current
  entity whose slug breaks the convention while the canonical number is right there.

## Datasets / catalog seeding

- **`validate_data.py`'s `ENDED_AS_PRED` must stay in lockstep with the `EventType`
  enum.** The retired-entity invariant only fires for an entity ended as a `predecessor`
  if its event type is in that set (`merged`/`absorbed`/`split`/`superseded`). Add any new
  ending event type there or a retired entity can silently keep an open (current) version.
- **The published `items` `oneOf` union is safe only while every current-projection type
  has disjoint `required` fields under `additionalProperties:false`.** CurrentCouncil /
  CurrentTerritory / CurrentMeritBadge don't overlap, so exactly one matches. A future
  current type that isn't disjoint makes `oneOf` reject valid items (0 or 2 matches) — keep
  them disjoint or switch to a discriminated union on `kind`.
- **A retired entity's `index.json` row reflects its LAST version** (e.g. Citizenship in
  Society shows `eagle_required:true, current:false`), so a raw count of a boolean facet in
  `*/index.json` exceeds the `current/*.json` count. Intentional + consistent across
  datasets; consumers filter `current:true` for current facts.
- **Catalog-layer house style for copyright-sensitive data:** publish only catalogue facts
  + curated flags, keep `description` null, cite the source + authoritative URL, and set
  `confidence < 1` + a note when dates are approximate. For copyright-sensitive verbatim
  text, the catalog layer stayed facts-only; the requirement-set layer later included it
  under the enforced mixed-rights marking (next bullet).
- **Mixed-rights datasets: prove the marking is ENFORCED, not just present.** For
  third-party (e.g. Scouting America) verbatim text, pair a validator invariant
  (`includes_official_text` ⇔ any `text` present, validate_data pass 4) with a schema
  conditional (`if includes_official_text then text_rights` required, non-empty). Together
  the copyright marker is un-droppable. This is the standing template for any future
  third-party-text inclusion (ranks/awards reuse the requirement-set schema).
- **When a change reverses a documented policy, update the canonical schema's own
  `description` prose in the SAME patch** — not just NOTICE/README/PLAN/TODO. Schema
  descriptions are load-bearing docs; a stale one (e.g. "summaries-only default") that
  contradicts the data misleads the next maintainer.
- **Honest parser degradation:** a workbook-style parser that hits irregular input must
  make it visible in the data — flip a fallback flag, drop confidence (0.9→0.75), and stamp
  `provenance.notes` + top-level `notes`. Never silently flatten. (seed_requirement_sets.py)
- **Never re-run a SEED generator during a review** when its source is git-ignored/out-of-diff
  — it rewrites tracked data. Review runs only `validate_*`/`build` (read committed data,
  write only git-ignored `dist/`).
- **When an importer keys off another entity's versioned attribute (e.g. council
  `bsa_number` -> slug), read it from the OPEN version (`valid_to: null`), not
  `versions[0]`.** versions[0] is the *earliest* (possibly historical) snapshot; a
  renumbered/renamed entity would misroute. Harmless today (councils are single-version)
  but latent — resolve current-value lookups against the current version. (import_camps.py)
- **Agent scaffolding can be the only copy of real signal — commit it before you tidy.**
  Sixteen survey agents wrote `proposals-NN.json` (observations the frozen vocabulary could
  not express). Treating them as scratch and `rm`-ing them before `git add` destroyed the
  camp→proposed-code mapping; only the aggregate counts survived, which are useless for
  applying anything. 182 of 226 were later clawed back out of the agents' session
  transcripts (`toolCall.arguments.content` in `~/.omp/agent/sessions/**/<Agent>.jsonl`),
  but four agents had built theirs inside `eval` cells and were unrecoverable. Either commit
  the scaffolding or fold it into data before deleting — and know the transcript path as a
  last resort.
- **Curating a controlled vocabulary AFTER the survey guarantees false negatives.** Terms
  added post-wave match zero entities, so a consumer filtering on the most-requested term of
  all (`whitewater_rafting`, 15 camps' pages described it) gets an empty result that reads as
  "nobody offers this". Publishing is what made it visible. Either freeze the vocabulary and
  accept proposals as a *later* enrichment pass with the evidence retained, or run a
  calibration slice first and curate before the main wave — never curate and publish in the
  same breath without re-checking term usage. A `zero-camp terms` count is a cheap standing
  health check.
- **A shared eval kernel across parallel agents is a silent data-corruption channel.** Generic
  globals (`p`, `d`, `camp`) get reassigned by siblings mid-run, so one agent's write lands on
  another's target path. Namespace per-agent (`S06_*`) or, better, run writes as a separate
  process. Relative paths in edit headers are the same class of bug: they resolve against the
  session cwd, not the worktree, and leak edits into the main checkout.
- **Verify parallel agents' claims against the artifact, not their reports.** Self-reports are
  honest but lossy: one agent reported a clobbered feature list that was actually a compliant
  parent→leaf refinement (it compared diff lines, where a reordered array shows codes as both
  removed and added). Compare parsed *sets* before and after; and treat a subagent exit code
  as unrelated to whether its work landed — 9 of 16 exited non-zero after their writes were
  already on disk and valid.
- **An agent's *observation* is evidence; its *identity conclusion* is a hypothesis. Verify before
  it reaches a doc.** Of four lifecycle findings handed up by the survey wave, two did not survive
  checking, and I had already written one of them into `TODO.md` as "almost certainly a rename".
  - The false rename came from absence-of-evidence reasoning: "Lumpkin Adventure Base" appeared
    only in a meta keywords tag while the council marketed "Harrison High Adventure Base", so they
    looked like one property under two names. The council's own older programme guide settled it in
    one line — crews were housed "between the Harrison High Adventure Outpost **and** Lumpkin
    Adventure Base". **When a current page is silent, the organisation's own older documents are
    the cheapest disproof**, and a public search found it in one query.
  - The false status change came from reading a headline literally: "closed for the 2026 summer
    camp sessions" is a *season* fact, and the next sentence offered weekend camping, Wood Badge,
    NYLT and BrownSea at the same property. Know which granularity your field models —
    `operating_status` describes the property, and a dataset that deliberately holds no sessions
    has nothing to record.
  - Corollary for future waves: a page can contradict itself and usually will. MOHAB announces a
    pause *and* advertises next season's dates and fees on the same page. Prefer the dated
    announcement, and record that the other block is stale rather than silently picking one.
- **A future-dated fact is not a version change yet.** MOHAB's pause is real, sourced, and starts
  after a season that is still running. Writing it into `operating_status` now would publish a
  falsehood, and future-dating a new version would too, since `open_version` picks whatever has
  `valid_to: null` and would surface it immediately. Park it in entity `notes` with the trigger
  condition and the exact value to set later.
- **"The data on disk is valid" is not "the work got done".** After a 16-agent wave I verified every
  file parsed, every code was known, and nothing outside the batches was touched — all true, and I
  concluded nothing was lost. Two releases later, five camps turned out to be the "final five
  payloads" an agent announced writing in its last message before it exited non-zero. Reconcile the
  **assigned** manifest against the **written** set, not just the integrity of what landed.
- **Image-only PDFs are readable: rasterize and look at them.** The main wave wrote off a scanned
  programme PDF as "needs OCR, impossible without it". A later agent rasterized map PDFs at 4x and
  read the program-area labels visually, turning two otherwise-thin camps into 16-feature records.
  Any vision-capable reader can do this; do not mark an image PDF unusable.
- **Beware the site-wide default meta-description.** One agent nearly sourced features from a
  council page's `meta-description` advertising sea kayaking and sandboarding — then noticed it was
  byte-identical on a sibling camp's page, i.e. a CMS default, not a description of either camp.
  Body copy only; if a "description" repeats across pages it describes the council, not the camp.
- **Negative results are worth a changelog entry.** The guide-PDF lever that transformed the main
  wave produced **0 hits across 12 camps** on the remaining portal-linked councils, because those
  councils publish neither a camp page nor a camp guide. Recording that stops the next person
  building a third crawler for the same 62 camps.
- **`check_ref` proving a reference resolves is not the same as it being *current*.** A council that
  merged away still exists as an entity, so six active camps sat on dissolved councils for several
  releases with a clean validator. When entities have lifecycle state, referential checks need to
  assert the *state* of the target, not just its existence — and hard-fail only where the repair is
  unambiguous (a recorded successor), reporting the rest for research.
- **When a whole population looks uniformly empty, suspect the instrument before the population.**
  62 camps were written off across three separate attempts — an automated council crawl, a
  12-camp guide spike I ran myself, and a changelog entry declaring "cheap automation is exhausted"
  — because their registration pages appeared to be bare forms. They were not. Reading a
  `scoutingevent.com` URL without a selector follows a redirect to an empty "you have not selected a
  calendar" shell; the same URL read with `:raw` returns the full page. Every one of the 62 then
  proved surveyable, at an average of 28 features each. A uniform negative across a large,
  heterogeneous population is far more likely to be a measurement artefact than a property of the
  world — sanity-check one case by a completely different route (a real browser, curl, a different
  reader mode) before generalising.
- **A quality tier must be derived from evidence you actually recorded, not asserted.**
  `features_source_tier` is computed from which provenance sources carry an `accessed` date, biased
  so `guide` is never over-claimed. That it separates cleanly (21 features/camp vs 13) is what makes
  it trustworthy; had the two tiers scored the same, the field would have been decoration. Validate
  a new quality signal by checking it predicts something before you publish it.
- **Add vocabulary and populate it in the same release.** 0.35.0 shipped 26 codes curated after the
  survey, so `whitewater_rafting` matched zero camps and a consumer filtering it saw "nobody offers
  this". This release admitted 7 codes and applied all 7 to the camps whose evidence justified them,
  in the same change. The standing check is the zero-use count in `tools/maintenance.py`.
- **Squatted domains are a real sourcing hazard, and name-matching is not evidence.** Three camp
  domains in this project are squats — one SEO spam with a paid termite-company backlink, one a
  gambling site — and each carried the exactly-correct camp name. Test: a genuine camp site names
  its council or owning body in its own prose. Related: a council with no page for a camp it
  operates often does not own it (trust, foundation, or alumni association), but only when the
  silence is *asymmetric* — a council promoting sibling camps while silent on this one. Uniform
  silence just means the council's website is broken.
- **If a licensing boundary runs through your dataset, make a validator hold the line.** This repo
  publishes verbatim requirement text as © Scouting America under a narrow `text_rights` carve-out,
  while everything else is CC-licensed. Badge `description` sits on the CC side, so a description
  that quoted the requirements would quietly move copyrighted wording across that boundary — and no
  amount of instruction to "write original prose" is auditable later. A gate that rejects any
  description sharing 8+ consecutive words with its own badge's requirement text turns a policy into
  a build failure. Build the comparison corpus from the union of ALL documents for that entity, not
  the one you happened to read.
- **When a rule has a hard threshold, check the margin, not just the threshold.** The copyright gate
  fires at 8 shared words. Agents probing at 7 and 6 found five descriptions that passed at 8 while
  clearly tracking a requirement's clause with one word swapped — passing the letter, failing the
  intent, and one requirement revision away from failing the build. Short runs of genuine domain
  vocabulary ("plaited coiled ribbed and wicker") are fine; the margin probe is what distinguishes
  them from borrowed sentence structure.
- **Never let the exemplars in a brief become shipped content.** Four worked examples were included
  to fix the voice, and one of those badges happened to sit in an agent's batch — so it shipped my
  illustration instead of writing from the requirements. It flagged this honestly, which is the only
  reason it was caught. Either pick exemplars from outside the work set, or rewrite them centrally
  afterwards.
