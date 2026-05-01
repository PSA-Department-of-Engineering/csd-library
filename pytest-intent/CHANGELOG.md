# Changelog

All notable changes to pytest-intent are documented here. Format follows [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Added
- `py.typed` marker (PEP 561) so type-aware consumers see pytest-intent's annotations.
- `.gitignore` covering Python build / cache artefacts.
- `mypy>=1.0` to `[project.optional-dependencies] dev`; `examples*` excluded from wheel via `[tool.setuptools.packages.find]`.

### Changed
- `coverage_violations(claims, ...)` parameter type relaxed to `dict[str, dict[str, object]]` — function only consults `.keys()`, so the inner-value type was needlessly narrow and forced casts upstream.

Planned for v0.2:
- pytest plugin auto-injection of meta-tests via `pytest_collection_modifyitems` (eliminates need for `tests/test_meta.py` boilerplate)
- HTML coverage report (intent claims × tests, with last-run timestamps)
- Better error messages - suggest claim ID on typo
- More realistic examples (currently one minimal-project)

## [0.1.0] — 2026-04-26

Initial release.

### Added
- `@intent("INT-NNN", ...)` decorator for marking tests with intent claim references. Multi-claim per test supported (`@intent("INT-001", "INT-002")`).
- `parse_intent_yaml(path)` — PyYAML-backed parser returning `{claim_id: {field: value}}` for `INT-*` keys.
- `check_schema(claims)` — validates required fields (statement, rationale, criticality, scope) and allowed values per CSD.
- `collect_annotated_tests(tests_dir)` — AST walker that finds `@intent`-decorated test functions without importing the modules (robust to fixture/import errors).
- `coverage_violations(claims, annotated)` — returns intent ↔ test mismatches.
- Drop-in meta-tests at `pytest_intent.meta_tests`: `test_intent_schema`, `test_intent_coverage`. Override-able fixtures `intent_yaml_paths` and `intent_tests_dirs` for multi-file / multi-dir layouts.
- pytest plugin entry point (`pytest11`) — fixtures auto-register on install.
- Package's own test suite (22 tests covering decorator, schema, coverage).
- LICENSE (MIT).

### Known limitations
- Meta-tests still require manual import in `tests/test_meta.py`. Auto-injection deferred to v0.2.
- No CLI for standalone schema validation; must run via pytest.
- Single-language scope (Python+pytest only). Other CSD implementations would be separate packages.
