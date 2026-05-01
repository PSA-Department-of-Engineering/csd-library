# pytest-intent

**Python+pytest implementation of CSD's Intent Specification annotation pattern.**

> CSD (Cognitive Software Delivery) is a language-agnostic methodology that lives at `D:/rc/CSD/`. *This package is one specific implementation* of CSD's intent-test annotation idea, scoped to Python projects using pytest. Other languages would need their own implementations.

## What this package IS

- A small Python library (~150 LOC) installable into any pytest project.
- Provides:
  - **`@intent("INT-NNN")` decorator** — links a test function to one or more claims in `intent.yaml`. Multi-claim per test supported (`@intent("INT-001", "INT-002")`); multi-test per claim also supported.
  - **`intent_schema` meta-test** — checks every claim in `intent.yaml` has the required fields with valid values.
  - **`intent_coverage` meta-test** — checks every claim has ≥ 1 decorated test, every decorated test references a real claim. Uses AST walk (no module import — robust to fixture/import errors).

## What this package is NOT

- Not a test generator. You write your own tests; this annotates them.
- Not a data validator. Tests do that work; this validates the *test ↔ intent* relationship.
- Not a methodology. CSD is the methodology; this is plumbing for one Python+pytest expression of it.
- Not yet a pytest plugin. v0.1 requires a 1-line import in `tests/test_meta.py`. Plugin auto-registration is on the v0.2 roadmap.

## Hidden assumptions (be aware)

- Project is Python ≥ 3.10 with pytest installed.
- Test files follow `tests/test_*.py` discovery pattern.
- `intent.yaml` lives at the pack/project root (where `pack_root` fixture resolves).
- A `pack_root` (or equivalent) fixture exists in the project's conftest pointing at the directory containing `intent.yaml`.

## Install

```bash
pip install -e D:/rc/CSD-Library/pytest-intent
```

(Local-only for now. PyPI publication only if/when external users appear.)

## Usage

```python
# tests/test_my_claims.py
from pytest_intent import intent

@intent("INT-001")
def test_resource_ids_unique(data_dir):
    ...

@intent("INT-021", "INT-022")  # one test serves two claims
def test_referential_integrity(data_dir):
    ...
```

```python
# tests/test_meta.py — two-line file enabling the framework:
from pytest_intent.meta_tests import test_intent_schema, test_intent_coverage  # noqa
```

```python
# Project's conftest.py needs:
@pytest.fixture(scope="session")
def pack_root() -> Path:
    return Path(__file__).resolve().parent.parent  # or wherever intent.yaml lives
```

That's the entire surface area.

## Why a package and not per-project copies

- Single source of truth for the schema definition (one place to update if CSD's schema evolves)
- Consistent test patterns across Data Packs, Estimation Kit projects, vault, etc.
- Drift between projects is impossible — they all import the same checks
- Fits the playbook's no-duplication principle (`AI-PLAYBOOK.md` Top Violation #12)

## Roadmap

v0.2 candidates (none implemented yet):
- pytest plugin auto-registration via `pytest11` entry point — eliminate the `tests/test_meta.py` boilerplate
- HTML coverage report (intent claims × tests, with last-run timestamps)
- Intent quality lints (claims with vague rationale, missing scope, etc.)
- Multi-test linkage in YAML (`tests:` list per claim, complementing the decorator)

Do not add v0.2 features speculatively — wait until they're needed.
