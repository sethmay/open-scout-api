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


def main() -> None:
    n = apply_graph()
    print(f"advancement graph: {n} requirement-set(s) rewritten"
          if n else "advancement graph: already applied (no changes)")


if __name__ == "__main__":
    main()
