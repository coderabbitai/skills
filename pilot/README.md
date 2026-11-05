# CodeRabbit MCP pilot

**Give your Claude Code or Codex agent this page and say:**

> Install this CodeRabbit MCP pilot for the client I'm using. Follow the agent installation steps. Don't start a review; I'll complete sign-in and test it myself.

For **macOS Apple Silicon**, **Claude Code or Codex CLI**, and the **coderabbitai** organization. Git and the chosen client must already be installed. This is an opt-in pilot, not the released marketplace plugin.

## Agent installation

1. Identify the current client and check `uname -s` / `uname -m`. Stop on unsupported platforms. Install only the requested client; ask which one if the host is unclear.
2. Clone this exact branch into a permanent directory. If the destination exists, inspect its origin, branch and working tree; do not overwrite unrelated or dirty files. Use a new directory if necessary.

   ```sh
   git clone --depth 1 --branch nehal/mcp-team-pilot https://github.com/coderabbitai/skills.git "$HOME/.local/share/coderabbit-mcp-pilot"
   cd "$HOME/.local/share/coderabbit-mcp-pilot"
   ```

3. Read `pilot/install.sh` and `pilot/prepare.sh`, then run **one** command for the chosen client:

   ```sh
   ./pilot/install.sh claude
   # OR
   ./pilot/install.sh codex
   ```

   The installer downloads the pinned CLI, verifies archive and executable SHA-256, and registers the local marketplace/plugin in that client's user profile. No global CodeRabbit CLI, Python, Node or separate CLI login is required. Keep the checkout in place. Do not substitute a floating nightly or install the repository root as the MCP plugin.
4. Verify installation with the client's `plugin list` command. Report the installed plugin and request a **fresh client session** in the user's repository. Do not claim that installation proves authentication or launch a review as a setup check.
5. In the fresh session, use the installed CodeRabbit setup skill. Complete browser consent and select **coderabbitai**; confirm the returned identity/org. The user approves native folder/hook trust. Codex's `/hooks` should show one trusted CodeRabbit PostToolUse hook. Do not bypass trust, inspect OAuth stores or ask for pasted tokens. Repository configuration is optional.

Use only one active CodeRabbit plugin. If another copy is enabled, identify it and use the client's native controls to disable that copy. If a manual MCP connection hides Claude's plugin, temporarily Disable the duplicate for this repository in `/mcp`, preserve it, and restart. Never remove unrelated connections or change global permission policy.

## Test when you're ready

Ask:

> Review my uncommitted changes. Review only; do not edit files.

This sends the selected code to CodeRabbit and may consume review usage/credits. Expect one review start and one bundled hook, then findings. Keep the review ID. To recover missing output or read it in a fresh session:

> Recover the saved CodeRabbit review REVIEW_ID. Follow next_offset until null. Do not start a new review or upload source.

Failed, skipped or incomplete analysis is not a clean review. Do not submit another review just to recover missing output.

## Limits and feedback

- Pinned CLI: `0.9.2-nightly.main.20261102.268.1`; MCP: `https://mcp.coderabbit.ai/`. Review/recovery passed in Codex `0.166.0-alpha.5.1` and Claude Code `2.1.318` on November 4. This kit's agent installation is a new path; fresh teammate acceptance remains part of the pilot.
- Other platforms, organizations and sign-in methods are not qualified. The binary is ad-hoc signed. If macOS blocks it, stop and report the error; do not bypass system protections.
- Browser logout, session rotation or an organization change can require native Connect/Reconnect. Never perform a second CLI login.
- Report client/version, failed step, sanitized error and review ID in the internal pilot discussion. No tokens, authorization URLs or private source.
- To leave: `claude plugin uninstall --scope user coderabbit@coderabbit-mcp-team-pilot` or `codex plugin remove coderabbit@coderabbit-mcp-team-pilot`, then restart. Re-enable any original connection you temporarily disabled.

For a session-only Claude trial instead of persistent installation, run `pilot/prepare.sh`, then launch `pilot/start-claude.sh` from your repository using its absolute path.

Host references: [Codex packaging](https://developers.openai.com/plugins/build/plugins), [Claude plugins](https://code.claude.com/docs/en/plugins), [Claude MCP controls](https://code.claude.com/docs/en/mcp).
