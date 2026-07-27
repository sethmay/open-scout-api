"""Audit camp program `features` against the sources each camp record itself cites.

`validate_data.py` gates features on *vocabulary membership* — "zero invented codes" means every
code exists, not that any camp offers it. Nothing in the pipeline can know what a web page says, so
two failure modes shipped, one in each direction:

  * **A claim no source attests.** Camp Baker carried `mountain_biking` and `pool`. Both were
    inherited from camp-finder's single LLM-extracted record, whose own provenance note said
    "features inferred" (confidence 0.82). The later camp-page survey rewrote that camp's list,
    added 23 page-attested features, and stamped the whole record `features_source_tier: camp_page`
    — laundering an admitted inference into something that looks page-verified. Its page mentions
    biking nowhere and has no pool; it swims in Siltcoos Lake.
  * **A survey that stopped at an index page.** Camp Parsons was surveyed from three pages of
    ~5 KB each, none of which mention the ATV program that has its own section at
    `campparsons.org/program/` — never fetched. 11 features recorded where ~22 are evidenced.

So: fetch each camp's cited sources plus any program page they link to, and report per camp the
features with no lexical trace, the vocabulary terms those pages name but the record omits, and the
program pages provenance never cites.

REPORT ONLY, and that is not timidity — lexical matching provably cannot settle these. On the very
camps this tool was built for it flags `rappelling` (the page says "the final rappel"),
misses nothing at `black_powder` (the page says "muzzleloading", which the vocabulary knows as an
alias), and would happily "find" `golf` in Camp Parsons' *Whiffle Ball* Golf Tournament. Treat every
line as a lead for a human, then edit `data/camps/` by hand — the discipline `tools/maintenance.py`
already uses.

    python tools/audit_camp_features.py --camps or-camp-baker,wa-camp-parsons
    python tools/audit_camp_features.py --all --limit 40
    python tools/audit_camp_features.py --all

Pages cache under `.workbench/campaudit/`, so re-runs are free and councils' sites are fetched once.
"""

from __future__ import annotations

import argparse
import html
import json
import pathlib
import re
import ssl
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = ROOT / ".workbench" / "campaudit"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/140.0 Safari/537.36"}
# Words that attest nothing on a Scout camp page. A term whose every token is here cannot be
# checked lexically at all, and is reported as UNVERIFIABLE rather than as a defect.
STOP = {"program", "programs", "area", "areas", "center", "centre", "camp", "camps", "scout",
        "scouts", "option", "options", "facility", "facilities", "lodge", "field", "fields",
        "sports", "course", "courses", "activity", "activities", "study", "hall", "site", "sites",
        "tents", "tent", "shelter", "shelters", "trail", "trails", "water", "high", "adventure",
        "first", "year", "older", "open", "large", "small", "new", "house", "public", "private"}
PROGRAM_HINTS = ("program", "programme", "activities", "summer-camp", "summercamp",
                 "resident-camp", "merit-badge", "what-we-offer", "our-camp", "camp-life")
PREFIX = 5          # "rappelling"[:5] == "rappe" matches the page's "rappel"


def _ctx():
    c = ssl.create_default_context(); c.check_hostname = False; c.verify_mode = ssl.CERT_NONE
    return c


def fetch(url: str, delay: float = 0.6) -> str | None:
    """Cached page text plus its same-host links. None when unreadable."""
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / (re.sub(r"[^a-z0-9]+", "_", url.lower())[:150] + ".txt")
    if cached.exists():
        return cached.read_text("utf-8", errors="ignore")
    try:
        raw = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30,
                                     context=_ctx()).read(1_200_000).decode("utf-8", "ignore")
    except Exception:
        cached.write_text("", encoding="utf-8")          # negative cache; do not re-hammer
        return None
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", raw, flags=re.S | re.I)
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
    links = []
    for href in re.findall(r'<a[^>]+href="([^"#?]+)"', raw, re.I):
        u = urllib.parse.urljoin(url, href)
        if urllib.parse.urlparse(u).netloc == urllib.parse.urlparse(url).netloc:
            links.append(u)
    cached.write_text(text + "\n<!--LINKS-->\n" + "\n".join(sorted(set(links))), encoding="utf-8")
    time.sleep(delay)
    return cached.read_text("utf-8", errors="ignore")


def split_cache(blob: str) -> tuple[str, list[str]]:
    text, _, links = blob.partition("\n<!--LINKS-->\n")
    return text, [l for l in links.splitlines() if l.strip()]


