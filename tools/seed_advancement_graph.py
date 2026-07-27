"""Turn Eagle requirement 3's merit-badge list from prose into a resolvable slot tree.

Eagle requirement 3 reads, verbatim: "Earn a total of 21 merit badges ... including these 14 merit
badges: (a) First Aid, ... (i) Emergency Preparedness OR Lifesaving, (j) Environmental Science OR
Sustainability, ... (l) Swimming OR Hiking OR Cycling ... You must choose only one of the merit
badges listed in categories i, j, and l."

That is a graph, and it shipped as one string. The consequence is concrete: a tracker counting the
18 badges flagged `eagle_required` reports "9 of 18" when the Scout owes **14 slots**, three of
which are either/or. Both numbers are real and the source uses both — Star and Life requirement 3
say "any of the 18 merit badges on the required list for Eagle" — so this adds the slot structure
rather than touching the flag, and the pipeline checks the two agree.

After this runs, requirement 3 has 14 children: eleven leaves carrying `ref` to a merit badge, and
three `choose: 1` option groups. The parent keeps its verbatim text; the children make it
resolvable, using the same `ref` mechanism the Cub rank trees use for adventures.

    python tools/seed_advancement_graph.py            # apply to the committed requirement-sets

Idempotent: re-running rebuilds the same children from `tools/advancement_graph.json`. It is also
called by tools/seed_rank_requirements.py after that tool regenerates the docs from the source PDF,
so a full regeneration cannot silently drop the structure.
"""

from __future__ import annotations

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
FACTS = ROOT / "tools" / "advancement_graph.json"
RS = ROOT / "data" / "requirement-sets"
BADGES = ROOT / "data" / "merit-badges"


def badge_names() -> dict[str, str]:
    out = {}
    for p in sorted(BADGES.glob("*.json")):
        if p.name == "_events.json":
            continue
        d = json.loads(p.read_text("utf-8"))
        cur = next((v for v in d["versions"] if v.get("valid_to") is None), d["versions"][-1])
        out[d["id"]] = cur["name"]
    return out


def build_children(spec: dict, names: dict[str, str], verbatim: str) -> list[dict]:
    """The slot tree for one requirement, verified against the requirement's own text.

    Every badge name placed in the tree must appear in the verbatim requirement, so a slot table
    that drifts from the source it claims to structure cannot be applied.
    """
    kids = []
    for slot in spec["slots"]:
        label, badges = slot["label"], slot["badges"]
        for b in badges:
            if b not in names:
                raise SystemExit(f"slot {label}: no merit badge {b!r}")
            if names[b].lower() not in verbatim.lower():
                raise SystemExit(f"slot {label}: {names[b]!r} does not appear in the requirement "
                                 f"text it claims to structure")
        num = f"{spec['requirement']}{label}"
        if len(badges) == 1:
            kids.append({"number": num, "text": names[badges[0]],
                         "ref": f"merit-badge:{badges[0]}"})
        else:
            kids.append({
                "number": num,
                "text": " OR ".join(names[b] for b in badges),
                "choose": 1,
                "children": [{"number": f"{num}({i})", "text": names[b], "ref": f"merit-badge:{b}"}
                             for i, b in enumerate(badges, start=1)],
            })
    return kids


def apply_graph(quiet: bool = False) -> int:
    facts = json.loads(FACTS.read_text("utf-8"))
    names = badge_names()
    changed = 0
    for key, spec in facts.items():
        if not isinstance(spec, dict) or "slots" not in spec:
            continue
        subject = spec["subject"]
        slug = subject.split(":", 1)[1]
        matches = [p for p in sorted(RS.glob(f"{slug}-*.json"))
                   if json.loads(p.read_text("utf-8")).get("subject") == subject
                   and json.loads(p.read_text("utf-8")).get("effective_to") is None]
        if not matches:
            raise SystemExit(f"{key}: no in-force requirement-set for {subject}")
        for p in matches:
            doc = json.loads(p.read_text("utf-8"))
            req = next((r for r in doc["requirements"] if r["number"] == spec["requirement"]), None)
            if req is None:
                raise SystemExit(f"{p.name}: no requirement {spec['requirement']!r}")
            kids = build_children(spec, names, req.get("text") or "")
            if req.get("children") == kids:
                continue
            req["children"] = kids
            p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
            changed += 1
            if not quiet:
                opt = sum(1 for k in kids if k.get("choose"))
                print(f"  {p.name}: requirement {spec['requirement']} -> {len(kids)} slots "
                      f"({opt} either/or) over "
                      f"{sum(len(s['badges']) for s in spec['slots'])} badges")
    return changed


