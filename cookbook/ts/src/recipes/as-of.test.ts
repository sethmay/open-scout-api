/**
 * Resolve the version of an entity that was in force on a given date.
 *
 * TRAP: `doc.versions[0]` reads like "the entity". It is the OLDEST snapshot -- versions are
 *       published oldest first -- so a directory built on it shows 1920s council names as
 *       today's. Reaching for the last element instead is the same bug wearing a nicer face:
 *       it answers "now" for every question, including historical ones, and it invents an
 *       answer for dates before the entity existed.
 * FIX:  select the version whose half-open window [valid_from, valid_to) contains the date.
 *       Either bound may be null, meaning open-ended, and a date before the first window has
 *       NO answer at all.
 *
 * A second trap rides along: `valid_from` is a HistoricalDate, so "1914", "1914-05" and
 * "1914-05-01" are all legal. Compare them as strings -- ISO prefixes already sort correctly.
 * `new Date("1914")` parses to a UTC instant and drags a timezone into a date-only question.
 */

import { test } from "vitest";
import { check, endpoint, get, items } from "../osa.js";
import type { CouncilIndexItem, Version, VersionedEntity } from "../generated/v1.js";

// Bounded scan for a demonstration subject. Naming one council id here would be a different
// kind of hardcoding: councils merge and get renamed, which is the very thing this recipe is
// about. Multi-version councils are common, so the loop exits after a handful of fetches.
const SCAN = 80;

const TODAY = new Date().toISOString().slice(0, 10);

function label(v: Version): string {
  const name = typeof v["name"] === "string" ? v["name"] : "(unnamed)";
  return `${name} [${v.valid_from ?? "-inf"} .. ${v.valid_to ?? "open"})`;
}

/** The version in force on `date`, or undefined when the entity did not exist yet. */
function asOf(doc: VersionedEntity, date: string): Version | undefined {
  return doc.versions.find((v) => {
    const from = v.valid_from;
    const to = v.valid_to;
    // Half-open: valid_from is inclusive, valid_to is exclusive, null is open-ended.
    return (from === null || date >= from) && (to === null || date < to);
  });
}

test("as-of resolution beats versions[0]", async () => {
  const template = await endpoint("v1/councils/{id}.json");
  const index = await items<CouncilIndexItem>("v1/councils/index.json");
  check(index.length > 0, "the council index must not be empty");

  let subject: VersionedEntity | undefined;
  let scanned = 0;
  for (const entry of index.slice(0, SCAN)) {
    const doc = await get<VersionedEntity>(template.replace("{id}", entry.id));
    scanned += 1;

    // Dataset invariant, enforced by tools/validate_data.py: an entity has at most one open
    // version. Two would make "current" ambiguous and every as-of query non-deterministic.
    const open = doc.versions.filter((v) => v.valid_to === null);
    check(open.length <= 1, `${entry.id}: more than one version has valid_to null`);

    // The demonstration needs a history whose windows are dated and ordered, and whose first
    // listed version is not the open one -- that is exactly the shape where versions[0] lies.
    const first = doc.versions[0];
    const dated = doc.versions.every((v) => {
      const from = v.valid_from;
      const to = v.valid_to;
      return from !== null && (to === null || from < to);
    });
    if (doc.versions.length > 1 && dated && first !== undefined && first.valid_to !== null) {
      subject = doc;
      break;
    }
  }
  check(subject !== undefined, `no dated multi-version council in ${scanned} index entries`);

  const first = subject.versions[0];
  check(first !== undefined, "a multi-version entity has a first version");
  const current = asOf(subject, TODAY);
  check(current !== undefined, "an entity with an open version must resolve for today");

  // The trap, stated as an invariant: the first element is NOT the current record.
  check(first !== current, "versions[0] must not be the version in force today");
  check(current.valid_to === null, "the version in force today is the open one");

  // The windows partition the timeline: every version is the answer on its own start date,
  // which only holds if the windows neither overlap nor leave the wrong one reachable.
  for (const v of subject.versions) {
    const from = v.valid_from;
    check(from !== null, "scan selected an entity whose versions are all dated");
    check(asOf(subject, from) === v, `${subject.id}: ${from} must resolve to its own version`);
  }

  // Before the first window there is no answer, and saying so is the whole point: an as-of
  // query that falls back to the oldest version fabricates history.
  check(asOf(subject, "0001-01-01") === undefined, "a date before the first window has no answer");

  // The window the naive read would have shown, resolved honestly rather than assumed.
  const firstFrom = first.valid_from;
  check(firstFrom !== null, "the first version is dated");

  console.log(`subject         ${subject.id} (${subject.versions.length} versions)`);
  console.log(`versions[0]     ${label(first)}   <- what the naive read returns`);
  console.log(`as of ${firstFrom.padEnd(10)}     ${label(first)}`);
  console.log(`as of ${TODAY.padEnd(10)}     ${label(current)}`);
  console.log(`as of 0001-01-01     no version applies (the council did not exist)`);
  console.log(`scanned         ${scanned} council documents to find a dated history`);
});
