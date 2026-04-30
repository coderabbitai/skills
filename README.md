# CodeRabbit Skills and Plugins

![Version](https://img.shields.io/badge/version-1.1.1-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/works_with-35%2B_agents-brightgreen)](#supported-agents)

The canonical home for CodeRabbit's agent-native skills and plugin packaging.
Use it to install AI-powered code review into 35+ coding agents, Claude Code,
Cursor, and other supported agent environments.

CodeRabbit detects bugs, security issues, and quality risks before you merge.

## Quickstart

Install the CodeRabbit CLI via the [CLI docs](https://docs.coderabbit.ai/cli),
then authenticate:

```bash
coderabbit auth login
```

Then tell your agent: **“Review my code.”**

## Installation

### 1. Install the CodeRabbit CLI

Use the [CLI docs](https://docs.coderabbit.ai/cli) for the primary install path.
They cover Homebrew, the install script, authentication, and CLI usage.

### 2. Install the agent integration

Choose the path that matches your coding agent.

#### Skills installer

For agents that support portable `SKILL.md` files, use the
[skills docs](https://docs.coderabbit.ai/cli/skills).

```bash
npx skills add coderabbitai/skills
```

Installation options for the skills installer:

| Flag           | Purpose                                          |
| -------------- | ------------------------------------------------ |
| `-g, --global` | Install to user directory instead of project     |
| `-a, --agent`  | Target specific agents (for example `claude-code`) |
| `-s, --skill`  | Install particular skills by name                |
| `--all`        | Install all skills to all agents without prompts |

#### Claude Code Plugin

Claude Code users can also install this as a plugin directly from the official marketplace:

```text
/plugin marketplace update
/plugin install coderabbit
```

For the full setup flow, see the
[Claude Code integration guide](https://docs.coderabbit.ai/cli/claude-code-integration).

#### Cursor Plugin

This repository now includes Cursor marketplace metadata in
[`/.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json).

After publication, Cursor marketplace installs use:

```text
/add-plugin coderabbit
```

For the current recommended setup, see the
[Cursor integration guide](https://docs.coderabbit.ai/cli/cursor-integration).

#### Codex App

Codex users can install the official CodeRabbit plugin by following the
[Codex app integration guide](https://docs.coderabbit.ai/cli/codex-integration#codex-app).

For an at-a-glance inventory of active and repo-packaged distribution paths, see
[DISTRIBUTION_CHANNELS.md](DISTRIBUTION_CHANNELS.md).

## What Lives Here

| Path | Purpose |
| --- | --- |
| `skills/` | Portable CodeRabbit skills for agents that support `SKILL.md`. |
| `.claude-plugin/` | Claude Code plugin marketplace metadata. |
| `commands/` | Claude Code slash commands shipped by the plugin. |
| `agents/` | Claude Code subagents shipped by the plugin. |
| `.cursor-plugin/` | Cursor marketplace metadata. |
| `assets/` | Shared marketplace and brand assets. |
| `DISTRIBUTION_CHANNELS.md` | Maintainer inventory of live, packaged, and in-development channels. |

## Usage

Once installed, just ask your agent:

```text
Review my code
Check for security issues
What's wrong with my changes?
Run a code review
Review my PR
Review the directory at ../my-service
```

The agent will automatically:

1. Check if CodeRabbit CLI is installed and authenticated
2. Run the review on your changes
3. Present findings grouped by severity
4. Optionally fix issues and re-review

When you ask for a specific review directory, the agent can pass CodeRabbit CLI
`--dir <path>` after confirming that path is an initialized Git repository.

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
- Supports directory-scoped reviews through CodeRabbit CLI `--dir <path>`

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

## Plugin Components

### Claude Code

- Slash command: `/coderabbit:review`
- Subagent: `code-reviewer`
- Marketplace manifest: `.claude-plugin/plugin.json`

The `code-review` skill also remains available for natural-language triggering
inside compatible agents.

### Cursor

- Marketplace manifest: `.cursor-plugin/plugin.json`
- Skills source: `skills/`

## Resources

- [CodeRabbit Documentation](https://coderabbit.ai/docs)
- [CodeRabbit CLI Guide](https://docs.coderabbit.ai/cli)
- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [Agent Skills Specification](https://agentskills.io/specification)

## License

MIT
