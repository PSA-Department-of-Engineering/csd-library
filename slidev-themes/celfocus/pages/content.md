---
layout: default
section: Section name
---

<!-- The ordinary content page.

     THIS THEME HAS NO SVG ATOM SYSTEM. There are no ks-* classes here, so a drawn figure
     would have to carry literal colours in the page - which is the one thing that makes a
     deck impossible to re-skin. Instead this theme ships two HTML diagram components and
     the content page uses them:

       k-flow      > k-flow-step (+ --primary / --dark), separated by k-flow-arrow
       k-pipeline  > k-pipeline-stage (+ --accent / --ok / --warn / --bad)
                     each holding k-stage-title + k-stage-items

     Reach for the flow when the argument is a sequence, the pipeline when it is a set of
     stages with states. If an argument genuinely needs a drawn figure, it wants one of the
     showcase themes, not a hand-coloured SVG in here.

     The other rules still hold: no inline styles, no <style> block, no literal colours,
     and no class this theme does not define. -->

<div class="k-section-title">Page title</div>

<div class="k-note">One line that frames the page. One line, not two.</div>

<div class="k-flow">
  <div class="k-flow-step">The thing itself</div>
  <div class="k-flow-arrow">→</div>
  <div class="k-flow-step">The next thing</div>
  <div class="k-flow-arrow">→</div>
  <div class="k-flow-step k-flow-step--primary">Where it ends</div>
</div>

<div class="k-pipeline">
  <div class="k-pipeline-stage k-pipeline-stage--ok">
    <div class="k-stage-title">Stage one</div>
    <div class="k-stage-items">what it holds, in a clause</div>
  </div>
  <div class="k-pipeline-stage k-pipeline-stage--warn">
    <div class="k-stage-title">Stage two</div>
    <div class="k-stage-items">what it holds, in a clause</div>
  </div>
  <div class="k-pipeline-stage k-pipeline-stage--accent">
    <div class="k-stage-title">Stage three</div>
    <div class="k-stage-items">what it holds, in a clause</div>
  </div>
</div>

<div class="k-alert k-alert--info">The one sentence the room should leave with.</div>

<div class="k-footer">
  <span class="k-brand">BRAND</span>
  <span>Presenter Name · Month Year</span>
</div>
