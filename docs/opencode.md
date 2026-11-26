# CodeRabbit skills and MCP in OpenCode

CodeRabbit is the governance and control layer for agentic software development
helping developers trust AI written code.

This source candidate targets OpenCode V2. It combines an HTTP skill catalog
served from this repository with CodeRabbit's hosted MCP connection. The catalog
contains the existing five portable skills and their supporting files.

**Availability:** the examples below point to `main`. The HTTP catalog becomes
available there after the source change is merged. No OpenCode marketplace
listing, installed-host qualification, or MCP Apps rendering is claimed.

## Configure skills and the hosted connection

Choose the example for your CodeRabbit organization's region:

- [US configuration](../packaging/opencode/opencode.us.json)
- [EU configuration](../packaging/opencode/opencode.eu.json)

Merge the example's `skills` entry and `mcp.servers.coderabbit` object into your
project's `opencode.json` or `opencode.jsonc`. Preserve your existing settings.
Use one regional connection for the account you intend to access. These are
configuration examples; files under `packaging/opencode/` are not auto-installed.

OpenCode reads `index.json` from the skill catalog's base URL, then downloads the
listed files from this repository. The skills remain maintained in the shared
`skills/` directories. No separate OpenCode copies are maintained.

The available skills are `code-review`, `autofix`, `coderabbit-config`,
`coderabbit-secure`, and `coderabbit-setup`. Explicit catalog entries have higher
precedence than automatically discovered skill directories in OpenCode V2;
avoid installing another copy with the same skill IDs unless that override is
intentional.

For a pinned source, replace `main` in the catalog URL with a commit or tag that
contains `skills/index.json`. For a local source checkout, use its absolute
`skills/` directory as the `skills` entry instead of the HTTP URL.

## Sign in through OpenCode

Run `/mcps` in OpenCode, select `coderabbit`, and complete its browser sign-in.
The equivalent command is:

```sh
opencode mcp auth coderabbit
```

OpenCode discovers OAuth configuration from the remote server and manages the
credentials outside project configuration. The examples contain no token,
client secret, authorization header, or manually selected OAuth scopes. Review
the permissions presented during sign-in and choose your CodeRabbit organization.
Reconnect when changing between US and EU accounts.

Ask: “Check my CodeRabbit connection and selected organization.” Remote tools
operate within your granted scopes, account permissions, and entitlements.
For example, ask which findings are open on an accessible pull request or
which Deep Scan findings in a named repository should be addressed first.

## Local reviews

Local review uses the separately installed and authenticated
[CodeRabbit CLI](https://docs.coderabbit.ai/cli), as described by the portable
`code-review` skill. OpenCode must have access to the intended Git checkout and
permission to execute the CLI. The hosted MCP connection does not collect local
files or transfer its credentials to the CLI.

Ask “Review my uncommitted changes. Review only; do not edit” when you want to
start a local review. Follow the shared skills for any later approved fixes.

## Maintain the catalog

After changing a skill or any of its supporting files, regenerate the index
from the repository root and commit it with the source change:

```sh
python3 .github/scripts/generate_opencode_catalog.py
```

The generator lists files from the existing skill directories and derives each
entry's cache version from its file paths and contents. This changes the cache
version even when only a reference file is edited. It does not rewrite skill
instructions, change their semantic versions, or create another source copy.
Keep the catalog and its referenced files in the same source revision.

The repository's Antigravity version guard includes `skills/` and `README.md`.
Changes to the catalog therefore also require the normal root `plugin.json`
version increment before merging. That source version is separate from an
OpenCode marketplace release.

## References

- [OpenCode V2 skill catalogs](https://opencode.ai/docs/skills/#catalogs)
- [OpenCode V2 remote MCP and OAuth](https://opencode.ai/docs/mcp-servers/#oauth)
- [CodeRabbit MCP workflows](mcp.md)
- [CodeRabbit privacy policy](https://www.coderabbit.ai/privacy-policy)
- [CodeRabbit support](https://www.coderabbit.ai/contact-us/support)
