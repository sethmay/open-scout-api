#!/usr/bin/env bash
# Discover the API surface from v1/meta.json instead of guessing paths.
#
# TRAP: pasting the provisional host into a script and hand-writing paths under it. The
#       published host is expected to move before 1.0, and a guessed path such as
#       v1/current/positions.json 404s -- which curl without -f reports as an empty result,
#       so the bug reads as "no positions" rather than as a broken URL.
# FIX:  take the base from configuration and read every path out of the discovery document.
#       meta.json publishes dataset totals and the endpoint list, templates included.
set -euo pipefail

BASE="${OSA_BASE:-https://sethmay.github.io/open-scout-api}"
fetch() { curl -fsSL "$BASE/$1"; }

META="$(fetch v1/meta.json)"

# Datasets: `total` counts every version of every entity, `current` only the in-force ones.
# A dataset with no `current` key is not versioned, so total is the only number that exists.
# Padding stays inside jq: piping jq into a `while read` loop would split on whitespace in the
# values and is the usual way this table quietly loses a column.
printf '%s\n' "$META" | jq -r '
  def pad($s; $w): " " * ($w - ($s | length)) + $s;
  "  dataset                    total   current",
  (.datasets | to_entries | sort_by(.key) | .[]
   | (if .value | has("current") then .value.current else "-" end) as $cur
   | "  \(.key)\(" " * (25 - (.key | length)))"
     + pad("\(.value.total)"; 6) + "  " + pad("\($cur)"; 8))
'

# Templated endpoints carry their placeholders verbatim, e.g. v1/councils/{id}.json. Build
# per-entity URLs by substituting into the published template, never by inventing a layout.
printf '%s\n' "$META" | jq -r '
  "  version         \(.version) (generated \(.generated_at))",
  "  endpoints       \([.endpoints[] | select((. | contains("{")) | not)] | length) collections"
    + " + \([.endpoints[] | select(. | contains("{"))] | length) templated",
  "  vocabularies    \(.vocab | length)",
  "  license         \(.license)",
  "  text_rights     \(.text_rights)"
'

# `unofficial` is const:true in the published contract so no consumer can read a subset of
# this document and lose the no-affiliation fact. If it is ever absent, stop.
if ! printf '%s\n' "$META" | jq -e '.unofficial == true' >/dev/null; then
  echo "FAIL: meta.json must assert unofficial == true" >&2
  exit 1
fi

# An empty endpoint list would mean discovery silently degrades back to guessing.
if ! printf '%s\n' "$META" |
  jq -e '(.endpoints | length) >= 1 and (.vocab | length) >= 1' >/dev/null; then
  echo "FAIL: meta.json must publish endpoints and vocabularies" >&2
  exit 1
fi

echo "  ok              discovery document is self-describing and marked unofficial"
