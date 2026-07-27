"""Seed generator for HISTORICAL merit badge requirement-sets.

Until now every badge carried exactly one requirement-set (the current edition, from
OpenScouting/workbooks), so `supersedes` chains existed for ranks but not badges and the
question "which requirements applied when my Scout started" was unanswerable for badges.

Source: the U.S. Scouting Service Project (usscouts.org), which mirrors official requirements
per badge at /mb/mbNNN.asp AND keeps the preceding edition at /mb/Old/mbNNN-YY.asp. Each page
carries a Dreamweaver editable region naming its revision type and effective date, so editions
are dated from the source rather than guessed. That yields up to two recoverable historical
editions per badge, because usscouts' "current" page often trails the newest booklet that
workbooks tracks.

Requirement TEXT is verbatim Scouting America copyright: every emitted set carries
includes_official_text=true + text_rights, exactly like the rank history and the current sets.
Structure/numbering come from the pages' nested <ol>/<li> markup; `choose` is read from
"do TWO of the following" style parent text. method=scraped, confidence 0.8.

Editions are deduped BY TEXT, never by claimed date: if a scraped edition's normalized
requirement text matches a set we already hold, it is the same edition under a different label
and is skipped. Fetches are cached under .workbench/ so re-runs are deterministic and polite.

    python tools/seed_merit_badge_history.py            # write data/requirement-sets/*
    python tools/seed_merit_badge_history.py --dry-run  # report only
"""
from __future__ import annotations

import json
import re
import ssl
import sys
import time
import urllib.parse
import urllib.request
from datetime import date, timedelta
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = ROOT / ".workbench" / "mbhist_cache"
SCHEMA = "https://sethmay.github.io/open-scout-api/schema/v1/requirement-set.schema.json"
TEXT_RIGHTS = ("Requirement text \u00a9 Scouting America, reproduced with attribution for "
               "non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. "
               "See NOTICE.md.")
UA = {"User-Agent": "open-scout-api requirement-history seed (github.com/sethmay/open-scout-api)"}
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
CHOOSE = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
          "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}


def fetch(url: str) -> str:
    CACHE.mkdir(parents=True, exist_ok=True)
    key = CACHE / (re.sub(r"[^a-z0-9]+", "_", url.lower()) + ".html")
    if key.exists():
        return key.read_text("utf-8")
    body = urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                  timeout=40, context=CTX).read(900_000).decode("utf-8", "ignore")
    key.write_text(body, encoding="utf-8")
    time.sleep(0.45)          # be polite to a volunteer-run site
    return body


def editable(html: str, name: str) -> str | None:
    m = re.search(r'#BeginEditable "' + re.escape(name) + r'"\s*-->(.*?)<!--\s*#EndEditable',
                  html, re.S)
    if not m:
        return None
    v = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).strip()
    return v or None


def _label(depth: int, i: int, parent: str) -> str:
    if depth == 0:
        return str(i)
    if depth == 1:
        return f"{parent}{chr(ord('a') + i - 1)}"
    return f"{parent}({i})"