def apply_positions(quiet: bool = False) -> int:
    """Give each rank's positions-of-responsibility requirement a resolvable option tree.

    The requirement offers a choice of unit type, then a position within it — plus, for Star and
    Life only, a Scoutmaster-approved project instead. That is three levels of choice flattened
    into one sentence; here it is `choose: 1` over the unit-type groups, each itself `choose: 1`
    over `position:` refs.
    """
    facts = json.loads(FACTS.read_text("utf-8"))
    names = {r["slug"]: r["name"] for r in facts["positions"]}
    labels = dict(UNIT_GROUPS)
    changed = 0
    for rank, e in facts["rank_positions"].items():
        p = RS / f"{rank}-2024.json"
        doc = json.loads(p.read_text("utf-8"))
        req = next(r for r in doc["requirements"] if r["number"] == e["requirement"])
        kids, n = [], 0
        for g in e["groups"]:
            n += 1
            code = g["unit_type"]
            kids.append({
                "number": f"{e['requirement']}{chr(96 + n)}",
                "text": labels[code].rstrip("."),
                "choose": 1,
                "children": [{"number": f"{e['requirement']}{chr(96 + n)}({i})",
                              "text": names[s], "ref": f"position:{s}"}
                             for i, s in enumerate(g["slugs"], start=1)],
            })
        if e.get("lone_scout"):
            n += 1
            kids.append({"number": f"{e['requirement']}{chr(96 + n)}",
                         "text": f"{labels['lone_scout'].rstrip('.')} {e['lone_scout']}"})
        if e.get("leadership_project"):
            n += 1
            kids.append({"number": f"{e['requirement']}{chr(96 + n)}",
                         "text": "Carry out a Scoutmaster-approved leadership project to help the troop."})
        node = {"choose": 1, "children": kids}
        if req.get("choose") == 1 and req.get("children") == kids:
            continue
        req["choose"], req["children"] = node["choose"], node["children"]
        p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                     encoding="utf-8", newline="\n")
        changed += 1
        if not quiet:
            print(f"  {p.name}: requirement {e['requirement']} -> {len(kids)} alternatives "
                  f"({sum(len(k.get('children') or []) for k in kids)} position refs)")
    return changed


def main() -> None:
    import sys
    if "--extract" in sys.argv:
        extract_positions()
    n = generate_positions()
    print(f"positions: {n} entities written")
    n = apply_graph() + apply_positions() + apply_counts()
    print(f"advancement graph: {n} requirement-set(s) rewritten"
          if n else "advancement graph: already applied (no changes)")



# --------------------------------------------------------------------------- positions

RANK_POR = {"star": "5", "life": "5", "eagle": "4"}
UNIT_GROUPS = [("scout_troop", "Scout troop."),
               ("crew_or_ship", "Venturing crew/Sea Scout ship."),
               ("lone_scout", "Lone Scout.")]
SMALL = {"of", "the", "in", "to", "and", "or", "a", "an", "for"}


def title(name: str) -> str:
    """Display name from a mid-sentence lowercase list item."""
    words = name.split()
    return " ".join(w.capitalize() if i == 0 or w not in SMALL else w for i, w in enumerate(words))


def pos_slug(name: str) -> str:
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", name.replace("\u2019", ""))).strip("-")


def _por_groups(text: str) -> dict[str, str]:
    """The requirement's own unit-type groups, keyed by our vocab code."""
    marks = [(text.find(lbl), code, lbl) for code, lbl in UNIT_GROUPS]
    marks = sorted((i, c, l) for i, c, l in marks if i >= 0)
    out = {}
    for n, (i, code, lbl) in enumerate(marks):
        end = marks[n + 1][0] if n + 1 < len(marks) else len(text)
        out[code] = text[i + len(lbl):end].strip()
    return out


def _por_items(segment: str) -> list[str]:
    seg = re.sub(r"\(See[^)]*\)", "", segment).strip().rstrip(".")
    seg = re.sub(r",?\s+or\s+", ", ", seg)
    return [re.sub(r"\s+", " ", x).strip().lower() for x in seg.split(",") if x.strip()]


