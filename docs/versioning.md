# Versioning harness

The harness is installed before the version migration. **Shared versioning is
not activated:** there is no root `VERSION` file, no source version is changed,
and the existing tagged release workflow and marketplace processes continue.
Different current versions are expected and do not fail CI.

## Checks available now

```sh
python3 .github/release.py check
python3 -m unittest discover -s .github/tests -v
```

`check` reports the versions of six active package manifests and every canonical
skill. It requires stable `MAJOR.MINOR.PATCH` values, the existing package identity,
matching skill names and directories, and skill `metadata.version`. New host
manifests must be added to the inventory explicitly. It does not require parity
or introduce new bump requirements while packages are independently versioned.
The existing Antigravity version guard remains in force.

The `Package versions` workflow runs these checks and regression tests on PRs
and main, and builds both connected Codex ZIP profiles. The existing
`.github/workflows/release.yml` still owns tagged archive publication. Its
behavior is unchanged by installing this harness.

Historical `packaging/mcp/` and `packaging/releases/` inputs are not active
packages. Publication observations stay in `DISTRIBUTION_CHANNELS.md`; current
published versions are not inferred from source manifests or successful builds.

## Later: explicitly activate one shared source version

Choose the migration timing and target version in a separate reviewed change.
There is no predetermined 1.4.0 release. When ready, fetch current main and choose
a stable version greater than every active source package and skill version:

```sh
git fetch https://github.com/coderabbitai/skills.git main
python3 .github/release.py bump X.Y.Z --activate-shared
python3 .github/release.py check --base FETCH_HEAD
python3 -m unittest discover -s .github/tests -v
python3 .github/check_antigravity.py --base FETCH_HEAD
```

Replace `X.Y.Z` with the agreed version. The activation flag is required when
`VERSION` is absent, so an ordinary bump cannot silently migrate the repository.
Activation creates `VERSION` and synchronizes all active manifests and canonical
skill versions. From then on, `check` enforces parity, rejects downgrades and
requires a newer version when shipped content changes against the supplied base.
Deleting `VERSION` cannot disable an activated policy against that base.

Subsequent changes use `python3 .github/release.py bump X.Y.Z` without the
activation flag. If competing PRs choose the same version, the later PR must
update from main and choose a newer version. Require up-to-date branches when
making this check mandatory.

## Prepared archive tooling, inactive until migration

The harness includes an archive builder with regression coverage, but it refuses
to run on the current independently versioned source. After activation, CI also
builds a snapshot from the committed checkout:

```sh
python3 .github/release.py build --snapshot --output /tmp/new-skills-release
```

It preserves the CLI artifact names, checksum format and skill metadata, and
records the source commit and version inventory. Tag builds additionally require
an exact `vX.Y.Z` match at HEAD. These local builds do not publish anything.
Wiring this builder into tagged release publication, selecting release ordering
and overwrite protections, and qualifying host updates belong to the later
migration change. Merely adding `VERSION` does not replace the existing release
workflow.

## Enforcement and publication

After this harness has run in GitHub, its `validate versions and artifacts`
check can be made required alongside existing checks. This change does not
modify repository settings.

Continue existing host-specific validation and authenticated QA. In particular,
Google's crawler reads main, so a future source version bump can lead to an
Antigravity update without a GitHub release. Matching future source versions
will identify a shared source release, not establish equal capabilities or
marketplace availability.
