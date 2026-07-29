# Camp map starter

A real map of every published camp, in two files and no build step: `index.html` plus
`app.js`, plain ES modules, Leaflet from a CDN with subresource integrity. No npm install, no
bundler, no framework. Copy the directory onto any static host and edit it in place.

## Running it

`tools/build.py` copies this directory into `dist/starters/camp-map/`, so the simplest run is
to serve a built `dist/` and open the page from inside it:

```
python tools/build.py
python -m http.server 8000 --directory dist
```

then <http://localhost:8000/starters/camp-map/>.

The page resolves the API from a `?base=` query parameter and otherwise falls back to the
published host, so `…/starters/camp-map/?base=http://localhost:8000` points it at whatever
tree you are serving. Serving *this* directory on a different port than the data and passing
`?base=` at the other port will fail: that is a cross-origin fetch, and `python -m http.server`
sends no CORS headers. Serve them from one origin, or use a server that does.

Map tiles come from openstreetmap.org, so the page needs an internet connection even when the
API is local.

## Traps it demonstrates

| Trap | What the page does instead |
| --- | --- |
| Plotting every `lat`/`lon` as if surveyed | Branches on `geo_precision`: `exact` is a pin, `approximate` is a dashed translucent circle with a legend entry and a popup warning saying it is a city or state centroid backfill. |
| Dropping camps with no coordinate | Lists them by name under "Without a coordinate", so a gap in the data reads as a gap and not as an absence. |
| One pin per camp | Groups camps sharing a `reservation.id` into one marker per property, listing its members. Goshen and Peaceful Valley are one marker each, not six and three stacked pins. |
| `features.includes("aquatics")` | Expands the chosen code transitively over the vocabulary's `broader` hierarchy first, so filtering on Aquatics matches a camp tagged only `kayaking`. The filter shows how many codes each parent term expands to. |
| Rendering an empty `features` array as "none" | Reads `features_verified_at` and `features_source_tier` and says which of the four states applies: never surveyed, imported but unverified, surveyed and empty, or surveyed with features. |
| Retyping the licence into the footer | Reads `disclaimer`, `license`, `version` and `generated_at` out of `v1/meta.json`, so the no-affiliation statement travels with the data. |

## What it deliberately is not

Not a component library and not a starting point for a production app: there is no clustering,
no routing and no state management, because each of those would bury the six decisions above
under framework code. The point is that the decisions are visible.
