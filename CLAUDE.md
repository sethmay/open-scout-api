# CLAUDE.md — working guide for agents in this repo



## Workflow

Here is the workflow that will define how code gets implemented. `WORKFLOW.md` is kept locally
and is not published with the repo, so this import resolves only in a working checkout.

@WORKFLOW.md

## Release notes (CHANGELOG entries)

Each GitHub Release body is generated verbatim from the matching `CHANGELOG.md` section
(`.github/workflows/release.yml`), so write CHANGELOG entries as human release notes, not
engineering logs. Compose them with two skills: `pbisapps-writer` for voice, and
`avoid-ai-writing` for the pass that strips generated-text tells. Take the transferable half of
`pbisapps-writer` (banned words, Oxford comma, near-zero dashes, spelling, lead with the point)
and skip the PBIS-specific material, which does not apply to this project.

- Lead with one plain sentence: what changed and why it matters to someone using the data.
- Break the specifics into point form (bullets); keep each bullet short and concrete.
- Prefer plain language over jargon. Leave out internal file names, entity counts, and
  `method`/config tags unless they genuinely help a reader.
- No em dashes or en dashes (they read as machine-written). Use commas, parentheses, or a
  spaced hyphen ` - `; use "to" for ranges.
- Replace filler on sight: `utilize` -> use, `facilitate` -> help, `additionally` -> also.
- No bold inside an entry. The lead sentence carries the weight; bolding phrases in a release
  body is a tell, and `avoid-ai-writing` flags it.
- Run the `avoid-ai-writing` checks over the finished section: no negate-then-reframe
  ("this is not X, it is Y"), no self-labeling significance ("the interesting part is"), no
  hollow intensifiers, and no moral adjectives on things that cannot hold them.
- Keep the `` `sha` `` anchor and the `## X.Y.Z (type) — date` header per `skill://semver`;
  the version-to-sha alignment is load-bearing for `git bisect`, only the prose changes. The
  em dash in that header is deliberate and stays.

Sections for releases that have already been published are historical record. Rewrite an entry
only while its release is still untagged or unpushed, because `release.yml` copies the section
into the release body at tag-push time and never revisits it.