"""US state/territory bounding boxes for coordinate-integrity checks and centroid fallback.

Boxes are approximate published state extents (decimal degrees). They exist to catch grossly
mislocated points (wrong state/region, hundreds of km off), NOT to enforce precise borders, so
`in_state` pads generously. `state_centroid` (box midpoint) is the last-resort backfill for a
camp that has a state but no geocodable city. International codes (AE/AP military, etc.) are
absent by design: their coordinates cannot be state-checked and are left untouched.
"""

from __future__ import annotations

# code: (min_lat, max_lat, min_lon, max_lon)
STATE_BBOX: dict[str, tuple[float, float, float, float]] = {
    "AL": (30.1, 35.1, -88.5, -84.9), "AK": (51.0, 71.5, -179.9, -129.0),
    "AZ": (31.3, 37.1, -114.9, -109.0), "AR": (33.0, 36.6, -94.7, -89.6),
    "CA": (32.5, 42.1, -124.5, -114.1), "CO": (36.9, 41.1, -109.1, -102.0),
    "CT": (40.9, 42.1, -73.8, -71.7), "DE": (38.4, 39.9, -75.8, -75.0),
    "DC": (38.7, 39.1, -77.2, -76.9), "FL": (24.4, 31.1, -87.7, -79.9),
    "GA": (30.3, 35.1, -85.7, -80.8), "HI": (18.8, 22.3, -160.3, -154.7),
    "ID": (41.9, 49.1, -117.3, -111.0), "IL": (36.9, 42.6, -91.6, -87.4),
    "IN": (37.7, 41.8, -88.1, -84.7), "IA": (40.3, 43.6, -96.7, -90.1),
    "KS": (36.9, 40.1, -102.1, -94.6), "KY": (36.4, 39.2, -89.6, -81.9),
    "LA": (28.9, 33.1, -94.1, -88.8), "ME": (42.9, 47.5, -71.1, -66.9),
    "MD": (37.8, 39.8, -79.5, -75.0), "MA": (41.2, 42.9, -73.6, -69.9),
    "MI": (41.6, 48.3, -90.5, -82.3), "MN": (43.4, 49.5, -97.3, -89.4),
    "MS": (30.1, 35.1, -91.7, -88.0), "MO": (35.9, 40.7, -95.8, -89.0),
    "MT": (44.3, 49.1, -116.1, -104.0), "NE": (39.9, 43.1, -104.1, -95.2),
    "NV": (35.0, 42.1, -120.1, -114.0), "NH": (42.6, 45.4, -72.6, -70.6),
    "NJ": (38.8, 41.4, -75.6, -73.8), "NM": (31.2, 37.1, -109.1, -103.0),
    "NY": (40.4, 45.1, -79.8, -71.8), "NC": (33.8, 36.6, -84.4, -75.4),
    "ND": (45.9, 49.1, -104.1, -96.5), "OH": (38.3, 42.4, -84.9, -80.5),
    "OK": (33.6, 37.1, -103.1, -94.4), "OR": (41.9, 46.3, -124.6, -116.4),
    "PA": (39.7, 42.4, -80.6, -74.6), "RI": (41.1, 42.1, -71.9, -71.1),
    "SC": (32.0, 35.3, -83.4, -78.5), "SD": (42.4, 45.9, -104.1, -96.4),
    "TN": (34.9, 36.7, -90.4, -81.6), "TX": (25.8, 36.6, -106.7, -93.5),
    "UT": (36.9, 42.1, -114.1, -108.9), "VT": (42.7, 45.1, -73.5, -71.5),
    "VA": (36.5, 39.5, -83.7, -75.2), "WA": (45.5, 49.1, -124.9, -116.9),
    "WV": (37.1, 40.7, -82.7, -77.7), "WI": (42.4, 47.4, -92.9, -86.8),
    "WY": (40.9, 45.1, -111.1, -104.0), "PR": (17.8, 18.6, -67.3, -65.2),
    "VI": (17.6, 18.5, -65.1, -64.5), "GU": (13.2, 13.7, 144.6, 145.0),
}

PAD = 0.5  # degrees of slack so near-border points and box imprecision never false-fail


def known(state: str | None) -> bool:
    return state in STATE_BBOX


def in_state(state: str, lat: float, lon: float, pad: float = PAD) -> bool:
    """True if (lat, lon) falls within `state`'s padded box. Unknown state -> True (can't judge)."""
    box = STATE_BBOX.get(state)
    if box is None:
        return True
    mnla, mxla, mnlo, mxlo = box
    return (mnla - pad) <= lat <= (mxla + pad) and (mnlo - pad) <= lon <= (mxlo + pad)


def state_centroid(state: str) -> tuple[float, float] | None:
    """Box midpoint — a coarse 'somewhere in the state' fallback. None if state unknown."""
    box = STATE_BBOX.get(state)
    if box is None:
        return None
    mnla, mxla, mnlo, mxlo = box
    return (round((mnla + mxla) / 2, 4), round((mnlo + mxlo) / 2, 4))
