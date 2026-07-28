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

So: read each camp's cited sources AND the program pages and PDFs they link to, then report per
camp the features with no lexical trace, the vocabulary terms those pages name but the record
omits, and which URL attests what.

**Evidence is per source, never against the concatenation.** Merging every page into one blob is
the exact bug that produced both defects above: a council-wide page can attest a feature belonging
to a *different* camp of that council, and the merged text cannot tell you which page spoke. Every
finding here therefore carries the URL that produced it, so "attested only by the council's camping
index" is visible as the weak evidence it is.

**PDFs are read.** Leaders' guides were the richest source in the 0.38.0 wave (`guide` camps
average 21 features against 13 for `camp_page`), and a guide is usually a PDF the HTML survey
skipped.

REPORT ONLY, and that is not timidity — lexical matching provably cannot settle these. On the very
camps this tool was built for it flags `rappelling` (the page says "the final rappel"),
misses nothing at `black_powder` (the page says "muzzleloading", which the vocabulary knows as an
alias), and would happily "find" `golf` in Camp Parsons' *Whiffle Ball* Golf Tournament. Treat every
line as a lead for a human, then edit `data/camps/` by hand — the discipline `tools/maintenance.py`
already uses.

    python tools/audit_camp_features.py --camps or-camp-baker,wa-camp-parsons
    python tools/audit_camp_features.py --all --limit 40
    python tools/audit_camp_features.py --all --out .workbench/audit.json

