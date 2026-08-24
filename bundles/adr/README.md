# ADR bundle

Reusable Intent Bundle for Architecture Decision Records published as docs pages on a [Starlight](https://starlight.astro.build/) (Astro) site. Composes onto the STARLIGHT bundle: an ADR page is also a normal doc page, so it must satisfy the STARLIGHT frontmatter claims plus the ADR-lifecycle claims here.

## What it covers

| ID | Claim | Criticality |
|---|---|---|
| INT-ADR-001 | Every ADR has `adr_status` ∈ {Proposed, Decided, Superseded, Deprecated, Pending} | high |
| INT-ADR-002 | ADR `id` values are unique across the decisions collection | critical |
| INT-ADR-003 | Every `supersedes` / `superseded_by` reference resolves to an existing ADR | high |
| INT-ADR-004 | The decisions index's `## Current` table lists exactly the non-superseded records, with their own titles and statuses | medium |

## Runners

| Runner | Path |
|---|---|
| vitest | `impls/vitest/adr.test.ts` |

## Apply

```bash
python ../../playbook/skills/apply-intent-bundle/apply.py \
  --bundle adr \
  --target <path-to-starlight-project>
```

Merges the four claims into the target's `intent.yaml` and copies `impls/vitest/adr.test.ts` into the target's `tests/`.

## Assumptions

- ADR pages live under `src/content/docs/decisions/` (so Starlight renders them at `/decisions/...`).
- ADR pages are normal docs pages (`type: Reference`) carrying the extra frontmatter `adr_status`, and optionally `supersedes` / `superseded_by` (values are ADR slugs, e.g. `ADR-012`).
- The site already has the STARLIGHT bundle applied (this bundle does not duplicate its frontmatter claims).
- The decisions index, when there is one, is the page whose filename stem is `index` in that folder (the STARLIGHT bundle ships `templates/decisions-index.md` for it). INT-ADR-004 reads its `## Current` table and nothing else on the page.

## What INT-ADR-004 compares

One row per non-superseded record, matched on three things and lenient everywhere else:

| Column | Compared against | Leniency |
|---|---|---|
| Id | the record's filename stem | case-insensitive; the row may link page-relative (`[ADR-001](adr-001/)`) or root-absolute (`[ADR-001](/decisions/adr-001/)`) - link form belongs to INT-STARLIGHT-011, not here |
| Title | the record's `title` frontmatter | a leading `ADR-001: ` prefix is stripped from both sides, so either style passes |
| Status | the record's `adr_status` frontmatter | case-insensitive |

Records whose `adr_status` is `Superseded` belong in the template's separate `## Superseded` table, so they must NOT appear in `## Current`. That second table is deliberately unchecked: INT-ADR-003 already validates the supersede graph on the records themselves.

A collection with no index page passes: the claim is about an index that drifts from the records, not about requiring one to exist.

## Versioning

Manual SemVer in `bundle.yaml`.

## Changelog

### 0.2.0
Adds INT-ADR-004: the decisions index's `## Current` table is compared against the records it indexes, so a record added, retitled, or re-statused fails the build instead of leaving a stale table behind.

### 0.1.0
Initial bundle. Three claims: ADR status validity, id uniqueness, supersede-reference resolution.
