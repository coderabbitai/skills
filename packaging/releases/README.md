# Claude MCP release inputs

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

The assembled package includes the [MCP changelog](../mcp/CHANGELOG.md).
Qualify the exact package before publication. Keep the plugin name `coderabbit`
and the existing directory submission. Its source must point to the assembled
package at the repository root on a dedicated distribution ref; the source tree
on `main` remains the standalone distribution.

Use a channel-specific ref such as `claude-mcp-1.3.0`, not a `v*` tag: `v*` tags
trigger the shared standalone release workflow. A GitHub release for this package
must not replace the shared skills release as Latest. Disable directory
auto-publish before switching its tracked ref, verify the imported version and
data-handling disclosure, then complete the directory's review/publish flow.

The hosted MCP server requires its own connector submission. Mod and the existing
standalone Claude/Codex channels are independent; this release does not replace
their source manifests or publish them.
