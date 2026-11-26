# Connect CodeRabbit in other MCP clients

CodeRabbit is the governance and control layer for agentic software development
helping developers trust AI written code.

Use the hosted connection for CodeRabbit account and repository tools. Install
the [portable skills](../README.md#skills-installer) and the standalone CLI
separately when your agent needs local code review. MCP sign-in and CLI sign-in
are separate.

Repository tools require a GitHub Cloud organization. On other Git platforms,
only the account tools `connection_status`, `get_me`, and `get_usage` are
available, subject to the granted scopes.

Choose the endpoint for your organization:

| Region | URL |
| --- | --- |
| US | `https://mcp.coderabbit.ai/` |
| EU | `https://mcp.eu.coderabbit.ai/` |

The server uses Streamable HTTP and browser OAuth with PKCE. It does not accept
a CodeRabbit REST API key as an alternative to OAuth. Each connection is for
one organization. Follow the host's browser sign-in and review the consent
screen before connecting.

## Permissions

The canonical [Claude plugin](../.claude-plugin/plugin.json) requests:

```text
connection account:read usage:read pull_requests:read review repositories:read security:read security:write automations:write knowledge:write
```

When a client supports selecting OAuth scopes, request only the permissions
needed for your workflow. The full list above includes writes and actions that
can consume usage. A client that requests no scopes receives only `connection`,
which permits `connection_status`. Adding a server URL does not establish
access to review or Security tools. Check the permissions on the consent screen;
if the host cannot request the needed scopes, that workflow is not ready in
that host. See [CodeRabbit's MCP documentation](https://docs.coderabbit.ai/api/mcp).

These recipes use each host's documented configuration format. They do not
establish a marketplace listing, a completed OAuth session, or MCP Apps support.

## Amp

Install the canonical skills from this repository with Amp's own installer:

```sh
amp skill add https://github.com/coderabbitai/skills
```

Amp installs project skills under `.agents/skills/`. Add `--global` to install
on the current machine. For a remote connection available across your Amp
clients, use the personal scope:

```sh
amp mcp remote --personal add CodeRabbit https://mcp.coderabbit.ai/ --auth oauth
amp mcp remote --personal login CodeRabbit
```

For EU, use `CodeRabbit-EU` and `https://mcp.eu.coderabbit.ai/` instead. Do not
choose a workspace scope unless you intend to create a shared configuration.
Amp may reject providers it marks unsupported. Check the requested scopes
before approving sign-in; a successful connection alone does not establish
review-tool access.

Alternatively, merge the supplied [US settings](../packaging/hosted-clients/amp.us.json)
or [EU settings](../packaging/hosted-clients/amp.eu.json) into your local Amp
configuration. Local settings and Amp-hosted remote definitions are distinct
installation paths; choose one.

Sources: [Amp skills](https://ampcode.com/docs/customize/skills),
[MCP configuration](https://ampcode.com/docs/customize/mcp).

## Augment Code

In the Augment extension, open **Settings**, then **MCP > + Add remote MCP**.
Choose **HTTP**, name the server `CodeRabbit`, and enter the endpoint for your
region. Use **Authenticate** when Augment requests OAuth. You can also use
**Import from JSON** with the supplied [US](../packaging/hosted-clients/augment.us.json)
or [EU](../packaging/hosted-clients/augment.eu.json) configuration.

In Cosmos, custom MCP configurations are managed in **Settings > Connectors**.
Adding a personal connection does not add CodeRabbit to Augment's public
registry or Easy MCP catalog. Keep connection sharing limited to the intended
users and have each user connect their own CodeRabbit account.

Sources: [extension setup](https://docs.augmentcode.com/setup-augment/mcp),
[remote OAuth](https://www.augmentcode.com/changelog/remote-mcp-authentication),
[Cosmos MCP registry](https://docs.augmentcode.com/cosmos/config-mcp).

## Warp

In Warp, open **Settings > Agents > MCP servers**, choose **+ Add**, and paste
the [US configuration](../packaging/hosted-clients/warp.us.json) or
[EU configuration](../packaging/hosted-clients/warp.eu.json). Start the server
and complete Warp's OAuth flow. Check the requested permissions as described
above.

For a file-based project configuration, merge the selected snippet into
`.warp/.mcp.json` at the project root. Warp requires approval before starting
project servers. Global `~/.warp/.mcp.json` servers start automatically, so
choose the project file when you want to opt in per project.

Source: [Warp MCP configuration](https://docs.warp.dev/agents/capabilities/mcp/).

## GitHub Copilot CLI

Add the hosted server:

```sh
copilot mcp add --transport http coderabbit https://mcp.coderabbit.ai/
```

For EU, use `coderabbit-eu` and `https://mcp.eu.coderabbit.ai/`. Alternatively,
merge the supplied [US](../packaging/hosted-clients/copilot.us.json) or
[EU](../packaging/hosted-clients/copilot.eu.json) snippet into
`~/.copilot/mcp-config.json`. Preserve existing servers. Complete sign-in in
Copilot's MCP interface when prompted. The `tools` allowlist and OAuth scopes
are separate: `tools: ["*"]` does not grant permissions or approve tool calls.

### Copilot cloud agent

GitHub's repository-level cloud-agent MCP configuration currently does not
support remote servers that require OAuth. The CLI configuration above cannot
be copied there as a working CodeRabbit connection. GitHub-managed Copilot
connectors are a separate route, and CodeRabbit is not currently in its
published supported-connectors list. Do not place a browser session token or
another product's API key in repository settings to work around this boundary.

Sources: [CLI MCP setup](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-mcp-servers),
[cloud agent configuration](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers),
[supported connectors](https://docs.github.com/en/copilot/reference/supported-connectors).

## LibreChat

A LibreChat deployment operator can merge the
[US configuration](../packaging/hosted-clients/librechat.us.yaml) or
[EU configuration](../packaging/hosted-clients/librechat.eu.yaml) into
`librechat.yaml`, then restart the deployment. The snippet uses native OAuth,
dynamic client registration, explicit canonical scopes, and `startup: false`
so authentication belongs to each user. Each user connects through LibreChat's
MCP interface and reviews the requested permissions.

LibreChat also supports experimental deployment-installed Agent Plugins. Their
`mcp.json` schema does not expose LibreChat's OAuth scope settings, so this
recipe keeps the authenticated connection in `librechat.yaml`. Portable skills
can be installed separately by the deployment operator. No shared token or
command hook is needed for the hosted connection.

Sources: [MCP server configuration](https://www.librechat.ai/docs/configuration/librechat_yaml/object_structure/mcp_servers),
[Agent Plugins](https://www.librechat.ai/docs/configuration/agent_plugins).

## Emergent

Emergent has two distinct configuration surfaces. Custom Agents currently
document command-based MCP configuration. Wingman documents hosted HTTP MCP
and accepts an endpoint or standard `mcpServers` JSON, but its custom-server
authentication documentation describes bearer tokens, API keys and headers;
it does not establish the PKCE browser OAuth flow CodeRabbit requires.

The canonical endpoints and skills are available, but a direct hosted
CodeRabbit connection is pending confirmation of compatible OAuth in Emergent.
Do not substitute a REST API key or paste an OAuth session token into chat.

Sources: [Custom Agents](https://help.emergent.sh/custom-agents),
[Wingman custom MCP](https://help.emergent.sh/custom-mcp-integrations).

## LM Studio

Copy the URI for your region into your browser's address bar with LM Studio
installed, then approve opening LM Studio. GitHub strips this custom protocol
from Markdown link targets, so the installation URIs are provided as text.

US:

```text
lmstudio://add_mcp?name=coderabbit&config=eyJ1cmwiOiJodHRwczovL21jcC5jb2RlcmFiYml0LmFpLyJ9
```

EU:

```text
lmstudio://add_mcp?name=coderabbit-eu&config=eyJ1cmwiOiJodHRwczovL21jcC5ldS5jb2RlcmFiYml0LmFpLyJ9
```

Alternatively, merge the [US](../packaging/hosted-clients/lmstudio.us.json)
or [EU](../packaging/hosted-clients/lmstudio.eu.json) snippet through
**Program > Install > Edit mcp.json**. Each URI contains only the server URL.

Adding the entry is separate from authentication. CodeRabbit requires native
OAuth with PKCE and the permissions for your workflow. If your LM Studio
version does not offer that flow, stop at configuration; an API key or manually
copied session token is not a replacement. The published LM Studio guide
documents the link format and remote servers, but does not establish
CodeRabbit OAuth or MCP Apps qualification.

Sources: [LM Studio MCP](https://lmstudio.ai/docs/app/mcp),
[install-link format](https://lmstudio.ai/docs/app/mcp/deeplink).

## Zed discovery

Zed has stopped accepting new MCP extensions while it migrates to the official
MCP Registry. There is no separate discovery submission form documented on its
extension publishing page. Follow the [migration issue](https://github.com/zed-industries/zed/issues/59351)
for availability. Publishing in the official Registry does not itself prove
that a server is already visible in Zed.

Source: [Zed publishing prerequisites](https://zed.dev/docs/extensions/publishing/prerequisites).
