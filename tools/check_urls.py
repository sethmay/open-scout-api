"""Audit each camp's stored `website` and classify what is actually there (maintenance tool).

The 0.30.0 features spike found that a stored camp URL frequently does not describe its camp:
of 10 sampled, 5 pointed at a different camp, a dead registration link, the BSA health-record
PDF, a church-hosted day camp, or a six-year-stale event. Feature population depends on the
link, and so does the site's "visit official page" call to action, so the links get audited
before anything is read off them.

For every current camp (day camps excluded — their property link is weak by nature, since a
day camp often runs at a rented site) this fetches the stored URL, follows redirects, and
classifies the result:

  ok           page loads and mentions the camp
  redirect     loads and mentions the camp, but the final URL differs -> canonicalise it
  no_name      page loads but never names the camp (generic index, wrong camp, or image-only)
  portal       a registration platform rather than a descriptive page (nothing to survey)
  document     the URL is a PDF/office document, not a page
  stale        newest year on the page is well in the past (a dead event)
  http_error   4xx/5xx
  unreachable  DNS/TLS/timeout failure

Findings are advisory: `no_name` in particular needs a human look, since some real camp pages
carry their name only inside images. Nothing is written to data/; repairs are deliberate edits.

Writes a JSON report (default .workbench/url_health.json, git-ignored — link health is a
point-in-time observation, not durable data). Run manually; NOT part of the CI build.

Usage: python tools/check_urls.py [--out PATH] [--limit N]
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST_CAMPS = ROOT / "dist" / "v1" / "current" / "camps.json"
UA = "open-scout-api link audit (github.com/sethmay/open-scout-api)"
PORTALS = ("scoutingevent.com", "247scouting.com", "tentaroo.com", "campreservation.com",
           "doubleknot.com", "blackpug")
DOCTYPES = ("application/pdf", "application/msword", "application/vnd.openxml")
# words that do not distinguish one camp from another
STOP = {"camp", "camps", "scout", "scouts", "scouting", "reservation", "reserve", "base",
        "ranch", "high", "adventure", "bsa", "america", "the", "and", "at", "of", "center",
        "centre", "council", "summer", "resident", "program", "area", "park"}
WORKERS = 3
TIMEOUT = 12          # a camp page that cannot answer in 12s is itself a finding


def distinctive(name: str) -> list[str]:
    """The tokens that actually identify this camp, longest first."""
    toks = [t for t in re.split(r"[^a-z0-9]+", name.lower()) if len(t) > 2 and t not in STOP]
    return sorted(set(toks), key=len, reverse=True)


def _content_text(body: str) -> str:
    """Body with scripts, styles, and copyright lines removed. Script blocks carry cookie and
    cache timestamps (2038 turns up constantly) and every footer carries the current year, so
    neither is evidence about when the page's CONTENT was written."""
    txt = re.sub(r"<(script|style|noscript)\b.*?</\1>", " ", body, flags=re.S)
    return re.sub(r"[^\n]*(?:&copy;|©|copyright|all rights reserved)[^\n]*", " ", txt)


def _norm_url(u: str) -> str:
    return re.sub(r"^https?://(www\.)?", "", (u or "").rstrip("/").lower())


def check(camp: dict) -> dict:
    url = camp.get("website") or ""
    out = {"id": camp["id"], "name": camp["name"], "camp_type": camp["camp_type"],
           "url": url, "final_url": None, "status": None, "verdict": None, "note": None}
    if not url:
        out["verdict"] = "no_website"
        return out
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                final = r.geturl()
                ctype = (r.headers.get("Content-Type") or "").lower()
                body = r.read(400_000).decode("utf-8", "ignore").lower()
                out["status"], out["final_url"] = r.status, final
            break
        except urllib.error.HTTPError as e:
            # 429 usually means THIS audit was too eager, not that the link is broken. Back off
            # and retry before recording a failure against the council.
            if e.code == 429 and attempt < 2:
                time.sleep(int(e.headers.get("Retry-After") or 0) or 15 * (attempt + 1))
                continue
            out["status"], out["verdict"] = e.code, "http_error"
            return out
        except Exception as e:                                # DNS, TLS, timeout, redirect loop
            if attempt < 2:
                time.sleep(3)
                continue
            out["verdict"], out["note"] = "unreachable", type(e).__name__
            return out

    host = re.sub(r"^https?://", "", final).split("/")[0]
    toks = distinctive(camp["name"])
    # word-boundary, not substring: 'lick' (Elk Lick) otherwise matches 'click' and 'publickey'
    named = any(re.search(rf"\b{re.escape(t)}\b", body) for t in toks) if toks else True
    years = [int(y) for y in re.findall(r"\b(20[0-3]\d)\b", _content_text(body))]
    newest = max(years) if years else None

    if any(d in ctype for d in DOCTYPES):
        out["verdict"], out["note"] = "document", ctype.split(";")[0]
    elif any(p in host for p in PORTALS):
        # A registration platform is not a descriptive page whether or not it names the camp.
        out["verdict"] = "portal"
        out["note"] = ("names the camp" if named else "does not name the camp")
        if newest and newest < 2025:
            out["note"] += f"; newest content year {newest}"
    elif not named:
        out["verdict"], out["note"] = "no_name", f"looked for {toks[:3]}"
    elif newest and newest < 2025:
        out["verdict"], out["note"] = "stale", f"newest content year {newest}"
    elif _norm_url(final) != _norm_url(url):
        out["verdict"] = "redirect"
    else:
        out["verdict"] = "ok"
    return out


def main() -> None:
    args = sys.argv[1:]
    out_path = Path(args[args.index("--out") + 1]) if "--out" in args else ROOT / ".workbench" / "url_health.json"
    limit = int(args[args.index("--limit") + 1]) if "--limit" in args else None
    if not DIST_CAMPS.exists():
        raise SystemExit(f"missing {DIST_CAMPS} — run tools/build.py first")
    camps = [c for c in json.loads(DIST_CAMPS.read_text("utf-8"))["items"]
             if c["camp_type"] != "day_camp"]
    camps.sort(key=lambda c: c["id"])
    if limit:
        camps = camps[:limit]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    # Resume: a full pass takes a while (dead hosts burn the whole timeout), so results are
    # checkpointed and an interrupted run picks up where it stopped.
    results: list[dict] = json.loads(out_path.read_text("utf-8")) if out_path.exists() else []
    done = {r["id"] for r in results}
    todo = [c for c in camps if c["id"] not in done]
    print(f"auditing {len(todo)} camps ({len(done)} already done, day camps excluded), "
          f"{WORKERS} workers")

    def flush():
        out_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n",
                            encoding="utf-8", newline="\n")

    def run(c):
        r = check(c)
        time.sleep(0.2)                                      # politeness
        return r
    try:
        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            for i, r in enumerate(ex.map(run, todo), 1):
                results.append(r)
                if i % 25 == 0:
                    flush()
                    print(f"  {len(results)}/{len(camps)}", flush=True)
    finally:
        flush()
    from collections import Counter
    tally = Counter(r["verdict"] for r in results)
    print(f"\nwrote {out_path}")
    for v, n in tally.most_common():
        print(f"  {n:4}  {v}")
    bad = sum(n for v, n in tally.items() if v != "ok")
    print(f"\n{bad} of {len(results)} camps have a link worth attention")


if __name__ == "__main__":
    main()
