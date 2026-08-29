# ADR-0001: Private distribution of csd-library packages

- **adr_status:** Superseded
- **Date:** 2026-06-11
- **Deciders:** Rafael Pires
- **Applies to:** `vitest-intent`, `pytest-intent`, `csd-intent` (and future intent packages in this repo)
- **Superseded by:** [ADR-0003](0003-public-npm-distribution.md) (npm half) and [ADR-0004](0004-public-pypi-distribution.md) (Python half) — **fully superseded**

> **The npm decision below no longer holds.** GitHub Packages requires an auth token to read even a public package, so the arrangement here survived the repo going public as friction with nothing left to protect — and it made any consumer repo unforkable. npm packages now ship to the public npm registry under the same scope; see [ADR-0003](0003-public-npm-distribution.md).
>
> **The Python decision below no longer holds either.** The pinned git-tag install carried this repo's owner, name, and tag into every consumer's conformance gate; the packages now ship to PyPI as `csd-intent` and `csd-pytest-intent` via trusted publishing, and consumers use an ordinary version constraint. See [ADR-0004](0004-public-pypi-distribution.md). The per-package SemVer and the `<pkg>-vX.Y.Z` tag namespace described below remain current.

## Context

`csd-library` is a monorepo that ships reusable intent-testing packages consumed by sibling projects:

- `vitest-intent` - npm package (ESM, built with `tsc`).
- `pytest-intent`, `csd-intent` - pure-Python packages (setuptools).

Consumers historically referenced them by sibling path - `"vitest-intent": "file:../../csd-library/vitest-intent"` and `pip install -e ../csd-library/<pkg>`. This is **not fresh-clone reproducible**:

- `vitest-intent`'s entrypoint is `dist/index.js`, but `dist/` is built by `tsc` and is gitignored, so a freshly cloned consumer cannot resolve the package until someone manually runs the build.
- The editable Python installs assume the exact sibling-clone layout on disk.

We want consumers to install these as **normal, versioned, private dependencies**, reproducible from a clean checkout. Constraints: solo maintainer; GitHub org `PSA-Department-of-Engineering` (where this repo lives); a single-node k3s homelab. Cost should stay near zero and operational burden minimal.

## Decision

### npm (`vitest-intent`, future JS/TS packages) → GitHub Packages, scoped to the owning org

- The package name is scoped to the GitHub owner of this repo: `@psa-department-of-engineering/vitest-intent`.
  - **Portable rule:** the npm scope is the owning org's GitHub login, lowercased. `@psa-department-of-engineering` is the concrete value for this deployment; a fork re-points the scope to its own owner in one place.
- Published to `https://npm.pkg.github.com` (via `publishConfig.registry`). Private visibility is inherited from the repository.
- The existing `prepublishOnly: tsc` + `files: ["dist", ...]` already build `dist/` and bundle it into the tarball, so the published artifact is self-contained. This - not committing `dist/` - is the actual fix for the uncommitted-build problem; `dist/` stays gitignored.

### Python (`pytest-intent`, `csd-intent`) → pinned git-tag installs (no registry)

- Consumers depend via a PEP 508 direct reference at a tag, using the monorepo subdirectory:
  `pkg @ git+https://github.com/PSA-Department-of-Engineering/csd-library.git@<tag>#subdirectory=<pkg>`
- `pip` builds the wheel from source at install time (both packages are pure-Python), so "publishing" is just pushing a tag - no build/upload step, no index to host.
- **Why the npm/Python asymmetry:** `pip` has first-class support for installing a subdirectory of a git repo at a tag; npm's git support does not handle monorepo subdirectories cleanly. npm therefore benefits from a real registry while Python does not need one.

### Versioning

SemVer per package, versioned independently. Git tags are per-package prefixed: `<pkg>-vX.Y.Z` (e.g. `vitest-intent-v0.2.0`, `pytest-intent-v0.2.0`). A single `vX.Y.Z` namespace cannot represent three independently-versioned packages in one repo.

### Not self-hosting a registry (Verdaccio / devpi) in the homelab - for now

A single-node homelab behind a Cloudflare tunnel would become a hard dependency for every `npm install` / `pip install` / CI run. GitHub Packages + git-tags lean on infrastructure GitHub already runs. Revisit self-hosting when any of these become true: multiple contributors, many packages, a need for bare-name `pip install <pkg>` from a private index, or wanting a pull-through cache of the public registries.

## Consequences

- **Consumers need auth.** npm: a `read:packages` GitHub PAT referenced from `.npmrc`. pip: git auth to the private repo (SSH, or a token via `git config url.<...>.insteadOf`).
- **npm consumers import the scoped name directly.** The dependency is declared and imported under its published scoped name (`@psa-department-of-engineering/vitest-intent`); `.npmrc` maps the scope to GitHub Packages. An `npm:` alias to a bare specifier (`"vitest-intent": "npm:@psa-department-of-engineering/vitest-intent@^0.2.0"`) is **discouraged**: it creates two names for one package, so a later direct or `file:` install resolves the real scoped name and the bare import breaks. The playbook generators and all consumers use the scoped name directly.
- **Generic source stays portable.** Only the published artifact's identity and the consumer's dependency declaration name the org. The package source and CSD methodology carry no deployment coupling; a fork re-points scope/URLs in one place.
- **Migration.** Consumers move off `file:` / `-e` to versioned deps (npm `^X.Y.Z`, pip git-tag URL). `npm link` / `pip install -e` remain available as a local-dev escape hatch for working against unreleased changes, but the committed state is always the versioned dependency. For an npm `file:` install of a package that bundles dev peers, use `npm install --install-links` so npm packs per the `files` allowlist instead of symlinking the checkout's `node_modules` (which would otherwise duplicate a peer such as `@playwright/test` → *"Requiring @playwright/test second time"*).
- **A future public release** (npm / PyPI under a neutral name) would be a separate distribution identity; it neither blocks nor conflicts with this private setup.

## Alternatives considered

| Option | Why not (now) |
|---|---|
| Self-hosted Verdaccio (npm) in k3s | Allows unscoped private names, but makes every install / CI run depend on single-node homelab uptime. Revisit for multi-dev. |
| Self-hosted devpi (Python) in k3s | Same uptime coupling; only needed if bare-name `pip install` matters. |
| npm paid private registry | GitHub Packages is free for private repos under the org. |
| Gemfury / AWS CodeArtifact (Python) | Paid / extra account for two internal pure-Python packages. |
| `npm install` from a git subdirectory | npm git support does not handle monorepo subdirectories cleanly (unlike pip's `#subdirectory=`). |

## Rollout

All four packages published and install-verified (2026-06-11):

- `@psa-department-of-engineering/vitest-intent` 0.2.0 → GitHub Packages, tag `vitest-intent-v0.2.0`.
- `@psa-department-of-engineering/playwright-intent` 0.1.0 → GitHub Packages, tag `playwright-intent-v0.1.0`.
- `pytest-intent` 0.2.0 → git tag `pytest-intent-v0.2.0`.
- `csd-intent` 0.1.0 → git tag `csd-intent-v0.1.0`.

Consumers migrated off `file:`/`-e`: git-switchboard, SolveOS (night-approver + foundry-platform applied in working tree, pending commit alongside in-progress work). The `bootstrap-*` generators and the `apply-intent-bundle` validator emit/accept the published installs.