class ReqParser(HTMLParser):
    """Nested <ol>/<li> -> Requirement nodes with official-style numbering."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.depth = -1
        self.root: list[dict] = []
        self.stack: list[tuple[list, str]] = []
        self.counter: list[int] = []
        self.li: list[dict] = []
        self.buf: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "ol":
            if self.li:
                self.li[-1].setdefault("children", [])
                self.stack.append((self.li[-1]["children"], self.li[-1]["number"]))
            else:
                self.stack.append((self.root, ""))
            self.depth += 1
            self.counter.append(0)
        elif tag == "li" and self.stack:
            self._flush()
            self.counter[-1] += 1
            lst, parent = self.stack[-1]
            node = {"number": _label(self.depth, self.counter[-1], parent), "text": None}
            lst.append(node)
            self.li.append(node)
            self.buf = []

    def handle_endtag(self, tag):
        if tag == "li":
            self._flush()
            if self.li:
                self.li.pop()
        elif tag == "ol":
            if self.stack:
                self.stack.pop()
            if self.counter:
                self.counter.pop()
            self.depth -= 1

    def handle_data(self, d):
        if self.li:
            self.buf.append(d)

    def _flush(self):
        if self.li and self.buf:
            t = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            if t:
                prev = self.li[-1]["text"]
                self.li[-1]["text"] = (prev + " " + t) if prev else t
            self.buf = []


def _set_choose(nodes: list[dict]) -> list[dict]:
    for n in nodes:
        kids = n.get("children") or []
        if kids and n.get("text"):
            m = re.search(r"\bdo\s+(one|two|three|four|five|six|seven|eight|nine|ten)\s+of\b",
                          n["text"], re.I)
            if m:
                n["choose"] = CHOOSE[m.group(1).lower()]
        _set_choose(kids)
    return nodes


def parse_requirements(html: str) -> list[dict] | None:
    m = re.search(r'<div id="requirements">(.*?)(?=<div id="footnotes"|<div id="footer"|</body>)',
                  html, re.S | re.I)
    if not m:
        return None
    p = ReqParser()
    p.feed(m.group(1))
    p.close()
    tree = _set_choose(p.root)
    return tree or None


def flat_text(nodes: list[dict]) -> str:
    """Normalized text of a whole tree, for edition-identity comparison."""
    out: list[str] = []

    def walk(rs):
        for r in rs:
            out.extend(re.findall(r"[a-z0-9]+", (r.get("text") or "").lower()))
            walk(r.get("children") or [])
    walk(nodes)
    return " ".join(out)


def parse_rev_date(raw: str | None, fallback_year: int | None) -> str | None:
    """'January 1, 2024' -> '2024-01-01'; tolerate the page's stray nbsp/typo years."""
    if raw:
        m = re.search(r"([A-Z][a-z]+)\s+(\d{1,2}),\s*(\d{4})", raw)
        if m:
            try:
                mon = ["january", "february", "march", "april", "may", "june", "july", "august",
                       "september", "october", "november", "december"].index(m.group(1).lower()) + 1
                return f"{int(m.group(3)):04d}-{mon:02d}-{int(m.group(2)):02d}"
            except ValueError:
                pass
        m = re.search(r"\b(19|20)\d{2}\b", raw)
        if m:
            return f"{m.group(0)}-01-01"
    return f"{fallback_year}-01-01" if fallback_year else None


def day_before(iso: str) -> str:
    y, m, d = (int(x) for x in iso.split("-"))
    return (date(y, m, d) - timedelta(days=1)).isoformat()


