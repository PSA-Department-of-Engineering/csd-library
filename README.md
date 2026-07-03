# csd-library

Reusable implementation artifacts for projects following CSD methodology. Anything that helps implement, test, or scaffold a CSD-aligned project lives here. Methodology stays separate (the canonical CSD source); this folder is the *implementation* counterpart.

The Playbook (`ai-coding-prompts/`) stays separate too - it covers many topics beyond CSD (Java, FastAPI, Frontend, PowerShell, …), so `csd-library` can grow without dragging unrelated guidance along.

## Layout

```
csd-library/
├── README.md            ← you are here
├── pytest-intent/       ← publishable Python runtime: the @intent(...) decorator for pytest
├── csd-intent/          ← publishable Python CLI: cross-runtime intent.yaml auditor
├── vitest-intent/       ← publishable TypeScript runtime: intent() for vitest
├── playwright-intent/   ← publishable TypeScript runtime: intent() for Playwright e2e
├── starlight-theme/     ← publishable TypeScript/CSS package: the shared Starlight look (stylesheet + mermaidConfig)
├── playbook-studio/     ← local web app (not published): visual browser/editor for the sibling playbook, with intent-gated writes
├── slidev-themes/       ← theme catalog (CSS per brand/org) resolved by the bootstrap-slidev-deck skill
└── bundles/             ← reusable Intent Bundles (claims + enforcement) consuming the runtimes
    ├── adr/             ← ADR bundle: lifecycle claims for decision records on Starlight sites
    └── starlight/       ← STARLIGHT bundle: 6 claims for Starlight docs sites
```

## How the pieces relate

| Piece              | What                                                          | Consumed by |
|--------------------|---------------------------------------------------------------|-------------|
| `pytest-intent`    | Python+pytest runtime: the `@intent("INT-NNN")` decorator | Any Python project that wants CSD-style intent testing |
| `csd-intent`       | Standalone Python CLI: validates `intent.yaml` and checks every claim is attested across pytest / vitest / Playwright | Any CSD project, in CI or locally, for auditing |
| `vitest-intent`    | TS+vitest runtime: the `intent()` wrapper, same shape as pytest-intent | Any TS/JS project that wants the same |
| `playwright-intent`| TS+Playwright runtime: the `intent()` wrapper for browser e2e | Any frontend project doing CSD-style e2e |
| `starlight-theme`  | Shared Starlight look: a token-based stylesheet (warm dark palette + Mermaid contrast layer) plus the `astro-mermaid` `mermaidConfig` object | Any Starlight docs site, via `customCss` + a config import |
| `bundles/<topic>/` | Packaged claim set + per-runner test impls (`impls/pytest/`, `impls/vitest/`, …) | The `apply-intent-bundle` skill drops these into target projects |
| `playbook-studio`  | Hexagonal FastAPI + React MVVM app that browses and edits the sibling playbook with intent-test-gated writes; dogfoods `pytest-intent`, `vitest-intent`, and `csd-intent` | Run locally via `playbook-studio/devops/start.ps1` |
| `slidev-themes/`   | Brand/org theme CSS for Slidev decks | The `bootstrap-slidev-deck` skill resolves themes from here |

`starlight-theme` is a *runtime-styling* package (the look) and is independent of the STARLIGHT *intent bundle* under `bundles/starlight/` (the frontmatter + page-structure contract). A docs site can adopt either, both, or neither; the theme is consumed as an npm dependency, while the bundle is copied in by `apply-intent-bundle`.

`bundles/` consumes the runtimes (its impls call into `pytest-intent` / `vitest-intent`). The runtimes themselves don't depend on the bundles.

## Tooling that drives this

The Playbook hosts the skills that operate on this folder. Cloned as a sibling of `csd-library/`, those skills reach in via relative path:

- `apply-intent-bundle` - applies a bundle from `bundles/<topic>/` to a target project
- `bootstrap-pytest-intent` - wires `pytest-intent` into a Python project
- `bootstrap-vitest-intent` - wires `vitest-intent` into a JS/TS project
- `bootstrap-starlight` - scaffolds a Starlight site and (by default) applies the `starlight` bundle

Reference documentation lives in `REF-Intent-Bundle.md` (bundle contract) and `REF-CSD.md` (cites the canonical methodology site) in the playbook.

## Expected layout on disk

This repo and the playbook are designed to be cloned as siblings:

```
<workspace>/
├── ai-coding-prompts/   ← the playbook
└── csd-library/         ← this repo
```

Skills and references in the playbook point here via `../csd-library/...`.

## Releasing

Releases are automated with [release-please](https://github.com/googleapis/release-please) through the org's shared CI (`PSA-Department-of-Engineering/ci` → `library.yml`). The decision, and why it diverges from the services' auto-cut model, is recorded in [ADR-0002](docs/adr/0002-release-automation.md); per-package distribution targets are [ADR-0001](docs/adr/0001-private-package-distribution.md).

How a release happens:

1. Land work on `main` as usual, with Conventional Commits scoped by package (`feat(pytest-intent): …`) so only that package's version moves. Day-to-day commits go straight to `main`; no PR is required.
2. release-please maintains one **release PR per package**, accumulating the version bump + CHANGELOG from those commits. This is the only PR in the flow.
3. The repo's tests (`.github/workflows/test.yml`) run on that PR. Merge it when you want to cut the release; the merge is the release gate.
4. On merge, release-please tags `<pkg>-vX.Y.Z`, creates the GitHub release, and:
   - **npm** (`vitest-intent`, `playwright-intent`): publishes to GitHub Packages.
   - **Python** (`pytest-intent`, `csd-intent`): nothing more to push - the tag *is* the release; consumers `pip install` it (see ADR-0001).

Because those bumps are computed from the commit messages, a committed `.pre-commit-config.yaml` ships a bypassable local `commit-msg` hook that checks each message is a Conventional Commit before it lands. Install it once per clone (the `.git/hooks` install is not committed, only the config is):

```bash
pip install pre-commit
pre-commit install --install-hooks
```

A non-conforming message is rejected; `git commit --no-verify` bypasses it when needed.

Versioning is per-package SemVer; `release-please-config.json` and `.release-please-manifest.json` at the repo root hold the package map and current versions. Two one-time GitHub settings are needed: allow Actions to create pull requests (Settings → Actions → General), and mark the `tests` checks required on `main` so a release PR cannot merge red.

## Naming and growth policy

- New runtimes (e.g. a future `jest-intent`) live as siblings under `csd-library/`.
- New bundles live under `bundles/<topic>/`.
- Things that help implement CSD but aren't runtimes or bundles (codemods, example projects, reference data packs) can also live here once they become reusable. Until then, they stay in their host project.
