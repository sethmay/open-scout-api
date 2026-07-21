"""Build the published static API into dist/ for GitHub Pages.

Layout (served at https://sethmay.github.io/open-scout-api/):
  dist/
    index.html                     landing page
    schema/v1/*.schema.json        copied canonical + published schemas (matches $id)
    v1/
      meta.json                    version, counts, license, disclaimer
      councils/index.json          lightweight listing of all council entities
      councils/<slug>.json         per-entity: canonical entity + folded lifecycle events
      territories/index.json
      territories/<slug>.json
      current/councils.json        denormalized, current-only (open valid_to) councils
      current/territories.json

Canonical data stays normalized in data/; this build denormalizes for consumers.
The build validates its own current/ projections against
schema/v1/published-current.schema.json (fail-fast) and checks referential
integrity of the projected territory refs. Run after validate_data.py.

Usage: python tools/build.py   ->   writes dist/
"""

from __future__ import annotations

import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SCHEMA_DIR = ROOT / "schema" / "v1"
DIST = ROOT / "dist"
BASE_URL = "https://sethmay.github.io/open-scout-api"
LICENSE = "CC-BY-NC-SA-4.0"
DISCLAIMER = ("Unofficial community project. Not affiliated with, endorsed by, or "
              "sponsored by Scouting America. Confirm facts against each council's own site.")


def read_json(p: Path):
    return json.loads(p.read_text("utf-8"))


