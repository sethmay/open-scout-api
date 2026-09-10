"""Keep the hand-written counts in Markdown honest, the same way the data is.

The README and docs quote figures that are computable from `data/` — camp totals, coordinate
precision splits, operating-status counts. Typed by hand, they drift the moment the data moves
(the den-leader audit measured ~23% drift). This tool is the drift gate: every managed number is
wrapped in an HTML-comment sentinel

    plots all <!--n:camps.total-->553<!--/n--> camps

(invisible in rendered Markdown), and this tool recomputes the value and either checks it
(`--check`, CI) or rewrites it (`--write`). A number without a sentinel is not managed; a sentinel
naming an unknown metric is an error, so a typo cannot silently pass.

Usage:
  python tools/doc_counts.py            # check (default); nonzero on any drift
  python tools/doc_counts.py --write    # rewrite every sentinel to the computed value
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DOCS = ["README.md", "docs/endpoints.md", "docs/datasets.md"]

SENTINEL = re.compile(r"<!--n:([a-z0-9_.]+)-->(.*?)<!--/n-->", re.S)


def _load(name: str) -> list[dict]:
    d = DATA / name
    return [json.loads(p.read_text("utf-8")) for p in sorted(d.glob("*.json")) if p.name != "_events.json"]


def _open(entity: dict) -> dict | None:
    for v in entity.get("versions", []):
        if v.get("valid_to") is None:
            return v
    return None


def _feature_closure(root: str, terms: list[dict]) -> set[str]:
    narrower: dict[str, list[str]] = {}
    for t in terms:
        if t.get("broader"):
            narrower.setdefault(t["broader"], []).append(t["code"])
    out, queue = {root}, [root]
    while queue:
        for child in narrower.get(queue.pop(), []):
            if child not in out:
                out.add(child)
                queue.append(child)
    return out


def compute() -> dict[str, int]:
    m: dict[str, int] = {}

    # Per-dataset total / current, keyed <dataset>.total / <dataset>.current.
    datasets = {
        "councils": "councils", "territories": "territories", "merit-badges": "merit-badges",
        "camps": "camps", "ranks": "ranks", "awards": "awards", "oa-lodges": "oa-lodges",
        "adventures": "adventures", "positions": "positions", "training": "training",
    }
    for key, folder in datasets.items():
        ents = _load(folder)
        m[f"{key}.total"] = len(ents)
        m[f"{key}.current"] = sum(1 for e in ents if _open(e) is not None)
    rs = [json.loads(p.read_text("utf-8")) for p in sorted((DATA / "requirement-sets").glob("*.json"))]
    m["requirement-sets.total"] = len(rs)
    m["requirement-sets.current"] = sum(1 for d in rs if d.get("effective_to") is None)

    # Camps: coordinate precision, operating status, and reservation-grouped map markers.
    camps = _load("camps")
    cur = [(_open(e), e) for e in camps]
    cur = [(v, e) for v, e in cur if v is not None]
    m["camps.exact"] = sum(1 for v, _ in cur if v.get("geo_precision") == "exact")
    m["camps.approximate"] = sum(1 for v, _ in cur if v.get("geo_precision") == "approximate")
    m["camps.no_coord"] = sum(1 for v, _ in cur if v.get("lat") is None or v.get("lon") is None)
    m["camps.placeable"] = m["camps.exact"] + m["camps.approximate"]
    for st in ("active", "not_operating", "closed"):
        m[f"camps.{st}"] = sum(1 for v, _ in cur if v.get("operating_status") == st)
    m["camps.nonactive"] = m["camps.not_operating"] + m["camps.closed"]

    # Aquatics: the feature-hierarchy trap. A bare `aquatics` match undercounts the closure.
    vocab = json.loads((DATA / "vocab" / "camp-features.json").read_text("utf-8"))
    aquatics = _feature_closure("aquatics", vocab["terms"])
    codes = [{f["code"] for f in (v.get("features") or [])} for v, _ in cur]
    m["camps.aquatics_bare"] = sum(1 for s in codes if "aquatics" in s)
    m["camps.aquatics_closure"] = sum(1 for s in codes if s & aquatics)
    m["camps.aquatics_missed"] = m["camps.aquatics_closure"] - m["camps.aquatics_bare"]

    # Councils that changed name (a rename is a new version, not an event).
    m["councils.renamed"] = sum(1 for e in _load("councils")
                                if len({v["name"] for v in e["versions"]}) > 1)
    return m


def main() -> int:
    write = "--write" in sys.argv
    metrics = compute()
    errors: list[str] = []
    changed = 0
    for rel in DOCS:
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text("utf-8")

        def sub(mobj: re.Match) -> str:
            nonlocal changed
            name, shown = mobj.group(1), mobj.group(2)
            if name not in metrics:
                errors.append(f"{rel}: unknown metric '{name}'")
                return mobj.group(0)
            want = str(metrics[name])
            if shown != want:
                if write:
                    changed += 1
                    return f"<!--n:{name}-->{want}<!--/n-->"
                errors.append(f"{rel}: {name} says {shown!r}, data says {want!r}")
            return mobj.group(0)

        new = SENTINEL.sub(sub, text)
        if write and new != text:
            path.write_text(new, encoding="utf-8", newline="\n")

    if errors:
        print("doc_counts: drift\n  " + "\n  ".join(errors))
        return 1
    print(f"doc_counts: {'rewrote ' + str(changed) + ' sentinels' if write else 'ok, all sentinels match'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
