/**
 * The single host global this workspace touches, declared here instead of installing
 * @types/node.
 *
 * That is not miserliness: osa.ts is meant to be copied into a browser, Deno or Workers app
 * unchanged, and a dependency list that says "node" would misdescribe what it needs. One
 * environment variable is the entire runtime requirement.
 */
declare const process: {
  readonly env: Readonly<Record<string, string | undefined>>;
};
