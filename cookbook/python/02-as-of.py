"""Resolve an entity's state on a given date.

TRAP: reading `versions[0]` and treating it as the current record. Identity is permanent --
      `council:conquistador` is the same council it was in 1918 -- but name, number, website
      and headquarters live in effective-dated versions, and the array is not ordered by
      recency. Any council that was ever renamed carries a decades-dead name at `versions[0]`.
FIX:  select the version whose half-open [valid_from, valid_to) window contains the target
      instant, treating a null bound as open-ended rather than as missing. "Current" means
      `valid_to is None` -- a property of the version, never its position in the array.
"""

from datetime import date

from osa import check, endpoint, get, items

TODAY = date.today().isoformat()


def day(bound: str | None, *, lower: bool) -> str:
    """Normalize an effective-date bound to a comparable YYYY-MM-DD.

    Bounds are published at mixed granularity -- "1926" for a rename known only by year,
    "2026-06-01" for a documented merger -- and lexicographic order survives zero padding, so
    no date parsing is needed. A null bound is open-ended, not absent: widen it to infinity
    instead of skipping the version, or every still-in-force record disappears.
    """
    if bound is None:
        return "0000-01-01" if lower else "9999-12-31"
    return bound if len(bound) == 10 else f"{bound}-01-01"


def as_of(doc: dict, when: str) -> dict | None:
    """The one version in force at `when`, or None if the entity did not exist then.

    The window is half-open because consecutive versions share a boundary ("1918".."1926"
    then "1926".."1927"); an inclusive upper bound would put two names in force during 1926.
    """
    hits = [
        v
        for v in doc["versions"]
        if day(v["valid_from"], lower=True) <= when < day(v["valid_to"], lower=False)
    ]
    check(len(hits) <= 1, f"{doc['id']}: {len(hits)} versions in force at {when}")
    return hits[0] if hits else None


def current(doc: dict) -> dict:
    """The version a consumer should show today, matching how the index is projected.

    A retired entity has no open version at all, so fall back to the last one -- that is what
    makes a merged council still displayable instead of a blank row.
    """
    opens = [v for v in doc["versions"] if v["valid_to"] is None]
    check(len(opens) <= 1, f"{doc['id']}: {len(opens)} open-ended versions")
    check(doc["versions"], f"{doc['id']}: an entity must have at least one version")
    return opens[0] if opens else doc["versions"][-1]


tpl = endpoint("v1/councils/{id}.json")
renamed = get(tpl.format(id="conquistador"))
merged = get(tpl.format(id="golden-spread"))

# The trap, stated as data: versions[0] is a 1918 name, and it is not what `as_of` returns.
first = renamed["versions"][0]
mid = as_of(renamed, "1930-06-01")
now = as_of(renamed, TODAY)
check(first["name"] != now["name"], "versions[0] must not be mistaken for the current version")
check(mid["name"] != now["name"], "two different dates must resolve to two different versions")
check(now is current(renamed), "the open-ended version is the one in force today")

# A merged council resolves to None today: the identity survives, the record is not in force.
# `current()` still yields something to display, which is why the index can list it.
check(as_of(merged, "2020-01-01") is not None, "golden-spread existed in 2020")
check(as_of(merged, TODAY) is None, "a merged council has no version in force today")
check(current(merged)["valid_to"] is not None, "a retired entity's last version is closed")

# Corpus-wide: the two invariants that make effective dating usable at all. A step function
# only changes at its boundaries, so probing every published bound is exhaustive, not a sample.
probed = 0
for row in items("v1/councils/index.json"):
    doc = get(tpl.format(id=row["id"]))
    current(doc)  # raises if an entity has two open versions or none at all
    for v in doc["versions"]:
        for edge in (day(v["valid_from"], lower=True), day(v["valid_to"], lower=False)):
            as_of(doc, edge)  # raises if two versions are in force at the same instant
            probed += 1

check(probed > 0, "the corpus scan must actually probe something")

print(f"today           {TODAY}")
print(f"council         {renamed['id']} ({len(renamed['versions'])} versions)")
print(f"versions[0]     {first['name']} ({first['valid_from']}..{first['valid_to']})  <- the trap")
print(f"as of 1930      {mid['name']} ({mid['valid_from']}..{mid['valid_to']})")
print(f"as of today     {now['name']} ({now['valid_from']}..open)")
print(f"merged council  {merged['id']} -> in force today: {as_of(merged, TODAY)}")
print(f"  displayable   {current(merged)['name']} (closed {current(merged)['valid_to']})")
print(f"invariants      {probed} instants probed across every council; <=1 version in force")
