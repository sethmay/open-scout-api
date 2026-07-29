#!/usr/bin/env bash
# Expand a coarse camp feature code over the vocabulary, then match camps against the closure.
#
# TRAP: `select(.features | any(. == "aquatics"))` finds only the camps we could not describe
#       any better than "has water stuff". Feature codes form a hierarchy through each vocab
#       term's `broader`, and a well-surveyed camp is tagged with the SPECIFIC code -- kayaking,
#       sailing, snorkeling -- so the coarse query quietly misses most of the real matches.
# FIX:  read v1/vocab/camp-features.json, walk `broader` to the transitive closure of the code
#       you were asked about, and match on the whole set. The hierarchy is shallow today, so
#       one pass would usually do -- iterate to a fixed point anyway, because the vocabulary is
#       marked `open` and gaining a third level must not silently change your answers.
set -euo pipefail

BASE="${OSA_BASE:-https://sethmay.github.io/open-scout-api}"
fetch() { curl -fsSL "$BASE/$1"; }

CODE="${1:-aquatics}"

VOCAB="$(fetch v1/vocab/camp-features.json)"
CAMPS="$(fetch v1/current/camps.json)"

# Fixed-point expansion: keep adding terms whose `broader` is already in the set until a pass
# adds nothing. Two iterations for a two-level vocabulary, N+1 for an N-level one.
CLOSURE="[\"$CODE\"]"
PASSES=0
while true; do
  NEXT="$(printf '%s\n' "$VOCAB" | jq -c --argjson have "$CLOSURE" '
    ($have + [.terms[] | . as $t | select($t.broader != null)
              | select(any($have[]; . == $t.broader)) | .code])
    | unique
  ')"
  PASSES=$((PASSES + 1))
  [[ "$NEXT" == "$CLOSURE" ]] && break
  CLOSURE="$NEXT"
done

count_camps() { # $1 = JSON array of codes
  printf '%s\n' "$CAMPS" | jq -r --argjson codes "$1" '
    [.items[] | select(any(.features[]; . as $f | any($codes[]; . == $f)))] | length
  '
}

BARE="$(count_camps "[\"$CODE\"]")"
EXPANDED="$(count_camps "$CLOSURE")"

echo "  code            $CODE"
echo "  closure         $(printf '%s\n' "$CLOSURE" | jq -r 'length') codes after $PASSES passes"
printf '%s\n' "$CLOSURE" | jq -r 'sort_by(.) | .[] | "    \(.)"'
echo "  camps (bare)    $BARE"
echo "  camps (closure) $EXPANDED"

# Semantic assert: the closure must actually contain a known child. A one-line expansion that
# forgot to look at `broader` would still produce a set -- just the wrong one.
if ! printf '%s\n' "$CLOSURE" | jq -e --arg code "$CODE" '
  if $code == "aquatics" then any(.[]; . == "kayaking") else length >= 1 end
' >/dev/null; then
  echo "FAIL: the closure of $CODE must contain its children (expected kayaking under aquatics)" >&2
  exit 1
fi

# And it must buy you something: strictly more camps than the bare code, or the expansion is
# not doing the work the reader thinks it is.
if [[ "$EXPANDED" -le "$BARE" ]]; then
  echo "FAIL: closure matched $EXPANDED camps, bare code matched $BARE; expected strictly more" >&2
  exit 1
fi