Pages cache under `.workbench/campaudit/`, so re-runs are free and councils' sites are fetched once.
Be polite: this walks hundreds of volunteer-run council sites. The fetcher rate-limits per host,
honours `Retry-After`, and retries transient failures instead of poisoning the cache with them —
the 0.34.0 survey libelled 35 camps' sites by hammering them into 429s. Do not remove that.
"""

from __future__ import annotations

import argparse
import collections
import html
import io
import json
import pathlib
import re
import ssl
import time
import urllib.error
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
                 "resident-camp", "merit-badge", "what-we-offer", "our-camp", "camp-life",
                 "leaders-guide", "leader-guide", "guidebook", "guide")
PREFIX = 5          # "rappelling"[:5] == "rappe" matches the page's "rappel"
MAX_EXTRA = 5       # linked program pages/PDFs read per camp, best-looking first
HOST_DELAY = 1.5    # seconds between requests to the SAME host
_last_hit: dict[str, float] = {}


def _ctx():
    c = ssl.create_default_context(); c.check_hostname = False; c.verify_mode = ssl.CERT_NONE
    return c


def _pdf_text(raw: bytes) -> str:
    try:
        from pypdf import PdfReader
        r = PdfReader(io.BytesIO(raw))
        return " ".join((p.extract_text() or "") for p in r.pages[:40])
    except Exception:
        return ""


def _docx_text(raw: bytes) -> str:
    """A .docx is a ZIP. Decoding it as UTF-8 yields 600 KB of XML noise that looks like a page.

    Muskingum Valley cites its leaders' guide as .docx; the audit "read" 594 KB of that archive,
    found the camp's name 72 times inside the markup, and reported 24 of its 35 features as
    unattested. Scoring evidence against binary is worse than having none.
    """
    try:
        import zipfile
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
        return html.unescape(re.sub(r"<[^>]+>", " ", xml))
    except Exception:
        return ""


def _looks_binary(text: str) -> bool:
    """True when a decode produced bytes-as-mojibake rather than prose."""
    sample = text[:4000]
    if not sample:
        return False
    odd = sum(1 for c in sample if not (c.isprintable() or c.isspace()) or ord(c) > 0x2E00)
    return odd / len(sample) > 0.15


def _throttle(url: str) -> None:
    host = urllib.parse.urlparse(url).netloc
    wait = HOST_DELAY - (time.time() - _last_hit.get(host, 0))
    if wait > 0:
        time.sleep(wait)
    _last_hit[host] = time.time()


def fetch(url: str) -> str | None:
    """Cached page text plus its same-host links. None when unreadable.

    A transient failure is NOT cached: negative-caching a 429 or a timeout turns "the site was busy
    for a second" into "this camp has no readable source" permanently, which is how an audit
    manufactures findings about sites that are fine.
    """
    CACHE.mkdir(parents=True, exist_ok=True)
    cached = CACHE / (re.sub(r"[^a-z0-9]+", "_", url.lower())[:150] + ".txt")
    if cached.exists():
        return cached.read_text("utf-8", errors="ignore")
    raw, ctype = None, ""
    for attempt in range(3):
        _throttle(url)
        try:
            r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30,
                                       context=_ctx())
            ctype = (r.headers.get("content-type") or "").lower()
            raw = r.read(40_000_000)   # a truncated PDF has no EOF marker and
                                       # pypdf rejects the whole file: a 4 MB cap
                                       # silently emptied 45 leaders' guides
            break
        except urllib.error.HTTPError as e:
            if e.code in (429, 503):
                time.sleep(min(float(e.headers.get("Retry-After") or 5) + 2 * attempt, 30))
                continue
            cached.write_text("", encoding="utf-8")      # a real 404/403: settled, cache it
            return None
        except Exception:
            time.sleep(2 + 3 * attempt)                  # transient: back off and retry
            continue
    if raw is None:
        return None                                      # give up WITHOUT caching the failure
    if raw[:5] == b"%PDF-" or "pdf" in ctype:
        text = re.sub(r"\s+", " ", _pdf_text(raw))
        if not text.strip():
            # Scanned or unparseable. Caching it as an empty page would make every feature the
            # guide attests look unsupported — the audit inventing defects out of its own blind
            # spot. Leave it uncached so a later run with a better extractor can try again.
            return None
        cached.write_text(text + "\n<!--LINKS-->\n", encoding="utf-8")
        return cached.read_text("utf-8", errors="ignore")
    if raw[:2] == b"PK" and (url.lower().endswith(".docx") or "word" in ctype
                             or "officedocument" in ctype):
        text = re.sub(r"\s+", " ", _docx_text(raw))
        if not text.strip():
            return None
        cached.write_text(text + "\n<!--LINKS-->\n", encoding="utf-8")
        return cached.read_text("utf-8", errors="ignore")
    decoded = raw.decode("utf-8", "ignore")
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", decoded, flags=re.S | re.I)
    text = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)))
    if _looks_binary(text):
        return None                                      # served bytes, not a page
    links = []
    for href in re.findall(r'<a[^>]+href="([^"#]+)"', decoded, re.I):
        u = urllib.parse.urljoin(url, href)
        if urllib.parse.urlparse(u).netloc == urllib.parse.urlparse(url).netloc:
            links.append(u)
    cached.write_text(text + "\n<!--LINKS-->\n" + "\n".join(sorted(set(links))), encoding="utf-8")
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
        # `len > 3` drops acronyms that ARE the whole term: `atv` vanished from its own probe, so
        # 16 camps whose pages plainly say "ATV" were reported as claiming it with no trace. A
        # one-word code is the term itself and always survives; multi-word names keep the filter,
        # which is what stops "sports"/"field" leaking in as evidence.
        keep = (lambda w: w not in STOP) if len(words) == 1 else \
               (lambda w: len(w) > 3 and w not in STOP)
        tokens |= {w for w in words if keep(w)}
    return phrases, sorted(tokens)


def roots(token: str) -> set[str]:
    """Prefixes that should count as naming this token.

    A fixed 5-character prefix demands the page use the LONGER form: `swimming` probes for
    "swimm", which never matches a page that says "swim", and `rowing` probes "rowin" against
    "row boats". Both were flagged as unsupported on dozens of camps that plainly have them.
    Stripping the inflection is the fix, and erring toward matching is the safe direction here:
    a missed flag costs nothing, while a false flag sends a human to re-verify a real feature.
    """
    out = {token[:PREFIX]}
    stem = re.sub(r"(mming|ing|es|s)$", "", token)
    if len(stem) >= 3:
        out.add(stem)
    return out


def hits(page: str, phrases: list[str], tokens: list[str]) -> tuple[list[str], list[str]]:
    return ([p for p in phrases if p in page],
            [t for t in tokens
             if any(re.search(r"\b" + re.escape(r), page) for r in roots(t))])


_chrome: dict[str, set[str]] = {}


def chrome_phrases(host: str, vocab: list[dict]) -> set[str]:
    """Vocabulary codes a host's NAVIGATION attests, learned from its homepage.

    Council sites carry the same header, menu and footer on every page, and those name real
    vocabulary: Chief Seattle Council's chrome says "Trading Post" (its gear shop) and "National
    Youth Leadership Training" (a council event). Match a camp page from that council and both
    appear to be attested for that camp — on EVERY camp that council owns. It is the same
    source-to-subject bleed as reading a council-wide page, except the page really is the camp's,
    so URL scoping cannot see it.

    The council homepage is a control: a phrase there is site chrome or council-level programme,
    not evidence about any one camp. Fetched once per host and reused across all its camps.
    """
    if host in _chrome:
        return _chrome[host]
    found: set[str] = set()
    blob = fetch(f"https://{host}/")
    if blob:
        text = split_cache(blob)[0].lower()
        for term in vocab:
            if hits(text, *probes(term))[0]:
                found.add(term["code"])
    _chrome[host] = found
    return found


def camp_tokens(cid: str, cited: list[str]) -> set[str]:
    """Strings that mark a URL as being about THIS camp rather than its council."""
    slug = re.sub(r"^[a-z]{2}-", "", cid)                 # "wa-camp-parsons" -> "camp-parsons"
    toks = {slug, slug.replace("-", ""), slug.replace("camp-", "")}
    return {t for t in toks if len(t) > 3}


def audit_camp(cid: str, v: dict, vocab: list[dict], by_code: dict) -> dict:
    cited = list(dict.fromkeys(([v["website"]] if v.get("website") else []) +
                               [s["url"] for s in v["provenance"].get("sources", [])
                                if s.get("url")]))
    pages: dict[str, str] = {}          # url -> lowercased text, kept SEPARATE on purpose
    links: list[str] = []
    for u in cited:
        blob = fetch(u)
        if not blob:
            continue
        t, l = split_cache(blob)
        if t.strip():
            pages[u] = t.lower(); links += l
    # Program pages and guide PDFs the record never cites. Reading them is where the coverage is:
    # Parsons' whole ATV programme lived one link past the page the survey stopped at.
    seen = {u.rstrip("/") for u in cited}
    # A host whose ROOT the record cites is the camp's own site, so everything on it is about this
    # camp. On a shared council host, only URLs naming the camp are — following /donate/ or
    # /advancement/ from a camp page is how a survey ends up quoting the council at itself.
    own_hosts = {urllib.parse.urlparse(u).netloc for u in cited
                 if urllib.parse.urlparse(u).path.strip("/") == ""}
    toks = camp_tokens(cid, cited)
    def about_this_camp(u: str) -> bool:
        pu = urllib.parse.urlparse(u)
        return pu.netloc in own_hosts or any(t in u.lower() for t in toks)
    extra = [l for l in dict.fromkeys(links)
             if l.rstrip("/") not in seen and about_this_camp(l)
             and (l.lower().endswith(".pdf") or any(h in l.lower() for h in PROGRAM_HINTS))]
    extra.sort(key=lambda u: (not u.lower().endswith(".pdf"), len(u)))   # PDFs first, then short
    read_extra = []
    for u in extra[:MAX_EXTRA]:
        blob = fetch(u)
        if not blob:
            continue
        t, _ = split_cache(blob)
        if t.strip():
            pages[u] = t.lower(); read_extra.append(u)

    unread_cited = [u for u in cited if u not in pages]
    claimed = {f["code"] for f in (v.get("features") or [])}
    out = {"id": cid, "tier": v.get("features_source_tier"), "claimed": len(claimed),
           "cited": cited, "read": sorted(pages), "read_extra": read_extra,
           "uncited_unread": [u for u in extra[MAX_EXTRA:]], "unread_cited": unread_cited,
           "unsupported": [], "unverifiable": [], "unverified": [], "missing": {}, "thin_evidence": {},
           "nav_only": {}}
    if not pages:
        out["unreadable"] = True
        return out
    for code in sorted(claimed):
        term = by_code.get(code)
        if term is None:
            continue
        ph, tk = probes(term)
        # A term whose every word is generic ("Older Scout Program", "High Adventure Option")
        # cannot be confirmed OR denied by word matching — saying "no trace" would be a lie
        # dressed as a finding.
        if not tk:
            out["unverifiable"].append(code); continue
        where = [u for u, txt in pages.items() if any(hits(txt, ph, tk))]
        if not where:
            # Only a defect if we actually read everything the record points at. Otherwise the
            # honest statement is "we could not check", and it is reported as `unverified` —
            # 812 of the first sweep's 1,377 "no trace" flags came from 63 camps whose own
            # leaders' guide we had failed to download.
            (out["unsupported"] if not unread_cited else out["unverified"]).append(code)
        elif len(where) == 1 and where[0] not in cited:
            out["thin_evidence"][code] = where[0]
    claimed_parents = {by_code[c].get("broader") for c in claimed if c in by_code}
    nav = {}
    for u in pages:
        h = urllib.parse.urlparse(u).netloc
        if h not in own_hosts:
            nav[h] = chrome_phrases(h, vocab)
    for term in vocab:
        code = term["code"]
        if code in claimed or code in claimed_parents:
            continue
        ph, tk = probes(term)
        where, chromed = [], []
        for u, txt in pages.items():
            if not hits(txt, ph, tk)[0]:                  # phrase-level only, to keep noise down
                continue
            if code in nav.get(urllib.parse.urlparse(u).netloc, ()):
                chromed.append(u)
            else:
                where.append(u)
        if where:
            out["missing"][code] = where
        elif chromed:
            out["nav_only"][code] = chromed
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--camps", help="comma-separated camp ids")
    ap.add_argument("--all", action="store_true", help="every camp with features_verified_at")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", help="write full findings as JSON for triage")
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

    results, tot = [], collections.Counter()
    for i, (cid, v) in enumerate(camps, 1):
        r = audit_camp(cid, v, vocab, by_code)
        results.append(r)
        if args.out and i % 25 == 0:                     # checkpoint: a long crawl can be resumed
            pathlib.Path(args.out).write_text(json.dumps(results, indent=1), encoding="utf-8")
            print(f"... {i}/{len(camps)}", flush=True)
        if r.get("unreadable"):
            tot["unreadable"] += 1
            print(f"\n## {cid}: none of {len(r['cited'])} cited source(s) readable — cannot audit",
                  flush=True)
            continue
        if not (r["unsupported"] or r["missing"] or r["read_extra"] or r["thin_evidence"]
                or r.get("unverified")):
            continue
        print(f"\n## {cid}  ({r['claimed']} features, tier={r['tier']}, "
              f"{len(r['read'])} page(s) read incl. {len(r['read_extra'])} uncited)", flush=True)
        if r["unsupported"]:
            tot["unsupported"] += len(r["unsupported"])
            print(f"   NO LEXICAL TRACE: {', '.join(r['unsupported'])}")
        if r.get("unverified"):
            tot["unverified"] += len(r["unverified"])
            print(f"   UNCHECKABLE ({len(r['unread_cited'])} cited source(s) unread): "
                  f"{', '.join(r['unverified'][:8])}")
        if r["thin_evidence"]:
            tot["thin"] += len(r["thin_evidence"])
            for code, u in sorted(r["thin_evidence"].items()):
                print(f"   ONLY AN UNCITED PAGE ATTESTS {code}: {u}")
        if r["missing"]:
            tot["missing"] += len(r["missing"])
            for code, urls in sorted(r["missing"].items()):
                print(f"   PAGE NAMES, RECORD OMITS {code}: {urls[0]}"
                      f"{'' if len(urls) == 1 else f' (+{len(urls) - 1} more)'}")
        if r["uncited_unread"]:
            tot["unread"] += len(r["uncited_unread"])
    if args.out:
        pathlib.Path(args.out).write_text(json.dumps(results, indent=1), encoding="utf-8")
    print(f"\n{len(camps)} camp(s): {tot['unsupported']} with no lexical trace "
          f"(evidence complete), {tot['unverified']} uncheckable (a cited source would not load), "
          f"{tot['missing']} candidate omission(s), {tot['thin']} attested only by an uncited page, "
          f"{tot['unread']} link(s) left unread, {tot['unreadable']} unreadable. "
          f"Every line is a lead for a human, not a verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
