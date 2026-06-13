# vitest-intent

**The `intent()` wrapper for vitest — links a test to one or more CSD intent claims.**

> CSD (Cognitive Software Delivery) is a language-agnostic methodology. This package is one specific implementation, scoped to Node/TypeScript projects using vitest. Sister project to [pytest-intent](../pytest-intent) and [playwright-intent](../playwright-intent).

## What this package is

A tiny TypeScript library (~80 LOC) that exposes a single helper:

```typescript
import { expect } from 'vitest';
import { intent } from '@psa-department-of-engineering/vitest-intent';

intent('INT-FOO-001', 'rejects empty passwords', () => {
    expect(authenticate('user', '')).toBe(false);
});

// Multi-claim per test:
intent(['INT-FOO-002', 'INT-FOO-003'], 'parses and validates the token', () => {
    /* ... */
});
```

That's the entire public surface. `intent()` is a thin wrapper around vitest's `test()` — it validates the claim ID, then delegates to the underlying `test(name, fn)`.

## What it is NOT

- **Not a validator.** Schema checks (CSD-INTENT-01), orphan detection (test references unknown claim), and cross-runtime coverage all live in the standalone [`csd-intent`](../csd-intent) CLI — point it at any project to audit.
- **Not a vitest plugin.** Just a function. No config, no setup files.
- **Not a generator.** You write your tests; this annotates them.

## Why split the wrapper from the auditor?

- **One concern per package.** The wrapper runs inside vitest; the auditor is cross-language and runs standalone (CI step, pre-commit, ad-hoc).
- **Same `intent()` shape across runtimes.** vitest-intent, pytest-intent, and playwright-intent all expose the same marker. The auditor reads all of them, regardless of which package put the marker there.
- **Tiny install.** vitest-intent has no runtime dependencies beyond `vitest` itself.

## Install

Published privately to GitHub Packages under the org scope. Map the scope once (in `.npmrc`), then install by the scoped name:

```bash
echo '@psa-department-of-engineering:registry=https://npm.pkg.github.com' >> .npmrc
# auth: a read:packages PAT → //npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}

npm install --save-dev vitest @psa-department-of-engineering/vitest-intent
```

Local dev against a `csd-library` checkout (no registry/auth):

```bash
npm install --save-dev --install-links ../path/to/csd-library/vitest-intent
```

`--install-links` makes npm pack the package per its `files` allowlist instead of symlinking the checkout (whose `node_modules` carries a dev `vitest`).

Peer dependency: `vitest >= 1.0`.

## Companion: csd-intent

To validate your `intent.yaml` against CSD-INTENT-01 and check that every claim has a test:

```bash
pip install csd-intent
csd-intent /path/to/your/project
```

See [csd-intent README](../csd-intent/README.md) for full options.

## License

MIT.
