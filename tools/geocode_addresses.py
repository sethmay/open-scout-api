"""Refine approximate camp coordinates from their street address (go-forward enrichment).

For each camp with geo_precision 'approximate' and a UNIQUE street address (a house/route number,
not shared with another camp — a shared address is a reservation gate, not a distinct camp point),
geocode the address via the US Census geocoder (OpenStreetMap Nominatim fallback). A match that
lands in-state AND within ~60 km of the existing approximate point (a sanity guard against a wrong
hit) upgrades the camp to that point with geo_precision 'exact'. Results cache to
tools/geocode_addresses.json so reruns are free/offline.

Unlike tools/import_camps.py + tools/geocode_camps.py (historical camp-finder seed), this reads and
writes data/ directly — data/ is the authoritative source now, so this is a live enrichment tool.
"""

from __future__ import annotations

import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import us_geo  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CAMPS = ROOT / "data" / "camps"
CACHE = ROOT / "tools" / "geocode_addresses.json"
UA = "open-scout-api coordinate enrichment (github.com/sethmay/open-scout-api)"
MAX_KM = 60.0  # a street match farther than this from the approximate point is rejected as wrong


def _km(a_lat, a_lon, b_lat, b_lon):
    r = 6371.0
    dlat = math.radians(b_lat - a_lat)
    dlon = math.radians(b_lon - a_lon)
    x = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(a_lat)) * math.cos(math.radians(b_lat)) * math.sin(dlon / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(x))


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def census(q):
    url = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?" + urllib.parse.urlencode(
        {"address": q, "benchmark": "Public_AR_Current", "format": "json"})
    m = _get(url).get("result", {}).get("addressMatches", [])
    if m:
        c = m[0]["coordinates"]
        return round(float(c["y"]), 6), round(float(c["x"]), 6)
    return None


def nominatim(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "json", "limit": 1, "countrycodes": "us"})
    d = _get(url)
    if d:
        return round(float(d[0]["lat"]), 6), round(float(d[0]["lon"]), 6)
    return None


def load(cid):
    return json.loads((CAMPS / f"{cid}.json").read_text("utf-8"))


def write(cid, obj):
    (CAMPS / f"{cid}.json").write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8", newline="\n")


def _norm(a: str) -> str:
    return re.sub(r"\s+", " ", a.strip().lower())


def _street(a) -> bool:
    # a real house/route number + street name (not a zip-only "Town, ST 12345", PO box, or mile marker)
    return bool(a and re.match(r"\s*\d+\s+[A-Za-z]", a))


def main() -> None:
    camps = {}
    for p in sorted(CAMPS.glob("*.json")):
        if p.name.endswith("_events.json"):
            continue
        camps[p.stem] = load(p.stem)
    ver = {cid: d["versions"][0] for cid, d in camps.items()}

    # a street address is upgradeable only if it is unique across all camps
    addr_count: dict[str, int] = {}
    for v in ver.values():
        a = v.get("address")
        if _street(a):
            addr_count[_norm(a)] = addr_count.get(_norm(a), 0) + 1
    targets = []
    for cid, v in ver.items():
        a = v.get("address")
        if v.get("geo_precision") != "approximate" or not _street(a):
            continue
        if addr_count[_norm(a)] == 1 and v.get("lat") is not None:
            targets.append(cid)

    cache = json.loads(CACHE.read_text("utf-8")) if CACHE.exists() else {}
    print(f"{len(targets)} unique-street-address approximate camps; cache has {len(cache)}")
    for i, cid in enumerate(targets, 1):
        if cid in cache:
            continue
        v = ver[cid]
        q = ", ".join(x for x in [v["address"], v.get("city"), v.get("state")] if x)
        res = None
        try:
            res = census(q) or (time.sleep(1.1) or nominatim(q))
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}] {cid}: ERROR {type(e).__name__}")
        ok = False
        if res:
            in_st = not us_geo.known(v.get("state")) or us_geo.in_state(v["state"], *res)
            near = _km(v["lat"], v["lon"], *res) <= MAX_KM
            if in_st and near:
                cache[cid] = list(res); ok = True
            else:
                print(f"  [{i}] {cid}: REJECT (in_state={in_st}, near={near}) {res} for {q!r}")
        if not ok and cid not in cache:
            cache[cid] = None  # tried, no usable match — don't retry
        time.sleep(0.5)
    CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    # apply cached hits to data (only camps still 'approximate')
    upgraded = 0
    for cid in targets:
        hit = cache.get(cid)
        v = ver[cid]
        if hit and v.get("geo_precision") == "approximate":
            v["lat"], v["lon"] = hit
            v["geo_precision"] = "exact"
            pr = v["provenance"]
            pr.setdefault("sources", []).append({"citation": "coordinate geocoded from street address (US Census / OpenStreetMap), 2026-07-22"})
            pr["notes"] = "Coordinate refined 2026-07-22 from the camp's street address (was a city/state-centroid approximation). " + pr.get("notes", "")
            write(cid, camps[cid])
            upgraded += 1
    print(f"upgraded {upgraded} camps to exact; {sum(1 for c in cache.values() if c)} usable / {len(cache)} tried")


if __name__ == "__main__":
    main()
