/**
 * Count what an Eagle candidate actually has to fill, using the requirement tree as a graph.
 *
 * TRAP: "how many Eagle-required merit badges are there" has three different published
 *       answers and a consumer picks one by accident. `merit-badges` flags 18 badges
 *       `eagle_required: true`; requirement 3 of the eagle-2024 edition has 14 lettered
 *       slots; the same requirement asks for 21 badges in total. Filtering the badge index on
 *       the flag and calling the result "the Eagle checklist" overstates the work by four
 *       badges, because three of those slots are either/or choices.
 * FIX:  walk the requirement tree. A child with `choose: 1` is ONE slot with alternatives, not
 *       N obligations. The flag marks the union of every badge that appears anywhere in that
 *       tree; the tree says how many of them a Scout must actually earn.
 *
 * Requirement text is (c) Scouting America and is not under this dataset's licence, so this
 * recipe reads `number`, `ref`, `choose` and `badge_count` and never touches `text`. The
 * structure is the answer here anyway.
 */

import { test } from "vitest";
import { check, endpoint, get, items } from "../osa.js";
import type { MeritBadgeIndexItem, RequirementSetDocument } from "../generated/v1.js";

// `text` is deliberately absent: a shape you cannot print by mistake is better than a rule
// you have to remember. `requirements` arrives as unknown[] because the tree is recursive and
// dataset-specific, so narrow it at the edge.
interface RequirementNode {
  readonly number: string;
  readonly ref?: string;
  readonly choose?: number;
  readonly children?: readonly RequirementNode[];
  readonly badge_count?: { readonly earn: number; readonly cumulative: number };
}

test("eagle requirement 3 is a 14-slot graph, not an 18-badge list", async () => {
  const template = await endpoint("v1/requirement-sets/{id}.json");
  const doc = await get<RequirementSetDocument>(template.replace("{id}", "eagle-2024"));

  check(doc.subject === "rank:eagle", "eagle-2024 must be a rank:eagle edition");
  check(doc.effective_to === null, "eagle-2024 must still be the edition in force");
  // The licensing carve-out travels with the document that carries the text.
  check(doc.includes_official_text, "this edition transcribes official requirement text");
  check(
    typeof doc.text_rights === "string" && doc.text_rights.includes("Scouting America"),
    "a document carrying official text must carry its rights notice",
  );

  const top = doc.requirements as readonly RequirementNode[];
  const three = top.find((r) => r.number === "3");
  check(three !== undefined, "eagle-2024 must have a requirement 3");
  const children = three.children ?? [];

  // One slot per lettered child. `choose: n` means pick n of that child's children, so the
  // alternatives collapse into the slot instead of multiplying it.
  const slots = children.map((child) => {
    const options = child.choose ? (child.children ?? []).map((g) => g.ref) : [child.ref];
    const refs = options.filter((r): r is string => typeof r === "string");
    check(refs.length === options.length, `${child.number}: a slot option with no ref`);
    check(refs.length > 0, `${child.number}: a slot with nothing in it`);
    // Every either/or node in this edition is `choose: 1`. A `choose: 2` would need a
    // different slot model, so refuse it loudly rather than silently miscount.
    check(child.choose === undefined || child.choose === 1, `${child.number}: choose must be 1`);
    return { number: child.number, choose: child.choose ?? 0, refs };
  });

  // 14 and 3 are safe to pin because a requirement-set edition is immutable: `eagle-2024` will
  // never gain a slot. A 2028 rewrite arrives as a new id with its own effective window.
  check(slots.length === 14, "eagle-2024 requirement 3 has 14 lettered slots");
  const eitherOr = slots.filter((s) => s.choose > 0);
  check(eitherOr.length === 3, "three of those slots are either/or choices");
  check(
    eitherOr.every((s) => s.refs.length >= 2),
    "an either/or slot with one option is not a choice",
  );

  const reachable = new Set(slots.flatMap((s) => s.refs));
  for (const ref of reachable) {
    check(ref.startsWith("merit-badge:"), `${ref} is not a merit-badge reference`);
  }

  const badges = await items<MeritBadgeIndexItem>("v1/merit-badges/index.json");
  const flagged = new Set(
    badges.filter((b) => b.eagle_required === true).map((b) => `merit-badge:${b.id}`),
  );

  // The two numbers are reconciled, not merely observed to differ: the flag marks exactly the
  // badges the tree can reach, and the tree says how many slots those badges compete for.
  check(flagged.size === reachable.size, "the eagle_required flag must mark every reachable badge");
  for (const ref of reachable) {
    check(flagged.has(ref), `${ref} is in the tree but not flagged eagle_required`);
  }
  check(
    flagged.size !== slots.length,
    "the flag count and the slot count answer different questions",
  );

  const total = three.badge_count;
  check(total !== undefined, "requirement 3 publishes its badge_count");
  check(total.cumulative > slots.length, "the total badge requirement exceeds the named slots");
  check(total.cumulative > total.earn, "the cumulative total includes badges already earned");

  console.log(`edition         ${doc.id} (effective ${doc.effective_from}, still in force)`);
  console.log(`slots           ${slots.length} lettered children of requirement 3`);
  for (const slot of slots) {
    const how = (slot.choose > 0 ? `choose ${slot.choose} of` : "required").padEnd(12);
    console.log(`  ${slot.number.padEnd(3)} ${how} ${slot.refs.join(" | ")}`);
  }
  console.log(`either/or       ${eitherOr.map((s) => s.number).join(", ")}`);
  console.log(`badges reached  ${reachable.size} distinct refs across those ${slots.length} slots`);
  console.log(`eagle_required  ${flagged.size} badges carry the flag -- same set, different count`);
  console.log(`badge_count     earn ${total.earn}, cumulative ${total.cumulative}`);
  console.log(`text rights     ${doc.text_rights}`);
});
