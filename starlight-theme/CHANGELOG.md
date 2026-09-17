# Changelog

All notable changes to starlight-theme. Format follows [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

## [1.3.2](https://github.com/PSA-Department-of-Engineering/csd-library/compare/starlight-theme-v1.3.1...starlight-theme-v1.3.2) (2026-09-17)


### Bug Fixes

* **starlight-theme:** rehue the dark documentation palette from Zinc to Stone ([1216aca](https://github.com/PSA-Department-of-Engineering/csd-library/commit/1216aca1ef6b70f966fce6bef1cb674eb8c1a5f2))

## [1.3.1](https://github.com/PSA-Department-of-Engineering/csd-library/compare/starlight-theme-v1.3.0...starlight-theme-v1.3.1) (2026-09-16)


### Bug Fixes

* **docs:** ship the Copper identity addition ([f5634ad](https://github.com/PSA-Department-of-Engineering/csd-library/commit/f5634add86a45da3e5d0f1236a69b39f636993ed))
* **starlight-theme:** revert the documentation palette to PSA Molten ([956eda2](https://github.com/PSA-Department-of-Engineering/csd-library/commit/956eda251ddca403e44473c3989c4c506f0d8d78))

## [1.3.0](https://github.com/PSA-Department-of-Engineering/csd-library/compare/starlight-theme-v1.2.0...starlight-theme-v1.3.0) (2026-09-16)


### Features

* **starlight-theme:** add shared Starlight theme package ([5d501da](https://github.com/PSA-Department-of-Engineering/csd-library/commit/5d501da87be452c8b52d33fae2bcd882e4ade346))
* **starlight-theme:** apply PSA documentation palettes ([2d2eb94](https://github.com/PSA-Department-of-Engineering/csd-library/commit/2d2eb94b43f2e70b7f3cc5f1cce6875424daccf3))
* **starlight-theme:** switch the documentation palette from PSA Molten to Copper ([#25](https://github.com/PSA-Department-of-Engineering/csd-library/issues/25)) ([4a0e183](https://github.com/PSA-Department-of-Engineering/csd-library/commit/4a0e183d30e4b05f77eb33a6276501c13e151d43))


### Bug Fixes

* **starlight-theme:** document the public npm install, not the GitHub Packages one ([005993e](https://github.com/PSA-Department-of-Engineering/csd-library/commit/005993ee02fa782019a3632f97b171d91e428f55))
* **starlight-theme:** publish to the public npm registry ([bd886e2](https://github.com/PSA-Department-of-Engineering/csd-library/commit/bd886e279b029728cb2464820fe76d1ff7e8719c))

## [1.2.0](https://github.com/PSA-Department-of-Engineering/csd-library/compare/starlight-theme-v1.1.0...starlight-theme-v1.2.0) (2026-09-13)


### Features

* **starlight-theme:** apply PSA documentation palettes ([2d2eb94](https://github.com/PSA-Department-of-Engineering/csd-library/commit/2d2eb94b43f2e70b7f3cc5f1cce6875424daccf3))

## [1.1.0](https://github.com/PSA-Department-of-Engineering/csd-library/compare/starlight-theme-v1.0.1...starlight-theme-v1.1.0) (2026-08-09)


### Features

* **starlight-theme:** add shared Starlight theme package ([5d501da](https://github.com/PSA-Department-of-Engineering/csd-library/commit/5d501da87be452c8b52d33fae2bcd882e4ade346))


### Bug Fixes

* **starlight-theme:** document the public npm install, not the GitHub Packages one ([005993e](https://github.com/PSA-Department-of-Engineering/csd-library/commit/005993ee02fa782019a3632f97b171d91e428f55))
* **starlight-theme:** publish to the public npm registry ([bd886e2](https://github.com/PSA-Department-of-Engineering/csd-library/commit/bd886e279b029728cb2464820fe76d1ff7e8719c))

## [1.0.1](https://github.com/PSA-Department-of-Engineering/csd-library/compare/starlight-theme-v1.0.0...starlight-theme-v1.0.1) (2026-08-09)


### Bug Fixes

* **starlight-theme:** publish to the public npm registry ([bd886e2](https://github.com/PSA-Department-of-Engineering/csd-library/commit/bd886e279b029728cb2464820fe76d1ff7e8719c))

## 1.0.0 (2026-06-14)


### Features

* **starlight-theme:** add shared Starlight theme package ([5d501da](https://github.com/PSA-Department-of-Engineering/csd-library/commit/5d501da87be452c8b52d33fae2bcd882e4ade346))

## [Unreleased]

## [0.1.0]

Initial release.

### Added
- `styles.css` - the shared docs-site stylesheet: a warm dark palette override of Starlight's `:root[data-theme='dark']` base tokens, plus a token-based Mermaid contrast layer mapping the rendered `.mermaid` SVG to Starlight's `--sl-color-*` tokens (correct contrast in light and dark). Consumed via Starlight `customCss`.
- `mermaidConfig` - the theme-neutral `astro-mermaid` config object (flowchart curve/spacing/padding/useMaxWidth + font family and size). Diagram colour is not set here; it lives in the stylesheet against the theme tokens.
- `StarlightThemeMermaidConfig` type and a `VERSION` string.
- Published privately to GitHub Packages as `@psa-department-of-engineering/starlight-theme`.