def main() -> None:
    dry = "--dry-run" in sys.argv
    mp = json.loads((ROOT / ".workbench" / "badge_mb_ids.json").read_text("utf-8"))

    current: dict[str, dict] = {}
    for p in sorted((DATA / "requirement-sets").glob("*.json")):
        d = json.loads(p.read_text("utf-8"))
        s = d.get("subject") or ""
        if s.startswith("merit-badge:"):
            current[s.split(":", 1)[1]] = {"path": p, "doc": d}

    written, skipped, chained, problems = [], [], [], []
    for bid, mb in sorted(mp.items()):
        cur = current.get(bid)
        if not cur:
            problems.append((bid, "no current requirement-set"))
            continue
        have_text = {flat_text(cur["doc"]["requirements"])}
        base = f"http://usscouts.org/mb/{mb}.asp"
        editions: list[dict] = []          # newest first
        try:
            live = fetch(base)
        except Exception as e:              # noqa: BLE001
            problems.append((bid, f"live fetch {type(e).__name__}"))
            continue
        tree = parse_requirements(live)
        rev = parse_rev_date(editable(live, "revision-date"), None)
        if tree and rev:
            editions.append({"tree": tree, "from": rev, "url": base,
                             "title": f"{cur['doc']['source_document'].get('title','').split(' Merit')[0]} "
                                      f"Merit Badge Requirements ({rev[:4]}, usscouts.org mirror)"})
        olds = [h for h in re.findall(r'href="([^"]+)"', live) if re.search(r"(^|/)old/mb", h, re.I)]
        if olds:
            ourl = urllib.parse.urljoin(base, olds[0])
            try:
                ohtml = fetch(ourl)
                otree = parse_requirements(ohtml)
                ym = re.search(r"-(\d{2})\.asp", ourl)
                oyear = 2000 + int(ym.group(1)) if ym else None
                ofrom = parse_rev_date(editable(ohtml, "revision-date"), oyear)
                if otree and ofrom:
                    editions.append({"tree": otree, "from": ofrom, "url": ourl,
                                     "title": f"{cur['doc']['source_document'].get('title','').split(' Merit')[0]} "
                                              f"Merit Badge Requirements ({ofrom[:4]}, usscouts.org mirror)"})
            except Exception as e:          # noqa: BLE001
                problems.append((bid, f"old fetch {type(e).__name__}"))

        # drop editions whose text we already hold, and internal duplicates
        # An edition is identified by TEXT; its id is <badge>-<year>, so a year already
        # taken by another edition of the same badge would silently overwrite it. Same year
        # + different text means one of the two labels is wrong, and we cannot tell which,
        # so the older claimant is dropped rather than given an invented date.
        keep = []
        years = {cur["doc"]["effective_from"][:4]}
        for ed in editions:
            ft = flat_text(ed["tree"])
            if len(ft) < 80:
                problems.append((bid, f"thin parse at {ed['url'].split('/')[-1]}"))
                continue
            if ft in have_text:
                skipped.append((bid, ed["from"], "same text as an edition we hold"))
                continue
            if ed["from"][:4] in years:
                skipped.append((bid, ed["from"], "year already claimed by another edition (ambiguous label)"))
                continue
            years.add(ed["from"][:4])
            have_text.add(ft)
            keep.append(ed)
        keep.sort(key=lambda e: e["from"], reverse=True)
        if not keep:
            continue

        # chain: our current set -> newest scraped -> older scraped
        newer_from = cur["doc"]["effective_from"]
        ids = []
        for ed in keep:
            sid = f"{bid}-{ed['from'][:4]}"
            ids.append(sid)
            doc = {
                "$schema": SCHEMA, "id": sid, "kind": "requirement-set",
                "subject": f"merit-badge:{bid}",
                "effective_from": ed["from"],
                # half-open: a window closes on the date its successor took effect (see
                # tools/requirement_windows.py)
                "effective_to": newer_from if newer_from > ed["from"] else None,
                "supersedes": None,
                "source_document": {"title": ed["title"], "url": ed["url"], "year": int(ed["from"][:4])},
                "includes_official_text": True,
                "text_rights": TEXT_RIGHTS,
                "requirements": ed["tree"],
                "notes": ("Historical edition recovered from the usscouts.org mirror, which keeps the "
                          "preceding edition of each badge alongside the current one. Effective date "
                          "is the date the source page states; the end date is the day before the "
                          "next edition we hold began."),
                "provenance": {"sources": [{"url": ed["url"], "accessed": date.today().isoformat()}],
                               "method": "scraped", "verified_at": date.today().isoformat(),
                               "confidence": 0.8},
            }
            written.append(doc)
            newer_from = ed["from"]
        # link supersedes newest->oldest, then point our current set at the newest scraped
        for i, sid in enumerate(ids):
            nxt = ids[i + 1] if i + 1 < len(ids) else None
            for doc in written:
                if doc["id"] == sid and nxt:
                    doc["supersedes"] = f"requirement-set:{nxt}"
        chained.append((cur["path"], f"requirement-set:{ids[0]}"))

    print(f"badges processed: {len(mp)}")
    print(f"historical editions to write: {len(written)}")
    print(f"editions skipped as already-held text: {len(skipped)}")
    print(f"current sets to chain: {len(chained)}")
    if problems:
        print(f"problems: {len(problems)}")
        for b, why in problems[:15]:
            print(f"   {b}: {why}")
    if dry:
        return
    for doc in written:
        (DATA / "requirement-sets" / f"{doc['id']}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for path, ref in chained:
        d = json.loads(path.read_text("utf-8"))
        d["supersedes"] = ref
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8", newline="\n")
    print(f"wrote {len(written)} historical sets; chained {len(chained)} current sets")


if __name__ == "__main__":
    main()
