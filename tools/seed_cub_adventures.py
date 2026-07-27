"""Seed generator: Cub Scout adventures (entities + requirement-sets).

The 2024 Cub Scout program is built from *adventures*: a rank is earned by completing six
required adventures plus any two electives, and each adventure carries its own requirements.
Adventures are therefore entities in their own right — the Cub-side analogue of merit badges —
so requirement content lives once, on the adventure, and each rank's requirement-set holds
only the advancement structure (which adventures, in which group, how many to choose) with a
`ref` to each adventure.

Two modes:

  --extract <dir>   Parse saved scouting.org pages into the committed facts file
                    tools/cub_adventures.json, and rewrite the six Cub entries of
                    tools/program_rank_requirements.json to the ref-based structure.
                    <dir> holds `adventures/*.htm` (one page per adventure) and
                    `requirements/<Rank> Adventures _ Scouting America.htm` (six rank pages).
                    scouting.org is behind bot protection, so the pages are saved by hand;
                    this mode is the only step that needs them.

  (default)         Generate data/ from the facts file. Deterministic and reproducible
                    without the saved pages.

Output:
  data/adventures/<slug>.json                       one entity per adventure
  data/requirement-sets/adventure-<slug>-<year>.json  one edition per adventure that has
                                                    published requirements

Slugs come from each page's own `rel=canonical` URL, not from the name, so they match
scouting.org (e.g. "Pick My Path" -> `pick-my-path-lion`). Requirement-set ids are prefixed
`adventure-` because several adventures share a name with a merit badge (Swimming, First Aid,
Cycling, Fishing, Personal Fitness) and requirement-set ids are one flat namespace.

Requirement text is (c) Scouting America (text_rights), reproduced with attribution for
non-commercial use; see NOTICE.md.
"""

from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FACTS = ROOT / "tools" / "cub_adventures.json"
HIST_FACTS = ROOT / "tools" / "cub_adventures_history.json"
RANK_FACTS = ROOT / "tools" / "program_rank_requirements.json"
OUT_ADV = ROOT / "data" / "adventures"
OUT_RS = ROOT / "data" / "requirement-sets"
TODAY = "2026-07-27"
YEAR = "2024"
TEXT_RIGHTS = ("Requirement text \u00a9 Scouting America, reproduced with attribution for "
               "non-commercial Scouting use; NOT licensed under this dataset's CC BY-NC-SA. "
               "See NOTICE.md.")
PROGRAM = "cub_scouts"

# rank slug -> the saved rank page's display name
RANKS = {"lion": "Lion", "tiger": "Tiger", "wolf": "Wolf", "bear": "Bear",
         "webelos": "Webelos", "arrow-of-light": "Arrow Of Light"}
# the page's own group headings -> our category codes (data/vocab/adventure-categories.json)
CATEGORY = {"Required Adventures": "required",
            "Elective Adventures": "elective",
            "Special Elective Adventures": "special_elective"}
# the rank rule text: "six required Adventures and any two elective Adventures"
CHOOSE = {"required": None, "elective": 2, "special_elective": None}
# The six requirement AREAS a rank's required adventures fill, one each. Five come straight from
# the CMS taxonomy on each adventure card (`cs-adv-topic-<slug>`); the sixth, Bobcat's, is a
# hand-built callout on every rank page and is read from its label. Electives carry no area.
AREA_FROM_TOPIC = str.maketrans({"-": "_"})       # cs-adv-topic-personal-fitness -> personal_fitness


