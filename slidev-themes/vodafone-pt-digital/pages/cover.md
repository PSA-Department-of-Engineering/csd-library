---
layout: default
class: vfd-cover
section: Cover
---

<!-- Cover, the shell's first slide. `vfd-cover` on the frontmatter is what the chrome
     reads: it keeps the lockup top-left (the shell's cover carries it) and drops the
     running head and the legal line, so keep the class. Slot order: the corner brackets
     and the orbit figure (decorative, fixed), then a centred stack: eyebrow, the title,
     the kicker, a short red bar, one line of description; the mono foot line last.

     The title carries the shell's white-to-red gradient and bloom. To paint its last
     word or letter solid red as the shell does ("Project X"), wrap it:
     # Project <span class="vfd-accent">X</span>
     The vfd-rise--N steps only stagger the arrival; the base state is the finished
     slide, so a print or a paused deck reads complete. -->

<svg class="vfd-corners" viewBox="0 0 980 551" aria-hidden="true">
  <path d="M20 61 V20 H61" /><path d="M960 61 V20 H919" /><path d="M20 490 V531 H61" /><path d="M960 490 V531 H919" />
</svg>

<svg class="vfd-orbit" viewBox="0 0 980 551" aria-hidden="true">
  <defs><radialGradient id="vfd-orbit-grad" cx="50%" cy="50%" r="60%"><stop class="vfd-orbit-stop-a" offset="0" /><stop class="vfd-orbit-stop-b" offset="1" /></radialGradient></defs>
  <ellipse class="vfd-orbit-glow" cx="490" cy="207" rx="230" ry="158" />
  <circle class="vfd-orbit-ring1" cx="490" cy="207" r="92" />
  <circle class="vfd-orbit-ring2" cx="490" cy="207" r="69" />
  <circle class="vfd-orbit-ring3" cx="490" cy="207" r="46" />
  <g class="vfd-orbit-sat"><rect x="533.6" y="204.7" width="4.6" height="4.6" /><rect x="441.8" y="204.7" width="4.6" height="4.6" /></g>
  <circle class="vfd-orbit-core-glow" cx="490" cy="207" r="14" />
  <circle class="vfd-orbit-core" cx="490" cy="207" r="5.4" />
</svg>

<div class="vfd-eyebrow vfd-rise">Eyebrow · Category</div>

# Presentation title

<div class="vfd-kicker vfd-rise--2">Presentation subtitle</div>

<div class="vfd-bar vfd-rise--3"></div>

<div class="vfd-desc vfd-rise--4">One-line description of the initiative</div>

<div class="vfd-cover-foot">Vodafone Portugal · Digital Engineering</div>
