/**
 * playwright-intent - the `intent()` wrapper that links a Playwright e2e test
 * to a CSD intent claim.
 *
 * Validation, coverage, and orphan-detection live in the separate `csd-intent`
 * CLI (standalone, Python), not here. This package is intentionally small: it
 * only exposes the marker; auditing is somebody else's job.
 */

export { intent, validateIntentArgs } from './intent.js';
export type { IntentOptions } from './intent.js';

export const VERSION = '0.1.0';
