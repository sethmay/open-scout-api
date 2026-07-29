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


BUCKETS = ("never_surveyed", "surveyed_offers_none", "unverified_import", "surveyed_with_findings")
groups: dict[str, list[dict]] = {name: [] for name in BUCKETS}
for camp in camps:
    groups[bucket(camp)].append(camp)

# Exhaustive and disjoint: every camp lands in exactly one bucket, so no camp's features can be
# read without also reading its survey date. Both halves matter -- a partition that missed camps
# would let the ambiguous ones slip through as "no features".
check(sum(len(g) for g in groups.values()) == len(camps), "the buckets must cover every camp")
check(
    len({c["id"] for g in groups.values() for c in g}) == len(camps),
    "the buckets must be disjoint",
)
# The ambiguity is real, not hypothetical: some camps have nothing known about their features.
check(groups["never_surveyed"], "an empty features array is not the same fact as `offers none`")

# What the trap costs, in one concrete query. The naive "no aquatics" answer is the honest
# answer plus every camp nobody has looked at -- the arithmetic is the proof.
aquatics = closure("aquatics")
surveyed = [c for c in camps if c["features_verified_at"] is not None]
naive_without = [c for c in camps if not aquatics & set(c["features"])]
honest_without = [c for c in surveyed if not aquatics & set(c["features"])]
unknown = groups["never_surveyed"]

check(len(naive_without) == len(honest_without) + len(unknown),
      "the naive answer absorbs the unknowns")
check(len(naive_without) > len(honest_without), "the naive answer over-reports `without aquatics`")
# The other direction of the same mistake: a "has X" filter can only under-report, never over.
check(
    len([c for c in surveyed if aquatics & set(c["features"])])
    == len([c for c in camps if aquatics & set(c["features"])]),
    "no unsurveyed camp can match a has-X filter, which is exactly why they under-report",
)

print(f"corpus          {len(camps)} camps, {len(surveyed)} with a features survey date")
for name in BUCKETS:
    coded = sum(len(c["features"]) for c in groups[name])
    print(f"  {name:22} {len(groups[name]):4}  ({coded} coded features)")
print("query           camps without any aquatics feature")
print(f"  naive         {len(naive_without)}  (features filter alone)")
print(f"  honest        {len(honest_without)}  (surveyed camps only)")
print(f"  unknown       {len(unknown)}  never surveyed -- unanswerable, not negative")
print(f"has-aquatics    {len([c for c in camps if aquatics & set(c['features'])])} known, "
      f"floor not total: a survey is not a guarantee of completeness")
