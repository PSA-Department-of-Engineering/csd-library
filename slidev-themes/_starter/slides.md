---
theme: default
colorSchema: dark
class: k-cover
title: "Deck title"
info: |
  ## Deck title
titleTemplate: "%s"
download: true
exportFilename: deck
drawings:
  persist: false
transition: slide-left
mdc: true
fonts:
  provider: none
---

<!-- The cover is this file's own slide, so t1-title.md's markup lives here inline.
     Keep the slot order: brand, eyebrow, title, kicker, rail, meta. -->

<div class="k-title-brand k-rise">B R A N D</div>

<div class="k-eyebrow k-rise--2">Practice · Engagement</div>

<h1 class="k-rise--2">Deck title</h1>

<div class="k-kicker k-rise--3">
One sentence framing what this deck is and who it is for. Two lines at most.
</div>

<svg class="k-section-rail k-rise--4" viewBox="0 0 560 8" aria-hidden="true"><path class="k-live-flow" d="M 4 4 H 556" /></svg>

<div class="k-title-meta k-rise--5">
  <span>Presenter Name</span>
  <span class="k-gate-dot"></span>
  <span>Month Year</span>
</div>

<!-- One import per slide, in running order. Rename the templates into real pages
     (01-…, 02-…) as you write them; never edit a variant deck's pages directly. -->

---
src: ./pages/t2-agenda.md
---

---
src: ./pages/t3-section.md
---

---
src: ./pages/t4-content.md
---
