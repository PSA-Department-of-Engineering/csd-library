import { describe, expect, test } from "vitest";
import { mkdtempSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { checkSchema, parseIntentYaml } from "../src/schema.js";

function withTmpFile(content: string, fn: (path: string) => void): void {
  const dir = mkdtempSync(join(tmpdir(), "vi-"));
  const p = join(dir, "intent.yaml");
  writeFileSync(p, content, "utf-8");
  try {
    fn(p);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

describe("parseIntentYaml", () => {
  test("parses INT-prefixed top-level keys", () => {
    withTmpFile(
      `
INT-FOO-001:
  statement: "x"
  rationale: "y"
  criticality: critical
  scope: unit
INT-FOO-002:
  statement: "another"
  rationale: "because"
  criticality: high
  scope: integration
      `,
      (p) => {
        const claims = parseIntentYaml(p);
        expect(Object.keys(claims).sort()).toEqual(["INT-FOO-001", "INT-FOO-002"]);
        expect(claims["INT-FOO-001"]["statement"]).toBe("x");
      },
    );
  });

  test("ignores non-INT keys", () => {
    withTmpFile(
      `
title: "Project intent"
INT-A-001:
  statement: "x"
  rationale: "y"
  criticality: low
  scope: unit
      `,
      (p) => {
        const claims = parseIntentYaml(p);
        expect("title" in claims).toBe(false);
        expect("INT-A-001" in claims).toBe(true);
      },
    );
  });

  test("returns {} for empty file", () => {
    withTmpFile("", (p) => {
      expect(parseIntentYaml(p)).toEqual({});
    });
  });

  test("returns {} for missing file", () => {
    expect(parseIntentYaml("/nonexistent/path/intent.yaml")).toEqual({});
  });
});

describe("checkSchema", () => {
  test("passes a complete claim", () => {
    expect(
      checkSchema({
        "INT-FOO-001": {
          statement: "x",
          rationale: "y",
          criticality: "critical",
          scope: "unit",
        },
      }),
    ).toEqual([]);
  });

  test("flags missing field", () => {
    const violations = checkSchema({
      "INT-FOO-001": {
        statement: "x",
        rationale: "y",
        criticality: "critical",
        // scope missing
      },
    });
    expect(violations.length).toBe(1);
    expect(violations[0]).toContain("scope");
  });

  test("flags invalid criticality", () => {
    const violations = checkSchema({
      "INT-FOO-001": {
        statement: "x",
        rationale: "y",
        criticality: "BLOCKER",
        scope: "unit",
      },
    });
    expect(violations.some((v) => v.includes("criticality"))).toBe(true);
  });

  test("flags invalid scope", () => {
    const violations = checkSchema({
      "INT-FOO-001": {
        statement: "x",
        rationale: "y",
        criticality: "high",
        scope: "module",
      },
    });
    expect(violations.some((v) => v.includes("scope"))).toBe(true);
  });

  test("passes empty claims vacuously", () => {
    expect(checkSchema({})).toEqual([]);
  });
});
