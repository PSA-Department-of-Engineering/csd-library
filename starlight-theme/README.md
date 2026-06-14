# starlight-theme

**The shared Starlight look for every docs site, in one installable package.**

> One source of truth for the docs-site theme. Every site consumes this package instead of copy-pasting the same stylesheet and Mermaid config. Sister project to [vitest-intent](../vitest-intent), [pytest-intent](../pytest-intent), and [playwright-intent](../playwright-intent).

## What this package is

A runtime-styling package with two consumable parts:

1. **A stylesheet** (`styles.css`) with two layers:
   - a dark-mode palette override that re-hues Starlight's `:root[data-theme='dark']` base tokens to warm charcoal / cream / terracotta (mirrors Claude's app palette);
   - a token-based Mermaid contrast layer that maps the rendered `.mermaid` SVG to Starlight's `--sl-color-*` tokens, so flowcharts and sequence diagrams keep correct contrast in both light and dark.
2. **A `mermaidConfig` object** for the [`astro-mermaid`](https://www.npmjs.com/package/astro-mermaid) integration: the theme-neutral layout and font choices (flowchart curve, spacing, padding, `useMaxWidth`, font family and size). Diagram colour is not set here; it lives in the stylesheet against the `--sl-color-*` tokens, which flip with the active theme.

The CSS is fully token-based: it defines the palette once and the Mermaid layer reads Starlight tokens. There are no per-site colours.

## What it is NOT

- **Not a Starlight or Astro integration.** `astro-mermaid` must run *before* `starlight()` in the `integrations` array (it transforms ` ```mermaid ` blocks before expressive-code renders them as code). An integration that injected `astro-mermaid` on the site's behalf could not guarantee that ordering, so each site keeps its explicit `mermaid()` / `starlight()` wiring and consumes the stylesheet and config from here.
- **Not the STARLIGHT intent bundle.** This package is the *look* (CSS + Mermaid config). The [STARLIGHT intent bundle](../bundles/starlight/) is the *contract* (frontmatter + page-structure claims and their tests). They are independent: a site can adopt either, both, or neither. Changing the theme never touches intent claims, and vice versa.

## Install

Published privately to GitHub Packages under the org scope. Map the scope once (in `.npmrc`), then install by the scoped name:

```bash
echo '@psa-department-of-engineering:registry=https://npm.pkg.github.com' >> .npmrc
# auth: a read:packages PAT -> //npm.pkg.github.com/:_authToken=${NODE_AUTH_TOKEN}

npm install @psa-department-of-engineering/starlight-theme
```

The site also installs `astro-mermaid` and `mermaid` itself (this package does not pull them in; it only ships the config object they consume).

Local dev against a `csd-library` checkout (no registry/auth):

```bash
npm install --install-links ../path/to/csd-library/starlight-theme
```

`--install-links` makes npm pack the package per its `files` allowlist instead of symlinking the checkout (whose `node_modules` carries dev tooling).

## Wire it into a site

In `astro.config.mjs`, spread the `mermaidConfig` into `astro-mermaid` and point Starlight's `customCss` at the bundled stylesheet:

```js
import { defineConfig } from 'astro/config';
import mermaid from 'astro-mermaid';
import starlight from '@astrojs/starlight';
import { mermaidConfig } from '@psa-department-of-engineering/starlight-theme';

export default defineConfig({
  integrations: [
    // Must precede starlight so it transforms ```mermaid blocks before
    // expressive-code renders them as code. autoTheme follows dark/light.
    mermaid({ autoTheme: true, mermaidConfig }),
    starlight({
      title: 'My Docs',
      customCss: ['@psa-department-of-engineering/starlight-theme/styles.css'],
      // ...the rest of the site config
    }),
  ],
});
```

That is the whole integration. The `bootstrap-starlight` skill scaffolds new sites with exactly this wiring.

## Exports

| Import | What |
|---|---|
| `@psa-department-of-engineering/starlight-theme/styles.css` | The stylesheet, for Starlight `customCss`. |
| `import { mermaidConfig } from '@psa-department-of-engineering/starlight-theme'` | The theme-neutral `astro-mermaid` config object. |
| `import type { StarlightThemeMermaidConfig } from '@psa-department-of-engineering/starlight-theme'` | The type of `mermaidConfig`. |
| `import { VERSION } from '@psa-department-of-engineering/starlight-theme'` | The package version string. |

## License

MIT.
