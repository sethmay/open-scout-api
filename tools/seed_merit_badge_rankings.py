"""Seed generator: merit badge popularity RANKINGS by year (2021-2025).

TODO.md listed this as "merit badge earned-counts by year". **Scouting America does not publish
counts.** Its annual recap (On Scouting, formerly Bryan on Scouting, sourced from the national
Scouts BSA director) publishes a complete *ranking* of every merit badge by how many were earned,
and nothing else — no absolute numbers appear anywhere in those posts. So this dataset is ranks, and
says so: `metric: "earned_rank"`. A rank is still the longitudinal series nobody else has
machine-readable, and it is honest about what the source states.

    python tools/seed_merit_badge_rankings.py --fetch     # download the posts, then extract
    python tools/seed_merit_badge_rankings.py --extract <dir of cached post HTML>
    python tools/seed_merit_badge_rankings.py             # generate data/ from the facts file

Output: data/merit-badge-rankings/<year>.json, one immutable document per year.

Three traps in the source, all handled and all worth knowing:

  * **999 is a sentinel, not a rank.** The 2025 post gives Artificial Intelligence, Cybersecurity
    and Multisport a "2024 Rank" of 999 because they did not exist in 2024. Imported literally they
    would rank below every real badge.
  * **Footnote markers ride along in names** ("Hiking**", "Cycling**").
  * **Renames appear mid-transition** ("American Indian Culture (Indian Lore)", "Indian Lore",
    "Medicine/Health Care Professions"), so names map to slugs through an explicit alias table
    rather than by string luck.

Each post also carries the *previous* year's rank per badge, which is what makes 2021 recoverable at
all and gives 2022 and 2024 a second, independent source. Those overlaps are compared at extract
time and disagreement is fatal — when the check last ran, 135 shared 2024 badges agreed exactly.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import ssl
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
FACTS = ROOT / "tools" / "merit_badge_rankings.json"
OUT = ROOT / "data" / "merit-badge-rankings"
CACHE = ROOT / ".workbench" / "mbrankings"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"}
ACCESSED = "2026-07-27"
NOT_RANKED = 999          # the source's sentinel for "did not exist / unranked that year"

# data year -> the post that publishes its full ranking table
POSTS = {
    2022: "https://onscouting.org/2023/02/28/2022-merit-badge-rankings-a-new-chart-topper-emerges/",
    2023: ("https://onscouting.org/2024/02/13/"
           "2023-merit-badge-rankings-a-look-into-scouts-current-interests-and-achievements/"),
    2024: ("https://onscouting.org/2025/03/06/"
           "the-2024-merit-badge-rankings-take-a-swing-at-guessing-what-made-the-largest-gains-this-year/"),
    2025: ("https://onscouting.org/2026/03/18/"
           "first-aid-is-first-again-2025-merit-badge-rankings-are-here/"),
}
# post badge name -> our merit-badge slug, where the name alone does not resolve
ALIASES = {
    "american indian culture (indian lore)": "american-indian-culture",
    "indian lore": "american-indian-culture",
    "fish & wildlife management": "fish-wildlife-management",
    "medicine/health care professions": "health-care-professions",
    # The 2022 post still prints the pre-2021 name. Every year this dataset covers is 2021 or later,
    # i.e. after Medicine became Health Care Professions, so the surviving entity is the subject.
    "medicine": "health-care-professions",
}


def clean(s: str) -> str:
    """Collapse whitespace and drop trailing footnote markers ("Hiking**")."""
    return re.sub(r"[*\u2020\u2021]+$", "", re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()).strip()


def norm(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", name.lower().replace("\u2019", "'"))


def _ctx():
    c = ssl.create_default_context(); c.check_hostname = False; c.verify_mode = ssl.CERT_NONE
    return c


def fetch(dest: pathlib.Path) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for year, url in POSTS.items():
        p = dest / f"{year}.html"
        if p.exists():
            continue
        b = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30,
                                   context=_ctx()).read(2_000_000).decode("utf-8", "ignore")
        p.write_text(b, encoding="utf-8")
        print(f"  fetched {year} ({len(b)} bytes)")
        time.sleep(0.6)


def full_table(body: str) -> list[list[str]]:
    """The post's complete per-badge table — the only one with a row per merit badge."""
    best: list[list[str]] = []
    for tbl in re.findall(r"<table.*?</table>", body, re.S | re.I):
        rows = []
        for tr in re.findall(r"<tr.*?</tr>", tbl, re.S | re.I):
            cells = [clean(html.unescape(re.sub(r"<[^>]+>", " ", c)))
                     for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.S | re.I)]
            if any(cells):
                rows.append(cells)
        if len(rows) > len(best):
            best = rows
    return best if len(best) > 100 else []


