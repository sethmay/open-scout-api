"""Follow a retired camp id's tombstone to the camp that survived, instead of reading a 404.

TRAP: a stored bookmark or a citation points at a camp id that was later merged away. A consumer
      that treats a missing per-entity document as "gone" drops it; one that assumes the id's
      document is a live camp record reads a stub as a camp.
FIX:  a retired camp id no longer 404s -- it serves a TOMBSTONE, `{ "gone": true, "moved_to": ... }`,
      at the same `v1/camps/<id>.json` URL. `gone` is what tells a tombstone from a live document.
      `moved_to` is ONE hop (it mirrors the aliases map), so follow it transitively: a merge target
      can itself be merged away, and the chain terminates at a live camp.
"""

from osa import check, endpoint, get, items

aliases = get(endpoint("v1/camps/aliases.json"))
live = {c["id"] for c in items("v1/current/camps.json")}

check(aliases, "there must be retired ids to demonstrate")


def doc(camp_id):
    return get(endpoint("v1/camps/{id}.json").format(id=camp_id))


def follow(camp_id):
    """Resolve a possibly-retired id to a live camp document by following tombstones."""
    seen = set()
    d = doc(camp_id)
    while d.get("gone"):
        check(d["id"] not in seen, f"tombstone chain must not cycle at {d['id']}")
        seen.add(d["id"])
        d = doc(d["moved_to"])
    return d


# Every retired id serves a tombstone at its own URL -- the id keeps a document, it is not deleted.
missing = [rid for rid in aliases if "gone" not in doc(rid)]
check(missing == [], f"these retired ids do not serve a tombstone: {missing[:3]}")

# A tombstone is exactly {$schema, id, gone:true, moved_to}; gone is what marks it.
rid = sorted(aliases)[0]
t = doc(rid)
check(t["gone"] is True, "a tombstone is marked gone:true")
check(t["moved_to"] == aliases[rid], "moved_to mirrors the aliases map (one hop)")
check(set(t) == {"$schema", "id", "gone", "moved_to"}, "a tombstone carries no live-camp fields")

# The forward terminates on a real, live camp -- follow transitively, never one hop.
survivor = follow(rid)
check("gone" not in survivor, "the chain ends on a live camp document, not another tombstone")
check(survivor["id"] in live, "the surviving camp is in current/camps.json")

# A live camp is NOT a tombstone: the two shapes never collide at the same URL.
some_live = sorted(live)[0]
check("gone" not in doc(some_live), "a live camp document has no gone flag")

# Every tombstone forwards, transitively, to a live camp (referential integrity + cycle-freedom).
unresolved = [k for k in aliases if follow(k)["id"] not in live]
check(unresolved == [], f"these tombstones do not forward to a live camp: {unresolved[:3]}")

print(f"tombstones      {len(aliases)} retired camp ids each serve a forward")
print(f"retired id      {rid}")
print(f"  gone          {t['gone']}")
print(f"  moved_to      {t['moved_to']}  (one hop)")
print(f"  survivor      {survivor['id']} ({survivor['versions'][-1]['name']})")
print(f"live camp       {some_live} -> has gone flag: {'gone' in doc(some_live)}")
print(f"invariants      {len(aliases)} tombstones, all forward to a live camp; 0 cycles")
