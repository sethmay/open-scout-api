"""What does this Scout still need? Progress toward the next rank, from the requirement trees.

TRAP: reading Eagle requirement 3 as "21 badges, 18 of them required", and testing a Scout's
      positions of responsibility against the `position:` entity. Both produce a confident
      wrong answer. Requirement 3 is a 14-slot graph: three of its children carry `choose: 1`,
      so 14 slots span 18 distinct badge refs, and neither number is the 21 cumulative badges.
      Position acceptance is asymmetric per rank -- Bugler appears in Star's and Life's trees
      but not Eagle's, and only Star and Life accept a Scoutmaster-approved project in place
      of a position -- so acceptance lives on the rank, never on the position.
FIX:  resolve the requirement set whose `effective_to` is null for each rank, then walk it.
      Treat a node with `choose: 1` as ONE slot satisfied by any single child. Read the
      accepted `position:` refs and `tenure_months` off that rank's own leadership
      requirement, which is numbered 5 for Star and Life but 4 for Eagle.

Requirement text is (c) Scouting America and is NOT under this dataset's license, so this tool
never reads it: `narrow()` rebuilds every requirement node without a `text` field at the fetch
edge, and the document's own text_rights string is printed as a footer.

  python main.py --rank first-class --badges camping,cooking --positions patrol-leader:6
  python main.py --selftest
"""

from __future__ import annotations

import argparse
import sys

from osa import CheckError, check, endpoint, get, items

PROGRAM = "scouts_bsa"  # this CLI reports on the Scouts BSA ladder

# The internal requirement-node shape: every field this tool reads, and deliberately NOT `text`.
# A shape that cannot carry (c) Scouting America prose beats a rule about not printing it; see
# cookbook/ts/src/recipes/eagle-slots.test.ts, which narrows the same tree the same way.
NODE_FIELDS = ("number", "ref", "choose", "tenure_months", "badge_count")

# The canned --selftest scenario: a First Class Scout part-way through, holding only Bugler.
SELFTEST_RANK = "first-class"
SELFTEST_BADGES = (
    "camping",
    "citizenship-in-the-community",
    "communication",
    "cooking",
    "first-aid",
    "personal-fitness",
    "swimming",
)
SELFTEST_POSITIONS = {"bugler": 8}


# --- resolving the trees -----------------------------------------------------------------


def ladder() -> list[dict]:
    """The Scouts BSA ranks in advancement order.

    `order` is an ordinal *within a program*, so other programs must be filtered out before
    sorting: Sea Scout `able` is also order 3.
    """
    ranks = sorted(
        (r for r in items("v1/current/ranks.json") if r["program"] == PROGRAM),
        key=lambda r: r["order"],
    )
    check(
        [r["order"] for r in ranks] == list(range(1, len(ranks) + 1)),
        f"{PROGRAM} rank orders must form a complete 1..N ladder",
    )
    return ranks


def in_force_id(rank_id: str, index: list[dict]) -> str:
    """The requirement set in force for a rank: `effective_to is None`, not the newest id.

    Pinning the literal `star-2024` is the same bug as pinning a hostname -- a 2027 revision
    would leave this tool quietly scoring a Scout against withdrawn requirements.
    """
    live = [
        r["id"]
        for r in index
        if r["subject"] == f"rank:{rank_id}" and r["effective_to"] is None
    ]
    check(len(live) == 1, f"rank:{rank_id} must have exactly one in-force requirement set")
    return live[0]


def narrow(node: dict) -> dict:
    """A requirement node reduced to NODE_FIELDS, recursively. Applied once where the document
    is fetched, so nothing downstream has a `text` field to reach for by accident."""
    out = {k: node[k] for k in NODE_FIELDS if k in node}
    if node.get("children"):
        out["children"] = [narrow(c) for c in node["children"]]
    return out


def walk(node: dict):
    """Every node of a requirement subtree, parents before children."""
    yield node
    for child in node.get("children") or []:
        yield from walk(child)


