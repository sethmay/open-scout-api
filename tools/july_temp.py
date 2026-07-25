"""Fill July temperature normals from WorldClim rasters (go-forward enrichment).

Adds `july_high_f` and `july_low_f` to every camp version that has a lat/lon: the average
daily high and average overnight low for July, sampled from WorldClim v2.1 monthly climate
normals (1970-2000) at 30 arc-seconds (~1 km). Values are converted °C -> °F and rounded to
whole degrees. Results are cached by coordinate in tools/july_temp.json, which IS committed —
so re-runs are offline and deterministic, and no consumer or CI job needs rasterio or the
source rasters. NOT part of the CI build; run manually when camps or coordinates change.

Source rasters are ~8 GB and are NOT redistributed (gitignored). Fetch once:
  mkdir -p tools/worldclim && cd tools/worldclim
  curl -O https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_30s_tmax.zip
  curl -O https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_30s_tmin.zip
Only the July member of each zip is read, in place, via GDAL's /vsizip/. Override the location
with WORLDCLIM_DIR, or use a lighter tier (10m/5m/2.5m, coarser) with WORLDCLIM_RES.

Requires rasterio (tool-only dependency): python -m pip install rasterio

Caveats. The normals inherit the camp's geo_precision: for an 'approximate' point they describe
the city/reservation-centroid location, not the camp's exact ground. WorldClim is a land-surface
product, so a coastal or island camp whose pixel is open water falls back to the nearest land
cell. July is a fixed month (US resident-camp season); for overseas/equatorial camps it is still
a real July value, not necessarily their camp season.

WorldClim v2.1 is CC-BY 4.0 — Fick & Hijmans (2017), Int. J. Climatol. 37:4302-4315. See NOTICE.md.

Usage: python tools/july_temp.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import numpy as np
import rasterio
from rasterio.windows import Window

ROOT = Path(__file__).resolve().parents[1]
CAMPS = ROOT / "data" / "camps"
CACHE = ROOT / "tools" / "july_temp.json"
RASTERS = Path(os.environ.get("WORLDCLIM_DIR") or (ROOT / "tools" / "worldclim"))
RES = os.environ.get("WORLDCLIM_RES", "30s")
NODATA_FLOOR = -1e30  # WorldClim nodata is ~-3.4e38; any real °C is far above this
MAX_RING = 12  # nearest-land search radius in pixels (~12 km at 30s)


def _key(lat: float, lon: float) -> str:
    return f"{lat:.5f},{lon:.5f}"


def _c_to_f(c: float) -> int:
    return round(c * 9 / 5 + 32)


def _raster(var: str) -> str:
    """GDAL /vsizip path to the July member of the WorldClim zip for `var` (tmax|tmin)."""
    z = RASTERS / f"wc2.1_{RES}_{var}.zip"
    if not z.exists():
        raise SystemExit(
            f"missing raster {z}\nFetch it (see this file's docstring):\n"
            f"  https://geodata.ucdavis.edu/climate/worldclim/2_1/base/wc2.1_{RES}_{var}.zip"
        )
    return f"zip://{z.as_posix()}!wc2.1_{RES}_{var}_07.tif"


def _nearest_land(ds, lon: float, lat: float):
    """Value of the closest land pixel to (lon, lat), or None. For coastal/island points
    whose own cell is open water in this land-surface product."""
    row, col = ds.index(lon, lat)
    for ring in range(1, MAX_RING + 1):
        blk = ds.read(1, window=Window(col - ring, row - ring, 2 * ring + 1, 2 * ring + 1),
                      boundless=True, fill_value=ds.nodata)
        land = blk > NODATA_FLOOR
        if land.any():
            yy, xx = np.nonzero(land)
            nearest = ((yy - ring) ** 2 + (xx - ring) ** 2).argmin()
            return float(blk[yy[nearest], xx[nearest]])
    return None


def _sample(var: str, coords):
    """coords: [(lat, lon), ...] -> ([°C | None, ...], n_fallback)."""
    out, fallback = [], 0
    with rasterio.open(_raster(var)) as ds:
        vals = [float(v[0]) for v in ds.sample([(lo, la) for la, lo in coords])]
        for (la, lo), v in zip(coords, vals):
            if v > NODATA_FLOOR:
                out.append(v)
                continue
            land = _nearest_land(ds, lo, la)
            fallback += land is not None
            out.append(land)
    return out, fallback


def _place(v: dict, hi: int, lo: int) -> None:
    """Set july_high_f/july_low_f right after elevation_ft (else geo_precision) for a clean diff."""
    anchor = "elevation_ft" if "elevation_ft" in v else "geo_precision"
    out = {}
    for k, val in v.items():
        if k in ("july_high_f", "july_low_f"):
            continue
        out[k] = val
        if k == anchor:
            out["july_high_f"] = hi
            out["july_low_f"] = lo
    if anchor not in v:
        out["july_high_f"] = hi
        out["july_low_f"] = lo
    v.clear()
    v.update(out)


def main() -> None:
    cache = json.loads(CACHE.read_text("utf-8")) if CACHE.exists() else {}
    files = [p for p in sorted(CAMPS.glob("*.json")) if not p.name.endswith("_events.json")]
    camps = [(p, json.loads(p.read_text("utf-8"))) for p in files]

    need = sorted({(v["lat"], v["lon"]) for _, c in camps for v in c["versions"]
                   if v.get("lat") is not None and v.get("lon") is not None
                   and _key(v["lat"], v["lon"]) not in cache})
    if need:
        highs, fb_hi = _sample("tmax", need)
        lows, fb_lo = _sample("tmin", need)
        for (la, lo), hi, low in zip(need, highs, lows):
            cache[_key(la, lo)] = ({"july_high_f": _c_to_f(hi), "july_low_f": _c_to_f(low)}
                                   if hi is not None and low is not None else None)
        CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
        print(f"sampled {len(need)} coords from WorldClim {RES}; "
              f"nearest-land fallback: {fb_hi} high / {fb_lo} low")

    filled = 0
    for p, c in camps:
        changed = False
        for v in c["versions"]:
            if v.get("lat") is None or v.get("lon") is None:
                continue
            rec = cache.get(_key(v["lat"], v["lon"]))
            if rec and (v.get("july_high_f") != rec["july_high_f"]
                        or v.get("july_low_f") != rec["july_low_f"]):
                _place(v, rec["july_high_f"], rec["july_low_f"])
                changed = True
                filled += 1
        if changed:
            p.write_text(json.dumps(c, indent=2, ensure_ascii=False) + "\n",
                         encoding="utf-8", newline="\n")
    usable = sum(1 for x in cache.values() if x is not None)
    print(f"july normals set on {filled} camp versions; cache {usable} usable / {len(cache)} coords")


if __name__ == "__main__":
    main()
