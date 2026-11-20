# CodeRabbit for Claude

Use CodeRabbit to review local changes, work through pull request feedback, and configure repository reviews.

In Claude apps, install CodeRabbit from the Anthropic Directory. In Claude Code, install the version published to the official marketplace:

```text
/plugin install coderabbit --marketplace anthropics/claude-plugins-official
```

Run `/coderabbit:setup` to check the hosted CodeRabbit MCP connection and local CLI. Claude handles sign-in to the hosted connection. Local reviews use your installed CodeRabbit CLI and its own sign-in.

For a local review, ask “Review my uncommitted changes.” To work through feedback on a pull request, use `/coderabbit:autofix`.

This is the Claude Directory package for version 1.3.4. Its manifest, skills, agents, setup command, and icons come from [the source release](https://github.com/coderabbitai/skills/tree/983db9d387ec0e76ec06f5c58acfb8470fce8edd). See the [MCP setup guide](https://github.com/coderabbitai/skills/blob/983db9d387ec0e76ec06f5c58acfb8470fce8edd/docs/mcp.md) and the [MIT license](LICENSE).
