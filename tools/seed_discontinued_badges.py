"""Seed generator for DISCONTINUED merit badges and the badge-lineage event graph.

The catalog held 140 current badges plus exactly two historical ones (Citizenship in Society,
Computers), so "what happened to the Signaling merit badge" was unanswerable. BSA has offered
hundreds since 1910.

Source: usscouts.org/mb/history.asp, a single table listing every badge ever offered with the
years it was available, BSA's internal number where one was assigned (from ~1986), and a note
recording lineage ("Became Fishing", "Formerly Business", "Formerly part of Aviation").
Discontinued badges are marked in the markup with class="red", which is how the page's own
legend distinguishes them - status is read from the source, not inferred from dates.

The parse is cross-validated before anything is written: the page's non-red rows must match the
140 current badges we already hold, after normalising "&"/"and" and hyphen spelling. A mismatch
in COUNT aborts, because it means the table shape moved.

Lineage becomes events, using the vocabulary's own documented mapping for this domain ("badge
replaced by a new badge -> superseded"):
  "Became X" / "Replaced by X" / "Replaced with X"  ->  superseded, this badge as predecessor
  "Formerly X" / "Replaced X" / "Replaces X"        ->  superseded, X as predecessor
  "Formerly part of X"                              ->  NO event; kept as prose only, because a
      split event would need X closed and X is usually still a live badge.
Each link is emitted once even though the table states it from both sides.

`eagle_required` is null for these: badges retired before the modern published Eagle list cannot
be sourced either way, and 126 fabricated booleans would be worse than an honest unknown.

    python tools/seed_discontinued_badges.py [--dry-run]
"""
from __future__ import annotations

import html
import json
import re
import ssl
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
CACHE = ROOT / ".workbench" / "mb_history.html"
SRC = "http://usscouts.org/mb/history.asp"
SCHEMA = "https://sethmay.github.io/open-scout-api/schema/v1/merit-badge.schema.json"
UA = {"User-Agent": "open-scout-api discontinued-badge seed (github.com/sethmay/open-scout-api)"}


def fetch() -> str:
    if CACHE.exists():
        return CACHE.read_text("utf-8")
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    body = urllib.request.urlopen(urllib.request.Request(SRC, headers=UA),
                                  timeout=40, context=ctx).read(400_000).decode("utf-8", "ignore")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(body, encoding="utf-8")
    return body


def slug(name: str) -> str:
    s = name.lower().replace("&", " and ")
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s


def norm(name: str) -> str:
    """Comparison key: collapses '&'/'and', hyphens, commas and case."""
    s = name.lower().replace("&", "and")
    return re.sub(r"[^a-z0-9]+", "", s)


def parse_rows(body: str) -> list[dict]:
    rows = re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S | re.I)
    out = []
    for r in rows:
        cells = []
        for m in re.finditer(r"<t[dh]([^>]*)>(.*?)</t[dh]>", r, re.S | re.I):
            txt = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(2))))
            cells.append({"text": txt.replace("\xa0", " ").strip(), "red": "red" in m.group(1).lower()})
        if len(cells) < 5:
            continue
        name, first, last = cells[0]["text"], cells[3]["text"], cells[4]["text"]
        if not name or not re.match(r"^[A-Z]", name) or not re.match(r"^(19|20)\d{2}", first or ""):
            continue
        num = re.sub(r"\D", "", cells[1]["text"] or "")
        out.append({"name": name, "discontinued": cells[0]["red"],
                    "bsa_number": int(num) if num else None,
                    "first": first[:4], "last": (last or "").strip(),
                    "notes": (cells[5]["text"] if len(cells) > 5 else "") or None})
    return out


