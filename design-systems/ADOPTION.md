# Adoption and release

The identity source is design-systems/<identity>/identity.json with its original assets and DESIGN.md guidance. Shared templates generate the consumer projections. defaults.json selects this installation's identity and reading/deck modes.

## Prepared consumers

| Repository | Consumer change |
|---|---|
| csd-library | Three identity definitions, six generated themes, original Vodafone ADC theme, Press CSS, Protopane JSON and interactive preview |
| protopane | Exact packaged presets in both modes, imported mechanically from this catalog |
| playbook | Press identity layer for reading instruments and their email output; installation-aware Slidev scaffold |
| psa-slides | Persistent default theme selection; complete theme chrome/assets adoption; configurable private assets and browser executable |

## Release order

1. Review preview.html and the generated document/deck examples.
2. Publish the csd-library catalog commit first.
3. Publish Protopane and psa-slides, then verify their serving releases. The psa-slides chart defaultTheme selects its installation identity; chart changes require the installation's chart pin to advance.
4. Publish the Playbook and refresh installed skills so the active harness uses the shared Press layer and updated scaffold.
5. Verify a newly created deck's persisted theme and built output, and the six presets returned by the live Protopane library.

Licensed fonts are installation assets. Supply them under the consumer's private asset directory and retain their original filenames. The public catalog uses the approved font-family declarations with fallback stacks. Existing artifacts retain their frozen appearance until deliberately regenerated.

Application UI adoption is deferred. Its first step is one application's semantic token mapping, followed by a visual review; extending that mapping across other applications is a separate release scope.
