"""Read `features` together with `features_verified_at`, which is what makes it interpretable.

TRAP: reading an empty `features` array as "this camp has no aquatics", and therefore answering
      "camps without aquatics" with every camp that failed the filter. Absence of a code is not
      absence of the thing; most of those camps were never surveyed at all.
FIX:  the two fields vary independently and encode four different facts:
        null date + []       never surveyed -- nothing is known
        date + []            surveyed, and the camp genuinely offers none of the vocabulary
        null date + entries  incidental codes from a bulk import, not a survey
        date + entries       surveyed, with findings
      A date means a survey happened, NOT that the resulting list is exhaustive (see
      07-source-tier.py for how complete it was). So "has X" filters on the whole corpus
      under-report, and "without X" is only answerable over the surveyed subset.
"""

from osa import check, get, items

camps = items("v1/current/camps.json")
vocab = get("v1/vocab/camp-features.json")

children: dict[str, list[str]] = {}
for term in vocab["terms"]:
    parent = term.get("broader")
    if parent is not None:
        children.setdefault(parent, []).append(term["code"])


def closure(code: str) -> set[str]:
    """`code` plus everything transitively beneath it (see 05-feature-hierarchy.py)."""
    out: set[str] = set()
    stack = [code]
    while stack:
        current = stack.pop()
        if current in out:
            continue
        out.add(current)
        stack.extend(children.get(current, ()))
    return out


def bucket(camp: dict) -> str:
    """Which of the four facts this camp's (features, features_verified_at) pair states."""
    surveyed = camp["features_verified_at"] is not None
    coded = bool(camp["features"])
    if surveyed:
        return "surveyed_with_findings" if coded else "surveyed_offers_none"
    return "unverified_import" if coded else "never_surveyed"


# The same four facts as a lookup table, keyed by (surveyed?, coded?). bucket() spells them as
# branches and this spells them as data, which is what lets each camp's label be checked below
# against something instead of trusted.
STATES = {
    (False, False): "never_surveyed",
    (True, False): "surveyed_offers_none",
    (False, True): "unverified_import",
    (True, True): "surveyed_with_findings",
}
BUCKETS = tuple(STATES.values())
groups: dict[str, list[dict]] = {name: [] for name in BUCKETS}
for camp in camps:
    groups[bucket(camp)].append(camp)

# Every camp lands in exactly one bucket, so no camp's features can be read without also reading
# its survey date. Coverage is by construction -- bucket() returns one of the four labels or
# raises -- so what this can really catch is a repeated `id`, and it has to: every answer below is
# a SET of ids, and two camps sharing one would silently merge into a single row of the printout.
bucketed = [c["id"] for g in groups.values() for c in g]
check(len(bucketed) == len(camps) == len(set(bucketed)),
      "every camp must land in exactly one bucket under an id of its own")

# Now the labels themselves, re-derived from the raw pair rather than through bucket(). Reading
# `features` as a list (`!= []`) instead of through bool() is what makes this fail on a
# `features: null` -- JSON's other way to write "no codes", and the one that would quietly turn
# "nobody has looked" into "we looked and found nothing".
for name, group in groups.items():
    for camp in group:
        date = camp["features_verified_at"]
        # `""` is falsy but not null, so it would report a survey nobody performed.
        check(date is None or (isinstance(date, str) and date),
              f"{camp['id']}: features_verified_at must be null or a date, not {date!r}")
        state = STATES[(date is not None, camp["features"] != [])]
        check(state == name, f"{camp['id']}: the raw pair reads as {state}, bucketed as {name}")

# The ambiguity is real, not hypothetical: some camps have nothing known about their features. A
# build that had surveyed everything would fail here and should -- the cost measured below is
# exactly the size of this bucket, so with it empty the recipe would be demonstrating nothing.
check(groups["never_surveyed"], "an empty features array is not the same fact as `offers none`")

# What the trap costs, in one concrete query, taken over the closure of the coarse code (05's
# lesson). The closure is asserted here too, because 06's numbers silently become a different
# question if it degenerates: closure() seeds its argument unconditionally, so an `aquatics` that
# is no longer a published term -- renamed, or its children re-parented -- comes back as
# `{"aquatics"}` alone, matches almost nothing, and reports nearly the whole corpus as "without".
aquatics = closure("aquatics")
check({"aquatics"} < aquatics <= {t["code"] for t in vocab["terms"]},
      "the aquatics closure must expand, and every code in it must be a published term")

surveyed = [c for c in camps if c["features_verified_at"] is not None]
naive_without = {c["id"] for c in camps if not aquatics & set(c["features"])}
honest_without = {c["id"] for c in surveyed if not aquatics & set(c["features"])}
unknown = {c["id"] for c in groups["never_surveyed"]}
has_aquatics = {c["id"] for c in camps if aquatics & set(c["features"])}
absorbed = naive_without - honest_without

# Both sides of the split need members, or the comparison below compares two empty sets: a corpus
# where every surveyed camp offers aquatics, or where none does, prints the right shape and
# proves nothing. 07 guards its tier comparison the same way.
check(honest_without and has_aquatics,
      "some camps must offer aquatics and some surveyed camps must not, or nothing is compared")

# `naive_without` is `honest_without` plus both unsurveyed states, and that is the whole trap.
# The containment is true by construction of the two filters, so the printout states it in
# numbers rather than asserting it; the line that can fail is the `never_surveyed` guard above,
# which is what makes the difference non-zero and therefore what makes the trap cost anything.
print(f"corpus          {len(camps)} camps, {len(surveyed)} with a features survey date")
for name in BUCKETS:
    coded = sum(len(c["features"]) for c in groups[name])
    print(f"  {name:22} {len(groups[name]):4}  ({coded} coded features)")
print("query           camps without any aquatics feature")
print(f"  naive         {len(naive_without)}  (features filter alone)")
print(f"  honest        {len(honest_without)}  (surveyed camps only)")
print(f"  absorbed      {len(absorbed)}  unsurveyed camps the naive answer silently claims "
      f"({len(unknown)} never surveyed, {len(absorbed - unknown)} imported but unverified)")
print(f"has-aquatics    {len(has_aquatics)} known, "
      f"floor not total: a survey is not a guarantee of completeness")
