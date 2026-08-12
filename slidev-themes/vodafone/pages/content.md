---
layout: default
section: Section name
---

<!-- The ordinary content page.

     THIS THEME HAS NO SVG ATOM SYSTEM. There are no ks-* classes, so a drawn figure would
     have to carry literal colours in the page - the one thing that makes a deck
     impossible to re-skin. This theme ships two HTML diagram components instead:

       vf-flow      > vf-flow-step (+ --primary / --dark / --blue), split by vf-flow-arrow
       vf-pipeline  > vf-pipeline-stage (+ --green / --orange / --red / --blue)
                      each holding vf-stage-title + vf-stage-items

     Reach for the flow when the argument is a sequence, the pipeline when it is stages
     with states. An argument that genuinely needs a drawn figure wants a showcase theme,
     not a hand-coloured SVG in here.

     The other rules hold: no inline styles, no <style> block, no literal colours, and no
     class this theme does not define. -->

<div class="vf-section-title">Page title</div>

<div class="vf-note">One line that frames the page. One line, not two.</div>

<div class="vf-flow">
  <div class="vf-flow-step">The thing itself</div>
  <div class="vf-flow-arrow">→</div>
  <div class="vf-flow-step">The next thing</div>
  <div class="vf-flow-arrow">→</div>
  <div class="vf-flow-step vf-flow-step--primary">Where it ends</div>
</div>

<div class="vf-pipeline">
  <div class="vf-pipeline-stage vf-pipeline-stage--green">
    <div class="vf-stage-title">Stage one</div>
    <div class="vf-stage-items">what it holds, in a clause</div>
  </div>
  <div class="vf-pipeline-stage vf-pipeline-stage--orange">
    <div class="vf-stage-title">Stage two</div>
    <div class="vf-stage-items">what it holds, in a clause</div>
  </div>
  <div class="vf-pipeline-stage vf-pipeline-stage--red">
    <div class="vf-stage-title">Stage three</div>
    <div class="vf-stage-items">what it holds, in a clause</div>
  </div>
</div>

<div class="vf-alert vf-alert--info">The one sentence the room should leave with.</div>

<div class="vf-footer">
  <span class="vf-brand">VODAFONE</span>
  <span>Presenter Name · Month Year</span>
</div>
