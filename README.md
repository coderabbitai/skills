# CodeRabbit for Claude

Use CodeRabbit to review local changes, work through pull request feedback, and configure repository reviews.

In Claude apps, install CodeRabbit from the Anthropic Directory. In Claude Code, install the version published to the official marketplace:

```text
/plugin install coderabbit --marketplace anthropics/claude-plugins-official
```

Run `/coderabbit:setup` to check the hosted CodeRabbit MCP connection and local CLI. Claude handles sign-in to the hosted connection. Local reviews use your installed CodeRabbit CLI and its own sign-in.

For a local review, ask “Review my uncommitted changes.” To work through feedback on a pull request, use `/coderabbit:autofix`.

This is the Claude Directory package for version 1.3.5. Its local review and setup guidance comes from [the source release](https://github.com/coderabbitai/skills/tree/13c46c8f30948feb4e4f48dbdc5c7b0ae5ff8408). See the [MCP setup guide](https://github.com/coderabbitai/skills/blob/13c46c8f30948feb4e4f48dbdc5c7b0ae5ff8408/docs/mcp.md) and the [MIT license](LICENSE).
