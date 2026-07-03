/**
 * vitest-intent - the `intent()` wrapper that links a vitest test to a CSD claim.
 *
 * Validation, coverage, and orphan-detection live in the separate `csd-intent`
 * CLI (standalone, Python), not here. This package is intentionally small: it
 * only exposes the marker; auditing is somebody else's job.
 */

export { intent, validateIntentArgs } from './intent.js';
export type { IntentOptions } from './intent.js';

export const VERSION = '0.2.0';
