# Changelog

All notable changes to vitest-intent. Format follows [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

## [1.0.1](https://github.com/PSA-Department-of-Engineering/csd-library/compare/vitest-intent-v1.0.0...vitest-intent-v1.0.1) (2026-08-09)


### Bug Fixes

* **vitest-intent:** publish to the public npm registry ([e7b8dcf](https://github.com/PSA-Department-of-Engineering/csd-library/commit/e7b8dcf74a93cb419117b73e2b09a01900dedd4b))

## [1.0.0](https://github.com/PSA-Department-of-Engineering/csd-library/compare/vitest-intent-v0.2.1...vitest-intent-v1.0.0) (2026-06-13)


### ⚠ BREAKING CHANGES

* updated intent tests & added playwright-intent

### Features

* publish intent testing packages ([7fba066](https://github.com/PSA-Department-of-Engineering/csd-library/commit/7fba06654169102e072398eca1b025abe13b0b42))
* updated intent tests & added playwright-intent ([7f66d1c](https://github.com/PSA-Department-of-Engineering/csd-library/commit/7f66d1cb67a5271d8089edcbff8bea80e4113cc1))

## [Unreleased]

## [0.2.0] - 2026-06-11

### Changed
- **BREAKING** - removed the in-suite meta-tests: `registerIntentMetaTests` and the `vitest-intent/meta-tests` subpath are gone. Schema validation (CSD-INTENT-01), orphan detection, and intent↔test coverage now live in the standalone, cross-runtime `csd-intent` CLI, run out of band. The public surface is now `intent()` / `validateIntentArgs` only.
- Published privately to GitHub Packages as `@psa-department-of-engineering/vitest-intent` (previously consumed as an unscoped `file:` sibling dependency).

## [0.1.0] - 2026-04-26

Initial release.

### Added
- `intent(id, name, fn, options?)` - wraps `vitest.test()`, binds CSD intent claim ID. Supports single ID or array (multi-claim per test).
- `validateIntentArgs(id, fn, options?)` - pure validator (does not call `test()`). Useful for unit-testing intent invocations.
- `parseIntentYaml(path)` - reads `intent.yaml`, returns parsed claims (skips non-`INT-` prefixed top-level keys).
- `checkSchema(claims)` - validates required fields (`statement`, `rationale`, `criticality`, `scope`) and allowed values per CSD.
- `collectAnnotatedTests(dir)` - walks test files (`*.test.*` / `*.spec.*`), finds `intent(...)` calls via regex.
- `coverageViolations(claims, annotated)` - returns intent ↔ test mismatch strings.
- `registerIntentMetaTests(options)` - drop-in: registers `intent.schema` + `intent.coverage` vitest tests.
- 25 internal tests covering all public APIs.
- LICENSE (MIT), TypeScript declarations, ESM-only output.

### Known limitations
- Meta-tests still require manual `registerIntentMetaTests()` call. Auto-injection via vitest plugin deferred to v0.2.
- Coverage walker is regex-based, not AST. Aliased imports (`import { intent as foo }`) aren't detected.
- Single-language scope (Vitest+TypeScript only). Sister project [pytest-intent](https://github.com/rafael-pires/pytest-intent) covers Python+pytest.
