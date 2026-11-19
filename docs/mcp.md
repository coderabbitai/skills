# Connect CodeRabbit through MCP

The Claude plugin combines CodeRabbit's remote MCP connection
with standalone CLI local reviews. It declares no automatic hooks. Source on
`main` and directory publication are separate; see
[distribution status](../DISTRIBUTION_CHANNELS.md).

For the Antigravity plugin, use the
[Google-specific setup guide](../.antigravity-plugin/README.md). Its connection
is declared in `mcp_config.json` and uses Antigravity's native OAuth discovery.

## Set up

Run `/coderabbit:setup` in the installed Claude plugin.

1. Connect CodeRabbit through Claude's native browser sign-in and select your
   organization. In Claude Code, use `/mcp` to inspect the connection.
2. For local reviews, install the official [CodeRabbit CLI](https://docs.coderabbit.ai/cli)
   and sign in through its own browser flow. An existing authenticated CLI can
   be reused. MCP and CLI sign-ins are separate.
3. Ask “Review my uncommitted changes. Review only; do not edit.” Local reviews
   use the standalone CLI and the host's normal execution permissions.

A remote MCP connection cannot read files on your laptop. Local review requires
an initialized Git working tree available to the host, permission to run the
CLI and network access to CodeRabbit. If those are unavailable, remote tools
can still be used but local review cannot run.

## Remote tools and local reviews

In Antigravity, Claude and Codex, a connected CodeRabbit MCP server can
present a finished CLI review inline. Ask to review local changes or to show a
GitHub PR's readiness. When the host has MCP Apps enabled, it can render the
review findings or PR status as a card. With Apps disabled, the same workflows
return text in chat. The skills-only Codex package uses local CLI results
unless a CodeRabbit connection is configured separately.

For a GitHub PR, native Autofix uses `get_pull_request`, `get_code_autofix` and
`set_code_autofix` to repair review findings, failing checks and merge conflicts.
Its state persists on the backend. A request to start Autofix can push commits
to that PR; it does not authorize merging. Showing status alone does not start it.

Version 1.4.0 requests repository discovery and `code:read` / `code:write` in
addition to the existing account, usage, PR and review scopes. Install the updated
package before renewing an old connection's consent. Renew only after an actual
missing-scope error or the host's consent prompt; do not copy credentials or
replace the separately authenticated CLI session. Organization entitlement and
repository authorization still apply. A successful connection does not prove
native card rendering or Autofix completion.

The declared remote connection provides tools within the granted scopes and
your account's permissions. Use it for account, usage and accessible pull-request
workflows. Product and tool availability depends on the plan and permissions;
connecting does not grant access to every CodeRabbit product.

Local reviews do not call MCP `start_code_review`, reserve an MCP review, or use
a review handoff. They use the CLI's authentication, review output and saved
results. To retrieve local findings or fix prompts without rerunning, follow
[the CLI workflow guide](../skills/code-review/references/cli-workflows.md).

An existing MCP review may still be recovered through `get_code_review` using
its original review ID and all result pages. Do not start a standalone CLI
review to recover an uncertain MCP review. Do not assume a standalone CLI review
is available through MCP recovery.

## Data and support

Local review sends the selected code changes and required repository context to
CodeRabbit through the CLI. Remote MCP tools exchange their requested data with
CodeRabbit through Claude. The host manages connector OAuth; the standalone CLI
manages its own credentials. The plugin does not copy credentials between them.
Setup alone does not upload code or start a review.

See the [CodeRabbit Privacy Notice](https://www.coderabbit.ai/privacy-policy).
Contact [CodeRabbit support](mailto:support@coderabbit.ai) with versions, the
concrete error and review ID when available; never send credentials.

## OAuth credential handling

The Claude manifest `.claude-plugin/plugin.json` declares an HTTP MCP connection to
`https://mcp.coderabbit.ai/` and the requested OAuth scopes. It declares no
`env`, `headers`, `headersHelper`, client secret, credential-file path or
credential environment-variable substitution. It declares no hook or local
MCP server command.

Claude manages the connector's browser OAuth flow and uses the resulting
CodeRabbit access token to authenticate MCP requests. “No custom authorization
header” does not mean unauthenticated requests: the host supplies OAuth
authentication through its native MCP client. The plugin does not configure
forwarding of a pre-existing Git-provider token or another service's API key.
The standalone CLI uses its separate sign-in; this manifest does not transfer
its credentials into the MCP connection.

See Claude's [remote MCP authentication documentation](https://code.claude.com/docs/en/mcp#authenticate-with-remote-mcp-servers).
If a directory check reports credential forwarding against this manifest,
request the exact field and data path identified by the check. This description
explains the configuration; it does not establish a policy waiver or a passed
directory scan.

## Other packages

The independently assembled MCP hook/direct packages under `packaging/` are
separate development candidates. Their runtime and authentication instructions
do not apply to the repository-root 1.4.0 plugin and require their own qualification.

The OpenAI MCP candidate is built from `packaging/openai/` and the shared skills:
`python3 scripts/package-openai.py --output /tmp/coderabbit-mcp-1.4.0.zip`.
The builder uses an explicit file allowlist. It is separate from the existing
skills-only `.codex-plugin` listing; that listing does not gain an MCP connection
just because it contains these instructions. Validate and test the actual
installed artifact before submitting it to a directory. This PR does not publish
either candidate or change existing users' grants.

For local Codex installations that cannot read the portable OAuth declaration,
build the connected native package with
`python3 scripts/package-openai.py --codex-native --output /tmp/coderabbit-mcp-native-1.4.0.zip`.
This format uses Codex's native MCP declaration with the same server URL
and requested scopes. Both ZIPs contain the same four shared skills.
