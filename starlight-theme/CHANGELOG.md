# Changelog

All notable changes to starlight-theme. Format follows [Keep a Changelog](https://keepachangelog.com/), versioning follows [SemVer](https://semver.org/).

## [Unreleased]

## [0.1.0]

Initial release.

### Added
- `styles.css` - the shared docs-site stylesheet: a warm dark palette override of Starlight's `:root[data-theme='dark']` base tokens, plus a token-based Mermaid contrast layer mapping the rendered `.mermaid` SVG to Starlight's `--sl-color-*` tokens (correct contrast in light and dark). Consumed via Starlight `customCss`.
- `mermaidConfig` - the theme-neutral `astro-mermaid` config object (flowchart curve/spacing/padding/useMaxWidth + font family and size). Diagram colour is not set here; it lives in the stylesheet against the theme tokens.
- `StarlightThemeMermaidConfig` type and a `VERSION` string.
- Published privately to GitHub Packages as `@psa-department-of-engineering/starlight-theme`.
