# Connected Codex candidate

The source in this directory belongs to the connected `coderabbit` 1.3.0
listing. Both ZIPs contain the same five skills, including `coderabbit-secure`. The portable listing
uses the original OAuth declaration and review metadata. The native Codex
reader uses its own manifest and native `scopes` field for the same hosted
server and five scopes. The repository root's skills-only Codex package has
its own version and release process.

Secure operations require a connection with the repository and Security
permissions for the requested action. See the [Secure connection guide](../../docs/mcp.md#coderabbit-secure).

Both profiles wire the native setup action to `coderabbit-setup`. The
portable server-level OAuth extension follows [OpenAI's packaging reference](https://developers.openai.com/plugins/build/plugins).
The base Agent Plugins MCP schema currently rejects per-server extensions.
Use the OpenAI portal to verify its importer before publication.

From a clean checkout with Python 3 and Git, build into new files:

```sh
python3 packaging/codex-connected/build.py portal /tmp/coderabbit-portal.zip
python3 packaging/codex-connected/build.py native /tmp/coderabbit-native.zip
```

Use the portable artifact for partner-portal validation, and extract the native
artifact at a local Codex marketplace's plugin source for a native reader test.
Neither ZIP starts a local process on install. On a local host, ask “Set up
inline CodeRabbit review cards.” The setup skill can register an eligible
installed CLI using the current user's verified executable path. Hosted-only
clients can still connect to the production server. Portal acceptance, native
installation and a successful card render are separate release checks.
