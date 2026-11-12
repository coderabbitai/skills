# Claude release inputs

The staged Claude MCP 1.3.3 candidate restores the hook-enabled repository-root
package. Do not merge or publish it until hook-free 1.3.2 is live and the separate
Anthropic review/approval for the hook update is obtained.
Its `.claude-plugin/plugin.json`, `cli.json` and `runtime/` metadata are committed
and installable without assembling or tracking a distribution branch. The
matching release JSON records CLI 0.9.3 executable/archive checksums and the
notes describe the source transition. Update these pins together; the focused
package tests enforce their agreement.

The 1.3.0 and 1.3.1 files below remain historical inputs for earlier candidates.
Independently assembled variants still use the instructions below.
Directory approval and publication remain separate.

`claude-1.3.0.json` pins the assembled Claude MCP plugin to version **1.3.0** and
CodeRabbit CLI **0.9.3**, including archive and executable SHA-256 values for
macOS/Linux ARM64 and x64. It is an input to the existing package assembler,
not a standalone plugin manifest or a statement of directory approval.

Place the verified official executables under `native/<platform>/coderabbit`
beside the manifest. These ignored files are local assembly inputs; the directory
package contains only the readable launcher and hash pins. The assembler checks
each native executable against the manifest before producing a package.

From the repository root:

```sh
python3 scripts/assemble-plugin.py --client claude \
  --artifacts packaging/releases/claude-1.3.0.json \
  --mcp-url https://mcp.coderabbit.ai/ \
  --launcher hook --delivery download \
  --output /absolute/path/to/new-claude-1.3.0-package
```

The matching Claude hook package includes the [MCP changelog](claude-1.3.0.md).
Other clients, versions or launcher modes omit these release notes and their link.
Qualify the exact package before publication. Keep the plugin name `coderabbit`
and the existing directory submission. The historical 1.3.0 candidate used a
separate distribution ref. The native 1.3.3 source package replaces that need:
keep the existing repository-root listing tracking `main`. Merging and
publishing this staged follow-up remain separate approved steps.

For independently assembled variants, use a channel-specific ref such as
`claude-mcp-1.3.0`, not a `v*` tag: `v*` tags trigger the shared standalone release
workflow. A GitHub release for an assembled variant must not replace the shared
skills release as Latest. The native repository-root listing follows `main`.
Disable directory auto-publish before switching its tracked ref, verify the
imported version and data-handling disclosure, then complete the directory's
review/publish flow.

The hosted MCP server requires its own connector submission. Mod and the existing
standalone skill and Codex channels are independent; the native Claude manifest
has its own version. Updating source does not publish any channel.
