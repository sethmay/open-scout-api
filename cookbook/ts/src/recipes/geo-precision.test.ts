/**
 * Partition camps by how much their coordinates are worth before plotting any of them.
 *
 * TRAP: `map.pin(camp.lat, camp.lon)` renders every camp as a surveyed location. Some of those
 *       coordinates are city or state centroids backfilled so the record has SOMETHING, so the
 *       map confidently shows a camp in the middle of a highway thirty miles from the gate --
 *       and the camps with no coordinate at all simply disappear from the interface.
 * FIX:  read `geo_precision` first and split into three sets: `exact` pins, `approximate`
 *       plots that must render as an area and say why, and null coordinates that get listed
 *       rather than dropped. Precision is published for exactly this decision; use it.
 */

import { test } from "vitest";
import { check, items } from "../osa.js";
import type { CurrentCamp } from "../generated/v1.js";

test("camps partition into pinnable, soft-plot and unplaceable", async () => {
  const camps = await items<CurrentCamp>("v1/current/camps.json");
  check(camps.length > 0, "current/camps.json must not be empty");

  const pinnable = camps.filter((c) => c.geo_precision === "exact");
  const softPlot = camps.filter((c) => c.geo_precision === "approximate");
  const unplaceable = camps.filter((c) => c.geo_precision === null);

  // Tri-state exhaustiveness: no fourth bucket and no camp in two of them. A consumer that
  // switches on precision needs to know the switch is total.
  check(
    pinnable.length + softPlot.length + unplaceable.length === camps.length,
    "geo_precision must be exactly one of exact | approximate | null",
  );

  for (const camp of camps) {
    // The contract that makes the partition safe: a coordinate always arrives with a stated
    // precision, so there is no "plot it and hope" case.
    check(
      camp.lat === null || camp.geo_precision !== null,
      `${camp.id}: has a coordinate but no geo_precision`,
    );
    check(
      camp.geo_precision !== null || (camp.lat === null && camp.lon === null),
      `${camp.id}: geo_precision is null but a coordinate is present`,
    );
    check((camp.lat === null) === (camp.lon === null), `${camp.id}: half a coordinate`);
    check(
      camp.lat === null ||
        camp.lon === null ||
        (camp.lat >= -90 && camp.lat <= 90 && camp.lon >= -180 && camp.lon <= 180),
      `${camp.id}: coordinate out of range`,
    );
  }

  // Lower bounds, not counts. Both plotted classes are large and structural. `unplaceable`
  // deliberately gets no floor: it should shrink toward zero as coverage improves, and an
  // assertion that it stays non-empty would punish the fix.
  check(pinnable.length > 0, "some camps must be surveyed to exact coordinates");
  check(softPlot.length > 0, "the approximate class is a documented part of this dataset");

  // An approximate coordinate is a backfill from the camp's own city/state, which is why the
  // honest UI caption is the place name rather than the number.
  const soft = softPlot[0];
  check(soft !== undefined, "a non-empty class has a first member");
  check(
    soft.city !== null || soft.state !== null,
    `${soft.id}: an approximate coordinate must be explainable by a place`,
  );

  const listed = unplaceable.map((c) => `${c.name} (${c.city ?? "?"}, ${c.state ?? "?"})`);

  console.log(`camps           ${camps.length} in current/camps.json`);
  console.log(`pinnable        ${pinnable.length}  geo_precision=exact -> a marker`);
  console.log(`soft plot       ${softPlot.length}  approximate -> an area, captioned`);
  console.log(`unplaceable     ${unplaceable.length}  no coordinate -> a list, not a hole`);
  console.log(`example soft    ${soft.name} sits at the centroid of ${soft.city}, ${soft.state}`);
  console.log(`unplaceable are ${listed.length === 0 ? "(none right now)" : listed.join("; ")}`);
});
