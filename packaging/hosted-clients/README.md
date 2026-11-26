# Hosted MCP client configuration

Choose one region and merge the corresponding snippet into your host's existing
configuration; do not overwrite other servers. Follow the
[client guide](../../docs/hosted-mcp-clients.md) for file locations,
authentication, scope limitations, and availability.

The files contain public endpoint configuration only. They do not include
credentials or establish that a connection has been authenticated. The
LibreChat snippets request the same scopes as the canonical Claude plugin;
review those read/write permissions before connecting. Other formats retain
their host's documented URL-based configuration and require checking the
requested OAuth scopes in that host.
