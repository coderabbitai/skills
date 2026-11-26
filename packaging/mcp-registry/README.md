# Official MCP Registry

This directory describes the existing hosted CodeRabbit MCP service for the
official MCP Registry. It does not package or deploy the hosted server.

CodeRabbit is the governance and control layer for agentic software development helping developers trust AI written code.

The registry's 100-character description limit requires the shortened copy in
`server.json`. The US and EU URLs match the canonical Claude MCP configuration.
Both use Streamable HTTP and native OAuth discovery; no API keys, credentials or
client-specific OAuth scope fields belong in this registry record. Hosted access
does not read unsynced local files; CLI installation and sign-in remain separate.

`1.3.5` is this metadata candidate's version, aligned with the source plugin. It
is not a statement about the hosted service's deployment version. Bump the
registry version when changing a published record and check for an existing
record before publishing.

## Maintainer publication

The `MCP Registry metadata` workflow is manual, restricted to this repository's
`main` branch, and defaults to validation. Opening or merging a PR, creating a
tag, and pushing code do not publish anything.

After reviewing and merging the metadata and workflow:

1. Run the workflow with `mode: validate`.
2. Inspect the metadata, existing registry records and validation result.
3. For an approved publication, run with `mode: publish` and enter the exact
   `server.json` version in `version_confirmation`.

Only the publish job requests GitHub's `id-token: write`; the validation job
cannot request an OIDC token. Authentication uses `mcp-publisher login
github-oidc` and does not need a PAT, stored registry token or new repository
secret. The publisher is pinned to v1.8.16, with a fixed SHA-256 and Sigstore
verification before extraction. Checkout and the Sigstore installer are pinned
to commits, and checkout does not persist Git credentials.

The current registry requires organization ownership for PAT-based organization
authentication; interactive GitHub device authentication currently grants only
personal namespaces. Repository OIDC is the documented alternative for this
organization-owned source. Do not publish a second personal namespace just to
work around an organization permission problem.

This workflow has been prepared for review, not run for authentication or
publication. Registry acceptance and host compatibility are not claimed by
metadata validation.

References:

- [Registry authentication](https://modelcontextprotocol.io/registry/authentication)
- [GitHub Actions publication](https://modelcontextprotocol.io/registry/github-actions)
- [Remote server records](https://modelcontextprotocol.io/registry/remote-servers)
- [Canonical MCP guide](../../docs/mcp.md)