def _text(frag: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", frag))).strip()


def _strip_scripts(b: str) -> str:
    return re.sub(r"<script.*?</script>|<style.*?</style>", " ", b, flags=re.S | re.I)


def _slug_from_name(name: str) -> str:
    s = unicodedata.normalize("NFKD", name.replace("\u2019", "").replace("\u2018", ""))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", s.lower())).strip("-")


def _slug_from_url(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).replace("\u2019", "'").replace("\u2018", "'")
    return re.sub(r"\s+", " ", s.lower()).strip()


# --------------------------------------------------------------------------- extract

def _parse_adventure_page(path: Path) -> dict:
    """name, canonical url and the requirement list from one adventure page.

    The page repeats `Requirement N` twice: once as the requirement list under
    'Complete the following requirements', then again as activity-resource sections further
    down. Only the first block is requirements, so parsing stops at the next <h2>.
    """
    body = _strip_scripts(path.read_text("utf-8", errors="ignore"))
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S | re.I)
    can = re.search(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', body, re.I)
    if not h1 or not can:
        raise SystemExit(f"{path.name}: no <h1> or rel=canonical")
    lower = body.lower()
    i = lower.find("complete the following requirements")
    if i < 0:
        raise SystemExit(f"{path.name}: no 'Complete the following requirements' heading")
    j = lower.find("<h2", lower.find("</h2>", i))
    seg = body[i:j if j > 0 else len(body)]
    reqs = [{"number": n, "text": _text(frag)}
            for n, frag in re.findall(
                r"<h3[^>]*>\s*Requirement\s+([0-9]+[a-z]?)\s*</h3>(.*?)(?=<h3|\Z)", seg, re.S | re.I)]
    if not reqs:
        raise SystemExit(f"{path.name}: requirement block parsed to zero requirements")
    return {"name": _text(h1.group(1)), "url": can.group(1), "requirements": reqs}


def _parse_rank_page(path: Path) -> tuple[list[dict], dict[str, str], dict[str, str], str]:
    """(groups, url_by_name, area_by_name, bobcat_area) for one rank page.

    Groups are the <h3> 'Required / Elective / Special Elective Adventures' headings; the
    adventures in each are the <h2>s that follow. Bobcat is not in any group — it is linked
    separately ('View Wolf Bobcat') — but the rank rule counts *six* required adventures
    against five listed, so Bobcat is the sixth and is prepended to the required group.

    Areas come from the CMS, not from reading the layout: every required adventure is rendered as
    a loop-item whose class list carries `cs-adv-rank-<rank> cs-adv-type-required
    cs-adv-topic-<area>`. Pairing an adventure with the area label printed next to it would be
    guesswork about card order (Bear prints its areas in a different order than Wolf); the class on
    the card the heading lives inside is authoritative. Electives carry no topic class at all.
    """
    body = _strip_scripts(path.read_text("utf-8", errors="ignore"))
    url_by_name: dict[str, str] = {}
    for u, a in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', body, re.S | re.I):
        if "/cub-scout-adventures/" in u:
            url_by_name.setdefault(_norm(_text(a)), u)
    groups: list[dict] = []
    skip = {"resources", "info", "legal", "connect with us"}
    for m in re.finditer(r"<h([23])[^>]*>(.*?)</h\1>", body, re.S | re.I):
        label = _text(m.group(2))
        if m.group(1) == "3" and label in CATEGORY:
            groups.append({"group": label, "names": []})
        elif m.group(1) == "2" and groups and label and _norm(label) not in skip:
            groups[-1]["names"].append(label)
    bobcat = next((u for n, u in url_by_name.items() if "bobcat" in n), None)
    if not bobcat:
        raise SystemExit(f"{path.name}: no Bobcat link")

    # walk cards and headings in document order; a heading belongs to the card it sits inside
    marks: list[tuple[int, str, str]] = []
    for m in re.finditer(r'<div[^>]*class="([^"]*e-loop-item[^"]*)"', body, re.I):
        marks.append((m.start(), "card", m.group(1)))
    for m in re.finditer(r'<h2[^>]*>\s*<a[^>]+href="[^"]*cub-scout-adventures[^"]*"[^>]*>(.*?)</a>\s*</h2>',
                         body, re.S | re.I):
        marks.append((m.start(), "name", _text(m.group(1))))
    marks.sort()
    area_by_name: dict[str, str] = {}
    card = ""
    for _, kind, val in marks:
        if kind == "card":
            card = val
        else:
            topic = re.search(r"cs-adv-topic-([a-z0-9-]+)", card)
            if topic:
                area_by_name[_norm(val)] = topic.group(1).translate(AREA_FROM_TOPIC)

    # Bobcat's area is the one the CMS does not tag: a plain <p> label in its hand-built callout.
    inner = body[body.lower().find("<body"):]
    lab = next((_text(m.group(1)) for m in re.finditer(r"<p>([^<>]{3,40})</p>", inner)
                if "leadership" in m.group(1).lower()), None)
    if not lab:
        raise SystemExit(f"{path.name}: no Bobcat area label (expected a <p> naming its area)")
    bobcat_area = re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", lab.lower())).strip("_")
    return groups, {**url_by_name, "__bobcat__": bobcat}, area_by_name, bobcat_area


def extract(src: Path) -> None:
    pages = {}
    for p in sorted((src / "adventures").glob("*.htm")):
        info = _parse_adventure_page(p)
        pages[_norm(info["name"])] = info
    print(f"parsed {len(pages)} adventure pages")

    adv: dict[str, dict] = {}          # slug -> record
    rank_structure: dict[str, list] = {}
    for rank, disp in RANKS.items():
        groups, urls, area_by_name, bobcat_area = _parse_rank_page(
            src / "requirements" / f"{disp} Adventures _ Scouting America.htm")
        # A rank page's hrefs can redirect (Arrow of Light links `bobcat-arrow-of-light`,
        # whose page is canonically `bobcat-aol`), so a saved page's own canonical URL always
        # wins; the href is only a fallback for adventures with no page.
        bobcat_page = pages.get(_norm(f"Bobcat {disp}"))
        if bobcat_page is None:
            raise SystemExit(f"{rank}: no saved page named 'Bobcat {disp}'")
        bobcat_url = bobcat_page["url"]
        bobcat_slug = _slug_from_url(bobcat_url)
        out_groups = []
        for g in groups:
            cat = CATEGORY[g["group"]]
            slugs = []
            if cat == "required":                       # Bobcat is the sixth required adventure
                slugs.append(bobcat_slug)
                _record(adv, bobcat_slug, bobcat_page["name"], bobcat_url, rank, cat,
                        bobcat_page["requirements"], bobcat_area)
            for name in g["names"]:
                page = pages.get(_norm(name))
                url = (page or {}).get("url") or urls.get(_norm(name))
                slug = _slug_from_url(url) if url else _slug_from_name(name)
                slugs.append(slug)
                _record(adv, slug, (page or {}).get("name", name), url, rank, cat,
                        (page or {}).get("requirements", []), area_by_name.get(_norm(name)))
            out_groups.append({"group": g["group"], "category": cat,
                               "choose": CHOOSE[cat], "slugs": slugs})
        rank_structure[rank] = out_groups

    # Every rank must fill all six areas exactly once. This is the check that would have caught the
    # original Arrow of Light error: its adventures are *named* "Personal Fitness" and "Citizenship",
    # identical to two area labels, so a parser reading labels as adventures produced seven required
    # entries and nobody noticed. Coverage is now arithmetic, not eyeballing.
    areas = sorted({r["area"] for r in adv.values() if r["area"]})
    for rank in RANKS:
        got = sorted(r["area"] for r in adv.values() if r["area"] and rank in r["ranks"])
        if got != areas:
            raise SystemExit(f"{rank}: required adventures fill {got}, expected each of {areas} once")
    if len(areas) != 6:
        raise SystemExit(f"expected 6 requirement areas, found {len(areas)}: {areas}")

    unsourced = sorted(s for s, r in adv.items() if not r["requirements"])
    facts = {
        "note": ("Cub Scout adventures for the 2024 program: identity, rank/category/area placement "
                 "and requirement text, parsed from saved scouting.org pages (the site is behind bot "
                 "protection). Slugs are the pages' own canonical slugs. Areas come from each card's "
                 "CMS taxonomy class, not from the printed layout. Requirement text is "
                 "verbatim (c) Scouting America; see NOTICE.md."),
        "accessed": TODAY,
        "effective_from": YEAR,
        "areas": areas,
        "unsourced": unsourced,
        "rank_structure": rank_structure,
        "adventures": [adv[s] for s in sorted(adv)],
    }
    FACTS.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n",
                     encoding="utf-8", newline="\n")
    print(f"wrote {FACTS.relative_to(ROOT).as_posix()}: {len(adv)} adventures, "
          f"{sum(len(r['requirements']) for r in adv.values())} requirement nodes, "
          f"{len(unsourced)} without published requirements ({', '.join(unsourced)})")
    _patch_rank_facts(rank_structure, adv)


