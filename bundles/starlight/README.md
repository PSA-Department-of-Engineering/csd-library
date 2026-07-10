# STARLIGHT bundle

Reusable Intent Bundle for [Starlight](https://starlight.astro.build/) (Astro) documentation sites. Enforces content-collection conventions and generic page structure on every doc page.

## What it covers

### Frontmatter and content collection

| ID | Claim | Criticality |
|---|---|---|
| INT-STARLIGHT-001 | Every doc has a non-empty `title` | critical |
| INT-STARLIGHT-002 | Every doc has a non-empty `id` | critical |
| INT-STARLIGHT-003 | Doc `id` values are unique across the collection | critical |
| INT-STARLIGHT-004 | Every doc has `type` ∈ {Overview, Guide, Standard, Reference, Template, Intent, Flow} | high |
| INT-STARLIGHT-005 | Every doc has `status` ∈ {Draft, Active, Deprecated} | high |
| INT-STARLIGHT-006 | Every doc has `updated` formatted as YYYY-MM-DD | high |

### Page structure

These claims read each page's body (the markdown after the frontmatter) and are deliberately lenient so well-formed docs across different sites pass.

| ID | Claim | Criticality |
|---|---|---|
| INT-STARLIGHT-007 | Every page has connective intro prose, not pure scaffolding; a leading navigation or onward-links block (heading plus link list) and a leading bold-only line are tolerated | high |
| INT-STARLIGHT-008 | Every page contains at least one level-2 heading | medium |
| INT-STARLIGHT-009 | A `type: Flow` page contains a Mermaid `sequenceDiagram` and a steps section (a `## Steps` heading OR an ordered list) | high |
| INT-STARLIGHT-010 | A `type: Guide` page contains a numbered procedure (an ordered list OR at least two headings beginning with a number) | medium |
| INT-STARLIGHT-011 | Internal markdown link targets are relative to the current page: no root-absolute (`/...`) link or image targets in prose; code blocks exempt | high |

The type enum (INT-STARLIGHT-004) allows {Overview, Guide, Standard, Reference, Template, Intent, Flow}: Template and Intent match REF-Documentation 7.3, and Flow covers sequence-diagram pages.

Base-safe linking (INT-STARLIGHT-011) exists because Astro's `base` prefixes generated navigation and asset URLs but never rewrites hand-written hrefs: a root-absolute internal link escapes the base path and 404s the moment the site serves under a portal prefix (`DOCS_BASE`).

## Runners

| Runner | Path |
|---|---|
| vitest | `impls/vitest/starlight.test.ts` |

Python+pytest impl: not yet shipped. A Starlight site is JS/TS, so pytest is the wrong runtime.

## Templates

The bundle ships generic, site-agnostic page skeletons under `templates/`. Each carries frontmatter placeholders and the required and recommended sections for its type, so a new page starts already conformant with the structure claims above.

| Template | Type | Required structure it seeds |
|---|---|---|
| `templates/overview.md` | Overview | Intro, `## At a glance` (mermaid), `## Read next` |
| `templates/guide.md` | Guide | Intro, `## Steps` ordered list, `## Verify`, `## Read next` |
| `templates/flow.md` | Flow | Intro, `## Sequence` (mermaid `sequenceDiagram`), `## Steps`, `## Read next` |
| `templates/reference.md` | Reference | Intro, a table section, `## Read next` |
| `templates/decisions-index.md` | Reference | Intro, `## Current`, `## Superseded` (prefer generated tables) |

These are starting points, not enforced artifacts; the intent claims are what the suite checks.

## Apply

```bash
python ../../ai-coding-prompts/skills/apply-intent-bundle/apply.py \
  --bundle starlight \
  --target <path-to-starlight-project>
```

The target must already have:
- `package.json` with `@psa-department-of-engineering/vitest-intent` and `vitest` as devDependencies
- The Starlight content layout: `src/content/docs/`

The bundle's vitest impl (`impls/vitest/starlight.test.ts`) is a normal vitest test using `intent()` markers: vitest discovers it directly; schema + coverage auditing is the standalone `csd-intent` CLI's job (no in-suite meta-test needed). `bootstrap-starlight` Skill (default flags) creates that layout AND applies this bundle.

## Assumptions

- Docs live under `src/content/docs/` (Starlight default).
- Markdown files use YAML frontmatter delimited by `---`.
- The vitest test in `impls/vitest/starlight.test.ts` walks the docs directory at runtime, so it works whether the project has 1 or 1000 docs.
- The structure claims (007-010) read the page body and are deliberately lenient: prose may live inside the first section, leading navigation blocks are tolerated, and Starlight splash pages (`template: splash`, which render from frontmatter `hero:`) are exempt from 007 and 008.

## Versioning

Manual SemVer in `bundle.yaml` for now. Once Git tracks the playbook, bumps come via Conventional Commits (`feat(starlight):` minor, `fix(starlight):` patch, `feat(starlight)!:` major).

## Changelog

### 0.3.0 - 2026-07-10
Adds base-safe linking. New claim INT-STARLIGHT-011: internal markdown link and image targets in prose must be relative (no root-absolute `/...` targets; code blocks exempt), because Astro's `base` never rewrites hand-written hrefs and a root-absolute link 404s under a portal prefix (`DOCS_BASE`).

### 0.2.0 - 2026-06-14
Adds generic page-structure enforcement. New claims INT-STARLIGHT-007 (intro prose before the first level-2 heading), INT-STARLIGHT-008 (at least one level-2 heading), INT-STARLIGHT-009 (Flow pages need a `sequenceDiagram` plus steps), and INT-STARLIGHT-010 (Guide pages need a numbered procedure). Expands the INT-STARLIGHT-004 type enum to {Overview, Guide, Standard, Reference, Template, Intent, Flow}. Ships generic page skeletons under `templates/`.

### 0.1.0 - 2026-04-26
Initial bundle. Six claims covering required frontmatter (title/id/type/status/updated), ID uniqueness, and `updated` date formatting.
