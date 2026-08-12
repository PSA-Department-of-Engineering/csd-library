# Commissioning a deck as a delivery

Paste the filled-in request below into the Foundry Console's **establish** box. It scaffolds
the repo, writes `.delivery/request.md`, and the scope worker turns it into the requirement
spine — so every claim downstream traces back to this text, and anything it leaves open is
settled by the assumption protocol in a pod that cannot ask you.

Two things to do before you drive scope:

- **Commit the content sources** the request points at, under `docs/sources/`. A request that
  names a file which isn't there fails the fresh-eyes gate, which checks that the record's
  claims trace to the request.
- **Pick the theme by name** from this catalog. The design phase adopts it; it does not
  prototype a new one. Copy that theme's folder whole — `style.css`, `meta.json`,
  `global-top.vue`, `package.json` and its own `pages/` — and supply whatever its
  `meta.requires` declares (fonts, brand marks) under the deck's `public/`.

Delete this header and the angle-bracket guidance; keep the prose voice — estimatekit ingests
it verbatim, so vague sentences mint vague requirements.

---

# Request

## What we want

<Who is in the room, and what they must leave believing. Two or three sentences. If there is
an ask at the end — a decision, a budget, a next meeting — say it here, because the deck's
whole shape follows from it.>

Build the deck for <occasion / audience>. It runs <N> minutes, presented by <who>, and it has
to land one thing: <the single claim>.

## The spine

<The running order, in the order the room sees it. One line per part, saying what that part
answers — not what it is called. A part with no answer is a part to cut.>

1. <part> — <what it answers>
2. <part> — <what it answers>
3. <part> — <what it answers>

## What it is built from

The sources are in this repo and are authoritative:

- `docs/sources/<file>` — <what it is, and what it is authoritative for>.
- `docs/sources/<file>` — <what it is, and what it is authoritative for>.

<Say what may be researched beyond them, and apply the harvest rule:> anything you lean on,
you harvest — if a source changed the deck, write it into `docs/sources/` as a short note
with its URL and the date you read it, and cite it in the proposal. The next run is a cold
pod that can only read what is in the repo.

Write our own words. Do not lift a source's text onto a slide.

## Look and feel

Adopt the `<theme-name>` theme from the csd-library slidev-themes catalog, verbatim, and the
`_starter/` pages with it. **The design phase's job is the storyboard, not a new visual
language**: choose the running order and the figure per page, and record the choice. Do not
author a new theme, and do not invent taxonomy classes inside pages — a visual that does not
exist in `style.css` either gets added to `style.css` or does not get used.

<Any brand constraint the theme does not already carry: classification line, a logo lockup,
a language.>

## Boundaries

At most <N> content slides. No new theme, no per-page styling, no `<style>` blocks and no
inline styles — every visual lives in the theme, which is what keeps the deck renderable
under its sibling themes.

Explicitly not wanted, and not to be priced: <the tempting extras — a video, an interactive
build, a second language edition, a leave-behind document>.

Where the choice is between a shorter deck that lands and a longer one that covers, take the
shorter one.

## Done

- Live at `<host>.chaos-architect.dev`, behind the same identity as the studios.
- Exports to PDF, and **the PDF is a real one** — an export that silently produces a stub of a
  few kilobytes is the failure mode here, so check the file size against its sibling exports.
- Zero overflow on every slide, and no SVG text outside its figure. Measure both; an overflow
  check alone cannot see SVG text escaping.
- No literal colours anywhere in `pages/`, so the deck still renders under the sibling themes
  in the family. Prove it by rendering it under one of them.
- Reads complete as a static page: nothing that carries meaning may depend on an animation
  having run.

## Decisions you would otherwise have to assume

- Content language: <language>.
- Classification and footer line: <text, or "the theme's default">.
- Licensing: permissive only for anything vendored; no copyleft in the shipped bundle.
- Images publish to GHCR under the same org and visibility as the rest of the fleet.
- Data classification: <what is in the content — customer names, figures, anything that
  decides whether this can be public>.
- Infrastructure: the Ground is up; there is no availability window to wait for.
- The four gates are signed by <name>, recorded as such.
