#!/usr/bin/env bash
# Find camps whose source confirmation is more than 12 months old.
#
# TRAP: staleness-checking `imported_at`. That is OUR ingest date -- it moves every time the
#       build runs, so a record copied forward untouched for years looks fresh and the check
#       never fires. `verified_at` is the date a human last confirmed the record against its
#       source, and it is the only field that can make a staleness check mean anything.
# FIX:  compare `verified_at` against a cutoff. Dates are ISO-8601 yyyy-mm-dd, so a plain
#       string compare is a correct date compare -- no parsing needed.
set -euo pipefail

BASE="${OSA_BASE:-https://sethmay.github.io/open-scout-api}"
fetch() { curl -fsSL "$BASE/$1"; }

CAMPS="$(fetch v1/current/camps.json)"

# Cutoff computed once, in the shell, and passed in with --arg: jq's date handling is one of
# the least portable corners of the language and none of it is needed for yyyy-mm-dd.
CUTOFF="$(date -u -d '12 months ago' +%Y-%m-%d 2>/dev/null || date -u -v-12m +%Y-%m-%d)"

echo "  cutoff          $CUTOFF (verified_at before this is stale)"

printf '%s\n' "$CAMPS" | jq -r --arg cutoff "$CUTOFF" '
  [.items[] | select(.verified_at < $cutoff)] | sort_by(.verified_at) | .[]
  | "    \(.verified_at)  \(.state)  \(.id)  (imported \(.imported_at), confidence \(.confidence))"
'

STALE="$(printf '%s\n' "$CAMPS" |
  jq -r --arg cutoff "$CUTOFF" '[.items[] | select(.verified_at < $cutoff)] | length')"

# The same query against imported_at, to show why it cannot substitute: ingest dates cluster
# at the last build, so this number is normally 0 no matter how old the underlying facts are.
IMPORT_STALE="$(printf '%s\n' "$CAMPS" |
  jq -r --arg cutoff "$CUTOFF" '[.items[] | select(.imported_at < $cutoff)] | length')"

echo "  stale by verified_at   $STALE"
echo "  stale by imported_at   $IMPORT_STALE  (wrong field: tracks our build, not the source)"

# The invariant that makes the check trustworthy: every current camp carries a verified_at, so
# a null can never be silently read as "not stale" by the string compare above.
if ! printf '%s\n' "$CAMPS" |
  jq -e 'all(.items[]; .verified_at != null and (.verified_at | length) == 10)' >/dev/null; then
  echo "FAIL: every current camp must carry an ISO-8601 verified_at" >&2
  exit 1
fi

# And provenance must be complete: no camp may claim confirmation it does not date.
if ! printf '%s\n' "$CAMPS" | jq -e 'all(.items[]; .imported_at != null)' >/dev/null; then
  echo "FAIL: every current camp must carry imported_at" >&2
  exit 1
fi
