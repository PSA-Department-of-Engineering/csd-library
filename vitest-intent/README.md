# vitest-intent

Vitest+TypeScript implementation of [CSD](https://github.com/rafael-pires/csd)'s Intent Specification annotation pattern. Sister project to [pytest-intent](https://github.com/rafael-pires/pytest-intent).

## Why

In CSD, intent claims (declarative truth statements about what must be correct) are bound to executable tests. This package provides:

1. An `intent()` wrapper for vitest's `test()` — binds a claim ID to each test
2. Schema validation for `intent.yaml` files
3. Meta-tests that enforce 1:1 between claim IDs and test functions

## Install

```bash
npm install --save-dev vitest-intent
```

Peer dependency: `vitest >=1.0`.

## Use

### 1. Declare intent claims

`intent.yaml` at your project root:

```yaml
INT-FOO-001:
  statement: "Authentication fails fast on invalid credentials"
  rationale: "Brute-force resistance hinges on this"
  criticality: critical
  scope: unit
```

### 2. Bind tests to claims

`tests/auth.test.ts`:

```typescript
import { expect } from "vitest";
import { intent } from "vitest-intent";

intent("INT-FOO-001", "rejects empty credentials", () => {
  expect(authenticate("", "")).toBe(false);
});
```

Multiple claims per test:

```typescript
intent(["INT-A-001", "INT-B-001"], "covers two claims", () => { /* ... */ });
```

Skipped / only / todo flags:

```typescript
intent("INT-FOO-002", "todo", undefined, { todo: true });
intent("INT-FOO-003", "skipped", () => {}, { skip: true });
```

### 3. Wire up the meta-tests

`tests/meta.test.ts`:

```typescript
import { registerIntentMetaTests } from "vitest-intent/meta-tests";
import path from "node:path";

registerIntentMetaTests({ packRoot: path.join(__dirname, "..") });
```

This registers two tests:
- **`intent.schema`** — every claim in `intent.yaml` has required fields (`statement`, `rationale`, `criticality`, `scope`) and valid values
- **`intent.coverage`** — every claim has a test, every annotated test references a real claim

Both pass vacuously when no claims are declared (empty/missing `intent.yaml`).

### Multi-file / multi-dir layouts

```typescript
registerIntentMetaTests({
  intentYamlPaths: [
    path.join(root, "intent", "users.yaml"),
    path.join(root, "intent", "auth.yaml"),
  ],
  testsDirs: [
    path.join(root, "src", "users", "tests"),
    path.join(root, "src", "auth", "tests"),
  ],
});
```

## Public API

```typescript
import {
  intent,
  validateIntentArgs,
  parseIntentYaml,
  checkSchema,
  collectAnnotatedTests,
  coverageViolations,
  registerIntentMetaTests,
  REQUIRED_FIELDS,
  VALID_CRITICALITY,
  VALID_SCOPE,
  VERSION,
} from "vitest-intent";
```

| Export | What it does |
|---|---|
| `intent(id, name, fn, options?)` | Wraps `vitest.test()`, binds an intent claim ID. Throws on malformed ID. |
| `validateIntentArgs(id, fn, options?)` | Pure validator (no test() registration); useful for unit-testing your own intent calls. |
| `parseIntentYaml(path)` | Reads and parses `intent.yaml`; returns `{INT-XXX: {field: value}}`. |
| `checkSchema(claims)` | Validates required fields + valid criticality/scope. Returns violation strings. |
| `collectAnnotatedTests(dir)` | Walks test files, finds `intent(...)` calls. Returns `{INT-XXX: ["file::name"]}`. |
| `coverageViolations(claims, annotated)` | Returns claim ↔ test mismatches as strings. |
| `registerIntentMetaTests(options?)` | Drop-in: registers schema + coverage meta-tests. |

## Schema

```yaml
INT-<TOPIC>-<NNN>:
  statement: <string>      # required — what must be true
  rationale: <string>      # required — why this matters
  criticality: critical|high|medium|low    # required
  scope: unit|integration|e2e|system       # required
  # optional fields are allowed; not validated
```

ID format: `INT-` prefix + uppercase + digits + dashes. Topic-prefix convention (`INT-AUTH-001`) is recommended for clarity but not enforced.

## How coverage detection works

`collectAnnotatedTests` walks files matching `*.test.*` / `*.spec.*` (with .ts/.tsx/.mts/.cts/.js/.jsx/.mjs/.cjs extensions) and uses regex to find calls of the form:

```
intent('INT-XXX', 'name', ...)
intent("INT-XXX", "name", ...)
intent(['INT-A', 'INT-B'], 'name', ...)
```

No TypeScript compiler dependency. Trade-off: if you alias `intent` to another name (`import { intent as foo }`), the regex won't find calls. Use the canonical name.

## Caveats

- **Coverage walker is regex-based**, not AST. Some pathological cases (intent calls inside string literals, dynamic IDs) won't be detected accurately. For 99% of real test code this is fine.
- **`intent()` calls vitest's `test()` at module load**, which means it must be at module scope, not inside another `test()`. Nested test calls aren't allowed by vitest. Use `validateIntentArgs` if you need to test the validation in isolation.
- **Single-language scope.** Cross-language CSD bundles need a separate runtime per language. The Python sister is [pytest-intent](https://github.com/rafael-pires/pytest-intent).

## License

MIT — see LICENSE.
