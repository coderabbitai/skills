# CodeRabbit for Claude

Use CodeRabbit to review local changes, work through pull request feedback, and configure repository reviews.

In Claude apps, install CodeRabbit from the Anthropic Directory. In Claude Code, install the version published to the official marketplace:

```text
/plugin install coderabbit --marketplace anthropics/claude-plugins-official
```

Run `/coderabbit:setup` to check the hosted CodeRabbit MCP connection and local CLI. Claude handles sign-in to the hosted connection. Local reviews use your installed CodeRabbit CLI and its own sign-in.

For a local review, ask “Review my uncommitted changes.” To work through feedback on a pull request, use `/coderabbit:autofix`.

## What CodeRabbit can read, send, and change

The hosted CodeRabbit MCP server can read your connected account, review usage, and pull requests you can access, including review comments and checks. Its review tools can start a review, receive selected code changes through a compatible CLI, and return findings to Claude. Reviews can consume CodeRabbit review credits.

The hosted server also offers tools with separate write permissions. For example, it can send product feedback to CodeRabbit, publish an issue to GitHub, Jira, or Linear, start a paid security scan, change a scan schedule, or delete a saved security learning. These actions require additional OAuth permissions and access to the relevant product or destination. This Directory package requests only connection, account read, usage read, pull request read, and review permissions.

When you ask for a local review, the standalone CLI sends the selected changes and required repository context to CodeRabbit for analysis. If you enable inline cards, a separate local MCP server reads the saved result and displays it in Claude. Displaying the card does not upload the findings again.

This is the Claude Directory package for version 1.3.5. Its local review and setup guidance comes from [the source release](https://github.com/coderabbitai/skills/tree/13c46c8f30948feb4e4f48dbdc5c7b0ae5ff8408). See the [MCP setup guide](https://github.com/coderabbitai/skills/blob/13c46c8f30948feb4e4f48dbdc5c7b0ae5ff8408/docs/mcp.md) and the [MIT license](LICENSE).
