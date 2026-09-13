# Foundry design systems

The canonical shared home for PSA Molten, Vodafone Portugal Digital Engineering and Celfocus Digital. Each identity has its approved semantic colours, typography, original marks and design guidance. The published PSA Library briefs are the approval references linked by identity.json.

## One source, generated consumers

Edit identity.json for tokens, DESIGN.md for guidance, or templates/ for shared layouts. Run `python design-systems/generate.py`; CI uses `--check` to detect drift. Generated files are committed consumer projections and must not be edited by hand.

| Consumer | Projection |
|---|---|
| Slidev and psa-slides | slidev-themes/psa, vodafone-digital-engineering, celfocus-digital and their -light variants |
| Protopane | Each identity's generated/dark/protopane.json and generated/light/protopane.json |
| Press instruments | Each identity's generated mode-specific press.css |
| Application adoption | Semantic tokens.css; application rollout is a separate activity |

The three new slide themes share ds- content roles. A deck can switch among them without editing its pages. Existing catalog themes remain selectable; their specialized vocabularies may require page adaptation.

## Installation choice

defaults.json selects this catalog's defaults. A copied installation can change that one file. Press accepts PRESS_IDENTITY and PRESS_MODE; the Slidev scaffold accepts PRESS_SLIDE_THEME or an explicit --theme. psa-slides uses PSA_SLIDES_DEFAULT_THEME, set by its chart's defaultTheme value. A deck's explicit choice takes precedence and is stored with the deck.

Each consumer depends on this catalog. Changing a colour means editing one identity and regenerating, then updating the consuming release. It does not rewrite existing frozen artifacts or automatically deploy applications.

## Brand assets

The marks are extracted from the approved briefs. The Celfocus wordmark is the official transparent SVG; Vodafone's speechmark and flag retain their original geometry. Fonts remain licensed installation assets and are not distributed by this public repository. Supply the Vodafone and Aptos font files through a private asset directory. The themes declare matching family names and system fallback stacks.
