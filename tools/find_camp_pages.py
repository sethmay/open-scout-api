"""Find a real camp page for camps whose stored website is a registration portal.

The 0.31.0 link audit found 132 non-day-camps whose `website` points at a registration platform
(scoutingevent, tentaroo, doubleknot, …). A registration link has nothing to survey, so those
camps are the blocker on feature population — but every one of them belongs to a council whose
own website we already store, and councils almost always publish a page per camp.

So rather than searching the open web 132 times, this walks each council's own site: fetch the
homepage, follow its camping-ish links one level down, and look for a link whose anchor text or
URL slug names the camp. Candidates are then fetched and confirmed to actually name the camp and
not be another portal. Work is grouped by council, so a council with four portal camps is
crawled once.

Output is a review file (default .workbench/portal_candidates.json), NOT a data change: a
candidate is a suggestion with the evidence attached, and applying one is a deliberate edit.
Checkpointed and resumable; polite by construction (few workers, backoff on 429).

Usage: python tools/find_camp_pages.py [--out PATH] [--limit N]
"""

from __future__ import annotations

import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_urls as cu  # noqa: E402  (distinctive(), PORTALS, UA, TIMEOUT)

ROOT = Path(__file__).resolve().parents[1]
DIST_CAMPS = ROOT / "dist" / "v1" / "current" / "camps.json"
WORKERS = 4
# council pages likely to list camps, tried after the homepage
CAMPY = re.compile(r"camp|outdoor|propert|facilit|reservation|ranch|base", re.I)
MAX_INDEX_PAGES = 4


