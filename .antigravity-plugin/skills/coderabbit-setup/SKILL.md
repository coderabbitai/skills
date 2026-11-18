---
name: coderabbit-setup
description: Connect CodeRabbit MCP in Antigravity and check readiness for local CLI reviews. Use when setting up CodeRabbit, reconnecting its remote tools, or diagnosing separate MCP and CLI sign-ins.
---

# Set up CodeRabbit in Antigravity

Report remote connection and local review readiness separately. Setup alone
does not authorize a review or source upload.

## Connect remote tools

Use Antigravity's native sign-in for this plugin's `coderabbit_coderabbit`
server at `https://mcp.coderabbit.ai/`. In the App, open the installed CodeRabbit
plugin's Accounts tab, or Customizations > Installed > MCP Servers;
in the CLI, inspect `/mcp` or choose Sign in on the
installed CodeRabbit plugin in `/plugin`.

Let the user complete consent and select the intended organization. If the
host requests an authorization code, the user enters it directly into the
host's authentication dialog, never into chat. Do not read credential stores
or copy tokens between the host and CLI. Preserve other connections.

If submitting the code fails with `invalid_grant` or “Invalid authorization
code,” use the native Restart sign-in action and let the user complete a fresh
flow. Do not resubmit the rejected code or infer its cause from that message
alone. If the fresh flow also fails, report the error and stop retrying.

Verify the selected account and organization using `connection_status` or
`get_me` when available. A browser success page alone does not establish tool
discovery or access. If tools are absent, report the observed connection error
and use the host's reconnect flow. Do not promise capabilities beyond the
granted scopes, organization, plan and permissions.

## Prepare local reviews

Local reviews require a Git working tree, the official CodeRabbit CLI, its own
sign-in, and host execution/network permission. Locate the installed
`code-review` skill and follow its `references/auth-recovery.md` for trusted
CLI discovery and authentication checks. That reference also routes to
Antigravity sandbox recovery when an installed executable is inaccessible.
Hand off missing CLI installation or login to the user through the official
[CLI instructions](https://docs.coderabbit.ai/cli).

MCP sign-in does not authenticate the CLI. Do not call `start_code_review`,
reserve a review, install a hook, or pass an MCP handoff into shell commands.
If local execution is unavailable, explain that remote tools remain usable.
Configuration uses the installed `coderabbit-config` skill and needs no login.

If the user already requested a review, continue with the installed
`code-review` skill and preserve their scope. Otherwise summarize what is
ready and suggest “Review my uncommitted changes. Review only; do not edit.”