def _record(adv: dict, slug: str, name: str, url: str | None, rank: str, cat: str,
            reqs: list[dict], area: str | None) -> None:
    r = adv.setdefault(slug, {"slug": slug, "name": name, "url": url, "ranks": [],
                              "category": cat, "area": area, "requirements": reqs})
    if rank not in r["ranks"]:
        r["ranks"].append(rank)
    if r["category"] != cat:
        raise SystemExit(f"{slug}: category differs across ranks ({r['category']} vs {cat}); "
                         f"category would have to move onto the rank edge")
    if r.get("area") != area:
        raise SystemExit(f"{slug}: area differs across ranks ({r.get('area')} vs {area}); "
                         f"area would have to move onto the rank edge")
    if (cat == "required") != (area is not None):
        raise SystemExit(f"{slug}: category={cat} but area={area!r}; every required adventure fills "
                         f"exactly one area and no elective fills any")
    if reqs and not r["requirements"]:
        r["requirements"] = reqs


def _patch_rank_facts(rank_structure: dict, adv: dict) -> None:
    """Rewrite the six Cub rank requirement trees to the ref-based structure.

    Before: two groups, with Bobcat's requirements inlined (and, in Arrow of Light, three of the
    page's *area* labels captured as if they were adventures). After: the two groups the rank
    rule actually states -- "complete six required Adventures and any two elective Adventures" --
    with each adventure a leaf carrying a `ref` to its entity. Requirement content is no longer
    duplicated here; it lives on the adventure, exactly as a rank's merit-badge requirements live
    on the badge.

    The page splits electives again into "Elective Adventures" and "Special Elective Adventures"
    (the shooting sports, "only ... at approved events with qualified instructors"). That split is
    a property of the adventure, not a third rank requirement, and it is carried by
    `adventure.category`. Keeping it as a peer group here would have meant `choose: null` on it --
    which this schema reads as "all children required" -- i.e. asserting every Cub must earn BB
    Guns to rank up. So the elective pool is one group: the two electives the rank needs may come
    from any of them.
    """
    facts = json.loads(RANK_FACTS.read_text("utf-8"))
    for rank, groups in rank_structure.items():
        pool: dict[str, list[str]] = {"required": [], "elective": []}
        for g in groups:
            key = "required" if g["category"] == "required" else "elective"
            pool[key].extend(s for s in g["slugs"] if s not in pool[key])
        reqs = []
        for gi, (key, label) in enumerate((("required", "Required Adventures"),
                                           ("elective", "Elective Adventures")), start=1):
            node = {"number": str(gi), "text": label, "choose": CHOOSE[key], "children": []}
            for ai, slug in enumerate(pool[key], start=1):
                node["children"].append({"number": str(ai), "text": adv[slug]["name"],
                                         "ref": f"adventure:{slug}", "choose": None,
                                         "children": []})
            reqs.append(node)
        facts[rank]["requirements"] = reqs
    RANK_FACTS.write_text(json.dumps(facts, indent=1, ensure_ascii=False) + "\n",
                          encoding="utf-8", newline="\n")
    print(f"patched {RANK_FACTS.relative_to(ROOT).as_posix()}: {len(rank_structure)} Cub rank trees "
          f"rewritten as adventure refs")


