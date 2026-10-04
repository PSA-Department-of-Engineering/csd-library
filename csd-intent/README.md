# csd-intent

Cross-runtime audit tool for CSD intent specifications. Validates `intent.yaml`
against [CSD-INTENT-01](https://github.com/PSA-Department-of-Engineering/cognitive-software-delivery) and confirms every
runner-bound claim is attested by at least one test marker across **any** test runner -
pytest, vitest, Playwright, Jest, or anything that uses the standard `intent()`
/ `@intent()` marker shape.

This tool is **standalone**. It does not run inside your project's test suite; it
is invoked separately (CLI, CI step, or pre-commit hook).

## Why it exists

`pytest-intent`, `vitest-intent`, and `playwright-intent` provide the test-side
marker helpers - they let a test declare which intent claim it attests. They
deliberately know nothing about other runtimes, schema validation, or whether a
claim is unattested.

`csd-intent` owns the cross-runtime auditing: it walks every test file in the
project (Python via AST, TS/JS via regex), reads `intent.yaml`, and answers:

1. **Schema** - does every claim match CSD-INTENT-01?
2. **Orphan** - does every test marker reference a real claim?
3. **Coverage** - does every active claim have an attesting test or a current `llm` review?

## Install

```bash
# From PyPI:
pip install csd-intent

# Local dev against a csd-library checkout:
pip install -e path/to/csd-library/csd-intent
```

## Use

```bash
# Audit the current directory (expects intent.yaml at the root):
csd-intent

# Audit a specific project:
csd-intent /path/to/project

# Audit but tolerate unattested claims (the "intent before test" workflow):
csd-intent --fail-on schema

# Constrain the scan to specific directories:
csd-intent --tests-dir backend/tests --tests-dir frontend/src --tests-dir e2e

# Quiet summary only:
csd-intent --quiet

# The same audit as one JSON object on stdout, for a script or a dashboard:
csd-intent --json
```

Exit code is `0` on a clean audit, `1` when any violation falls into the
configured `--fail-on` set (`any` by default).

## Output

```
intent.yaml (/path/to/project/intent.yaml): 24 claims, 2 violation(s).

UNATTESTED (2):
  [unattested] INT-SB-018: no @intent / intent() marker references this claim
  [unattested] INT-SB-029: no @intent / intent() marker references this claim
```

### JSON output

`--json` prints the same audit as one JSON object on stdout and nothing else. The
exit code still follows `--fail-on`, so one run both records the summary and gates
on it.

```json
{
  "generated_at": "2026-09-22T09:41:07Z",
  "claims": 24,
  "attested": 20,
  "unattested": 2,
  "draft": 1,
  "active": 22,
  "deprecated": 1,
  "violations": 2,
  "requirements_traced": 17,
  "clean": false,
  "projects": [
    {
      "intent_path": "/path/to/project/intent.yaml",
      "claims": 24,
      "attested": 20,
      "unattested": 2,
      "draft": 1,
      "active": 22,
      "deprecated": 1,
      "violations": 2,
      "requirements_traced": 17,
      "clean": false,
      "claims_by_id": {
        "INT-SB-001": {
          "status": "active",
          "attested": true,
          "scope": "unit",
          "derived_from": ["REQ-003"]
        }
      }
    }
  ]
}
```

| Key | Meaning |
| --- | ------- |
| `claims` | claims declared in `intent.yaml` |
| `attested` | claims with a valid marker or a current PASS review |
| `unattested` | claims the report lists under `UNATTESTED`: active and lacking a valid attestation |
| `draft`, `active`, `deprecated` | claims by status |
| `violations` | violations of every kind: the report's "N violation(s)" |
| `requirements_traced` | distinct ids across every claim's `derived_from` annotation |
| `clean` | `true` when there is no violation of any kind |
| `generated_at` | when the audit ran, ISO-8601 UTC |
| `projects` | one entry per audited project, root first, with its `intent_path`, its own counts, and its `claims_by_id` |
| `claims_by_id` | in each `projects[]` entry: that project's claims by id, each with `status`, `attested`, `scope`, and `derived_from` |

Unattested draft and deprecated claims are excluded from the coverage gate, so
those two counts do not sum to `claims`. A tree of nested projects sums its counts into
the top-level keys and keeps `requirements_traced` distinct across projects; a claim id
is scoped to the project that declares it, so an id two projects both declare is
reported under each.

## What it scans

- **Python**: any file matching `test_*.py` or `*_test.py`, walked via AST for
  `@intent("INT-...")` decorators on functions starting with `test_`.
- **JS/TS**: any file matching `*.test.{ts,tsx,js,jsx,mts,cts}` or
  `*.spec.{ts,...}`, scanned by regex for `intent('INT-...', 'name', fn)` calls
  (single-ID and array-of-IDs forms both supported).
- **Excluded directories**: `node_modules`, `.venv`, `venv`, `dist`, `build`,
  `.git`, `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `.tox`.

## CSD-INTENT-01 conformance

The schema check validates each claim against the canonical fields per
[CSD-INTENT-01 §4.1](https://github.com/PSA-Department-of-Engineering/cognitive-software-delivery):

```yaml
INT-NNN:
  version: 1.0.0
  status: active                # draft | active | deprecated
  statement: "..."              # >= 10 chars, RFC 2119 language
  rationale: "..."              # optional but recommended
  test:
    scope: integration          # unit | integration | e2e | llm
    component: SwitchFlow
    type: behavior              # invariant | behavior | contract
  criticality: critical         # critical | high | medium | low
```

The scope can also be declared as a top-level `scope` field.

### Repository review

An `llm` claim carries only its latest verdict and reviewed commit:

```yaml
review:
  commit: 0123456789abcdef0123456789abcdef01234567
  verdict: PASS
```

The commit is a full lowercase Git object ID naming the revision the reviewer
read. A new review replaces this mapping; Git preserves its history. Reasons and
findings belong to the reviewer's PR or delivery record.

An active `llm` claim requires a current PASS. The auditor compares repository
content with the reviewed commit. It excludes `review` and `status` fields from
specification comparisons, so recording a review and activating a claim preserve
freshness. Other content changes make the review stale, including unrelated
files. Working-tree reads include untracked files that Git does not ignore.
Missing, failed, stale and unreadable reviews are unattested; markers on `llm`
claims are mismarked. CI checks the record without invoking a model.

The public `read_review` helper accepts a working tree or an explicit pinned
commit. JSON summaries expose `state`, a derived freshness `reason`, `commit`
and `verdict` for each `llm` claim.

### Duplicate keys are refused

`intent.yaml` is parsed with a loader that raises on a repeated key rather than
resolving it last-wins. A claim id reused by accident would otherwise delete the
earlier claim before any check could see it - and every marker written for that
claim would silently start attesting the survivor, with the audit still printing
`CLEAN`. The duplicate is reported as a schema violation naming both lines:

```
SCHEMA (1):
  [schema] intent.yaml: duplicate key `INT-GATE-006` (first declared on line 42,
  declared again on line 187); YAML would silently keep only the last one
```

Merge keys still work: `<<: *base` plus an explicit override is not a duplicate.

## License

MIT.
