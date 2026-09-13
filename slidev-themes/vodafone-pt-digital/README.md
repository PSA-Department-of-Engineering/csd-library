# vodafone-pt-digital

The look of the deck shell Vodafone Portugal's Digital Engineering lead authored, as a
Slidev theme for `bootstrap-slidev-deck`: a near-black stage with red technical grids,
three slowly drifting glows, rising red particles and a vignette; the speechmark lockup
with the Portuguese flag top-left; the deck title over section and page number top-right;
a mono legal line at the foot; Vodafone type; red rationed to eyebrows, numerals, rules,
corner marks and callouts. Class prefix `vfd-` for the page vocabulary, `vfs-` for the
SVG figure atoms.

## Scaffold a deck

```bash
python bootstrap.py --target <path> --title "<Deck Title>" --theme vodafone-pt-digital
cd <path>
npm install
npm run dev      # http://localhost:3030
```

The scaffold copies the marks and chrome. Supply licensed Vodafone fonts through the installation private assets directory or the deck public/fonts/ folder.

## What the theme ships

```
vodafone-pt-digital/
├── meta.json        prefix, tiers, the chrome classes, the page order, what it requires
├── style.css        the implementation
├── global-top.vue   the chrome: the stage, the lockup, the head, the legal line
├── pages/           cover, agenda, section, content, stats, references, thanks-qa
├── public/          the marks (vf-tile-50.png, flag-pt.svg)
└── README.md        this file
```

No `package.json`: the theme needs nothing beyond what the scaffold installs.

## The brand payload

**The Vodafone face.** The stylesheet declares Vodafone at weights 300 to 800 from /fonts/Vodafone-<weight>.woff2. These licensed files are supplied by the installation. The public catalog ships the fallback stack and the font declarations.

**The marks.** The lockup's speechmark tile and the Portuguese flag are embedded in
`global-top.vue` (a data URI and an inline SVG), so the chrome renders whether or not a
deck's `public/` was ever populated. The same two files sit in the theme's `public/` for
pages that want to place them in content (`/vf-tile-50.png`, `/flag-pt.svg`), and the
scaffolder copies that folder into the deck's `public/`, so either path resolves straight
after the scaffold with nothing to fetch by hand.

Slidev's default theme also links its Google Fonts (Nunito Sans, Fira Code) on every
page. They are never used, since the theme sets its own family everywhere, and the deck
builds fine either way; a deck that must not touch the network adds `fonts: provider: none`
to its `slides.md` headmatter.

## How the chrome works

`global-top.vue` is Slidev's top global layer. It emits the **stage** once, positioned
under every slide: `style.css` puts it at `z-index: -1` inside the scaled slide container
and keeps the layout transparent, so the connective tissue stays continuous while pages
transition, and it never repaints with the slide. It then reads the current page's
frontmatter `class` and `section`:

| `class:` on the page | Lockup | Head (title, section, page) | Legal line | Stage |
|---|---|---|---|---|
| (none) | yes | yes | yes | yes |
| `vfd-cover` | yes (the shell's cover carries it) | no | no (the cover draws its own centred foot line) | yes |
| `vfd-section` | yes | yes | yes | yes |
| `vfd-bare vfd-close` | no | no | no | covered by the red field; the chrome draws the speechmark |

The chrome reads the slide through `useSlideContext().$slidev.nav` rather than the shared
`useNav()`: in print and export Slidev renders every page with its own fixed nav while
the shared one stays on slide 1, which is why earlier Vodafone decks exported every page
without its header. This theme's export carries the chrome on every page.

## Pages

Every template uses only classes the theme defines, plus Slidev's UnoCSS utilities
(`grid`, `gap-*`, `my-auto`, `text-xs`). The catalog gate (`check-themes.mjs` in
`csd-library/slidev-themes`) passes on this folder. The content page's opening comment
lists the rules that cost the most to rediscover; read it before writing a page.

| Page | What it is |
|---|---|
| `cover` | corner brackets, the orbit figure, eyebrow, the gradient title with its bloom, kicker, red bar, description, mono foot line |
| `agenda` | eyebrow, title, rule, a ledger of red numerals with a mono clause on the right |
| `section` | corner brackets, a red ghost numeral, eyebrow, the gradient title, one line, the red segment |
| `content` | eyebrow, title, lede, rule, three numbered cards with icon tiles, a centred callout |
| `stats` | red numerals with mono labels, one hero, a note, a callout |
| `references` | three columns under mono column heads |
| `thanks-qa` | "Together we can" on the red field, the shell's close |

## Doctrine

Motion never carries meaning and never moves anything you read. The stage, the flows
(`vfs-flow`), halos, rings and the cover orbit loop; text, cards and tiles never do,
entrances (`vfd-rise`, `--2` to `--5`) excepted: once, settling into place. Base styles are
the final static state, so print and reduced motion render the true slide; every
animation is CSS, and one media query stops them all. Typography inside SVG is sized by
class only (`vfs-t`, `vfs-b`, `vfs-s`, `vfs-m`, `vfs-tag`, `vfs-num`): a `font-size`
presentation attribute is captured by UnoCSS attributify and recompiled on the rem scale.
Pages carry no literal colour; the tokens in `style.css` are the brand.

## Where the shell could not be matched exactly

- The shell is drawn on a 1280 by 800 stage (16:10); Slidev's canvas is 980 by 551.25
  (16:9). Every measure is the shell's scaled by 0.766 horizontally and 0.689
  vertically, so the proportions of the header, rule, cards and callout hold, and the
  stage's grids are scaled the same way; the slide is a touch wider in feel.
- The shell animates its glows and particles with SMIL inside each slide's SVG. Here they
  are HTML elements animated with CSS, on the same periods and paths, so they composite
  cheaply and stop under print and reduced motion, which SMIL cannot do.
- The shell's cover title is a gradient-filled SVG text; here it is HTML text with a
  background-clipped gradient, fitted to the text so the red lands on the last letters.
- The shell's close is a photograph of the red field with the speechmark and the line;
  here the field is a CSS gradient sampled from it, the speechmark is the tile, the line
  is typeset in the brand face. A deck that prefers the photograph puts it under
  `public/` and adds an `<img>` to the page, above the line.
