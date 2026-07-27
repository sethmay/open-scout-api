"""Extract the PRE-2024 Cub Scout adventure line-up from usscouts.org into a facts file.

The 2024 Cub program replaced the adventure line-up wholesale: of the 92 adventures the
2015-2024 program ended with, 54 carried into 2024 and 38 were retired. usscouts.org (the U.S.
Scouting Service Project) still serves the old program under `advance/cubscout/`, including two
archived elective editions, so the requirement text is recoverable rather than merely the names.

This tool only writes `tools/cub_adventures_history.json`. `tools/seed_cub_adventures.py` remains
the single writer of `data/adventures/` and the adventure requirement-sets, and consumes this file
alongside `tools/cub_adventures.json` — two writers for one output would clobber each other.

    python tools/seed_cub_adventure_history.py --extract <dir of cached .asp pages>
    python tools/seed_cub_adventure_history.py --fetch <dir>     # download, then extract

Editions and dates come from each page's own `revision-date` region, never inferred:
  * core adventures + all Lion         REVISED effective 2018-09-01
  * Tiger/Wolf/Bear/Webelos-AOL elect. REVISED effective 2022-06-01, with 2018-09-01 editions
                                       archived under `old/` for all but Tiger
An adventure present in a 2018 elective edition but absent from the 2022 one was retired in 2022,
not 2024, and its window closes accordingly — several such pages say so outright ("To be retired
on May 31, 2022").

Requirement text is (c) Scouting America (text_rights), reproduced with attribution for
non-commercial use; see NOTICE.md. usscouts.org is unaffiliated with Scouting America.
"""

from __future__ import annotations

import html
import json
import pathlib
import re
import ssl
import sys
import time
import unicodedata
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
FACTS = ROOT / "tools" / "cub_adventures_history.json"
CURRENT_FACTS = ROOT / "tools" / "cub_adventures.json"
BASE = "http://usscouts.org/advance/cubscout/"
UA = {"User-Agent": "open-scout-api requirement-history seed (github.com/sethmay/open-scout-api)"}
ACCESSED = "2026-07-27"
PROGRAM_END = "2024"          # the 2024 program replaced the line-up; half-open with valid_from 2024
ELECTIVE_2022 = "2022-06-01"  # the June 2022 elective revision

# page -> (rank slugs, category, effective_from)
PAGES: dict[str, tuple[list[str], str, str]] = {
    "lion-core.asp":            (["lion"], "required", "2018-09-01"),
    "lion-elective.asp":        (["lion"], "elective", "2018-09-01"),
    "tiger-core.asp":           (["tiger"], "required", "2018-09-01"),
    "tiger-elective.asp":       (["tiger"], "elective", ELECTIVE_2022),
    "wolf-core.asp":            (["wolf"], "required", "2018-09-01"),
    "wolf-elective.asp":        (["wolf"], "elective", ELECTIVE_2022),
    "bear-core.asp":            (["bear"], "required", "2018-09-01"),
    "bear-elective.asp":        (["bear"], "elective", ELECTIVE_2022),
    "webelos-core.asp":         (["webelos"], "required", "2018-09-01"),
    "aol-core.asp":             (["arrow-of-light"], "required", "2018-09-01"),
    "webelos-aol-elective.asp": (["webelos", "arrow-of-light"], "elective", ELECTIVE_2022),
    "old__wolf-elective-2018.asp":        (["wolf"], "elective", "2018-09-01"),
    "old__bear-elective-2018.asp":        (["bear"], "elective", "2018-09-01"),
    "old__webelos-aol-elective-2018.asp": (["webelos", "arrow-of-light"], "elective", "2018-09-01"),
}

PREFIX = re.compile(
    r"^(?:Lion|Tiger|Wolf|Bear|Webelos|Arrow of Light|Webelos/AOL|AOL)"
    r"(?:\s+(?:Elective|Required|Core))?(?:\s+Preview)?\s+Adventure:\s*", re.I)
