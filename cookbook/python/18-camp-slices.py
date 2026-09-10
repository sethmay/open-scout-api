"""Pull one narrow cut of the camps instead of the whole corpus.

TRAP: fetching `current/camps.json` (hundreds of KB, ~167k tokens) to answer "camps in Oregon"
      or "camps in this council" -- then filtering client-side, or worse, handing the whole thing
      to a model that cannot hold it. The corpus is the wrong unit for a per-state or per-council
      question.
FIX:  read `meta.camp_slices`, which indexes the counts for every published slice, then fetch the
      one file you need: `v1/camps/by-state/<USPS>.json` or `v1/camps/by-council/<slug>.json`.
      Each slice has the SAME envelope and item shape as `current/camps.json`, just filtered, so
      existing code reads it unchanged.
"""

from osa import check, endpoint, get, items, meta

slices = meta()["camp_slices"]
check(slices["by_state"] and slices["by_council"], "meta must index the state and council slices")

# The whole corpus, fetched once, only to prove each slice is a faithful, smaller subset of it.
corpus = items("v1/current/camps.json")
by_state_ids: dict[str, list[str]] = {}
by_council_ids: dict[str, list[str]] = {}
for c in corpus:
    if c["state"]:
        by_state_ids.setdefault(c["state"], []).append(c["id"])
    if c["council"]:
        by_council_ids.setdefault(c["council"].split(":", 1)[1], []).append(c["id"])

state_tpl = endpoint("v1/camps/by-state/{state}.json")
council_tpl = endpoint("v1/camps/by-council/{id}.json")

# One state slice: same shape as the corpus, equal to the corpus's subset, and much smaller.
st = "OR"
or_slice = items(state_tpl.format(state=st))
check(sorted(c["id"] for c in or_slice) == sorted(by_state_ids[st]),
      f"by-state/{st} must be exactly the {st} camps in the corpus")
check(len(or_slice) == slices["by_state"][st], f"meta.camp_slices.by_state[{st}] must match the file")
check(len(or_slice) < len(corpus), "a state slice must be smaller than the whole corpus")
check(all(c["state"] == st for c in or_slice), f"every camp in the {st} slice must be in {st}")

# One council slice: every camp resolves to that council, and matches the corpus subset.
slug = "grand-canyon"
gc = items(council_tpl.format(id=slug))
check(all(c["council"] == f"council:{slug}" for c in gc), "a council slice holds one council only")
check(sorted(c["id"] for c in gc) == sorted(by_council_ids[slug]),
      f"by-council/{slug} must be exactly that council's camps")

# The published index is trustworthy corpus-wide: the state slices partition every camp that has a
# state, and the council slices every camp that has a council. A drifted index is a silent gap.
check(sum(slices["by_state"].values()) == sum(1 for c in corpus if c["state"]),
      "the by_state index must cover every camp with a state, once")
check(sum(slices["by_council"].values()) == sum(1 for c in corpus if c["council"]),
      "the by_council index must cover every camp with a council, once")
check(slices["by_state"] == {s: len(v) for s, v in by_state_ids.items()},
      "every by_state count must match the corpus")
check(slices["by_council"] == {s: len(v) for s, v in by_council_ids.items()},
      "every by_council count must match the corpus")

print(f"corpus          {len(corpus)} camps in current/camps.json")
print(f"slices indexed  {len(slices['by_state'])} states, {len(slices['by_council'])} councils (meta.camp_slices)")
print(f"by-state/{st}     {len(or_slice)} camps -- fetch this, not the corpus")
print(f"by-council/{slug}  {len(gc)} camps: {', '.join(sorted(c['id'] for c in gc))}")
