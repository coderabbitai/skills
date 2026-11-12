---
description: Connect CodeRabbit MCP for remote tools and set up the standalone CLI for local reviews. The connector and CLI use separate sign-ins.
---

# Set up CodeRabbit

This plugin combines a remote MCP connection with standalone CLI local reviews.
It has no automatic review hook and does not prepare a pinned MCP runtime.
Setup alone does not authorize a review or source upload.

## Connect remote tools

Use Claude's native Connect or Reconnect flow for this plugin's CodeRabbit
server at `https://mcp.coderabbit.ai/`. In Claude Code, inspect it through `/mcp`.
Let the user complete browser consent and select the intended organization.
Verify the account and organization through `connection_status` or `get_me`.
Do not inspect stored credentials or request pasted authorization codes.
Preserve other connections; if a duplicate prevents discovery, explain the
conflict before changing it. Available remote tools depend on granted scopes,
plan and permissions. Do not claim access from the browser success page alone.

## Prepare local reviews

Local review requires an initialized Git working tree, an official CodeRabbit
CLI, its own sign-in, and permission to execute it and reach CodeRabbit.
MCP sign-in does not sign in the CLI. Remote-only users can skip this section.

Read `${CLAUDE_PLUGIN_ROOT}/skills/code-review/references/auth-recovery.md` for
trusted CLI discovery and authentication checks. For a missing CLI, use the
[official installation instructions](https://docs.coderabbit.ai/cli). Follow
the native browser login procedure when needed; never copy MCP credentials into
the CLI. Preserve the user's requested organization and review scope.

Do not call `start_code_review`, pass an MCP review handoff to a shell command,
or install a hook. This package starts local reviews only through the ordinary
CLI workflow. If local execution is unavailable, report local review as
unavailable; remote MCP tools can still be connected.

If a review was already requested, follow
`${CLAUDE_PLUGIN_ROOT}/skills/code-review/SKILL.md` with the original scope.
Otherwise report remote connection and local CLI readiness separately, then
suggest “Review my changes.” Repository configuration uses
`${CLAUDE_PLUGIN_ROOT}/skills/coderabbit-config/SKILL.md` and needs no login.
