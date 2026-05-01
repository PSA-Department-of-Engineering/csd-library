/**
 * Tests for the `intent()` wrapper.
 *
 * Validation paths are tested via `validateIntentArgs` (a pure function
 * that doesn't call vitest's test() — so we can exercise it from inside
 * another test without nested-test-call errors).
 *
 * Live `intent()` calls happen at module scope at the bottom of this file.
 */

import { describe, expect, test } from "vitest";

import { intent, validateIntentArgs } from "../src/intent.js";

describe("validateIntentArgs", () => {
  test("rejects empty array of IDs", () => {
    expect(() => validateIntentArgs([], () => {})).toThrow(/at least one claim ID/);
  });

  test("rejects malformed ID (no INT- prefix)", () => {
    expect(() => validateIntentArgs("BAD-001", () => {})).toThrow(/INT-/);
  });

  test("rejects malformed ID in array form", () => {
    expect(() =>
      validateIntentArgs(["INT-OK-001", "BAD-002"], () => {}),
    ).toThrow(/INT-/);
  });

  test("requires fn unless options.todo", () => {
    expect(() => validateIntentArgs("INT-OK-001", undefined)).toThrow(/test body/);
  });

  test("accepts options.todo without fn", () => {
    expect(() =>
      validateIntentArgs("INT-OK-002", undefined, { todo: true }),
    ).not.toThrow();
  });

  test("returns normalized id list (single)", () => {
    expect(validateIntentArgs("INT-A-001", () => {})).toEqual(["INT-A-001"]);
  });

  test("returns normalized id list (array)", () => {
    expect(
      validateIntentArgs(["INT-A-001", "INT-B-001"], () => {}),
    ).toEqual(["INT-A-001", "INT-B-001"]);
  });
});

// Real intent calls — at module scope, exercising the actual wrapper.
intent("INT-VITEST-INTENT-001", "intent registers a passing test", () => {
  expect(true).toBe(true);
});

intent(
  ["INT-VITEST-INTENT-002", "INT-VITEST-INTENT-003"],
  "intent supports multiple claim IDs",
  () => {
    expect(1 + 1).toBe(2);
  },
);
