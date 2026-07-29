"""Trend merit-badge popularity across the published years.

TRAP: doing arithmetic on `earned_rank`. Averaging it, summing it, plotting it as a quantity, or
      reading rank 1 as "one badge earned" -- all produce numbers that look like statistics and
      mean nothing. Scouting America publishes ORDER ONLY. There is no count anywhere in this
      dataset, and none can be derived: rank 1 may be ten times rank 2 or a hair ahead of it.
FIX:  ordinal operations only. Rank deltas between two years, biggest movers, entries and exits.
      Read the `complete` flag before comparing years, because a partial list makes "not ranked"
      ambiguous, and check `metric` rather than assuming what the numbers mean.
"""

from osa import check, endpoint, get, items

template = endpoint("v1/merit-badge-rankings/{year}.json")
years = sorted(row["year"] for row in items("v1/merit-badge-rankings/index.json"))
check(len(years) >= 2, "a trend needs at least two years")

ranks: dict[int, dict[str, int]] = {}
docs = {}
for year in years:
    doc = get(template.format(year=year))
    docs[year] = doc
    # The metric is published per document precisely so a consumer cannot assume it is a count.
    check(doc["metric"] == "earned_rank", f"{year}: metric is {doc['metric']!r}, not earned_rank")
    check(doc["year"] == year, f"{year}: document disagrees with its index entry")

    listed = [row["rank"] for row in doc["rankings"]]
    # A complete 1..N with no gaps or ties is what makes a delta meaningful: any gap would mean
    # a rank was withheld, and a duplicate would mean the order is not a total order.
    check(sorted(listed) == list(range(1, len(listed) + 1)),
          f"{year}: ranks are not a complete 1..N")
    ranks[year] = {row["subject"]: row["rank"] for row in doc["rankings"]}
    check(len(ranks[year]) == len(listed), f"{year}: a badge is ranked twice")

# Only compare complete lists. In a partial year, absence means "not published", not "not earned".
complete = [y for y in years if docs[y]["complete"]]
check(len(complete) >= 2, "at least two complete years are needed to compare")
first, last = complete[0], complete[-1]

# Referential integrity, and the ordinal version of "did this badge exist yet". A badge cannot be
# ranked in a year that precedes its own introduction.
published = {b["id"] for b in items("v1/merit-badges/index.json")}
entity = endpoint("v1/merit-badges/{id}.json")
for year, table in ranks.items():
    unknown = sorted(s for s in table if s.split(":", 1)[1] not in published)
    check(not unknown, f"{year}: unranked subjects {unknown[:3]}")

both = set(ranks[first]) & set(ranks[last])
entries = sorted(set(ranks[last]) - set(ranks[first]))
exits = sorted(set(ranks[first]) - set(ranks[last]))

# Every badge that entered the ranking must already have existed in the year it entered -- the
# one check on this dataset that needs the entity documents, so it runs only on the entrants.
for subject in entries:
    doc = get(entity.format(id=subject.split(":", 1)[1]))
    started = min((v["valid_from"] or "0000")[:4] for v in doc["versions"])
    check(int(started) <= last, f"{subject} entered the {last} ranking but starts {started}")

# A positive delta means the badge moved UP, because a SMALLER rank is better. Getting this sign
# backwards is the other half of the arithmetic trap, and it reads perfectly plausibly: every
# riser is reported as a faller. So assert the direction, not just that a delta was computed.
deltas = sorted(((ranks[first][s] - ranks[last][s], s) for s in both), reverse=True)
check(deltas, "the two years must share badges to compare")
riser, faller = deltas[0][1], deltas[-1][1]
check(ranks[last][riser] < ranks[first][riser], "the biggest riser must have moved toward rank 1")
check(ranks[last][faller] > ranks[first][faller], "the biggest faller must have moved away from 1")
check(
    all(1 <= ranks[y][s] <= len(ranks[y]) for y in complete for s in ranks[y]),
    "every rank must fall inside its own year's range",
)
# The invariant that makes a delta legitimate at all: an ordinal is only comparable within a
# ranking of the same metric over the same population shape.
check(
    len({docs[y]["metric"] for y in complete}) == 1,
    "years with different metrics are not comparable",
)

top_now = sorted(ranks[last].items(), key=lambda kv: kv[1])[:3]
held = [s for s in both if ranks[first][s] == ranks[last][s]]


def name(subject: str) -> str:
    return subject.split(":", 1)[1]


print(f"years           {', '.join(str(y) for y in years)} "
      f"({len(complete)} complete, metric {docs[last]['metric']})")
print(f"source          {docs[last]['source_document']['title']}")
print(f"population      {len(ranks[first])} ranked in {first} -> {len(ranks[last])} in {last}")
print(f"most earned     {', '.join(f'{r}. {name(s)}' for s, r in top_now)}")
print(f"biggest risers  {first} -> {last}")
for delta, subject in deltas[:4]:
    print(f"  {name(subject):32} {ranks[first][subject]:3} -> {ranks[last][subject]:3}  (+{delta})")
print("biggest fallers")
for delta, subject in deltas[-4:][::-1]:
    print(f"  {name(subject):32} {ranks[first][subject]:3} -> {ranks[last][subject]:3}  ({delta})")
print(f"entries         {len(entries)}: {', '.join(name(s) for s in entries)}")
print(f"exits           {len(exits)}: {', '.join(name(s) for s in exits) or '(none)'}")
print(f"unchanged       {len(held)} badges held their exact rank")
print("not computable  totals, averages, growth rates -- no count exists in this dataset")
