"""Compile the canonical data/ tree into a single queryable SQLite artifact.

Emits dist/v1/open-scout-api.sqlite: one typed table per dataset (mirroring the flat
`current` projection columns) plus a `data` column holding the full canonical JSON of each
entity (query it with SQLite's json_extract). Requirement-sets and lifecycle events get
their own tables; a `meta` table records the version + counts. Pure stdlib (sqlite3, json).

Run after tools/build.py in the release/CI flow. `current` = the entity has an open
(valid_to:null) version; for retired entities the newest version's attributes are used.
"""
from __future__ import annotations

import json
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DIST = ROOT / "dist"
OUT = DIST / "v1" / "open-scout-api.sqlite"

# dataset dir -> (table name, [(column, sql_type, json_key_in_version)])
ENTITY_TABLES = {
    "councils": ("councils", [("number", "INTEGER", "number"), ("state", "TEXT", "state"),
                              ("hq_city", "TEXT", "hq_city")]),
    "territories": ("territories", [("number", "INTEGER", "number"),
                                    ("division_type", "TEXT", "division_type")]),
    "merit-badges": ("merit_badges", [("eagle_required", "INTEGER", "eagle_required")]),
    "camps": ("camps", [("camp_type", "TEXT", "camp_type"), ("operator", "TEXT", "operator"),
                        ("council", "TEXT", "council"), ("state", "TEXT", "state")]),
    "ranks": ("ranks", [("program", "TEXT", "program"), ("rank_order", "INTEGER", "order")]),
    "awards": ("awards", [("category", "TEXT", "category"), ("audience", "TEXT", "audience"),
                          ("square_knot_no", "TEXT", "square_knot_no")]),
}


def read_json(p: Path):
    return json.loads(p.read_text("utf-8"))


def current_version() -> str:
    text = (ROOT / "CHANGELOG.md").read_text("utf-8")
    m = re.search(r"##\s+(\d+\.\d+\.\d+)\b", text)
    if not m:
        raise RuntimeError("no version heading in CHANGELOG.md")
    v = m.group(1)
    return v + "+unreleased" if re.search(r"^-\s+`PENDING`", text, re.M) else v


def open_version(entity: dict) -> dict | None:
    for v in entity.get("versions", []):
        if v.get("valid_to") is None:
            return v
    return None


def _as_int(v):
    return int(v) if isinstance(v, bool) else v


def main() -> None:
    if not OUT.parent.exists():
        raise SystemExit(f"{OUT.parent} missing — run tools/build.py first")
    if OUT.exists():
        OUT.unlink()
    con = sqlite3.connect(OUT)
    cur = con.cursor()
    cur.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    counts: dict[str, int] = {}

    for dsdir, (table, extra) in ENTITY_TABLES.items():
        cols = ["id TEXT PRIMARY KEY", "name TEXT", "current INTEGER"]
        cols += [f'"{c}" {t}' for c, t, _ in extra]
        cols.append("data TEXT")
        cur.execute(f"CREATE TABLE {table} ({', '.join(cols)})")
        rows = []
        for p in sorted((DATA / dsdir).glob("*.json")):
            if p.name == "_events.json":
                continue
            e = read_json(p)
            ov = open_version(e)
            v = ov or (e.get("versions") or [{}])[-1]
            row = [e["id"], v.get("name"), 1 if ov else 0]
            row += [_as_int(v.get(key)) for _, _, key in extra]
            row.append(json.dumps(e, ensure_ascii=False))
            rows.append(row)
        ph = ", ".join("?" * (3 + len(extra) + 1))
        cur.executemany(f"INSERT INTO {table} VALUES ({ph})", rows)
        cur.execute(f"CREATE INDEX idx_{table}_current ON {table}(current)")
        counts[table] = len(rows)

    # requirement-sets (immutable dated documents)
    cur.execute("CREATE TABLE requirement_sets (id TEXT PRIMARY KEY, subject TEXT, "
                "effective_from TEXT, effective_to TEXT, includes_official_text INTEGER, "
                "supersedes TEXT, data TEXT)")
    rs_dir = DATA / "requirement-sets"
    rs_rows = []
    if rs_dir.exists():
        for p in sorted(rs_dir.glob("*.json")):
            d = read_json(p)
            rs_rows.append([d["id"], d.get("subject"), d.get("effective_from"),
                            d.get("effective_to"), 1 if d.get("includes_official_text") else 0,
                            d.get("supersedes"), json.dumps(d, ensure_ascii=False)])
    cur.executemany("INSERT INTO requirement_sets VALUES (?,?,?,?,?,?,?)", rs_rows)
    cur.execute("CREATE INDEX idx_rs_subject ON requirement_sets(subject)")
    cur.execute("CREATE INDEX idx_rs_current ON requirement_sets(effective_to)")
    counts["requirement_sets"] = len(rs_rows)

    # lifecycle events (one row per event, tagged with its dataset)
    cur.execute("CREATE TABLE events (dataset TEXT, id TEXT, type TEXT, date TEXT, data TEXT)")
    ev_rows = []
    for dsdir in ENTITY_TABLES:
        ep = DATA / dsdir / "_events.json"
        if ep.exists():
            for e in read_json(ep).get("events", []):
                ev_rows.append([dsdir, e.get("id"), e.get("type"), e.get("date"),
                                json.dumps(e, ensure_ascii=False)])
    cur.executemany("INSERT INTO events VALUES (?,?,?,?,?)", ev_rows)
    cur.execute("CREATE INDEX idx_events_id ON events(id)")
    counts["events"] = len(ev_rows)

    version = current_version()
    meta = {"name": "Open Scout API", "version": version,
            "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            "source": "https://github.com/sethmay/open-scout-api", **{f"count_{k}": v for k, v in counts.items()}}
    cur.executemany("INSERT INTO meta VALUES (?, ?)", [(k, str(v)) for k, v in meta.items()])
    con.commit()
    con.close()
    total = sum(counts.values())
    print(f"built {OUT.relative_to(ROOT)} v{version}: {total} rows across "
          f"{len(ENTITY_TABLES) + 2} tables ({', '.join(f'{k}={v}' for k, v in counts.items())})")


if __name__ == "__main__":
    main()
