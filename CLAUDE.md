# CLAUDE.md — working guide for agents in this repo



## Workflow

Here is the workflow that will define how code gets implemented

@WORKFLOW.md

## Release notes (CHANGELOG entries)

Each GitHub Release body is generated verbatim from the matching `CHANGELOG.md` section
(`.github/workflows/release.yml`), so write CHANGELOG entries as human release notes, not
engineering logs. Author them with the `pbisapps-writer` skill's voice.

- Lead with one plain sentence: what changed and why it matters to someone using the data.
- Break the specifics into point form (bullets); keep each bullet short and concrete.
- Prefer plain language over jargon. Leave out internal file names, entity counts, and
  `method`/config tags unless they genuinely help a reader.
- No em dashes or en dashes (they read as machine-written). Use commas, parentheses, or a
  spaced hyphen ` - `; use "to" for ranges.
- Replace filler on sight: `utilize` -> use, `facilitate` -> help, `additionally` -> also.
- Keep the `` `sha` `` anchor and the `## X.Y.Z (type) — date` header per `skill://semver`;
  the version-to-sha alignment is load-bearing for `git bisect`, only the prose changes.