def parse_post(body: str, year: int) -> tuple[dict[str, int], dict[str, int], int | None]:
    """(this year's ranks, previous year's ranks, previous year) keyed by badge NAME.

    Column order differs by post — some lead with the rank, the 2025 post leads with the name — so
    columns are identified by their header rather than by position.
    """
    rows = full_table(body)
    if not rows:
        raise SystemExit(f"{year}: no full ranking table found")
    header, body_rows = rows[0], rows[1:]
    name_i = next((i for i, h in enumerate(header) if "merit badge" in h.lower()), None)
    year_cols = {}
    for i, h in enumerate(header):
        m = re.search(r"(20\d\d)", h)
        if m and i != name_i:
            year_cols[int(m.group(1))] = i
    if name_i is None or year not in year_cols:
        raise SystemExit(f"{year}: unexpected header {header}")
    prev = next((y for y in sorted(year_cols) if y != year), None)
    cur, old = {}, {}
    for r in body_rows:
        if len(r) <= name_i:
            continue
        name = clean(r[name_i])
        if not name:
            continue
        for y, target in ((year, cur), (prev, old)):
            if y is None:
                continue
            i = year_cols[y]
            if i < len(r) and r[i].strip().isdigit():
                v = int(r[i])
                if v != NOT_RANKED:            # the sentinel is an absence, not a rank
                    target[name] = v
    return cur, old, prev


