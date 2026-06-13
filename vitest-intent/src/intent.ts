/**
 * The `intent()` function — a thin wrapper around vitest's `test()` that
 * binds a CSD intent claim ID to a test case.
 *
 * Usage:
 *   import { intent } from '@psa-department-of-engineering/vitest-intent';
 *
 *   intent('INT-FOO-001', 'thing must be true', () => {
 *     expect(thing).toBe(true);
 *   });
 *
 * The ID is recorded in the test's source so the coverage walker
 * (which uses regex on test files) can map claims ↔ tests.
 */

import { test } from "vitest";

const INTENT_ID_RE = /^INT-[A-Z0-9-]+$/;

export interface IntentOptions {
  /** Marks the test as `skip` while keeping the intent linkage. */
  skip?: boolean;
  /** Marks the test as `only` while keeping the intent linkage. */
  only?: boolean;
  /** Marks the test as `todo` (no body). */
  todo?: boolean;
}

/**
 * Validates the args to `intent()`. Exported for direct unit testing without
 * triggering vitest's `test()` registration.
 *
 * Throws if invalid; returns the normalized list of IDs if valid.
 */
export function validateIntentArgs(
  id: string | readonly string[],
  fn?: (() => void | Promise<void>) | undefined,
  options: IntentOptions = {},
): string[] {
  const ids = Array.isArray(id) ? [...id] : [id as string];
  if (ids.length === 0) {
    throw new Error("intent() requires at least one claim ID");
  }
  for (const cid of ids) {
    if (!INTENT_ID_RE.test(cid)) {
      throw new Error(
        `intent() claim ID must match /^INT-[A-Z0-9-]+$/, got: ${cid}`,
      );
    }
  }
  if (!options.todo && !fn) {
    throw new Error(
      "intent() requires a test body unless options.todo is true",
    );
  }
  return ids;
}

/**
 * Wraps `vitest.test()` and binds an intent claim ID.
 *
 * Multiple intent IDs per test: pass an array as the first arg.
 */
export function intent(
  id: string | readonly string[],
  name: string,
  fn?: () => void | Promise<void>,
  options: IntentOptions = {},
): void {
  validateIntentArgs(id, fn, options);

  if (options.todo) {
    test.todo(name);
    return;
  }
  if (options.skip) {
    test.skip(name, fn!);
    return;
  }
  if (options.only) {
    test.only(name, fn!);
    return;
  }
  test(name, fn!);
}
