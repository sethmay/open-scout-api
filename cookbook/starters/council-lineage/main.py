"""My council merged -- what is it now? A lineage timeline for any council, live or defunct.

TRAP: looking a council up in `v1/current/councils.json`, getting nothing, and reporting "no
      such council". Roughly half of the published councils are historical, and their identity
      is not lost: it is spread across `versions` (each with `valid_from`/`valid_to`, either of
      which may be null) and `events` (`merged`, `absorbed`, `renamed`, `discontinued`), whose
      `participants[].ref` point at BOTH ends of the change. Two further traps ride along:
      almost every rename shows up only as a name change between consecutive `versions` -- one
      single council in the whole dataset has a `renamed` event -- and lineage facts are the
      least certain thing here, carrying `date: null` and `confidence` from 0.4 to 0.8. Printing
      "Choctaw Area merged into Mississippi Riverlands in 2026" is a fabricated date.
FIX:  read the entity document, build the timeline from versions AND events together, follow
      `role` in both directions (`predecessor`/`subject` end, `continuing`/`successor` survive),
      and print `date`, `method` and `confidence` as published -- `?` where the source has no
      date, rather than inventing one.

  python main.py mississippi-riverlands
  python main.py choctaw-area
  python main.py --selftest
"""

from __future__ import annotations

import argparse
import sys

from osa import CheckError, check, endpoint, get, items

DATASET = "council"  # refs are `council:<id>`; the same walk works for territories
ENDED = ("predecessor", "subject")  # roles whose council stops being itself
SURVIVED = ("continuing", "successor")  # roles that carry the area forward
CLIP = 44  # event notes are the dataset's own prose; clipped to keep the timeline readable

# The canned --selftest council: it has both a merger and a rename, and both are undated.
SELFTEST_COUNCIL = "mississippi-riverlands"


# --- fetching ----------------------------------------------------------------------------


class Councils:
    """The council index plus a per-process document cache, so a lineage walk is cheap."""

    def __init__(self) -> None:
        self.index = {c["id"]: c for c in items("v1/councils/index.json")}
        self.template = endpoint("v1/councils/{id}.json")
        self._docs: dict[str, dict] = {}

    def doc(self, cid: str) -> dict:
        if cid not in self._docs:
            self._docs[cid] = get(self.template.format(id=cid))
        return self._docs[cid]

    def label(self, cid: str) -> str:
        """A ref rendered for a human. Strict on purpose: an unresolvable ref is a dataset
        defect and should fail loudly rather than print a dangling id."""
        entry = self.index.get(cid)
        check(entry is not None, f"council:{cid} is referenced but not published")
        return f"{entry['name']}, {'current' if entry['current'] else 'defunct'}"

    def is_current(self, cid: str) -> bool:
        entry = self.index.get(cid)
        return bool(entry and entry["current"])


def ref_id(ref: str) -> str:
    """`council:choctaw-area` -> `choctaw-area`."""
    kind, _, cid = ref.partition(":")
    check(kind == DATASET, f"expected a {DATASET}: ref, got {ref!r}")
    return cid


# --- the timeline ------------------------------------------------------------------------


def in_force(versions: list[dict]) -> dict:
    """The version in force, i.e. `valid_to is None`. Falls back to the last version for a
    defunct council, which has no open-ended version by definition."""
    check(versions, "an entity document must publish at least one version")
    open_ended = [v for v in versions if v["valid_to"] is None]
    return open_ended[-1] if open_ended else versions[-1]


def entry(when, kind, detail, provenance, notes=None) -> dict:
    """One timeline row. `when` may be None: the dataset says so, and so do we."""
    note = " ".join((notes or "").split())
    return {
        "when": when,
        "kind": kind,
        "detail": detail,
        "method": provenance.get("method"),
        "confidence": provenance.get("confidence"),
        "notes": note[:CLIP] + ("..." if len(note) > CLIP else ""),
    }


def timeline(doc: dict, councils: Councils) -> list[dict]:
    """Versions and events merged into one ordered list.

    A rename is usually NOT an event: it is the name changing between two consecutive versions.
    Reading only `events` therefore loses nearly every rename in the dataset.
    """
    rows = []
    versions = doc["versions"]
    first = versions[0]
    rows.append(
        entry(
            first["valid_from"],
            "first record",
            f"as {first['name']}" + (f" (#{first['bsa_number']})" if first["bsa_number"] else ""),
            first["provenance"],
            first["provenance"].get("notes"),
        )
    )
    for previous, current in zip(versions, versions[1:]):
        if current["name"] != previous["name"]:
            rows.append(
                entry(
                    current["valid_from"],
                    "renamed",
                    f"{previous['name']} -> {current['name']}",
                    current["provenance"],
                    current["provenance"].get("notes"),
                )
            )
    last = versions[-1]
    if last["valid_to"] is not None:
        rows.append(
            entry(
                last["valid_to"],
                "record ends",
                f"{last['name']} last recorded (valid_to is a coarse bound)",
                last["provenance"],
            )
        )

    for event in doc["events"]:
        parts = " ".join(f"{p['role']}={ref_id(p['ref'])}" for p in event["participants"])
        rows.append(entry(event["date"], event["type"], parts, event["provenance"], event["notes"]))

    # Dated rows first, in date order (`YYYY` and `YYYY-MM-DD` both sort correctly as strings);
    # undated rows keep document order and are printed as their own section. Interleaving them
    # would invent a sequence the source does not claim.
    rows.sort(key=lambda r: (r["when"] is None, r["when"] or ""))
    return rows


