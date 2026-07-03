/**
 * The `intent()` function - a thin wrapper around Playwright's `test()` that
 * binds a CSD intent claim ID to an e2e test.
 *
 * Usage:
 *   import { intent } from '@psa-department-of-engineering/playwright-intent';
 *
 *   intent('INT-SB-E01', 'clicking Pull all refreshes status', async ({ page }) => {
 *     await page.goto('http://localhost:5173');
 *     await page.getByRole('button', { name: 'Pull all' }).click();
 *     await expect(page.getByText('REPOSITORIES')).toBeVisible();
 *   });
 *
 * The ID is recorded in the test's source so the csd-intent walker
 * (which uses regex on test files) can map claims to tests.
 *
 * For skip / only / fixme variants, call Playwright's `test.skip(name, fn)` etc
 * directly - the intent marker only covers the regular `test(name, fn)` path.
 */

import { test, type PlaywrightTestArgs, type TestInfo } from '@playwright/test';

const INTENT_ID_RE = /^INT-[A-Z0-9-]+$/;

/**
 * A Playwright test body. Mirrors the internal `TestBody<TestArgs>` Playwright
 * uses for its `test(title, body)` overload. The args parameter is intentionally
 * loose so user fixtures (custom extensions of `test`) are forwarded transparently.
 */
export type IntentTestBody = (
    args: PlaywrightTestArgs & Record<string, unknown>,
    testInfo: TestInfo,
) => void | Promise<void>;

export interface IntentOptions {
    // Reserved for future use. For skip / only / fixme variants, call Playwright's
    // test.skip / test.only / test.fixme directly - their overloads are too
    // ambiguous to forward generically through a single helper.
    _reserved?: never;
}

/**
 * Validates the args to `intent()`. Exported for direct unit testing without
 * triggering Playwright's `test()` registration.
 *
 * Throws if invalid; returns the normalized list of IDs if valid.
 */
export function validateIntentArgs(
    id: string | readonly string[],
    fn: IntentTestBody | undefined,
    options: IntentOptions = {},
): string[] {
    const ids = Array.isArray(id) ? [...id] : [id as string];
    if (ids.length === 0) {
        throw new Error('intent() requires at least one claim ID');
    }
    for (const cid of ids) {
        if (!INTENT_ID_RE.test(cid)) {
            throw new Error(`intent() claim ID must match /^INT-[A-Z0-9-]+$/, got: ${cid}`);
        }
    }
    if (!fn) {
        throw new Error('intent() requires a test body');
    }
    void options;
    return ids;
}

/**
 * Wraps Playwright's `test()` and binds an intent claim ID.
 *
 * Multiple intent IDs per test: pass an array as the first arg.
 */
export function intent(
    id: string | readonly string[],
    name: string,
    fn: IntentTestBody,
    options: IntentOptions = {},
): void {
    validateIntentArgs(id, fn, options);
    // The `(title, body)` overload is what we always want. Cast via unknown is
    // needed because Playwright's `test()` has multiple overloads with strict
    // generic constraints - our loose `IntentTestBody` deliberately forwards any
    // user fixtures, which TS can't reconcile with the strict overload set.
    (test as unknown as (title: string, body: IntentTestBody) => void)(name, fn);
}
