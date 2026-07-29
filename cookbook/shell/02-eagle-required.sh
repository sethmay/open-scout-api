#!/usr/bin/env bash
# List the Eagle-required merit badges, and keep "unknown" out of "not required".
#
# TRAP: `select(.eagle_required == false)` looks like the complement of the required list, but
#       it silently drops every historical badge, whose `eagle_required` is null. null means
#       UNKNOWN here, not false: we simply have no sourced answer for a badge discontinued
#       decades ago. Treat null as false and you assert a fact about history you cannot back.
# FIX:  the flag is TRI-STATE. Branch on true / false / null and say "unknown" out loud.
set -euo pipefail

BASE="${OSA_BASE:-https://sethmay.github.io/open-scout-api}"
fetch() { curl -fsSL "$BASE/$1"; }

BADGES="$(fetch v1/merit-badges/index.json)"

# The split is the whole lesson: three buckets, and the null bucket is not empty.
# group_by keeps null as its own group, which is exactly the distinction we want to see.
echo "  eagle_required split"
printf '%s\n' "$BADGES" | jq -r '
  [.items[] | .eagle_required] | group_by(.) | .[]
  | "    \(if .[0] == null then "null (unknown)" else .[0] end): \(length)"
'

# The 18 badges Star and Life cite. Note this is NOT the 14-slot Eagle requirement graph --
# requirement 3 of the Eagle rank has 14 slots, three of them either/or. Different number.
echo "  eagle-required badges"
printf '%s\n' "$BADGES" | jq -r '
  [.items[] | select(.eagle_required == true) | .name] | sort_by(.) | .[] | "    \(.)"
'

UNKNOWN="$(printf '%s\n' "$BADGES" | jq -r '[.items[] | select(.eagle_required == null)] | length')"
# Same query written the naive way, to show what the tri-state costs you if you ignore it.
NOT_REQUIRED="$(printf '%s\n' "$BADGES" |
  jq -r '[.items[] | select(.eagle_required == false)] | length')"

if [[ "$UNKNOWN" -lt 1 ]]; then
  echo "FAIL: expected badges with eagle_required == null; the tri-state is the point" >&2
  exit 1
fi

# Why null is safe to leave unknown: nothing null is a current badge, so a consumer filtering
# on `current` never has to decide. Any current badge with a null flag is a data defect.
if ! printf '%s\n' "$BADGES" |
  jq -e 'all(.items[] | select(.eagle_required == null); .current == false)' >/dev/null; then
  echo "FAIL: a current badge has eagle_required == null; the flag must be sourced" >&2
  exit 1
fi

echo "  unknown badges  $UNKNOWN (all historical) -- misfiled as 'not required' they would"
echo "                  inflate that bucket from $NOT_REQUIRED to $((NOT_REQUIRED + UNKNOWN))"