def extract_positions() -> None:
    """Derive the position catalog and each rank's option groups from the requirement text itself.

    Positions are listed only inside the rank requirements, so the requirement text IS the source;
    deriving rather than hand-typing means a reissued requirements book changes the catalog by
    re-running this, and a typo cannot creep in unnoticed.
    """
    facts = json.loads(FACTS.read_text("utf-8"))
    catalog: dict[str, dict] = {}
    rank_positions: dict[str, dict] = {}
    for rank, num in RANK_POR.items():
        p = RS / f"{rank}-2024.json"
        doc = json.loads(p.read_text("utf-8"))
        req = next(r for r in doc["requirements"] if r["number"] == num)
        text = req["text"]
        groups = _por_groups(text)
        entry = {"requirement": num, "groups": [], "lone_scout": None,
                 # Star and Life offer a Scoutmaster-approved project instead of a position; Eagle
                 # does not, and that asymmetry is in the requirement's own parenthetical.
                 "leadership_project": "leadership project" in text.lower()}
        for code, _ in UNIT_GROUPS:
            seg = groups.get(code)
            if seg is None:
                continue
            if code == "lone_scout":
                entry["lone_scout"] = re.sub(r"\s+", " ", seg).strip()
                continue
            slugs = []
            for name in _por_items(seg):
                slug = pos_slug(name)
                rec = catalog.setdefault(slug, {"slug": slug, "name": title(name), "unit_types": []})
                if code not in rec["unit_types"]:
                    rec["unit_types"].append(code)
                slugs.append(slug)
            entry["groups"].append({"unit_type": code, "slugs": slugs})
        rank_positions[rank] = entry
    facts["positions"] = [catalog[k] for k in sorted(catalog)]
    facts["rank_positions"] = rank_positions
    FACTS.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n",
                     encoding="utf-8", newline="\n")
    only = {s: [r for r, e in rank_positions.items()
                if any(s in g["slugs"] for g in e["groups"])] for s in catalog}
    partial = {s: r for s, r in only.items() if len(r) < len(RANK_POR)}
    print(f"positions: {len(catalog)} distinct across {len(RANK_POR)} ranks")
    print(f"  accepted by only some ranks: {partial or 'none'}")


