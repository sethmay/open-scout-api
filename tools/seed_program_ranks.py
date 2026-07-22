"""Seed generator: Cub Scout / Venturing / Sea Scout rank entities (entity layer).

Adds the non-Scouts-BSA advancement ranks as versioned entities (name/program/order
stable -> one version each). Requirement CONTENT lives in requirement-set documents
(subject 'rank:<slug>'), produced by seed_program_rank_requirements.py.

Reads the committed facts file tools/program_rank_requirements.json (program/order/
name/url per rank), so this stays in sync with the requirement generator. Facts
(names, order, program) are common knowledge, confirmed against scouting.org /
seascout.org. Output: data/ranks/<slug>.json
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / "tools" / "program_rank_requirements.json"
OUT = ROOT / "data" / "ranks"
TODAY = "2026-07-21"


def main() -> None:
    facts = json.loads(FACTS.read_text("utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for slug, f in facts.items():
        entity = {
            "id": slug, "kind": "rank",
            "versions": [{
                "valid_from": None, "valid_to": None,
                "name": f["name"], "program": f["program"], "order": f["order"],
                "url": f["rank_url"], "description": None,
                "provenance": {
                    "sources": [{"url": f["rank_url"]}],
                    "method": "curated", "verified_at": TODAY, "confidence": 0.9,
                    "notes": "Rank name/order/program; requirement content in requirement-set docs.",
                },
            }],
            "notes": None,
        }
        (OUT / f"{slug}.json").write_text(
            json.dumps(entity, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        n += 1
    print(f"program ranks: {n} rank entities written "
          f"({sum(1 for f in facts.values() if f['program']=='cub_scouts')} cub, "
          f"{sum(1 for f in facts.values() if f['program']=='venturing')} venturing, "
          f"{sum(1 for f in facts.values() if f['program']=='sea_scouts')} sea)")


if __name__ == "__main__":
    main()
