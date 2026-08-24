# Intent Bundles

Reusable, importable Intent Specifications + their enforcement tests, packaged together. See `../../playbook/REF-Intent-Bundle.md` for the contract.

Apply a bundle to a project via the `apply-intent-bundle` Skill (master at `../../playbook/skills/apply-intent-bundle/`).

## Bundles in this folder

| Bundle | Purpose | Supported runners | Applies to |
|---|---|---|---|
| `starlight` | Required frontmatter, ID format, canonical type/status, ISO-date validation for Starlight docs sites | `vitest` | `bootstrap-starlight` |

Bundles are extracted only when starter intent claims are shared across ≥2 bootstrap Skills, or when a claim set is genuinely reusable across non-bootstrapped projects. Don't speculate.
