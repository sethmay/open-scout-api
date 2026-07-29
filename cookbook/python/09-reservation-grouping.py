"""Render one map pin per property instead of one per camp.

TRAP: plotting each camp separately, so a reservation with six camps on it becomes six pins
      stacked on the same coordinate -- five of them unclickable. The camps are genuinely
      distinct entities with their own programs, so deduplicating by name or by coordinate
      either merges things that are not the same camp or misses camps a few hundred metres off.
FIX:  `reservation.id` is the grouping key. Group by it and render one pin per group. It is a
      STABLE OPAQUE key: a bare slug, deliberately NOT a `{kind}:{slug}` EntityRef, because no
      reservation entity exists to resolve. Group by it, compare it, store it -- never parse it,
      never assume it addresses a document. `reservation.name` may be null; the id never is.
"""

from osa import check, items

camps = items("v1/current/camps.json")
camp_ids = {c["id"] for c in camps}

groups: dict[str, list[dict]] = {}
standalone = []
for camp in camps:
    reservation = camp["reservation"]
    if reservation is None:
        standalone.append(camp)
    else:
        groups.setdefault(reservation["id"], []).append(camp)

check(groups, "the corpus must contain at least one shared property")
check(
    len(standalone) + sum(len(g) for g in groups.values()) == len(camps),
    "every camp is either standalone or in exactly one group",
)

# Opacity, asserted rather than asserted-in-prose. No colon means it is not an EntityRef, and at
# least one key naming no camp document proves it cannot be resolved as one -- even though a few
# reservations happen to share a slug with a camp, which is exactly the coincidence to not rely on.
check(all(":" not in key for key in groups), "a reservation id is a bare slug, not an EntityRef")
check(
    [key for key in groups if key not in camp_ids],
    "at least one reservation id must resolve to no camp, proving the key is opaque",
)

# Internal consistency: every camp in a group must agree on the property's name, or the pin has
# no label. `{None}` is a consistent group -- some properties carry no common name.
for key, members in groups.items():
    names = {c["reservation"]["name"] for c in members}
    check(len(names) == 1,
          f"{key}: members disagree about the name: {sorted(names, key=str)}")
    # The field is only set when a camp shares its location, so a group of one is a contradiction.
    check(len(members) >= 2, f"{key}: a reservation group must contain at least two camps")

pins_naive = len(camps)
pins_grouped = len(standalone) + len(groups)
check(pins_grouped < pins_naive, "grouping must strictly reduce the pin count")

# The overlap the trap produces: camps inside a group sitting on a single coordinate.
stacked = 0
for members in groups.values():
    points = {(c["lat"], c["lon"]) for c in members if c["lat"] is not None}
    stacked += sum(1 for c in members if c["lat"] is not None) - len(points)

largest = max(groups.items(), key=lambda kv: len(kv[1]))
label = largest[1][0]["reservation"]["name"] or "(no common name)"
sizes = sorted((len(g) for g in groups.values()), reverse=True)

print(f"corpus          {len(camps)} camps")
print(f"  standalone    {len(standalone)} (reservation is null)")
print(f"  grouped       {sum(len(g) for g in groups.values())} camps across "
f"{len(groups)} properties")
print(f"pins            {pins_naive} naive -> {pins_grouped} grouped "
f"({pins_naive - pins_grouped} fewer)")
print(f"stacked         {stacked} camps would have drawn on top of another camp's pin")
print(f"largest group   {largest[0]}")
print(f"  name          {label}")
print(f"  members       {', '.join(c['id'] for c in largest[1])}")
print(f"group sizes     {', '.join(str(n) for n in sizes)}")
print("key discipline  opaque slug: group and compare, never parse; no reservation entity exists")
