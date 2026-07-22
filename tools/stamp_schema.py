"""Stamp every canonical data file with a `$schema` reference to its schema.

The `$schema` value is a pure function of the file's location (councils/ -> council,
_events.json -> event, etc.), so this is the single source of truth for those refs.
Insertion is textual (add one line after the opening brace) so existing formatting is
untouched and the operation is idempotent. Generators call `stamp_tree(<their dir>)`
after writing; `validate_data.py` enforces the result; run `python tools/stamp_schema.py`
to (re)stamp everything, or `--check` to report drift without writing.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"
BASE = "https://sethmay.github.io/open-scout-api/schema/v1/"
KIND_BY_DIR = {
    "councils": "council", "territories": "territory", "merit-badges": "merit-badge",
    "camps": "camp", "ranks": "rank", "awards": "award", "requirement-sets": "requirement-set",
    "oa-lodges": "oa-lodge", "vocab": "vocab",
}


def schema_url_for(path: Path) -> str | None:
    """Expected $schema URL for a data file, or None if it isn't a canonical data file."""
    if path.name == "_events.json":
        return f"{BASE}event.schema.json"
    kind = KIND_BY_DIR.get(path.parent.name)
    return f"{BASE}{kind}.schema.json" if kind else None


def _stamp_text(txt: str, url: str) -> tuple[str, bool]:
    head = txt[:300]
    m = re.search(r'"\$schema"\s*:\s*"([^"]*)"', head)
    if m:
        if m.group(1) == url:
            return txt, False
        return txt[: m.start(1)] + url + txt[m.end(1):], True
    i = txt.index("{")
    nl = txt.index("\n", i)
    return txt[: nl + 1] + f'  "$schema": "{url}",\n' + txt[nl + 1:], True


def _files(root: Path):
    return (p for p in root.rglob("*.json"))


def stamp_tree(root: Path = DATA) -> int:
    changed = 0
    for p in _files(root):
        url = schema_url_for(p)
        if not url:
            continue
        txt = p.read_text(encoding="utf-8")
        new, did = _stamp_text(txt, url)
        if did:
            p.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
    return changed


def check_tree(root: Path = DATA) -> list[str]:
    bad = []
    for p in _files(root):
        url = schema_url_for(p)
        if not url:
            continue
        m = re.search(r'"\$schema"\s*:\s*"([^"]*)"', p.read_text(encoding="utf-8")[:300])
        if not m:
            bad.append(f"{p.relative_to(root.parent)}: missing $schema (expected {url})")
        elif m.group(1) != url:
            bad.append(f"{p.relative_to(root.parent)}: $schema {m.group(1)!r} != {url!r}")
    return bad


def main() -> int:
    if "--check" in sys.argv:
        bad = check_tree()
        for b in bad:
            print(b)
        print(f"{len(bad)} file(s) need stamping" if bad else "all data files carry the correct $schema")
        return 1 if bad else 0
    n = stamp_tree()
    print(f"stamped {n} data file(s) with $schema")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
