---
description: Connect CodeRabbit and prepare its pinned review runtime without a separate CLI login.
---

# Set up CodeRabbit

Read and follow `${CLAUDE_PLUGIN_ROOT}/packaging/mcp/skills/setup/SKILL.md`.
The installed root is `${CLAUDE_PLUGIN_ROOT}`. Its Claude manifest declares the
MCP connection and plugin-owned review hook. Setup does not authorize a review
or upload by itself. Preserve the requested organization, repository and scope.
