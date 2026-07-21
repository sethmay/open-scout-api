"""One-time seed generator for merit-badge requirement sets.

Parses the requirement source files in the OpenScouting/workbooks repo
(badges/<slug>/<year>.md: YAML frontmatter + a numbered requirement list) into
requirement-set documents. The workbooks repo is located by walking up from this
file to find .workbench/workbooks-main/ (git-ignored; not committed).

COPYRIGHT: the requirement TEXT is Scouting America's property. It is reproduced
verbatim here with attribution, for non-commercial Scouting use, and is NOT
licensed under this dataset's CC BY-NC-SA (each set carries `text_rights` and
`includes_official_text: true`; see NOTICE.md). Only the compilation, structure,
numbering, and metadata are the project's contribution.

Requirement tree: nesting is signaled by MARKER TYPE, not indentation —
`N.` (top) -> `(a)` (letter child) -> `(1)` (digit child, under the letter).
`choose` is derived from count phrases in a parent's text ("do TWO of the
following", "one of the following:").

Output: data/requirement-sets/<slug>-<year>.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "requirement-sets"
TODAY = "2026-07-21"
TEXT_RIGHTS = ("Requirement text \u00a9 Scouting America, reproduced with attribution for "
               "non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. See NOTICE.md.")
EFFECTIVE_TO = {"citizenship-in-society": "2026-02-27"}  # discontinued badges: requirements no longer in effect

WORDNUM = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten".split())}
TOP = re.compile(r"^(\d+)\.\s+(.*)$")
LETTER = re.compile(r"^\s*\(([a-z])\)\s+(.*)$")
DIGIT = re.compile(r"^\s*\((\d+)\)\s+(.*)$")
OPTION = re.compile(r"^(?:[A-Z]\s+)?Option\s+([A-Z])\b[\u2014:.\-]?\s*(.*)$")   # "Option A—…" / "A Option A—…"
COUNT = re.compile(r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\b\s+of the following", re.I)


def find_workbooks() -> Path:
    for p in [ROOT, *ROOT.parents]:
        cand = p / ".workbench" / "workbooks-main" / "badges"
        if cand.exists():
            return cand
    raise SystemExit("workbooks repo not found at .workbench/workbooks-main/badges")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---"):
        raise ValueError("no frontmatter")
    _, fm, body = text.split("---", 2)
    meta = {}
    for line in fm.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m and m.group(2):
            meta[m.group(1)] = m.group(2).strip().strip('"')
    return meta, body


def parse_requirements(body: str) -> tuple[list[dict], bool]:
    """Returns (tree, used_fallback). Nesting by marker type via a level stack:
    top(0) < Option(1) < letter(2) < digit(3). Unrecognized non-blank lines are
    appended to the current node's text (non-fatal) and flip used_fallback."""
    root = {"number": "", "text": "", "children": [], "_level": -1}
    stack = [root]
    used_fallback = False
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("NOTE:"):
            continue
        if (m := TOP.match(line)):
            level, token, text = 0, m.group(1), m.group(2).strip()
        elif (m := OPTION.match(line)):
            level, token, text = 1, m.group(1).upper(), m.group(2).strip()   # uppercase = Option
        elif (m := LETTER.match(line)):
            level, token, text = 2, m.group(1), m.group(2).strip()
        elif (m := DIGIT.match(line)):
            level, token, text = 3, f"({m.group(1)})", m.group(2).strip()
        else:  # unrecognized -> continuation of the current node's text
            used_fallback = True
            cur = stack[-1]
            if cur is root:
                raise ValueError(f"stray line before any requirement: {line!r}")
            cur["text"] = (cur["text"] + " " + line).strip()
            continue
        while stack[-1]["_level"] >= level:
            stack.pop()
        parent = stack[-1]
        num = token if parent is root else (parent["number"] + token)
        node = {"number": num, "text": text, "children": [], "_level": level}
        parent["children"].append(node)
        stack.append(node)

    def finish(node: dict) -> dict:
        kids = [finish(c) for c in node["children"]]
        out = {"number": node["number"], "text": node["text"]}
        if kids:
            out["children"] = kids
            if (cm := COUNT.search(node["text"])):
                out["choose"] = WORDNUM[cm.group(1).lower()]
        return out

    if not root["children"]:
        raise ValueError("no requirements parsed")
    return [finish(n) for n in root["children"]], used_fallback


def main() -> None:
    wb = find_workbooks()
    OUT.mkdir(parents=True, exist_ok=True)
    count = 0
    fallback_files = []
    for md in sorted(wb.glob("*/*.md")):
        meta, body = parse_frontmatter(md.read_text("utf-8"))
        slug, year = meta["slug"], meta["effective"]
        reqs, used_fallback = parse_requirements(body)
        if used_fallback:
            fallback_files.append(slug)
        sources = [{"url": meta["source_url"]},
                   {"citation": f"OpenScouting/workbooks badges/{slug}/{year}.md"}]
        if meta.get("pamphlet_pdf"):
            sources.insert(1, {"url": meta["pamphlet_pdf"]})
        doc = {
            "id": f"{slug}-{year}", "kind": "requirement-set",
            "subject": f"merit-badge:{slug}",
            "effective_from": meta.get("requirements_revision") or year,
            "effective_to": EFFECTIVE_TO.get(slug),
            "supersedes": None,
            "source_document": {"title": f'{meta["badge"]} Merit Badge Requirements ({year})',
                                "url": meta["source_url"], "year": int(year)},
            "includes_official_text": True,
            "text_rights": TEXT_RIGHTS,
            "requirements": reqs,
            "provenance": {"sources": sources, "method": "curated", "verified_at": TODAY,
                           "confidence": 0.75 if used_fallback else 0.9,
                           "notes": ("Requirement text verbatim from the official pamphlet; structure/numbering derived."
                                     + (" Some deeply-nested/irregular requirements were flattened during parsing — consult the source pamphlet for exact sub-structure." if used_fallback else ""))},
            "notes": ("Deep/irregular sub-structure was partially flattened; text complete, nesting approximate." if used_fallback else None),
        }
        (OUT / f"{slug}-{year}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        count += 1
    print(f"requirement-sets: {count} documents written")
    if fallback_files:
        print(f"  text-continuation fallback used in {len(fallback_files)}: {', '.join(fallback_files)}")


if __name__ == "__main__":
    main()
