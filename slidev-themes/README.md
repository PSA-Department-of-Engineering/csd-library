# Slidev theme catalog

Brand- and organization-specific themes for the `bootstrap-slidev-deck` skill (master copy in the sibling `ai-coding-prompts` playbook). The skill resolves themes from its built-in `themes/` directory first, then from this catalog (override with `--themes-root`).

Each theme is a directory:

```
<name>/
├── style.css    # the theme, copied verbatim into the scaffolded deck
└── meta.json    # {"prefix": "<short>", "description": "..."}
```

`prefix` is the namespace for the theme's utility classes (e.g. `vf-footer`, `k-alert`). Themes are immutable per brand: meaningful variations get a new directory here; project-specific one-offs use the skill's `--theme-css` flag instead.

A theme is only half a template, so the other half lives once, in [`_starter/`](_starter/): the templated pages (title, agenda, section divider, content), the `global-top.vue` chrome, and the scaffold. It is shared rather than copied per theme because every `k`-prefixed theme renders the same pages — duplicating them would break the invariant that makes the family a family. Start a deck by copying `_starter/` plus one theme's `style.css`; to commission one through the Foundry line instead, fill in [`_starter/delivery-request.md`](_starter/delivery-request.md) and paste it into the Console's establish box.

| Theme | Prefix | Notes |
|---|---|---|
| `vodafone` | `vf` | Vodafone corporate. Red accent on white, Inter sans, full standard taxonomy. |
| `celfocus` | `k` | Celfocus corporate. Terracotta accent, editorial typography, standard taxonomy plus decorative extras (eyebrow, kicker, big, huge, tag). |
| `celfocus-showcase` | `k` | Celfocus showcase (dark). Glass surfaces, rationed accent, ambient animation layer, title/section templates. |
| `celfocus-showcase-light` | `k` | Celfocus showcase (light). Warm paper stage, same taxonomy and ambient layer. |
| `celfocus-apple-showcase` | `k` | Celfocus over the Apple grammar, showcase edition. Inter type, apple neutrals, ambient layer kept. |
| `celfocus-corporate-static` | `k` | The 2026 corporate template extended with the showcase taxonomy, rendered statically (no motion). |
| `celfocus-apple-static` | `k` | The Apple grammar extended with the showcase taxonomy, rendered statically. |
| `vodafone-showcase` | `k` | Vodafone showcase (dark). Same taxonomy and doctrine as `celfocus-showcase`; cool stage, Vodafone red, SF Pro stack. |

All `k`-prefixed themes render the same deck pages: content decks keep one master `pages/` set and swap `style.css` (see the ADC deck-8 series and its `sync-variants.ps1` for the mechanical propagation pattern). Pages must carry no literal colors: figure atoms (`ks-bdot`, `ks-sep`, `ks-plate`, `ks-mask`, `ks-frame`, `ks-hstop`, `ks-dashed`) exist so every theme restyles them.

## The showcase family

Showcase themes deliberately share the `k-` taxonomy so one deck's pages render under any of them (brand swap = replace `style.css`). Each carries, in its file header, the ambient-animation doctrine earned in production:

- Motion never carries meaning and never moves anything you read; it lives in connective tissue (flows, halos, pings). Base styles ARE the final static state; print and reduced-motion render the true resting slide.
- Typography in SVG figures via classes only: a `font-size="N"` presentation attribute is captured by UnoCSS attributify and compiled on the rem scale (13.5 becomes 3.375rem).
- SVG content groups never animate transforms (no compositing; whole-figure repaint). Halo softness comes from radial gradients, never `filter: blur`.
- Boxes that occlude a routed line use the opaque `ks-solid*` twins; glass fills are translucent and ghost anything behind them.

Every theme in this catalog, showcase or corporate, must carry the Slidev goto-dialog repair (`#slidev-goto-dialog:has(#slidev-goto-input:disabled) { display: none !important; }`): the dialog otherwise parks its stale results list over the slide after closing.
