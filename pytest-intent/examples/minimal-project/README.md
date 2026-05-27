# Minimal pytest-intent example

The smallest realistic project showing pytest-intent end-to-end.

## Layout

```
minimal-project/
├── intent.yaml         # 2 claims (CSD-INTENT-01 canonical shape)
└── tests/
    ├── __init__.py
    └── test_user_id.py # @intent-decorated tests for the claims
```

No `test_meta.py`, no `conftest.py`. The `@intent` decorator does its job
(annotating test functions); auditing is somebody else's job.

## Run the tests

```bash
pip install -e ../..        # install pytest-intent (just the decorator)
cd <this dir>
pytest -v
```

Expected: 2 tests pass.

## Audit the spec + coverage

```bash
pip install csd-intent      # the standalone auditor
csd-intent .
```

Expected: `intent.yaml (...): 2 claims, 2 attested. CLEAN.`

## What this demonstrates

- `@intent("INT-NNN")` decorator on test functions
- Multi-claim per test (`@intent("INT-001", "INT-002")`)
- `intent.yaml` in CSD-INTENT-01 canonical shape
- Clean separation: decorator does annotation; `csd-intent` does validation + coverage
