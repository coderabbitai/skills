# CodeRabbit MCP pilot

For **macOS Apple Silicon**, **Codex CLI or Claude Code**, and the **coderabbitai** organization. This is an opt-in pilot, not the released marketplace plugin. Git and an installed client are required; no global CodeRabbit CLI, Python, Node or separate CLI login is needed.

## Prepare once

```sh
git clone --depth 1 --branch nehal/mcp-team-pilot https://github.com/coderabbitai/skills.git coderabbit-mcp-pilot
cd coderabbit-mcp-pilot
./pilot/prepare.sh
PILOT="$(pwd)/pilot"
```

Keep this checkout in place and continue in the same terminal so `$PILOT` stays set. Preparation downloads the exact tested CLI and verifies both archive and executable SHA-256 before installing it inside the two plugin folders. It does not sign in, change client settings or upload code.

## Choose your client

**Codex CLI** — use a client with `codex plugin` and trusted hooks:

```sh
codex plugin marketplace add "$PILOT/codex-marketplace"
codex plugin add coderabbit@coderabbit-mcp-team-pilot
cd /path/to/your/repository
codex
```

If Codex is not on PATH, use the executable supplied by your Codex installation. In `/hooks`, confirm one CodeRabbit PostToolUse hook and approve its trust through the native prompt.

**Claude Code:**

```sh
cd /path/to/your/repository
"$PILOT/start-claude.sh"
```

Use only one active CodeRabbit plugin. If an existing manual MCP connection hides the Claude plugin, temporarily Disable that entry for this repository in `/mcp`, preserve it, then restart with the launcher. Re-enable it when returning to your old setup.

## Connect, review, recover

Ask **“Set up CodeRabbit for this repository.”** Complete browser consent, select **coderabbitai**, and verify the returned identity and organization. Repository configuration is optional.

Then ask:

> Review my uncommitted changes. Review only; do not edit files.

This sends the selected code to CodeRabbit and may consume review usage/credits. It should start one review and one bundled hook, then return findings. Keep the review ID. If output is interrupted, or in a fresh session, ask:

> Recover the saved CodeRabbit review REVIEW_ID. Follow next_offset until null. Do not start a new review or upload source.

Failed, skipped or incomplete analysis is not a clean review. Do not submit another review just to recover missing output.

## Pilot limits and feedback

- The pinned CLI is `0.9.2-nightly.main.20261102.268.1`; MCP uses `https://mcp.coderabbit.ai/`. Real review and recovery passed in Codex `0.166.0-alpha.5.1` and Claude Code `2.1.318` on November 4. This kit changes preparation and setup guidance; fresh teammate onboarding is still being qualified.
- Other operating systems, processors, organizations and sign-in methods are not qualified by this pilot. The binary is ad-hoc signed; if macOS blocks execution, stop and report it—do not bypass system protections.
- Browser logout, session rotation or an organization change can require reconnecting. Use native Connect/Reconnect; do not run a second CLI login.
- Report client/version, failed step, sanitized error and review ID in the internal pilot discussion. Do not include tokens, authorization URLs or private source. Remove this local Codex plugin through its native controls, or stop launching Claude with `start-claude.sh`, to leave the pilot.

Host references: [Codex plugin packaging](https://developers.openai.com/plugins/build/plugins), [Claude plugins](https://code.claude.com/docs/en/plugins), [Claude MCP controls](https://code.claude.com/docs/en/mcp).
