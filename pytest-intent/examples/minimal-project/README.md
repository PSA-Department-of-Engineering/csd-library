# Minimal pytest-intent example

The smallest realistic project showing pytest-intent end-to-end.

## Layout

```
minimal-project/
├── intent.yaml         # 2 claims about a hypothetical "user-id" guarantee
├── conftest.py         # pack_root fixture
└── tests/
    ├── __init__.py
    ├── test_user_id.py # @intent-decorated tests for the claims
    └── test_meta.py    # one-line wiring for the meta-tests
```

## Run

```bash
pip install -e ../..        # install pytest-intent
pip install pytest pyyaml   # already deps but explicit
cd <this dir>
pytest -v
```

Expected output: 2 claim tests pass, 2 meta-tests pass (intent_schema + intent_coverage). Total: 4 passed.

## What this demonstrates

- `@intent("INT-NNN")` decorator on test functions
- Multi-claim per test (`@intent("INT-001", "INT-002")` example)
- `intent.yaml` schema: statement / rationale / criticality / scope, no extra fields
- Meta-tests catching schema and coverage drift
- The `pack_root` fixture pattern projects must define
