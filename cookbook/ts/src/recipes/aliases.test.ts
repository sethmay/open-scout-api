/**
 * Resolve a camp id you stored last season into the camp that still exists.
 *
 * TRAP: ids are stable until two camps turn out to be the same property, or a weekend program
 *       is folded into its host camp. The retired id then 404s on `v1/camps/{id}.json` and is
 *       absent from `current/camps.json`, so a saved bookmark, a cached favourite or a foreign
 *       key in someone's database reads as "this camp closed". It did not; it was merged.
 * FIX:  consult `v1/camps/aliases.json` before concluding anything. It is a bare
 *       `{retired-id: surviving-id}` map -- no envelope, no `$schema`, no `items` -- so fetch
 *       it with `get`, not with the collection helper, and resolve ids through it on the way
 *       in. One hop is enough: aliases never chain.
 */

import { test } from "vitest";
import { check, endpoint, get, items } from "../osa.js";
import type { AliasMap, CurrentCamp } from "../generated/v1.js";

test("retired camp ids resolve to live camps", async () => {
  // A bare map, deliberately unenveloped: `items()` would throw here, and that is the point.
  const aliases = await get<AliasMap>(await endpoint("v1/camps/aliases.json"));
  const camps = await items<CurrentCamp>("v1/current/camps.json");

  const live = new Set(camps.map((c) => c.id));
  const retired = Object.keys(aliases).sort();
  check(retired.length > 0, "the alias map must not be empty");

  for (const [from, to] of Object.entries(aliases)) {
    // Referential integrity: an alias that points at nothing is worse than no alias, because
    // it converts a missing record into a confidently wrong redirect.
    check(live.has(to), `${from} -> ${to}, which is not a live camp`);
    // A retired id must not also be live, or a lookup would have two valid answers.
    check(!live.has(from), `${from} is both an alias and a live camp id`);
    // No chains, so one lookup resolves. A chain would need a loop, and a loop needs a cycle
    // guard, and none of that is necessary here -- but only because this holds.
    check(aliases[to] === undefined, `${from} -> ${to} -> ... : aliases must not chain`);
  }

  // The resolver a consumer actually ships: unknown ids pass through untouched, because the
  // alias map answers "was this renamed", not "does this exist".
  const resolve = (id: string): string => aliases[id] ?? id;

  for (const id of retired) {
    check(resolve(resolve(id)) !== id, `${id} must resolve away from itself`);
    check(resolve(resolve(id)) === resolve(id), `${id} must resolve in one hop`);
  }
  const anyLive = camps[0];
  check(anyLive !== undefined, "there is at least one live camp");
  check(resolve(anyLive.id) === anyLive.id, "a live id resolves to itself");

  // Prove the failure mode rather than describing it: the retired id really is a 404.
  const stale = retired[0];
  check(stale !== undefined, "a non-empty map has a first key");
  const template = await endpoint("v1/camps/{id}.json");
  let missing = false;
  try {
    await get(template.replace("{id}", stale));
  } catch {
    missing = true;
  }
  check(missing, `${stale} still resolves; this recipe's premise would be stale`);

  const survivor = await get<{ readonly kind: string; readonly id: string }>(
    template.replace("{id}", resolve(stale)),
  );
  check(survivor.kind === "camp", "the resolved id must fetch a camp document");
  check(survivor.id === resolve(stale), "the fetched document must be the one asked for");

  console.log(`aliases         ${retired.length} retired camp ids`);
  console.log(`stale lookup    v1/camps/${stale}.json -> 404`);
  console.log(`resolved        ${stale}`);
  console.log(`             -> ${survivor.id}`);
  console.log(`live check      every alias target is present in current/camps.json`);
  console.log(`chains          none: resolve() is a single lookup`);
});
