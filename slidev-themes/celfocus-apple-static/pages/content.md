---
layout: default
section: Section name
---

<!-- The ordinary content page. Grammar: title, one-line lede, the argument, and a bottom
     alert holding the sentence the room should leave with.

     This theme draws the same arguments as the showcase themes, without the ambient
     layer: the flow rails are plain rules, not marching ants, and nothing animates in.
     The rules that still apply:

     1. No inline styles, no <style> block, and no class this theme does not define -
        one-off figure heights live in style.css as modifiers (k-fig--h20/--h58/--h96).
     2. No literal colours. The ks-* atoms exist so the drawing restyles with the theme.
     3. Typography inside SVG by CLASS ONLY. A font-size="13.5" presentation attribute is
        captured by UnoCSS attributify and recompiled on the rem scale - it renders 54px.
     4. Tiles a routed line passes behind ride the opaque ks-solid* twins.
     5. Measure geometry rather than eyeballing it: an overflow check cannot see SVG text
        escaping its figure.
     6. The bottom alert never wraps to two lines.

     For a step sequence, k-stages / k-stage / k-stage-t / k-stage-x is this theme's own
     component and reads better than drawing one. -->

# Page title

<div class="k-lede">
One line that frames the page. One line, not two.
</div>

<svg class="k-fig" viewBox="0 0 1240 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Describe the figure for a reader who cannot see it">
  <path class="k-live-flow k-live-flow--dim" d="M 16 150 H 620" />
  <path class="k-live-flow" d="M 620 150 H 1224" />

  <g>
    <rect class="ks-solid" x="16" y="104" width="280" height="92" rx="12" />
    <text class="ks-tag" x="36" y="130">LABEL</text>
    <text class="ks-t ks-t--sm" x="36" y="152">The thing itself</text>
    <text class="ks-m" x="36" y="172">what it does, lower case</text>
  </g>

  <g>
    <rect class="ks-solid" x="480" y="104" width="280" height="92" rx="12" />
    <text class="ks-tag" x="500" y="130">LABEL</text>
    <text class="ks-t ks-t--sm" x="500" y="152">The next thing</text>
    <text class="ks-m" x="500" y="172">what it does, lower case</text>
  </g>

  <g>
    <rect class="ks-solid--hl" x="944" y="104" width="280" height="92" rx="12" />
    <text class="ks-tag--red" x="964" y="130">EMPHASIS</text>
    <text class="ks-t ks-t--sm" x="964" y="152">Where it ends</text>
    <text class="ks-m" x="964" y="172">the end of the flow</text>
    <circle class="ks-dot" cx="1200" cy="122" r="4.5" />
  </g>
</svg>

<div class="k-alert mt-auto">

The one sentence the room should leave with, with <strong>the load-bearing words</strong> emphasised.

</div>
