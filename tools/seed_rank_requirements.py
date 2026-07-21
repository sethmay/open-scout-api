"""Seed generator for Scouts BSA rank requirement-sets (7 documents).

Parses the official 2024 Scouts BSA Requirements rank section (PDF dropped into the
repo's .workbench/, git-ignored like the workbooks source) into one requirement-set
document per rank: data/requirement-sets/<rank>-2024.json (subject: rank:<slug>).

Requirement TEXT is verbatim Scouting America copyright (includes_official_text=true +
text_rights); structure/numbering is derived. Topical section headers (CAMPING, COOKING,
...) and page/footnote furniture are dropped. Two source irregularities are corrected in
code and documented in NOTES below: Life req 6's two-column option list (de-interleaved)
and an Eagle req 7 footnote digit merged into a Guide-to-Advancement topic number.

Not in CI (needs the .workbench PDF). Re-run after dropping an updated requirements PDF.
"""
from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

import pdfplumber

PDF_NAME = "Scouts-BSA-Rank-Requirements.pdf"
TODAY = date.today().isoformat()
ADV_URL = "https://www.scouting.org/programs/scouts-bsa/advancement-and-awards/"
TEXT_RIGHTS = ("Requirement text \u00a9 Scouting America, reproduced with attribution for "
               "non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. "
               "See NOTICE.md.")
# (slug, Display Name) in advancement order
RANKS = [("scout", "SCOUT"), ("tenderfoot", "TENDERFOOT"), ("second-class", "SECOND CLASS"),
         ("first-class", "FIRST CLASS"), ("star", "STAR"), ("life", "LIFE"), ("eagle", "EAGLE")]
NAME = {"scout": "Scout", "tenderfoot": "Tenderfoot", "second-class": "Second Class",
        "first-class": "First Class", "star": "Star", "life": "Life", "eagle": "Eagle"}

HDR = re.compile(r'^(SCOUT|TENDERFOOT|SECOND CLASS|FIRST CLASS|STAR|LIFE|EAGLE) RANK REQUIREMENTS')
PALM = re.compile(r'^EAGLE PALM')
MARK = re.compile(r'^(\d+)([a-z])?\.\s*(.*)$')   # \s* so bare table rows ("1.") match -> dropped
LET = re.compile(r'^([a-z])\.\s+(.*)$')
BULLET = re.compile(r'^[\u2022\u00b7]\s*(.*)$')


def find_pdf() -> Path:
    for p in [Path(__file__).resolve()] + list(Path(__file__).resolve().parents):
        cand = p / ".workbench" / PDF_NAME
        if cand.exists():
            return cand
    raise SystemExit(f"source PDF not found: .workbench/{PDF_NAME} (drop it in the repo root)")


def clean(t: str) -> str:
    t = re.sub(r'([a-z])- ([a-z])', r'\1\2', t)                      # de-hyphenate line breaks
    t = re.sub(r'-+\u2013', '\u2013', t)                             # "38--39" -> "38-39"
    t = re.sub(r'([A-Za-z\)\u201d])\.(\d{1,2}(?:,\d{1,2})*)(?=[\s(]|$)', r'\1.', t)  # footnote sup
    t = re.sub(r'([a-z])(\d{1,2})(?=:)', r'\1', t)                   # "responsibility11:" -> ":"
    t = re.sub(r'(\))(\d{1,2})(?=[\s(]|$)', r'\1', t)                # "victim.)5" -> "victim.)"
    return re.sub(r'\s{2,}', ' ', t).strip()


def is_noise(s: str) -> bool:
    return (not s or s.startswith("(cid:") or s in {"INITIAL", "& DATE", "RANK", "REQUIREMENTS",
            "LEADER", "NAME OF MERIT BADGE DATE EARNED", "(Eagle-required)"}
            or bool(re.fullmatch(r'\d{3}', s)))


def is_section(s: str) -> bool:  # all-caps topical header (dropped)
    return (bool(s) and s == s.upper() and bool(re.search(r'[A-Z]', s)) and not re.match(r'^\d', s)
            and not s.startswith("(") and len(s) < 45 and s not in {"INITIAL", "& DATE"})


def is_footnote(s: str) -> bool:
    return (s.startswith("Notes:") or s.startswith("Alternative requirements")
            or bool(re.match(r'^\d{1,2}[A-Za-z]', s)))


def rank_bounds(lines: list[str]) -> dict[str, tuple[int, int]]:
    starts, order = {}, [k for _, k in RANKS]
    for i, ln in enumerate(lines):
        m = HDR.match(ln.strip())
        if m:
            starts[m.group(1)] = i
    palm_i = next((i for i, ln in enumerate(lines) if PALM.match(ln.strip())), len(lines))
    bounds = {}
    for k, key in enumerate(order):
        s = starts[key] + 1
        e = starts[order[k + 1]] if k + 1 < len(order) else palm_i
        bounds[key] = (s, e)
    return bounds


