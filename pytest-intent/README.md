# pytest-intent

**The `@intent` decorator for pytest - links a test function to one or more CSD intent claims.**

> CSD (Cognitive Software Delivery) is a language-agnostic methodology. This package is one specific implementation, scoped to Python projects using pytest.

## What this package is

A tiny library (~40 LOC) that exposes a single decorator:

```python
from pytest_intent import intent

@intent("INT-001")
def test_resource_ids_unique(data_dir):
    ...

@intent("INT-021", "INT-022")  # one test serves two claims
def test_referential_integrity(data_dir):
    ...
```

That's the entire public surface.

## What it is NOT

- **Not a validator.** Schema checks (CSD-INTENT-01), orphan detection (test references unknown claim), and cross-runtime coverage all live in the standalone [`csd-intent`](https://github.com/PSA-Department-of-Engineering/csd-library/tree/main/csd-intent) CLI - point it at any project to audit.
- **Not a pytest plugin.** Just a decorator. No fixtures, no entry points, no autoloading. Drop the import in your tests and you're done.
- **Not a generator.** You write your tests; this annotates them.

## Why split the decorator from the auditor?

- **One concern per package.** The decorator runs inside pytest; the auditor is cross-language and runs standalone (CI step, pre-commit, ad-hoc).
- **No coupling.** Other test runners (vitest-intent, playwright-intent) expose the same `intent()` marker shape. The auditor reads all of them, regardless of which decorator package put the marker there.
- **Tiny install.** `pytest-intent` has no dependency on PyYAML or anything beyond pytest. The auditor pulls those in only when you actually need to audit.

## Install

```bash
# Private install, pinned to a release tag:
pip install "pytest-intent @ git+https://github.com/PSA-Department-of-Engineering/csd-library.git@pytest-intent-v0.2.0#subdirectory=pytest-intent"

# Local dev against a csd-library checkout:
pip install -e path/to/csd-library/pytest-intent
```

## Companion: csd-intent

To validate your `intent.yaml` against CSD-INTENT-01 and check that every claim has a test:

```bash
pip install "csd-intent @ git+https://github.com/PSA-Department-of-Engineering/csd-library.git@csd-intent-v0.1.0#subdirectory=csd-intent"
csd-intent /path/to/your/project
```

See [csd-intent README](../csd-intent/README.md) for full options.

## License

MIT.