def ref_ids(node: dict, prefix: str) -> set[str]:
    """Every `<prefix>:<id>` ref anywhere beneath (and on) a node, as bare ids."""
    return {
        n["ref"].split(":", 1)[1]
        for n in walk(node)
        if (n.get("ref") or "").startswith(prefix)
    }


def badge_requirement(doc: dict) -> dict:
    """The requirement carrying `badge_count` -- found by shape, since it is 3 for every rank
    today but the number is not a contract."""
    found = [r for r in doc["requirements"] if r.get("badge_count")]
    check(len(found) == 1, f"{doc['id']} must carry exactly one badge_count requirement")
    return found[0]


def badge_slots(req: dict) -> list[tuple[str, bool, list[str]]]:
    """The children of the badge requirement are SLOTS, not badges.

    A child carrying `choose: 1` is ONE slot that any one of its children satisfies. That is
    the whole reason Eagle's 14 slots span 18 distinct badge refs.
    """
    slots = []
    for child in req.get("children") or []:
        options = sorted(ref_ids(child, "merit-badge:"))
        check(options, f"slot {child['number']} must offer at least one badge ref")
        check(
            not child.get("choose") or len(options) > 1,
            f"slot {child['number']} declares choose but offers one option",
        )
        slots.append((child["number"], bool(child.get("choose")), options))
    return slots


def slot_state(slots: list[tuple[str, bool, list[str]]], badges: set[str]) -> tuple[list, list]:
    """Split slots into filled and open. A choose-1 slot is filled by ANY of its options, so
    matching badges against slots is not the same as counting badges."""
    filled = [(n, o) for n, _, o in slots if badges & set(o)]
    return filled, [(n, c, o) for n, c, o in slots if not badges & set(o)]


def leadership(doc: dict) -> dict:
    """The rank's own leadership requirement, located by structure rather than by number.

    It is `5` under Star and Life and `4` under Eagle, so the number cannot be hardcoded.
    """
    found = [r for r in doc["requirements"] if ref_ids(r, "position:")]
    check(len(found) == 1, f"{doc['id']} must carry exactly one requirement with position refs")
    return found[0]


def alternatives(req: dict) -> list[str]:
    """The NUMBERS of the leadership requirement's non-position leaves: the per-rank escape
    hatches. Star and Life publish two, Eagle one -- that difference IS the asymmetry.

    The number is the whole load-bearing datum: met() never scores an alternative, because
    every one of them needs a human to judge it. The wording stays unread (see narrow()).
    """
    return [
        node["number"]
        for node in walk(req)
        if node is not req and not node.get("children") and not node.get("ref")
    ]


def leadership_status(req: dict, held: dict[str, int]) -> dict:
    """Does a held position satisfy THIS rank's leadership requirement?

    Two traps at once. The accepted set is per-rank (Bugler is simply absent from Eagle's
    tree), and `tenure_months` hangs off the requirement, so months served must be measured
    against the rank being attempted -- not against the position, which knows nothing of it.
    """
    accepted = ref_ids(req, "position:")
    months = req.get("tenure_months")
    check(isinstance(months, int), f"requirement {req['number']} must publish tenure_months")
    return {
        "number": req["number"],
        "accepted": accepted,
        "months": months,
        "qualifying": sorted(p for p, m in held.items() if p in accepted and m >= months),
        "short": sorted(p for p, m in held.items() if p in accepted and m < months),
        "rejected": sorted(p for p in held if p not in accepted),
        "alternatives": alternatives(req),
    }


def met(status: dict) -> bool:
    """A position satisfies the requirement outright; the non-position alternatives need a
    human (a Scoutmaster approval, a Lone Scout situation), so they are reported, not scored."""
    return bool(status["qualifying"])


# --- reference data ---------------------------------------------------------------------


