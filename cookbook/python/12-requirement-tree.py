"""Traverse a requirement tree without inflating what a Scout actually has to do.

TRAP: treating every child as required, because most nodes' children are. Roughly half the
      requirement sets carry a `choose: N` node somewhere, and counting all of their children
      turns a badge with 28 real requirements into 86 -- a progress bar that never fills, and a
      checklist that demands work nobody owes.
FIX:  a node with `choose: N` means pick N of its children; recurse into whichever N, and count
      the rest as optional. A node's `ref` is the entity it stands for (`merit-badge:`,
      `position:`, `adventure:`) and resolves against that dataset. Numbering, refs and counts
      only below -- requirement text is (c) Scouting America, see `text_rights`.
"""

from osa import check, endpoint, get, items

template = endpoint("v1/requirement-sets/{id}.json")


def walk(nodes: list[dict], depth: int = 0):
    """Every node in a tree, depth first, with its depth."""
    for node in nodes:
        yield depth, node
        yield from walk(node.get("children") or [], depth + 1)


def leaf_total(node: dict) -> int:
    """Leaves beneath `node`, ignoring `choose` -- i.e. what the trap counts."""
    kids = node.get("children") or []
    return 1 if not kids else sum(leaf_total(k) for k in kids)


def required(node: dict) -> int:
    """Leaves a Scout must actually complete, honouring `choose`.

    For a `choose: N` node take the N cheapest branches: the requirement is satisfied by any N,
    so the work owed is the smallest N, and a caller offering a progress bar needs that floor.
    """
    kids = node.get("children") or []
    if not kids:
        return 1
    costs = sorted(required(k) for k in kids)
    pick = node.get("choose")
    return sum(costs[:pick]) if pick else sum(costs)


# A ref prefix names the dataset that resolves it, and it must be resolved against that
# dataset's FULL index, not its `current/` projection. An in-force requirement set can name an
# entity that has since been discontinued -- Eagle 2024 still requires Citizenship in Society,
# which ended in February 2026 -- so resolving against `current/` reports a dangling ref that
# is not dangling. Ask "does this entity exist?" and "is it current?" as separate questions.
REFS = {"merit-badge": "merit-badges", "position": "positions", "adventure": "adventures"}
known = {kind: {row["id"] for row in items(f"v1/{ds}/index.json")} for kind, ds in REFS.items()}
live = {kind: {row["id"] for row in items(f"v1/current/{ds}.json")} for kind, ds in REFS.items()}
for kind in REFS:
    check(live[kind] <= known[kind],
          f"{kind}: the current projection must be a subset of the index")

index = items("v1/requirement-sets/index.json")
current = [row for row in index if row["effective_to"] is None]
check(current, "some requirement sets must be in force")

worst = (0, None, 0, 0)  # (gap, doc, naive, required)
choose_nodes = optional_nodes = resolved = retired = 0
for row in current:
    doc = get(template.format(id=row["id"]))
    naive = sum(leaf_total(r) for r in doc["requirements"])
    owed = sum(required(r) for r in doc["requirements"])
    check(owed <= naive, f"{row['id']}: required work cannot exceed the leaf count")

    for _, node in walk(doc["requirements"]):
        pick, kids = node.get("choose"), node.get("children") or []
        if pick is not None:
            # `choose` greater than the child count would be unsatisfiable, and `choose` on a
            # leaf would be meaningless -- both would break the recursion above silently.
            check(kids, f"{row['id']} {node['number']}: choose with no children")
            check(pick <= len(kids), f"{row['id']} {node['number']}: choose {pick} of {len(kids)}")
            choose_nodes += 1
            optional_nodes += len(kids) - pick
        ref = node.get("ref")
        if ref:
            kind, _, slug = ref.partition(":")
            check(kind in known, f"{row['id']} {node['number']}: unknown ref kind {kind!r}")
            check(slug in known[kind], f"{row['id']} {node['number']}: {ref} resolves to nothing")
            resolved += 1
            retired += slug not in live[kind]

    if naive - owed > worst[0]:
        worst = (naive - owed, doc, naive, owed)

check(choose_nodes > 0, "the corpus must contain choose nodes or this traversal is pointless")
check(resolved > 0, "the corpus must contain refs for the resolution to be exercised")
# If no set had a gap, `choose` would be decorative and the trap would be harmless.
check(worst[1] is not None, "at least one set must demand less work than its leaf count")

gap, doc, naive, owed = worst
tiers = {}
for depth, node in walk(doc["requirements"]):
    tiers[depth] = tiers.get(depth, 0) + 1
top = doc["requirements"][0]

print(f"corpus          {len(current)} requirement sets in force, of {len(index)} published")
print(f"  choose nodes  {choose_nodes} (making {optional_nodes} child requirements optional)")
print(f"  refs          {resolved} resolved against merit-badges, positions and adventures")
print(f"  retired refs  {retired} name an entity no longer current "
      "(resolve via index, not current/)")
print(f"worst inflation {doc['id']} ({doc['subject']})")
print(f"  naive         {naive} leaves if every child is required  <- the trap")
print(f"  required      {owed} leaves once `choose` is honoured")
print(f"  overstated by {gap} ({naive / owed:.1f}x)")
print(f"  depth         {', '.join(f'{d}:{n}' for d, n in sorted(tiers.items()))} (depth:nodes)")
print(f"  first node    {top['number']}: {len(top.get('children') or [])} children, "
      f"choose={top.get('choose')}, ref={top.get('ref')}")
print(f"text_rights     {doc['text_rights']}")
