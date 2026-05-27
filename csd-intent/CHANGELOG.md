# Changelog

All notable changes to this project will be documented in this file. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-26

### Added
- `csd-intent` CLI: `csd-intent [PROJECT_DIR] [--intent PATH] [--tests-dir DIR]... [--fail-on KIND] [--quiet]`.
- Schema validation against [CSD-INTENT-01](https://github.com/rafael-pires/csd) §4.1 — required fields, valid enums, semver version, INT-* id pattern.
- Backwards-compat acceptance of the legacy flat `scope:` layout alongside the canonical `test: {scope, component, type}` block.
- Orphan-ref detection — flags any `@intent / intent()` marker that references a claim not declared in `intent.yaml`.
- Coverage check — reports unattested claims, except those with `status: deprecated` (no test expected) or `status: draft` (pre-implementation placeholder).
- Multi-runtime walker: Python via AST (`@intent("INT-NNN")` decorators on functions starting with `test_`); JS/TS via regex (`intent('INT-NNN', name, fn)` calls in `*.test.{ts,tsx,js,jsx,mts,cts}` or `*.spec.{ts,...}` files).
- Standard exclude-dirs: `node_modules`, `.venv`, `dist`, `build`, `.git`, `__pycache__`, `.pytest_cache`, etc.
- `--fail-on schema|orphan|unattested|any|none` exit-code policy.
- Public Python API: `audit()`, `parse_intent_yaml()`, `check_schema()`, `collect_attestations()`, `AuditReport`, `AuditViolation`.
