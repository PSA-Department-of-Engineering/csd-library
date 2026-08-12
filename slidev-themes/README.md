# Slidev theme catalog

Brand- and organization-specific deck themes for the `bootstrap-slidev-deck` skill (master copy in the sibling `ai-coding-prompts` playbook). The skill resolves themes from its built-in `themes/` directory first, then from this catalog (override with `--themes-root`). Nothing here is published as a package — themes are source assets, read from a clone.

## A theme is self-contained

```
<theme>/
├── style.css        the implementation
├── meta.json        prefix, tiers, chrome, pages, and what it requires
├── global-top.vue   its chrome — absent if the theme has none
├── package.json     only the dependencies THIS theme needs
└── pages/           its own templates, using only what it defines
```

Pick a theme, copy the folder, write the deck. You never assemble a theme from parts kept
elsewhere, and no theme's templates are shared with another's.

**Share the vocabulary, never share the pages.** Class *names* are common where the concept
is common — a lede is a lede — which is what lets one deck be re-skinned. What differs per
theme is which names it implements and what its own templates demonstrate. Sharing a prefix
is not sharing a vocabulary: `celfocus` defines 33 `k-` classes and the showcases define 69,
so a page written against one renders unstyled against the other.

Re-skinning one deck into several variants is a property of *that deck*: it pins the subset
it uses, keeps one master `pages/`, and propagates mechanically. No other deck inherits the
constraint.

## Tiers

`meta.json` declares which tiers a theme implements, and its templates use only those.

| Tier | What it is | Who has it |
|---|---|---|
| `core` | Cover slots, headings, lede, alert, note, cards, stats, dividers — the concepts every deck has | Every theme |
| `atoms` | The `ks-*` figure parts (tiles, dots, rails, plates, masks, text roles) that let a drawn figure carry no literal colour | Themes that draw SVG figures |
| `ambient` | Entrances, marching-ants flows, halos, rings, live dots | Showcase themes only |

A theme without a tier **does not define its classes as no-ops** — it does not have them, and
its templates do not reach for them. `celfocus` and `vodafone` have no `atoms`, so their
content pages are built from HTML flow and pipeline components instead of an SVG figure.

## The catalog

| Theme | Prefix | Tiers | Chrome | Notes |
|---|---|---|---|---|
| `celfocus` | `k` | core | — | Celfocus corporate. Terracotta accent, editorial type, display sizes, flow + pipeline components. |
| `vodafone` | `vf` | core | — | Vodafone corporate. Red on white, Inter; cards, flows, pipelines, stats. Its own `vf-` vocabulary. |
| `celfocus-showcase` | `k` | core, atoms, ambient | 5 | Near-black warm stage, glass surfaces, accent rationed to featured nodes and live flows. |
| `celfocus-showcase-light` | `k` | core, atoms, ambient | 6 | Warm paper stage, white tiles; header carries a deck-name slot. |
| `celfocus-apple-showcase` | `k` | core, atoms, ambient | 6 | Apple grammar — Inter, apple neutrals, radius tiers — ambient layer kept. |
| `vodafone-showcase` | `k` | core, atoms, ambient | 5 | Cool near-black stage, Vodafone red, SF Pro stack. |
| `celfocus-corporate-static` | `k` | core, atoms | 8 | The 2026 corporate template: logo lockup, two-line header, paper texture, no motion. |
| `celfocus-apple-static` | `k` | core, atoms | 5 | Apple grammar rendered statically. |

## Commissioning a deck through the line

[`delivery-request.md`](delivery-request.md) is the fill-in request for the Foundry Console's
**establish** box: it becomes the repo's `.delivery/request.md` and the requirement spine. It
pins the things a deck delivery gets wrong otherwise — that the design phase storyboards
against a catalog theme rather than inventing a visual language, and that "done" includes an
export that is actually a PDF.

## The gate

```bash
node check-themes.mjs          # every theme
node check-themes.mjs <name>   # one
```

It fails a theme when a template uses a class the theme does not define, when `meta.chrome`
names something `style.css` does not define or `global-top.vue` does not produce, or when
the component emits a class the CSS never styles. Asset references are **reported, not
failed**: fonts and brand marks are payload the catalog deliberately does not carry, so
`meta.requires` declares them and the deck supplies them under `public/`.

## Rules that outrank taste

1. **Pages carry no styling.** No inline styles, no `<style>` blocks, no literal colours, and
   no class the theme does not define — including one-off figure heights, which belong in
   `style.css` as modifiers.
2. **Typography inside SVG by class only.** UnoCSS attributify captures a `font-size="13.5"`
   presentation attribute and recompiles it on the rem scale: it renders at 54px.
3. **Motion never carries meaning.** Ambient loops live in connective tissue; nothing the
   room reads may move. Base styles *are* the final resting state, so print and
   reduced-motion render the true slide. SVG-internal transforms do not composite — loops
   ride HTML elements, halos come from radial gradients, never `filter: blur`.
4. **Dash-loop offsets** must be an exact multiple of the variant's dash period or the loop
   snaps: base 9+9=18, `--dim` 2+8=10, `--good` 1.5+9=10.5.
5. **Correctness here is visual, so measure it.** An overflow check cannot see SVG text
   escaping its figure; sample the path against rect bounds. Check an exported PDF's size
   against its siblings — a silent stub export is the failure that hides.
6. **Every theme carries the Slidev goto-dialog repair**
   (`#slidev-goto-dialog:has(#slidev-goto-input:disabled) { display: none !important; }`),
   or the `g` dialog parks its stale result list over the slide after closing.

The taxonomy and the measurements behind these decisions are written up in the
`slidev-theming` flyer.
