import { defineConfig } from "vitest/config";

// Recipes are documentation first and tests second, so the reporter's captured console output
// is part of the artifact, not noise.
export default defineConfig({
  test: {
    include: ["src/recipes/*.test.ts"],
    // `verbose` because the recipes' printed output IS the artifact: a reader who runs
    // `npm test` should see the answers, not just six green ticks.
    reporters: ["verbose"],
    // Every recipe talks to a real API over HTTP. CI points OSA_BASE at a loopback server, but
    // a reader running these against the published host is on someone else's network.
    testTimeout: 60_000,
    hookTimeout: 60_000,
  },
});
