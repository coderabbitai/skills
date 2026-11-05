# CodeRabbit MCP connector pilot

Give your agent this page and say:

> Set up CodeRabbit using this guide: standalone MCP connector for authentication and account tools, standalone CLI for local reviews. No plugin, skills or hooks. Verify the connector and prepare the supported CLI without starting a review. Leave browser consent to me.

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

## Local reviews: MCP authorization → CLI execution

MCP authenticates the user and returns a short-lived, single-review handoff. The CLI uses it to collect and review the selected local changes, without another login. MCP can retrieve the saved findings afterward. **Needing the CLI is intended behavior.** Connector registration alone does not install it.

This pilot's pinned CLI is **0.9.2-nightly.main.20261102.268.1**, macOS Apple Silicon. Prepare it with `bash pilot/prepare-cli.sh`; this verifies both archive and executable checksums and installs only `pilot/.runtime/coderabbit`. No plugin, skill, hook or global CLI change is made. Python 3 is required for the Claude bridge. Other platforms and Codex review launch remain unqualified by this kit; account/PR connector setup remains available.

### Claude desktop Code tab / Claude Code

Claude's shell tool does not expose separate stdin. `pilot/claude-review.py` bridges one selected native MCP tool result into CLI stdin. It reads that result from the **current session's native transcript**, validates its review ID, approved options and workspace, and launches the verified CLI without putting the handoff in shell text, arguments, environment variables or a new credential file. The native host may already retain the tool result in its transcript; the handoff is a short-lived bearer capability, not the host OAuth token. This adapter depends on Claude's transcript format and is a pilot, not a portable MCP transport.

For an authorized review, the agent must:

1. Resolve the current session ID and its exact native transcript (normally `~/.claude/projects/<project>/<session-id>.jsonl`). Never scan unrelated sessions or credential stores. Confirm no review hook is also active. Inspect this bridge and the selected Git workspace. If the transcript is unavailable, stop before starting.
2. Run the bridge's `--preflight` with the verified CLI, checksum and absolute workspace below. Confirm its version. Choose this execution path before starting; respect native tool and source-upload permissions.
3. Call the connected `start_code_review` **once**, using an absolute `dir` and the user's requested scope/options.
4. Immediately run the bridge below with the server-returned review ID. The handoff stays in memory. Keep the process handle and wait for completion. Do not launch again after timeout or uncertain output; recover that ID through `get_code_review` instead.

```sh
python3 /absolute/path/to/kit/pilot/claude-review.py \
  --cli /absolute/path/to/kit/pilot/.runtime/coderabbit \
  --sha256 2f9663d6cf3ebef80da0a0c36a26d0010dba02ae87e19b8162446966a01c2470 \
  --dir /absolute/path/to/workspace \
  --transcript /absolute/path/to/current-session.jsonl \
  --session-id CURRENT_SESSION_UUID \
  --review-id SERVER_RETURNED_REVIEW_UUID
```

For preflight, use the same CLI/checksum/directory arguments plus `--preflight`, omitting transcript/session/review arguments. Do not copy the handoff into a heredoc, command, environment variable or token file. Do not change its destination or substitute ordinary CLI authentication. Report terminal status, coverage and complete delivery separately; a failed or partial review is not clean code. The account-wide Claude Chat connector alone cannot execute this local CLI path.

## First connection check

For the first test, ask for your CodeRabbit identity and organization only. Report the client/version, failed step and sanitized error if it fails. Never share tokens, authorization URLs or private source.

Remove with `claude mcp remove --scope user coderabbit` or `codex mcp remove coderabbit`; account connectors are disconnected in Claude's connector settings.

References: [Claude desktop shared configuration](https://code.claude.com/docs/en/desktop#shared-configuration), [Claude MCP](https://code.claude.com/docs/en/mcp), [Claude account connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp).
