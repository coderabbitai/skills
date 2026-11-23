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

Antigravity, Claude and Codex show local CLI findings directly in chat.
To enable cards with the [latest stable CLI](https://cli.coderabbit.ai/releases/latest/VERSION)
on a local host, ask “Set up inline CodeRabbit review cards.” The shared setup
skill uses the native host's MCP settings to register a compatible installed
CLI as a local stdio server. When that connection confirms Apps support, the
agent can request a receipt during the review and present the exact ID locally
after completion. Selected fixes continue in the local checkout. Missing
support or receipt leaves the findings in chat. The hosted connector receives
neither CLI findings nor the card ID. Hosted-only clients continue using their
existing account tools. See [local presenter setup](../skills/coderabbit-setup/references/local-review-card.md).

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

## CodeRabbit Secure

With the source plugin, ask “Which open Deep Scan findings in owner/repo
should we fix first?” Claude's source manifest requests repository discovery,
Security reads and Security writes. It also requests `automations:write` for
schedule changes and `knowledge:write` for editing or deleting Security
learnings. These are shared product permissions. Reconnect through the host
if an older grant lacks the scope returned by the tool. The account also needs access to
the selected repository. Google uses native scope discovery.

In Codex, the source plugin and the portable skill both use your configured
CodeRabbit MCP connection. With
no server configured, add the hosted endpoint for your organization's region
and sign in using the name you configured. For example, for a US organization:

```sh
codex mcp add coderabbit --url https://mcp.coderabbit.ai/
codex mcp login coderabbit --scopes connection,account:read,repositories:read,security:read
```

The EU endpoint is `https://mcp.eu.coderabbit.ai/`. Start a new session after
connecting. The example grants read access for triage, quotes and ticket
previews. To request fixes or start scans, include `security:write` in the
login scopes alongside the reads you need. Editing a scan schedule also needs
`automations:write`; editing or deleting an existing Security learning needs
`knowledge:write`. Preserve scopes used by other workflows when reconnecting.
Use the permissions your host and account support. The remote server supplies
scan data; checking a deployment or logs uses the host's separately authorized
access to that evidence. If sign-in succeeds and Security tools are absent,
check the server's tool allowlist in the host. A configuration limited to
PR review tools can hide `list_security_findings` even after Security consent.

## Optional product feedback

When the connected server exposes `submit_feedback`, your agent can voluntarily
report bugs, suggestions, or useful experiences with any CodeRabbit product.
You can also ask it to send your feedback. Only a concise `message` is required;
optional fields identify the product, category, tool, an existing request ID,
and whether the feedback comes from the agent or you.

Submission requires `feedback:write`. Claude 1.3.6 source requests this scope;
hosts using native scope discovery can request the server's `write` group.
Existing connections keep their original permissions until you reconnect.
For a connection with an explicit scope list, preserve its current scopes and
add `feedback:write` when you choose to enable feedback. The server must advertise
the scope first; publish this source update after that backend deployment.
Agents should skip unsolicited feedback when the tool or permission is unavailable.

Feedback is stored in CodeRabbit's PostHog project for product investigation.
It includes the submitted text, connected user and organization, region, and
normalized agent attribution. Do not include secrets, private source code, or
conversation transcripts. `received` and `feedback_id` confirm ingestion
acceptance, not that someone read the report or a fix is promised. A failed or
interrupted submission is not confirmed; avoid repeatedly resubmitting it.

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
do not apply to the repository-root plugin and require their own qualification.
