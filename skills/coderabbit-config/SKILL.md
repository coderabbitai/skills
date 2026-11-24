---
name: coderabbit-config
description: Create, update, or validate CodeRabbit repository configuration through the official CLI. Use for .coderabbit.yaml or .coderabbit.yml setup, review-style changes, path guidance, and configuration validation requests.
metadata:
  version: "0.2.0"
---

# CodeRabbit Configuration

Requires config protocol v2, a Git working tree, and network access to the
current configuration schema.

Keep configuration generation, schema validation, previews, and repository writes
in the CLI. Do not edit repository YAML yourself, copy a schema, or implement a
fallback editor. Configuration is local; it does not need CodeRabbit login or
start a review.

## Find the CLI and requested repository

Use the intended Git working tree for every invocation. Select the installed
workflow before looking for a standalone CLI:

- Packages without a managed runtime use the standalone CLI discovery below.
  A remote MCP connection does not provide a managed local runtime.
- For another installed package that explicitly declares a managed runtime,
  use its verified launcher and preparation instructions.
- For standalone installs, resolve an official installed `coderabbit` to a
  quoted canonical absolute path, checking PATH and the documented installer
  location `~/.local/bin/coderabbit` on macOS/Linux. Reject repository-local
  executables, aliases, and unknown wrappers. If the installation source is
  uncertain, ask the user to identify their installation. A source checkout's
  `cli.json` alone does not select a managed runtime.

The `<cli>` examples below mean that verified executable, not a literal command.

Check `<cli> --version`, `<cli> config --help`, and support for the needed
subcommands. Missing commands or an unsupported
protocol require an upgrade. For a standalone CLI, follow the
[official installation instructions](https://docs.coderabbit.ai/cli) for its
actual installation method (for example, `brew upgrade coderabbit` for Homebrew).
For a managed runtime, update the plugin to a version with a compatible pinned
CLI and follow its preparation instructions; never run `<cli> update` on the
managed launcher. Do not install or upgrade without authorization. Preserve
permission and network errors as such; they do not prove an upgrade is needed.
After any upgrade, repeat trusted executable discovery and verification, then
recheck version and command support. Do not reuse the old canonical path: an
upgrade can replace a versioned installation directory or managed launcher.

## Select the settings schema

Agent protocol 2 is the JSON response format for both V2 and V3 settings.
For a new repository config or YAML with a numeric top-level `version: 3`,
expect the CLI's `schema` field to be
`https://www.coderabbit.ai/integrations/schema.v3.json`. A V3-capable CLI
generates new configs in V3 by default. Existing unversioned YAML keeps its
V2 schema and layout during ordinary edits. The YAML editor comment alone
does not select the settings version.

If the CLI reports the V2 schema for a new config or a V3 document, report
that this installation lacks the expected V3 workflow. Stop before proposing
a change or interpreting V2 validation errors as defects in V3 YAML.

## Check the hosted environment

Before generating or recommending a new V3 repository configuration for hosted
reviews, establish that the repository uses GitHub Cloud on CodeRabbit Cloud.
Use known session context or ask for the hosting environment when it is missing.
Each such repository can opt in with numeric `version: 3`. Central configuration
files, other Git hosting platforms, and self-hosted CodeRabbit continue to use
V2. The web app has separate enrollment for its V3 editor. Follow the current
[migration guide](https://docs.coderabbit.ai/guides/migrate-configuration-v3).

Local CLI capability and schema validation establish file compatibility.
Hosted support also depends on the environment above. If the environment is
unknown or requires V2, explain that constraint before generating V3. Continue
an existing V2 configuration through the CLI, or use a documented V2 creation
workflow if the installed CLI provides one. If it only creates V3, report that
capability gap. Read-only validation of an explicitly selected file can proceed
without establishing hosted support.

## Validate only

Run `<cli> config validate --agent` for the repository configuration, or
`<cli> config validate <file> --agent` for the user's explicitly selected YAML
file. Check the returned `schema` against that file's settings version, even
when it differs from the repository's active config. Require exit zero,
`ok: true`, and `operation: validate` for success. Report a schema fetch
failure separately from YAML validation errors. This validates the YAML file;
directory documents and hosted review activation are outside that check.
Do not generate or apply changes for a validation-only request.

## Create or change review style

1. Run `<cli> config --agent`. Require exit zero, `ok: true`,
   `protocolVersion: 2`, `operation: inspect`, and `writable: true`. Preserve
   the returned repository root, target, `schema`, and `baseHash` (`none` for a
   new file). Check the settings schema and, for new V3 hosted configuration,
   the hosting environment before generating.
   Respect authority warnings, including TypeScript, remote configuration,
   symlinks, and multiple YAML files; do not delete or bypass them.
2. Run `<cli> config --agent --generate`. For a requested style, add
   `--profile chill` (Balanced), `--profile quiet` (Focused),
   `--profile assertive` (Thorough), or `--profile default` (remove the local
   style override). Without a profile, the CLI generates its baseline for a new
   file and preserves an existing file. Do not infer a style change from a
   general request to check configuration.
3. Require a successful protocol-v2 `operation: generate` response with the
   inspected target, schema, and base hash. Copy its exact `after` string into a temporary
   proposal file outside the repository; do not rewrite or extend that YAML.
4. Preview with `<cli> config apply <proposal> --agent --dry-run --base <baseHash>`.
   Require exit zero and a successful protocol-v2 `operation: apply` result.
   If unchanged, re-inspect the same base hash and report that no save is needed.
   Otherwise show the returned before/after diff and obtain approval for it.
5. Save the same proposal with
   `<cli> config apply <proposal> --agent --yes --base <baseHash>`.
   Require a successful protocol-v2 result with `applied: true`. Re-inspect and
   verify the target and saved hash against the approved `proposedHash`, then
   report the local change. Remove your temporary proposal; preserve any
   CLI-reported recovery file.

On changed input, inspect and preview again instead of bypassing the base hash.
On schema, validation, permission, or network errors, report the diagnostic and
stop without an alternate writer. An interrupted save has an unknown outcome:
inspect the file before retrying or reporting success.

## Guided path settings

Inspect the repository with `<cli> config --agent` first. For existing V2 YAML,
run `<cli> config --detailed` in an interactive terminal to edit path guidance.
For V3, path instructions are Markdown files under `.coderabbit/instructions/`
and custom checks live under `.coderabbit/pre-merge-checks/`. The CLI wizard
can edit review style but cannot author those documents. For a request limited
to V3 instructions or checks, explain the relevant location and CLI limitation
without starting the wizard or proposing a review-style change.
For general interactive setup, check the hosting environment before creating
a new V3 configuration, then use `<cli> config` or `<cli> config --generate`.
Relay the CLI's actual prompts and preview, using settled user preferences and
asking for missing choices. Confirm the displayed changes only after approval.
If the host cannot interact with a terminal, give the user the exact command to
run in the selected repository and resume after they finish. Do not simulate the
wizard with piped answers. For settings the installed CLI cannot edit, explain
the capability gap instead of inventing flags or editing YAML yourself.

After a successful save, validate and inspect the resulting configuration.
Saving locally does not activate settings on hosted PR reviews. Commit, push,
dashboard changes, and running a review require their own user-requested scope.
