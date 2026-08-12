# Starter

The pages half of a theme. A theme in this catalog is a `style.css` (plus `meta.json`);
this folder is everything else a new deck needs — the templated pages, the chrome
component, and the scaffold — so "use the templates" means layouts, not just colours.

**Scope: the showcase family only** (`celfocus-showcase`, `-light`, `celfocus-apple-showcase`,
`vodafone-showcase`). These pages are not universal and were never validated as such —
measured against the catalog, they leave 11 classes undefined under the two static themes
(the whole `k-agenda*` family, `k-section-num`, `k-section-sub`, `k-rise--2..5`) and 29
undefined under `celfocus`, whose 33-class `k-` vocabulary is a different one that happens to
share the prefix.

Each theme is to ship its own `pages/`, because a template's job is to demonstrate what is
idiomatic in *that* theme — a static theme's content page should draw the same argument
without the ambient layer, not inherit a page that reaches for entrances it does not
implement. This folder is the showcase family's set until that lands. See the
`slidev-theming` flyer for the taxonomy and the tiers.

## Start a deck as a delivery

[`delivery-request.md`](delivery-request.md) is the fill-in request for commissioning a deck
through the Foundry line: paste it into the Console's **establish** box and it becomes the
repo's `.delivery/request.md` and the requirement spine. It pins the things a deck delivery
gets wrong otherwise — that the design phase storyboards rather than invents a visual
language, and that "done" includes a PDF that is actually a PDF.

No Dockerfile or chart lives here on purpose: `establish` already scaffolds `devops/`, `k8s/`
and the workflows, and a second copy in this catalog would drift against it.

## Start a deck by hand

```
mkdir my-deck && cd my-deck
cp -r <catalog>/slidev-themes/_starter/*        .
cp    <catalog>/slidev-themes/<theme>/style.css .
npm install && npm run dev
```

Then rename `pages/t*.md` into your real pages (`01-…`, `02-…`), and list them in
`slides.md` in order. `t1-title.md` is the cover: `slides.md` carries its markup inline
because the cover is the deck's own frontmatter slide.

## The templates

| Page | What it is |
| --- | --- |
| `t1-title.md` | The branded title slide: brand, eyebrow, title, kicker, rail, meta |
| `t2-agenda.md` | The agenda ledger: numbered rows, title + subtitle per row |
| `t3-section.md` | A section divider: ghost numeral, eyebrow, title, sub, rail |
| `t4-content.md` | The ordinary content page: title, lede, figure, bottom alert |

`t4-content.md` is the one to read first — it carries the rules that are expensive to
rediscover, as comments at the point where you would break them.

## Rules that outrank taste

1. **No inline styles and no `<style>` blocks in pages.** Every visual belongs in the
   theme's `style.css`, including one-off heights (`.k-fig--h96`) — that is what keeps one
   `pages/` set renderable under every theme.
2. **No literal colours in pages.** Use the figure atoms (`ks-bdot`, `ks-sep`, `ks-plate`,
   `ks-mask`, `ks-frame`, `ks-hstop`, `ks-dashed`) so a theme can restyle them.
3. **Typography inside SVG by class only.** UnoCSS attributify captures a
   `font-size="13.5"` presentation attribute and recompiles it on the rem scale — 13.5
   becomes 54px. Use `.ks-t`, `.ks-m`, `.ks-tag`.
4. **Motion never carries meaning.** Ambient loops live in connective tissue only; the base
   styles are the final resting state, so print and reduced-motion render the true slide.
   Nothing you read may move.
5. **Measure geometry, don't eyeball it.** An overflow check cannot see SVG text escaping
   its figure. Sample paths (`getPointAtLength`) against rect bounds when a connector looks
   wrong.

## Scaffold notes

`package.json` pins Slidev and the two Inter families the apple themes need; drop those two
dependencies if your theme uses system fonts. `global-top.vue` is the persistent chrome
(wordmark, section/page header, legal footer) — set the two constants at the top of its
script block, and note it hides itself on any slide whose `class` contains `k-cover`.

Every theme's `style.css` already carries the Slidev goto-dialog repair
(`#slidev-goto-dialog:has(#slidev-goto-input:disabled)`); without it the `g` dialog leaves
a stale result list over the slide.
