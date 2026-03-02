# CodeRabbit Skills

![Version](https://img.shields.io/badge/version-1.0.0-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/works_with-35%2B_agents-brightgreen)](#supported-agents)

AI-powered code review for 35+ coding agents, powered by [CodeRabbit](https://coderabbit.ai). Detect bugs, security issues, and quality risks before you merge.

## Quickstart

```bash
# Install the CodeRabbit CLI
# Follow official instructions: https://www.coderabbit.ai/cli

# Authenticate
coderabbit auth login

# Install the skill
npx skills add coderabbitai/skills
```

Then tell your agent: **“Review my code.”**

## Installation

```bash
npx skills add coderabbitai/skills
```

### Installation Options

| Flag           | Purpose                                          |
| -------------- | ------------------------------------------------ |
| `-g, --global` | Install to user directory instead of project     |
| `-a, --agent`  | Target specific agents (e.g., `-a claude-code`)  |
| `-s, --skill`  | Install particular skills by name                |
| `--all`        | Install all skills to all agents without prompts |

Examples:

```bash
npx skills add coderabbitai/skills
npx skills add coderabbitai/skills -g
npx skills add coderabbitai/skills -a claude-code
npx skills add coderabbitai/skills -a codex
npx skills add coderabbitai/skills -a cursor
```

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

Skills can be installed to any of these agents:

| Agent              | `--agent`         | Project Path           | Global Path                            |
| ------------------ | ----------------- | ---------------------- | -------------------------------------- |
| Amp, Kimi Code CLI | `amp`, `kimi-cli` | `.agents/skills/`      | `~/.config/agents/skills/`             |
| Antigravity        | `antigravity`     | `.agent/skills/`       | `~/.gemini/antigravity/global_skills/` |
| Claude Code        | `claude-code`     | `.claude/skills/`      | `~/.claude/skills/`                    |
| Cline              | `cline`           | `.cline/skills/`       | `~/.cline/skills/`                     |
| CodeBuddy          | `codebuddy`       | `.codebuddy/skills/`   | `~/.codebuddy/skills/`                 |
| Codex              | `codex`           | `.codex/skills/`       | `~/.codex/skills/`                     |
| Command Code       | `command-code`    | `.commandcode/skills/` | `~/.commandcode/skills/`               |
| Continue           | `continue`        | `.continue/skills/`    | `~/.continue/skills/`                  |
| Crush              | `crush`           | `.crush/skills/`       | `~/.config/crush/skills/`              |
| Cursor             | `cursor`          | `.cursor/skills/`      | `~/.cursor/skills/`                    |
| Droid              | `droid`           | `.factory/skills/`     | `~/.factory/skills/`                   |
| Gemini CLI         | `gemini-cli`      | `.gemini/skills/`      | `~/.gemini/skills/`                    |
| GitHub Copilot     | `github-copilot`  | `.github/skills/`      | `~/.copilot/skills/`                   |
| Goose              | `goose`           | `.goose/skills/`       | `~/.config/goose/skills/`              |
| Junie              | `junie`           | `.junie/skills/`       | `~/.junie/skills/`                     |
| Kilo Code          | `kilo`            | `.kilocode/skills/`    | `~/.kilocode/skills/`                  |
| Kiro CLI           | `kiro-cli`        | `.kiro/skills/`        | `~/.kiro/skills/`                      |
| Kode               | `kode`            | `.kode/skills/`        | `~/.kode/skills/`                      |
| MCPJam             | `mcpjam`          | `.mcpjam/skills/`      | `~/.mcpjam/skills/`                    |
| Moltbot            | `moltbot`         | `skills/`              | `~/.moltbot/skills/`                   |
| Mux                | `mux`             | `.mux/skills/`         | `~/.mux/skills/`                       |
| Neovate            | `neovate`         | `.neovate/skills/`     | `~/.neovate/skills/`                   |
| OpenClaude IDE     | `openclaude`      | `.openclaude/skills/`  | `~/.openclaude/skills/`                |
| OpenCode           | `opencode`        | `.opencode/skills/`    | `~/.config/opencode/skills/`           |
| OpenHands          | `openhands`       | `.openhands/skills/`   | `~/.openhands/skills/`                 |
| Pi                 | `pi`              | `.pi/skills/`          | `~/.pi/agent/skills/`                  |
| Pochi              | `pochi`           | `.pochi/skills/`       | `~/.pochi/skills/`                     |
| Qoder              | `qoder`           | `.qoder/skills/`       | `~/.qoder/skills/`                     |
| Qwen Code          | `qwen-code`       | `.qwen/skills/`        | `~/.qwen/skills/`                      |
| Replit             | `replit`          | `.agent/skills/`       | N/A (project-only)                     |
| Roo Code           | `roo`             | `.roo/skills/`         | `~/.roo/skills/`                       |
| Trae               | `trae`            | `.trae/skills/`        | `~/.trae/skills/`                      |
| Trae CN            | `trae-cn`         | `.trae/skills/`        | `~/.trae-cn/skills/`                   |
| Windsurf           | `windsurf`        | `.windsurf/skills/`    | `~/.codeium/windsurf/skills/`          |
| Zencoder           | `zencoder`        | `.zencoder/skills/`    | `~/.zencoder/skills/`                  |

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

Auto-fix workflow for unresolved CodeRabbit GitHub PR review comments, with interactive per-issue review or batch fixing.

**Use when:**

- You already have an open GitHub PR reviewed by CodeRabbit
- You want to apply suggested fixes from unresolved CodeRabbit threads
- You want either manual approval per issue or one-pass batch autofix

**Categories covered:** Review-thread extraction, issue prioritization, guided fixes, consolidated commit and PR summary

**Triggers:** "coderabbit autofix", "fix coderabbit", "cr fix"

**Capabilities:**

- Fetches unresolved CodeRabbit review threads for the current PR
- Parses and prioritizes issues by severity
- Applies fixes interactively or in batch mode
- Produces a single consolidated commit and posts a PR summary comment

## Resources

- [CodeRabbit Documentation](https://coderabbit.ai/docs)
- [CodeRabbit CLI Guide](https://docs.coderabbit.ai/cli)
- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [Agent Skills Specification](https://agentskills.io/specification)

## License

MIT
