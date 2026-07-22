"""One-time enrichment: fill in city-level coordinates for camps whose source lat/lon is
missing or grossly out-of-state, writing a committed lookup at tools/geocode.json.

This is NOT part of the build. It calls the OpenStreetMap Nominatim service (max 1 req/s) once,
validates each result against the camp's state box, and caches by camp id so reruns are free and
add only new gaps. import_camps.py reads the committed lookup, so the build stays offline and
deterministic. Coordinates from here are city centroids -> geo_precision "approximate".
"""

from __future__ import annotations

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import us_geo  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CAMPS = ROOT / "data" / "camps"
UA = "open-scout-api geocode enrichment (github.com/sethmay/open-scout-api)"
OUT = ROOT / "tools" / "geocode.json"

def nominatim(query: str) -> tuple[float, float] | None:
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 1, "countrycodes": "us"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data:
        return round(float(data[0]["lat"]), 6), round(float(data[0]["lon"]), 6)
    return None


def needs_coords(v: dict) -> bool:
    lat, lon, st = v.get("lat"), v.get("lon"), v.get("state")
    if lat is None or lon is None:
        return True
    return us_geo.known(st) and not us_geo.in_state(st, lat, lon)


def main() -> None:
    cache: dict[str, list[float]] = json.loads(OUT.read_text("utf-8")) if OUT.exists() else {}
    todo = []
    for p in sorted(CAMPS.glob("*.json")):
        if p.name.endswith("_events.json"):
            continue
        d = json.loads(p.read_text("utf-8"))
        v = d["versions"][0]
        cid, city, st = d["id"], v.get("city"), v.get("state")
        if needs_coords(v) and city and us_geo.known(st) and cid not in cache:
            todo.append((cid, f"{city}, {st}, USA"))

    print(f"{len(todo)} camps to geocode (cache has {len(cache)})")
    hits = miss = rejected = 0
    for i, (cid, q) in enumerate(todo, 1):
        try:
            res = nominatim(q)
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}/{len(todo)}] {cid}: ERROR {type(e).__name__}")
            res = None
        if res:
            st = cid_state(cid)
            if st and not us_geo.in_state(st, res[0], res[1]):
                print(f"  [{i}/{len(todo)}] {cid}: REJECT out-of-state {res} for {q!r}")
                rejected += 1
            else:
                cache[cid] = list(res)
                hits += 1
        else:
            miss += 1
        time.sleep(1.1)
        if i % 20 == 0:
            OUT.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    OUT.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"done: +{hits} geocoded, {miss} no-match, {rejected} rejected; {len(cache)} total in {OUT.name}")


def cid_state(cid: str) -> str | None:
    d = json.loads((CAMPS / f"{cid}.json").read_text("utf-8"))
    return d["versions"][0].get("state")


if __name__ == "__main__":
    main()