def parse_rank(lines: list[str], s: int, e: int) -> list[dict]:
    top, cur_num, cur_child, tgt, skip, maxn = [], None, None, None, False, 0
    for i in range(s, e):
        st = lines[i].strip()
        if is_noise(st):
            continue
        mk, bl, lt = MARK.match(st), BULLET.match(st), LET.match(st)
        real_marker = backref = False
        if mk:
            num, let, txt = int(mk.group(1)), mk.group(2), mk.group(3).strip()
            if not let and not txt:                       # blank merit-badge table row
                continue
            if num >= maxn + 1 or num == maxn:
                real_marker = True
            if num < maxn:                                # back-reference to earlier requirement
                real_marker = False
            if (let and cur_num is not None and cur_num["number"] == str(num)
                    and any(c.get("number") == f"{num}{let}" for c in cur_num.get("children", []))):
                real_marker = False                       # duplicate child label = back-reference
            backref = not real_marker
        if real_marker or bl or (lt and cur_num is not None) or backref:
            skip = False
        if skip:
            continue
        if backref:                                       # marker-shaped ref inside body -> append
            if tgt is not None:
                tgt["text"] = clean((tgt.get("text") or "") + " " + st)
            continue
        if not real_marker and is_footnote(st) and not (bl or (lt and cur_num)):
            skip = True                                   # footnote/Notes -> skip to next marker
            continue
        if is_section(st):
            continue
        if real_marker:
            if not let:
                node = {"number": str(num), "text": clean(txt)}
                top.append(node)
                cur_num, cur_child, tgt = node, None, node
            else:
                if cur_num is None or cur_num["number"] != str(num):
                    cur_num = {"number": str(num), "children": []}
                    top.append(cur_num)
                    cur_child = None
                child = {"number": f"{num}{let}", "text": clean(txt)}
                cur_num.setdefault("children", []).append(child)
                cur_child = tgt = child
            maxn = max(maxn, num)
        elif lt and cur_num is not None:
            child = {"number": f"{cur_num['number']}{lt.group(1)}", "text": clean(lt.group(2))}
            cur_num.setdefault("children", []).append(child)
            cur_child = tgt = child
        elif bl:                                          # unlabeled bullet list -> fold into text
            parent = cur_child or cur_num
            if parent is None:
                continue
            parent["text"] = clean((parent.get("text") or "") + " " + bl.group(1))
            tgt = parent
        elif tgt is not None:
            tgt["text"] = clean((tgt.get("text") or "") + " " + st)
    return top


# --- source-irregularity corrections (documented in each rank's `notes`) ----------
LIFE6_OPTIONS = [
    ("a", "Tenderfoot 4a and 4b (first aid)"),
    ("b", "Second Class 2b, 2c, and 2d (cooking/tools)"),
    ("c", "Second Class 3a and 3d (navigation)"),
    ("d", "First Class 3a, 3b, 3c, and 3d (tools)"),
    ("e", "First Class 4a and 4b (navigation)"),
    ("f", "Second Class 6a and 6b (first aid)"),
    ("g", "First Class 7a and 7b (first aid)"),
    ("h", "Three requirements from one of the required Eagle merit badges, "
          "as approved by your Scoutmaster"),
]
NOTES = {
    "life": ("Requirement 6's choose-one option list (a-h) was printed in the source as two "
             "interleaved columns; de-interleaved here and choose=1 applied. Bullets, topical "
             "section headers, and footnotes omitted."),
    "eagle": ("Requirement 7's Guide-to-Advancement topic number had a footnote digit merged "
              "into it in the source (\"8.0.3.1.13\"); corrected to \"8.0.3.1\". Topical section "
              "headers and footnotes omitted."),
}
DEFAULT_NOTE = "Topical section headers and page/footnote furniture omitted from the tree."


def fixups(slug: str, top: list[dict]) -> None:
    if slug == "life":
        r6 = next(n for n in top if n["number"] == "6")
        r6["choose"] = 1
        r6["children"] = [{"number": f"6{c}", "text": t} for c, t in LIFE6_OPTIONS]
    if slug == "eagle":
        r7 = next(n for n in top if n["number"] == "7")
        r7["text"] = r7["text"].replace("8.0.3.1.13)", "8.0.3.1)")


def main() -> None:
    pdf_path = find_pdf()
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(pg.extract_text() or "" for pg in pdf.pages)
    lines = text.splitlines()
    bounds = rank_bounds(lines)
    out_dir = Path(__file__).resolve().parents[1] / "data" / "requirement-sets"
    out_dir.mkdir(parents=True, exist_ok=True)
    for slug, key in RANKS:
        s, e = bounds[key]
        reqs = parse_rank(lines, s, e)
        fixups(slug, reqs)
        doc = {
            "id": f"{slug}-2024",
            "kind": "requirement-set",
            "subject": f"rank:{slug}",
            "effective_from": "2024-01-01",
            "effective_to": None,
            "supersedes": None,
            "source_document": {
                "title": f"{NAME[slug]} Rank Requirements (2024 Scouts BSA Requirements, No. 33216)",
                "url": ADV_URL,
                "year": 2024,
            },
            "includes_official_text": True,
            "text_rights": TEXT_RIGHTS,
            "requirements": reqs,
            "provenance": {
                "sources": [
                    {"url": ADV_URL},
                    {"citation": "2024 Scouts BSA Requirements (No. 33216), rank requirements section"},
                ],
                "method": "curated",
                "verified_at": TODAY,
                "confidence": 0.9,
                "notes": "Requirement text verbatim from the official 2024 Scouts BSA "
                         "Requirements; structure/numbering derived.",
            },
            "notes": NOTES.get(slug, DEFAULT_NOTE),
        }
        (out_dir / f"{slug}-2024.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"rank requirement-sets: {len(RANKS)} documents written")


if __name__ == "__main__":
    main()
