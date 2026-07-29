"""Follow an entity through renames, mergers and supersessions.

TRAP: two different wrong answers, from the same wrong assumption -- that a lifecycle change
      overwrote the old record. (a) Grepping `events` for `type == "renamed"` finds almost
      nothing, so the dataset looks like it has no rename history; in fact a council rename is
      the `name` field CHANGING BETWEEN CONSECUTIVE VERSIONS, and dozens of councils have one.
      (b) A stored id missing from a `current/` projection looks defunct, so a consumer drops
      the user's bookmark instead of forwarding it to the council that survived the merger.
FIX:  the two mechanisms are separate on purpose. A rename keeps the identity, so it is a
      version boundary: diff `name` across versions ordered by `valid_from`. A merger changes
      which identity carries on, so it is an event: walk `participants[].ref`/`role`, where
      `predecessor -> successor|continuing` is the forward edge and its reverse walks back.
      Merit-badge supersession is the contrast -- that lineage genuinely IS an event, and its
      `date` is usually null, so order the walk by graph edges and never by date.
"""

from osa import check, endpoint, get

FORWARD = ("successor", "continuing")  # who carries on; `continuing` is the absorbing party
BACKWARD = ("predecessor",)
TEMPLATES = {
    "council": endpoint("v1/councils/{id}.json"),
    "merit-badge": endpoint("v1/merit-badges/{id}.json"),
}


def fetch(ref: str) -> dict:
    """Resolve a `{kind}:{slug}` participant ref to its document."""
    kind, _, slug = ref.partition(":")
    doc = get(TEMPLATES[kind].format(id=slug))
    # Referential integrity, checked where it can be checked: a participant ref must name a
    # document that agrees about what it is.
    check(f"{doc['kind']}:{doc['id']}" == ref, f"{ref} resolved to {doc['kind']}:{doc['id']}")
    return doc


def renames(doc: dict) -> list[tuple[str, str, str]]:
    """Rename boundaries as (effective, old name, new name), from the version timeline.

    Sort by `valid_from` rather than trusting array order, and pad a year-only bound so the
    comparison stays lexicographic. Consecutive versions that share a name are not renames --
    a version boundary can also mean a number or headquarters changed.
    """
    ordered = sorted(doc["versions"], key=lambda v: (v["valid_from"] or "0000").ljust(10, "0"))
    return [
        (b["valid_from"], a["name"], b["name"])
        for a, b in zip(ordered, ordered[1:])
        if a["name"] != b["name"]
    ]


def hop(doc: dict, forward: bool) -> list[tuple[dict, str]]:
    """The (event, ref) pairs one lifecycle step from `doc` in one direction.

    An event whose only role is `subject` has no edge at all, which is why renames cannot be
    walked: there is no second identity to walk to.
    """
    src, dst = (BACKWARD, FORWARD) if forward else (FORWARD, BACKWARD)
    me = f"{doc['kind']}:{doc['id']}"
    out = []
    for event in doc["events"]:
        if any(p["ref"] == me and p["role"] in src for p in event["participants"]):
            out += [(event, p["ref"]) for p in event["participants"] if p["role"] in dst]
    return out


def walk(start: str, forward: bool) -> tuple[list[str], list[dict], int]:
    """Breadth-first lineage walk. Returns (refs visited, events crossed, cycle guard hits).

    The guard is not decoration: a `merged` event can list several predecessors, so this is a
    DAG rather than a list, and one bad edge would otherwise spin here forever.
    """
    seen, order, crossed, guarded = {start}, [], [], 0
    frontier = [start]
    while frontier:
        ref = frontier.pop(0)
        order.append(ref)
        for event, nxt in hop(fetch(ref), forward):
            crossed.append(event)
            if nxt in seen:
                guarded += 1
                continue
            seen.add(nxt)
            frontier.append(nxt)
    return order, crossed, guarded


# --- renames live in versions, not in events -------------------------------------------------
cq = fetch("council:conquistador")
cq_renames = renames(cq)
cq_rename_events = [e for e in cq["events"] if e["type"] == "renamed"]

check(len(cq_renames) >= 2, "conquistador must expose several renames through its versions")
check(
    len({n for _, old, new in cq_renames for n in (old, new)}) > 1,
    "a rename means consecutive versions carry different names",
)
# The load-bearing half of the lesson: this council has a rename history and NO rename event,
# so a consumer that looks only at `events` sees nothing. If renames ever migrate into events,
# this check fails and the recipe gets fixed instead of quietly teaching the wrong mechanism.
check(cq_rename_events == [], "conquistador's renames must be version boundaries, not events")
check(hop(cq, forward=True) == [], "a renamed council has no lineage edge to walk")

# --- mergers and absorptions live in events -------------------------------------------------
# `llano-estacado` merged into `golden-spread` in 1987, which merged into `prairie-sky` in
# 2026, so the oldest id still forwards -- across two events -- to a council in force today.
fwd, fwd_events, fwd_cycles = walk("council:llano-estacado", forward=True)
check(len(fwd) >= 3, "llano-estacado must forward through at least two mergers")
check(fwd_cycles == 0, "a lineage chain must terminate, not cycle")
terminal = fetch(fwd[-1])
check(
    any(v["valid_to"] is None for v in terminal["versions"]),
    "walking forward must end on an entity that is still in force",
)

back, _, back_cycles = walk("council:prairie-sky", forward=False)
check(back_cycles == 0, "a reverse lineage walk must terminate too")
check(set(fwd[:-1]) <= set(back), "forward and reverse edges must describe the same graph")

# --- badge supersession: an event chain with no dates at all ---------------------------------
badges, badge_events, badge_cycles = walk("merit-badge:clerk", forward=True)
check(len(badges) >= 3, "the clerk supersession chain must be at least two hops")
check(badge_cycles == 0, "the badge chain must terminate")
undated = [e for e in badge_events if e["date"] is None]
check(undated, "this chain is exactly the case where the event date is null")

first, last = cq_renames[0], cq_renames[-1]
via = ", ".join(f"{e['type']} {e['date'] or 'undated'}" for e in fwd_events)
print("renames (versions, not events)")
print(f"  council       {cq['id']}: {len(cq['versions'])} versions, {len(cq_renames)} renames")
print(f"  first         {first[1]} -> {first[2]} ({first[0]})")
print(f"  last          {last[1]} -> {last[2]} ({last[0]})")
print(f"  renamed evts  {len(cq_rename_events)}  <- grepping events for renames finds nothing")
print("mergers (events)")
print(f"  forward       {' -> '.join(r.split(':', 1)[1] for r in fwd)}")
print(f"  via           {via}")
print(f"  terminal      {terminal['id']} is still in force")
print(f"  backward      {back[0].split(':', 1)[1]} <- "
      f"{', '.join(sorted(r.split(':', 1)[1] for r in back[1:]))}")
print("supersession (events)")
print(f"  badge chain   {' -> '.join(r.split(':', 1)[1] for r in badges)}")
print(f"  dates         {len(undated)}/{len(badge_events)} undated; walked by edge, not by date")
print(f"cycle guard     {fwd_cycles + back_cycles + badge_cycles} revisits across all walks")