def ordered(rows: list[dict]) -> bool:
    dated = [r["when"] for r in rows if r["when"]]
    return dated == sorted(dated)


# --- walking the lineage in both directions ----------------------------------------------


def successors(doc: dict) -> list[tuple[dict, str]]:
    """Events in which this council ended, paired with whoever carried its area forward.

    The same event document is published on every participant, so one fetch answers both
    directions -- no index scan and no reverse lookup table.
    """
    me = doc["id"]
    out = []
    for event in doc["events"]:
        mine = [p["role"] for p in event["participants"] if ref_id(p["ref"]) == me]
        if not any(role in ENDED for role in mine):
            continue
        for participant in event["participants"]:
            if participant["role"] in SURVIVED:
                out.append((event, ref_id(participant["ref"])))
    return out


def predecessors(doc: dict) -> list[tuple[dict, str]]:
    """Events in which this council survived, paired with the ids that ended in it."""
    me = doc["id"]
    out = []
    for event in doc["events"]:
        mine = [p["role"] for p in event["participants"] if ref_id(p["ref"]) == me]
        if not any(role in SURVIVED for role in mine):
            continue
        for participant in event["participants"]:
            if participant["role"] in ENDED and ref_id(participant["ref"]) != me:
                out.append((event, ref_id(participant["ref"])))
    return out


def forward(cid: str, councils: Councils) -> list[str]:
    """Who serves that area now: hop successor to successor until a current council or a dead
    end. Cycle-guarded, because a merger recorded from both sides can point back."""
    chain = [cid]
    while not councils.is_current(chain[-1]):
        nxt = successors(councils.doc(chain[-1]))
        if not nxt or nxt[0][1] in chain:
            break
        chain.append(nxt[0][1])
    return chain


def territory(doc: dict, councils: Councils) -> tuple[str, str]:
    """Resolve `territory:cst-NN` to the territory's name in force.

    Territories are versioned too: cst-16 was 'National Service Territory 16' before the 2024
    reorganisation, so the last version is the one to print -- not the first.
    """
    ref = in_force(doc["versions"])["territory"]
    via = doc["id"]
    if ref is None:
        # A defunct council often has no territory; the successor's is the honest answer.
        chain = forward(doc["id"], councils)
        if len(chain) > 1:
            via = chain[-1]
            ref = in_force(councils.doc(via)["versions"])["territory"]
    if ref is None:
        return "none recorded", via
    kind, _, tid = ref.partition(":")
    check(kind == "territory", f"expected a territory: ref, got {ref!r}")
    version = in_force(get(endpoint("v1/territories/{id}.json").format(id=tid))["versions"])
    return f"{ref} -> {version['name']} (in force from {version['valid_from']})", via


# --- reporting ---------------------------------------------------------------------------


def render(cid: str, councils: Councils) -> dict:
    doc = councils.doc(cid)
    rows = timeline(doc, councils)
    current = in_force(doc["versions"])
    chain = forward(cid, councils)
    came_from = predecessors(doc)
    place, via = territory(doc, councils)

    state = "current" if councils.is_current(cid) else "defunct"
    print(f"council         {cid} ({state})")
    label = "in force as" if state == "current" else "last recorded"
    number = f" #{current['bsa_number']}" if current["bsa_number"] else ""
    where = ", ".join(x for x in (current["hq_city"], current["hq_state"]) if x)
    print(f"{label:<15} {current['name']}{number}" + (f" -- {where}" if where else ""))
    print(f"territory       {place}" + ("" if via == cid else f"  (via {via})"))
    if doc["notes"]:
        print(f"notes           {' '.join(doc['notes'].split())}")

    print("timeline        dated rows first, in published order")
    undated = 0
    for row in rows:
        if row["when"] is None and not undated:
            print(f"  {'(undated)':<11}the source records no date; sequence unknown")
        undated += row["when"] is None
        print(f"  {row['when'] or '?':<11}{row['kind']:<14}{row['detail']}")
        trust = f"method={row['method']} conf={row['confidence']}"
        print(f"  {'':<11}{'':<14}{trust}" + (f"  {row['notes']}" if row["notes"] else ""))

    if len(chain) > 1:
        hops = " -> ".join(chain)
        print(f"serves now      {hops}  ({councils.label(chain[-1])})")
    elif state == "current":
        print("serves now      still its own council; nothing supersedes it")
    else:
        print("serves now      unknown: no event records a successor for this council")
    if came_from:
        for event, other in came_from:
            when = event["date"] or "?"
            print(f"absorbed        {other} ({councils.label(other)}) via {event['type']} {when}")
    else:
        print("absorbed        no predecessors recorded")

    soft = [r for r in rows if (r["confidence"] or 1) < 1]
    undated = [r for r in rows if r["when"] is None]
    print(
        f"certainty       {len(soft)} of {len(rows)} rows below confidence 1.0, "
        f"{len(undated)} undated -- inferred, not settled fact"
    )
    print()
    return {"doc": doc, "rows": rows, "chain": chain, "predecessors": came_from}


