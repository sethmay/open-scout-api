#!/usr/bin/env bash
# Resolve a retired camp id through the alias map before giving up on a 404.
#
# TRAP: an id you stored last season now 404s, and the obvious conclusion -- the camp closed --
#       is usually wrong. Duplicate listings get merged as the data improves, and the losing id
#       is retired rather than deleted. Treating 404 as "gone" drops live camps out of your app.
#       The second trap is stopping after one hop: the map is emitted one camp at a time and is
#       NOT transitively closed, so a merge target that was itself later merged away leaves a
#       value that is another key -- and one hop lands on an id that still 404s.
# FIX:  on a miss, look the id up in v1/camps/aliases.json and follow the map TRANSITIVELY,
#       until you reach an id the API actually publishes. Note the shape: that file is a BARE
#       map of old-id -> current-id, with no envelope, no `count` and no `$schema`, so
#       `.items[]` gets you nothing. Index it directly.
set -euo pipefail

BASE="${OSA_BASE:-https://sethmay.github.io/open-scout-api}"
fetch() { curl -fsSL "$BASE/$1"; }

RETIRED="${1:-az-scouts-bsa-weekend-camp-2026-new}"

ALIASES="$(fetch v1/camps/aliases.json)"
INDEX="$(fetch v1/camps/index.json)"

# The bare map has no envelope, so `length` counts entries and `keys` lists the retired ids.
COUNT="$(printf '%s\n' "$ALIASES" | jq -r 'length')"
echo "  alias map       $COUNT retired ids, no envelope"

# The ids the API actually publishes, as an object so jq can `has` them without a linear scan.
# This is the set resolution has to terminate on; an alias VALUE is not required to be in it.
LIVE="$(printf '%s\n' "$INDEX" | jq -c '[.items[].id | {key: ., value: true}] | from_entries')"

# One definition of resolution, shared by the lookup and the map-wide invariant below.
# `until` walks the chain instead of taking a single hop, and `seen` bounds the walk by the size
# of the map, so a cycle in the data yields null rather than hanging a request. A null is a real
# 404, not a merge, and must not be reported as one.
RESOLVE='
def resolve($m; $live):
  {id: ., seen: {}}
  | until(.id as $c | ($live | has($c)) or (.seen | has($c)) or (($m | has($c)) | not);
          .id as $c | {id: $m[$c], seen: (.seen + {($c): true})})
  | .id as $c | if ($live | has($c)) then $c else null end;
'

# The lookup itself. `has` first, because indexing an absent key yields null, and a null id
# would go on to build the URL "$BASE/v1/camps/null.json" -- a 404 blamed on the wrong thing.
if ! printf '%s\n' "$ALIASES" | jq -e --arg id "$RETIRED" 'has($id)' >/dev/null; then
  echo "FAIL: $RETIRED is not in the alias map" >&2
  exit 1
fi

# Bind the map to $m before calling: jq evaluates a function argument in the caller's context,
# and by then `.` is the id being resolved, not the map.
CURRENT="$(printf '%s\n' "$ALIASES" | jq -r --arg id "$RETIRED" --argjson live "$LIVE" "$RESOLVE"'
  . as $m | ($id | resolve($m; $live)) // ""
')"

if [[ -z "$CURRENT" ]]; then
  echo "FAIL: $RETIRED is in the alias map but no chain from it reaches a published camp" >&2
  exit 1
fi

# How many redirects point at another redirect, i.e. need the walk rather than one hop. Note
# `.value` has to be captured into $v first -- inside has(), `.` is still the map, not the entry.
CHAINED="$(printf '%s\n' "$ALIASES" | jq -r '
  . as $m | ([to_entries[] | .value as $v | select($m | has($v))] | length)
')"

echo "  requested       $RETIRED"
echo "  resolves to     $CURRENT"
echo "  chained         $CHAINED of $COUNT need a transitive hop"

# The two namespaces must stay disjoint: a retired id that the API also publishes would make the
# redirect shadow a real record, so a lookup would have two valid answers.
SHADOWED="$(printf '%s\n' "$ALIASES" | jq -r --argjson live "$LIVE" '
  [keys_unsorted[] | . as $k | select($live | has($k))] | join(" ")
')"
if [[ -n "$SHADOWED" ]]; then
  echo "FAIL: these retired ids are also published camps: $SHADOWED" >&2
  exit 1
fi

# Cycle-freedom AND referential integrity in one pass, and the only referential rule there is:
# every retired id must end up somewhere published. resolve returns null both for a chain that
# runs off the end of the map and for one that loops, so the guard turns a cycle in the data
# into this failed assertion rather than a hung request.
UNRESOLVED="$(printf '%s\n' "$ALIASES" | jq -r --argjson live "$LIVE" "$RESOLVE"'
  . as $m | [keys_unsorted[] | . as $k | select(($k | resolve($m; $live)) == null)] | join(" ")
')"
if [[ -n "$UNRESOLVED" ]]; then
  echo "FAIL: these aliases do not terminate on a published camp: $UNRESOLVED" >&2
  exit 1
fi

# Having resolved it, fetch the document the retired id could never have reached. The fetch is
# its own assignment, not an argument: a command substitution inside `printf ...` would leave
# printf's exit status to mask curl's, so a 404 here would print nothing and still exit 0.
DOC="$(fetch "v1/camps/$CURRENT.json")"
printf '%s\n' "$DOC" | jq -r '
  "  kind            \(.kind)",
  "  versions        \(.versions | length)",
  "  current name    \([.versions[] | select(.valid_to == null) | .name] | .[0])"
'
