"""Expand a coarse camp feature code to everything beneath it.

TRAP: `"aquatics" in camp["features"]` matches almost nothing, so a "camps with water
      activities" filter returns a handful of results and looks like a data gap. Feature codes
      form a hierarchy through each vocab term's `broader`, and camps are tagged with the
      SPECIFIC code they actually offer (`kayaking`), not with the parent.
FIX:  build the child index from `broader`, take the TRANSITIVE closure of the coarse code, and
      match against the closure. Transitive matters: `ice_fishing`'s parent is `fishing`, whose
      parent is `aquatics`, so a one-level lookup still misses it. One namespace holds both the
      coarse and the specific codes, which is why `code` is the only filterable key.
"""

from osa import check, get, items

vocab = get("v1/vocab/camp-features.json")
terms = {t["code"]: t for t in vocab["terms"]}

children: dict[str, list[str]] = {}
for term in vocab["terms"]:
    parent = term.get("broader")
    if parent is not None:
        children.setdefault(parent, []).append(term["code"])

# `broader` names a code in the same vocabulary, so a typo would silently orphan a whole branch.
check(all(p in terms for p in children), "every `broader` must name a term in this vocabulary")


def closure(code: str) -> set[str]:
    """`code` plus every code transitively beneath it.

    The `seen` guard makes this cycle-safe. `broader` is meant to be a forest, but a consumer
    cannot verify that per-request, and an unguarded walk on a cyclic edge never returns.
    """
    out: set[str] = set()
    stack = [code]
    while stack:
        current = stack.pop()
        if current in out:
            continue
        out.add(current)
        stack.extend(children.get(current, ()))
    return out


def ancestors(code: str) -> list[str]:
    """The `broader` chain above `code`, walked upward with the same guard."""
    chain, seen = [], {code}
    parent = terms[code].get("broader")
    while parent is not None and parent not in seen:
        chain.append(parent)
        seen.add(parent)
        parent = terms[parent].get("broader")
    return chain


aquatics = closure("aquatics")
check(aquatics >= {"aquatics", "kayaking", "canoeing"},
      "aquatics closure must contain its children")
# The reason the closure has to be transitive rather than one level of `broader`.
check("ice_fishing" in aquatics, "a grandchild must appear in the closure")
check(terms["ice_fishing"]["broader"] != "aquatics", "ice_fishing hangs off aquatics indirectly")
check(ancestors("ice_fishing")[-1] == "aquatics", "ice_fishing's chain must reach aquatics")
# Acyclicity, proved for every term rather than assumed: an upward walk must leave the set it
# started in, so the last ancestor is a root with no `broader` of its own.
for code in terms:
    chain = ancestors(code)
    check(code not in chain, f"{code} is its own ancestor")
    check(not chain or terms[chain[-1]].get("broader") is None,
          f"{code}'s chain must end at a root")

camps = items("v1/current/camps.json")
# Every code a camp carries must exist in the vocabulary, or the closure match is meaningless.
tagged = {code for c in camps for code in c["features"]}
check(tagged <= set(terms), f"unknown feature codes: {sorted(tagged - set(terms))[:3]}")

exact = [c for c in camps if "aquatics" in c["features"]]
matched = [c for c in camps if aquatics & set(c["features"])]
check(len(matched) >= len(exact), "the closure can only ever match more camps than the bare code")
# If those two were equal the hierarchy would be decoration; the gap is the whole lesson.
check(len(matched) > len(exact), "camps are tagged with specific codes, so the closure must win")

leaves = sorted(aquatics - {"aquatics"}, key=lambda c: -sum(1 for x in camps if c in x["features"]))
top = [(c, sum(1 for x in camps if c in x["features"])) for c in leaves[:5]]
deepest = max(terms, key=lambda c: len(ancestors(c)))

print(f"vocabulary      {vocab['id']}: {len(terms)} terms, {len(children)} with children")
print(f"aquatics        expands to {len(aquatics)} codes ({len(children['aquatics'])} direct)")
print(f"deepest chain   {deepest} -> {' -> '.join(ancestors(deepest)) or '(root)'}")
print(f"bare code       {len(exact)} camps carry \"aquatics\" itself")
print(f"closure match   {len(matched)} camps carry something in the closure")
print(f"top codes       {', '.join(f'{c}={n}' for c, n in top)}")
print(f"missed by trap  {len(matched) - len(exact)} camps a bare `in features` check drops")
