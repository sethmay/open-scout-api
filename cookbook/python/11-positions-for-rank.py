"""Decide which positions of responsibility count toward a given rank.

TRAP: reading acceptance off the position entity, or assuming Star, Life and Eagle accept the
      same set. `v1/current/positions.json` carries a position's name, audience and unit types
      and says NOTHING about which ranks accept it -- there is no field to read, so a consumer
      either invents one or assumes "a position is a position". Both are wrong: Bugler counts
      for Star and Life but not for Eagle.
FIX:  acceptance lives on the RANK's requirement tree, as `position:` refs beneath the
      leadership requirement, and the three trees genuinely differ. Resolve the refs per rank
      and diff the sets. The trees also differ in their non-position routes: Star and Life
      allow a Scoutmaster-approved leadership project, Eagle does not.
"""

import hashlib

from osa import check, endpoint, get, items

RANK_SETS = {"star": "star-2024", "life": "life-2024", "eagle": "eagle-2024"}

positions = {p["id"]: p for p in items("v1/current/positions.json")}
# The trap, stated as a schema fact: nothing in the position projection mentions a rank.
check(
    not any("rank" in key for p in positions.values() for key in p),
    "a position record carries no rank acceptance -- that is why the rank tree is authoritative",
)

template = endpoint("v1/requirement-sets/{id}.json")
docs = {rank: get(template.format(id=set_id)) for rank, set_id in RANK_SETS.items()}


def walk(nodes: list[dict]):
    """Every node in a requirement tree, depth first."""
    for node in nodes:
        yield node
        yield from walk(node.get("children") or [])


def leadership(doc: dict) -> dict:
    """The one top-level requirement whose subtree carries `position:` refs."""
    hits = [
        r
        for r in doc["requirements"]
        if any((n.get("ref") or "").startswith("position:") for n in walk([r]))
    ]
    check(len(hits) == 1,
          f"{doc['id']}: expected one leadership requirement, got {len(hits)}")
    return hits[0]


def fingerprint(node: dict) -> str:
    """A requirement node's text as a digest -- never as prose.

    Routes have to be compared by the identity of their text rather than by `number` (see
    below), and a digest compares identically while being impossible to print as a requirement.
    The text is (c) Scouting America, so it is reduced here and never formatted into output.
    """
    return hashlib.sha256((node["text"] or "").encode("utf-8")).hexdigest()


accepted, routes = {}, {}
for rank, doc in docs.items():
    top = leadership(doc)
    refs = {n["ref"] for n in walk([top]) if (n.get("ref") or "").startswith("position:")}
    check(refs, f"{rank}: the leadership requirement must resolve to positions")
    # Referential integrity: a ref that names no position would silently shrink the set.
    unknown = sorted(r for r in refs if r.split(":", 1)[1] not in positions)
    check(not unknown, f"{rank}: unresolvable position refs {unknown}")
    accepted[rank] = {r.split(":", 1)[1] for r in refs}
    # Alternatives to holding a position: children of the leadership node with no position
    # beneath them at all. `choose: 1` on the parent is what makes them alternatives.
    check(top.get("choose") == 1, f"{rank}: the leadership requirement must be a choose-1")
    routes[rank] = [
        c
        for c in top["children"]
        if not any((n.get("ref") or "").startswith("position:") for n in walk([c]))
    ]

# The asymmetry, which is the whole reason acceptance cannot live on the position.
check(accepted["star"] != accepted["eagle"], "Star and Eagle must not accept the same positions")
check("bugler" in accepted["star"], "Bugler counts for Star")
check("bugler" not in accepted["eagle"], "Bugler does not count for Eagle")
check(accepted["star"] == accepted["life"], "Star and Life accept the same positions")
check(accepted["eagle"] < accepted["star"], "Eagle's set must be a strict subset of Star's")
# Star and Life offer one non-position route Eagle does not. Diff by text, not by `number`:
# the shared Lone Scout route is numbered 5c under Star and 4c under Eagle, so matching on
# numbering would pair up the wrong nodes and name the wrong route as the extra one.
eagle_routes = {fingerprint(c) for c in routes["eagle"]}
extra = [c for c in routes["star"] if fingerprint(c) not in eagle_routes]
check(len(extra) == 1, f"Star must offer exactly one route Eagle lacks, found {len(extra)}")
check(
    eagle_routes < {fingerprint(c) for c in routes["star"]},
    "Eagle's non-position routes must be a strict subset of Star's",
)

star_only = sorted(accepted["star"] - accepted["eagle"])

print(f"positions       {len(positions)} published; rank acceptance fields: 0")
for rank in RANK_SETS:
    tenure = leadership(docs[rank]).get("tenure_months")
    print(f"  {rank:6} {RANK_SETS[rank]:12} {len(accepted[rank]):3} positions, "
          f"{len(routes[rank])} non-position route(s), {tenure} months")
print(f"star == life    {accepted['star'] == accepted['life']}")
print(f"eagle subset    {accepted['eagle'] < accepted['star']} "
      f"({len(star_only)} accepted for Star/Life only)")
print(f"star-only       {', '.join(star_only)}")
# The number names the route; naming it by a clipped quotation would reproduce the requirement.
print(f"extra route     {extra[0]['number']} <- Star/Life only "
      f"(non-position alternative; text omitted: (c) Scouting America)")
print(f"text_rights     {docs['star']['text_rights']}")
