/**
 * vitest-intent — Vitest+TypeScript implementation of CSD's Intent Specification annotation pattern.
 *
 * Public API:
 *   - intent(id, name, fn, options?) — wraps vitest's test() and binds an intent claim ID
 *   - parseIntentYaml(path) — parse + validate intent.yaml
 *   - checkSchema(claims) — schema validation
 *   - collectAnnotatedTests(dir) — find intent() calls in test files
 *   - coverageViolations(claims, annotated) — claim ↔ test mismatches
 *   - registerIntentMetaTests(options) — drop-in meta-tests (also exported from /meta-tests)
 */

export { intent, validateIntentArgs } from "./intent.js";
export type { IntentOptions } from "./intent.js";

export {
  parseIntentYaml,
  checkSchema,
  REQUIRED_FIELDS,
  VALID_CRITICALITY,
  VALID_SCOPE,
} from "./schema.js";
export type { Claim, Claims } from "./schema.js";

export {
  collectAnnotatedTests,
  coverageViolations,
} from "./coverage.js";
export type { AnnotatedTests } from "./coverage.js";

export { registerIntentMetaTests } from "./meta-tests.js";
export type { RegisterOptions } from "./meta-tests.js";

export const VERSION = "0.1.0";
