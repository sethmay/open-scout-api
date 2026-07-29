/**
 * Shared plumbing for the TypeScript cookbook recipes. No runtime dependencies.
 *
 * This is the mirror of cookbook/python/osa.py and it keeps the same split: only the boring
 * parts live here -- resolving the base, fetching and decoding JSON, reading the discovery
 * document, and a check helper. The interesting per-dataset logic lives inline in each recipe,
 * because that logic is what a consumer has to copy into their own app; hiding it behind a
 * helper would defeat the point of the cookbook.
 *
 * Base resolution order:
 *   1. $OSA_BASE          -- what the CI runner sets (a local http://127.0.0.1:PORT)
 *   2. the published host -- provisional pre-1.0, hence never hardcoded in a recipe
 */

import type { CurrentCollection, IndexCollection, Meta } from "./generated/v1.js";

// Provisional pre-1.0: the base URL is expected to move (see TODO.md "v1.0 readiness"), which
// is exactly why this string appears once, here, and in no recipe.
export const DEFAULT_BASE = "https://sethmay.github.io/open-scout-api";

export const USER_AGENT = "open-scout-api-cookbook (+https://github.com/sethmay/open-scout-api)";

let metaCache: Meta | undefined;

/** A recipe's invariant did not hold. */
export class CheckError extends Error {
  override readonly name = "CheckError";
}

/**
 * Assert an invariant.
 *
 * Recipes assert invariants, never record counts: the dataset grows every week, so
 * `camps.length === 448` is a time bomb while `closure.has("kayaking")` is a real contract.
 * This is a plain throw rather than a test-framework matcher so a recipe keeps working when
 * it is lifted out of vitest and pasted into an application.
 */
export function check(cond: unknown, msg: string): asserts cond {
  if (!cond) {
    throw new CheckError(msg);
  }
}

/** The API root, without a trailing slash. */
export function base(): string {
  const env = process.env["OSA_BASE"];
  const root = env !== undefined && env !== "" ? env : DEFAULT_BASE;
  return root.replace(/\/+$/, "");
}

/** Fetch and decode one published JSON file. `path` is relative, e.g. `v1/meta.json`. */
export async function get<T>(path: string): Promise<T> {
  const url = `${base()}/${path.replace(/^\/+/, "")}`;
  const res = await fetch(url, { headers: { "user-agent": USER_AGENT } });
  // A 404 handled as "empty" is how a consumer silently loses a whole dataset, so surface it.
  if (!res.ok) {
    throw new Error(`GET ${url} -> ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

/** The discovery document, fetched once per process. */
export async function meta(): Promise<Meta> {
  metaCache ??= await get<Meta>("v1/meta.json");
  return metaCache;
}

/**
 * Look a templated endpoint up in `meta.endpoints` instead of assuming it exists.
 *
 * Returns the template itself (e.g. `v1/councils/{id}.json`) so a caller can fill it in.
 * Throws if the running API does not publish it -- which is the point: a consumer pinned to
 * an endpoint that went away should fail loudly rather than 404 silently per-request.
 */
export async function endpoint(template: string): Promise<string> {
  const { endpoints } = await meta();
  if (!endpoints.includes(template)) {
    throw new Error(`${template} is not published; meta lists ${endpoints.length} endpoints`);
  }
  return template;
}

/**
 * The `items` array of a collection projection, with the envelope discarded.
 *
 * Every `v1/current/*.json` and `v1/{dataset}/index.json` file shares the envelope
 * `{$schema, version, generated_at, kind, count, items[]}`. The envelope also carries the
 * discriminator that says what the items ARE -- see recipes/kind-discrimination.test.ts for
 * the typed narrowing this convenience wrapper deliberately skips.
 */
export async function items<T>(path: string): Promise<readonly T[]> {
  const doc = await get<CurrentCollection | IndexCollection>(path);
  check(doc.count === doc.items.length, `${path}: count disagrees with items length`);
  return doc.items as readonly T[];
}
