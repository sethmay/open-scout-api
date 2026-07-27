"""The one rule for how consecutive requirement-set editions abut.

`effective_to` is HALF-OPEN: it holds the date the *successor* took effect, so a window is
[effective_from, effective_to) and `effective_to: null` means still in force. That matches the
schema's own wording ("when a later revision superseded this one") and the half-open convention
entity `versions` already use and `validate_data.py` already enforces there.

It was not always so. Merit-badge and rank editions were generated closing on the last day they
applied (`2023-12-31` followed by `2024-01-01`) while adventure editions closed on the successor's
start date (`2024` followed by `2024`) — 253 abutments in the older style against 83 in the newer.
The schema never said which, which is exactly how two conventions grew in one dataset and why a
consumer could not write a single "which edition applied on date D" predicate. Owner decision,
2026-07-27: half-open everywhere.

Generators call `close_half_open()` on the documents they own; `validate_data.py` enforces the
result, so a generator that forgets is caught rather than quietly reintroducing the old style.
"""

from __future__ import annotations


def close_half_open(docs: list[dict]) -> int:
    """Set each edition's `effective_to` to its successor's `effective_from`, in place.

    The newest edition of a subject is left alone: its `effective_to` is either null (in force) or a
    genuine retirement date, and neither is an abutment.
    """
    by_subject: dict[str, list[dict]] = {}
    for d in docs:
        by_subject.setdefault(d.get("subject"), []).append(d)
    changed = 0
    for sets in by_subject.values():
        sets.sort(key=lambda d: d["effective_from"])
        for prev, nxt in zip(sets, sets[1:]):
            if prev.get("effective_to") != nxt["effective_from"]:
                prev["effective_to"] = nxt["effective_from"]
                changed += 1
    return changed
