# Connect CodeRabbit through MCP

CodeRabbit's hosted MCP connection lets your assistant read account information,
usage, accessible repositories and pull requests, and saved review results.
Available tools depend on your account, permissions and the current rollout.

The repository root on `main` contains the complete Claude MCP 1.4.0 candidate:
its connection and hook are declared in `.claude-plugin/plugin.json`, and runtime
pins are checked in under `runtime/`. No generated distribution branch or local
assembly is needed for that native Claude package. Source availability does not
publish the candidate: confirm the current directory or marketplace version
before installation. Codex and other standalone integrations remain separate.

## Connect your account

1. In your host's connector settings, add CodeRabbit with the server URL supplied
   with your preview package, or use **Connect** for the server included in your
   MCP-enabled plugin. In Claude Code, use `/mcp` to inspect that connection and
   follow its authentication action. In Codex, use the plugin's native connection
   controls.
2. Complete browser sign-in and consent for the organization you intend to use.
   Do not paste an authorization code or token into a conversation.
3. Ask: **“Which CodeRabbit account, organization and region am I connected to?”**
   Verify the returned identity. A successful browser page alone does not prove
   which organization the connection uses.
4. Ask for usage, an accessible repository or pull-request information. The
   connection does not grant access beyond your account's permissions. A listed
   organization membership does not switch the active organization.

Keep an existing connection when setup verifies that its endpoint, tool name,
account and review permission match the installed package. If another connection
hides the plugin server, let setup identify the conflict before changing native
settings. Preserve unrelated connections; another login is not always necessary.

## Prepare local review

For the native Claude plugin, run `/coderabbit:setup` or ask to set up CodeRabbit.
This command reads the packaged setup guide, prepares the pinned runtime and
connects the plugin-owned MCP server. The connection and review hook live in the
Claude manifest; a manual MCP connection does not substitute for plugin ownership.

A remote connector alone cannot collect files from your laptop. Local review
requires an MCP-enabled plugin in a host that can run its CLI and access the
intended Git working tree. The current local launcher supports macOS and Linux;
check the supplied package's platform list. Chat-only hosts can still use the
available remote tools.

In your intended repository, ask:

> Set up CodeRabbit. Prepare its pinned CLI and verify my account, organization
> and review access. Do not start a review, upload code or write configuration.

For a download package, explicit setup downloads the version-pinned runtime from
CodeRabbit's CLI CDN, verifies its archive and executable hashes, and reuses a
verified cache. It needs curl, unzip, a SHA-256 utility and network access; review
also needs Git. This dependency does not replace your global CLI or change its
login and update settings. MCP reviews use the browser connection without a
separate CLI login.

Setup follows the launcher already selected in your package; it does not ask
you to choose one. For the hook-based v1, review and trust the CodeRabbit hook in the
host's native controls. Folder trust, execution, network and upload permissions
still apply. A host without permitted local execution cannot start a local
review. Codex hook packages are unavailable because the current bare tool name
does not establish plugin server identity. Existing standalone Codex installs
remain supported. OpenAI's public directory also excludes lifecycle hooks.
See [OpenAI's plugin packaging guidance](https://developers.openai.com/plugins/build/plugins).

An unavailable hook requires setup or a compatible host. The assistant does not
replace it with a shell command. Separately assembled hook-free packages require
permitted direct execution with authorization supplied through separate stdin;
their existence does not establish support in every host or directory approval.

Repository configuration is optional. Ask setup to suggest review settings and
path instructions if useful. It inspects local context and shows validated
changes before an approved save. You can keep existing settings and begin
reviewing without changing configuration. If schema loading fails, setup should
report the concrete error; the package includes a bounded troubleshooting
reference for the qualified macOS timeout.

## Review and retrieve results

After checking the organization and selected changes, ask:

> Review my uncommitted changes with CodeRabbit. Review only; do not edit files.

Specify a different directory or scope explicitly when needed. An approved MCP
start reserves one review; its selected local launcher collects the requested
changes and sends them to CodeRabbit for analysis. Reviews can consume plan usage
or credits. Keep secrets and credentials out of the selected changes.

Record the returned review ID. In a later session, or if output is missing, ask:

> Retrieve CodeRabbit MCP review REVIEW_ID. Do not start or rerun a review.

The assistant should read all returned pages for that same ID. A pending,
failed, skipped or unavailable result is not evidence that the code was analyzed
and found clean. Do not start another review to recover uncertain output or
silently switch launchers after a failure.

If the runtime is missing or fails integrity checks, return to setup or
reinstall the complete package as directed. A review hook does not download a
replacement or use your global CLI as a fallback. If authentication expires,
use the host's native Authenticate or Reconnect action and verify identity again.

## Keep using your existing CLI

The MCP-enabled package also preserves the original standalone workflow. Ask:

> Review my uncommitted changes with my existing CodeRabbit CLI only. Use its
> current sign-in. Do not connect MCP or reserve an MCP review. Review only;
> do not edit files.

This explicit choice follows the ordinary CLI guide before MCP setup or review
reservation. It uses your existing CLI, authentication and current organization,
and checks any requested account, organization or region. It does not prepare
the pinned MCP runtime. An older CLI may lack newer options; confirm support and
preserve the requested scope rather than silently changing it. See the
[standalone CLI guide](https://docs.coderabbit.ai/cli) for installation and native
authentication.

CLI-only reviews can also consume usage or credits. Their output is a separate
workflow; the MCP saved-review recovery command above applies to MCP reviews.
An MCP denial, failed launch or uncertain result does not authorize an automatic
CLI-only retry.

## Data and support

Account and PR tools return information from CodeRabbit within your permissions.
Runtime preparation sends artifact requests to CodeRabbit's CLI CDN. Approved
local reviews transmit selected source and repository context to CodeRabbit's
review service. MCP returns account data and saved findings to the host; the
host may retain tool output and the short-lived review handoff in its transcript.
The plugin does not inspect the host's OAuth store. Service retention and data
handling depend on the applicable policy and account settings.

See the [CodeRabbit Privacy Notice](https://www.coderabbit.ai/privacy-policy).
For help, contact [CodeRabbit support](mailto:support@coderabbit.ai) with the
client/package versions, concrete error and review ID when available. Do not
send credentials, authorization codes or review handoff tokens.

## Hook and credential handling

`.claude-plugin/plugin.json` declares:

- an HTTP MCP connection to `https://mcp.coderabbit.ai/` with least-privilege
  OAuth scopes `connection account:read usage:read pull_requests:read review`;
- one `PostToolUse` hook whose matcher is only this plugin's
  `start_code_review` tool. It runs the readable launcher
  `scripts/coderabbit-runtime mcp-hook`.

It declares no `env`, `headers`, `headersHelper`, client secret,
credential-file path or credential environment-variable substitution.

Claude owns the OAuth sign-in and token; the plugin never reads Claude's OAuth
store. After the user approves `start_code_review`, the server returns a review
ID and a short-lived, single-review handoff. The hook passes that tool result
on stdin to the pinned CodeRabbit CLI, which uses it once to upload the
selected changes to CodeRabbit's review service. The handoff is never written
to files, flags or environment variables, and it goes only to CodeRabbit.

The launcher runs only a CLI whose archive and executable SHA-256 match the
pins in `runtime/`. Explicit setup downloads it from CodeRabbit's CLI CDN; the
hook never downloads, and it never falls back to a global CLI.
