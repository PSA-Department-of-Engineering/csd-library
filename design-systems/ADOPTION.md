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

Application UI adoption is deferred. Begin with one application's palette, logo and shared stylesheet, review it, then proceed application by application. Each organization maintains its concrete branding in source.

## Press audit, 2026-09-13

The operator has accepted Library, Notes, Plans and Slides for this rollout; Slides' remaining chart work belongs to its build task. The next rollout covers the other Foundry applications.

The catalog palette/projection drift check and all 15 theme vocabulary checks pass. Six identity covers render with their original marks in Light/Dark. Corporate font files remain consumer-supplied; verify their loaded faces in each corporate installation.

Press REFs and all seven authoring Skills route appearance to `THEMING.md` and the maintained templates. Flyer scaffolds include the 1120px screen frame, open side fields and fading particles. Workshop semantic colours use the current theme roles. Representative flyer, plan, workshop, MoM, report and executive-brief outputs were checked in Light/Dark at desktop and mobile sizes. The flyer, MoM and authored executive-brief specimens print to one page; schedules and facilitator scripts paginate according to their own formats.
