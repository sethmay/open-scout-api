# Agent Workflow

- Always feature branch for new work, **in fresh git worktree** — never on main folder checkout. See Worktrees below. Cannot tell from your context if other agents run concurrently on same repo — assume parallelism, isolate. Applies to every feature branch, not only "parallel-looking" work.
- Commit all code between tasks, useful messages.

## Worktrees — always required for feature work

**Always worktree for feature work. Even when task looks serial.** Cannot see other agents from your context; user routinely runs many agents parallel on same repo. Agent that checks out branch directly on main folder clobbers sibling doing same — both confused, work lost, or wrong branch merged. Worktree = only safe-by-default way.

Worktree = separate filesystem checkout sharing same `.git` as main folder. Branches, commits, merges in one worktree instantly visible in others (no push/pull). Cross-cutting work touching hub + API repos in lockstep → make worktree in *each* repo under same branch name.

**Lifecycle:**

1. From main folder, create worktree on fresh feature branch off `main`:
```bash
git worktree add .claude/worktrees/<slug> -b feature/<slug> main
```
2. Brief **implementing agent** on worktree path; it commits there on `feature/<slug>`. **Feature work must be committed before review** — reviewer reads committed branch tip, not worktree's uncommitted state.
3. **Review gate — before merge.** Dispatch **`code-reviewer` agent** — never implementing agent's own context; reviewer that remembers writing the code reviews intentions, not code. Agent supplies isolated context + read-only tool scope, so no detached checkout needed. Pass as absolute paths so they don't collapse onto agent's working dir:
   - **read from** = feature worktree (`.claude/worktrees/<slug>`)
   - **base** = `git merge-base main feature/<slug>`; **head** = `feature/<slug>` tip
   - **write to** = **main folder's** `.workbench/reviews/` — not worktree's, deleted at cleanup

   Writes paired `<YYYY-MM-DD>/<HHMMSS>-<slug>-review.md` + `...-lessons.md` there.
   When dispatching the code-reviewer agent, clearly announce `** Starting Review Gate **`.
4. **Consume review.** Back in feature worktree, implementing agent reads review just written — newest `*-<slug>-review.md` under `.workbench/reviews/<YYYY-MM-DD>/`. Resolve every BLOCKER (fix + recommit, then re-run step 3 on new tip). MAJOR/MINOR/NIT at your discretion; proceeding past them is human decision, not agent's. Never merge with outstanding blockers.

   **If review's Basis lists resource gaps** (concern-classes reviewer found no standard for — e.g. security or accessibility area, no matching skill/reference), surface to user so resources added for future reviews. Notification, not merge gate.

   **Harvest lessons.** Reviewer also writes paired `...-lessons.md`. Read it, pull any *durable, project-specific* lesson (reusable gotcha, invariant, convention — not per-change retrospective like "clean change") into **two** places:
   - **agent memory** — auto-surfaces future sessions; and
   - repo-root **`LESSONS.md`** — committed, survives project move or loss of machine-local memory.

   Curate, don't append blind: dedupe against existing, fold repeats into existing entry, drop filler. Dated `...-lessons.md` stay as untracked audit trail; `LESSONS.md` = curated distillation. Make `LESSONS.md` edit in feature worktree so it merges with the work (memory writes are machine-local, outside branch).
5. From main folder (`main` checked out), merge `--no-ff`:
```bash
git merge --no-ff feature/<slug>
```
6. Remove worktree:
```bash
git worktree remove .claude/worktrees/<slug>
```
`git worktree remove` refuses if uncommitted changes; `--force` overrides. Branch preserved — delete with `git branch -d feature/<slug>` when done.


## Tracking files (`CHANGELOG.md` + `TODO.md` + `LESSONS.md`)

Root files = source of truth for what shipped, what's planned, what we've learned. Keep current — memory is for durable preferences + project context, not a shipping log.

- **`CHANGELOG.md`** — historical record of shipped features. **Add entry in same commit that ships the feature.** Grouped by version, newest first. Section heading = `## <version> (<bump>) — <date>` where `<bump>` = `major`/`minor`/`patch`, so reader sees at a glance whether release adds/fixes/breaks. Inside, one line per merge: `` - `<short-sha>` <imperative description> ``. Going forward, one version section per merge (Versioning rule bumps every merge). Don't backfill long paragraphs — commit message has the detail.
- **`TODO.md`** — active queue, deferred items, tech debt. **When starting an item, leave it in `TODO.md`; when it ships, move to `CHANGELOG.md` in the merge commit.** Add new items here as they come up — don't leave them only in conversation. Mark deferred items with reason + signal that would unblock them. **Write every item to survive a clean context** — a fresh session with no history must pick it up from its text alone: goal, key files/symbols, decisions made, next concrete step. Keep pickup context to a few lines; prefer pointers (paths, branch names, CHANGELOG shas, claude-mem observation IDs) over inlined prose. TODO.md is read on demand, not auto-loaded, but every line costs tokens when read — prune detail a pointer already covers, delete pickup context once item ships.
- **`LESSONS.md`** — curated durable engineering lessons distilled from `code-reviewer`'s `...-lessons.md` files (Worktrees lifecycle step 4). Committed, persistent backstop for reusable gotchas, invariants, conventions; same items also go to agent memory. Curate, don't accrete — dedupe, fold repeats, drop per-change retrospectives. Read before similar work.
