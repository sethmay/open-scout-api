"""Sign a Scout off against the edition in force, not the oldest one.

TRAP: reading `requirement_sets[0]` and printing it as the requirements. The array is ordered
      OLDEST-first (ascending by id), exactly like `versions[]`, so `[0]` is a superseded
      edition -- Swimming's is the 2015 text, retired in 2024. Handing a Scout the wrong
      requirement text on the one thing they get signed off on is the sharpest failure in this
      dataset, and it has none of the guard rails the `versions[0]` trap has.
FIX:  read `current_requirement_set` -- the id of the edition whose `effective_to` is null --
      published on every requirement-bearing entity document (merit badges, ranks, awards,
      adventures) and on the current/adventures.json projection. The arrays are untouched and
      still ascending, so a consumer who wants the history still has it.
"""

from osa import check, endpoint, get, items

# The current-only requirement-set projection: exactly the in-force edition per subject. Use it
# as the independent oracle for what `current_requirement_set` on each entity must equal.
in_force = {r["subject"]: r["id"] for r in items("v1/current/requirement-sets.json")}

badge = endpoint("v1/merit-badges/{id}.json")
swim = get(badge.format(id="swimming"))

first = swim["requirement_sets"][0]                 # the trap: oldest edition
current = swim["current_requirement_set"]           # the fix: in-force edition
check(first != current, "requirement_sets[0] must not be mistaken for the in-force edition")
check(current == in_force.get("merit-badge:swimming"),
      "current_requirement_set must match the current/requirement-sets projection")

# Prove the two editions really are older vs. in-force, from their own effective windows.
rs = endpoint("v1/requirement-sets/{id}.json")
check(get(rs.format(id=first))["effective_to"] is not None, f"{first} must be superseded")
check(get(rs.format(id=current)).get("effective_to") is None, f"{current} must be in force")

# The version pointer is the same idea for the entity's own name/attributes.
cvi = swim["current_version_index"]
check(swim["versions"][cvi]["valid_to"] is None, "current_version_index must point at the open version")

# Corpus-wide across every merit badge: the published pointer equals the independent oracle, and
# a naive versions[0]/requirement_sets[0] read disagrees with it wherever an edition was retired.
traps = 0
for row in items("v1/merit-badges/index.json"):
    doc = get(badge.format(id=row["id"]))
    check(doc["current_requirement_set"] == in_force.get(f"merit-badge:{doc['id']}"),
          f"{doc['id']}: current_requirement_set disagrees with the current projection")
    idx = doc["current_version_index"]
    check(idx is None or doc["versions"][idx]["valid_to"] is None,
          f"{doc['id']}: current_version_index must point at an open version or be null")
    sets = doc["requirement_sets"]
    if sets and doc["current_requirement_set"] and sets[0] != doc["current_requirement_set"]:
        traps += 1

check(traps > 0, "the scan must find at least one badge where [0] is not the in-force edition")

print(f"swimming            requirement_sets[0] = {first}   <- the trap")
print(f"                    current_requirement_set = {current}   <- in force")
print(f"                    current_version_index = {cvi} -> {swim['versions'][cvi]['name']}")
print(f"corpus              {traps} merit badges where requirement_sets[0] is a superseded edition")
