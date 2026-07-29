"""Plot camps without putting geocoder backfills on the map as real locations.

TRAP: pinning every camp that has a `lat`/`lon`. Roughly a quarter of the coordinates are city
      or state-centroid backfills, so a "camps near me" search returns camps that are nowhere
      near the pin, and a state centroid shows up as a camp in an empty field. The coordinate
      is present and in range; nothing about the value itself looks wrong.
FIX:  branch on `geo_precision`. `exact` is a camp-specific source point and can be pinned;
      `approximate` is a centroid backfill, so soft-plot or bucket it and never quote a
      distance from it; `null` means the camp could not be placed and must be listed, not
      plotted. `elevation_ft` and the July temperatures are sampled AT that point, so they
      inherit the same precision -- an approximate camp's elevation is the city's.
"""

from osa import check, items

camps = items("v1/current/camps.json")

PLOTTABLE = {"exact": "pin", "approximate": "soft-plot or bucket", None: "list, do not plot"}
plans = {plan: [] for plan in PLOTTABLE.values()}
for camp in camps:
    check(camp["geo_precision"] in PLOTTABLE, f"{camp['id']}: unknown geo_precision")
    plans[PLOTTABLE[camp["geo_precision"]]].append(camp)

check(sum(len(g) for g in plans.values()) == len(camps), "every camp must get a plotting plan")

# The coupling that makes the branch safe: a coordinate always arrives with a precision, and a
# missing coordinate always arrives with a null precision. Neither half can be assumed alone.
for camp in camps:
    placed = camp["lat"] is not None
    check(placed == (camp["lon"] is not None), f"{camp['id']}: half a coordinate")
    check(placed == (camp["geo_precision"] is not None),
          f"{camp['id']}: precision disagrees with coords")
    if placed:
        check(-90 <= camp["lat"] <= 90, f"{camp['id']}: latitude out of range")
        check(-180 <= camp["lon"] <= 180, f"{camp['id']}: longitude out of range")

# What proves these are backfills rather than measurements: distinct camps landing on the SAME
# point. Two camps cannot share a survey pin, but they do share a city centroid.
def reuse(precision: str) -> tuple[int, int, dict]:
    group = [c for c in camps if c["geo_precision"] == precision]
    at: dict[tuple[float, float], list[dict]] = {}
    for camp in group:
        at.setdefault((camp["lat"], camp["lon"]), []).append(camp)
    shared = {point: cs for point, cs in at.items() if len(cs) > 1}
    return len(group), sum(len(cs) for cs in shared.values()), shared


n_exact, exact_shared, _ = reuse("exact")
n_approx, approx_shared, approx_points = reuse("approximate")

check(n_exact and n_approx, "both precisions must be present for the branch to be exercised")
check(approx_shared >= 1, "approximate points are backfills, so distinct camps must share one")
check(
    approx_shared > exact_shared,
    f"coordinate reuse must concentrate in `approximate` ({approx_shared} vs {exact_shared})",
)

worst = max(approx_points.items(), key=lambda kv: len(kv[1]), default=(None, []))
unplaceable = plans["list, do not plot"]

print(f"corpus          {len(camps)} camps")
for precision, plan in PLOTTABLE.items():
    group = [c for c in camps if c["geo_precision"] == precision]
    print(f"  {str(precision):12} {len(group):4}  -> {plan}")
print("coordinate reuse (distinct camps sharing one point)")
print(f"  exact         {exact_shared:4} camps of {n_exact}")
print(f"  approximate   {approx_shared:4} camps of {n_approx}  <- centroids, not survey pins")
if worst[0] is not None:
    where = worst[1][0]
    scope = where["city"] or f"{where['state']} state centroid"
    print(f"  worst point   {worst[0][0]:.4f},{worst[0][1]:.4f} shared by "
          f"{len(worst[1])} camps ({scope})")
print("derived fields  elevation_ft and july_*_f inherit geo_precision (sampled at the point)")
if unplaceable:
    one = unplaceable[0]
    print(f"unplaceable     {one['id']} ({one['city'] or one['state']}): list it, never plot it")
