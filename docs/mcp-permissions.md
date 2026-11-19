# Connector permissions and reconnecting

A tool in a directory or scan tells you what the server offers. CodeRabbit checks
the calling user's grant, selected organization, product access and resource
permissions when a tool runs. Workspace admins can also restrict available tools
in the host. Each person connects their own CodeRabbit account.

## What each connection requests

The Claude and OpenAI 1.4.1 packages pin the US permissions advertised on
November 19, 2026. Consent covers account, usage, PR and repository reads,
hosted reviews, and read/write operations for code, triage, security, settings,
connections, knowledge, reports, Verify and automations. These writes can
change organization settings, launch work or incur usage within the user's
existing authority. Review the access for the selected organization before
approving.

- **OpenAI MCP package.** `baseScopes` includes `connection` on every request.
  `defaultScopes` lists the remaining permissions for the default consent flow.
  [OpenAI package authentication](https://developers.openai.com/plugins/build/plugins)
- **Claude Code plugin.** `oauth.scopes` pins the space-separated request. A
  user or administrator who needs a narrower grant can configure a server with
  an explicit subset including `connection`. [Claude OAuth scopes](https://code.claude.com/docs/en/mcp#restrict-oauth-scopes)
- **claude.ai directory connector.** The published listing uses dynamic client
  registration at the US endpoint. Its initial HTTP challenge requests the
  deployed cloud permissions. The challenge omits the local CLI review handoff.
  Changing the Claude Code package has no effect on this directory connection.

## When access is denied

| When a call fails | What to do |
| --- | --- |
| `401` or `invalid_token` | Sign in again to the same regional endpoint and select the intended organization. Check the result with `connection_status`. |
| `403 insufficient_scope` | Read the named `required_scope`. Update the package if its requested scopes omit that permission, then start a new browser authorization and review the requested access. Refreshing the token or rescanning tools cannot add permissions. |
| Organization, repository, role or plan denial | Check the selected organization, repository access and product entitlement. A broader OAuth grant cannot resolve these denials. |

**OpenAI.** For the publisher draft, upload the updated package, use **MCPs →
Reconnect**, review consent, then **Rescan**. Installed users renew their own
connection in the host. Publisher authorization covers the scan account only.

**Claude.** For a plugin-provided server, update the plugin, open `/mcp`, select
its CodeRabbit server and authenticate again. The claude.ai directory connector
is a separate connection to the hosted URL. In **Customize → Connectors →
CodeRabbit**, reconnect it (disconnect and connect again if needed). Review the
new consent screen. In Claude Code, an existing local, project or user server
at the same endpoint can take precedence over the plugin. Check which entry is
active before changing it. [Claude MCP configuration](https://code.claude.com/docs/en/mcp#scope-hierarchy-and-precedence)

**Region.** The packaged entries target `https://mcp.coderabbit.ai/` (US).
For an EU organization, configure a custom remote connector at
`https://mcp.eu.coderabbit.ai/` and authorize there. Use that issuer's
`/.well-known/oauth-protected-resource` to check its supported scopes. On
November 19, 2026 both regions advertised the same cloud operations. Only US
advertised `review` for the hosted local-review handoff. Requesting an
unsupported scope can prevent the entire OAuth connection.

After consent, use a read for the affected workflow, such as `list_repositories`
for `repositories:read`. `connection_status` alone only verifies the connection.
For a write, wait for the user's actual request before invoking the tool.