class Reference:
    """Everything fetched once: the ladder, the requirement-set index, badges, positions."""

    def __init__(self) -> None:
        self.ranks = ladder()
        self.by_id = {r["id"]: r for r in self.ranks}
        self.sets = items("v1/requirement-sets/index.json")
        self.badges = {b["id"]: b for b in items("v1/merit-badges/index.json")}
        self.positions = {p["id"]: p for p in items("v1/current/positions.json")}
        # `eagle_required` is tri-state: null means UNKNOWN on a historical badge, not false.
        self.flagged = {i for i, b in self.badges.items() if b["eagle_required"] is True}
        self.unknown = {i for i, b in self.badges.items() if b["eagle_required"] is None}
        self._docs: dict[str, dict] = {}

    def doc(self, rank_id: str) -> dict:
        """The in-force document, narrowed: the requirement tree arrives without `text`."""
        if rank_id not in self._docs:
            template = endpoint("v1/requirement-sets/{id}.json")
            raw = get(template.format(id=in_force_id(rank_id, self.sets)))
            self._docs[rank_id] = raw | {"requirements": [narrow(r) for r in raw["requirements"]]}
        return self._docs[rank_id]

    def remaining(self, current_rank: str) -> list[dict]:
        """The ranks above the Scout's current one, nearest first."""
        order = self.by_id[current_rank]["order"]
        return [r for r in self.ranks if r["order"] > order]


# --- reporting ---------------------------------------------------------------------------


def render(ref: Reference, rank: dict, badges: set[str], held: dict[str, int], label: str) -> dict:
    """One rank's report. Returns the computed slots/status so --selftest can assert on them."""
    doc = ref.doc(rank["id"])
    bc_req = badge_requirement(doc)
    counts = bc_req["badge_count"]
    slots = badge_slots(bc_req)
    status = leadership_status(leadership(doc), held)

    print(f"{label:<15} {rank['name']} -- {doc['id']}, in force from {doc['effective_from']}")

    cumulative_left = max(0, counts["cumulative"] - len(badges))
    print(
        f"  req {bc_req['number']:<10} {counts['cumulative']} cumulative badges: holding "
        f"{len(badges)}, {cumulative_left} to go"
    )
    if (from_flagged := counts.get("from_eagle_required")) is not None:
        have = len(badges & ref.flagged)
        print(
            f"{'':<16} {from_flagged} from the {len(ref.flagged)}-badge eagle_required list: "
            f"holding {have}, {max(0, from_flagged - have)} to go"
        )
    print(f"{'':<16} earn {counts['earn']} counts badges since the previous rank (needs dates)")

    filled, still_open = slot_state(slots, badges)
    if slots:
        either = [n for n, choose, _ in slots if choose]
        distinct = {b for _, _, o in slots for b in o}
        print(
            f"{'':<16} {len(slots)} slots ({len(slots) - len(either)} fixed + {len(either)} "
            f"choose-1: {' '.join(either)}) spanning {len(distinct)} distinct badge refs"
        )
        print(
            f"{'':<16} {len(slots)} slots != {len(distinct)} badges != "
            f"{counts['cumulative']} cumulative: three separate numbers"
        )
        print(f"{'':<16} filled {len(filled)}, open {len(still_open)}")
        for number, choose, options in still_open:
            names = ", ".join(ref.badges[o]["name"] for o in options)
            how = f"choose 1 of {len(options)}" if choose else "required"
            print(f"{'':<18} {number:<6} {how:<15} {names}")

    unit = f"{len(status['accepted'])} accepted positions"
    print(f"  req {status['number']:<10} leadership: {status['months']} months in one of {unit}")
    for pid in status["qualifying"]:
        name = ref.positions[pid]["name"]
        print(f"{'':<18} {name} ({held[pid]} mo) accepted for {rank['name']}")
    for pid in status["short"]:
        print(
            f"{'':<18} {ref.positions[pid]['name']} ({held[pid]} mo) accepted but short of "
            f"{status['months']} months"
        )
    for pid in status["rejected"]:
        print(
            f"{'':<18} {ref.positions[pid]['name']} ({held[pid]} mo) NOT in {rank['name']}'s "
            f"tree -- this rank does not accept it"
        )
    for number in status["alternatives"]:
        print(f"{'':<18} {number:<6} non-position alternative (text omitted: (c) Scouting America)")
    print(f"{'':<16} leadership requirement met by a position: {'yes' if met(status) else 'no'}")
    print()
    return {"doc": doc, "slots": slots, "filled": filled, "open": still_open, "status": status}


