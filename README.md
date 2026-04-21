# CodeRabbit Skills

![Version](https://img.shields.io/badge/version-1.0.0-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/works_with-35%2B_agents-brightgreen)](#supported-agents)

AI-powered code review for 35+ coding agents, powered by [CodeRabbit](https://coderabbit.ai). Detect bugs, security issues, and quality risks before you merge.

## Quickstart

```bash
# Install the CodeRabbit CLI
# Use Homebrew or the install script:
# https://docs.coderabbit.ai/cli
curl -fsSL https://cli.coderabbit.ai/install.sh | sh

# Authenticate
coderabbit auth login
```

Then tell your agent: **“Review my code.”**

## Installation

Install the CodeRabbit CLI using Homebrew or the install script by following the
[CLI docs](https://docs.coderabbit.ai/cli).

### Claude Code Plugin

Claude Code users can also install this as a plugin directly from the official marketplace:

In Claude Code:

```text
/plugin marketplace update
/plugin install coderabbit
```

### Cursor Plugin

This repository now includes Cursor marketplace metadata in
[`/.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json).

After publication, Cursor marketplace installs use:

```text
/add-plugin coderabbit
```

For the current recommended setup, see the
[Cursor integration guide](https://docs.coderabbit.ai/cli/cursor-integration).

### Codex App

Codex users can install the official CodeRabbit plugin by following the
[Codex app integration guide](https://docs.coderabbit.ai/cli/codex-integration#codex-app).

## Usage

Once installed, just ask your agent:

```text
Review my code
Check for security issues
What's wrong with my changes?
Run a code review
Review my PR
```

The agent will automatically:

1. Check if CodeRabbit CLI is installed and authenticated
2. Run the review on your changes
3. Present findings grouped by severity
4. Optionally fix issues and re-review

## Supported Agents

CodeRabbit supports 35+ coding agents.

| Agent              | Project Path           | Global Path                            |
| ------------------ | ---------------------- | -------------------------------------- |
| Amp, Kimi Code CLI | `.agents/skills/`      | `~/.config/agents/skills/`             |
| Antigravity        | `.agent/skills/`       | `~/.gemini/antigravity/global_skills/` |
| Claude Code        | `.claude/skills/`      | `~/.claude/skills/`                    |
| Cline              | `.cline/skills/`       | `~/.cline/skills/`                     |
| CodeBuddy          | `.codebuddy/skills/`   | `~/.codebuddy/skills/`                 |
| Codex              | `.codex/skills/`       | `~/.codex/skills/`                     |
| Command Code       | `.commandcode/skills/` | `~/.commandcode/skills/`               |
| Continue           | `.continue/skills/`    | `~/.continue/skills/`                  |
| Crush              | `.crush/skills/`       | `~/.config/crush/skills/`              |
| Cursor             | `.cursor/skills/`      | `~/.cursor/skills/`                    |
| Droid              | `.factory/skills/`     | `~/.factory/skills/`                   |
| Gemini CLI         | `.gemini/skills/`      | `~/.gemini/skills/`                    |
| GitHub Copilot     | `.github/skills/`      | `~/.copilot/skills/`                   |
| Goose              | `.goose/skills/`       | `~/.config/goose/skills/`              |
| Junie              | `.junie/skills/`       | `~/.junie/skills/`                     |
| Kilo Code          | `.kilocode/skills/`    | `~/.kilocode/skills/`                  |
| Kiro CLI           | `.kiro/skills/`        | `~/.kiro/skills/`                      |
| Kode               | `.kode/skills/`        | `~/.kode/skills/`                      |
| MCPJam             | `.mcpjam/skills/`      | `~/.mcpjam/skills/`                    |
| Moltbot            | `skills/`              | `~/.moltbot/skills/`                   |
| Mux                | `.mux/skills/`         | `~/.mux/skills/`                       |
| Neovate            | `.neovate/skills/`     | `~/.neovate/skills/`                   |
| OpenClaude IDE     | `.openclaude/skills/`  | `~/.openclaude/skills/`                |
| OpenCode           | `.opencode/skills/`    | `~/.config/opencode/skills/`           |
| OpenHands          | `.openhands/skills/`   | `~/.openhands/skills/`                 |
| Pi                 | `.pi/skills/`          | `~/.pi/agent/skills/`                  |
| Pochi              | `.pochi/skills/`       | `~/.pochi/skills/`                     |
| Qoder              | `.qoder/skills/`       | `~/.qoder/skills/`                     |
| Qwen Code          | `.qwen/skills/`        | `~/.qwen/skills/`                      |
| Replit             | `.agent/skills/`       | N/A (project-only)                     |
| Roo Code           | `.roo/skills/`         | `~/.roo/skills/`                       |
| Trae               | `.trae/skills/`        | `~/.trae/skills/`                      |
| Trae CN            | `.trae/skills/`        | `~/.trae-cn/skills/`                   |
| Windsurf           | `.windsurf/skills/`    | `~/.codeium/windsurf/skills/`          |
| Zencoder           | `.zencoder/skills/`    | `~/.zencoder/skills/`                  |

## Available Skills

### [code-review](skills/code-review/SKILL.md)

AI-powered code review that finds bugs, security issues, and suggests improvements using CodeRabbit.

**Use when:**

- You want to review code changes before committing or merging
- Checking for bugs, security vulnerabilities, or anti-patterns
- Getting PR feedback or suggestions for improvements
- Running automated code quality checks

**Categories covered:** Bug detection, security analysis, code quality, performance issues, best practices

**Triggers:** "review my code", "check for bugs", "security review", "PR feedback", "run coderabbit"

**Capabilities:**

- Analyzes code changes for bugs, security issues, and anti-patterns
- Groups findings by severity (critical, warning, info)
- Supports autonomous fix-review cycles
- Works with staged, committed, or all changes

### [autofix](skills/autofix/SKILL.md)

Safe fix workflow for unresolved CodeRabbit GitHub PR review threads, with per-issue review and approval.

**Use when:**

- You already have an open GitHub PR reviewed by CodeRabbit
- You want to apply suggested fixes from unresolved current CodeRabbit review threads
- You want guided fixes with explicit approval for each change

**Categories covered:** Review-thread extraction, issue prioritization, guarded fixes, consolidated commit and PR summary

**Triggers:** "coderabbit autofix", "fix coderabbit", "cr fix"

**Capabilities:**

- Fetches unresolved current CodeRabbit review threads for the current PR
- Parses and prioritizes issues by severity
- Applies fixes only after validating the issue and getting approval
- Produces a single consolidated commit and posts a PR summary comment

## Resources

- [CodeRabbit Documentation](https://coderabbit.ai/docs)
- [CodeRabbit CLI Guide](https://docs.coderabbit.ai/cli)
- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [Agent Skills Specification](https://agentskills.io/specification)

## License

MIT
