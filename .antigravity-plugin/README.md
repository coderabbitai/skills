# CodeRabbit

Review local code, work through pull-request feedback, and configure CodeRabbit
from Antigravity. Connect your account for remote tools, including connection,
usage and accessible pull-request workflows.

## Get connected

Ask **“Set up CodeRabbit”** to use the included `coderabbit-setup` skill, or
follow the steps below.

Install CodeRabbit from **Customizations > Marketplace**, or run
`agy plugin install coderabbit` in your terminal. Marketplace updates follow
the published version; source on GitHub may be newer.

Open the installed **CodeRabbit > Accounts** tab and sign in, or use
**Customizations > Installed > MCP Servers**.
Complete browser consent and choose your organization. If Antigravity asks for
an authorization code, enter it in Antigravity's authentication dialog, never
in a chat. In the CLI, use `/mcp` to inspect the connection.

If code submission reports “Invalid authorization code,” choose **Restart
sign-in** and complete the fresh flow. Use the new code only; if it fails again,
keep the error message for support. Review the permissions shown on consent:
Antigravity's discovered grant can include both read and write access.

Ask **“Check my CodeRabbit connection and selected organization.”** A successful
tool response confirms the connected account; the browser success page alone
does not confirm that tools are ready. Available tools depend on your plan,
organization, permissions and granted scopes.

## Review local code

Install the official [CodeRabbit CLI](https://docs.coderabbit.ai/cli), then run
`coderabbit auth login` in your own terminal. For an EU-hosted account, use
`coderabbit auth login --region eu`. MCP and CLI sign-ins are separate.

Open your Git repository in Antigravity and ask:

- **“Review my uncommitted changes. Review only; do not edit.”**
- **“Show unresolved CodeRabbit feedback on my pull request and propose fixes.”**
- **“Validate my CodeRabbit repository configuration.”**

Local reviews need terminal execution and network access. Follow Antigravity's
command approval prompts; if it cannot execute an installed CLI, ask the agent
to use the review skill's Antigravity sandbox recovery instructions.
Remote tools remain useful in sessions without local execution.
GitHub fallback and PR writes use the separately authenticated GitHub CLI.
Configuration validation requires a CLI supporting config protocol v2 and
does not require login.

## Included workflows

Four skills: `coderabbit-setup`, `code-review`, `autofix`, and `coderabbit-config`. Two agents:
`code-reviewer` and `autofix`. The autofix agent proposes a plan; the autofix
skill applies independently checked fixes with your approval. After a local
review, the agent shows findings in chat. Ask **“Set up inline CodeRabbit
review cards”** to register a compatible local CLI. When the session confirms
Apps for this local connection, the agent sends only the card ID to it. With no usable
ID the agent shows the findings in chat and sends nothing to MCP.

## Data and support

Local reviews send the selected code and required repository context to
CodeRabbit through the CLI. Remote tools exchange requested account and
repository data through MCP. Antigravity manages MCP OAuth; the CLI manages
its own credentials. Connecting alone does not upload code or start a review.

[Setup and troubleshooting](https://docs.coderabbit.ai/cli/antigravity) ·
[Support](https://www.coderabbit.ai/contact-us/support) ·
[Privacy](https://www.coderabbit.ai/privacy-policy) ·
[Terms](https://www.coderabbit.ai/terms-of-service) ·
[Source](https://github.com/coderabbitai/skills)