def fetch(url: str) -> str | None:
    req = urllib.request.Request(url, headers={"User-Agent": cu.UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=cu.TIMEOUT) as r:
                ctype = (r.headers.get("Content-Type") or "").lower()
                if "html" not in ctype:
                    return None
                return r.read(500_000).decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(int(e.headers.get("Retry-After") or 0) or 15 * (attempt + 1))
                continue
            return None
        except Exception:
            if attempt < 2:
                time.sleep(2)
                continue
            return None
    return None


LINK_RE = re.compile(r"<a\s[^>]*href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", re.S | re.I)
TAG_RE = re.compile(r"<[^>]+>")


def links(html: str, base: str) -> list[tuple[str, str]]:
    """[(absolute_url, anchor_text), ...]"""
    out = []
    for href, text in LINK_RE.findall(html or ""):
        try:
            url = urllib.parse.urljoin(base, href.strip())
        except ValueError:
            continue
        if not url.startswith("http"):
            continue
        out.append((url, TAG_RE.sub(" ", text).strip().lower()))
    return out


def is_portal(url: str) -> bool:
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    return any(p in host for p in cu.PORTALS)


def council_pages(site: str) -> list[tuple[str, str]]:
    """Homepage links plus links from a few camping-ish index pages, one level down."""
    home = fetch(site)
    if home is None:
        return []
    found = links(home, site)
    seen = {site.rstrip("/")}
    idx = [u for u, t in found
           if (CAMPY.search(t) or CAMPY.search(u)) and not is_portal(u)
           and urllib.parse.urlparse(u).netloc == urllib.parse.urlparse(site).netloc]
    for u in idx[:MAX_INDEX_PAGES]:
        if u.rstrip("/") in seen:
            continue
        seen.add(u.rstrip("/"))
        sub = fetch(u)
        time.sleep(0.3)
        if sub:
            found += links(sub, u)
    return found


DOCEXT = re.compile(r"\.(pdf|docx?|xlsx?|pptx?|jpe?g|png|gif|svg|zip)(\?|$)", re.I)


def path_depth(url: str) -> int:
    """Path segments. A camp's own page is usually shallower than a page about one of its
    programmes (…/bear-paw/ beats …/bear-paw/apiary/), so this breaks score ties."""
    return len([s for s in urllib.parse.urlparse(url).path.split("/") if s])


def score(camp_name: str, url: str, text: str) -> int:
    """How strongly a link looks like THIS camp's page."""
    toks = cu.distinctive(camp_name)
    if not toks:
        return 0
    slug = re.sub(r"[^a-z0-9]+", " ", url.lower())
    hits_text = sum(1 for t in toks if re.search(rf"\b{re.escape(t)}\b", text))
    hits_url = sum(1 for t in toks if re.search(rf"\b{re.escape(t)}\b", slug))
    s = hits_text * 2 + hits_url            # anchor text is stronger evidence than a slug
    if hits_text == len(toks) or hits_url == len(toks):
        s += 2                              # every distinctive token present
    return s


def confirm(url: str, camp_name: str) -> bool:
    html = fetch(url)
    if html is None:
        return False
    body = html.lower()
    toks = cu.distinctive(camp_name)
    return any(re.search(rf"\b{re.escape(t)}\b", body) for t in toks)


def main() -> None:
    args = sys.argv[1:]
    out_path = Path(args[args.index("--out") + 1]) if "--out" in args else ROOT / ".workbench" / "portal_candidates.json"
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    if not DIST_CAMPS.exists():
        raise SystemExit(f"missing {DIST_CAMPS} — run tools/build.py first")

    camps = [c for c in json.loads(DIST_CAMPS.read_text("utf-8"))["items"]
             if c["camp_type"] != "day_camp" and is_portal(c.get("website") or "")]
    camps.sort(key=lambda c: c["id"])
    by_council: dict[str, list[dict]] = defaultdict(list)
    for c in camps:
        by_council[c.get("council") or "?"].append(c)
    councils = sorted(by_council)
    if limit:
        councils = councils[:limit]

    out_path.parent.mkdir(parents=True, exist_ok=True)
    results = json.loads(out_path.read_text("utf-8")) if out_path.exists() else []
    done = {r["council"] for r in results}
    todo = [k for k in councils if k not in done]
    print(f"crawling {len(todo)} councils ({len(done)} done) covering "
          f"{sum(len(by_council[k]) for k in todo)} portal camps, {WORKERS} workers")

    def work(cref: str) -> list[dict]:
        group = by_council[cref]
        site = group[0].get("council_website")
        rows = []
        found = council_pages(site) if site else []
        for camp in group:
            row = {"council": cref, "council_website": site, "id": camp["id"],
                   "name": camp["name"], "portal_url": camp.get("website"),
                   "candidate": None, "anchor": None, "score": 0, "confirmed": False}
            best = None
            site_host = urllib.parse.urlparse(site).netloc.lower().removeprefix("www.") if site else ""
            for url, text in found:
                if is_portal(url) or DOCEXT.search(url):
                    continue
                s = score(camp["name"], url, text)
                if not s:
                    continue
                # Rank: the council's OWN domain first, then score, then the shallower path.
                # Host has to dominate — a bare root elsewhere otherwise wins on depth alone, which
                # picked the Illinek OA lodge and the Buffalo Bill museum over the real camp pages.
                same = urllib.parse.urlparse(url).netloc.lower().removeprefix("www.") == site_host
                key = (same, s, -path_depth(url))
                if best is None or key > best[0]:
                    best = (key, url, text)
            if best:
                row["score"], row["candidate"], row["anchor"] = best[0][1], best[1], best[2][:80]
                row["same_host"] = best[0][0]
                row["confirmed"] = confirm(best[1], camp["name"])
                time.sleep(0.3)
            rows.append(row)
        return rows

    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for i, rows in enumerate(ex.map(work, todo), 1):
                results.extend(rows)
                if i % 10 == 0:
                    out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                                        encoding="utf-8", newline="\n")
                    print(f"  {i}/{len(todo)} councils", flush=True)
    finally:
        out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8", newline="\n")

    ok = [r for r in results if r["confirmed"]]
    print(f"\nwrote {out_path}")
    print(f"  {len(ok)} of {len(results)} portal camps have a confirmed candidate page")


if __name__ == "__main__":
    main()
