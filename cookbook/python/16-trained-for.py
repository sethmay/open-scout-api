"""Work out what an adult leader must complete to be Position Trained.

TRAP: keying training requirements by position alone -- by registration code, or by position
      name. Code `CC` is a committee chairman in a pack, a troop, a team, a crew and a ship, and
      needs a DIFFERENT course in each; even the Youth Protection course differs, because
      Venturing and Sea Scouting use their own. A lookup keyed on `CC` returns one of the five
      arbitrarily and tells four out of five leaders to take the wrong course.
FIX:  key by (registration_code, unit_type). Both are published on every training-requirement
      record for exactly this reason. Resolve the `requires` tree -- a bare `ref`, or a
      `choose: N` node of alternative deliveries -- against the training catalogue.
"""

from osa import check, endpoint, get, items

catalogue = {t["id"]: t for t in items("v1/current/training.json")}
requirements = items("v1/training-requirements/index.json")
check(requirements, "the training-requirements index must not be empty")

template = endpoint("v1/training-requirements/{id}.json")


def courses(nodes: list[dict]) -> tuple[set[str], int]:
    """(course refs beneath these nodes, number of either/or groups).

    A node is either a single `ref` -- a course that must be taken -- or a `choose: N` group of
    alternative deliveries of the same content, e.g. classroom or online. Both count as the
    same requirement; only the delivery differs.
    """
    refs: set[str] = set()
    choices = 0
    for node in nodes:
        if node.get("ref"):
            refs.add(node["ref"])
            continue
        kids = node.get("children") or []
        check(node.get("choose"), f"a node with no ref must offer a choice: {node}")
        check(node["choose"] <= len(kids), f"choose {node['choose']} of {len(kids)}")
        choices += 1
        nested, deeper = courses(kids)
        refs |= nested
        choices += deeper
    return refs, choices


# (code, unit_type) -> the requirement record. The composite key is the whole lesson: building
# this dict keyed on `code` alone would silently drop four of the five `CC` records.
by_key: dict[tuple[str, str], dict] = {}
by_code: dict[str, set[str]] = {}
for row in requirements:
    check(row["registration_codes"], f"{row['id']}: a requirement must carry a registration code")
    check(row["unit_type"], f"{row['id']}: a requirement must carry a unit type")
    for code in row["registration_codes"]:
        key = (code, row["unit_type"])
        check(key not in by_key, f"{code}/{row['unit_type']} is published twice")
        by_key[key] = row
        by_code.setdefault(code, set()).add(row["unit_type"])

collisions = {code: units for code, units in by_code.items() if len(units) > 1}
check(collisions, "at least one registration code must appear under several unit types")

# For each colliding code, resolve every unit type's course set and prove they differ. If they
# were all identical the composite key would be redundant and the trap would cost nothing.
resolved: dict[str, dict[str, set[str]]] = {}
for code, units in sorted(collisions.items()):
    per_unit = {}
    for unit in sorted(units):
        doc = get(template.format(id=by_key[(code, unit)]["id"]))
        check(doc["unit_type"] == unit, f"{doc['id']}: unit_type disagrees with the index")
        check(code in doc["registration_codes"], f"{doc['id']}: does not carry code {code}")
        refs, choices = courses(doc["requires"])
        check(refs, f"{doc['id']}: a requirement must resolve to at least one course")
        # Referential integrity against the catalogue, which is what makes the refs usable.
        for ref in refs:
            slug = ref.split(":", 1)[1]
            check(slug in catalogue, f"{doc['id']}: {ref} resolves to nothing")
        per_unit[unit] = {r.split(":", 1)[1] for r in refs}
    resolved[code] = per_unit

# The invariant the whole recipe exists for: some code's course set genuinely varies by unit type.
varying = {c: u for c, u in resolved.items() if len({frozenset(s) for s in u.values()}) > 1}
check(varying, "at least one code must require a different course set per unit type")

worst = max(varying.items(), key=lambda kv: len({frozenset(s) for s in kv[1].values()}))
code, per_unit = worst
shared = set.intersection(*per_unit.values())
distinct = {frozenset(s) for s in per_unit.values()}
name = by_key[(code, sorted(per_unit)[0])]["position_name"]

print(f"catalogue       {len(catalogue)} courses; {len(requirements)} training requirements")
print(f"keys            {len(by_key)} (code, unit_type) pairs over {len(by_code)} codes")
print(f"codes reused    {len(collisions)} appear under more than one unit type")
print(f"varying         {len(varying)} of those need different courses per unit type")
print(f"worked example  code {code} ({name}) in {len(per_unit)} unit types, "
      f"{len(distinct)} distinct course sets")
for unit in sorted(per_unit):
    print(f"  {unit:8} {', '.join(sorted(per_unit[unit]))}")
print(f"shared          {', '.join(sorted(shared)) or '(nothing -- not even Youth Protection)'}")
print(f"wrong key       looking `{code}` up by code alone returns 1 of {len(per_unit)} answers")
