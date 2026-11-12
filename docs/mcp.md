# Connect CodeRabbit through MCP

The Claude plugin 1.3.2 candidate combines CodeRabbit's remote MCP connection
with standalone CLI local reviews. It declares no automatic hooks. Source on
`main` and directory publication are separate; see
[distribution status](../DISTRIBUTION_CHANNELS.md).

## Set up

Run `/coderabbit:setup` in the installed Claude plugin.

1. Connect CodeRabbit through Claude's native browser sign-in and select your
   organization. In Claude Code, use `/mcp` to inspect the connection.
2. For local reviews, install the official [CodeRabbit CLI](https://docs.coderabbit.ai/cli)
   and sign in through its own browser flow. An existing authenticated CLI can
   be reused. MCP and CLI sign-ins are separate.
3. Ask “Review my uncommitted changes. Review only; do not edit.” Local reviews
   use the standalone CLI and the host's normal execution permissions.

A remote MCP connection cannot read files on your laptop. Local review requires
an initialized Git working tree available to the host, permission to run the
CLI and network access to CodeRabbit. If those are unavailable, remote tools
can still be used but local review cannot run.

## Remote tools and local reviews

The declared remote connection provides tools within the granted scopes and
your account's permissions. Use it for account, usage and accessible pull-request
workflows. Product and tool availability depends on the plan and permissions;
connecting does not grant access to every CodeRabbit product.

Local reviews do not call MCP `start_code_review`, reserve an MCP review, or use
a review handoff. They use the CLI's authentication, review output and saved
results. To retrieve local findings or fix prompts without rerunning, follow
[the CLI workflow guide](../skills/code-review/references/cli-workflows.md).

An existing MCP review may still be recovered through `get_code_review` using
its original review ID and all result pages. Do not start a standalone CLI
review to recover an uncertain MCP review. Do not assume a standalone CLI review
is available through MCP recovery.

## Data and support

Local review sends the selected code changes and required repository context to
CodeRabbit through the CLI. Remote MCP tools exchange their requested data with
CodeRabbit through Claude. The host manages connector OAuth; the standalone CLI
manages its own credentials. The plugin does not copy credentials between them.
Setup alone does not upload code or start a review.

See the [CodeRabbit Privacy Notice](https://www.coderabbit.ai/privacy-policy).
Contact [CodeRabbit support](mailto:support@coderabbit.ai) with versions, the
concrete error and review ID when available; never send credentials.

## Other packages

The independently assembled MCP hook/direct packages under `packaging/` are
separate development candidates. Their runtime and authentication instructions
do not apply to the repository-root 1.3.2 plugin and require their own qualification.
