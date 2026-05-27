# Minimal csd-intent example

The smallest project showing csd-intent end-to-end.

## Layout

```
minimal-project/
├── intent.yaml             # 2 claims (CSD-INTENT-01 canonical shape)
└── tests/
    └── test_calculator.py  # @intent-decorated test for INT-001
```

INT-001 is `status: active` and has a test → counted as attested.
INT-002 is `status: draft` and has no test → exempt from coverage enforcement (pre-implementation placeholder).

## Run

```bash
pip install -e ../..              # install csd-intent
pip install -e ../../../pytest-intent  # install the @intent decorator
pytest tests/                     # run the demo test
csd-intent .                      # audit the spec + coverage
```

Expected audit output:
```
intent.yaml (.../intent.yaml): 2 claims, 1 attested. CLEAN.
```
