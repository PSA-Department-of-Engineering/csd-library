# Foundry design systems

The shared home for PSA Molten, Vodafone Portugal Digital Engineering and Celfocus Digital: approved semantic colours, typography, original marks and guidance. Each identity's `identity.json` links its approved PSA Library brief.

## Source ownership

| Concern | Edit here |
|---|---|
| Palette and typography | `<identity>/identity.json` |
| Brand guidance and original artwork | `<identity>/DESIGN.md` and `assets/` |
| Slide layout, motion and surfaces | `../slidev-themes/<theme>/style.css` |
| Slide logo and background markup | Each theme's `global-top.vue` |
| Slide content structures | Each theme's `pages/` |

Run `python design-systems/generate.py` after changing palette or guidance. It converts approved colours to Protopane tokens, writes standalone CSS variables, updates only the palette block in each slide stylesheet, and refreshes the review gallery. `--check` detects drift. Theme layout, chrome, metadata and pages are authored independently.

The six Dark/Light themes are `psa`, `vodafone-digital-engineering`, `celfocus-digital` and their `-light` variants. The original ADC deck theme is available as `vodafone-pt-digital`. Each theme documents its content classes; changing a deck's theme may require adapting its pages.

## Consumers

Protopane imports `generated/<mode>/protopane.json` as packaged presets. Press embeds the PSA palette into its own authored templates during maintenance. psa-slides and the Slidev scaffold use a plain `psa` code default; individual decks can select any catalog theme. Other organizations adapt their copies in source.

Updating this catalog requires updating and releasing the affected consumer. Existing frozen artifacts retain their approved appearance. Application UI adoption is tracked separately.

## Brand assets

The Celfocus wordmark is the official transparent SVG; Vodafone's speechmark and flag retain their original geometry. Licensed fonts are supplied privately by the consuming installation. The public catalog declares their family names and system fallback stacks.
