---
layout: default
section: Section name
---

<!-- The ordinary content page, and the one worth reading before you write any others.
     The grammar is fixed: title, one-line lede, a figure that carries the argument, and
     a bottom alert holding the single sentence the room should leave with.

     THE RULES THAT COST THE MOST TO REDISCOVER

     1. No inline styles, no <style> block. Every visual lives in the theme's style.css,
        including one-off figure heights (.k-fig--h58, .k-fig--h96). This is what lets one
        pages/ set render under every theme in the family.

     2. No literal colours here. Use the figure atoms — ks-bdot, ks-sep, ks-plate, ks-mask,
        ks-frame, ks-hstop, ks-dashed — so a theme can restyle the same drawing.

     3. Typography inside SVG by CLASS ONLY. A font-size="13.5" presentation attribute is
        captured by UnoCSS attributify and recompiled on the rem scale: 13.5 renders 54px.
        Use .ks-t / .ks-t--sm / .ks-m / .ks-tag / .ks-b.

     4. Ambient motion only, in connective tissue. Marching-ants flows on paths are cheap;
        transforms INSIDE an SVG do not composite and repaint the whole figure, so any loop
        that moves belongs on an HTML element with will-change. Halo softness comes from a
        radialGradient, never filter: blur. Nothing the audience reads may move.

     5. Base styles ARE the final resting state. k-rise--N only staggers the arrival. If a
        page depends on an animation having run, it prints blank.

     6. Dash-loop offsets must be an exact multiple of the variant's dash period, or the
        loop visibly snaps: base 9+9=18 → -36, --dim 2+8=10 → -40, --good 1.5+9=10.5 → -42.

     7. Measure geometry; do not eyeball it. An overflow check cannot see SVG text escaping
        its figure, and a connector that "looks off" is answered by sampling the path
        (getPointAtLength) against the rect bounds — not by another look at a screenshot.

     8. The bottom alert never wraps to two lines. If it does, the sentence is too long. -->

# Page title

<div class="k-lede">
One line that frames the page. One line — not two.
</div>

<svg class="k-fig k-rise" viewBox="0 0 1240 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Describe the figure for a reader who cannot see it">
  <!-- The connective flow: a dim marching-ants rail behind, a live one for the stretch
       that matters. Endpoints on a grid of N columns land at (2k+1)/2N of the viewBox
       width, so figure and column headings line up exactly. -->
  <path class="k-live-flow k-live-flow--dim" d="M 16 150 H 620" />
  <path class="k-live-flow" d="M 620 150 H 1224" />

  <!-- Tiles ride on opaque twins (ks-solid*) wherever a routed line passes behind them:
       glass fills are translucent and ghost the line through. Uniform widths, or the gaps
       between them stop being uniform. -->
  <g class="k-rise--2">
    <rect class="ks-solid" x="16" y="104" width="280" height="92" rx="12" />
    <text class="ks-tag" x="36" y="130">LABEL</text>
    <text class="ks-t ks-t--sm" x="36" y="152">The thing itself</text>
    <text class="ks-m" x="36" y="172">what it does, lower case</text>
  </g>

  <g class="k-rise--3">
    <rect class="ks-solid" x="480" y="104" width="280" height="92" rx="12" />
    <text class="ks-tag" x="500" y="130">LABEL</text>
    <text class="ks-t ks-t--sm" x="500" y="152">The next thing</text>
    <text class="ks-m" x="500" y="172">what it does, lower case</text>
  </g>

  <g class="k-rise--4">
    <rect class="ks-solid--hl" x="944" y="104" width="280" height="92" rx="12" />
    <text class="ks-tag--red" x="964" y="130">EMPHASIS</text>
    <text class="ks-t ks-t--sm" x="964" y="152">Where it ends</text>
    <text class="ks-m" x="964" y="172">the live end of the flow</text>
    <circle class="ks-dot" cx="1200" cy="122" r="4.5" />
  </g>
</svg>

<div class="k-alert mt-auto k-rise--5">

The one sentence the room should leave with, with <strong>the load-bearing words</strong> emphasised.

</div>