def extract(src: pathlib.Path) -> None:
    # Name -> slug. Normalising for comparison collapses real distinctions ("Leather Work" the
    # 1911-1951 badge vs today's "Leatherwork"; "Life Saving" vs "Lifesaving"; the 1911 "Aviation"
    # vs today's), so a CURRENT badge always outranks a retired one for the same normalised name -
    # a 2020s ranking means the badge that exists now. Retired names still resolve where they are
    # unambiguous, which is how "Indian Lore" finds its successor.
    badges: dict[str, str] = {}
    current: set[str] = set()
    for p in sorted((ROOT / "data" / "merit-badges").glob("*.json")):
        if p.name == "_events.json":
            continue
        d = json.loads(p.read_text("utf-8"))
        live = any(v.get("valid_to") is None for v in d["versions"])
        if live:
            current.add(d["id"])
        for v in d["versions"]:
            k = norm(v["name"])
            if k not in badges or (live and badges[k] not in current):
                badges[k] = d["id"]
    for k, v in ALIASES.items():
        badges[norm(k)] = v

    by_year: dict[int, dict[str, int]] = {}
    sources: dict[int, dict] = {}
    unknown: set[str] = set()
    conflicts: list[str] = []
    extras: dict[int, list[str]] = {}

    def record(year: int, ranks: dict[str, int], src_year: int, secondhand: bool) -> None:
        slug_ranks = {}
        for name, rank in ranks.items():
            slug = badges.get(norm(name))
            if slug is None:
                unknown.add(name); continue
            if slug in slug_ranks and slug_ranks[slug] != rank:
                conflicts.append(f"{year}: {slug} ranked {slug_ranks[slug]} and {rank} in one table")
            slug_ranks[slug] = rank
        if year in by_year:
            # This year already has its own post's table, which is DEFINITIVE: a secondary
            # prior-column restatement may only corroborate it, never extend it. Adding a badge the
            # primary table omits would break the 1..N ranking it publishes.
            for slug, rank in slug_ranks.items():
                if slug not in by_year[year]:
                    extras.setdefault(year, []).append(f"{slug} (rank {rank})")
                elif by_year[year][slug] != rank:
                    conflicts.append(f"{year}: {slug} is rank {by_year[year][slug]} in one source "
                                     f"and {rank} in another")
        else:
            by_year[year] = slug_ranks
            sources[year] = {"post_year": src_year, "secondhand": secondhand}

    for year in sorted(POSTS):                        # own tables first, so they own the year
        body = (src / f"{year}.html").read_text("utf-8", errors="ignore")
        cur, _, _ = parse_post(body, year)
        record(year, cur, year, False)
    for year in sorted(POSTS):                        # then prior-year columns: cross-check + 2021
        body = (src / f"{year}.html").read_text("utf-8", errors="ignore")
        _, old, prev = parse_post(body, year)
        if prev is not None and old:
            record(prev, old, year, prev not in POSTS)

    if unknown:
        raise SystemExit("badge names that resolve to no merit badge (add to ALIASES):\n  "
                         + "\n  ".join(sorted(unknown)))
    # A year's OWN post is its primary publication, so where the following year's prior-column
    # restates it differently the primary wins and the discrepancy is disclosed on the document
    # rather than silently averaged away or fatal. (2022 has four; 2024 has none across 135 shared
    # badges.) A conflict WITHIN one table is a parse failure and stays fatal.
    intra = [c for c in conflicts if "in one table" in c]
    if intra:
        raise SystemExit("one table ranks a badge twice — parse failure:\n  " + "\n  ".join(intra))
    disputed: dict[int, list[str]] = {}
    for c in conflicts:
        y = int(c.split(":", 1)[0])
        disputed.setdefault(y, []).append(c.split(":", 1)[1].strip())
    for y, ex in sorted(extras.items()):
        print(f"  {y}: {len(ex)} badge(s) appear only in the following year's restatement and were "
              f"NOT added (the primary table's 1..N ranking is definitive): {', '.join(ex)}")
    if disputed:
        print("  cross-source discrepancies (primary post kept, recorded on the document):")
        for y, cs in sorted(disputed.items()):
            for c in cs:
                print(f"    {y}: {c}")

    # The primary table can be internally broken: the 2022 post prints rank 130 twice and omits 135,
    # and the 2023 post's restatement puts Journalism at exactly 135. Where a duplicate rank and a
    # gap coexist AND the secondary assigns one of the tied badges precisely the missing rank, the
    # secondary is repairing a typo, not disagreeing - so it wins, and the repair is recorded.
    repairs: dict[int, list[str]] = {}
    for year, ranks in by_year.items():
        for c in list(disputed.get(year, [])):
            m = re.match(r"([a-z0-9-]+) is rank (\d+) in one source and (\d+) in another", c)
            if not m:
                continue
            slug, primary, secondary = m.group(1), int(m.group(2)), int(m.group(3))
            tied = [s2 for s2, r in ranks.items() if r == primary]
            taken = set(ranks.values())
            if len(tied) > 1 and secondary not in taken:
                ranks[slug] = secondary
                repairs.setdefault(year, []).append(
                    f"{slug}: {primary} -> {secondary} (the primary table printed {primary} twice "
                    f"and omitted {secondary})")
                disputed[year].remove(c)
    for year, rs in sorted(repairs.items()):
        for r in rs:
            print(f"  {year}: REPAIRED {r}")

    years = []
    for year in sorted(by_year):
        ranks = by_year[year]
        vals = sorted(ranks.values())
        complete = vals == list(range(1, len(vals) + 1))
        years.append({
            "year": year,
            "complete": complete,
            "source_post_year": sources[year]["post_year"],
            "source_url": POSTS[sources[year]["post_year"]],
            "secondhand": sources[year]["secondhand"],
            "rankings": [{"rank": r, "subject": f"merit-badge:{s}"}
                         for s, r in sorted(ranks.items(), key=lambda x: x[1])],
            "disputed": sorted(disputed.get(year, [])),
            "repairs": sorted(repairs.get(year, [])),
        })
        print(f"  {year}: {len(ranks):>3} badges, ranks {vals[0]}..{vals[-1]}, "
              f"contiguous={complete}, secondhand={sources[year]['secondhand']}")
    FACTS.write_text(json.dumps({
        "note": ("Merit badge popularity RANKINGS by year from Scouting America's annual recap "
                 "(On Scouting). The source publishes ranks only - no absolute earned-counts appear "
                 "in any post - so `metric` is earned_rank. Each post also gives the prior year's "
                 "rank per badge, which recovers 2021 and independently corroborates 2022 and 2024; "
                 "disagreement is fatal at extract time. The source's 999 means 'did not exist that "
                 "year' and is dropped, not imported."),
        "accessed": ACCESSED, "aliases": ALIASES,
        "sentinel_dropped": NOT_RANKED, "years": years,
    }, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {FACTS.relative_to(ROOT).as_posix()}: {len(years)} years, "
          f"{sum(len(y['rankings']) for y in years)} badge-year ranks")


def generate() -> None:
    facts = json.loads(FACTS.read_text("utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    for y in facts["years"]:
        year = y["year"]
        doc = {
            "id": str(year), "kind": "merit-badge-ranking", "year": year,
            "metric": "earned_rank",
            "complete": y["complete"],
            "source_document": {
                "title": f"{year} merit badge rankings \u2014 On Scouting (Scouting America)",
                "url": y["source_url"], "year": y["source_post_year"] + 1},
            "rankings": y["rankings"],
            "provenance": {
                "sources": [{"url": y["source_url"], "accessed": facts["accessed"]}],
                "method": "scraped", "verified_at": facts["accessed"], "confidence": 0.9,
                "notes": (("Taken from the following year's post, which publishes each badge's "
                           "previous-year rank; no post of its own covers this year. ")
                          if y["secondhand"] else "")
                + "Ranks by number earned; Scouting America publishes no absolute counts."
                + (" The following year's post restates this year's ranks and disagrees on "
                   + str(len(y["disputed"])) + " badge(s) (" + "; ".join(y["disputed"]) + "); this "
                   "document keeps the ranks from this year's own post, its primary publication."
                   if y["disputed"] else "")
                + ((" The primary table is internally inconsistent and the following year's post "
                    "resolves it exactly; corrected here: " + "; ".join(y["repairs"]) + ".")
                   if y["repairs"] else ""),
            },
            "notes": None,
        }
        (OUT / f"{year}.json").write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                                         encoding="utf-8", newline="\n")
    print(f"merit-badge-rankings: {len(facts['years'])} year documents written")


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] == "--fetch":
        fetch(CACHE); extract(CACHE)
    elif args and args[0] == "--extract":
        extract(pathlib.Path(args[1]) if len(args) > 1 else CACHE)
    generate()


if __name__ == "__main__":
    main()
