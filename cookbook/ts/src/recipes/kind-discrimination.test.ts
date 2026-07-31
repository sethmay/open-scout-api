/**
 * Narrow a collection to its item type using the envelope's own `kind`.
 *
 * TRAP: every collection in this API -- `v1/current/*.json` and `v1/{dataset}/index.json` --
 *       shares one envelope, so `items` is a bag of objects and TypeScript will happily let
 *       you assert it into whatever shape you had in mind. Assert `CurrentCamp` over
 *       `current/councils.json` and nothing complains until `camp.features` is undefined in
 *       production. The published shapes also move while the project is pre-1.0; a hand-typed
 *       interface drifts silently because there is nothing to compare it against.
 * FIX:  read the envelope's `kind` at runtime, check it, and let the generated `CurrentByKind`
 *       map pick the item type from that literal. Then verify against live data that the
 *       generated shape is still true. This recipe is the drift detector for the whole
 *       workspace: `npm test` runs `tsc --noEmit` first for exactly this reason.
 */

import { test } from "vitest";
import { check, get } from "../osa.js";
import type { CurrentByKind, CurrentCollection } from "../generated/v1.js";

/**
 * The typed read. Deliberately NOT folded into osa.ts: choosing the item type from the
 * envelope is the lesson, and a consumer needs to see the check that makes the cast sound.
 */
async function currentOf<K extends keyof CurrentByKind>(
  kind: K,
  path: string,
): Promise<readonly CurrentByKind[K][]> {
  const doc = await get<CurrentCollection>(path);
  // The cast below is only honest because of this line: the file itself said what it holds.
  check(doc.kind === kind, `${path}: expected kind=${kind}, got kind=${doc.kind}`);
  check(doc.count === doc.items.length, `${path}: count disagrees with items length`);
  // Through `unknown`, because the generated envelope types items as an opaque record: the
  // schema cannot express "the kind field picks the item shape", which is what this map is for.
  return doc.items as unknown as readonly CurrentByKind[K][];
}

/** The keys a value must actually carry, i.e. everything not declared with `?`. */
type RequiredKeys<T> = { [K in keyof T]-?: {} extends Pick<T, K> ? never : K }[keyof T];

const REQUIRED_CAMP_FIELDS = [
  "id",
  "name",
  "camp_type",
  "operator",
  "operating_status",
  "council",
  "parent",
  "state",
  "city",
  "lat",
  "lon",
  "geo_precision",
  "reservation",
  "website",
  "program_types",
  "summary",
  "features",
  "features_signature",
  "features_source_tier",
  "features_verified_at",
  "council_name",
  "council_website",
  "council_number",
  "url",
  "verified_at",
  "imported_at",
  "method",
  "confidence",
] as const satisfies readonly RequiredKeys<CurrentByKind["camp"]>[];

type UnlistedField = Exclude<
  RequiredKeys<CurrentByKind["camp"]>,
  (typeof REQUIRED_CAMP_FIELDS)[number]
>;

// Half of the drift check happens in the compiler. If the generated CurrentCamp gains a
// required field, `UnlistedField` stops being `never`, this initialiser stops typechecking,
// and the error message names the field that the runtime loop below would otherwise ignore.
const fieldListIsComplete: [UnlistedField] extends [never] ? true : UnlistedField = true;

test("the envelope kind selects the item type, and the generated type still matches", async () => {
  check(fieldListIsComplete, "the required-field list must cover the generated CurrentCamp");

  const camps = await currentOf("camp", "v1/current/camps.json");
  check(camps.length > 0, "current/camps.json must not be empty");

  // The other half happens against live data: a field the schema calls required must be
  // PRESENT on every item, including when its value is null. `?.` would hide exactly this.
  for (const camp of camps) {
    for (const field of REQUIRED_CAMP_FIELDS) {
      check(Object.hasOwn(camp, field), `camp ${camp.id}: missing required field ${field}`);
    }
  }

  // Narrowing is real, not decorative: these reads only compile because `kind` was "camp".
  const first = camps[0];
  check(first !== undefined, "a non-empty collection has a first item");
  check(Array.isArray(first.features), "CurrentCamp.features is an array of feature codes");
  check(
    first.geo_precision === null ||
      first.geo_precision === "exact" ||
      first.geo_precision === "approximate",
    "CurrentCamp.geo_precision is a closed three-valued enum",
  );

  // The same helper at a second kind, to show the map is generic rather than a camp special
  // case. `bsa_number` exists on CurrentCouncil and on nothing else in the union.
  const councils = await currentOf("council", "v1/current/councils.json");
  const council = councils[0];
  check(council !== undefined, "current/councils.json must not be empty");
  check(
    typeof council.bsa_number === "number" || council.bsa_number === null,
    "CurrentCouncil.bsa_number is number | null",
  );

  // And the guard has to actually guard, or the cast is a lie told politely.
  let rejected = false;
  try {
    await currentOf("council", "v1/current/camps.json");
  } catch {
    rejected = true;
  }
  check(rejected, "reading camps as councils must fail on the envelope kind, not later");

  console.log(`camps           kind=camp  ${camps.length} items typed as CurrentCamp`);
  console.log(`councils        kind=council  ${councils.length} items typed as CurrentCouncil`);
  console.log(`checked fields  ${REQUIRED_CAMP_FIELDS.length} required fields on every camp`);
  console.log(`mismatched kind rejected before the cast, as it must be`);
  const where = first.state ?? "??";
  console.log(`first camp      ${first.name} (${where}), ${first.features.length} features`);
});
