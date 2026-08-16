# csd-intent

Cross-runtime audit tool for CSD intent specifications. Validates `intent.yaml`
against [CSD-INTENT-01](https://github.com/PSA-Department-of-Engineering/cognitive-software-delivery) and confirms every
claim is attested by at least one test marker across **any** test runner -
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
3. **Coverage** - does every claim have at least one attesting test, anywhere?

## Install

```bash
# Private install, pinned to a release tag:
pip install "csd-intent @ git+https://github.com/PSA-Department-of-Engineering/csd-library.git@csd-intent-v0.3.2#subdirectory=csd-intent"

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
    scope: integration          # unit | integration | e2e
    component: SwitchFlow
    type: behavior              # invariant | behavior | contract
  criticality: critical         # critical | high | medium | low
```

For projects still on the legacy flat-`scope:` shape, the tool accepts it (with
no warning) - that's a migration concession, not a recommendation.

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
