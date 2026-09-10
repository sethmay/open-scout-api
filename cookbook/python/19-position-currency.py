"""Offer only the positions a leader can actually register for today.

TRAP: reading every row of the Trained Leader Requirements chart as a CURRENT position. The chart
      is transcribed faithfully, retired positions included -- the rank-specific Cub den leaders
      that folded into one Den Leader in 2024, the Varsity "team" positions, "Leader of 11-Year-Old
      Scouts". Answering "what training do I need TODAY" off the raw list offers roles that no
      longer exist.
FIX:  read `status`. A discontinued row is KEPT -- ids are permanent, so a registration code a
      consumer holds still resolves -- and carries a `discontinued` block with the reason and, where
      known, the position that replaced it. Filter to status == "active" for the current roster.
"""

from osa import check, endpoint, get, items, meta

rows = items("v1/training-requirements/index.json")
active = [r for r in rows if r["status"] == "active"]
retired = [r for r in rows if r["status"] == "discontinued"]

check(retired, "the chart carries retired positions; they must be marked, not dropped")
check(len(active) + len(retired) == len(rows), "status must partition every row")
check(meta()["datasets"]["training-requirements"]["current"] == len(active),
      "meta.current must equal the active roster")

# A known retirement: the 2024 den-leader consolidation. The id still resolves -- that is the point.
tpl = endpoint("v1/training-requirements/{id}.json")
ids = {r["id"] for r in rows}
check("pack-tiger-cub-den-leader" in ids, "a retired position keeps its id, it is not deleted")
tiger = get(tpl.format(id="pack-tiger-cub-den-leader"))
check(tiger["status"] == "discontinued", "Tiger Cub Den Leader is a retired position")
check(tiger["discontinued"]["reason"], "a discontinued position must say why it was retired")

# Every retired row is honest about itself, and a naive "all positions" read over-counts the
# current roster by exactly the retired set -- which is the miscount this field prevents.
for r in retired:
    doc = get(tpl.format(id=r["id"]))
    check(doc["status"] == "discontinued", f"{r['id']}: index and document disagree on status")
    check(doc["discontinued"].get("reason"), f"{r['id']}: no discontinuation reason")
check(len(rows) - len(active) == len(retired), "a raw count over-reports current positions")

print(f"positions       {len(rows)} rows in the chart")
print(f"current         {len(active)} active -- the roster to offer today")
print(f"retired         {len(retired)} discontinued, kept so held codes still resolve")
print(f"example         pack-tiger-cub-den-leader -> {tiger['discontinued']['reason']}")
by_reason: dict[str, int] = {}
for r in retired:
    doc = get(tpl.format(id=r["id"]))
    key = "superseded" if doc["discontinued"].get("superseded_by") else "program ended / legacy"
    by_reason[key] = by_reason.get(key, 0) + 1
for k, n in sorted(by_reason.items()):
    print(f"  {k:24} {n}")
