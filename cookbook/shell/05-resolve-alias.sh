#!/usr/bin/env bash
# Resolve a retired camp id through the alias map before giving up on a 404.
#
# TRAP: an id you stored last season now 404s, and the obvious conclusion -- the camp closed --
#       is usually wrong. Duplicate listings get merged as the data improves, and the losing id
#       is retired rather than deleted. Treating 404 as "gone" drops live camps out of your app.
# FIX:  on a miss, look the id up in v1/camps/aliases.json and retry with the value. Note the
#       shape: that file is a BARE map of old-id -> current-id, with no envelope, no `count`
#       and no `$schema`, so `.items[]` gets you nothing. Index it directly.
set -euo pipefail

BASE="${OSA_BASE:-https://sethmay.github.io/open-scout-api}"
fetch() { curl -fsSL "$BASE/$1"; }

RETIRED="${1:-az-scouts-bsa-weekend-camp-2026-new}"

ALIASES="$(fetch v1/camps/aliases.json)"
INDEX="$(fetch v1/camps/index.json)"

# The bare map has no envelope, so `length` counts entries and `keys` lists the retired ids.
echo "  alias map       $(printf '%s\n' "$ALIASES" | jq -r 'length') retired ids, no envelope"

# The lookup itself. `has` first, because indexing an absent key yields null, and a null id
# would go on to build the URL "$BASE/v1/camps/null.json" -- a 404 blamed on the wrong thing.
CURRENT="$(printf '%s\n' "$ALIASES" | jq -r --arg id "$RETIRED" '
  if has($id) then .[$id] else "" end
')"

if [[ -z "$CURRENT" ]]; then
  echo "FAIL: $RETIRED is not in the alias map" >&2
  exit 1
fi

echo "  requested       $RETIRED"
echo "  resolves to     $CURRENT"

# Referential integrity is what makes the retry safe: the target must be a live camp, or the
# alias map is just a second way to 404.
if ! printf '%s\n' "$INDEX" |
  jq -e --arg id "$CURRENT" 'any(.items[]; .id == $id)' >/dev/null; then
  echo "FAIL: alias target $CURRENT is not present in v1/camps/index.json" >&2
  exit 1
fi

# And no alias may point at another alias: one hop must always be enough. Note `.value` has to
# be captured into $v first -- inside has(), `.` is still the map, not the entry.
if ! printf '%s\n' "$ALIASES" | jq -e '
  . as $m | ([to_entries[] | .value as $v | select($m | has($v))] | length) == 0
' >/dev/null; then
  echo "FAIL: an alias points at another alias; resolution must terminate in one hop" >&2
  exit 1
fi

# Having resolved it, fetch the document the retired id could never have reached.
printf '%s\n' "$(fetch "v1/camps/$CURRENT.json")" | jq -r '
  "  kind            \(.kind)",
  "  versions        \(.versions | length)",
  "  current name    \([.versions[] | select(.valid_to == null) | .name] | .[0])"
'