def footer(docs: list[dict]) -> None:
    """The licensing carve-out travels with the documents this tool read."""
    rights = {d["text_rights"] for d in docs}
    check(len(rights) == 1, "the rank requirement sets must agree on text_rights")
    print(f"text_rights     {rights.pop()}")


# --- selftest ----------------------------------------------------------------------------


def selftest(ref: Reference) -> int:
    """A canned scenario, then the invariants that make the trap logic above load-bearing."""
    badges = set(SELFTEST_BADGES)
    rank = ref.by_id[SELFTEST_RANK]
    print(f"scenario        {rank['name']} Scout, {len(badges)} badges, ", end="")
    print(", ".join(f"{p} {m} mo" for p, m in SELFTEST_POSITIONS.items()))
    print()

    reports = {}
    for i, nxt in enumerate(ref.remaining(SELFTEST_RANK)):
        label = "next rank" if i == 0 else "then"
        reports[nxt["id"]] = render(ref, nxt, badges, dict(SELFTEST_POSITIONS), label)

    eagle = reports["eagle"]
    slots = eagle["slots"]
    filled, still_open = eagle["filled"], eagle["open"]

    # The slot graph is exhaustive: a partial badge set splits it, it never loses a slot.
    check(
        len(filled) + len(still_open) == len(slots),
        "filled + open slots must equal the slot count",
    )
    check(filled and still_open, "the canned partial set must both fill and leave slots open")

    # 14 slots vs 18 badges vs 21 cumulative: the three numbers a naive reader collapses.
    distinct = {b for _, _, o in slots for b in o}
    check(
        len(distinct) > len(slots),
        "choose-1 slots must make distinct badge refs outnumber slots",
    )
    check(
        distinct == ref.flagged,
        "the badge refs in Eagle's tree must be exactly the eagle_required flag list",
    )
    cumulative = badge_requirement(eagle["doc"])["badge_count"]["cumulative"]
    check(cumulative > len(distinct), "cumulative badges must exceed the refs named in the tree")

    # A full required set closes every slot -- including the three either/or ones. Computed
    # rather than rendered: the point is the accounting, not another page of report.
    _, none_open = slot_state(slots, set(ref.flagged))
    check(not none_open, "holding every eagle_required badge must close every slot")

    # Position acceptance is asymmetric, and it is asymmetric on the RANK, not the position.
    bugler = dict(SELFTEST_POSITIONS)
    star_status = leadership_status(leadership(ref.doc("star")), bugler)
    life_status = leadership_status(leadership(ref.doc("life")), bugler)
    eagle_status = eagle["status"]
    check(met(star_status), "Bugler must satisfy Star's leadership requirement")
    check(met(life_status), "Bugler must satisfy Life's leadership requirement")
    check(not met(eagle_status), "Bugler must NOT satisfy Eagle's leadership requirement")
    check(
        "bugler" in star_status["accepted"] and "bugler" not in eagle_status["accepted"],
        "the Bugler asymmetry must come from the rank trees themselves",
    )
    check("bugler" in ref.positions, "the position entity is published")
    # The TRAP's other half: if the position entity ever started publishing its own acceptance,
    # a consumer could read it and be wrong for Eagle. This fails the day such a field appears.
    acceptance = {"ranks", "accepted_for_ranks", "eligible_ranks", "tenure_months"}
    check(
        not (set(ref.positions["bugler"]) & acceptance),
        "acceptance must live on the rank tree, not on the position entity",
    )

    # tenure_months is honoured: the same position, served too briefly, does not qualify.
    brief = leadership_status(leadership(ref.doc("star")), {"bugler": 1})
    check(not met(brief), "one month as Bugler must not satisfy Star's 4-month tenure")
    check(brief["short"] == ["bugler"], "a short-tenure position must report as short, not absent")

    # Star and Life offer a non-position alternative Eagle does not.
    check(
        len(star_status["alternatives"]) > len(eagle_status["alternatives"]),
        "Star must publish more non-position alternatives than Eagle",
    )

    # Referential integrity: every position a rank tree names is a published position.
    for rank_id in ("star", "life", "eagle"):
        refs = ref_ids(leadership(ref.doc(rank_id)), "position:")
        missing = sorted(refs - set(ref.positions))
        check(not missing, f"{rank_id} names unpublished positions: {missing}")

    print(f"slots           {len(filled)} filled + {len(still_open)} open = {len(slots)} total")
    print(
        f"numbers         {len(slots)} slots, {len(distinct)} distinct badge refs (== the "
        f"eagle_required list), {cumulative} cumulative badges"
    )
    print(f"full set        {len(ref.flagged)} flagged badges close all {len(slots)} slots")
    print(f"eagle_required  {len(ref.flagged)} flagged, {len(ref.unknown)} null (unknown, not no)")
    print("bugler          Star yes, Life yes, Eagle no -- read off each rank's own tree")
    print("tenure          1 month as Bugler fails Star's 4-month tenure; 8 months passes")
    footer([reports[r]["doc"] for r in reports])
    return 0


