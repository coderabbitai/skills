---
name: setup
description: Use when setting up CodeRabbit, connecting the plugin, tailoring repository review settings or path instructions, or recovering an expired MCP connection. Guide setup with the packaged CLI and MCP browser sign-in without a separate CLI login.
---

# Set up CodeRabbit

Help the user reach **connected and ready to review**, with optional review
settings tailored to their repository. Setup alone does not authorize uploading
code or starting a review.

If the user wants to keep the existing CLI-only workflow, explain the review
skill's CLI-only option and leave MCP setup unstarted. That route does not need
MCP consent or preparation of the pinned runtime.

For a configuration-only request, read
[references/repository-config.md](references/repository-config.md) and use the
packaged CLI; local configuration does not require MCP sign-in. For general setup,
make the connection ready below, then offer repository configuration once. Keep
existing suitable settings and avoid delaying an already-requested review with
optional configuration.

1. Read this plugin's `cli.json`. Resolve its `launcher` relative to the plugin
   root, keep it inside that root, and quote its absolute path. In Claude Code,
   the root is `${CLAUDE_PLUGIN_ROOT}`; in Codex it is two directories above this
   loaded skill. For `delivery: download`, follow
   [runtime preparation](references/runtime-install.md) before using the CLI.
   For `delivery: bundled`, run `--version` directly. If local execution is
   unavailable, connect the remote account/PR tools but report that local
   reviews and local configuration are unavailable; do not reserve a review.
   A missing or corrupt bundled executable requires reinstalling the complete
   package. Neither delivery mode installs a global CLI or needs a CLI login.
2. Read `launchMode` in `cli.json`. Prefer the post-tool hook when supported,
   installed and trusted through the host's controls. It runs the normal CLI
   review only after an approved `start_code_review` call. Hook-containing Codex
   packages use the supported manual installation channel. A `direct` package is
   the hook-free fallback for channels without hook support. Confirm permitted
   local execution, network access and a process interface that can supply stdin
   separately from command arguments before selecting direct execution. Ensure
   no hook will also launch. When direct execution is selected and safe stdin
   delivery is unavailable, report that local review is unavailable; do not
   reserve a review. A trusted hook supplies its own handoff. Do not bypass a
   denied execution or upload decision.
3. In Claude Code, check the active server in `/mcp` against this package's
   `.mcp.json` URL. A manually configured connection at the same endpoint can
   hide the plugin connection. Keep an existing matching connection if its tool
   name matches the installed hook (`mcp__coderabbit__start_code_review` or
   `mcp__plugin_coderabbit_coderabbit__start_code_review`). Verify its account and
   review access below; no deletion or second connection is needed. If its name
   cannot match, explain the conflict and let the user disable that duplicate
   in its native scope, then restart and verify the plugin server. Preserve the
   entry and unrelated integrations. Renaming alone does not fix endpoint
   deduplication. Never widen the hook to arbitrary names or another endpoint.
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

The plugin needs permission to prepare and run its pinned CLI and access the requested
repository and review endpoint. Use the host's normal permissions when needed;
do not change sandbox settings or route around a denied permission. A cloud or
remote session uses its own available filesystem, not the user's laptop.

If browser sign-in or reconnection fails, show the concrete error and the next
supported app action. Do not claim a successful connection from a browser success
page alone; verify it through `get_me` or the available connection-status tool.

Reference: [Claude MCP scope precedence](https://code.claude.com/docs/en/mcp#scope-hierarchy-and-precedence).
