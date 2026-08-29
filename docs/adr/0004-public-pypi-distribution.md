# ADR-0004: Public PyPI distribution for the Python packages

- **adr_status:** Decided
- **Date:** 2026-08-29
- **Deciders:** Rafael Pires
- **Applies to:** `csd-intent`, `csd-pytest-intent` (the package directory stays `pytest-intent/`; and future Python packages in this repo)
- **Relates to:** supersedes the **Python half** of [ADR-0001](0001-private-package-distribution.md), completing what [ADR-0003](0003-public-npm-distribution.md) began for npm; [ADR-0002](0002-release-automation.md) (how a release is cut); issue [#18](https://github.com/PSA-Department-of-Engineering/csd-library/issues/18)

## Context

[ADR-0001](0001-private-package-distribution.md) kept the Python packages off any registry: consumers install a pinned git tag,

```
pip install "csd-intent @ git+https://github.com/PSA-Department-of-Engineering/csd-library.git@csd-intent-v0.3.2#subdirectory=csd-intent"
```

which needs no credential on a public repo and no publish step at all. That was the right cheap answer while the only consumers were siblings of this repo. Two things make it the wrong answer now.

**The URL couples every consumer's gate to this repo's identity.** The pinned line sits inside the conformance gate every consuming repository runs, and inside the playbook's own CI. A rename, an org move, a deleted tag, or a visibility change breaks the gate *everywhere at once*, in a job whose failure reads as the consumer's problem rather than as a broken dependency reference. The npm half of this same library already closed that hole with ADR-0003.

**It makes a second organization's instantiation depend on this org's GitHub.** An outside consumer standing up its own instantiation inherits a hard dependency on `PSA-Department-of-Engineering`'s GitHub inside the gate that is supposed to prove its own work — and forking this repo just to own the URL is the only escape. A registry name turns that into an ordinary version constraint and removes the main reason such a fork would exist.

Both packages already carry full metadata, LICENSE, README, CHANGELOG, and release-please already cuts their tags. The only missing piece was the upload.

## Decision

### Publish to PyPI, with one rename

`csd-intent` publishes under its own name, which was free. `pytest-intent` cannot: PyPI already carries an unrelated [`pytest-intent`](https://pypi.org/project/pytest-intent/) (celestialorb's requirement-coverage plugin — a genuine namesake, not a squatter). The distribution therefore takes the library's prefix: **`csd-pytest-intent`**.

The rename is distribution-name only. The directory stays `pytest-intent/`, the release-please component and tag namespace stay `pytest-intent-vX.Y.Z`, and the import name stays `pytest_intent` — the package registers no pytest plugin entry point, so there is nothing else to collide. Consumers change exactly one line.

### Trusted publishing, from the caller's workflow

Like npm (ADR-0003's target state), there is no stored credential: each PyPI project names `PSA-Department-of-Engineering/csd-library` + `release.yml` as its **trusted publisher**, and pypi.org mints a short-lived upload token from the release run's OIDC token. Unlike npm, PyPI supports the *first* publish this way too, via **pending publishers** registered before the project exists — so no bootstrap token ever enters the picture. Publishes carry PEP 740 provenance attestations from the same token.

One structural consequence: **the publish job cannot live in the shared `ci/library.yml`.** PyPI validates the OIDC token's `job_workflow_ref` claim, and for a job inside a reusable workflow that claim names the reusable file itself — never the caller's `release.yml` that the publisher registration names (reusable workflows are unsupported, [pypi/warehouse#11096](https://github.com/pypi/warehouse/issues/11096)). So `library.yml` exposes `paths_released` as a `workflow_call` output and this repo's `release.yml` carries the `publish-pypi` matrix job over it — with its steps **inline**, not behind a ci composite action: a composite would leave the OIDC claim intact, but `pypa/gh-action-pypi-publish` derives its Docker invocation from `github.action_repository`, which nested in a cross-repo composite names the composite's repo and yields an invalid image reference (the first publish attempt failed exactly this way). One deliberate deviation from ADR-0003's "a burned release stays burned": `release.yml` takes a `publish-paths` dispatch input that re-runs the upload for a release whose tag was cut but whose upload died on CI plumbing. PyPI never accepts a filename twice and the job skips existing files, so the lever can only *complete* a stuck release, never reissue one.

The job runs GitHub-hosted, the same deliberate ADR-037 exception as `publish-npm` and for the same reason: a public artifact for an audience outside the lab should not ride on homelab uptime.

### The Intent Bundles stay a clone concern — deliberately

Publishing the two distributions does not cover `bundles/`: the `apply-intent-bundle` skill reads them from a sibling clone at `../csd-library/bundles/<topic>/`, and that **stays the documented mechanism**. Bundles carry impls for several runtimes at once (pytest *and* vitest and playwright), so no single ecosystem's registry is a natural home, and packaging them into the Python dist would couple JS consumers to a pip install. The one-line answer consumers get: *packages come from the registries; bundles come from a clone.* Revisit if bundles grow consumers outside this workspace.

## Consequences

- **Consumers swap the git URL for a version constraint.** The gate line becomes `pip install "csd-intent~=0.4.0" "csd-pytest-intent~=0.3.0"`-style (compatible-release ranges, mirroring the npm side's `^`). Nothing about this repo's identity survives in any consumer.
- **First published versions:** `csd-intent` 0.4.0, `csd-pytest-intent` 0.3.0 — continuing each package's existing line, no discontinuity.
- **Existing git-URL pins keep working.** The tags and their metadata are immutable history; old pins of `pytest-intent @ git+…` still resolve (the metadata at those tags still says `pytest-intent`). Only new installs use the new name.
- **The migration is a sweep.** The install line is stamped across every consumer's conformance gate, many `pyproject.toml`s, the playbook's skills and CI, and platform-studio's app-repo scaffolder (which stamps it into every *new* repo). The scaffolder and the shared ci gate lines move with this change; the long tail of consumer repos follows.
- **A burned release stays burned**, exactly as ADR-0003 records for npm: a publish that fails after the tag is cut strands that version, and the recovery is the next release. (`skip-existing` on upload keeps a *partial* fan-out re-runnable without dying on the half that landed.)

## Alternatives considered

| Option | Why not |
|---|---|
| Keep the pinned git URL | This is the problem, restated: every consumer's gate carries this repo's owner, name, and tag, and a second org inherits all three. |
| Publish under `pytest-intent` anyway | The name is taken by an unrelated, active project in the same problem space. PyPI name disputes (PEP 541) are slow and the claim would be weak — the prefix costs one line per consumer. |
| Rename the import to `csd_pytest_intent` too | Breaks every consumer's test imports for zero disambiguation gain: the collision that matters is the distribution name on the index, and no plugin entry point exists to clash at runtime. |
| Put the publish job in the reusable `library.yml` | Fails `invalid-publisher` at upload: PyPI validates `job_workflow_ref`, which names the reusable file, not the registered `release.yml` (pypi/warehouse#11096). |
| Ship bundles inside the Python dist | Couples vitest/playwright bundle consumers to a pip install, and inflates a CLI dist with runner impls it never executes. The clone stays the bundles mechanism. |