# --- cli ---------------------------------------------------------------------------------


def parse_positions(raw: str, ap: argparse.ArgumentParser, known: dict) -> dict[str, int]:
    held: dict[str, int] = {}
    for chunk in (c.strip() for c in raw.split(",") if c.strip()):
        pid, _, months = chunk.partition(":")
        if not months.isdigit():
            ap.error(f"--positions wants id:months, got {chunk!r}")
        if pid not in known:
            ap.error(f"unknown position {pid!r}; see v1/current/positions.json")
        held[pid] = int(months)
    return held


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Progress toward a Scout's next rank.")
    ap.add_argument("--rank", default=SELFTEST_RANK, help="rank already earned")
    ap.add_argument("--badges", default="", help="comma-separated merit badge ids")
    ap.add_argument("--positions", default="", help="comma-separated id:months_served")
    ap.add_argument("--selftest", action="store_true", help="run the canned scenario and assert")
    ap.add_argument("--base", help="API root; also read from $OSA_BASE by the shared helper")
    args = ap.parse_args(argv)

    ref = Reference()
    if args.selftest:
        return selftest(ref)

    if args.rank not in ref.by_id:
        ap.error(f"unknown {PROGRAM} rank {args.rank!r}; try {ref.ranks[3]['id']}")
    badges = {b.strip() for b in args.badges.split(",") if b.strip()}
    if unknown := sorted(badges - set(ref.badges)):
        ap.error(f"unknown merit badge ids: {', '.join(unknown)}")
    held = parse_positions(args.positions, ap, ref.positions)

    remaining = ref.remaining(args.rank)
    if not remaining:
        print(f"{ref.by_id[args.rank]['name']} is the top of the {PROGRAM} ladder")
        return 0

    # Historical badges carry `eagle_required: null` -- unknown, and silently counting them as
    # "not required" is how a Scout gets told they are further along than they are.
    if murky := sorted(badges & ref.unknown):
        print(f"note            eagle_required is null (unknown) for: {', '.join(murky)}")
    docs = []
    for i, rank in enumerate(remaining):
        docs.append(render(ref, rank, badges, held, "next rank" if i == 0 else "then")["doc"])
    footer(docs)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except CheckError as exc:  # an invariant broke: fail loudly, and nonzero
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
