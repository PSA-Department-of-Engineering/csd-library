/**
 * Tests for the shared Starlight theme package.
 *
 * Two consumable surfaces, two things to guard:
 *   - `mermaidConfig` carries only theme-neutral layout/font choices (no colour);
 *   - `styles.css` re-hues the dark base ramp and maps the Mermaid layer to
 *     Starlight tokens (no per-site hardcoded colours in the diagram layer).
 *
 * Each test attests its claim in intent.yaml (CSD-INTENT-01) via intent().
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { intent } from "@psa-department-of-engineering/vitest-intent";
import { describe, expect } from "vitest";

import { mermaidConfig } from "../src/index.js";

describe("mermaidConfig", () => {
  intent("INT-SLT-001", "carries only theme-neutral layout + font choices", () => {
    expect(mermaidConfig).toEqual({
      flowchart: { curve: "basis", nodeSpacing: 50, rankSpacing: 60, padding: 14, useMaxWidth: true },
      themeVariables: { fontFamily: "ui-sans-serif, system-ui, sans-serif", fontSize: "14px" },
    });
  });

  intent("INT-SLT-002", "sets no diagram colour (colour lives in styles.css against --sl-color-* tokens)", () => {
    const json = JSON.stringify(mermaidConfig);
    expect(json).not.toMatch(/#[0-9a-fA-F]{3,6}\b/);
    expect(json).not.toMatch(/\b(hsl|rgb|rgba|oklch)\(/);
  });
});

describe("styles.css", () => {
  const css = readFileSync(fileURLToPath(new URL("../styles.css", import.meta.url)), "utf8");

  intent("INT-SLT-003", "re-hues the dark base ramp (warm palette override)", () => {
    expect(css).toContain(":root[data-theme='dark']");
    expect(css).toContain("--sl-color-accent");
  });

  intent("INT-SLT-004", "maps the Mermaid layer to Starlight tokens", () => {
    expect(css).toContain("--mmd-node");
    expect(css).toContain("var(--sl-color-");
  });

  intent("INT-SLT-005", "the Mermaid layer references no hardcoded colours", () => {
    // The dark-palette block legitimately defines the theme's colours once; the
    // Mermaid layer below it must be purely token-based. Assert on that section.
    const mermaidLayer = css.slice(css.indexOf(".mermaid {"));
    expect(mermaidLayer.length).toBeGreaterThan(0);
    expect(mermaidLayer).not.toMatch(/:\s*#[0-9a-fA-F]{3,6}\b/);
    expect(mermaidLayer).not.toMatch(/:\s*(hsl|rgb|rgba|oklch)\(/);
  });
});
