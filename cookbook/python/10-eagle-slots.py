"""Count the Eagle merit-badge slots a Scout has filled.

TRAP: using the `eagle_required` flag list as the requirement. The flag marks the badges that
      appear in Eagle requirement 3 -- the number Star and Life cite when they ask for badges
      "from the required list" -- but requirement 3 is not that many separate requirements. It
      is a graph of SLOTS, three of which are either/or, so a Scout satisfies it with fewer
      badges than the flag list contains and a naive checklist demands work nobody owes.
      (Separately: `eagle_required` is null for historical badges. Null is unknown, not false.)
FIX:  walk requirement 3's children. Each child is one slot; a child carrying `choose: 1` is one
      slot satisfiable by any of ITS children. Count slots filled, not badges matched. Structure
      and counts only below -- requirement text is (c) Scouting America, see `text_rights`.
"""

from osa import check, endpoint, get, items

RANK_SET = "eagle-2024"  # pinned: an effective-dated document, so its structure is immutable

doc = get(endpoint("v1/requirement-sets/{id}.json").format(id=RANK_SET))
check(doc["subject"] == "rank:eagle", f"{RANK_SET} must be an Eagle requirement set")

badges = next(r for r in doc["requirements"] if r.get("badge_count"))
check(badges["badge_count"] == {"earn": 10, "cumulative": 21}, "requirement 3's badge counts")


def slot_options(node: dict) -> list[str]:
    """The badge refs that satisfy one slot.

    A slot is either a single ref or a `choose: 1` node over alternatives. Anything else would
    be a structure this function does not understand, so say so rather than guessing.
    """
    if node.get("ref"):
        return [node["ref"]]
    options = [c["ref"] for c in node.get("children") or []]
    check(node.get("choose") == 1, f"{node['number']}: expected a single ref or choose:1")
    check(all(options) and len(options) >= 2,
          f"{node['number']}: an either/or slot needs alternatives")
    return options


slots = {child["number"]: slot_options(child) for child in badges["children"]}
either_or = {n: o for n, o in slots.items() if len(o) > 1}

# The structural contract of this document, and the number the trap gets wrong.
check(len(slots) == 14, f"Eagle requirement 3 has 14 slots, found {len(slots)}")
check(len(either_or) == 3, f"exactly 3 slots are either/or, found {len(either_or)}")

badge_index = items("v1/merit-badges/index.json")
flagged = {f"merit-badge:{b['id']}" for b in badge_index if b["eagle_required"]}
reachable = {ref for options in slots.values() for ref in options}
check(reachable == flagged, "the flag marks exactly the badges reachable from requirement 3")
# ...and yet the two numbers differ, which is the entire trap: an either/or slot contributes
# several flagged badges but only one slot, so the flag list is strictly the larger number.
check(len(flagged) > len(slots), "the flag-list size must not be read as the slot count")


def fill(earned: set[str]) -> tuple[set[str], set[str]]:
    """(slots filled, slots outstanding) for a set of `merit-badge:` refs."""
    filled = {n for n, options in slots.items() if earned & set(options)}
    return filled, set(slots) - filled


# A badge may satisfy at most one slot, or "slots filled" stops being a count of work done: one
# badge would close two slots at once and the trap's arithmetic would not hold. This is the check
# a scrambled or duplicated slot map fails -- no result of `fill()` can, because every slot is
# fed its own options and so always fills itself.
shared = sorted((a, b) for a in slots for b in slots if a < b and set(slots[a]) & set(slots[b]))
check(not shared, f"a badge may satisfy only one slot; these slots share one: {shared[:3]}")

# One badge per slot, taking the first alternative where there is a choice: the minimum set.
minimum = {options[0] for options in slots.values()}
filled = fill(minimum)[0]
check(len(minimum) == len(slots), "the minimum set is one badge per slot, not one per flag")

# A Scout who earned the other side of every either/or slot is equally done -- the point of the
# `choose` node. The load-bearing half is WHICH slots the two sets differ on: an either/or slot
# that listed one ref twice would pass `slot_options` and quietly stop being a choice.
swapped = {options[-1] for options in slots.values()}
check({n for n in slots if slots[n][0] != slots[n][-1]} == set(either_or),
      "the minimum and alternate sets must differ on exactly the either/or slots")
check(swapped != minimum, "the two satisfying sets must actually differ")

# A partial sample: everything except the badges behind one either/or slot.
gap = sorted(either_or)[0]
partial = {ref for n, options in slots.items() if n != gap for ref in options[:1]}
part_outstanding = fill(partial)[1]
check(part_outstanding == {gap}, f"dropping slot {gap}'s options must leave exactly it outstanding")

print(f"document        {doc['id']} (effective {doc['effective_from']}, in force: "
      f"{doc['effective_to'] is None})")
print(f"requirement     {badges['number']}: earn {badges['badge_count']['earn']} of "
      f"{badges['badge_count']['cumulative']} cumulative")
print(f"slots           {len(slots)}  ({len(either_or)} either/or, "
      f"{len(slots) - len(either_or)} fixed)")
print(f"either/or       {', '.join(f'{n}={len(o)} options' for n, o in sorted(either_or.items()))}")
print(f"eagle_required  {len(flagged)} badges carry the flag  <- not the number of slots")
print(f"minimum set     {len(minimum)} badges fill {len(filled)}/{len(slots)} slots")
print(f"alternate set   {len(swapped)} badges also fill all {len(slots)} "
      "(same slots, other options)")
print(f"partial sample  {len(partial)} badges -> outstanding: "
      f"{', '.join(sorted(part_outstanding))}")
print(f"text_rights     {doc['text_rights']}")
