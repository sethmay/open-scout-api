/**
 * Camp map -- a browser starter for the Open Scout API. Plain ES modules, no build step, no
 * npm install, no imports outside this directory.
 *
 * TRAP: `L.marker([camp.lat, camp.lon])` over every camp produces a map that is confidently
 *       wrong in four ways at once. A quarter of those coordinates are city or state centroid
 *       backfills rendered as if surveyed; camps with no coordinate vanish from the interface
 *       entirely; camps sharing one reservation stack into an unreadable pile of pins; and a
 *       feature filter written as `features.includes("aquatics")` hides the camp with a lake,
 *       because camps are tagged `kayaking`, not with the parent term.
 * FIX:  branch on `geo_precision` and say in the UI which pins are guesses, list the
 *       unplaceable camps rather than dropping them, group by `reservation.id` into one marker
 *       per property, and expand the chosen feature code over the vocabulary's `broader`
 *       hierarchy before matching.
 *
 * A fifth trap has no map symbol, so it is spelled out in each popup: an empty `features` array
 * means "never surveyed" or "surveyed and genuinely has none" depending on
 * `features_verified_at`, and collapsing both into "none" invents a fact.
 */

// Leaflet is loaded as a classic script by index.html, so it arrives as a global.
const L = globalThis.L;

// Provisional pre-1.0 and expected to move, which is why `?base=` exists: point this page at
// a local `python -m http.server` over dist/, or at a fork, without editing the source.
const DEFAULT_BASE = "https://sethmay.github.io/open-scout-api";
const BASE = (new URLSearchParams(location.search).get("base") || DEFAULT_BASE).replace(/\/+$/, "");

const TIER_LABEL = {
  guide: "a camp-specific leader's or program guide",
  camp_page: "a page owned by the camp or its council",
  portal: "a council-wide portal listing",
};

const els = {
  map: document.getElementById("map"),
  feature: document.getElementById("feature"),
  status: document.getElementById("status"),
  unplaceable: document.getElementById("unplaceable"),
  attribution: document.getElementById("attribution"),
  error: document.getElementById("error"),
};

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

