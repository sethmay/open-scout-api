"""Fill camp elevation from coordinates (go-forward enrichment).

Adds `elevation_ft` to every camp version that has a lat/lon, looked up from the
Copernicus 90 m DEM via the open-meteo elevation API (global, no key), converted
metres -> feet and rounded to the nearest 10 ft. Lookups are cached by coordinate in
tools/elevation.json so re-runs are offline, deterministic, and dedupe camps that
share a reservation-centroid point. Run manually; NOT part of the CI build.

elevation_ft inherits the camp's geo_precision: for an 'approximate' point this is the
city/reservation-centroid elevation, not the camp's exact ground.

Usage: python tools/elevation.py
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAMPS = ROOT / "data" / "camps"
CACHE = ROOT / "tools" / "elevation.json"
API = "https://api.open-meteo.com/v1/elevation"
UA = "open-scout-api elevation enrichment (github.com/sethmay/open-scout-api)"
BATCH = 100  # open-meteo accepts up to 100 comma-separated coords per request


def _key(lat: float, lon: float) -> str:
    return f"{lat:.5f},{lon:.5f}"


def _m_to_ft10(m):
    return None if m is None else int(round(m * 3.28084 / 10.0) * 10)


def _fetch(coords):
    """coords: [(lat, lon), ...] (<= BATCH) -> [elevation_ft | None, ...] in order."""
    q = urllib.parse.urlencode({
        "latitude": ",".join(f"{la:.5f}" for la, _ in coords),
        "longitude": ",".join(f"{lo:.5f}" for _, lo in coords),
    })
    req = urllib.request.Request(f"{API}?{q}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return [_m_to_ft10(m) for m in data["elevation"]]


def _place(v: dict, ft) -> None:
    """Set elevation_ft right after geo_precision for a clean, grouped diff."""
    out = {}
    for k, val in v.items():
        if k == "elevation_ft":
            continue
        out[k] = val
        if k == "geo_precision":
            out["elevation_ft"] = ft
    if "geo_precision" not in v:
        out["elevation_ft"] = ft
    v.clear()
    v.update(out)


def main() -> None:
    cache = json.loads(CACHE.read_text("utf-8")) if CACHE.exists() else {}
    files = [p for p in sorted(CAMPS.glob("*.json")) if not p.name.endswith("_events.json")]
    camps = [(p, json.loads(p.read_text("utf-8"))) for p in files]

    need = set()
    for _, c in camps:
        for v in c["versions"]:
            if v.get("lat") is not None and v.get("lon") is not None:
                k = _key(v["lat"], v["lon"])
                if k not in cache:
                    need.add((v["lat"], v["lon"]))
    need = sorted(need)
    for i in range(0, len(need), BATCH):
        chunk = need[i:i + BATCH]
        for (la, lo), ft in zip(chunk, _fetch(chunk)):
            cache[_key(la, lo)] = ft
    CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

    filled = 0
    for p, c in camps:
        changed = False
        for v in c["versions"]:
            if v.get("lat") is not None and v.get("lon") is not None:
                ft = cache.get(_key(v["lat"], v["lon"]))
                if ft is not None and v.get("elevation_ft") != ft:
                    _place(v, ft)
                    changed = True
                    filled += 1
        if changed:
            p.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    usable = sum(1 for x in cache.values() if x is not None)
    print(f"elevation_ft set on {filled} camp versions; cache {usable} usable / {len(cache)} coords")


if __name__ == "__main__":
    main()
