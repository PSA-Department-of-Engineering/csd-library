# ADR-0002: Release automation via release-please

- **adr_status:** Decided
- **Date:** 2026-06-13
- **Deciders:** Rafael Pires
- **Applies to:** `vitest-intent`, `playwright-intent`, `pytest-intent`, `csd-intent` (and future packages in this repo)
- **Relates to:** [ADR-0001](0001-private-package-distribution.md) (distribution targets); the homelab platform's ADR-024 (release automation for deployable services)

## Context

[ADR-0001](0001-private-package-distribution.md) settled *where* each package goes (npm to GitHub Packages; Python via git-tag installs) and *how* it is versioned (per-package SemVer, tags `<pkg>-vX.Y.Z`). It did not settle *how a release is cut*. Until now that was manual: bump the version by hand, tag, then `npm publish` or push the tag. The npm versions already drifted ahead of their tags this way (`vitest-intent` 0.2.1 and `playwright-intent` 0.1.1 in source, last tags `…-v0.2.0` / `…-v0.1.0`), which is the exact failure mode automation removes.

The org already automates releases for **deployable services** (homelab ADR-024): semantic-release computes a SemVer from Conventional Commits and cuts it automatically on push to `main`, with no PR. We want the same "version from commits, for free" property here.

But `csd-library` is not a service. It is a **polyglot, multi-package monorepo**: four independently-versioned packages, two npm and two Python, in one repo. semantic-release models one version per repo. Its monorepo plugin (`semantic-release-monorepo`) derives the tag from `package.json`'s `name`, so the npm packages would tag as `@psa-department-of-engineering/vitest-intent-v…` (scope and all, not the `vitest-intent-v…` of ADR-0001), and it is JS-only, with no way to version the Python packages from `pyproject.toml`.

## Decision

Use **release-please** (manifest mode) for this repo, run through a new reusable workflow `library.yml` in the shared `ci` repo, called by a thin `release.yml` here on push to `main`.

- **Per-package, polyglot.** `release-please-config.json` maps each package path to a release type (`node` / `python`) and a `component`; `.release-please-manifest.json` holds current versions. Tags are `<component>-v<version>`, matching ADR-0001 exactly.
- **PR-gated cut.** release-please maintains a per-package "release PR" from Conventional Commits. Merging it cuts the tag, GitHub release, and CHANGELOG. The merge is the release gate, and the repo's `test.yml` runs on that PR.
- **Publish.** On a cut, npm packages are published to GitHub Packages by `library.yml`; Python packages need no publish step (the tag is the release, per ADR-0001).
- **Authoring is unchanged.** Contributors still push straight to `main`; the only PR is the bot's release PR. This repo is therefore the deliberate exception to the org norm of "no mandated PRs, each team owns its flow" (ADR-024): the exception is one bot PR to merge, not a review gate on day-to-day work.

## Why diverge from ADR-024 (semantic-release, auto-cut, no PR)

- **Tooling fit.** semantic-release does not cleanly version four packages across two ecosystems in one repo (see Context). release-please is built for exactly this and reproduces the ADR-0001 tag scheme natively.
- **The cut is the gate.** ADR-024 prefers an automatic cut because for services *promotion* (ArgoCD, ADR-022) is the real human gate; the version cut is cheap and reversible. A library has no promotion downstream — publishing to consumers *is* the irreversible step. So a one-click release-PR gate is appropriate here, not ceremony.

## Consequences

- One reusable workflow (`ci/library.yml`) now serves library repos; `ci/build.yml` continues to serve deployable services. Two release tools live in the org (semantic-release for services, release-please for libraries), each matched to its artifact shape.
- The per-package `test.yml` files under `<pkg>/.github/workflows/` are removed: GitHub Actions runs workflows only from the repository-root `.github/workflows/`, so those never executed. A single root `test.yml` covers all four packages.
- Conventional-commit scopes now carry release meaning. Scope commits by package (`fix(csd-intent): …`); an unscoped or wrong-scoped commit can move the wrong package's version.
- Two one-time repo settings are required: allow GitHub Actions to create pull requests (for the release PR), and a branch-protection rule on `main` making the `tests` checks required (so a release PR cannot merge red).
- A future public release under a neutral name remains a separate distribution identity (as ADR-0001 noted) and is unaffected.

## Alternatives considered

| Option | Why not |
|---|---|
| semantic-release (match ADR-024) | One-version-per-repo model; the monorepo plugin mangles the scoped npm tags and cannot version the Python packages. |
| Tag-triggered publish (manual bump, CI publishes on a `<pkg>-v*` tag) | Works and is simpler, but keeps version bumps manual — the drift that motivated this ADR. Remains available as a local-dev escape hatch: you can still hand-tag to cut a release. |
| Self-hosted release tooling | Unjustified for a solo-maintained, four-package repo. |

## Rollout

- `ci/library.yml` (reusable) + `.github/workflows/release.yml` (caller) + `.github/workflows/test.yml` (all four packages).
- `release-please-config.json` + `.release-please-manifest.json` seeded to current source versions.
- The first run opens release PRs. Before merging, verify the proposed tags read `<pkg>-vX.Y.Z` and that `pyproject.toml`'s `[project].version` bumps for the Python packages. The `vitest-intent` 0.2.1 / `playwright-intent` 0.1.1 vs last-tag drift is reconciled either by tagging those versions now or by letting the first PR cut the next version on top of them.