async function get(path) {
  const res = await fetch(`${BASE}/${path}`);
  if (!res.ok) {
    throw new Error(`GET ${BASE}/${path} -> ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// --- the data ---------------------------------------------------------------------------

let meta;
let camps;
let vocab;
try {
  [meta, { items: camps }, vocab] = await Promise.all([
    get("v1/meta.json"),
    get("v1/current/camps.json"),
    get("v1/vocab/camp-features.json"),
  ]);
} catch (err) {
  els.error.classList.add("shown");
  els.error.append(
    el("strong", null, "Could not load the API."),
    el("p", null, String(err)),
    el(
      "p",
      null,
      "Serving a built dist/ locally? Open this page with ?base=http://localhost:8000 " +
        `(or wherever v1/meta.json lives). The default is ${DEFAULT_BASE}.`,
    ),
  );
  throw err;
}

// --- feature hierarchy ------------------------------------------------------------------

// The vocabulary publishes child -> parent (`broader`). Filtering needs parent -> children, so
// invert it once, then expand transitively: the hierarchy is shallow today and nothing says it
// stays that way.
const narrower = new Map();
for (const term of vocab.terms) {
  if (term.broader) {
    narrower.set(term.broader, [...(narrower.get(term.broader) ?? []), term.code]);
  }
}

function closure(root) {
  const out = new Set([root]);
  const queue = [root];
  for (let code = queue.pop(); code !== undefined; code = queue.pop()) {
    for (const child of narrower.get(code) ?? []) {
      // Membership guard doubles as a cycle guard: the vocabulary is open, so a mis-entered
      // `broader` must not hang the page.
      if (!out.has(child)) {
        out.add(child);
        queue.push(child);
      }
    }
  }
  return out;
}

// Only parent terms are worth offering: filtering on `kayaking` is just an exact match.
const labels = new Map(vocab.terms.map((t) => [t.code, t.label]));
const parents = [...narrower.keys()].sort((a, b) =>
  (labels.get(a) ?? a).localeCompare(labels.get(b) ?? b),
);
for (const code of parents) {
  const kinds = closure(code).size - 1;
  const option = el("option", null, `${labels.get(code) ?? code} (${kinds} kinds)`);
  option.value = code;
  els.feature.append(option);
}

// --- one marker per property --------------------------------------------------------------

// `reservation.id` is a stable grouping key for camps that share a property. Grouping on it is
// what turns eleven pins stacked on one lake into one pin that lists eleven camps.
function group(selection) {
  const groups = new Map();
  for (const camp of selection) {
    const key = camp.reservation ? `reservation:${camp.reservation.id}` : `camp:${camp.id}`;
    const existing = groups.get(key);
    if (existing) {
      existing.members.push(camp);
      continue;
    }
    groups.set(key, {
      key,
      label: camp.reservation ? (camp.reservation.name ?? camp.reservation.id) : camp.name,
      members: [camp],
    });
  }

  // A group's coordinate is the best one any member has: a surveyed fix beats a centroid, and
  // a marker must never claim more precision than the camp it stands on.
  for (const g of groups.values()) {
    const anchor =
      g.members.find((c) => c.geo_precision === "exact") ??
      g.members.find((c) => c.geo_precision === "approximate") ??
      null;
    g.anchor = anchor;
    g.precision = anchor === null ? null : anchor.geo_precision;
  }
  return [...groups.values()];
}

// --- what is actually known about a camp's features ---------------------------------------

// Four states, and flattening them to "none" is a lie in two of them.
function provenance(camp) {
  const tier = TIER_LABEL[camp.features_source_tier] ?? "an unrecorded source";
  if (camp.features_verified_at === null) {
    return camp.features.length === 0
      ? "Never surveyed. Nothing is known about this camp's program -- not that it has none."
      : `${camp.features.length} features carried in from a bulk import and never verified.`;
  }
  return camp.features.length === 0
    ? `Surveyed ${camp.features_verified_at} against ${tier}, which listed no program features.`
    : `${camp.features.length} features, surveyed ${camp.features_verified_at} from ${tier}.`;
}

function popup(g) {
  const box = el("div", "popup");
  box.append(el("h3", null, g.label));
  if (g.members.length > 1) {
    box.append(el("p", "muted", `${g.members.length} camps share this property`));
  }
  if (g.precision === "approximate") {
    box.append(
      el(
        "p",
        "warn",
        "Approximate location: plotted from the camp's city or state, not a surveyed " +
          "coordinate. Do not navigate to it.",
      ),
    );
  }
  for (const camp of g.members) {
    const item = el("div", "camp");
    // The heading already names a lone camp; repeat it only when the marker is a property.
    if (camp.name !== g.label) {
      item.append(el("strong", null, camp.name));
    }
    const where = `${camp.city ?? "?"}, ${camp.state ?? "?"}`;
    item.append(el("div", "muted", `${where} - ${camp.camp_type}`));
    item.append(el("div", "muted", provenance(camp)));
    if (camp.website) {
      const link = el("a", null, "Camp website");
      link.href = camp.website;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      item.append(link);
    }
    box.append(item);
  }
  return box;
}

// --- the map --------------------------------------------------------------------------------

const map = L.map(els.map).setView([39.5, -98.35], 4);
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

const markers = L.layerGroup().addTo(map);

function render(code) {
  const wanted = code === "" ? null : closure(code);
  const selection =
    wanted === null ? camps : camps.filter((c) => c.features.some((f) => wanted.has(f)));

  markers.clearLayers();
  els.unplaceable.replaceChildren();

  let pinned = 0;
  let plotted = 0;
  let missing = 0;
  for (const g of group(selection)) {
    if (g.anchor === null) {
      // Not on the map, but not gone either: an unplaceable camp is a hole in the data, and a
      // hole you can read beats a map that quietly pretends to be complete.
      for (const camp of g.members) {
        const row = el("li");
        row.append(el("strong", null, camp.name));
        const where = `${camp.city ?? "?"}, ${camp.state ?? "?"}`;
        row.append(el("div", "muted", `${where} -- no coordinate published`));
        els.unplaceable.append(row);
        missing += 1;
      }
      continue;
    }

    const at = [g.anchor.lat, g.anchor.lon];
    const exact = g.precision === "exact";
    const layer = exact
      ? L.marker(at, { title: g.label })
      : L.circleMarker(at, {
          // Deliberately not a pin: a centroid backfill should not look like a survey.
          radius: 9,
          color: "#b45309",
          weight: 1,
          dashArray: "3 3",
          fillColor: "#f59e0b",
          fillOpacity: 0.25,
        });
    if (exact) {
      pinned += 1;
    } else {
      plotted += 1;
    }
    layer.bindPopup(popup(g), { maxWidth: 340 });
    markers.addLayer(layer);
  }

  const scope =
    wanted === null ? "All camps" : `${labels.get(code) ?? code} (${wanted.size} feature codes)`;
  els.status.textContent =
    `${scope}: ${selection.length} camps -- ${pinned} exact markers, ` +
    `${plotted} approximate areas, ${missing} with no coordinate.`;
  if (missing === 0) {
    els.unplaceable.append(el("li", "muted", "None in this selection."));
  }
}

els.feature.addEventListener("change", () => render(els.feature.value));
render("");

// --- attribution -----------------------------------------------------------------------------

// The no-affiliation statement and the licence come from meta.json rather than being retyped
// here, so a change to either travels with the data instead of going stale in a footer.
const licence = el("a", null, meta.license);
licence.href = "https://creativecommons.org/licenses/by-nc-sa/4.0/";
licence.rel = "license noopener noreferrer";
licence.target = "_blank";

const credit = el("div");
credit.append(
  `${meta.name} ${meta.version} (generated ${meta.generated_at}), licensed under `,
  licence,
  `. Serving from ${BASE}. Map tiles by OpenStreetMap contributors.`,
);
els.attribution.append(el("div", null, meta.disclaimer), credit);