# --- selftest ----------------------------------------------------------------------------


def selftest(councils: Councils) -> int:
    """Walk a council with a real merger AND a real rename, then assert the walk's contracts."""
    report = render(SELFTEST_COUNCIL, councils)
    rows, doc = report["rows"], report["doc"]

    check(ordered(rows), "the timeline must be ordered by the dates the dataset publishes")
    check(rows, "a council document must yield at least one timeline row")

    kinds = {r["kind"] for r in rows}
    check(kinds & {"absorbed", "merged", "superseded"}, "this council must record a merger")
    check("renamed" in kinds, "this council must record a rename")

    # Referential integrity: every ref in every event resolves to a published council.
    refs = {ref_id(p["ref"]) for e in doc["events"] for p in e["participants"]}
    missing = sorted(r for r in refs if r not in councils.index)
    check(not missing, f"unpublished refs in {doc['id']} events: {missing}")
    check(refs - {doc["id"]}, "a merger must name a council other than the subject")

    # Uncertainty is surfaced, not smoothed over: these facts are inferred.
    for event in doc["events"]:
        provenance = event["provenance"]
        check(provenance.get("method"), f"event {event['id']} must publish a method")
        confidence = provenance.get("confidence")
        check(
            isinstance(confidence, (int, float)) and 0 < confidence <= 1,
            f"event {event['id']} must publish a confidence in (0, 1]",
        )
    check(
        any((r["confidence"] or 1) < 1 for r in rows),
        "lineage facts are inferred; at least one row must be below confidence 1.0",
    )
    check(any(r["when"] is None for r in rows), "an undated row must survive as undated")

    # Walking forward from a predecessor must land on a council that exists today.
    check(report["predecessors"], "this council must record at least one predecessor")
    for _, other in report["predecessors"]:
        chain = forward(other, councils)
        check(len(chain) > 1, f"{other} must resolve forward to a successor")
        check(councils.is_current(chain[-1]), f"{other} must resolve forward to a current council")
        check(chain[-1] == SELFTEST_COUNCIL, f"{other} must resolve forward to {SELFTEST_COUNCIL}")
        # And the walk is symmetric: the predecessor's own document carries the same event.
        back = {cid for _, cid in successors(councils.doc(other))}
        check(SELFTEST_COUNCIL in back, f"{other}'s document must name {SELFTEST_COUNCIL}")
        render(other, councils)

    check(
        forward(SELFTEST_COUNCIL, councils) == [SELFTEST_COUNCIL],
        "a current council must end the forward walk at itself",
    )
    place, _ = territory(doc, councils)
    check(place != "none recorded", "this council must resolve to a named territory")

    print(f"timeline        {len(rows)} rows, dated rows ordered, kinds: {' '.join(sorted(kinds))}")
    print(f"refs            {len(refs)} participant refs, all resolve in the council index")
    first_predecessor = report["predecessors"][0][1]
    print(f"forward         {' -> '.join(forward(first_predecessor, councils))}")
    print("certainty       method and confidence printed per row; undated rows stay undated")
    return 0


# --- cli ---------------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Council lineage: mergers, renames, successors.")
    ap.add_argument("council", nargs="?", help="council id, current or historical")
    ap.add_argument("--selftest", action="store_true", help="run the canned council and assert")
    ap.add_argument("--base", help="API root; also read from $OSA_BASE by the shared helper")
    args = ap.parse_args(argv)

    councils = Councils()
    if args.selftest:
        return selftest(councils)
    if not args.council:
        ap.error(f"a council id is required, e.g. {SELFTEST_COUNCIL}")
    if args.council not in councils.index:
        near = sorted(c for c in councils.index if args.council in c)[:5]
        hint = f"; did you mean {', '.join(near)}?" if near else ""
        ap.error(f"unknown council {args.council!r}{hint}")
    render(args.council, councils)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckError as exc:  # an invariant broke: fail loudly, and nonzero
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
