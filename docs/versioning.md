# Source versions and publication

[`VERSION`](../VERSION) is the source release version. Starting with **1.4.0**,
all six active package manifests and every canonical `skills/*/SKILL.md`
`metadata.version` use that version. Hosts retain their own package formats,
connections and publication processes. Equal versions identify a source release;
they do not imply equal capabilities or marketplace availability.

The initial 1.4.0 alignment advances every manifest and skill from its previous
version. Existing tags, archives, historical packaging inputs and publication
observations remain unchanged. Archived `packaging/mcp/` and
`packaging/releases/` inputs are not active source packages.

## Making a change

Use stable `MAJOR.MINOR.PATCH` versions. Patch releases correct guidance or
packaging; minor releases add compatible capabilities; major releases remove or
break supported workflows. The CLI release consumer does not accept prerelease
tags. Review candidates stay on branches until release.

From an idle checkout:

```sh
git fetch https://github.com/coderabbitai/skills.git main
python3 .github/release.py bump 1.4.1
python3 .github/release.py check --base FETCH_HEAD
python3 -m unittest discover -s .github/tests -v
python3 .github/check_antigravity.py --base FETCH_HEAD
git diff --check
```

Choose the next version after fetching main; `1.4.1` above is an example.
`bump` updates every active manifest, skill version and `VERSION` together.
Do not hand-edit individual versions. Add a changelog entry describing the
change. Missing skill metadata, manifest drift, unknown host manifests,
downgrades and shipped content changes without a newer version fail CI.
The tracked package paths are explicit in `.github/release.py`; add new shipping
surfaces there when introducing them. Publication observations and maintainer
CI/test-only changes do not require a package bump.

Every PR that changes shipped content carries a bump. If another PR merges with
the same target version, update from main and bump again. Require branches to be
up to date before merge so two passing PRs cannot ship different content with the
same version. The policy checker runs on PRs and main; it does not replace host
validators or authenticated end-to-end QA.

## Building and releasing

From a clean, committed checkout, exercise packaging without creating a tag:

```sh
python3 .github/release.py build --snapshot --output /tmp/new-skills-release
python3 packaging/codex-connected/build.py portal /tmp/new-coderabbit-portal.zip
python3 packaging/codex-connected/build.py native /tmp/new-coderabbit-native.zip
```

Each output destination must be new. The archive retains the existing CLI
contract: `coderabbit-skills-vX.Y.Z.tar.gz`, its `.sha256` file and
`release-manifest.json`. The manifest records the source commit, package and
skill versions, artifact URL and checksum. Builds use committed source and a
fixed gzip timestamp; use CI's pinned Python version when comparing bytes.
Snapshot outputs are test artifacts, not evidence of publication.

After review and the relevant host QA, a maintainer creates a `vX.Y.Z` tag at the
intended source commit and pushes it. Tag publication is a separate action from
preparing a PR. The release workflow first runs the official Antigravity
validator and regression tests, then checks all source versions, the exact tag
and commit, and builds the assets. It refuses to overwrite a release or replace
Latest with an older/equal version. It does not upload connected Codex candidates
to marketplaces. A failed or partially created release requires inspection;
do not move an existing tag or silently replace its assets.

## Tracking what customers have

[`DISTRIBUTION_CHANNELS.md`](../DISTRIBUTION_CHANNELS.md) records publication
separately. For each observed update, record the channel, installed version or
artifact identity, date, source/ref if known, and supporting release or QA
evidence. Use “unknown” or “publication unverified” when the host has not been
checked. Never advance this record just because `bump`, CI or a build succeeds.
Published installation instructions continue to point at the last verified
release until a replacement is actually available.

Some hosts follow main: Google's weekly crawler reads the root Antigravity
manifest. Merging a versioned source change can therefore lead to distribution
without a GitHub release. Other hosts require a portal review or separate
publication. Keep those host-specific procedures and QA gates in place.

## Repository enforcement

After this workflow exists on main, configure branch protection to require
`validate versions and artifacts`, the existing Antigravity `validate` check,
and the maintainer approval check. Require up-to-date branches (or a separately
qualified merge queue). This repository change defines checks; it does not
change GitHub branch protection, portal settings or publication permissions.
