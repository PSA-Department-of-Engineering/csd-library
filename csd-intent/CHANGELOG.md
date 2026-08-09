# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.3](https://github.com/PSA-Department-of-Engineering/csd-library/compare/csd-intent-v0.3.2...csd-intent-v0.3.3) (2026-08-09)


### Bug Fixes

* **csd-intent:** pin the install example to the current tag ([bddac48](https://github.com/PSA-Department-of-Engineering/csd-library/commit/bddac48e1015eb18963f93eac400ab768d85710c))

## [0.3.2](https://github.com/PSA-Department-of-Engineering/csd-library/compare/csd-intent-v0.3.1...csd-intent-v0.3.2) (2026-07-27)


### Bug Fixes

* csd-intent flags a zero-claim intent.yaml as a schema violation ([#5](https://github.com/PSA-Department-of-Engineering/csd-library/issues/5)) ([50e8c8e](https://github.com/PSA-Department-of-Engineering/csd-library/commit/50e8c8eb7745796670e4e02436457ff5cb850688))

## [0.3.1](https://github.com/PSA-Department-of-Engineering/csd-library/compare/csd-intent-v0.3.0...csd-intent-v0.3.1) (2026-07-10)


### Bug Fixes

* **csd-intent:** anchor relative --intent and --tests-dir to PROJECT_DIR ([f016883](https://github.com/PSA-Department-of-Engineering/csd-library/commit/f016883eca1bec4266fd80d2208233953bae28a6))

## [0.3.0](https://github.com/PSA-Department-of-Engineering/csd-library/compare/csd-intent-v0.2.0...csd-intent-v0.3.0) (2026-06-14)


### Features

* **csd-intent:** audit nested intent projects independently ([d9ac08a](https://github.com/PSA-Department-of-Engineering/csd-library/commit/d9ac08a3ab285eb6411fe8cd0dcb2ef5226ec4f2))

## [0.2.0](https://github.com/PSA-Department-of-Engineering/csd-library/compare/csd-intent-v0.1.0...csd-intent-v0.2.0) (2026-06-13)


### Features

* publish intent testing packages ([7fba066](https://github.com/PSA-Department-of-Engineering/csd-library/commit/7fba06654169102e072398eca1b025abe13b0b42))

## [Unreleased]

### Added
- Nested-project awareness. A subdirectory that carries its own `intent.yaml` is now
  treated as a separate project boundary: the outer marker scan no longer descends into
  it, so a nested project's `intent()` / `@intent` markers no longer orphan against the
  outer project's claims. `csd-intent <dir>` discovers nested intent projects and audits
  each as its own project (each `intent.yaml` against the markers in its own subtree,
  bounded by any still-deeper nested projects), prints a per-project summary, and exits
  non-zero if any project has violations.
- Public API: `audit_tree(project_dir) -> list[AuditReport]` and
  `find_nested_intent_projects(root) -> list[Path]`.

### Changed
- `collect_attestations` gained a `respect_nested_projects` parameter (default `True`)
  that enables the project-boundary walk. Passing `--intent` or `--tests-dir` keeps the
  explicit single-project behaviour (no auto-discovery). A repo with no nested
  `intent.yaml` behaves exactly as before, including output format and exit codes.

## [0.1.0] - 2026-05-26

### Added
- `csd-intent` CLI: `csd-intent [PROJECT_DIR] [--intent PATH] [--tests-dir DIR]... [--fail-on KIND] [--quiet]`.
- Schema validation against [CSD-INTENT-01](https://github.com/rafael-pires/csd) §4.1 - required fields, valid enums, semver version, INT-* id pattern.
- Backwards-compat acceptance of the legacy flat `scope:` layout alongside the canonical `test: {scope, component, type}` block.
- Orphan-ref detection - flags any `@intent / intent()` marker that references a claim not declared in `intent.yaml`.
- Coverage check - reports unattested claims, except those with `status: deprecated` (no test expected) or `status: draft` (pre-implementation placeholder).
- Multi-runtime walker: Python via AST (`@intent("INT-NNN")` decorators on functions starting with `test_`); JS/TS via regex (`intent('INT-NNN', name, fn)` calls in `*.test.{ts,tsx,js,jsx,mts,cts}` or `*.spec.{ts,...}` files).
- Standard exclude-dirs: `node_modules`, `.venv`, `dist`, `build`, `.git`, `__pycache__`, `.pytest_cache`, etc.
- `--fail-on schema|orphan|unattested|any|none` exit-code policy.
- Public Python API: `audit()`, `parse_intent_yaml()`, `check_schema()`, `collect_attestations()`, `AuditReport`, `AuditViolation`.