# "Preview" adventures were trialed alongside the official line-up, repeat verbatim per rank on the
# shared pages, and have their own source page. Out of scope; counted so the exclusion is visible.
PREVIEW = re.compile(r"preview\s+adventure", re.I)
BARE_PREVIEW = re.compile(r"^(?:protect yourself rules|yo-?yo|modular design)$", re.I)
SECTION = re.compile(r"^(?:required|elective|core)\b|^the requirements|^requirements$|^preview", re.I)


def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip()


def clean(s: str) -> str:
    """Heading/name hygiene — a name never ends in a period."""
    return _collapse(s).strip(" .")


def text(frag: str) -> str:
    """Verbatim requirement text. Stripping tags leaves a gap before the punctuation that
    followed a link ("earn your <a>Whittling Chip</a>." -> "Whittling Chip ."), and the source
    hangs footnote asterisks off a few requirements. Both are repaired; terminal punctuation is
    NOT stripped — this text is published as verbatim (c) Scouting America, so dropping the
    sentence's own full stop would make that claim untrue."""
    s = _collapse(html.unescape(re.sub(r"<[^>]+>", " ", frag)))
    s = re.sub(r"\s+([.,;:!?])", r"\1", s)
    return re.sub(r"\s*\*+$", "", s).strip()


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def slugify(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.replace("\u2019", "").replace("\u2018", ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def region(body: str) -> str:
    for name in ("requirements", "content"):
        m = re.search(r'#BeginEditable "' + name + r'"\s*-->(.*?)<!--\s*#EndEditable', body, re.S)
        if m:
            return m.group(1)
    return body


def editable(body: str, name: str) -> str | None:
    m = re.search(r'#BeginEditable "' + name + r'"\s*-->(.*?)<!--\s*#EndEditable', body, re.S)
    return text(m.group(1)) if m else None


def _items(ol_inner: str) -> list[str]:
    """Immediate <li> children of one <ol>, ignoring nested list markup."""
    out, depth, buf = [], 0, []
    for m in re.finditer(r"<(/?)(ol|ul|li)\b[^>]*>", ol_inner, re.I):
        tag, closing = m.group(2).lower(), bool(m.group(1))
        if tag in ("ol", "ul"):
            depth += -1 if closing else 1
            continue
        if depth != 0:
            continue
        if not closing:
            if buf:
                out.append(ol_inner[buf[0]:m.start()])
            buf = [m.end()]
        elif buf:
            out.append(ol_inner[buf[0]:m.start()]); buf = []
    if buf:
        out.append(ol_inner[buf[0]:])
    return out


def _first_ol(frag: str):
    m = re.search(r"<ol([^>]*)>", frag, re.I)
    if not m:
        return None
    depth = 1
    for mm in re.finditer(r"<(/?)ol\b[^>]*>", frag[m.end():], re.I):
        depth += -1 if mm.group(1) else 1
        if depth == 0:
            return frag[m.end():m.end() + mm.start()], m.group(1)
    return frag[m.end():], m.group(1)


def tree(frag: str, prefix: str = "") -> list[dict]:
    """Requirement tree. Nested <ol type="A"> becomes lettered children ('1', '1a', '1a1')."""
    got = _first_ol(frag)
    if not got:
        return []
    inner, attrs = got
    lettered = re.search(r'type\s*=\s*"?[aA]', attrs or "") is not None
    nodes = []
    for n, item in enumerate(_items(inner), start=1):
        label = f"{prefix}{chr(96 + n)}" if lettered else f"{prefix}{n}"
        kids = tree(item, label)
        own = text(re.split(r"<ol\b", item, maxsplit=1, flags=re.I)[0])
        node = {"number": label}
        if own:
            node["text"] = own
        if kids:
            node["children"] = kids
        if not own and not kids:
            continue
        nodes.append(node)
    return nodes


def parse_page(path: pathlib.Path) -> tuple[list[dict], list[str]]:
    """(adventures, skipped headings).

    Inclusion is content-based — an adventure is an <h3> whose section carries a requirement
    <ol> — so an unfamiliar heading style cannot silently drop one.
    """
    body = path.read_text("utf-8", errors="ignore")
    seg = re.sub(r"<script.*?</script>|<style.*?</style>", " ", region(body), flags=re.S | re.I)
    out, skipped = [], []
    hits = list(re.finditer(r"<h3[^>]*>(.*?)</h3>", seg, re.S | re.I))
    for i, m in enumerate(hits):
        raw = text(m.group(1))
        name = clean(PREFIX.sub("", raw))
        retired_note = None
        rm = re.search(r"\((?:to be )?retired[^)]*\)", name, re.I)
        if rm:
            retired_note = clean(rm.group(0)); name = clean(name[:rm.start()])
        chunk = seg[m.end(): hits[i + 1].start() if i + 1 < len(hits) else len(seg)]
        reqs = tree(chunk)
        if not reqs or PREVIEW.search(raw) or BARE_PREVIEW.match(name) or SECTION.match(name):
            skipped.append(raw[:70]); continue
        first_p = re.search(r"<p>(.*?)</p>", chunk, re.S | re.I)
        out.append({"name": name, "rule": text(first_p.group(1)) if first_p else "",
                    "retired_note": retired_note, "requirements": reqs})
    return out, skipped


def fetch(dest: pathlib.Path) -> None:
    ctx = ssl.create_default_context(); ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE          # usscouts.org serves a stale chain
    dest.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        p = dest / page
        if p.exists():
            continue
        url = BASE + page.replace("old__", "old/")
        try:
            b = urllib.request.urlopen(urllib.request.Request(url, headers=UA),
                                       timeout=30, context=ctx).read().decode("utf-8", "ignore")
            p.write_text(b, encoding="utf-8")
            print(f"  fetched {page} ({len(b)} bytes)")
            time.sleep(0.7)                  # a volunteer-run site; be polite
        except Exception as exc:
            print(f"  FAILED  {page}: {type(exc).__name__}")


def strip_qualifier(name: str) -> set[str]:
    """Names this one reduces to when a bare qualifier is dropped.

    Either side of a colon can be the qualifier — "Tiger: Safe and Smart" tidies to the second
    half, "Tiger Circles: Duty to God" to the first — as can a trailing parenthetical,
    "Council Fire (Duty to Country)". All three are the same adventure under a tidied name.
    """
    out = {re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()}
    if ":" in name:
        head, tail = name.split(":", 1)
        out.update({head.strip(), tail.strip()})
    return {clean(x) for x in out if clean(x)}


def extract(src: pathlib.Path) -> None:
    if not CURRENT_FACTS.exists():
        raise SystemExit(f"{CURRENT_FACTS} missing — run tools/seed_cub_adventures.py --extract first")
    current = json.loads(CURRENT_FACTS.read_text("utf-8"))
    cur_by_name: dict[str, list[dict]] = {}
    for a in current["adventures"]:
        cur_by_name.setdefault(norm(a["name"]), []).append(a)

    # ---- parse every page into per-adventure editions
    advs: dict[str, dict] = {}
    skipped_total, sources = 0, {}
    for page, (ranks, cat, eff) in PAGES.items():
        p = src / page
        if not p.exists():
            raise SystemExit(f"{p} missing — run with --fetch first")
        body = p.read_text("utf-8", errors="ignore")
        sources[page] = {"url": BASE + page.replace("old__", "old/"),
                         "revision_date": editable(body, "revision-date"),
                         "rev_type": editable(body, "rev-type")}
        parsed, skipped = parse_page(p)
        skipped_total += len(skipped)
        for a in parsed:
            key = norm(a["name"])
            rec = advs.setdefault(key, {"name": a["name"], "ranks": [], "category": cat,
                                        "editions": {}})
            for r in ranks:
                if r not in rec["ranks"]:
                    rec["ranks"].append(r)
            if rec["category"] != cat:
                raise SystemExit(f"{a['name']}: category differs across pages "
                                 f"({rec['category']} vs {cat})")
            rec["editions"][eff] = {"effective_from": eff, "rule": a["rule"],
                                    "retired_note": a["retired_note"], "source_page": page,
                                    "requirements": a["requirements"]}

    # ---- close each edition's window against the next, and the line against its retirement
    for rec in advs.values():
        effs = sorted(rec["editions"])
        # An elective in the 2018 edition but not the 2022 one was retired in 2022, not 2024.
        retired_2022 = (rec["category"] == "elective" and effs == ["2018-09-01"]
                        and rec["ranks"] != ["lion"] and rec["ranks"] != ["tiger"])
        rec["retired_on"] = ELECTIVE_2022 if retired_2022 else PROGRAM_END
        eds = []
        for i, eff in enumerate(effs):
            ed = rec["editions"][eff]
            ed["effective_to"] = effs[i + 1] if i + 1 < len(effs) else rec["retired_on"]
            eds.append(ed)
        rec["editions"] = eds

    # ---- disposition: does this adventure carry into the 2024 program?
    counts = {"continues": 0, "renamed": 0, "superseded": 0, "discontinued": 0}
    for rec in advs.values():
        ranks = set(rec["ranks"])
        hit = next((a for a in cur_by_name.get(norm(rec["name"]), [])
                    if ranks & set(a["ranks"])), None)
        if hit:
            rec["disposition"] = {"kind": "continues", "id": hit["slug"]}
            counts["continues"] += 1
            continue
        # An annotation drop ("Council Fire (Duty to Country)" -> "Council Fire") is the same
        # adventure under a tidied name: one entity, a new version window.
        alt = None
        for cand in strip_qualifier(rec["name"]):
            alt = next((a for a in cur_by_name.get(norm(cand), []) if ranks & set(a["ranks"])), None)
            if alt:
                break
        if alt:
            rec["disposition"] = {"kind": "renamed", "id": alt["slug"], "new_name": alt["name"]}
            counts["renamed"] += 1
            continue
        # A substantive rename is a DIFFERENT entity plus a `superseded` event, matching how
        # merit badges record `computers -> digital-technology`: asserting one entity would
        # fabricate continuity the source does not state.
        succ = None
        hw = re.findall(r"[a-z0-9]+", rec["name"].lower())
        for a in current["adventures"]:
            if not (ranks & set(a["ranks"])):
                continue
            aw = re.findall(r"[a-z0-9]+", a["name"].lower())
            if len(aw) < len(hw) and " ".join(aw) in " ".join(hw):
                succ = a; break
        if succ:
            rec["disposition"] = {"kind": "superseded", "by": succ["slug"], "by_name": succ["name"]}
            counts["superseded"] += 1
        else:
            rec["disposition"] = {"kind": "discontinued"}
            counts["discontinued"] += 1

    facts = {
        "note": ("The PRE-2024 Cub Scout adventure line-up (the 2015-2024 program as it stood at "
                 "each source page's revision), parsed from usscouts.org. Editions and dates come "
                 "from each page's own revision-date region. 'Preview' adventures and the pre-2024 "
                 "Bobcat (a rank then, an adventure only since 2024) are out of scope. Requirement "
                 "text is verbatim (c) Scouting America; see NOTICE.md."),
        "accessed": ACCESSED,
        "program_end": PROGRAM_END,
        "sources": sources,
        "counts": counts,
        "adventures": [advs[k] for k in sorted(advs, key=lambda k: advs[k]["name"])],
    }
    FACTS.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n",
                     encoding="utf-8", newline="\n")
    nodes = sum(_count(e["requirements"]) for r in advs.values() for e in r["editions"])
    print(f"wrote {FACTS.relative_to(ROOT).as_posix()}: {len(advs)} pre-2024 adventures, "
          f"{sum(len(r['editions']) for r in advs.values())} editions, {nodes} requirement nodes")
    print(f"  dispositions: {counts} | headings skipped (previews/sections): {skipped_total}")
    retired22 = [r["name"] for r in advs.values() if r["retired_on"] == ELECTIVE_2022]
    print(f"  retired in 2022 rather than 2024: {len(retired22)}")


def _count(rs) -> int:
    return sum(1 + _count(r.get("children", [])) for r in rs) if rs else 0


def main() -> None:
    args = sys.argv[1:]
    if not args or args[0] not in ("--extract", "--fetch"):
        raise SystemExit(__doc__)
    src = pathlib.Path(args[1]) if len(args) > 1 else ROOT / ".workbench" / "cubhist"
    if args[0] == "--fetch":
        fetch(src)
    extract(src)


if __name__ == "__main__":
    main()
