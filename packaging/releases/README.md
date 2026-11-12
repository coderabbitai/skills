# Claude release inputs

The repository-root Claude 1.3.3 candidate combines remote MCP with standalone
CLI local reviews. It declares no review hook and has no managed-runtime pins.
Its source is `main`; directory validation and publication remain separate.

The 1.3.0 and 1.3.1 files below are historical inputs for the MCP handoff packages.
Independently assembled variants still use the instructions below; they do not
define the repository-root plugin's local-review flow.

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
separate distribution ref. The repository-root listing now follows `main`; do not
switch it back to an assembled distribution branch.

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
