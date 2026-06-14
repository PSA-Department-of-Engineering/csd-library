# Changelog

All notable changes to starlight-theme. Format follows [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

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
