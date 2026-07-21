"""Seed generator for advancement ranks (entity layer).

The 7 Scouts BSA ranks as versioned entities. Names/order/program are stable, so one
version each. Requirement CONTENT is NOT here — it lives in requirement-set documents
(subject: 'rank:<slug>'), generated from the official Scouts BSA Requirements once that
source is available. Facts (names, order, program) are common knowledge, confirmed
against Wikipedia 'Ranks in Scouts BSA' + scouting.org advancement.

Output: data/ranks/<slug>.json
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "ranks"
TODAY = "2026-07-21"
ADV_URL = "https://www.scouting.org/programs/scouts-bsa/advancement-and-awards/"

# (slug, name, order)
SCOUTS_BSA = [
    ("scout", "Scout", 1),
    ("tenderfoot", "Tenderfoot", 2),
    ("second-class", "Second Class", 3),
    ("first-class", "First Class", 4),
    ("star", "Star", 5),
    ("life", "Life", 6),
    ("eagle", "Eagle Scout", 7),
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for slug, name, order in SCOUTS_BSA:
        entity = {
            "id": slug, "kind": "rank",
            "versions": [{
                "valid_from": None, "valid_to": None,
                "name": name, "program": "scouts_bsa", "order": order,
                "url": ADV_URL, "description": None,
                "provenance": {
                    "sources": [
                        {"url": "https://en.wikipedia.org/wiki/Ranks_in_Scouts_BSA", "accessed": TODAY},
                        {"url": ADV_URL},
                    ],
                    "method": "curated", "verified_at": TODAY, "confidence": 0.9,
                    "notes": "Rank name/order/program; requirement content in requirement-set docs.",
                },
            }],
            "notes": None,
        }
        (OUT / f"{slug}.json").write_text(
            json.dumps(entity, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"ranks: {len(SCOUTS_BSA)} Scouts BSA rank entities written")


if __name__ == "__main__":
    main()
