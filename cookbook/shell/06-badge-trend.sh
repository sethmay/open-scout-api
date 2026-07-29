#!/usr/bin/env bash
# Compare one badge's popularity between two years.
#
# TRAP: doing arithmetic on `earned_rank`. Scouting America publishes ORDER, never absolute
#       numbers -- there is not a single earn count anywhere in this dataset. So averaging or
#       summing ranks produces a number with no unit, "rank 1" is not "one badge earned", and
#       a 5-place move near the top is not comparable to a 5-place move near the bottom.
# FIX:  ordinal operations only. Compare, sort, take min/max, report the move as places and
#       as a direction. Check `.metric` before you trust any of it.
set -euo pipefail

BASE="${OSA_BASE:-https://sethmay.github.io/open-scout-api}"
fetch() { curl -fsSL "$BASE/$1"; }

BADGE="${1:-cooking}"
FROM="${2:-2021}"
TO="${3:-2025}"

FROM_DOC="$(fetch "v1/merit-badge-rankings/$FROM.json")"
TO_DOC="$(fetch "v1/merit-badge-rankings/$TO.json")"

rank_of() { # $1 = document, $2 = badge slug
  printf '%s\n' "$1" | jq -r --arg subject "merit-badge:$2" '
    [.rankings[] | select(.subject == $subject) | .rank] | if length == 0 then "" else .[0] end
  '
}

FROM_RANK="$(rank_of "$FROM_DOC" "$BADGE")"
TO_RANK="$(rank_of "$TO_DOC" "$BADGE")"

if [[ -z "$FROM_RANK" || -z "$TO_RANK" ]]; then
  echo "FAIL: merit-badge:$BADGE is not ranked in both $FROM and $TO" >&2
  exit 1
fi

# Both `metric` values must say earned_rank. If a future document ever published counts it
# would say so here, and only then would arithmetic become legitimate.
for DOC in "$FROM_DOC" "$TO_DOC"; do
  if ! printf '%s\n' "$DOC" | jq -e '.metric == "earned_rank"' >/dev/null; then
    echo "FAIL: expected metric == earned_rank; refusing to interpret this document" >&2
    exit 1
  fi
done

# Ordinal completeness: each year's ranks are a dense 1..N with no ties and no gaps. That is
# what makes "moved 3 places" meaningful and what makes a missing badge detectable.
for YEAR in "$FROM:$FROM_DOC" "$TO:$TO_DOC"; do
  DOC="${YEAR#*:}"
  if ! printf '%s\n' "$DOC" | jq -e '
    [.rankings[].rank] as $r
    | ($r | min) == 1 and ($r | max) == ($r | length) and ($r | unique | length) == ($r | length)
  ' >/dev/null; then
    echo "FAIL: ${YEAR%%:*} ranks are not a complete 1..N" >&2
    exit 1
  fi
done

# The move, stated the only way ranks allow: places, and which way. Lower rank is more popular,
# so a smaller number in the later year is a rise.
MOVE=$((FROM_RANK - TO_RANK))
if [[ "$MOVE" -gt 0 ]]; then
  DIRECTION="up $MOVE places"
elif [[ "$MOVE" -lt 0 ]]; then
  DIRECTION="down $((-MOVE)) places"
else
  DIRECTION="unchanged"
fi

summary() { # $1 = document
  printf '%s\n' "$1" | jq -r '
    "\(.rankings | length) ranked (complete: \(.complete), source: \(.source_document.title))"
  '
}

echo "  badge           merit-badge:$BADGE"
echo "  $FROM            rank $FROM_RANK of $(summary "$FROM_DOC")"
echo "  $TO            rank $TO_RANK of $(summary "$TO_DOC")"
echo "  move            $DIRECTION"
echo "  note            ranks are ordinal; the dataset publishes no earn counts to average"
