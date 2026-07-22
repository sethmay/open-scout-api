"""Seed generator: Cub/Venturing/Sea Scout rank requirement-sets (14 documents).

Reads the committed facts file tools/program_rank_requirements.json — the structured
requirement trees extracted from OFFICIAL sources (scouting.org Cub adventure + Venturing
rank pages; official Sea Scout rank PDFs; the Venturing rank via usscouts.org). Structure
was organized with LLM assistance, but EVERY requirement `text` was verified to appear
verbatim (whitespace-insensitive) in the official source before baking — so the text is a
faithful reproduction, not a paraphrase. Requirement text is (c) Scouting America
(text_rights), reproduced with attribution for non-commercial use; see NOTICE.md.

Output: data/requirement-sets/<slug>-<year>.json (subject 'rank:<slug>').
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / "tools" / "program_rank_requirements.json"
OUT = ROOT / "data" / "requirement-sets"
TODAY = "2026-07-21"
TEXT_RIGHTS = ("Requirement text \u00a9 Scouting America, reproduced with attribution for "
               "non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. "
               "See NOTICE.md.")


def clean_node(n: dict) -> dict:
    """Keep only schema fields; drop empty children/null choose; recurse."""
    out = {"number": str(n["number"])}
    if n.get("text") is not None and str(n["text"]).strip():
        out["text"] = str(n["text"]).strip()
    if n.get("choose") is not None:
        out["choose"] = int(n["choose"])
    kids = [clean_node(c) for c in (n.get("children") or []) if isinstance(c, dict)]
    if kids:
        out["children"] = kids
    # a node must carry text, summary, or children (schema anyOf)
    if "text" not in out and "children" not in out:
        out["text"] = str(n.get("text") or n["number"])
    return out


def main() -> None:
    facts = json.loads(FACTS.read_text("utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for slug, f in facts.items():
        year = f["effective_from"][:4]
        rid = f"{slug}-{year}"
        reqs = [clean_node(r) for r in f["requirements"]]
        doc = {
            "id": rid, "kind": "requirement-set",
            "subject": f"rank:{slug}",
            "effective_from": f["effective_from"],
            "effective_to": None,
            "supersedes": None,
            "source_document": f["source_document"],
            "includes_official_text": True,
            "text_rights": TEXT_RIGHTS,
            "requirements": reqs,
            "provenance": {
                "sources": [{"url": f["source_document"]["url"], "accessed": TODAY}],
                "method": "scraped", "verified_at": TODAY, "confidence": 0.9,
                "notes": ("Requirement text verbatim from the official source (verified as a "
                          "whitespace-insensitive substring of the page/PDF); tree structure "
                          "organized with LLM assistance."),
            },
            "notes": None,
        }
        (OUT / f"{rid}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
        n += 1
    print(f"program rank requirement-sets: {n} documents written")


if __name__ == "__main__":
    main()
