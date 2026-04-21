# CodeRabbit Skills

![Version](https://img.shields.io/badge/version-1.0.0-blue)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/works_with-35%2B_agents-brightgreen)](#supported-agents)

AI-powered code review for 35+ coding agents, powered by [CodeRabbit](https://coderabbit.ai). Detect bugs, security issues, and quality risks before you merge.

## Quickstart

```bash
# Install (or upgrade) the CodeRabbit CLI — this also prompts to install
# CodeRabbit skills into every coding agent it detects on your machine.
curl -fsSL https://cli.coderabbit.ai/install.sh | sh

# Authenticate
coderabbit auth login
```

Then tell your agent: **“Review my code.”**

The CLI auto-detects agents like Claude Code, Codex, Cursor, Gemini CLI, and 30+ others, and drops the skills into each agent's global skills directory.

## Installation

Skills are distributed by the CodeRabbit CLI directly from the [`main`](https://github.com/coderabbitai/skills) branch of this repo. There are three entry points, in priority order:

### 1. Automatic on CLI install (recommended)

```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

On a fresh install or upgrade, the install script prompts once — *only when running in an interactive terminal* — to install skills into every detected agent. Answer yes, and the CLI syncs skills to each agent's global skills path. Your answer is remembered so future CLI upgrades don't re-prompt.

### 2. Manual sync

```bash
coderabbit integrations setup
```

Runs the sync on demand. Always syncs, regardless of prior preference — no prompt. A successful run flips your preference to opted-in, so future CLI upgrades will keep skills up to date automatically.

### 3. Opt out

```bash
coderabbit integrations disable
```

Flips your preference to opted-out. Sticky: subsequent CLI installs, upgrades, and any automatic triggers will skip the skills sync entirely. Only a later `integrations setup` clears it.

### Behavior summary

The table below shows how the CLI decides whether to sync skills. "Preference" is the value stored in `~/.coderabbit/skills.json`.

| Trigger                  | Preference state | TTY | Action                                        |
| ------------------------ | ---------------- | --- | --------------------------------------------- |
| `install.sh`             | unset            | yes | Prompt once; sync if accepted, record choice  |
| `install.sh`             | unset            | no  | Skip (no prompt, no sync)                     |
| `install.sh`             | opted-in         | any | Sync silently                                 |
| `install.sh`             | opted-out        | any | Skip                                          |
| `integrations setup`     | any              | any | Sync; set preference to opted-in              |
| `integrations disable`   | any              | any | Set preference to opted-out (no files removed) |

The CLI fetches the `main` branch tarball of this repo and copies each skill directory atomically into every detected agent's global skills path. A sha256 of the archive is cached; identical archive content short-circuits to a no-op on subsequent runs.

### Where skills land

Skills are copied to each detected agent's global skills directory — for example, `~/.claude/skills/` for Claude Code or `~/.codex/skills/` for Codex. See [Supported Agents](#supported-agents) for the full map. Skills authored by others that already live in the same folder are left untouched; the CLI only manages directories it installed.

### Privacy and consent

Your install preference is captured in `~/.coderabbit/skills.json`, along with the installed `version` of each skill. Running `coderabbit integrations disable` flips the preference to opted-out but does **not** delete previously installed skill directories from your agent folders — remove those manually if you want them gone.

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

The CodeRabbit CLI auto-detects which of these agents are installed on your machine and syncs skills to each one's global skills path. There is no `--agent` flag to pass — detection is automatic.

| Agent              | Global Path                            |
| ------------------ | -------------------------------------- |
| Amp, Kimi Code CLI | `~/.config/agents/skills/`             |
| Antigravity        | `~/.gemini/antigravity/global_skills/` |
| Claude Code        | `~/.claude/skills/`                    |
| Cline              | `~/.cline/skills/`                     |
| CodeBuddy          | `~/.codebuddy/skills/`                 |
| Codex              | `~/.codex/skills/`                     |
| Command Code       | `~/.commandcode/skills/`               |
| Continue           | `~/.continue/skills/`                  |
| Crush              | `~/.config/crush/skills/`              |
| Cursor             | `~/.cursor/skills/`                    |
| Droid              | `~/.factory/skills/`                   |
| Gemini CLI         | `~/.gemini/skills/`                    |
| GitHub Copilot     | `~/.copilot/skills/`                   |
| Goose              | `~/.config/goose/skills/`              |
| Junie              | `~/.junie/skills/`                     |
| Kilo Code          | `~/.kilocode/skills/`                  |
| Kiro CLI           | `~/.kiro/skills/`                      |
| Kode               | `~/.kode/skills/`                      |
| MCPJam             | `~/.mcpjam/skills/`                    |
| Moltbot            | `~/.moltbot/skills/`                   |
| Mux                | `~/.mux/skills/`                       |
| Neovate            | `~/.neovate/skills/`                   |
| OpenClaude IDE     | `~/.openclaude/skills/`                |
| OpenCode           | `~/.config/opencode/skills/`           |
| OpenHands          | `~/.openhands/skills/`                 |
| Pi                 | `~/.pi/agent/skills/`                  |
| Pochi              | `~/.pochi/skills/`                     |
| Qoder              | `~/.qoder/skills/`                     |
| Qwen Code          | `~/.qwen/skills/`                      |
| Roo Code           | `~/.roo/skills/`                       |
| Trae               | `~/.trae/skills/`                      |
| Trae CN            | `~/.trae-cn/skills/`                   |
| Windsurf           | `~/.codeium/windsurf/skills/`          |
| Zencoder           | `~/.zencoder/skills/`                  |

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

## Alternative installers

If you'd rather not use the CodeRabbit CLI, you can install the skills directly via the Vercel Skills CLI:

```bash
npx skills add coderabbitai/skills
```

Claude Code users can also install this as a plugin from the official marketplace:

```bash
/plugin marketplace update
/plugin install coderabbit
```

This repository also includes Cursor marketplace metadata in
[`/.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json).

After publication, Cursor marketplace installs can use:

```text
/add-plugin coderabbit
```

Until then, you can install directly to Cursor with:

```bash
npx skills add coderabbitai/skills -a cursor
```

Note: skills installed via these alternative paths are not tracked in `~/.coderabbit/skills.json` and won't be kept up to date by future `coderabbit` CLI upgrades.

## Resources

- [CodeRabbit Documentation](https://coderabbit.ai/docs)
- [CodeRabbit CLI Guide](https://docs.coderabbit.ai/cli)
- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [Agent Skills Specification](https://agentskills.io/specification)

## License

MIT
