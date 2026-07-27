"""Seed generator for adult training: the course catalog and the position-trained requirements.

Parses Scouting America's TRAINED LEADER REQUIREMENTS chart (PDF dropped into the repo's
git-ignored `.workbench/training/`, like the rank requirements workbook) into two datasets:

  data/training/<slug>.json               one course - code, name, delivery, renewal
  data/training-requirements/<id>.json    one chart ROW - (position, unit_type) -> courses

Why the row and not the position is the record: the chart's key is the PAIR. Registration code
`CC` requires C60 in a pack, WS10 in a troop, WS11 in a team, WS12 in a crew and P44 in a ship;
a Chartered Organization Representative takes Y01 in a pack but Y02 in a crew. One record per
position would have to pick one of those and would be wrong five times over. This is the same
shape as the youth positions in 0.49.0 - acceptance is an edge, not an attribute - and it is why
adult roles are NOT added to `data/positions/`: that dataset's gate requires every position to be
offered by some rank requirement, which is true of youth positions and false of every adult one.

Irregularities in the source, preserved rather than corrected (see NOTES on each record):
  - Unit Scouter Reserve (91U) keeps Y01 inside the Crew and Ship sections, where every other row
    takes Y02. Recorded as printed; it is not ours to reconcile.
  - Typos: "Neigborhood Chairman", "Supernova Mentor Traning", "Youth Potection".
  - The chart writes "Y02 Youth Protection Training" for one Parent Coordinator row and
    "Y02 Venturing Youth Protection Training" everywhere else. Courses are keyed by CODE, so both
    land on the same entity; the name comes from the majority spelling.
  - Footnote markers sit on CELLS, not courses: WS10 is marked e-learning-only for the two Troop
    Committee rows and left unmarked for Parent Coordinator. So `delivery_note` is per requirement.

Re-run after dropping an updated PDF. Idempotent: same PDF in, byte-identical JSON out.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / ".workbench" / "training" / "trained_leader_positions.pdf"
COURSE_DIR = ROOT / "data" / "training"
REQ_DIR = ROOT / "data" / "training-requirements"
SOURCE_URL = "https://filestore.scouting.org/filestore/training/pdf/trained_leader_positions.pdf"
SOURCE_TITLE = "Trained Leader Requirements - Unit and Other Positions"
VERIFIED_AT = "2026-07-27"
SECTIONS = ["Pack", "Troop", "Team", "Crew", "Ship", "Other"]
WORDNUM = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten".split())}

CODED = re.compile(r"^([A-Z]{1,2}\d{2}[A-Z]?)\s+(.*)$")
POS = re.compile(r"^(.*?)\s*\(([^)]+)\)\s*$")
ANY_OF = re.compile(r"^(.*?)\s*\(([A-Z]\d{2}(?:,\s*[A-Z]\d{2})+)\)\s*$")
MODULE_BETWEEN = re.compile(r"Before the [Ff]irst [Mm]eeting\s+(.*?)\s+- First 30 Days")


def slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-{2,}", "-", s)[:80].strip("-")


class Catalog:
    """Courses discovered while walking the chart, deduplicated by code (or by name when uncoded)."""

    def __init__(self) -> None:
        self.by_key: dict[str, dict] = {}

    def add(self, code: str | None, name: str, **extra) -> str:
        key = code or f"~{name}"
        rec = self.by_key.get(key)
        if rec is None:
            slug = slugify(f"{code} {name}" if code else name)
            rec = self.by_key[key] = {"slug": slug, "code": code, "name": name,
                                      "delivery": "unknown", "renew_months": None, "names": set()}
            rec.update(extra)
        rec["names"].add(name)
        return rec["slug"]


def parse_cell(cell: str, cat: Catalog) -> dict | None:
    """One course cell -> one `requires` entry. Handles plain, footnoted, OR and any-of cells."""
    text = " ".join((cell or "").split())
    if not text:
        return None
    note = None
    if text.endswith("**"):
        note, text = "elearning_only", text[:-2].strip()
    elif text.endswith("*"):
        note, text = "either_instructor_led_or_elearning", text[:-1].strip()

    entry: dict
    if (m := ANY_OF.match(text)) and "Any" in m.group(1):
        # "Any Basic Commissioner Training (D16, D17, D18, D19, D20, D26)" - the chart names the
        # group but not the individual courses, so each code becomes a course with the group's name.
        label = m.group(1).strip()
        # The chart titles the GROUP and never the individual courses, and neither does the Guide
        # to Leader Training. So every one of them carries the only name the source supports; a
        # distinct invented title per code would be a fabrication dressed as data.
        group_name = re.sub(r"^Any\s+", "", label)
        kids = []
        for code in [c.strip() for c in m.group(2).split(",")]:
            kids.append({"ref": f"training:{cat.add(code, group_name, name_is_group=True)}"})
        entry = {"choose": 1, "label": label, "children": kids}
    elif " OR " in text and text.startswith("Classroom - "):
        classroom, online = text.split(" OR ", 1)
        c_txt = classroom[len("Classroom - "):].strip()
        cm = CODED.match(c_txt)
        if not cm:
            raise SystemExit(f"classroom option is not a coded course: {c_txt!r}")
        o_txt = online[len("Online - "):].strip() if online.startswith("Online - ") else online
        # The module prefix repeats the unit's name and the course name STARTS with that same
        # word, so scanning left-to-right for "X - Before the..." swallows a word of the title
        # ("Cubmaster Position-Specific" instead of "... Training"). Read the prefix from between
        # module 1 and module 2 instead, where it is bounded on both sides and cannot be confused.
        mm = MODULE_BETWEEN.search(o_txt)
        if not mm:
            raise SystemExit(f"online option has no module list: {o_txt!r}")
        prefix = mm.group(1).strip()
        parts = [p.strip() for p in re.split(rf"(?={re.escape(prefix)} - )", o_txt) if p.strip()]
        o_name, modules = parts[0], parts[1:]
        if len(modules) < 2:
            raise SystemExit(f"online option split into {len(modules)} module(s): {o_txt!r}")
        entry = {"choose": 1, "label": "Classroom or online", "children": [
            {"ref": f"training:{cat.add(cm.group(1), cm.group(2).strip(), delivery='classroom')}"},
            {"ref": f"training:{cat.add(None, o_name, delivery='online', modules=modules)}"}]}
    elif (m := CODED.match(text)):
        entry = {"ref": f"training:{cat.add(m.group(1), m.group(2).strip())}"}
    else:
        raise SystemExit(f"unrecognised course cell: {text!r}")
    if note:
        entry["delivery_note"] = note
    return entry


def read_chart() -> tuple[list[dict], Catalog, int]:
    cat = Catalog()
    rows: list[dict] = []
    with pdfplumber.open(PDF) as pdf:
        header = pdf.pages[0].extract_text() or ""
        section = "Pack"
        for page in pdf.pages:
            for raw in page.extract_table() or []:
                cells = [" ".join((c or "").split()) for c in raw]
                if cells and cells[0] in SECTIONS:
                    section = cells[0]
                if len(cells) < 3 or not (m := POS.match(cells[1] or "")):
                    continue
                requires = [e for e in (parse_cell(c, cat) for c in cells[2:]) if e]
                if not requires:
                    raise SystemExit(f"{cells[1]!r}: no courses parsed")
                rows.append({"unit": section.lower(), "name": m.group(1).strip(),
                             "codes": [c.strip() for c in m.group(2).split(",")],
                             "requires": requires})
    # YPT renewal is stated once, in the chart's own header. Derive it rather than typing 24.
    ym = re.search(r"retaken every (\w+) years?", header, re.I)
    if not ym or not WORDNUM.get(ym.group(1).lower()):
        raise SystemExit("could not read the Youth Protection renewal interval from the chart header")
    months = WORDNUM[ym.group(1).lower()] * 12
    for rec in cat.by_key.values():
        if (rec["code"] or "").startswith("Y"):
            rec["renew_months"] = months
            rec["delivery"] = "both"   # header: instructor-led in the council OR e-learning
    return rows, cat, months


def provenance(notes: str | None = None) -> dict:
    return {"sources": [{"citation": f"Scouting America, {SOURCE_TITLE}", "url": SOURCE_URL}],
            "method": "curated", "verified_at": VERIFIED_AT, "confidence": 0.9, "notes": notes}


def write(path: Path, doc: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8", newline="\n")


def main() -> None:
    if not PDF.exists():
        raise SystemExit(f"missing {PDF} - download it from {SOURCE_URL}")
    rows, cat, months = read_chart()

    for rec in sorted(cat.by_key.values(), key=lambda r: r["slug"]):
        version = {"valid_from": None, "valid_to": None, "code": rec["code"], "name": rec["name"],
                   "delivery": rec["delivery"], "renew_months": rec["renew_months"]}
        if rec.get("modules"):
            version["modules"] = rec["modules"]
        alt = sorted(n for n in rec["names"] if n != rec["name"])
        if rec.get("name_is_group"):
            note = (f"The chart lists {rec['code']} only inside \"Any {rec['name']}\" alongside the "
                    f"other basic commissioner course codes and never gives it its own title, so "
                    f"this name is the group's. Not a transcription of a printed course name.")
        elif alt:
            note = f"Course name and code as printed in the chart. Also printed as: {'; '.join(alt)}."
        else:
            note = None
        version["provenance"] = provenance(note)
        write(COURSE_DIR / f"{rec['slug']}.json",
              {"id": rec["slug"], "kind": "training", "versions": [version], "notes": None})

    seen: dict[str, str] = {}
    for row in rows:
        name_slug = slugify(row["name"])
        rid = name_slug if name_slug.startswith(f"{row['unit']}-") else f"{row['unit']}-{name_slug}"
        if rid in seen:
            raise SystemExit(f"id collision {rid!r}: {seen[rid]!r} and {row['name']!r}")
        seen[rid] = row["name"]
        write(REQ_DIR / f"{rid}.json", {
            "id": rid, "kind": "training-requirement", "position_name": row["name"],
            "registration_codes": row["codes"], "unit_type": row["unit"],
            "requires": row["requires"],
            "source_document": {"title": SOURCE_TITLE, "url": SOURCE_URL},
            "provenance": provenance(), "notes": None})

    print(f"training: {len(cat.by_key)} courses ({sum(1 for r in cat.by_key.values() if r['code'])} "
          f"coded), {len(rows)} position requirements; Youth Protection renews every {months} months")


if __name__ == "__main__":
    main()
