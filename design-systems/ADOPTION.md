# Adoption and release

The source is `design-systems/<identity>/identity.json`, original assets and `DESIGN.md`. Layouts belong to each consumer's authored styles and templates.

| Repository | Responsibility |
|---|---|
| csd-library | Three approved palettes and marks, six authored slide themes, original ADC theme, token projections and review gallery |
| protopane | Exact packaged Dark/Light presets imported from the catalog |
| playbook | PSA palettes embedded in each Press template; PSA-default Slidev scaffold |
| psa-slides | PSA code default for new decks; selected theme's stylesheet, chrome and assets |

Publish the catalog first, then consumer repositories. Verify CI and the serving Protopane and psa-slides versions. Refresh the installed Playbook skills. Verify the six live presets and a new deck's persisted theme and build output.

Licensed fonts are private consumer assets. Preserve original filenames and review actual rendered typography. Existing artifacts retain their appearance until deliberately regenerated.

Each organization maintains its concrete branding in source. Application adoption uses each consumer's shared stylesheet, wordmark and authored background composition. Light/Dark is a reading preference; material and motion are authored choices.

## Press audit, 2026-09-13

Library's application and published house briefs are adopted. Notes, Plans and Slides completed their software builds separately from the design work; build completion was not design acceptance. Their PSA application and output changes are committed and pushed, with release verification in progress. The next rollout covers the other Foundry applications.

Notes and Slides own their app styling in the shared CSS, shell and local appearance component. Plans uses the same arrangement, with its canonical renderer scoped to the rendered document so its colours cannot overwrite application controls. All three app backgrounds carry open side fields and rising, fading particles in Light/Dark, with hidden-page pause and reduced-motion support. Notes' current MoM source is mechanically vendored from Playbook; Plans uses one renderer for the cockpit and standalone export. Slides' PSA-default build passes the catalog gate and produces a checked PDF. Issued outputs retain their stored bytes.

The catalog palette/projection drift check and all 15 theme vocabulary checks pass. Six identity covers render with their original marks in Light/Dark. Corporate font files remain consumer-supplied; verify their loaded faces in each corporate installation.

Press REFs and all seven authoring Skills route appearance to `THEMING.md` and the maintained templates. Flyer scaffolds include the 1120px screen frame, open side fields and fading particles. Workshop semantic colours use the current theme roles. Representative flyer, plan, workshop, MoM, report and executive-brief outputs were checked in Light/Dark at desktop and mobile sizes. The flyer, MoM and authored executive-brief specimens print to one page; schedules and facilitator scripts paginate according to their own formats.
