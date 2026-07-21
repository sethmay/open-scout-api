# Open Scout API — license & attribution

## License

The **data** in this repository (everything under `data/`, and the compiled
projections published from it) is licensed under
**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
(CC BY-NC-SA 4.0)** — see [`LICENSE`](./LICENSE) or
<https://creativecommons.org/licenses/by-nc-sa/4.0/>.

The **pipeline/tooling source code** (`tools/`, any future `pipeline/`) is licensed
under the **MIT License**.

### How to attribute

> Data from the Open Scout API project (<repo URL>), licensed CC BY-NC-SA 4.0.

If you build on the data you must (a) credit the project, (b) keep it non-commercial,
and (c) release derived datasets under the same license.

## Unofficial & unaffiliated

This is an unofficial community project. It is **not affiliated with, endorsed by, or
sponsored by Scouting America (Boy Scouts of America)**. "Scouting America", "Boy Scouts
of America", and related names/marks belong to their owner; this project claims no
trademark rights and implies no endorsement (see LICENSE §2(a)(6)).

## Sources & their status

Per-fact provenance lives in each record's `provenance` block. Two seed sources are
noted here because their status shapes what we may redistribute:

- **Scouting America "Council Service Territory" maps** — the authoritative source for
  each council's territory assignment and official name + HQ city. The map **images are
  proprietary** ("may not be modified, reproduced or distributed electronically without
  express permission of Scouting America") and are therefore **NOT redistributed** in
  this repository (`maps/` is git-ignored). We extract only **facts** — council number,
  name, HQ city, territory assignment — which are not themselves subject to copyright
  (facts are uncopyrightable); the map is cited as the source. Production date of the
  map set used for the initial seed: mid-2026.
- **camp-finder** (sibling project, `D:\repos\claude\personal\camp-finder`) — an
  unofficial community dataset. Used for council websites and to cross-check names/HQ.
  Records seeded from it carry `method: imported` and its provenance; the official map
  supersedes it on name/HQ conflicts.

Nothing here is guaranteed accurate or current; confirm against the council's own site.
