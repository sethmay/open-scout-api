# Open Scout API — license & attribution

## License

The **data** in this repository (everything under `data/`, and the compiled
projections published from it) is licensed under
**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International
(CC BY-NC-SA 4.0)** — see [`LICENSE`](./LICENSE) or
<https://creativecommons.org/licenses/by-nc-sa/4.0/>.

The **pipeline/tooling source code** (`tools/`, any future `pipeline/`) is licensed
under the **MIT License**.

### Merit badge, rank & Cub adventure requirement text (third-party, excluded from the data license)

`requirement-set` documents reproduce **verbatim merit badge, rank and Cub Scout adventure
requirement text, which is
© Scouting America** (marked per-record with `includes_official_text: true` and a
`text_rights` statement). That text is **NOT** covered by the CC BY-NC-SA license above and
is **not ours to relicense** — it is reproduced with attribution, for non-commercial
Scouting use, and we honor takedown requests. Only the *compilation, structure, requirement
numbering, and metadata* of the requirement-sets are the project's contribution (CC BY-NC-SA).
Scouting America now distributes the merit badge pamphlets free at scouting.org. If you
reuse requirement-set files, keep the requirement text under Scouting America's copyright.

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
  The camp `summary` field is our own evergreen prose, regenerated from those descriptions
  (paraphrased, with dates/fees/schedules removed), not reproduced verbatim.
- **English Wikipedia** (CC BY-SA) — source for council **founding/rename/merger lineage
  facts**: founding years, prior council names and the years they changed, and which
  councils merged or were absorbed (with years). Only these uncopyrightable facts are
  extracted (`method: llm_extraction`, confidence 0.7–0.8) and the article is cited as the
  source URL in provenance; no article prose is reproduced. Facts are cross-checked by rule
  (bsa-number continuity, live-council collision guard) but remain best-effort — confirm
  against the council's own site.
- **OpenScouting/workbooks** (community project) — source of the merit badge catalogue
  (`badges/MANIFEST.md`) and the requirement source files (`badges/<slug>/<year>.md`) from
  which requirement-set structure + verbatim text were parsed. Their repository licenses its
  own workbook layout/code (CC BY-SA 4.0) and likewise treats the requirement text as
  Scouting America's property.
- **2024 Scouts BSA Requirements (No. 33216)** — the official Scouting America publication;
  authoritative source for the 7 rank `requirement-set` documents (`subject: rank:<slug>`).
  Requirement **text is © Scouting America** (see above), reproduced verbatim with
  attribution for non-commercial Scouting use; only the structure/numbering/metadata are the
  project's contribution. The source PDF is not redistributed (kept in git-ignored `.workbench/`).
- **U.S. Scouting Service Project (usscouts.org)** — community archive that mirrors official
  Scouting America requirements by effective year; source for the 26 historical rank
  `requirement-set` documents (2016-2023 editions), the discontinued merit-badge catalog, and the
  **pre-2024 Cub Scout adventure line-up**: 38 retired `adventure` entities and 121 historical
  adventure `requirement-set` editions, taken from `advance/cubscout/` including its `old/`
  archive of the 2018 elective editions. Effective dates are read from each page's own
  revision-date region rather than inferred. The requirement **text is © Scouting
  America** (see above), reproduced verbatim with attribution for non-commercial Scouting use;
  only the structure/numbering/metadata are the project's contribution. USSSP is unaffiliated
  with Scouting America; its own page layout/code is separately licensed and is not
  redistributed here (cached pages stay in git-ignored `.workbench/`).
- **Scouting America official advancement pages & PDFs (scouting.org, seascout.org)** —
  source for the current Cub Scout (Lion–Arrow of Light), Venturing (Discovery/Pathfinder/
  Summit), and Sea Scout (Apprentice–Quartermaster) rank `requirement-set` documents, and for
  the **131 Cub Scout `adventure` requirement-sets** and the identity/rank placement of all 139
  adventures: the scouting.org per-rank adventure pages (`/cub-scout-adventures/<rank>/`), the
  131 per-adventure pages, the Venturing rank pages, and the official 2026 Sea Scout rank
  PDFs. Requirement **text is © Scouting America** (see above), reproduced verbatim with
  attribution for non-commercial Scouting use — every requirement text was verified as a
  verbatim substring of the official source; only the tree structure/metadata are the
  project's contribution. Source pages/PDFs are not redistributed (kept in git-ignored `.workbench/`).
- **On Scouting (onscouting.org, formerly blog.scoutingmagazine.org)** — Scouting America's own editorial blog; source for the `merit-badge-ranking` dataset, whose annual recap ranks every merit badge by how many were earned (data credited there to the national Scouts BSA director). Only the **ranking facts** are extracted — badge name and position, which are uncopyrightable facts — never the posts' prose or images. No absolute earned-counts are published by the source, and none are inferred here.
- **Guide to Awards and Insignia (No. 33066)** — the official Scouting America publication;
  source for the `award` catalog. Only **facts** are extracted (award names, catalog item
  numbers, wear location) — uncopyrightable; the Guide's
  descriptive prose is © Scouting America and is not reproduced. The source PDFs are not
  redistributed (kept in git-ignored `.workbench/`).
- **OA lodge locator feed (oa-bsa.org)** — the official Order of the Arrow lodge directory;
  source for the `oa-lodge` catalog. We keep public/organizational facts only (lodge name,
  chartering council, OA section/region, HQ city/state + coordinates, website). Lodge OFFICER
  NAMES and CONTACT EMAILS in the feed are deliberately EXCLUDED as PII (especially youth
  officers). Not redistributed wholesale; the feed URL is cited in provenance.
- **WorldClim v2.1 climate normals** — source for each camp's `july_high_f` / `july_low_f`:
  1970-2000 monthly normals sampled at 30 arc-seconds (~1 km) from the camp's coordinate.
  WorldClim states the data are "freely available for academic use and other non-commercial
  use", and that "redistribution or commercial use is not allowed without prior permission"
  (<https://worldclim.org/about.html>). We therefore **do not redistribute the rasters** (~8 GB,
  git-ignored `tools/worldclim/`) and publish only derived per-coordinate point values
  (`tools/july_temp.json` and the camp records) under this project's non-commercial CC BY-NC-SA
  4.0 license. Cite as Fick, S.E. and R.J. Hijmans (2017), *WorldClim 2: new 1-km spatial
  resolution climate surfaces for global land areas*, International Journal of Climatology
  37(12):4302-4315. **Commercial reuse of these two fields requires permission from WorldClim.**

Nothing here is guaranteed accurate or current; confirm against the council's own site.
