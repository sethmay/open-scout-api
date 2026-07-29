/**
 * Resolve a camp id you stored last season into the camp that still exists.
 *
 * TRAP: ids are stable until two camps turn out to be the same property, or a weekend program
 *       is folded into its host camp. The retired id then 404s on `v1/camps/{id}.json` and is
 *       absent from `current/camps.json`, so a saved bookmark, a cached favourite or a foreign
 *       key in someone's database reads as "this camp closed". It did not; it was merged. The
 *       second trap is stopping after one hop: the map is written one camp at a time and is NOT
 *       transitively closed, so a merge target that was itself later merged away leaves a value
 *       that is another key, and one hop lands on an id that still 404s.
 * FIX:  consult `v1/camps/aliases.json` before concluding anything. It is a bare
 *       `{retired-id: surviving-id}` map -- no envelope, no `$schema`, no `items` -- so fetch
 *       it with `get`, not with the collection helper, and resolve ids through it on the way
 *       in. Follow it transitively, until the id is one the API actually publishes.
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

  for (const from of retired) {
    // A retired id must not also be live, or a lookup would have two valid answers. Alias
    // VALUES carry no such rule: a value that is not live is exactly what a chain looks like.
    check(!live.has(from), `${from} is both an alias and a live camp id`);
  }

  /**
   * The resolver a consumer actually ships. Walks the map until it lands on an id the API
   * publishes, and returns null when no chain gets there -- which is a real 404, not a merge,
   * and must not be reported as one. `seen` bounds the walk by the size of the map, so a cycle
   * in the data returns null instead of hanging a request.
   */
  const resolve = (id: string): string | null => {
    const seen = new Set<string>();
    let current = id;
    while (!live.has(current)) {
      const next = aliases[current];
      if (next === undefined || seen.has(current)) {
        return null;
      }
      seen.add(current);
      current = next;
    }
    return current;
  };

  // Cycle-freedom AND referential integrity in one pass, and the only referential rule there
  // is: every retired id has to end up somewhere published. `resolve` returns null both for a
  // chain that runs off the end of the map and for one that loops, so the cycle guard surfaces
  // as this failed assertion rather than as a hung request.
  const unresolved = retired.filter((id) => resolve(id) === null);
  check(
    unresolved.length === 0,
    `these aliases do not terminate on a live camp: ${unresolved.slice(0, 3).join(", ")}`,
  );
  // A miss is a miss: the map must not invent an answer for an id nobody ever published.
  check(resolve("no-such-camp-id-at-all") === null, "an unknown id resolves to null, not a guess");

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

  const surviving = resolve(stale);
  check(surviving !== null, `${stale} must still be recoverable through the alias map`);
  const survivor = await get<{ readonly kind: string; readonly id: string }>(
    template.replace("{id}", surviving),
  );
  check(survivor.kind === "camp", "the resolved id must fetch a camp document");
  check(survivor.id === surviving, "the fetched document must be the one asked for");

  // How many redirects point at another redirect, i.e. need the loop rather than one hop.
  const chained = Object.values(aliases).filter((to) => aliases[to] !== undefined).length;

  console.log(`aliases         ${retired.length} retired camp ids`);
  console.log(`stale lookup    v1/camps/${stale}.json -> 404`);
  console.log(`resolved        ${stale}`);
  console.log(`             -> ${survivor.id}`);
  console.log(`unknown id      resolve("no-such-camp-id-at-all") -> null`);
  console.log(`invariants      every key terminates on a live camp; ${chained} chain through one`);
});
