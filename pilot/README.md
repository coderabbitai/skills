# CodeRabbit MCP connector pilot

Give your agent this page and say:

> Install CodeRabbit as a standalone MCP connector for this client. No plugin, skills, hooks or CLI bundle. Verify it appears in my client's connector list. Leave browser consent to me and do not start a review.

Server URL: **`https://mcp.coderabbit.ai/`**. Pilot organization: **coderabbitai**.

## Agent setup

1. Identify the actual surface: Claude desktop **Code tab / Claude Code CLI**, Claude **Chat / Cowork**, or Codex. Use the matching route below. Do not install this repository as a plugin.
2. Check for an existing CodeRabbit MCP entry or plugin. Preserve unrelated integrations. When migrating from this kit's earlier plugin, uninstall `coderabbit@coderabbit-mcp-team-pilot` with the client's native plugin manager and remove its marketplace. Do not install both routes or overwrite an existing MCP entry.
3. Register the connector, then open a fresh session. Confirm the standalone CodeRabbit entry is visible. Registration, authentication and working tools are separate checks; report which passed.
4. Let the user complete browser sign-in and choose **coderabbitai**. Confirm identity/org through a read-only account tool after consent. Do not inspect credential stores, ask for pasted tokens, bypass permissions or start a review as a setup check.

### Claude desktop Code tab or Claude Code CLI

Run with the installed Claude Code CLI:

```sh
claude mcp add --transport http --scope user coderabbit https://mcp.coderabbit.ai/
```

The desktop **Code tab** shares this user MCP configuration. Open a fresh local Code session and check its **Connectors** panel; select CodeRabbit to authenticate. In the terminal client use `/mcp`. Existing sessions may need to be restarted to reload their server list.

### Claude Chat, Cowork or an account-wide connector

Use **Settings / Customize → Connectors → Add custom connector** with name **CodeRabbit** and the server URL above, then connect. On Team/Enterprise, an authorized organization owner/admin must first add it through **Organization settings → Connectors**. If Add is disabled, report that requirement; do not substitute a plugin or claim a local CLI registration added an account connector.

### Codex

```sh
codex mcp add coderabbit --url https://mcp.coderabbit.ai/
```

Complete native browser sign-in when offered, or run `codex mcp login coderabbit`. Start a fresh session and check `/mcp`.

### Script for agents

The two CLI routes are also available as `./pilot/install.sh claude` or `./pilot/install.sh codex`. Read the script first. Clone branch `nehal/mcp-team-pilot` from `https://github.com/coderabbitai/skills.git` into an unused directory; preserve existing or dirty checkouts. The script refuses an existing `coderabbit` entry and registers only the chosen client. It does not perform account-wide Claude UI setup.

## What this connector provides

Hosted tools for authorized account/usage/PR data and saved review retrieval, subject to granted scopes. This kit installs **no plugin, skills, hooks, native CLI or nightly binary**. A remote MCP connection alone cannot collect your local source; automatic local reviews are not included. Do not start a local review unless a separately supported local execution path is available and the user requests it.

For the first test, ask for your CodeRabbit identity and organization only. Report the client/version, failed step and sanitized error if it fails. Never share tokens, authorization URLs or private source.

Remove with `claude mcp remove --scope user coderabbit` or `codex mcp remove coderabbit`; account connectors are disconnected in Claude's connector settings.

References: [Claude desktop shared configuration](https://code.claude.com/docs/en/desktop#shared-configuration), [Claude MCP](https://code.claude.com/docs/en/mcp), [Claude account connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).
