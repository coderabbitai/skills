---
name: setup
description: Set up the CodeRabbit plugin's bundled CLI, host-appropriate launcher and MCP browser sign-in without a separate CLI login.
---

# Set up CodeRabbit

Help the user reach **connected and ready to review** in this app. Setup alone
does not authorize uploading code or starting a review.

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
   plugin server is hidden, identify the duplicate's scope and remove that
   duplicate through `claude mcp remove --scope <scope> <name>` within the user's
   setup authorization. Preserve connections to other endpoints. Restart Claude
   Code and verify the plugin server is active; renaming the duplicate does not
   fix endpoint deduplication. Do not widen the hook to arbitrary MCP servers.
4. Discover CodeRabbit MCP tools and call `get_me` or `connection_status`. If unavailable
   or signed out, use the app's CodeRabbit **Connect** or **Reconnect** action to
   open browser sign-in. Return to the app when it completes, refresh the tool
   connection if required, and verify status again. Never request a pasted code,
   inspect credentials, or run CLI authentication.
5. Confirm the returned account and organization, and that `start_code_review`
   and `get_code_review` are available with review permission. If a review was already
   requested, resume the packaged code-review skill with the original directory,
   base, and scope. Otherwise say the plugin is ready and suggest “Review my
   changes.” Do not upload a repository just to test setup.

The plugin needs permission to run its bundled CLI and access the requested
repository and review endpoint. Use the host's normal permissions when needed;
do not change sandbox settings or route around a denied permission. A cloud or
remote session uses its own available filesystem, not the user's laptop.

If browser sign-in or reconnection fails, show the concrete error and the next
supported app action. Do not claim a successful connection from a browser success
page alone; verify it through `get_me` or the available connection-status tool.

Reference: [Claude MCP scope precedence](https://code.claude.com/docs/en/mcp#scope-hierarchy-and-precedence).
