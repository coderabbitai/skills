# MCP-authorized CLI plugin packages

This branch prepares **install plugin → connect CodeRabbit once → review local
changes**. It requires the matching hosted MCP control service and a CLI build
that implements `review --agent --mcp-stdin` and `mcp-hook`. It is not a published release. Installing the
source tree directly does not supply the native CLI or hosted endpoint.

Shared `skills/code-review` and `agents/code-reviewer.md` retain the released CLI
workflow. The assembler replaces them with the MCP templates in `packaging/mcp`
and adds its setup skill only inside the complete pilot package.

Setup can also offer repository-specific review settings and path instructions
through the pinned CLI's configuration protocol v2. Configuration is optional,
uses local inspection without sign-in, and previews a validated proposal before
an approved save. A schema or validation failure leaves the file unchanged.

The release operator assembles a complete package before installation. Users do
not run this build step, install Node/Python, or perform a second CLI login.
The `bundled` variant includes native bytes for manual installation. The
`download` variant prepares a pinned native dependency during explicit setup.
The installed plugin uses that verified executable and the host's
normal execution/network permissions. Git must be available for local reviews.

Claude packages request `connection account:read usage:read pull_requests:read review`
OAuth scopes explicitly. Codex discovers OAuth and scopes from the server's
metadata; the verified endpoint must advertise those scopes, including `review`.
The shipped Codex loader rejects server-level `extensions` in portable `mcp.json`,
so do not add authentication fields there. Confirm the granted scopes in the
native browser sign-in flow before qualification. After the host approves `start_code_review`, its trusted
`PostToolUse` hook runs the pinned CLI's normal review using the returned
one-review handoff. Prefer this automatic path on supported hosts. The `direct`
package is a hook-free fallback for channels where hooks are unavailable or
unsuitable; its skill invokes the same CLI through permitted execution. Select
one launcher before starting. Neither path reads the host OAuth store. The
handoff may appear in the transcript, so it is scoped to one review and expires.
The synchronous hook's 40-minute cancellation budget covers the bounded launch,
execution and terminal-persistence windows; the old five-minute collector timeout
would terminate a longer review. Qualify the installed host's actual timeout and
output handling. See [Claude hooks](https://code.claude.com/docs/en/hooks) and
[Codex hooks](https://learn.chatgpt.com/docs/hooks).
The CLI delivers findings normally; MCP retrieves the same saved result when
output is unavailable, incomplete or needed in a later session.

## Assemble

Prepare a local JSON file with `version` and an `artifacts` array. Each entry
contains `platform` (`darwin-arm64`, `darwin-x64`, `linux-arm64`, or `linux-x64`),
`path` to the native CLI build, and its approved lowercase `sha256`. Include
all supported platforms in the distribution artifact. A single-platform package
is useful for a bounded local acceptance test, not a universal release.

For `--delivery download`, also include `archive_sha256` for each platform's
official ZIP. The assembler validates the local native artifact as before but
emits only the launcher and checksum metadata; it derives the versioned URL
under `https://cli.coderabbit.ai/releases/` (`nightly/` for nightly pins). Obtain
both hashes from approved CLI release artifacts. No mutable `latest` URL is
shipped. Public release signing/provenance is still a release-operator gate.
Set top-level `plugin_version` explicitly for this delivery mode, independently
of the CLI `version`, and increment it for each published plugin update. Hosts
cache by plugin version; changed source with the same version is not an upgrade.
The shared source manifests and standalone release version remain unchanged.

Run:

```sh
python3 scripts/assemble-plugin.py --client claude \
  --delivery download \
  --artifacts /absolute/path/to/approved-artifacts.json \
  --mcp-url "$VERIFIED_CODERABBIT_MCP_URL" \
  --output /absolute/path/to/new-plugin-package
```

For a Codex package use `--client codex` in this source directory. Hook packages
use `.codex-plugin/plugin.json` and `mcp.json`, with the review skill renamed for
Codex. Do not add a root portable `plugin.json` to a hook package: it takes
precedence, and the current native loader skips hooks for that format. Direct
packages also emit the portable root manifest with OpenAI presentation and
onboarding under `extensions.com.openai`. This remains an assembled
local-marketplace pilot, not a universal-directory submission. Claude hooks use
`CLAUDE_PLUGIN_ROOT`; Codex hooks use its native `PLUGIN_ROOT` variable.
The default `--launcher hook` includes the trusted post-tool integration. Use
`--launcher direct` for the hook-free fallback channel; it omits hook registration
and records that selection and the executable path in `cli.json`. Neither package may bypass a
host's execution or upload permissions. Both require a native CLI whose compiled
Reviewer origin matches the intended environment; the MCP URL does not override
that trust anchor. Dev2 URLs belong only in dedicated preview artifacts.
The endpoint must be the verified HTTPS MCP resource URL for the intended environment.
Both root URLs and URLs with a path are preserved exactly;
there is no default production endpoint. Do not put credentials in the URL.

The assembler verifies hashes and native executable headers, copies only plugin
components, and writes a credential-free artifact inventory. It does not download,
execute, sign, notarize, publish, or claim provenance for the input binaries.
Supply signed/notarized artifacts through the CLI release process where required.
The runtime launcher checks the shipped digest before execution; this detects
corruption, not malicious replacement of both binary and manifest.

Use **Actions → Assemble bundled MCP plugin pilot → Run workflow** to build
a single-platform test artifact. Select the client, launcher and delivery mode.
Supply the exact CLI version, platform, native executable HTTPS URL, approved
SHA-256, official ZIP SHA-256 for download delivery, and verified MCP URL. The workflow
validates inputs, verifies the downloaded artifact, and uploads a tar archive
plus checksum for three days. It does not execute the downloaded binary or
publish a release. Extract the tar archive before client installation; it
preserves executable permissions. Run once per platform for separate pilots.

Tagged releases continue to distribute the shared standalone CLI skills. The
presence of the pilot assembler does not change those skills or block their
release; the MCP overlay exists only in the assembler's output. A tagged source
archive is not an assembled MCP plugin. This pilot uses local marketplace installation for its assembled
Codex package. Bundled hooks require the host's trust approval and packaged
scripts; qualify each intended distribution channel separately. See the
[Codex bundled-hook guidance](https://developers.openai.com/plugins/build/plugins#bundled-hooks).
Publish the assembled plugin only after its archive/import behavior is verified. In particular, a source-repository marketplace install must deliver
these assembled files; pointing it at this source branch is insufficient.

## Install a Codex pilot locally

Assemble with `--client codex` first, or extract a complete Codex package. Put
that assembled folder in a local marketplace using the
[official OpenAI marketplace format](https://developers.openai.com/plugins/build/plugins).
Use a new marketplace folder so the copy does not nest inside an old package.

If `coderabbit-local-pilot` is already registered from a different folder, remove
only that pilot registration with
`codex plugin marketplace remove coderabbit-local-pilot` before adding the new
folder. Alternatively, update the package in its existing marketplace folder.
Keep the published marketplace and unrelated registrations.

```sh
package="/absolute/path/to/new-plugin-package"
marketplace="/absolute/path/to/new-local-marketplace"
mkdir -p "$marketplace/.agents/plugins" "$marketplace/plugins"
cp -R "$package" "$marketplace/plugins/coderabbit"
cat > "$marketplace/.agents/plugins/marketplace.json" <<'JSON'
{
  "name": "coderabbit-local-pilot",
  "interface": {"displayName": "CodeRabbit local pilot"},
  "plugins": [{
    "name": "coderabbit",
    "source": {"source": "local", "path": "./plugins/coderabbit"},
    "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
    "category": "Developer Tools"
  }]
}
JSON
codex plugin marketplace add "$marketplace"
```

Restart the desktop app. In its Plugins Directory, select **CodeRabbit local
pilot** and install `coderabbit`. A CLI with `plugin add` can instead run
`codex plugin add coderabbit@coderabbit-local-pilot`. Start a fresh session in
the intended Git repository, run CodeRabbit setup, and review/trust any hook
through native controls. Installation alone does not grant hook trust. Keep one
CodeRabbit plugin enabled while testing; preserve the published listing and
matching MCP connections. This registers a manual pilot, not a public release.

## Public directory submission

The native bundle is a manual-channel pilot. It is not a Claude directory
submission artifact: the [current directory checklist](https://claude.com/docs/plugins/pre-submission-checklist)
requires every plugin file to be under 5 MiB, while native CLI executables exceed
that limit. The local Claude validator checks only a subset of directory rules;
even `--strict --profile directory` passing does not establish portal acceptance.
The `download` variant addresses this packaging limit by shipping readable
scripts and pin metadata, with no compiled files or `bin/` directory. Explicit
setup downloads to a versioned user cache outside the plugin, verifies both
hashes, and checks the version. Hooks never download. Read
[runtime preparation](mcp/skills/setup/references/runtime-install.md) for storage
and permission behavior. This does not establish portal acceptance, all-platform
runtime qualification, or approval to publish an unqualified CLI build. Do not
present connector registration alone as a working local review.

Keep the existing `coderabbit` plugin name and update the existing listing.
[Delisting](https://claude.com/docs/plugins/submit#withdraw-or-delist-a-plugin)
stops updates and may remove existing users' copies. The official Claude Code
marketplace and Claude's directory are separate channels: an official-marketplace
entry pinned to a Git SHA needs its catalog reference updated; a directory
submission follows its configured branch or tag after review and publication.
Neither changes merely because this repository merges.

Submit the hosted server separately as an [MCP connector](https://claude.com/docs/connectors/building/submission),
even when a plugin references it. Preserve the same endpoint when pairing the two
from the same publisher organization. Account and PR tools can run remotely;
local code collection still requires a compatible CLI in an execution-capable
host. Chat-only surfaces must not promise local file access.

Claude's [manifest reference](https://code.claude.com/docs/en/plugins/manifest-reference#standard-layout)
also says packages with a `bin/` directory are not installed in Claude Chat or
Cowork. Qualify local execution separately from remote account/PR access.
Download packages keep the runtime outside the versioned plugin root, using the
same user cache for both hosts and for setup/hook execution. Their launcher can
also accept an explicit persistent `--data-dir`, but setup and the registered
hook must use the same location. Host plugin-data variables are not exported to
Claude's Bash tool, so an implicit switch between cache and hook environment
would prepare one directory and launch from another; this package avoids that.

For Codex, use its [current packaging requirements](https://developers.openai.com/plugins/build/plugins)
and qualify the actual target loader. OpenAI's public directory does not accept
plugins containing lifecycle hooks; hook packages are for manual desktop installs.
The `direct` package omits hooks, but directory acceptance and permitted local
execution still require qualification on the intended surface. The compatibility manifest workaround in
this pilot records tested client behavior; it is not a permanent claim that
portable manifests cannot load hooks. Hook trust remains a native user decision.

## Validate

```sh
python3 scripts/test-plugin-package.py
```

To also check connector, skill and hook discovery through an installed Codex
binary, run the same suite with `CODEX_TEST_BIN=/absolute/path/to/codex`.
This reads both package variants through the native loader using temporary
profiles; it does not install plugins, grant trust, authenticate or start reviews.

The tests use synthetic native headers for assembly and a shell test double for
launcher forwarding. They do not establish real CLI execution or authentication.
Before publication, unpack the real artifact under a path with spaces and verify:

- A clean machine with no global CodeRabbit CLI can run bundled `--version`.
- The installed artifact digest matches the approved CLI build.
- Both clients discover the packaged MCP connection and setup skill.
- Hook packages load the post-hook through the host's installation and trust flow;
  direct packages contain no hook and run only through permitted execution.
- One host browser sign-in connects CodeRabbit; no CLI login is requested.
- A fixture review uses the selected launcher once after an approved start and
  preserves requested base, scope and files; a denied start performs no upload.
- Complete CLI output and MCP retrieval have identical canonical findings and
  totals. Hidden hook output, a killed CLI and truncated output retrieve the
  original review instead of starting a second one.
- Failed/revoked authentication, missing permissions, upload uncertainty, and
  paid continuation do not silently start another review or change scope.
- The shipped platform matrix, code signature, executable permissions, package
  size limits, and client installation behavior pass on each supported target.
