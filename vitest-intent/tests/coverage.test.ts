import { describe, expect, test } from "vitest";
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

import { collectAnnotatedTests, coverageViolations } from "../src/coverage.js";

function withTmpDir(fn: (dir: string) => void): void {
  const dir = mkdtempSync(join(tmpdir(), "vi-cov-"));
  try {
    fn(dir);
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
}

describe("collectAnnotatedTests", () => {
  test("finds a single intent() call", () => {
    withTmpDir((dir) => {
      writeFileSync(
        join(dir, "a.test.ts"),
        `
import { intent } from 'vitest-intent';
intent('INT-FOO-001', 'thing works', () => { expect(1).toBe(1); });
`,
        "utf-8",
      );
      const found = collectAnnotatedTests(dir);
      expect(found["INT-FOO-001"]).toEqual(["tests/a.test.ts::thing works"]);
    });
  });

  test("finds array form (multiple IDs per test)", () => {
    withTmpDir((dir) => {
      writeFileSync(
        join(dir, "b.test.ts"),
        `
intent(['INT-A-001', 'INT-B-001'], 'covers two', () => {});
`,
        "utf-8",
      );
      const found = collectAnnotatedTests(dir);
      expect(found["INT-A-001"]).toEqual(["tests/b.test.ts::covers two"]);
      expect(found["INT-B-001"]).toEqual(["tests/b.test.ts::covers two"]);
    });
  });

  test("ignores non-test files", () => {
    withTmpDir((dir) => {
      writeFileSync(
        join(dir, "helpers.ts"),
        `intent('INT-NO-001', 'should not be picked', () => {});`,
        "utf-8",
      );
      const found = collectAnnotatedTests(dir);
      expect(found["INT-NO-001"]).toBeUndefined();
    });
  });

  test("handles syntax noise around intent() calls", () => {
    withTmpDir((dir) => {
      writeFileSync(
        join(dir, "noisy.test.ts"),
        `
// before
const x = 1;
intent("INT-FOO-001", "first", () => {
  expect(x).toBe(1);
});
intent("INT-FOO-002", \`second with backticks\`, async () => {
  expect(2).toBe(2);
});
        `,
        "utf-8",
      );
      const found = collectAnnotatedTests(dir);
      expect(found["INT-FOO-001"]).toBeDefined();
      expect(found["INT-FOO-002"]).toBeDefined();
    });
  });
});

describe("coverageViolations", () => {
  test("uncovered claim is flagged", () => {
    const violations = coverageViolations(
      { "INT-FOO-001": {}, "INT-FOO-002": {} },
      { "INT-FOO-001": ["t"] },
    );
    expect(violations.length).toBe(1);
    expect(violations[0]).toContain("INT-FOO-002");
  });

  test("orphan test is flagged", () => {
    const violations = coverageViolations(
      { "INT-FOO-001": {} },
      { "INT-FOO-001": ["t1"], "INT-ORPHAN-001": ["t2"] },
    );
    expect(violations.some((v) => v.includes("INT-ORPHAN-001"))).toBe(true);
  });

  test("clean pass on perfect coverage", () => {
    expect(
      coverageViolations(
        { "INT-A-001": {}, "INT-B-001": {} },
        { "INT-A-001": ["t1"], "INT-B-001": ["t2"] },
      ),
    ).toEqual([]);
  });
});