# --------------------------------------------------------------------------- generate

def _hist_version(rec: dict, ed_from: str, ed_to: str, accessed: str, page_url: str) -> dict:
    """One pre-2024 attribute snapshot. `area` is null: the six requirement areas are a 2024
    construct, and `url` is null because scouting.org no longer serves these pages — the source
    lives in provenance."""
    return {
        "valid_from": ed_from, "valid_to": ed_to,
        "name": rec["name"], "program": PROGRAM,
        "ranks": [f"rank:{r}" for r in rec["ranks"]],
        "category": rec["category"], "area": None, "url": None,
        "provenance": {
            "sources": [{"url": page_url, "accessed": accessed}],
            "method": "scraped", "verified_at": accessed, "confidence": 0.8,
            "notes": ("Pre-2024 Cub program, via the U.S. Scouting Service Project archive "
                      "(usscouts.org), which is unaffiliated with Scouting America."),
        },
    }


def _attrs(v: dict) -> tuple:
    """The attributes a version window exists to record a change in."""
    return (v["name"], v["category"], tuple(v["ranks"]), v.get("area"))


def generate() -> None:
    facts = json.loads(FACTS.read_text("utf-8"))
    hist = json.loads(HIST_FACTS.read_text("utf-8")) if HIST_FACTS.exists() else None
    OUT_ADV.mkdir(parents=True, exist_ok=True)
    OUT_RS.mkdir(parents=True, exist_ok=True)
    year = facts["effective_from"]

    # index the pre-2024 line-up by the 2024 entity it belongs to (continues/renamed), and keep
    # the retired ones aside — they become entities of their own with closed windows.
    hist_for: dict[str, dict] = {}
    hist_retired: list[dict] = []
    if hist:
        for rec in hist["adventures"]:
            d = rec["disposition"]
            if d["kind"] in ("continues", "renamed"):
                hist_for[d["id"]] = rec
            else:
                hist_retired.append(rec)

    entities: list[dict] = []
    docs: list[dict] = []

    # A rule that just says "do all of these" adds nothing over the list itself, so it collapses
    # to null; anything that narrows the list is published verbatim in `completion_rule`.
    ALL_REQUIRED = re.compile(r"^complete\s+(?:all\s+of\s+)?the\s+following(?:\s+requirements?)?\.?$", re.I)

    def rs_docs(slug: str, name: str, rec: dict, accessed: str) -> list[dict]:
        """One requirement-set per pre-2024 edition, chained newest-supersedes-oldest."""
        out = []
        prev = None
        for ed in rec["editions"]:
            eff = ed["effective_from"]
            rid = f"adventure-{slug}-{eff[:4]}"
            url = hist["sources"][ed["source_page"]]["url"]
            rule = (ed["rule"] or "").strip()
            out.append({
                "id": rid, "kind": "requirement-set",
                "subject": f"adventure:{slug}",
                "effective_from": eff, "effective_to": ed["effective_to"],
                "supersedes": f"requirement-set:{prev}" if prev else None,
                "source_document": {
                    "title": f"{rec['name']} \u2014 Cub Scout Adventure requirements "
                             f"(pre-2024 program, USSSP archive)",
                    "url": url, "year": int(eff[:4])},
                "includes_official_text": True,
                "text_rights": TEXT_RIGHTS,
                "completion_rule": None if (not rule or ALL_REQUIRED.match(rule)) else rule,
                "requirements": ed["requirements"],
                "provenance": {
                    "sources": [{"url": url, "accessed": accessed}],
                    "method": "scraped", "verified_at": accessed, "confidence": 0.8,
                    "notes": "Requirement text verbatim from the USSSP archive of the pre-2024 program.",
                },
                "notes": ed.get("retired_note"),
            })
            prev = rid
        return out

    # ---- the 2024 line-up, with any pre-2024 history folded in
    for a in facts["adventures"]:
        prov = {
            "sources": [{"url": a["url"] or "https://www.scouting.org/programs/cub-scouts/adventures/",
                         "accessed": facts["accessed"]}],
            "method": "scraped", "verified_at": facts["accessed"], "confidence": 0.9,
            "notes": ("Name, rank placement and category from the official rank adventure pages."
                      if a["requirements"] else
                      "Listed on the official rank pages; requirements are not published online "
                      "(completed only at approved events with qualified instructors)."),
        }
        current = {
            "valid_from": year, "valid_to": None,
            "name": a["name"], "program": PROGRAM,
            "ranks": [f"rank:{r}" for r in a["ranks"]],
            "category": a["category"], "area": a.get("area"), "url": a["url"],
            "provenance": prov,
        }
        versions = [current]
        rec = hist_for.get(a["slug"])
        if rec:
            first = rec["editions"][0]
            page_url = hist["sources"][first["source_page"]]["url"]
            old = _hist_version(rec, first["effective_from"], year, hist["accessed"], page_url)
            # A version window exists to record an ATTRIBUTE change. Where nothing changed but the
            # requirements, opening a second window would assert a change that never happened, so
            # the single window simply starts when the adventure did; the requirement editions
            # carry the revision history.
            if _attrs(old) == _attrs(current):
                current["valid_from"] = first["effective_from"]
            else:
                versions = [old, current]
            docs += rs_docs(a["slug"], a["name"], rec, hist["accessed"])
        entities.append({"id": a["slug"], "kind": "adventure", "versions": versions, "notes": None})
        if a["requirements"]:
            docs.append({
                "id": f"adventure-{a['slug']}-{year}", "kind": "requirement-set",
                "subject": f"adventure:{a['slug']}",
                "effective_from": year, "effective_to": None,
                "supersedes": (f"requirement-set:adventure-{a['slug']}-"
                               f"{rec['editions'][-1]['effective_from'][:4]}") if rec else None,
                "source_document": {"title": f"{a['name']} \u2014 Scouting America (Cub Scout Adventures)",
                                    "url": a["url"], "year": int(year)},
                "includes_official_text": True,
                "text_rights": TEXT_RIGHTS,
                "requirements": [{"number": r["number"], "text": r["text"]} for r in a["requirements"]],
                "provenance": {
                    "sources": [{"url": a["url"], "accessed": facts["accessed"]}],
                    "method": "scraped", "verified_at": facts["accessed"], "confidence": 0.9,
                    "notes": "Requirement text verbatim from the adventure's official page.",
                },
                "notes": None,
            })

    # ---- adventures the 2024 program dropped: identity persists, every window closed
    events = []
    for rec in hist_retired:
        slug = _slug_from_name(rec["name"])
        vers = []
        for ed in rec["editions"]:
            page_url = hist["sources"][ed["source_page"]]["url"]
            vers.append(_hist_version(rec, ed["effective_from"], ed["effective_to"],
                                      hist["accessed"], page_url))
        # collapse windows that record no attribute change (the usual case: only requirements moved)
        merged = [vers[0]]
        for v in vers[1:]:
            if _attrs(v) == _attrs(merged[-1]):
                merged[-1]["valid_to"] = v["valid_to"]
            else:
                merged.append(v)
        entities.append({"id": slug, "kind": "adventure", "versions": merged, "notes": None})
        docs += rs_docs(slug, rec["name"], rec, hist["accessed"])
        d = rec["disposition"]
        ev_prov = {"sources": [{"url": hist["sources"][rec["editions"][-1]["source_page"]]["url"],
                                "accessed": hist["accessed"]}],
                   "method": "scraped", "verified_at": hist["accessed"], "confidence": 0.8}
        if d["kind"] == "superseded":
            events.append({"id": f"supersede-{slug}-by-{d['by']}", "type": "superseded",
                           "date": rec["retired_on"],
                           "participants": [{"ref": f"adventure:{slug}", "role": "predecessor"},
                                            {"ref": f"adventure:{d['by']}", "role": "successor"}],
                           "notes": (f"The 2024 Cub program renamed this adventure to "
                                     f"{d['by_name']!r}."),
                           "provenance": ev_prov})
        else:
            events.append({"id": f"discontinue-{slug}", "type": "discontinued",
                           "date": rec["retired_on"],
                           "participants": [{"ref": f"adventure:{slug}", "role": "subject"}],
                           "notes": rec["editions"][-1].get("retired_note"),
                           "provenance": ev_prov})

    for e in entities:
        (OUT_ADV / f"{e['id']}.json").write_text(
            json.dumps(e, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for d in docs:
        (OUT_RS / f"{d['id']}.json").write_text(
            json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    if events:
        (OUT_ADV / "_events.json").write_text(
            json.dumps({"events": sorted(events, key=lambda e: e["id"])}, indent=2,
                       ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"adventures: {len(entities)} entities ({len(hist_retired)} retired), "
          f"{len(docs)} requirement-sets, {len(events)} lifecycle events")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "--extract":
        if len(sys.argv) < 3:
            raise SystemExit("usage: seed_cub_adventures.py --extract <dir with adventures/ and requirements/>")
        extract(Path(sys.argv[2]))
    generate()


if __name__ == "__main__":
    main()
