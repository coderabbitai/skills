# CodeRabbit Skills and Plugins

![Version](https://img.shields.io/badge/version-1.2.0--unreleased-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/works_with-35%2B_agents-brightgreen)](#supported-agents)

The canonical home for CodeRabbit's agent-native skills and plugin packaging.
Use it to install AI-powered code review into 35+ coding agents, Gemini CLI,
Antigravity CLI, Claude Code, Cursor, and other supported agent environments.

CodeRabbit detects bugs, security issues, and quality risks before you merge.

## Quickstart

Install the CodeRabbit CLI via the [CLI docs](https://docs.coderabbit.ai/cli),
then tell your agent: **“Review my code.”** The review command starts the
authentication flow when needed.

## Installation

### 1. Install the CodeRabbit CLI

Use the [CLI docs](https://docs.coderabbit.ai/cli) for the primary install path.
They cover Homebrew, the install script, and CLI usage.

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

#### Claude Plugin

In Claude Code, install the plugin from the official marketplace:

```text
/plugin marketplace update
/plugin install coderabbit@claude-plugins-official
```

A listing in the Claude directory is in review. Once it's published, you'll
also be able to add CodeRabbit from **Customize > Plugins > Discover** in
claude.ai or the Claude desktop app, and it will sync to Claude Code sessions
where you're signed in with the same claude.ai account. If you install from
both places, Claude Code loads the marketplace copy.

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

#### Gemini CLI Extension (pre-release)

Until `v1.2.0` is published as the Latest release, Gemini CLI users can install
the native extension from `main`:

```bash
gemini extensions install https://github.com/coderabbitai/skills --ref main
gemini extensions list
```

After `v1.2.0` is published, the `--ref main` option can be omitted.

The repository-root [`gemini-extension.json`](gemini-extension.json) packages
the portable skills, `/coderabbit:review` command, and both subagents.
This native extension is separate from the generic skills-installer path above.

#### Antigravity CLI Plugin

Antigravity CLI users can install the native plugin directly from this
repository:

```bash
agy plugin install https://github.com/coderabbitai/skills
agy plugin list
```

The repository-root [`plugin.json`](plugin.json) manifest packages the skills,
review command, and both subagents for Antigravity CLI's plugin discovery.

#### Codex App

Codex users can install the official CodeRabbit plugin by following the
[Codex app integration guide](https://docs.coderabbit.ai/cli/codex-integration#codex-app).

Native Codex metadata in [`.codex-plugin/plugin.json`](.codex-plugin/plugin.json)
references the existing `skills/` directory. Marketplace publication remains a
separate step; this source change does not update the live listing.

For an at-a-glance inventory of active and repo-packaged distribution paths, see
[DISTRIBUTION_CHANNELS.md](DISTRIBUTION_CHANNELS.md).

## What Lives Here

| Path | Purpose |
| --- | --- |
| `skills/` | Portable CodeRabbit skills for agents that support `SKILL.md`. |
| `.claude-plugin/` | Claude Code plugin marketplace metadata. |
| `commands/` | Native review commands for Gemini CLI and Antigravity CLI. |
| `agents/` | `code-reviewer` and `autofix` subagents shipped to Claude Code, Gemini CLI, and Antigravity CLI. |
| `.cursor-plugin/` | Cursor marketplace metadata. |
| `.codex-plugin/` | Codex metadata referencing the shared skills. |
| `gemini-extension.json` | Gemini CLI extension manifest. |
| `plugin.json` | Antigravity CLI plugin manifest. |
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

1. Check if CodeRabbit CLI is installed
2. Run the review on your changes
3. Present findings grouped by severity
4. Optionally fix issues and re-review

When you ask for a specific review directory, the agent can pass CodeRabbit CLI
`--dir <path>` after confirming that path is inside an initialized Git working
tree.

## Supported Agents

CodeRabbit supports 35+ coding agents.

| Agent              | Project Path           | Global Path                            |
| ------------------ | ---------------------- | -------------------------------------- |
| Amp, Kimi Code CLI | `.agents/skills/`      | `~/.config/agents/skills/`             |
| Antigravity CLI    | `.agents/skills/`      | `~/.gemini/config/skills/`              |
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
- Preserves finding severities (critical, major, minor, trivial, info, none)
- Supports autonomous fix-review cycles
- Reviews tracked changes by default, with committed and uncommitted scopes
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

- Skills: `code-review` and `autofix`. Run them as `/coderabbit:code-review`
  and `/coderabbit:autofix`, or ask in plain language, such as "review my
  changes" or "fix the CodeRabbit comments on this PR".
- Subagents: `code-reviewer` runs a CodeRabbit review in its own context, and
  `autofix` collects and checks unresolved CodeRabbit review threads
  and returns a fix plan without editing anything. Mention them as
  `@agent-coderabbit:code-reviewer` and `@agent-coderabbit:autofix`.
- Manifest: `.claude-plugin/plugin.json`

The Claude plugin doesn't include the review command in `commands/`, which is
packaged for Gemini CLI and Antigravity CLI. In Claude, use
`/coderabbit:code-review` instead of the earlier
`/coderabbit:coderabbit-review`.

The plugin runs reviews through the locally installed CodeRabbit CLI, so it
needs a shell on a machine where the CLI is installed and logged in. Claude Code
has full support. Cowork and Claude chat on the web, desktop, and mobile can
load the skills, but a review runs only where the CodeRabbit CLI is available,
and chat doesn't run subagents.

### Cursor

- Marketplace manifest: `.cursor-plugin/plugin.json`
- Skills source: `skills/`

### Antigravity CLI

- Native plugin manifest: `plugin.json`
- Skills source: `skills/`
- Review command: `commands/coderabbit-review.md` (converted to a skill during installation)
- Subagents: `agents/code-reviewer.md`, `agents/autofix.md`

### Gemini CLI

- Native extension manifest: `gemini-extension.json`
- Skills source: `skills/`
- Slash command: `/coderabbit:review` (`commands/coderabbit/review.toml`)
- Subagents: `agents/code-reviewer.md`, `agents/autofix.md`

## Data and Privacy

The Claude plugin contains two skills and two subagents. It bundles no MCP
servers, hooks, or executables.

- **Local commands**: the `code-review` skill and the `code-reviewer` subagent
  run the installed `coderabbit` CLI and read-only Git commands. The `autofix`
  skill uses the installed GitHub CLI (`gh`) to read CodeRabbit review threads
  on the current pull request and, when you approve, to create a pull request or
  post a summary comment. The `autofix` subagent only reads: it runs
  read-only `git` and `gh` commands and never edits, commits, pushes, or posts.
- **Data sent**: when you run a review, the CodeRabbit CLI sends the code
  changes under review and the repository context needed to review them to
  CodeRabbit's service. `autofix` exchanges pull request data with GitHub
  through `gh`. The plugin sends nothing on its own.
- **Credentials**: the CodeRabbit CLI and `gh` handle their own login and store
  their own credentials. The plugin doesn't read or send credentials.
- **Policy**: CodeRabbit's handling, retention, and sharing of review data is
  described in the [CodeRabbit Privacy Policy](https://www.coderabbit.ai/privacy-policy).
  Contact <support@coderabbit.ai> with questions.

## Resources

- [CodeRabbit Documentation](https://coderabbit.ai/docs)
- [CodeRabbit CLI Guide](https://docs.coderabbit.ai/cli)
- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [Agent Skills Specification](https://agentskills.io/specification)
- [Gemini CLI Extension Documentation](https://geminicli.com/docs/extensions/reference/)
- [Antigravity CLI Plugin Documentation](https://antigravity.google/docs/cli-plugins)

## License

MIT
