# ADR-0003: Public npm distribution for the JS/TS packages

- **adr_status:** Decided
- **Date:** 2026-08-09
- **Deciders:** Rafael Pires
- **Applies to:** `vitest-intent`, `playwright-intent`, `starlight-theme` (and future npm packages in this repo)
- **Relates to:** supersedes the **npm half** of [ADR-0001](0001-private-package-distribution.md) (its Python half stands unchanged); [ADR-0002](0002-release-automation.md) (how a release is cut); the homelab platform's ADR-037 (all CI on ARC runners)

## Context

[ADR-0001](0001-private-package-distribution.md) sent the npm packages to GitHub Packages, taking private visibility from the repository. Two things have changed since.

`csd-library` itself is now public. But **GitHub Packages requires an authentication token to read a package even when that package is public.** The registry has no anonymous read. So the auth requirement ADR-0001 accepted as the cost of privacy did not go away when the repo stopped being private — it survived as pure friction with nothing left to protect.

That friction is not local to this repo. Every consumer carries it:

- an `.npmrc` mapping the scope to `npm.pkg.github.com` with `${NODE_AUTH_TOKEN}`
- a `setup-node-auth` step in every Node CI job
- a `PACKAGES_READ_TOKEN` secret for any consumer outside this org
- a README line telling a human to export a token before `npm ci`

And it has a consequence ADR-0001 did not anticipate: **an app repo that depends on these packages cannot be open-sourced in any useful sense.** Making it public produces a repo whose source is readable and whose build is not runnable — an outside forker with no PSA token gets a 401 on `npm ci`. The source is visible; the project is not forkable.

The Python packages in this repo need none of this. They install from a git tag on a public repository, which is anonymous by construction. The npm half was the only asymmetry, and it was an accident of registry choice rather than a decision anyone made.

## Decision

### Publish to the public npm registry, keeping the scope

Packages go to `registry.npmjs.org` under the **same scope**, `@psa-department-of-engineering`, now backed by an npm organization of that name (free tier: unlimited public packages).

The scope is preserved deliberately. A shorter or neutral public scope would rename the package, which changes every consumer's `package.json`, every lockfile, and every `import` specifier — for no benefit. Keeping it makes the consumer migration a pure deletion of `.npmrc` and its CI step.

- `publishConfig.registry` is removed; `publishConfig.access: "public"` replaces it. A scoped package publishes as **restricted** by default, which a free org cannot do, so the explicit `access` is required rather than cosmetic.
- Consumers need no `.npmrc`, no token, and no registry configuration of any kind.

### Publish with provenance, from a GitHub-hosted runner

Every publish carries a sigstore provenance attestation (`npm publish --provenance`), minted from the release run's GitHub OIDC token. For a public package consumed by repos we invite people to fork, the attestation is the thing that ties a tarball back to the commit and workflow that built it.

This forces one deliberate exception to homelab ADR-037 (all CI on ARC runners, never GitHub-hosted): **npm rejects a provenance attestation minted on a self-hosted runner** (`422 … Only "github-hosted" runners are supported when publishing with provenance`). The `publish-npm` job therefore pins `ubuntu-latest`, while every other job in the shared `library.yml` stays on ARC. This is consistent with the rule's intent rather than an erosion of it: ADR-037 keeps *our* infrastructure off GitHub's runners, and this one job's artifact and audience are both outside the lab, so it should not ride on homelab uptime either.

### Credential: a token to bootstrap, OIDC as the target state

The publish credential is an npm granular access token, held as the `NPM_TOKEN` organization secret and passed through by `secrets: inherit`.

This is explicitly a **bootstrap**, not the end state. npm is retiring token-based publishing: as of July 2026 a bypass-2FA granular token can no longer manage tokens, maintainers, or trusted-publishing configuration, and from January 2027 it loses direct publish entirely. The target is **OIDC trusted publishing** — a short-lived credential minted per workflow run, with no standing secret to steal or rotate.

Trusted publishing cannot do a package's *first* publish (npm requires the package to exist before a trusted publisher can be configured), which is the only reason a token exists here at all. The switch is: configure a trusted publisher on each package against `PSA-Department-of-Engineering/csd-library` and the `release.yml` workflow, then delete `NPM_TOKEN`. npm validates the **calling** workflow, not the reusable one, so the shared `ci/library.yml` does not obstruct this.

## Consequences

- **Consumers drop the token entirely.** No `.npmrc`, no `setup-node-auth`, no `PACKAGES_READ_TOKEN`, no README instruction. An outside forker runs `npm ci` with nothing configured.
- **Lockfiles must be regenerated, not just edited.** Every existing `package-lock.json` pins `"resolved": "https://npm.pkg.github.com/…"` per entry; deleting `.npmrc` without rewriting the lock leaves `npm ci` still hitting GitHub Packages and still failing. The migration step is `npm i --package-lock-only`, committed.
- **A version discontinuity, and consumer ranges must move.** The first public versions are `vitest-intent` 2.0.0, `playwright-intent` 2.0.0, `starlight-theme` 1.1.0. The major bump carries no breaking API change: during the migration a force-push orphaned the freshly cut `1.0.1` tags, release-please lost its baseline for those packages, walked back past `1.0.0`, and swept up a historical breaking-change commit. Since npm forbids reusing a version number, correcting the digits would burn further versions for no gain, so the numbers stand. Consumers pinned `^1.0.0` resolve to **nothing** on npm for the two intent packages and must move to `^2.0.0`.
- **The GitHub Packages copies stay at 1.0.0.** They are superseded, not deleted; nothing resolves against them once consumers drop their `.npmrc`.
- **Python distribution is unchanged.** ADR-0001's git-tag mechanism still governs `pytest-intent` and `csd-intent`, and remains anonymous because the repository is public.
- **A failed publish cannot be retried in place.** release-please emits `paths_released` once per release; if the publish job fails after tags are cut, re-running it re-resolves nothing and the version is stranded. Recovery today is to cut the next version. A `workflow_dispatch` republish path would remove this, and is not built.

## Alternatives considered

| Option | Why not |
|---|---|
| Keep GitHub Packages, hand every forker a PAT | This is the problem, restated. It makes forkability contingent on a credential only this org can issue. |
| Move to a shorter neutral public scope | Renames the package: every consumer's `package.json`, lockfile, and import specifier changes, and the two names coexist during migration. No benefit over keeping the scope. |
| Git-tag installs for npm, mirroring the Python packages | npm's git support does not handle monorepo subdirectories cleanly (the original asymmetry ADR-0001 identified), and the packages' entrypoint is a built `dist/` that is not committed. |
| Self-hosted registry (Verdaccio) in the homelab | Rejected in ADR-0001 for uptime coupling, and it fails this ADR's actual goal outright: an outside forker cannot reach it at all. |
