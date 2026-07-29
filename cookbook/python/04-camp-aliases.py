"""Redirect a retired camp id to the listing that survived a merge.

TRAP: an id saved in a bookmark or a user's saved search 404s, or -- worse, because it is
      silent -- quietly falls out of a `current/camps.json` scan, after two duplicate listings
      for the same property were merged into one. The id was never wrong. It was retired.
FIX:  `v1/camps/aliases.json` is the redirect table. It is a BARE `{retired: surviving}` map:
      no `$schema`, no envelope, no `items` array to unwrap, so the collection-reading helper
      does not apply to it. Resolve an unknown id through the map before deciding it is gone,
      and follow the map transitively -- a merge target can itself later be merged away.
"""

from osa import check, endpoint, get, items

aliases = get(endpoint("v1/camps/aliases.json"))
live = {c["id"]: c for c in items("v1/current/camps.json")}

# The bare-map shape is the point: a consumer that reaches for `doc["items"]` here gets a
# KeyError, and one that assumes an envelope silently reads the redirects as camp records.
check(isinstance(aliases, dict), "aliases.json is a bare map")
check("items" not in aliases and "$schema" not in aliases, "aliases.json carries no envelope")
check(aliases, "the redirect table must not be empty")


def resolve(camp_id: str) -> str | None:
    """Follow the redirect table to a live camp id, or None if the id is genuinely unknown.

    Bounded by the size of the map so a cycle in the data cannot hang a request; a miss means
    a real 404, not a merge, and must not be reported as one.
    """
    seen = set()
    while camp_id not in live:
        if camp_id in seen or camp_id not in aliases:
            return None
        seen.add(camp_id)
        camp_id = aliases[camp_id]
    return camp_id


# Referential integrity of the table itself.
check(all(v in live for v in aliases.values()), "every alias must point at a live camp")
# A key that is also a live id would make the redirect shadow a real record, so the two
# namespaces must stay disjoint.
check(not (set(aliases) & set(live)), "no retired id may also be a live camp id")
# Cycle-freedom, proved rather than assumed: every key must terminate on a live id.
unresolved = [k for k in aliases if resolve(k) is None]
check(unresolved == [], f"these aliases do not terminate on a live camp: {unresolved[:3]}")

# The trap and the fix, on one real id. Sorted so the recipe is reproducible run to run.
retired = sorted(aliases)[0]
surviving = resolve(retired)
check(retired not in live, "the retired id is exactly what a naive scan drops")
check(surviving is not None, "the retired id must still be recoverable")

camp = get(endpoint("v1/camps/{id}.json").format(id=surviving))
check(camp["id"] == surviving, "the surviving id must resolve to its own document")
# A miss is a miss: the map must not invent an answer for an id nobody ever published.
check(resolve("no-such-camp-id-at-all") is None, "an unknown id must resolve to None, not a guess")

# How many redirects chain through another redirect, i.e. need the transitive loop above.
multi = sum(1 for k in aliases if aliases[k] in aliases)

print(f"redirects       {len(aliases)} retired ids -> {len(set(aliases.values()))} surviving camps")
print("envelope        none (bare map; keys are ids, not an items array)")
print(f"retired id      {retired}")
print(f"  in current/   {retired in live}  <- the silent drop")
print(f"  resolves to   {surviving}")
print(f"  camp          {camp['versions'][-1]['name']} ({camp['kind']})")
print(f"unknown id      resolve('no-such-camp-id-at-all') -> {resolve('no-such-camp-id-at-all')}")
print(f"invariants      {len(aliases)} keys terminate; {multi} need a transitive hop; 0 cycles")