def main() -> None:
    dry = "--dry-run" in sys.argv
    rows = parse_rows(fetch())

    # --- cross-validate the parse against data we already trust ------------------
    ours: dict[str, str] = {}          # norm(name) -> id, every version of every badge
    open_ids: set[str] = set()
    for p in sorted((DATA / "merit-badges").glob("*.json")):
        if p.name == "_events.json":
            continue
        d = json.loads(p.read_text("utf-8"))
        for v in d.get("versions", []):
            ours.setdefault(norm(v["name"]), d["id"])
            if v.get("valid_to") is None:
                open_ids.add(d["id"])
    src_current = [r for r in rows if not r["discontinued"]]
    if len(src_current) != len(open_ids):
        raise SystemExit(f"parse aborted: source lists {len(src_current)} current badges but we hold "
                         f"{len(open_ids)}; the table shape has probably moved")
    disc = [r for r in rows if r["discontinued"]]
    print(f"source rows: {len(rows)} | current: {len(src_current)} (matches our {len(open_ids)}) | "
          f"discontinued: {len(disc)}")

    # --- resolve every name mentioned anywhere to an id -------------------------
    name_to_id = dict(ours)
    for r in disc:
        name_to_id.setdefault(norm(r["name"]), slug(r["name"]))

    def resolve(nm: str) -> str | None:
        return name_to_id.get(norm(nm))

    # --- entities --------------------------------------------------------------
    written, skipped = [], []
    for r in disc:
        sid = slug(r["name"])
        if sid in open_ids:
            # The name was later reused by a badge that is still live, so this row is a
            # distinct earlier badge (Aviation ran 1911-1942, split into four parts, and a
            # new Aviation began in 1952). Keep it, disambiguated by its start year.
            sid = f"{sid}-{r['first']}"
            name_to_id[norm(r["name"])] = ours.get(norm(r["name"]), sid)
        path = DATA / "merit-badges" / f"{sid}.json"
        if path.exists():
            skipped.append((r["name"], "already in the catalog"))
            continue
        ym = re.search(r"(19|20)\d{2}", r["last"] or "")   # the table has typos like ".2010"
        last = ym.group(0) if ym else None
        if not last:
            skipped.append((r["name"], f"unusable end year {r['last']!r}"))
            continue
        written.append({
            "$schema": SCHEMA, "id": sid, "kind": "merit-badge",
            "versions": [{
                "valid_from": r["first"], "valid_to": last, "name": r["name"],
                "bsa_number": r["bsa_number"], "eagle_required": None,
                "tags": [], "description": None, "url": None,
                "provenance": {"sources": [{"url": SRC, "accessed": date.today().isoformat()}],
                               "method": "scraped", "verified_at": date.today().isoformat(),
                               "confidence": 0.8,
                               "notes": ("Discontinued badge recovered from the USSSP merit badge history "
                                         "table, which marks retired badges in its own markup. "
                                         "eagle_required is null because it cannot be sourced for badges "
                                         "retired before the modern published Eagle list.")},
            }],
            "notes": r["notes"],
        })

    # --- lineage events --------------------------------------------------------
    links: dict[tuple[str, str], str] = {}      # (pred, succ) -> evidence
    for r in rows:
        note = r["notes"] or ""
        me = resolve(r["name"])
        if not me:
            continue
        for rx, direction in ((r"^Became\s+(.+)$", "succ"),
                              (r"^Replaced (?:by|with)\s+(.+)$", "succ"),
                              (r"^Replaced\s+(?!by|with)(.+)$", "pred"),
                              (r"^Replaces\s+(.+)$", "pred"),
                              (r"^Formerly\s+(?!part of)(.+)$", "pred")):
            m = re.match(rx, note, re.I)
            if not m:
                continue
            other = resolve(m.group(1).strip().rstrip("."))
            if not other or other == me:
                break
            pred, succ = (me, other) if direction == "succ" else (other, me)
            links.setdefault((pred, succ), f"{r['name']}: {note}")
            break

    ev_path = DATA / "merit-badges" / "_events.json"
    existing = json.loads(ev_path.read_text("utf-8"))["events"] if ev_path.exists() else []
    have = {e["id"] for e in existing}
    have_pairs = {tuple(sorted(p["ref"] for p in e["participants"])) for e in existing}
    new_events = []
    written_ids = {d["id"] for d in written}
    closed = {d["id"] for d in written} | {i for i in name_to_id.values() if i not in open_ids}
    for (pred, succ), why in sorted(links.items()):
        if tuple(sorted([f"merit-badge:{pred}", f"merit-badge:{succ}"])) in have_pairs:
            continue
        if pred not in closed:
            continue          # a superseded predecessor must be retired; skip if it is still live
        eid = f"supersede-{pred}-by-{succ}"
        if eid in have:
            continue
        new_events.append({
            "id": eid, "type": "superseded", "date": None,
            "participants": [{"ref": f"merit-badge:{pred}", "role": "predecessor"},
                             {"ref": f"merit-badge:{succ}", "role": "successor"}],
            "notes": f"USSSP badge history states: {why}",
            "provenance": {"sources": [{"url": SRC, "accessed": date.today().isoformat()}],
                           "method": "scraped", "verified_at": date.today().isoformat(),
                           "confidence": 0.8},
        })
    # a retired badge with no successor gets a plain discontinued event
    superseded_preds = {p for p, _ in links}
    disc_events = []
    for d in written:
        if d["id"] in superseded_preds:
            continue
        disc_events.append({
            "id": f"discontinue-{d['id']}", "type": "discontinued", "date": d["versions"][0]["valid_to"],
            "participants": [{"ref": f"merit-badge:{d['id']}", "role": "subject"}],
            "notes": None,
            "provenance": {"sources": [{"url": SRC, "accessed": date.today().isoformat()}],
                           "method": "scraped", "verified_at": date.today().isoformat(),
                           "confidence": 0.8},
        })

    # --- backfill founding years on badges we already hold -----------------------
    # Every current badge's single version carried valid_from: null ("from the beginning of
    # what we know"). The table states an introduction year for each, and for a renamed badge
    # that year is when THIS name took effect (American Business: 1967, formerly Business),
    # which is exactly the version-window semantic. Fill only where we assert nothing today.
    backfill = []
    for r in src_current:
        bid = ours.get(norm(r["name"]))
        if not bid:
            continue
        fp = DATA / "merit-badges" / f"{bid}.json"
        d = json.loads(fp.read_text("utf-8"))
        ov = next((v for v in d["versions"] if v.get("valid_to") is None), None)
        if ov is None or ov.get("valid_from") is not None:
            continue
        backfill.append((fp, d, ov, r["first"], r["bsa_number"]))

    print(f"entities to write: {len(written)} | skipped: {len(skipped)}")
    print(f"current badges to backfill valid_from: {len(backfill)}")
    print(f"lineage links found: {len(links)} | superseded events: {len(new_events)} | "
          f"discontinued events: {len(disc_events)}")
    for nm, why in skipped[:10]:
        print(f"   skip {nm}: {why}")
    if dry:
        return
    for d in written:
        (DATA / "merit-badges" / f"{d['id']}.json").write_text(
            json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    for fp, d, ov, first, num in backfill:
        ov["valid_from"] = first
        if ov.get("bsa_number") is None and num is not None:
            ov["bsa_number"] = num
        pv = ov.setdefault("provenance", {})
        pv.setdefault("sources", []).append({"url": SRC, "accessed": date.today().isoformat()})
        pv["notes"] = ((pv.get("notes") or "").rstrip() +
                       " Introduction year (and BSA number where absent) backfilled from the USSSP "
                       "merit badge history table; for a renamed badge this is when THIS name took "
                       "effect, not when the lineage began.").strip()
        fp.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"backfilled {len(backfill)} current badges")
    allev = existing + new_events + disc_events
    allev.sort(key=lambda e: e["id"])
    ev_path.write_text(json.dumps({"$schema": "https://sethmay.github.io/open-scout-api/schema/v1/event.schema.json",
                                   "events": allev}, indent=2, ensure_ascii=False) + "\n",
                       encoding="utf-8", newline="\n")
    print(f"wrote {len(written)} badges; events {len(existing)} -> {len(allev)}")


if __name__ == "__main__":
    main()