def generate_positions() -> int:
    facts = json.loads(FACTS.read_text("utf-8"))
    out = ROOT / "data" / "positions"
    out.mkdir(parents=True, exist_ok=True)
    accepted: dict[str, list[str]] = {}
    for rank, e in facts["rank_positions"].items():
        for g in e["groups"]:
            for s in g["slugs"]:
                accepted.setdefault(s, []).append(rank)
    for rec in facts["positions"]:
        ranks = sorted(set(accepted.get(rec["slug"], [])))
        note = None
        if len(ranks) < len(RANK_POR):
            missing = sorted(set(RANK_POR) - set(ranks))
            note = ("Accepted for " + ", ".join(r.capitalize() for r in ranks)
                    + " but not " + ", ".join(r.capitalize() for r in missing)
                    + "; the requirement lists differ.")
        doc = {
            "id": rec["slug"], "kind": "position",
            "versions": [{
                "valid_from": None, "valid_to": None,
                "name": rec["name"], "audience": "youth",
                "unit_types": rec["unit_types"],
                "provenance": {
                    "sources": [{"citation": "2024 Scouts BSA Requirements (No. 33216), "
                                             "Star/Life/Eagle positions of responsibility"}],
                    "method": "curated", "verified_at": "2026-07-27", "confidence": 0.9,
                    "notes": "Name and unit types derived from the rank requirements that list it; "
                             "these positions appear in no other published catalog.",
                },
            }],
            "notes": note,
        }
        (out / f"{rec['slug']}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return len(facts["positions"])


# ------------------------------------------------------- countable facts (tenure, badge counts)

WORDNUM = {w: i for i, w in enumerate(
    "zero one two three four five six seven eight nine ten eleven twelve".split())}

# "for six months", "for at least six months", "for a period of at least six months"
TENURE_RE = re.compile(r"\bfor (?:a period of )?(?:at least )?([\w-]+) months?\b", re.I)
# Star/Life: "Earn six merit badges" / "Earn five more merit badges"
EARN_RE = re.compile(r"\bEarn ([\w-]+) (?:more )?merit badges\b", re.I)
# Eagle: "Earn a total of 21 merit badges (10 more than required for the Life rank)"
TOTAL_RE = re.compile(r"\bEarn a total of ([\w-]+) merit badges\b", re.I)
DELTA_RE = re.compile(r"\(([\w-]+) more than required for the \w+ rank\)", re.I)
# "(so that you have 11 in all)"
CUMUL_RE = re.compile(r"\(so that you have ([\w-]+) in all\)", re.I)
# Star/Life only: "including any four from the required list for Eagle". Eagle's own wording is
# "including these 14 merit badges" — a slot tree, not list membership — and deliberately misses.
FROM_LIST_RE = re.compile(
    r"\bincluding any ([\w-]+) (?:additional )?(?:merit )?(?:badges )?from the required list", re.I)


def _num(tok: str) -> int | None:
    tok = tok.strip().lower().replace(",", "")
    return int(tok) if tok.isdigit() else WORDNUM.get(tok)


def _walk(reqs: list[dict]):
    for r in reqs:
        yield r
        yield from _walk(r.get("children") or [])


def _inforce_rank_sets() -> list[Path]:
    out = []
    for p in sorted(RS.glob("*.json")):
        d = json.loads(p.read_text("utf-8"))
        if d.get("subject", "").startswith("rank:") and d.get("effective_to") is None:
            out.append(p)
    return out


def apply_counts(quiet: bool = False) -> int:
    """Make the numbers a rank prints in prose countable, derived from that prose.

    Two facts hide in requirement text and nowhere else:

    `tenure_months` — how long you must be active or serve in a position. Thirteen of them across
    Scouts BSA, Sea Scout and Venturing ranks, phrased three different ways ("for six months", "for
    at least six months", "for a period of at least six months"). All are minimums: serving longer
    never fails the requirement, so one integer is the honest reading of all three.

    `badge_count` — how many merit badges a rank needs. Star and Life say "any four/three from the
    required list for Eagle", which is *list membership*: all 18 badges are interchangeable, so
    earning both Swimming and Hiking counts twice (confirmed by the project owner, 2026-07-27).
    Eagle's own requirement is the different rule — 14 specific slots with either/or groups — and
    its "including these 14 merit badges" wording deliberately fails `FROM_LIST_RE`, because the
    slot tree built by `apply_graph()` is the authoritative constraint there, not a bare count.

    Derived from each requirement's own verbatim text at apply time, so a reissued requirement
    changes the numbers with it and nothing needs re-typing.
    """
    changed = 0
    for p in _inforce_rank_sets():
        doc = json.loads(p.read_text("utf-8"))
        before = json.dumps(doc, sort_keys=True)
        for req in _walk(doc["requirements"]):
            text = req.get("text") or ""
            m = TENURE_RE.search(text)
            months = _num(m.group(1)) if m else None
            if months:
                req["tenure_months"] = months
            counts: dict[str, int] = {}
            if (m := TOTAL_RE.search(text)):          # Eagle: total stated, delta parenthesised
                counts["cumulative"] = _num(m.group(1))
                if (d := DELTA_RE.search(text)):
                    counts["earn"] = _num(d.group(1))
            elif (m := EARN_RE.search(text)):         # Star/Life: earned-at-this-rank stated
                counts["earn"] = _num(m.group(1))
                c = CUMUL_RE.search(text)
                counts["cumulative"] = _num(c.group(1)) if c else counts["earn"]
            if counts and (m := FROM_LIST_RE.search(text)):
                counts["from_eagle_required"] = _num(m.group(1))
            if counts:
                req["badge_count"] = {k: counts[k] for k in
                                      ("earn", "cumulative", "from_eagle_required") if k in counts}
        after = json.dumps(doc, sort_keys=True)
        if before != after:
            p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
            changed += 1
            if not quiet:
                t = sum(1 for r in _walk(doc["requirements"]) if "tenure_months" in r)
                b = sum(1 for r in _walk(doc["requirements"]) if "badge_count" in r)
                print(f"  {p.name}: {t} tenure, {b} badge-count fact(s)")
    return changed
if __name__ == "__main__":
    main()
