---
name: setup
description: Use when setting up CodeRabbit, connecting the plugin, tailoring repository review settings or path instructions, or recovering an expired MCP connection. Guide setup with the bundled CLI and MCP browser sign-in without a separate CLI login.
---

# Set up CodeRabbit

Help the user reach **connected and ready to review**, with optional review
settings tailored to their repository. Setup alone does not authorize uploading
code or starting a review.

For a configuration-only request, read
[references/repository-config.md](references/repository-config.md) and use the
bundled CLI; local configuration does not require MCP sign-in. For general setup,
make the connection ready below, then offer repository configuration once. Keep
existing suitable settings and avoid delaying an already-requested review with
optional configuration.

1. Resolve the bundled `bin/coderabbit` from this plugin. In Claude Code, use
   `"${CLAUDE_PLUGIN_ROOT}/bin/coderabbit"`. In Codex, resolve `../../bin/coderabbit`
   relative to this loaded skill's directory and use the absolute path. Run
   `--version` to check the installed artifact. If the bundle is incomplete,
   unsupported, or corrupt, report the specific failure and reinstall through
   the app's plugin flow. Do not install a global CLI or a separate runtime.
2. Read the installed `bin/launch-mode`. Prefer the post-tool hook when supported,
   installed and trusted through the host's controls. It runs the normal CLI
   review only after an approved `start_code_review` call. Hook-containing Codex
   packages use the supported manual installation channel. A `direct` package is
   the hook-free fallback for channels without hook support. Confirm permitted
   local execution and network access before selecting direct execution; ensure
   no hook will also launch. Do not bypass a denied execution or upload decision.
3. In Claude Code, confirm `/mcp` shows the plugin-provided CodeRabbit server.
   A manually configured server at the same endpoint takes precedence, even with
   a different name, and can prevent the collector hook from matching. If the
   plugin server is hidden, identify the duplicate and use `/mcp` to temporarily
   Disable it for this repository through the user's native controls. Preserve
   the saved connection and connections to other endpoints. Restart Claude Code
   and verify the plugin server is active. Re-enable the original entry when
   returning to the previous setup. Renaming the duplicate does not fix endpoint
   deduplication. Do not widen the hook to arbitrary MCP servers.
4. Discover CodeRabbit MCP tools and call `get_me` or `connection_status`. If unavailable
   or signed out, use the app's CodeRabbit **Connect** or **Reconnect** action to
   open browser sign-in. Return to the app when it completes, refresh the tool
   connection if required, and verify status again. Never request a pasted code,
   inspect credentials, or run CLI authentication.
5. Confirm the returned account and organization, and that `start_code_review`
   and `get_code_review` are available with review permission. If a review was already
   requested, resume the packaged code-review skill with every original option,
   including directory, base, scope, `include_untracked`, and `instructions`.
   Otherwise confirm the connection is ready and offer to tailor review settings
   for this repository, or start with “Review my changes.” When the user wants
   configuration help, read
   [references/repository-config.md](references/repository-config.md). Do not
   upload a repository just to test setup.

The plugin needs permission to run its bundled CLI and access the requested
repository and review endpoint. Use the host's normal permissions when needed;
do not change sandbox settings or route around a denied permission. A cloud or
remote session uses its own available filesystem, not the user's laptop.

If browser sign-in or reconnection fails, show the concrete error and the next
supported app action. Do not claim a successful connection from a browser success
page alone; verify it through `get_me` or the available connection-status tool.

Reference: [Claude MCP scope precedence](https://code.claude.com/docs/en/mcp#scope-hierarchy-and-precedence).
