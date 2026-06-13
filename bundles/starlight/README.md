# STARLIGHT bundle

Reusable Intent Bundle for [Starlight](https://starlight.astro.build/) (Astro) documentation sites. Enforces content-collection conventions on every doc page.

## What it covers

| ID | Claim | Criticality |
|---|---|---|
| INT-STARLIGHT-001 | Every doc has a non-empty `title` | critical |
| INT-STARLIGHT-002 | Every doc has a non-empty `id` | critical |
| INT-STARLIGHT-003 | Doc `id` values are unique across the collection | critical |
| INT-STARLIGHT-004 | Every doc has `type` ∈ {Overview, Guide, Standard, Reference} | high |
| INT-STARLIGHT-005 | Every doc has `status` ∈ {Draft, Active, Deprecated} | high |
| INT-STARLIGHT-006 | Every doc has `updated` formatted as YYYY-MM-DD | high |

## Runners

| Runner | Path |
|---|---|
| vitest | `impls/vitest/starlight.test.ts` |

Python+pytest impl: not yet shipped. A Starlight site is JS/TS — pytest is the wrong runtime.

## Apply

```bash
python ../../ai-coding-prompts/skills/apply-intent-bundle/apply.py \
  --bundle starlight \
  --target <path-to-starlight-project>
```

The target must already have:
- `package.json` with `@psa-department-of-engineering/vitest-intent` and `vitest` as devDependencies
- The Starlight content layout: `src/content/docs/`

The bundle's vitest impl (`impls/vitest/starlight.test.ts`) is a normal vitest test using `intent()` markers — vitest discovers it directly; schema + coverage auditing is the standalone `csd-intent` CLI's job (no in-suite meta-test needed). `bootstrap-starlight` Skill (default flags) creates that layout AND applies this bundle.

## Assumptions

- Docs live under `src/content/docs/` (Starlight default).
- Markdown files use YAML frontmatter delimited by `---`.
- The vitest test in `impls/vitest/starlight.test.ts` walks the docs directory at runtime, so it works whether the project has 1 or 1000 docs.

## Versioning

Manual SemVer in `bundle.yaml` for now. Once Git tracks the playbook, bumps come via Conventional Commits (`feat(starlight):` minor, `fix(starlight):` patch, `feat(starlight)!:` major).

## Changelog

### 0.1.0 — 2026-04-26
Initial bundle. Six claims covering required frontmatter (title/id/type/status/updated), ID uniqueness, and `updated` date formatting.
