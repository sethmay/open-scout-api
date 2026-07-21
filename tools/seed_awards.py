"""Seed generator for the awards catalog (entity layer).

Earned awards & recognitions (religious emblems, training awards, scouting honors /
special recognitions) as versioned `award` entities: data/awards/<slug>.json. Scope
deliberately EXCLUDES plain uniform insignia, service stars, tenure/veteran pins, and the
per-faith religious-emblem programs (a separate, larger dataset).

FACTS ONLY: name, category, audience, square-knot + insignia catalog numbers, wear. No
verbatim Guide to Awards & Insignia prose is reproduced (that text is (c) Scouting
America); `summary` is original one-line prose. The records below were extracted from the
official Guide to Awards and Insignia (No. 33066) with LLM assistance and then verified:
every catalog number was checked to occur in the source, knot->award pairings were
anchor-checked, and categories/audience/summaries curated. Provenance therefore declares
method=llm_extraction, confidence 0.85. Re-running writes identical files.
"""
from __future__ import annotations

import json
from pathlib import Path

VERIFIED_AT = "2026-07-21"
SOURCE_CITATION = "Guide to Awards and Insignia (Scouting America, No. 33066, 2024-2025)"
AWARDS_URL = "https://www.scouting.org/awards/awards-central/"
NOTES = ("Facts (name, catalog numbers, wear) transcribed from the official Guide to Awards "
         "and Insignia and verified against the source; category, audience, and summary are "
         "classifications. Per-faith religious emblems and plain uniform insignia excluded.")

