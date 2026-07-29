"""Rank a camp's feature list by how complete the survey behind it was.

TRAP: treating every feature list as a description of the camp, so a thin list reads as a thin
      camp. A `portal` list came from a registration-platform blurb because the camp has no
      descriptive page anywhere -- it is a floor on what the camp offers, not an inventory.
      Sorting or scoring camps by `len(features)` therefore ranks sources, not camps.
FIX:  `features_source_tier` is a completeness qualifier in the same spirit as `geo_precision`.
      `guide` read a camp-specific document, `camp_page` a page owned by the camp or council,
      `portal` only a booking blurb. Compare within a tier, and treat a lower tier's list as a
      lower bound. `null` iff `features_verified_at` is null, which is 06's never-surveyed case.
"""

from osa import check, items

# Declared best-to-worst, which is the ordering the qualifier exists to express. Listing it
# here (rather than deriving it from the data) is what lets the check below fail loudly if a
# new tier is published: an unknown value must not be silently ranked as "least complete".
TIERS = ("guide", "camp_page", "portal")

camps = items("v1/current/camps.json")
observed = {c["features_source_tier"] for c in camps}
check(observed <= {*TIERS, None}, f"unknown source tier(s): {sorted(observed - {*TIERS, None})}")

# The documented coupling: a tier without a survey date, or a date without a tier, would make
# either field uninterpretable. Enforced upstream; a consumer can rely on it.
for camp in camps:
    check(
        (camp["features_source_tier"] is None) == (camp["features_verified_at"] is None),
        f"{camp['id']}: features_source_tier and features_verified_at must be null together",
    )

by_tier = {tier: [c for c in camps if c["features_source_tier"] == tier] for tier in TIERS}
unsurveyed = [c for c in camps if c["features_source_tier"] is None]
means = {t: sum(len(c["features"]) for c in g) / len(g) for t, g in by_tier.items() if g}

# A never-surveyed camp carries no codes at all, so it is not a fourth, worst tier -- it is
# simply absent from this comparison, and averaging it in would fabricate a data point.
check(
    all(not c["features"] for c in unsurveyed),
    "an unsurveyed camp must carry no features, so it cannot be ranked by completeness",
)

# The tiers must actually stratify, or the qualifier is decoration. Checked pairwise along the
# declared order over the tiers that are populated: `portal` is a small manual-review queue and
# can legitimately be empty in a given build, but whichever tiers exist must rank in order.
populated = [t for t in TIERS if t in means]
check(len(populated) >= 2, "at least two tiers must be populated to compare anything")
for better, worse in zip(populated, populated[1:]):
    check(
        means[better] > means[worse],
        f"{better} surveys must average more features than {worse}"
        f" ({means[better]:.2f} vs {means[worse]:.2f})",
    )

# What the trap costs: the thinnest camp in the best tier still beats the average of the worst,
# so `len(features)` cannot order camps across tiers.
best, worst = populated[0], populated[-1]
floor_best = min(len(c["features"]) for c in by_tier[best])
cross_tier_confusions = sum(
    1 for c in by_tier[best] if len(c["features"]) < means[worst]
)

print(f"corpus          {len(camps)} camps; {len(unsurveyed)} never surveyed (tier null)")
for tier in TIERS:
    group = by_tier[tier]
    if not group:
        print(f"  {tier:10} {0:4} camps   (none in this build; manual-review queue)")
        continue
    span = f"{min(len(c['features']) for c in group)}..{max(len(c['features']) for c in group)}"
    print(f"  {tier:10} {len(group):4} camps   mean {means[tier]:5.2f} features   range {span}")
print(f"stratified      {' > '.join(f'{t} {means[t]:.2f}' for t in populated)}")
print(f"floor           thinnest {best} camp has {floor_best} features")
print(f"comparable      only within a tier: {cross_tier_confusions} {best} camps sit below the "
      f"{worst} mean")
