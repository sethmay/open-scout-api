"""Decide whether a published fact is stale enough to re-check.

TRAP: two ways to get this wrong. Trusting `verified_at` forever, so a fact confirmed once in
      2025 is served as current indefinitely; or reaching for `imported_at`, which every camp
      carries and which is always recent, so a "stale after 12 months" check reports that
      nothing in the corpus is stale. `imported_at` measures OUR pipeline, not the fact.
FIX:  `verified_at` is the source-confirmation date -- for an imported camp it is camp-finder's
      own, not ours -- and it is the only date a staleness rule may use. `imported_at` is the
      ingest date and answers a different question. Read `confidence` alongside: 0.9 for curated
      or national sources, 0.8 for a higher-confidence import, 0.6 for a default import, and
      below 1.0 whenever a machine did the extracting.
"""

from datetime import date

from osa import check, items, meta

TODAY = date.today()
STALE_MONTHS = 12
AGING_MONTHS = 6


def months_since(iso: str) -> int:
    """Whole months from an ISO date to today. Calendar arithmetic, no third-party dates."""
    then = date.fromisoformat(iso)
    months = (TODAY.year - then.year) * 12 + (TODAY.month - then.month)
    return months - (TODAY.day < then.day)


def bucket(iso: str) -> str:
    age = months_since(iso)
    if age >= STALE_MONTHS:
        return "stale"
    return "aging" if age >= AGING_MONTHS else "fresh"


BUCKETS = ("fresh", "aging", "stale")

# Every current projection carries the provenance triple, so a consumer never has to fetch an
# entity document just to find out how much to trust a row.
projections = [e for e in meta()["endpoints"] if e.startswith("v1/current/")]
check(projections, "meta must publish the current projections")

rows = 0
methods: dict[str, set[float]] = {}
for path in projections:
    for row in items(path):
        for field in ("verified_at", "method", "confidence"):
            check(row.get(field) is not None, f"{path}: {row['id']} is missing {field}")
        check(0 < row["confidence"] <= 1,
              f"{row['id']}: confidence {row['confidence']} out of range")
        # `date.fromisoformat` raising here would be a schema violation, so assert the shape.
        check(len(row["verified_at"]) == 10, f"{row['id']}: verified_at is not a full date")
        date.fromisoformat(row["verified_at"])
        methods.setdefault(row["method"], set()).add(row["confidence"])
        rows += 1

# A machine-extracted fact is never certain, which is what `confidence` is for.
for method, values in methods.items():
    if "llm" in method:
        check(max(values) < 1.0, f"{method} must never claim confidence 1.0")

camps = items("v1/current/camps.json")
by_verified = {name: [] for name in BUCKETS}
for camp in camps:
    by_verified[bucket(camp["verified_at"])].append(camp)
check(sum(len(g) for g in by_verified.values()) == len(camps),
      "the age buckets must cover every camp")

# The two dates are different facts, not aliases: if they always agreed, the trap would be
# harmless and the field would be redundant.
divergent = [c for c in camps if c["verified_at"] != c["imported_at"]]
check(divergent, "verified_at and imported_at must be distinct facts")
lag = max(months_since(c["verified_at"]) - months_since(c["imported_at"]) for c in camps)
check(lag > 0, "at least one camp was verified well before it was imported")

# The measurable cost of using the wrong field, asserted STRICTLY. Ingest dates cluster at the
# last build, so a rule keyed on `imported_at` under-reports -- often to zero. Requiring a
# strict inequality is what makes this recipe fail if someone "simplifies" it to `imported_at`;
# and it only gets truer over time, because verified_at ages while imported_at is refreshed.
stale_correct = [c for c in camps if months_since(c["verified_at"]) >= STALE_MONTHS]
stale_wrong = [c for c in camps if months_since(c["imported_at"]) >= STALE_MONTHS]
check(len(stale_correct) > len(stale_wrong), "imported_at must under-report staleness")
check(
    any(bucket(c["verified_at"]) != bucket(c["imported_at"]) for c in camps),
    "the two dates must disagree about at least one camp, or the distinction is untestable",
)

oldest = min(camps, key=lambda c: c["verified_at"])
print(f"today           {TODAY} (stale >= {STALE_MONTHS} months, aging >= {AGING_MONTHS})")
print(f"provenance      {rows} rows across {len(projections)} current projections carry "
      f"verified_at + method + confidence")
print("confidence by method")
for method, values in sorted(methods.items()):
    span = ", ".join(f"{v:g}" for v in sorted(values))
    print(f"  {method:22} {span}")
print("camp age by verified_at")
for name in BUCKETS:
    print(f"  {name:22} {len(by_verified[name]):4}")
print(f"oldest fact     {oldest['id']} verified {oldest['verified_at']} "
      f"({months_since(oldest['verified_at'])} months ago, confidence {oldest['confidence']})")
print(f"  imported      {oldest['imported_at']} ({months_since(oldest['imported_at'])} months ago)")
print(f"stale count     {len(stale_correct)} by verified_at vs {len(stale_wrong)} by imported_at")
print(f"divergent       {len(divergent)}/{len(camps)} camps; largest lag {lag} months")
