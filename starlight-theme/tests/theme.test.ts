/**
 * Tests for the shared Starlight theme package.
 *
 * Two consumable surfaces, two things to guard:
 *   - `mermaidConfig` carries only theme-neutral layout/font choices (no colour);
 *   - `styles.css` re-hues the dark base ramp and maps the Mermaid layer to
 *     Starlight tokens (no per-site hardcoded colours in the diagram layer).
 */

import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";

import { describe, expect, test } from "vitest";

import { mermaidConfig } from "../src/index.js";

describe("mermaidConfig", () => {
  test("carries only theme-neutral layout + font choices", () => {
    expect(mermaidConfig).toEqual({
      flowchart: { curve: "basis", nodeSpacing: 50, rankSpacing: 60, padding: 14, useMaxWidth: true },
      themeVariables: { fontFamily: "ui-sans-serif, system-ui, sans-serif", fontSize: "14px" },
    });
  });

  test("sets no diagram colour (colour lives in styles.css against --sl-color-* tokens)", () => {
    const json = JSON.stringify(mermaidConfig);
    expect(json).not.toMatch(/#[0-9a-fA-F]{3,6}\b/);
    expect(json).not.toMatch(/\b(hsl|rgb|rgba|oklch)\(/);
  });
});

describe("styles.css", () => {
  const css = readFileSync(fileURLToPath(new URL("../styles.css", import.meta.url)), "utf8");

  test("re-hues the dark base ramp (warm palette override)", () => {
    expect(css).toContain(":root[data-theme='dark']");
    expect(css).toContain("--sl-color-accent");
  });

  test("maps the Mermaid layer to Starlight tokens", () => {
    expect(css).toContain("--mmd-node");
    expect(css).toContain("var(--sl-color-");
  });

  test("the Mermaid layer references no hardcoded colours", () => {
    // The dark-palette block legitimately defines the theme's colours once; the
    // Mermaid layer below it must be purely token-based. Assert on that section.
    const mermaidLayer = css.slice(css.indexOf(".mermaid {"));
    expect(mermaidLayer.length).toBeGreaterThan(0);
    expect(mermaidLayer).not.toMatch(/:\s*#[0-9a-fA-F]{3,6}\b/);
    expect(mermaidLayer).not.toMatch(/:\s*(hsl|rgb|rgba|oklch)\(/);
  });
});
