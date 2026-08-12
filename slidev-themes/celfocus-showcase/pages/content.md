---
layout: default
section: Section name
---

<!-- The ordinary content page, and the one to read before writing any others. Grammar:
     title, one-line lede, a figure that carries the argument, a bottom alert holding the
     single sentence the room should leave with.

     RULES THAT COST THE MOST TO REDISCOVER

     1. No inline styles, no <style> block, no class this theme does not define -
        including one-off figure heights, which live in style.css as modifiers
        (k-fig--h20 / --h58 / --h96 / --flush).
     2. No literal colours. Use the ks-* atoms so the drawing restyles with the theme.
     3. Typography inside SVG by CLASS ONLY. A font-size="13.5" presentation attribute is
        captured by UnoCSS attributify and recompiled on the rem scale - it renders 54px.
        Use ks-t / ks-t--sm / ks-m / ks-tag / ks-b.
     4. Tiles that a routed line passes behind ride the opaque ks-solid* twins; the glass
        fills are translucent and ghost the line through.
     5. Ambient motion only, in connective tissue. Transforms INSIDE an SVG do not
        composite and repaint the whole figure; loops belong on HTML elements. Halo
        softness comes from a radial gradient, never filter: blur.
     6. Dash-loop offsets must be an exact multiple of the variant's dash period or the
        loop snaps: base 9+9=18, --dim 2+8=10, --good 1.5+9=10.5.
     7. Measure geometry, don't eyeball it. An overflow check cannot see SVG text escaping
        its figure; sample the path against rect bounds instead.
     8. The bottom alert never wraps to two lines. If it does, the sentence is too long. -->

# Page title

<div class="k-lede">
One line that frames the page. One line, not two.
</div>

<svg class="k-fig k-rise" viewBox="0 0 1240 300" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Describe the figure for a reader who cannot see it">
  <!-- The connective flow: dim where it is context, live where it is the point.
       Endpoints on an N-column grid land at (2k+1)/2N of the viewBox width, so the
       figure and any columns beneath it line up exactly. -->
  <path class="k-live-flow k-live-flow--dim" d="M 16 150 H 620" />
  <path class="k-live-flow" d="M 620 150 H 1224" />

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