def probes(term: dict) -> tuple[list[str], list[str]]:
    """(phrases, tokens). A phrase hit is strong evidence; a token hit only rules out fabrication."""
    names = [term["code"].replace("_", " "), term.get("label", "")]
    names += [a.replace("_", " ") for a in term.get("aliases", [])]
    phrases, tokens = [], set()
    for n in names:
        words = re.findall(r"[a-z]+", n.lower())
        if len(words) > 1:
            phrases.append(" ".join(words))
        tokens |= {w for w in words if len(w) > 3 and w not in STOP}
    return phrases, sorted(tokens)


def hits(page: str, phrases: list[str], tokens: list[str]) -> tuple[list[str], list[str]]:
    return ([p for p in phrases if p in page],
            [t for t in tokens if re.search(r"\b" + re.escape(t[:PREFIX]), page)])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--camps", help="comma-separated camp ids")
    ap.add_argument("--all", action="store_true", help="every camp with features_verified_at")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    vocab = json.loads((DATA / "vocab" / "camp-features.json").read_text("utf-8"))["terms"]
    by_code = {t["code"]: t for t in vocab}
    camps = []
    for p in sorted((DATA / "camps").glob("*.json")):
        if p.name == "_events.json":
            continue
        d = json.loads(p.read_text("utf-8"))
        v = next((x for x in d["versions"] if x.get("valid_to") is None), None)
        if v is not None:
            camps.append((d["id"], v))
    if args.camps:
        want = {c.strip() for c in args.camps.split(",")}
        camps = [c for c in camps if c[0] in want]
    elif args.all:
        camps = [c for c in camps if c[1].get("features_verified_at")]
    else:
        ap.error("pass --camps or --all")
    if args.limit:
        camps = camps[: args.limit]

    tot = {"unsupported": 0, "missing": 0, "unread": 0, "unreadable": 0}
    for cid, v in camps:
        urls = ([v["website"]] if v.get("website") else []) + \
               [s["url"] for s in v["provenance"].get("sources", []) if s.get("url")]
        read, page, links = [], "", []
        for u in dict.fromkeys(urls):
            blob = fetch(u)
            if not blob:
                continue
            t, l = split_cache(blob)
            if t.strip():
                read.append(u); page += " " + t.lower(); links += l
        if not page.strip():
            tot["unreadable"] += 1
            print(f"\n## {cid}: none of {len(urls)} cited source(s) readable — cannot audit")
            continue
        unread = [l for l in dict.fromkeys(links)
                  if any(h in l.lower() for h in PROGRAM_HINTS)
                  and l.rstrip("/") not in {u.rstrip("/") for u in read}]
        claimed = {f["code"] for f in (v.get("features") or [])}
        unsupported, unverifiable, missing = [], [], []
        for code in sorted(claimed):
            term = by_code.get(code)
            if term is None:
                continue
            ph, tk = probes(term)
            # A term whose every word is generic ("Older Scout Program", "High Adventure Option")
            # cannot be confirmed OR denied by word matching — saying "no trace" would be a lie
            # dressed as a finding.
            if not tk:
                unverifiable.append(code); continue
            h_ph, h_tk = hits(page, ph, tk)
            if not h_ph and not h_tk:
                unsupported.append(code)
        claimed_parents = {by_code[c].get("broader") for c in claimed if c in by_code}
        for term in vocab:
            code = term["code"]
            if code in claimed:
                continue
            # Do not report a coarse parent when a leaf under it is already recorded: a page
            # saying "Climbing" over a tower we already have as `climbing_tower` is not an omission.
            if code in claimed_parents:
                continue
            if hits(page, *probes(term))[0]:            # phrase-level only, to keep noise down
                missing.append(code)
        if not (unsupported or missing or unread):
            continue
        print(f"\n## {cid}  ({len(claimed)} features, tier={v.get('features_source_tier')}, "
              f"{len(read)}/{len(urls)} source page(s) read)")
        if unsupported:
            tot["unsupported"] += len(unsupported)
            print(f"   NO LEXICAL TRACE: {', '.join(unsupported)}")
        if missing:
            tot["missing"] += len(missing)
            print(f"   PAGE NAMES, RECORD OMITS: {', '.join(missing)}")
        if unread:
            tot["unread"] += len(unread)
            print(f"   PROGRAM PAGE NOT CITED: {', '.join(unread[:4])}")
        if unverifiable:
            print(f"   (not lexically checkable: {', '.join(unverifiable)})")
    print(f"\n{len(camps)} camp(s): {tot['unsupported']} with no lexical trace, "
          f"{tot['missing']} candidate omission(s), {tot['unread']} uncited program page(s), "
          f"{tot['unreadable']} unreadable. Every line is a lead for a human, not a verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
