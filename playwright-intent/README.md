# playwright-intent

**The `intent()` wrapper for Playwright - links an e2e test to one or more CSD intent claims.**

> CSD (Cognitive Software Delivery) is a language-agnostic methodology. This package is one specific implementation, scoped to browser-driven end-to-end tests using Playwright. Sister project to [pytest-intent](../pytest-intent) and [vitest-intent](../vitest-intent).

## What this package is

A tiny TypeScript library (~70 LOC) that exposes a single helper:

```typescript
import { expect } from '@playwright/test';
import { intent } from '@psa-department-of-engineering/playwright-intent';

intent('INT-SB-E01', 'clicking Pull all refreshes status', async ({ page }) => {
    await page.goto('http://localhost:5173');
    await page.getByRole('button', { name: 'Pull all' }).click();
    await expect(page.getByText('REPOSITORIES')).toBeVisible();
});

// Multi-claim per test:
intent(
    ['INT-SB-E02', 'INT-SB-E03'],
    'stash on dirty repo updates badge',
    async ({ page }) => {
        /* ... */
    },
);
```

That's the entire public surface. `intent()` is a thin wrapper around Playwright's `test()` - it validates the claim ID, then delegates to `test(name, fn)`. All Playwright fixtures (`page`, `request`, `context`, etc.) are forwarded transparently.

## What it is NOT

- **Not a validator.** Schema checks (CSD-INTENT-01), orphan detection, and cross-runtime coverage all live in the standalone [`csd-intent`](../csd-intent) CLI - point it at any project to audit.
- **Not a Playwright plugin.** Just a function. No config, no setup files.
- **Not a generator.** You write your tests; this annotates them.

## Why split the wrapper from the auditor?

- **Same `intent()` shape across runtimes.** vitest-intent, pytest-intent, and playwright-intent all expose the same marker. The auditor reads all of them, regardless of which package put the marker there.
- **Tiny install.** No runtime deps beyond `@playwright/test`.
- **e2e tests are just another runtime.** The methodology doesn't care whether a claim is attested by a unit test, integration test, or e2e - it just needs at least one marker somewhere.

## Install

Published to the public npm registry. No `.npmrc` and no token — install it like any other package:

```bash
npm install --save-dev @playwright/test @psa-department-of-engineering/playwright-intent
npx playwright install   # one-time browser install (~300MB)
```

Local dev against a `csd-library` checkout:

```bash
npm install --save-dev --install-links ../path/to/csd-library/playwright-intent
```

`--install-links` makes npm pack the package per its `files` allowlist instead of symlinking the checkout. Without it, the checkout's dev copy of `@playwright/test` is pulled in and Playwright throws *"Requiring @playwright/test second time"*.

Peer dependency: `@playwright/test >= 1.40`.

## Companion: csd-intent

To validate your `intent.yaml` against CSD-INTENT-01 and check that every claim has a test:

```bash
pip install csd-intent
csd-intent /path/to/your/project
```

See [csd-intent README](../csd-intent/README.md) for full options.

## License

MIT.
