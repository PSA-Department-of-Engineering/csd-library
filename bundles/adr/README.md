# ADR bundle

Reusable Intent Bundle for Architecture Decision Records published as docs pages on a [Starlight](https://starlight.astro.build/) (Astro) site. Composes onto the STARLIGHT bundle: an ADR page is also a normal doc page, so it must satisfy the STARLIGHT frontmatter claims plus the ADR-lifecycle claims here.

## What it covers

| ID | Claim | Criticality |
|---|---|---|
| INT-ADR-001 | Every ADR has `adr_status` ∈ {Proposed, Decided, Superseded, Deprecated, Pending} | high |
| INT-ADR-002 | ADR `id` values are unique across the decisions collection | critical |
| INT-ADR-003 | Every `supersedes` / `superseded_by` reference resolves to an existing ADR | high |

## Runners

| Runner | Path |
|---|---|
| vitest | `impls/vitest/adr.test.ts` |

## Apply

```bash
python ../../ai-coding-prompts/skills/apply-intent-bundle/apply.py \
  --bundle adr \
  --target <path-to-starlight-project>
```

Merges the three claims into the target's `intent.yaml` and copies `impls/vitest/adr.test.ts` into the target's `tests/`.

## Assumptions

- ADR pages live under `src/content/docs/decisions/` (so Starlight renders them at `/decisions/...`).
- ADR pages are normal docs pages (`type: Reference`) carrying the extra frontmatter `adr_status`, and optionally `supersedes` / `superseded_by` (values are ADR slugs, e.g. `ADR-012`).
- The site already has the STARLIGHT bundle applied (this bundle does not duplicate its frontmatter claims).

## Versioning

Manual SemVer in `bundle.yaml`.

## Changelog

### 0.1.0
Initial bundle. Three claims: ADR status validity, id uniqueness, supersede-reference resolution.
