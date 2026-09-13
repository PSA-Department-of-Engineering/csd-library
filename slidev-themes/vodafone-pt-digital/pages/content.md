---
layout: default
section: Section name
---

<!-- The ordinary content page, the shell's "content example", and the one to read before
     writing any others. Grammar: a mono eyebrow behind a red square, the gradient title,
     a one-line lede, the rule (a full-bleed hairline with its red segment), then the
     argument, here three numbered cards with an icon tile each, then a centred callout
     holding the single sentence the room should leave with. The chrome adds the lockup,
     the running head (deck title, `section:` from this frontmatter, the page number)
     and the legal line; a page never draws those.

     RULES THAT COST THE MOST TO REDISCOVER

     1. No inline styles, no <style> block, no class this theme does not define,
        including one-off figure heights, which live in style.css as modifiers
        (vfd-fig--h20 / --h58 / --h96 / --flush).
     2. No literal colours. Use the vfs-* atoms so a drawing restyles with the theme.
     3. Typography inside SVG by CLASS ONLY. A font-size="13.5" presentation attribute
        is captured by UnoCSS attributify and recompiled on the rem scale; it renders
        54px. Use vfs-t / vfs-b / vfs-s / vfs-m / vfs-tag / vfs-num.
     4. Cards never move; vfd-card--lift is the pointer hover the shell opts into, and
        the vfd-rise--N entrances only stagger the arrival.
     5. Ambient motion only in connective tissue (vfs-flow, vfs-halo, vfs-ring, the
        stage). Nothing the room reads moves.
     6. Dash-loop offsets are exact multiples of the dash period or the loop snaps:
        base 7+7=14, --dim 2+8=10, --done 1.5+9=10.5.
     7. The callout never wraps to three lines. If it does, the sentence is too long. -->

<div class="vfd-eyebrow">Section · Eyebrow</div>

# Page title

<div class="vfd-lede">One line that frames the page. One line, not two.</div>

<div class="vfd-rule"></div>

<div class="grid grid-cols-3 gap-4">
  <div class="vfd-card vfd-card--lift vfd-rise">
    <div class="vfd-card-ico"><svg viewBox="-12 -12 24 24" aria-hidden="true"><circle class="vfs-ico" r="10" /><circle class="vfs-ico" r="5.5" /><circle class="vfs-ico--fill" r="1.4" /></svg></div>
    <div class="vfd-card-num">01</div>
    <div class="vfd-card-t">Card one</div>
    <div class="vfd-card-d">First line of description, second line of description.</div>
  </div>
  <div class="vfd-card vfd-card--lift vfd-rise--2">
    <div class="vfd-card-ico"><svg viewBox="-12 -12 24 24" aria-hidden="true"><circle class="vfs-ico" cx="-8" cy="6" r="2.2" /><circle class="vfs-ico" cx="8" cy="6" r="2.2" /><circle class="vfs-ico" cy="-8" r="2.2" /><path class="vfs-ico" d="M-6.4 4.8 L-1.6 -6.4 M6.4 4.8 L1.6 -6.4 M-5.8 6 H5.8" /></svg></div>
    <div class="vfd-card-num">02</div>
    <div class="vfd-card-t">Card two</div>
    <div class="vfd-card-d">First line of description, second line of description.</div>
  </div>
  <div class="vfd-card vfd-card--lift vfd-rise--3">
    <div class="vfd-card-ico"><svg viewBox="-12 -12 24 24" aria-hidden="true"><rect class="vfs-ico" x="-7" y="-7" width="14" height="14" rx="1" /><rect class="vfs-ico" x="-3" y="-3" width="6" height="6" rx="0.5" /><path class="vfs-ico" d="M-3 -7 V-10 M3 -7 V-10 M-3 7 V10 M3 7 V10 M-7 -3 H-10 M-7 3 H-10 M7 -3 H10 M7 3 H10" /></svg></div>
    <div class="vfd-card-num">03</div>
    <div class="vfd-card-t">Card three</div>
    <div class="vfd-card-d">First line of description, second line of description.</div>
  </div>
</div>

<div class="vfd-callout vfd-rise--4"><strong>Centred callout</strong>, the default pull-quote pattern. Keyword phrases render <strong>bold</strong>, the connective tissue stays regular weight.</div>
