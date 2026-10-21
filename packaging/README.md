# Bundled CLI pilot package

This branch prepares **install plugin → connect CodeRabbit once → review local
changes**. It requires the matching hosted MCP upload service and a CLI build
that implements `mcp-upload`. It is not a published release. Installing the
source tree directly does not supply the native CLI or hosted endpoint.

The release operator assembles a complete package before installation. Users do
not run this build step, install Node/Python, download a CLI, or perform a second
CLI login. The installed plugin uses its own native executable and the host's
normal execution/network permissions. Git must be available for local reviews.

## Assemble

Prepare a local JSON file with `version` and an `artifacts` array. Each entry
contains `platform` (`darwin-arm64`, `darwin-x64`, `linux-arm64`, or `linux-x64`),
`path` to the native CLI build, and its approved lowercase `sha256`. Include
all supported platforms in the distribution artifact. A single-platform package
is useful for a bounded local acceptance test, not a universal release.

Run:

```sh
python3 scripts/assemble-plugin.py --client claude \
  --artifacts /absolute/path/to/approved-artifacts.json \
  --mcp-url "$VERIFIED_CODERABBIT_MCP_URL" \
  --output /absolute/path/to/new-plugin-package
```

For a Codex package use `--client codex` in the Codex plugin source directory.
The endpoint must be the verified HTTPS `/mcp` URL for the intended environment;
there is no default production endpoint. Do not put credentials in the URL.

The assembler verifies hashes and native executable headers, copies only plugin
components, and writes a credential-free artifact inventory. It does not download,
execute, sign, notarize, publish, or claim provenance for the input binaries.
Supply signed/notarized artifacts through the CLI release process where required.
The runtime launcher checks the shipped digest before execution; this detects
corruption, not malicious replacement of both binary and manifest.

The existing source-only release archive is unchanged. Publish the assembled
plugin package only after the distribution channel's archive/import behavior is
verified. In particular, a source-repository marketplace install must deliver
these assembled files; pointing it at this source branch is insufficient.

## Validate

```sh
python3 scripts/test-plugin-package.py
```

The tests use synthetic native headers for assembly and a shell test double for
launcher forwarding. They do not establish real CLI execution or authentication.
Before publication, unpack the real artifact under a path with spaces and verify:

- A clean machine with no global CodeRabbit CLI can run bundled `--version`.
- The installed artifact digest matches the approved CLI build.
- Both clients discover the packaged MCP connection and setup skill.
- One host browser sign-in connects CodeRabbit; no CLI login is requested.
- A fixture review uploads once and preserves requested base, scope, and files.
- Failed/revoked authentication, missing permissions, upload uncertainty, and
  paid continuation do not silently start another review or change scope.
- The shipped platform matrix, code signature, executable permissions, package
  size limits, and client installation behavior pass on each supported target.