def write_json(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


def current_version() -> str:
    for line in (ROOT / "CHANGELOG.md").read_text("utf-8").splitlines():
        m = re.match(r"##\s+(\d+\.\d+\.\d+)\b", line)
        if m:
            return m.group(1)
    raise RuntimeError("no version heading in CHANGELOG.md")


def open_version(entity: dict) -> dict | None:
    """The current (valid_to:null) version, or None if the entity is retired."""
    for v in entity.get("versions", []):
        if v.get("valid_to") is None:
            return v
    return None


def load_dataset(name: str) -> tuple[list[dict], list[dict]]:
    d = DATA / name
    entities = [read_json(p) for p in sorted(d.glob("*.json")) if p.name != "_events.json"]
    events = read_json(d / "_events.json")["events"] if (d / "_events.json").exists() else []
    return entities, events


def events_for(ref: str, events: list[dict]) -> list[dict]:
    return [e for e in events if any(p.get("ref") == ref for p in e.get("participants", []))]


def main() -> None:
    version = current_version()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    if DIST.exists():
        shutil.rmtree(DIST)

    # schemas (served at /schema/v1/ to match every schema's $id)
    schema_out = DIST / "schema" / "v1"
    schema_out.mkdir(parents=True, exist_ok=True)
    for p in SCHEMA_DIR.glob("*.schema.json"):
        shutil.copyfile(p, schema_out / p.name)

    pub = read_json(SCHEMA_DIR / "published-current.schema.json")
    council_item = Draft202012Validator({**pub, "$ref": "#/$defs/CurrentCouncil"},
                                         format_checker=Draft202012Validator.FORMAT_CHECKER)
    terr_item = Draft202012Validator({**pub, "$ref": "#/$defs/CurrentTerritory"},
                                     format_checker=Draft202012Validator.FORMAT_CHECKER)

    councils, cevents = load_dataset("councils")
    territories, tevents = load_dataset("territories")

    # --- territories: per-entity + index + current -------------------------
    current_terr_ids: set[str] = set()
    terr_index = []
    current_territories = []
    for e in territories:
        ref = f"territory:{e['id']}"
        write_json(DIST / "v1" / "territories" / f"{e['id']}.json", {**e, "events": events_for(ref, tevents)})
        ov = open_version(e)
        terr_index.append({"id": e["id"], "name": (ov or e["versions"][-1])["name"],
                           "current": ov is not None})
        if ov is not None:
            current_terr_ids.add(e["id"])
            current_territories.append({"id": e["id"], "number": ov.get("number"),
                                        "name": ov["name"], "division_type": ov["division_type"],
                                        "confidence": ov["provenance"]["confidence"]})

    # --- councils: per-entity + index + current ----------------------------
    council_index = []
    current_councils = []
    errs: list[str] = []
    for e in councils:
        ref = f"council:{e['id']}"
        write_json(DIST / "v1" / "councils" / f"{e['id']}.json", {**e, "events": events_for(ref, cevents)})
        ov = open_version(e)
        council_index.append({"id": e["id"], "name": (ov or e["versions"][-1])["name"],
                              "bsa_number": (ov or e["versions"][-1]).get("bsa_number"),
                              "hq_state": (ov or e["versions"][-1]).get("hq_state"),
                              "territory": (ov or e["versions"][-1]).get("territory"),
                              "current": ov is not None})
        if ov is None:
            continue
        terr_ref = ov.get("territory")
        tnum = None
        if terr_ref is not None:
            tslug = terr_ref.split(":", 1)[1]
            if tslug not in current_terr_ids:
                errs.append(f"council {e['id']}: territory {terr_ref} is not a current territory")
            m = re.match(r"cst-(\d+)$", tslug)
            tnum = int(m.group(1)) if m else None
        current_councils.append({"id": e["id"], "name": ov["name"], "bsa_number": ov.get("bsa_number"),
                                 "hq_city": ov.get("hq_city"), "hq_state": ov.get("hq_state"),
                                 "website": ov.get("website"), "territory": terr_ref,
                                 "territory_number": tnum, "confidence": ov["provenance"]["confidence"]})

    # validate current projections against the published contract (fail-fast)
    for c in current_councils:
        errs += [f"current council {c['id']}: {er.message}" for er in council_item.iter_errors(c)]
    for t in current_territories:
        errs += [f"current territory {t['id']}: {er.message}" for er in terr_item.iter_errors(t)]
    if errs:
        raise SystemExit("build failed:\n  " + "\n  ".join(errs[:50]))

    coll = lambda kind, items: {"version": version, "generated_at": now, "kind": kind,
                                "count": len(items), "items": items}
    write_json(DIST / "v1" / "current" / "councils.json", coll("council", current_councils))
    write_json(DIST / "v1" / "current" / "territories.json", coll("territory", current_territories))
    write_json(DIST / "v1" / "councils" / "index.json", coll("council", council_index))
    write_json(DIST / "v1" / "territories" / "index.json", coll("territory", terr_index))

    write_json(DIST / "v1" / "meta.json", {
        "name": "Open Scout API", "version": version, "generated_at": now,
        "base_url": BASE_URL, "license": LICENSE, "unofficial": True, "disclaimer": DISCLAIMER,
        "schemas": f"{BASE_URL}/schema/v1/",
        "datasets": {
            "councils": {"total": len(councils), "current": len(current_councils)},
            "territories": {"total": len(territories), "current": len(current_territories)},
        },
        "endpoints": ["v1/meta.json", "v1/councils/index.json", "v1/councils/{id}.json",
                      "v1/territories/index.json", "v1/territories/{id}.json",
                      "v1/current/councils.json", "v1/current/territories.json"],
    })

    (DIST / "index.html").write_text(_landing(version, now, len(current_councils), len(current_territories)),
                                     encoding="utf-8", newline="\n")
    print(f"built dist/ v{version}: {len(councils)} councils ({len(current_councils)} current), "
          f"{len(territories)} territories ({len(current_territories)} current)")


def _landing(version, now, ncouncils, nterr) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Open Scout API</title>
<style>
 body{{font:16px/1.6 system-ui,sans-serif;max-width:52rem;margin:2rem auto;padding:0 1rem;color:#1b2a1b}}
 code{{background:#eef2ee;padding:.1em .35em;border-radius:.25em}}
 a{{color:#2f6b2f}} h1{{margin-bottom:.2em}} .muted{{color:#5a6b5a}}
 li{{margin:.25em 0}}
</style></head><body>
<h1>Open Scout API</h1>
<p class="muted">Open, versioned, machine-readable Scouting America reference data. v{version} &middot; built {now}</p>
<p><strong>Unofficial community project.</strong> Not affiliated with, endorsed by, or sponsored by
Scouting America. Data licensed <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>.</p>
<h2>Datasets</h2>
<p>{ncouncils} current councils across {nterr} Council Service Territories.</p>
<h2>Endpoints</h2>
<ul>
 <li><a href="v1/meta.json"><code>v1/meta.json</code></a> — version, counts, license</li>
 <li><a href="v1/current/councils.json"><code>v1/current/councils.json</code></a> — flat current council list</li>
 <li><a href="v1/current/territories.json"><code>v1/current/territories.json</code></a></li>
 <li><a href="v1/councils/index.json"><code>v1/councils/index.json</code></a> — all councils (incl. historical)</li>
 <li><code>v1/councils/&lt;id&gt;.json</code> — one council with its lifecycle events</li>
 <li><a href="v1/territories/index.json"><code>v1/territories/index.json</code></a></li>
 <li><code>v1/territories/&lt;id&gt;.json</code></li>
 <li><a href="schema/v1/council.schema.json"><code>schema/v1/</code></a> — JSON Schemas</li>
</ul>
<p class="muted">Source &amp; issues: <a href="https://github.com/sethmay/open-scout-api">github.com/sethmay/open-scout-api</a></p>
</body></html>
"""


if __name__ == "__main__":
    main()
