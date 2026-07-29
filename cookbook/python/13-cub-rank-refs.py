"""Read a Cub Scout rank, whose requirements are references rather than text.

TRAP: looking for requirement text in a Cub rank tree and finding almost none, then concluding
      the Cub ranks are unpopulated or that the scrape failed. Nothing is missing. A Cub rank
      genuinely IS a list of adventures: the work is defined by each adventure, and the rank
      only says which ones and how many.
FIX:  the six Cub rank trees are pure structure -- two groups of `adventure:` refs. Group 1 is
      the required adventures; group 2 carries `choose: 2`, so it is the elective pool, not a
      list of 20 obligations. Resolve the refs against `current/adventures.json` for names,
      categories and program areas. Refs and counts only below -- text is (c) Scouting America.
"""

from osa import check, endpoint, get, items

adventures = {a["id"]: a for a in items("v1/current/adventures.json")}
ranks = {r["id"]: r for r in items("v1/current/ranks.json")}
cub_ranks = {rid: r for rid, r in ranks.items() if r["program"] == "cub_scouts"}
check(cub_ranks, "the Cub Scouts program must publish ranks")

# One in-force requirement set per Cub rank, found through `subject` rather than by guessing an
# id: the naming convention (`bear-2024`) is not part of the published contract.
sets_by_subject = {
    row["subject"]: row["id"]
    for row in items("v1/requirement-sets/index.json")
    if row["effective_to"] is None
}

template = endpoint("v1/requirement-sets/{id}.json")
summary, rights = [], set()
for rid, rank in sorted(cub_ranks.items(), key=lambda kv: kv[1]["order"]):
    set_id = sets_by_subject.get(f"rank:{rid}")
    check(set_id, f"rank:{rid} must have a requirement set in force")
    doc = get(template.format(id=set_id))

    rights.add(doc["text_rights"])
    groups = doc["requirements"]
    check(len(groups) == 2, f"{set_id}: a Cub rank is two groups, found {len(groups)}")
    core, electives = groups

    # The distinction the trap misses: one group is obligations, the other is a pool.
    check(core.get("choose") is None, f"{set_id}: the required group is not a choose")
    check(electives.get("choose"), f"{set_id}: the elective group must carry a choose")
    check(
        electives["choose"] < len(electives["children"]),
        f"{set_id}: an elective pool must offer more adventures than it requires",
    )

    resolved = {}
    for group in groups:
        refs = [c["ref"] for c in group["children"]]
        # Every child is a ref and nothing else -- that IS the shape of a Cub rank.
        check(all(refs), f"{set_id} group {group['number']}: every child must carry a ref")
        check(
            all(not (c.get("children") or []) for c in group["children"]),
            f"{set_id} group {group['number']}: adventure refs are leaves",
        )
        for ref in refs:
            kind, _, slug = ref.partition(":")
            check(kind == "adventure", f"{set_id}: unexpected ref kind {kind!r}")
            check(slug in adventures, f"{set_id}: {ref} resolves to nothing")
        resolved[group["number"]] = [adventures[r.split(":", 1)[1]] for r in refs]

    core_adv, elective_adv = resolved[core["number"]], resolved[electives["number"]]
    # A required adventure is placed in a program area; electives deliberately are not.
    for adventure in core_adv:
        check(adventure["area"], f"{adventure['id']}: a required adventure must carry an area")
        check(f"rank:{rid}" in adventure["ranks"], f"{adventure['id']} must belong to rank:{rid}")

    owed = len(core_adv) + electives["choose"]
    summary.append((rank, set_id, core_adv, elective_adv, electives["choose"], owed))

# Across the whole program: the naive reading inflates the work by the unchosen electives.
naive_total = sum(len(c) + len(e) for _, _, c, e, _, _ in summary)
owed_total = sum(owed for *_, owed in summary)
check(owed_total < naive_total, "counting the whole elective pool must overstate the work")
check(
    len({len(c) for _, _, c, _, _, _ in summary}) == 1,
    "every Cub rank must require the same number of core adventures",
)

# The rights notice travels with each document, and the six Cub ranks share one.
check(len(rights) == 1, f"the Cub rank sets disagree about text_rights: {len(rights)} variants")

areas = sorted({a["area"] for _, _, core, _, _, _ in summary for a in core})
print(f"program         cub_scouts: {len(summary)} ranks, {len(adventures)} adventures published")
for rank, set_id, core, elective, pick, owed in summary:
    print(f"  {rank['name']:15} {set_id:20} {len(core)} required + {pick} of "
          f"{len(elective):2} electives = {owed}")
print(f"work owed       {owed_total} adventures across the program")
print(f"naive reading   {naive_total} (whole elective pool counted)  <- overstates by "
      f"{naive_total - owed_total}")
print(f"required areas  {', '.join(areas)}")
one = summary[0]
print(f"sample          {one[0]['name']} required: "
      f"{', '.join(a['id'] for a in one[2])}")
print(f"  categories    {', '.join(sorted({a['category'] for a in one[2]}))} (required); "
      f"{', '.join(sorted({a['category'] for a in one[3]}))} (elective)")
print(f"  elective area {sorted({str(a['area']) for a in one[3]})} -- electives carry no area")
print(f"text_rights     {next(iter(rights))}")