AWARDS = json.loads(r"""
[
  {
    "slug": "alumni-award",
    "name": "Alumni Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "611866",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes Scouting alumni; may include the Alumnus of the Year device."
  },
  {
    "slug": "arrow-of-light-rank-knot",
    "name": "Arrow of Light Rank Knot",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [
      "cub_scouts"
    ],
    "square_knot_no": "5018",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Adult knot for having earned the Arrow of Light rank as a youth."
  },
  {
    "slug": "arrowhead-honor",
    "name": "Arrowhead Honor",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "604940"
    ],
    "wear": "left sleeve on long-sleeved shirt",
    "restricted": false,
    "summary": "Recognizes commissioners for completing training milestones."
  },
  {
    "slug": "asian-american-scouting-service-award",
    "name": "Asian American Scouting Service Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [],
    "wear": null,
    "restricted": false,
    "summary": "Recognizes service developing Scouting opportunities for Asian American youth."
  },
  {
    "slug": "commissioner-award-of-excellence-in-unit-service",
    "name": "Commissioner Award of Excellence in Unit Service",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "613223",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes commissioners for excellence in delivering unit service."
  },
  {
    "slug": "community-organization-award",
    "name": "Community Organization Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "613864",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes Scouters for service honored by an approved national organization."
  },
  {
    "slug": "council-alumnus-of-the-year",
    "name": "Council Alumnus of the Year",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "611866",
    "insignia_nos": [
      "621089",
      "621294",
      "621404"
    ],
    "wear": null,
    "restricted": false,
    "summary": "Council recognition of an outstanding Scouting alumnus, worn with acorn device."
  },
  {
    "slug": "council-duty-to-god-award",
    "name": "Council Duty to God Award",
    "category": "religious_emblem",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [],
    "wear": null,
    "restricted": false,
    "summary": "Annual recognition of registered Scouters for transformational leadership supporting the spiritual foundation of Scouting at the council level."
  },
  {
    "slug": "den-leader-training-award",
    "name": "Den Leader Training Award",
    "category": "training_award",
    "audience": "adult",
    "programs": [
      "cub_scouts"
    ],
    "square_knot_no": "5016",
    "insignia_nos": [
      "604950",
      "615864",
      "620592",
      "932"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes den leaders for tenure, training, and performance."
  },
  {
    "slug": "distinguished-commissioner-service-award",
    "name": "Distinguished Commissioner Service Award",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "5019",
    "insignia_nos": [
      "17608",
      "17609",
      "17610",
      "747",
      "748",
      "749"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes commissioners for distinguished, sustained service, with plaque and medallion by level."
  },
  {
    "slug": "distinguished-conservation-service-award",
    "name": "Distinguished Conservation Service Award",
    "category": "special_recognition",
    "audience": "both",
    "programs": [],
    "square_knot_no": "1900",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes distinguished service to natural resource conservation, conferred by councils and the National Council."
  },
  {
    "slug": "distinguished-eagle-scout-award",
    "name": "Distinguished Eagle Scout Award",
    "category": "scouting_honor",
    "audience": "adult",
    "programs": [
      "scouts_bsa"
    ],
    "square_knot_no": null,
    "insignia_nos": [
      "328",
      "330",
      "94"
    ],
    "wear": "on Eagle knot",
    "restricted": false,
    "summary": "Recognizes Eagle Scouts for distinguished achievement over at least 25 years."
  },
  {
    "slug": "district-award-of-merit",
    "name": "District Award of Merit",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "5013",
    "insignia_nos": [
      "17565"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "District recognition for service to youth by district Scouters."
  },
  {
    "slug": "doctorate-of-commissioner-science-award",
    "name": "Doctorate of Commissioner Science Award",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "18093",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes commissioners who complete advanced commissioner training and a service project."
  },
  {
    "slug": "eagle-scout-nesa-life-membership-award",
    "name": "Eagle Scout NESA Life Membership Award",
    "category": "scouting_honor",
    "audience": "adult",
    "programs": [
      "scouts_bsa"
    ],
    "square_knot_no": "18092",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Eagle Scout knot with silver border for NESA life members."
  },
  {
    "slug": "eagle-scout-rank-knot",
    "name": "Eagle Scout Rank Knot",
    "category": "scouting_honor",
    "audience": "adult",
    "programs": [
      "scouts_bsa"
    ],
    "square_knot_no": "5011",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Adult knot recognizing having earned the Eagle Scout rank as a youth."
  },
  {
    "slug": "heroism-award",
    "name": "Heroism Award",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": "5020",
    "insignia_nos": [],
    "wear": "above left pocket",
    "restricted": true,
    "summary": "Awarded for meritorious action involving risk to save a life."
  },
  {
    "slug": "honor-medal",
    "name": "Honor Medal",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": "5010",
    "insignia_nos": [],
    "wear": "above left pocket",
    "restricted": true,
    "summary": "Awarded for saving or attempting to save life at risk to self, with Crossed Palms for extreme risk."
  },
  {
    "slug": "international-scouter-award",
    "name": "International Scouter Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "618969",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": true,
    "summary": "Recognizes Scouters who contribute to international Scouting."
  },
  {
    "slug": "james-e-west-fellowship-award",
    "name": "James E. West Fellowship Award",
    "category": "special_recognition",
    "audience": "both",
    "programs": [],
    "square_knot_no": "606783",
    "insignia_nos": [
      "613538",
      "613539",
      "613540",
      "613541"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes gifts to a council endowment in a member's honor."
  },
  {
    "slug": "medal-of-merit",
    "name": "Medal of Merit",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": "5025",
    "insignia_nos": [
      "620561"
    ],
    "wear": "above left pocket",
    "restricted": true,
    "summary": "Awarded for outstanding meritorious action not involving risk to self."
  },
  {
    "slug": "national-camping-school-emblem",
    "name": "National Camping School emblem",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "276",
      "277",
      "278"
    ],
    "wear": "right pocket",
    "restricted": false,
    "summary": "Recognizes Scouters who complete National Camping School training."
  },
  {
    "slug": "national-duty-to-god-award",
    "name": "National Duty to God Award",
    "category": "religious_emblem",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [],
    "wear": null,
    "restricted": false,
    "summary": "Annual recognition of adult members for exemplary faith-based service and promotion of religious duty in Scouting."
  },
  {
    "slug": "nesa-national-eagle-scout-association-membership",
    "name": "NESA (National Eagle Scout Association) Membership",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "2509"
    ],
    "wear": "right pocket",
    "restricted": false,
    "summary": "Recognizes membership in the National Eagle Scout Association."
  },
  {
    "slug": "nesa-outstanding-eagle-scout-award",
    "name": "NESA Outstanding Eagle Scout Award",
    "category": "scouting_honor",
    "audience": "adult",
    "programs": [
      "scouts_bsa"
    ],
    "square_knot_no": null,
    "insignia_nos": [
      "614640",
      "780744"
    ],
    "wear": "above left pocket",
    "restricted": false,
    "summary": "Recognizes Eagle Scouts for distinguished service at local, state, or regional levels."
  },
  {
    "slug": "north-star-award",
    "name": "North Star Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "610645"
    ],
    "wear": "worn around the neck",
    "restricted": false,
    "summary": "Honors nonregistered Scouting supporters at the level of the Silver Beaver and above."
  },
  {
    "slug": "nylt-trained-strip",
    "name": "NYLT Trained Strip",
    "category": "training_award",
    "audience": "youth",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "622630"
    ],
    "wear": "sleeve pocket flap above badge of office, or left sleeve below emblem of office",
    "restricted": false,
    "summary": "Recognizes youth leaders who completed National Youth Leadership Training."
  },
  {
    "slug": "order-of-the-arrow-distinguished-service-award",
    "name": "Order of the Arrow Distinguished Service Award",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": "5528",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "National OA recognition for outstanding service to the Order over time."
  },
  {
    "slug": "order-of-the-arrow-founder-s-award",
    "name": "Order of the Arrow Founder's Award",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "604943",
      "604954"
    ],
    "wear": "right pocket flap",
    "restricted": true,
    "summary": "Honors Arrowmen who give outstanding service to their lodge."
  },
  {
    "slug": "order-of-the-arrow-membership",
    "name": "Order of the Arrow Membership",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "604942"
    ],
    "wear": "right pocket flap",
    "restricted": false,
    "summary": "Recognizes membership in the Order of the Arrow, Scouting's honor society."
  },
  {
    "slug": "philmont-training-center-masters-track-award",
    "name": "Philmont Training Center Masters Track Award",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "18090",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes completion of the Masters Track program at Philmont Training Center."
  },
  {
    "slug": "powder-horn",
    "name": "Powder Horn",
    "category": "training_award",
    "audience": "adult",
    "programs": [
      "scouts_bsa",
      "venturing"
    ],
    "square_knot_no": null,
    "insignia_nos": [
      "4044"
    ],
    "wear": "left pocket",
    "restricted": false,
    "summary": "Recognizes adult leaders who complete a Powder Horn high-adventure resource course."
  },
  {
    "slug": "professional-training-award",
    "name": "Professional Training Award",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": true,
    "summary": "Recognizes professional Scouters for completing professional development training."
  },
  {
    "slug": "quartermaster-award",
    "name": "Quartermaster Award",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [
      "sea_scouts"
    ],
    "square_knot_no": "633337",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": true,
    "summary": "Highest rank award in Sea Scouts, worn as an adult knot."
  },
  {
    "slug": "religious-emblems",
    "name": "Religious Emblems",
    "category": "religious_emblem",
    "audience": "both",
    "programs": [],
    "square_knot_no": "5007",
    "insignia_nos": [
      "5014",
      "604950",
      "927",
      "931",
      "932",
      "940"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Knot recognizing earning a religious emblem of any faith, with devices by program level."
  },
  {
    "slug": "scouter-s-key-skipper-s-key",
    "name": "Scouter's Key/Skipper's Key",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "5006",
    "insignia_nos": [
      "604950",
      "620592",
      "871",
      "872",
      "924",
      "926",
      "927",
      "940"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes trained leaders for tenure and performance in their program phase."
  },
  {
    "slug": "scouter-s-training-award",
    "name": "Scouter's Training Award",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "5008",
    "insignia_nos": [
      "604950",
      "871",
      "872",
      "922",
      "926",
      "927",
      "931",
      "940"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes leaders for completing training and tenure requirements."
  },
  {
    "slug": "scouting-service-award",
    "name": "Scouting Service Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "625334",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes Scouters for service to an approved underserved market."
  },
  {
    "slug": "scouting-vale-la-pena-service-award",
    "name": "\u00a1Scouting \u2026 Vale la Pena! Service Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "619053",
    "insignia_nos": [
      "619108",
      "619109",
      "619239"
    ],
    "wear": null,
    "restricted": false,
    "summary": "Recognizes service developing Scouting opportunities for Hispanic/Latino youth."
  },
  {
    "slug": "sea-scout-leadership-award",
    "name": "Sea Scout Leadership Award",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [
      "sea_scouts"
    ],
    "square_knot_no": "14220",
    "insignia_nos": [
      "931"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes outstanding leadership by Sea Scouts or adult leaders."
  },
  {
    "slug": "silver-antelope-award",
    "name": "Silver Antelope Award",
    "category": "scouting_honor",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "5005",
    "insignia_nos": [
      "201",
      "322",
      "34",
      "666"
    ],
    "wear": "above left pocket",
    "restricted": false,
    "summary": "Territory-level recognition for distinguished service to youth."
  },
  {
    "slug": "silver-beaver-award",
    "name": "Silver Beaver Award",
    "category": "scouting_honor",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "5003",
    "insignia_nos": [
      "200",
      "33",
      "331",
      "665"
    ],
    "wear": "above left pocket",
    "restricted": false,
    "summary": "Council-level recognition for distinguished service to youth."
  },
  {
    "slug": "silver-buffalo-award",
    "name": "Silver Buffalo Award",
    "category": "scouting_honor",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "5004",
    "insignia_nos": [
      "324",
      "614186",
      "671"
    ],
    "wear": "above left pocket",
    "restricted": false,
    "summary": "National-level recognition for distinguished service to youth."
  },
  {
    "slug": "special-needs-scouting-service-award",
    "name": "Special Needs Scouting Service Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "625334",
    "insignia_nos": [
      "641462",
      "641463"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes Scouters who provide valuable service to youth with special needs or disabilities."
  },
  {
    "slug": "spirit-of-whitney-m-young-jr-service-award",
    "name": "Spirit of Whitney M. Young Jr. Service Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "625334",
    "insignia_nos": [
      "619051",
      "619054",
      "619105",
      "619106",
      "619110"
    ],
    "wear": "nonuniform wear",
    "restricted": true,
    "summary": "Recognizes outstanding contribution through Scouting to low-income urban/rural youth."
  },
  {
    "slug": "the-elbert-k-fretwell-outstanding-educator-award",
    "name": "The Elbert K. Fretwell Outstanding Educator Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "614187"
    ],
    "wear": null,
    "restricted": false,
    "summary": "Recognizes educators who exemplify the values of the Scout Oath and Law."
  },
  {
    "slug": "unit-leader-award-of-merit",
    "name": "Unit Leader Award of Merit",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "610091",
    "insignia_nos": [
      "610093",
      "610094",
      "610095",
      "635892",
      "646304"
    ],
    "wear": "above left pocket",
    "restricted": false,
    "summary": "Recognizes unit leaders who deliver an outstanding program in their unit."
  },
  {
    "slug": "venturing-leadership-award",
    "name": "Venturing Leadership Award",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [
      "venturing"
    ],
    "square_knot_no": "14220",
    "insignia_nos": [
      "940"
    ],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes outstanding leadership by Venturers or adult leaders."
  },
  {
    "slug": "venturing-summit-award",
    "name": "Venturing Summit Award",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [
      "venturing"
    ],
    "square_knot_no": "5027",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Highest Venturing recognition, worn as an adult knot."
  },
  {
    "slug": "vigil-honor",
    "name": "Vigil Honor",
    "category": "scouting_honor",
    "audience": "both",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "604944"
    ],
    "wear": "nonuniform wear",
    "restricted": false,
    "summary": "Highest honor of the Order of the Arrow for distinguished service."
  },
  {
    "slug": "william-d-boyce-new-unit-organizer-award",
    "name": "William D. Boyce New-Unit Organizer Award",
    "category": "special_recognition",
    "audience": "adult",
    "programs": [],
    "square_knot_no": "14269",
    "insignia_nos": [],
    "wear": "above the left pocket",
    "restricted": false,
    "summary": "Recognizes Scouters who organize new Scouting units."
  },
  {
    "slug": "wood-badge",
    "name": "Wood Badge",
    "category": "training_award",
    "audience": "adult",
    "programs": [],
    "square_knot_no": null,
    "insignia_nos": [
      "2173",
      "2175",
      "2176",
      "2177"
    ],
    "wear": "worn only with official field uniform",
    "restricted": true,
    "summary": "Recognizes Scouters who complete all phases of advanced leadership training, shown by beads on a thong."
  }
]
""")


def main() -> None:
    out_dir = Path(__file__).resolve().parents[1] / "data" / "awards"
    out_dir.mkdir(parents=True, exist_ok=True)
    for a in AWARDS:
        version = {
            "valid_from": None,
            "valid_to": None,
            "name": a["name"],
            "category": a["category"],
            "audience": a["audience"],
            "programs": a["programs"],
            "square_knot_no": a["square_knot_no"],
            "insignia_nos": a["insignia_nos"],
            "wear": a["wear"],
            "restricted": a["restricted"],
            "summary": a["summary"],
            "provenance": {
                "sources": [{"citation": SOURCE_CITATION}, {"url": AWARDS_URL}],
                "method": "llm_extraction",
                "verified_at": VERIFIED_AT,
                "confidence": 0.85,
                "notes": NOTES,
            },
        }
        doc = {"id": a["slug"], "kind": "award", "versions": [version], "notes": None}
        (out_dir / f"{a['slug']}.json").write_text(
            json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"awards: {len(AWARDS)} award entities written")


if __name__ == "__main__":
    main()
