# csd-library

Reusable implementation artifacts for projects following CSD methodology. Anything that helps implement, test, or scaffold a CSD-aligned project lives here. Methodology stays separate (the canonical CSD source); this folder is the *implementation* counterpart.

The Playbook (`ai-coding-prompts/`) stays separate too — it covers many topics beyond CSD (Java, FastAPI, Frontend, PowerShell, …), so `csd-library` can grow without dragging unrelated guidance along.

## Layout

```
csd-library/
├── README.md          ← you are here
├── pytest-intent/     ← publishable Python runtime: @intent(...) decorators + meta-tests
├── vitest-intent/     ← publishable TypeScript runtime: same model for vitest
└── bundles/           ← reusable Intent Bundles (claims + enforcement) consuming the runtimes
    └── starlight/     ← STARLIGHT bundle: 6 claims for Starlight docs sites
```

## How the pieces relate

| Piece              | What                                                          | Consumed by |
|--------------------|---------------------------------------------------------------|-------------|
| `pytest-intent`    | Python+pytest runtime: ships `@intent("INT-NNN")`, schema and coverage meta-tests | Any Python project that wants CSD-style intent testing |
| `vitest-intent`    | TS+vitest runtime: same shape as pytest-intent for JS/TS      | Any TS/JS project that wants the same |
| `bundles/<topic>/` | Packaged claim set + per-runner test impls (`impls/pytest/`, `impls/vitest/`, …) | The `apply-intent-bundle` skill drops these into target projects |

`bundles/` consumes the runtimes (its impls call into `pytest-intent` / `vitest-intent`). The runtimes themselves don't depend on the bundles.

## Tooling that drives this

The Playbook hosts the skills that operate on this folder. Cloned as a sibling of `csd-library/`, those skills reach in via relative path:

- `apply-intent-bundle` — applies a bundle from `bundles/<topic>/` to a target project
- `bootstrap-pytest-intent` — wires `pytest-intent` into a Python project
- `bootstrap-vitest-intent` — wires `vitest-intent` into a JS/TS project
- `bootstrap-starlight` — scaffolds a Starlight site and (by default) applies the `starlight` bundle

Reference documentation lives in `REF-Intent-Bundle.md` (bundle contract) and `REF-CSD.md` (cites the canonical methodology site) in the playbook.

## Expected layout on disk

This repo and the playbook are designed to be cloned as siblings:

```
<workspace>/
├── ai-coding-prompts/   ← the playbook
└── csd-library/         ← this repo
```

Skills and references in the playbook point here via `../csd-library/...`.

## Naming and growth policy

- New runtimes (e.g. a future `jest-intent`) live as siblings under `csd-library/`.
- New bundles live under `bundles/<topic>/`.
- Things that help implement CSD but aren't runtimes or bundles (codemods, example projects, reference data packs) can also live here once they become reusable. Until then, they stay in their host project.
