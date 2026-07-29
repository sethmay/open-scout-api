/**
 * Expand a coarse camp feature code to everything beneath it.
 *
 * TRAP: `camps.filter(c => c.features.includes("aquatics"))` looks right and returns a
 *       plausible, badly incomplete answer. Feature codes form a hierarchy through each vocab
 *       term's `broader`, and a camp is tagged with the specific code it offers -- `kayaking`,
 *       `sailing` -- not with the parent. The camp with a lake and no generic tag vanishes.
 * FIX:  compute the TRANSITIVE closure of the chosen code over `broader`, then match a camp if
 *       any of its features is in that set. Transitive, not one level: the vocabulary is
 *       shallow today and nothing promises it stays that way.
 */

import { test } from "vitest";
import { check, endpoint, get, items } from "../osa.js";
import type { CurrentCamp } from "../generated/v1.js";

// Vocabularies are open lists published beside the entity data and are not part of the
// generated entity types, so the two fields this recipe reads are shaped locally.
interface FeatureTerm {
  readonly code: string;
  readonly label: string;
  readonly broader?: string | null;
}

interface FeatureVocab {
  readonly id: string;
  readonly open: boolean;
  readonly terms: readonly FeatureTerm[];
}

test("feature closure finds camps that exact matching misses", async () => {
  const vocab = await get<FeatureVocab>(await endpoint("v1/vocab/camp-features.json"));
  const camps = await items<CurrentCamp>("v1/current/camps.json");
  check(vocab.terms.length > 0, "the camp-features vocabulary must not be empty");

  // Invert `broader` once: the published direction is child -> parent, and expansion needs
  // parent -> children.
  const narrower = new Map<string, string[]>();
  for (const term of vocab.terms) {
    if (term.broader) {
      const kids = narrower.get(term.broader) ?? [];
      kids.push(term.code);
      narrower.set(term.broader, kids);
    }
  }

  /** `root` plus every code that reaches it through a chain of `broader`. */
  function closure(root: string): ReadonlySet<string> {
    const out = new Set([root]);
    const queue = [root];
    for (let code = queue.pop(); code !== undefined; code = queue.pop()) {
      for (const child of narrower.get(code) ?? []) {
        // The membership guard is also the cycle guard: `open: true` means a term can be
        // added by anyone, and a mis-entered `broader` must not hang a consumer's UI.
        if (!out.has(child)) {
          out.add(child);
          queue.push(child);
        }
      }
    }
    return out;
  }

  const aquatics = closure("aquatics");
  check(aquatics.has("aquatics"), "a closure contains its own root");
  check(aquatics.has("kayaking"), "the aquatics closure must contain kayaking");
  check(aquatics.has("canoeing") && aquatics.has("swimming"), "and its other water children");
  check(aquatics.size > 1, "a parent term with no children would make this recipe pointless");

  // Every member really does chain up to the root, so the closure is the hierarchy's answer
  // and not an accident of the traversal.
  const parent = new Map(vocab.terms.map((t) => [t.code, t.broader ?? null]));
  for (const code of aquatics) {
    let cursor: string | null | undefined = code;
    let hops = 0;
    while (cursor !== null && cursor !== undefined && cursor !== "aquatics" && hops < 32) {
      cursor = parent.get(cursor);
      hops += 1;
    }
    check(cursor === "aquatics", `${code} is in the closure but does not lead back to aquatics`);
  }
  check(parent.get("aquatics") === null, "aquatics is a root term, so nothing is above it");

  const exact = camps.filter((c) => c.features.includes("aquatics"));
  const expanded = camps.filter((c) => c.features.some((f) => aquatics.has(f)));

  // Supersetness is a claim about `exact`, so it has to iterate `exact`: every literally tagged
  // camp must survive the widened filter. A closure that lost codes fails here.
  const exactIds = new Set(exact.map((c) => c.id));
  const expandedIds = new Set(expanded.map((c) => c.id));
  check(
    exact.every((c) => expandedIds.has(c.id)),
    "closure matching must be a superset of exact matching",
  );
  check(expanded.length > exact.length, "closure matching must find camps exact matching misses");

  // Name one of the misses, because "you lost some rows" lands differently with a camp on it.
  const missed = expanded.find((c) => !exactIds.has(c.id));
  check(missed !== undefined, "the strict superset must contain a nameable example");
  const why = missed.features.filter((f) => aquatics.has(f)).join(", ");

  console.log(`closure         aquatics -> ${aquatics.size} codes`);
  console.log(`sample          ${[...aquatics].slice(0, 8).sort().join(", ")}`);
  console.log(`exact match     ${exact.length} camps tagged literally "aquatics"`);
  console.log(`closure match   ${expanded.length} camps offering anything aquatic`);
  console.log(`missed by exact ${missed.name} (${missed.state ?? "??"}) via ${why}`);
});
