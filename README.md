# CodeRabbit Skills and Plugins

[![Standalone release](https://img.shields.io/badge/standalone-1.2.2-blue)](https://github.com/coderabbitai/skills/releases/tag/v1.2.2)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Agents](https://img.shields.io/badge/works_with-35%2B_agents-brightgreen)](#supported-agents)

The canonical home for CodeRabbit's agent-native skills and plugin packaging.
Use it to install AI-powered code review into 35+ coding agents, Gemini CLI,
Antigravity CLI, Claude Code, Cursor, and other supported agent environments.

CodeRabbit detects bugs, security issues, and quality risks before you merge.

## Quickstart

**Antigravity 1.3.2 candidate:** [install the local source candidate](#antigravity-cli-plugin),
then ask **“Set up CodeRabbit”** to connect remote tools and
check local review readiness with the native `coderabbit-setup` skill.
Authenticate the hosted connection through Antigravity's CodeRabbit account
settings, then ask **“Check my CodeRabbit connection and selected organization.”**
See the [Antigravity setup guide](.antigravity-plugin/README.md).

**Claude source package (1.3.4):** run `/coderabbit:setup` for the same two
readiness checks. See the [Claude MCP setup guide](docs/mcp.md). For a published
marketplace copy, follow its [integration guide](https://docs.coderabbit.ai/cli/claude-code-integration).

Both packages connect remote tools through MCP and use the standalone
CodeRabbit CLI for local reviews. **MCP and CLI sign-ins are separate.** Reuse
an existing CLI installation and login, then ask **“Review my uncommitted
changes. Review only; do not edit.”** A connected CodeRabbit MCP server can
show local findings and PR status inline in Antigravity, Claude and Codex.
Hosts without Apps support show text. There is no automatic review hook;
local reviews do not reserve MCP reviews or pass review handoffs through shell
commands. A hosted connector alone cannot collect local files.

The Antigravity connection is in `mcp_config.json`; Claude's is in its own
manifest. Other host packages retain their documented workflows. See
[distribution status](DISTRIBUTION_CHANNELS.md) for publication: source
availability and matching version numbers do not establish marketplace parity.

**Released CLI integration:** install the CodeRabbit CLI via the [CLI docs](https://docs.coderabbit.ai/cli),
then tell your agent: **“Review my code.”** If sign-in is needed, the agent
hands off the CLI's browser login to you.

## Installation

The standalone integration paths below remain available. Native MCP package
availability follows each host's release and marketplace process.

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

CodeRabbit is also listed in the Claude directory. Add it from
**Customize > Plugins > Discover** in
claude.ai or the Claude desktop app, and it will sync to Claude Code sessions
where you're signed in with the same claude.ai account. If you install from
both places, Claude Code loads the marketplace copy.

For the MCP candidate from this source, use `/coderabbit:setup` and the
[MCP setup guide](docs/mcp.md). Published marketplace copies may still use the
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

#### Gemini CLI Extension

Gemini CLI users can install the native extension from the published
[standalone `v1.2.2` tag](https://github.com/coderabbitai/skills/releases/tag/v1.2.2):

```bash
gemini extensions install https://github.com/coderabbitai/skills --ref v1.2.2
gemini extensions list
```

The repository-root [`gemini-extension.json`](gemini-extension.json) packages
the portable skills, `/coderabbit:review` command, and both subagents.
This native extension is separate from the generic skills-installer path above.

#### Antigravity CLI Plugin

Install the published plugin from **Customizations > Marketplace > CodeRabbit**
in Antigravity, or use `agy plugin install coderabbit` in the CLI.
To test the source candidate directly from this repository:

```bash
agy plugin install /absolute/path/to/skills
agy plugin list
```

The source candidate includes hosted MCP with native OAuth discovery through
[`mcp_config.json`](mcp_config.json), four shared skills and two agents.
Ask “Set up CodeRabbit” to use `coderabbit-setup` and
check connection and review readiness. Local reviews
still require the separately installed and authenticated CodeRabbit CLI.
See the [Antigravity setup guide](.antigravity-plugin/README.md).
Google's weekly crawler publishes versioned updates from `main`; source
readiness does not establish the version currently served by the Marketplace.

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
| `.claude-plugin/` | Native Claude manifest with its remote MCP connection; no review hook. |
| `commands/` | Gemini review command and Claude setup command; Antigravity uses native skills. |
| `agents/` | `code-reviewer` and `autofix` subagents shipped to Claude Code, Gemini CLI, and Antigravity CLI. |
| `.cursor-plugin/` | Cursor marketplace metadata. |
| `.codex-plugin/` | Codex metadata referencing the shared skills. |
| `gemini-extension.json` | Gemini CLI extension manifest. |
| `plugin.json` | Antigravity CLI plugin manifest. |
| `mcp_config.json` | Antigravity's hosted MCP connection with native OAuth discovery. |
| `.antigravity-plugin/README.md` | Antigravity Marketplace overview and setup guidance. |
| `skills/coderabbit-setup/` | Shared setup for local CLI reviews and the host's configured MCP connection. |
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

For standalone installs, the agent will automatically:

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

### [coderabbit-config](skills/coderabbit-config/SKILL.md)

Create, update, or validate repository configuration through the official CLI.
Ask “Set up CodeRabbit configuration”, “Make CodeRabbit reviews more thorough”,
or “Validate .coderabbit.yaml”. Where supported, invoke `$coderabbit-config` or
`/coderabbit-config`; the Claude plugin uses `/coderabbit:coderabbit-config`.
The distinct name leaves the host's `/config` command available.

Requires an official CLI supporting config protocol v2 (verified with 0.9.3).
The CLI owns defaults, schema checks, previews, and writes. The skill supports
review-style changes and the CLI's guided path settings; unsupported settings
remain a CLI capability gap. Missing commands require an upgrade, never an
agent-side YAML editor. Validation alone does not change files; saves require
approval of the preview. Configuration does not require login or run a review.

This skill is included in the source package and the published
[standalone `v1.2.2` archive](https://github.com/coderabbitai/skills/releases/tag/v1.2.2).
Marketplace caches require their normal publication update to deliver it.

## Plugin Components

The native Claude candidate combines a remote MCP connection and setup command
with standalone CLI review and configuration skills. It registers no hooks and
supplies no managed review runtime. Independently assembled MCP variants have
separate qualification requirements.

### Claude Code

- Skills: `code-review`, `autofix`, and `coderabbit-config`. Run them as
  `/coderabbit:code-review`, `/coderabbit:autofix`, and
  `/coderabbit:coderabbit-config`, or ask in plain language.
- Subagents: `code-reviewer` runs a CodeRabbit review in its own context, and
  `autofix` collects and checks unresolved CodeRabbit review threads
  and returns a fix plan without editing anything. Mention them as
  `@agent-coderabbit:code-reviewer` and `@agent-coderabbit:autofix`.
- Manifest: `.claude-plugin/plugin.json`

The Claude plugin adds `/coderabbit:setup` for MCP connection and standalone CLI readiness.
For review, use `/coderabbit:code-review` instead of the earlier
`/coderabbit:coderabbit-review`.

Local review uses the user's installed and authenticated CodeRabbit CLI and
requires host execution permission and access to the intended Git working tree.
MCP sign-in does not authenticate the CLI. A host without local execution can
use remote tools but cannot run a local review. No hook trust is needed.

### Cursor

- Marketplace manifest: `.cursor-plugin/plugin.json`
- Skills source: `skills/`

### Antigravity CLI

For sandboxed CLI sessions that cannot find or execute an installed CodeRabbit
CLI, follow the [scoped executable-access recovery](skills/code-review/references/antigravity-sandbox.md).
It keeps diagnostics sandboxed and retains per-command host approval for auth and review.

- Native plugin manifest: `plugin.json`
- Hosted MCP: `mcp_config.json`; native browser OAuth, separate from CLI login
- Skills: all four are discovered under `skills/`, including `coderabbit-setup`
- Review: ask “Review my changes” to activate `code-review`; do not rely on the legacy converted `/coderabbit:review` command
- Subagents: `agents/code-reviewer.md`, `agents/autofix.md`

The [Google-specific overview](.antigravity-plugin/README.md) covers connection,
prerequisites and example prompts. Maintainers should follow the
[Antigravity release and QA guide](docs/antigravity-release.md).

### Gemini CLI

- Native extension manifest: `gemini-extension.json`
- Skills source: `skills/`
- Slash command: `/coderabbit:review` (`commands/coderabbit/review.toml`)
- Subagents: `agents/code-reviewer.md`, `agents/autofix.md`

## Data and Privacy

The native Claude plugin contains four portable skills, a setup command, two
subagents and a remote MCP connection. It declares no automatic hooks.

- **Local commands**: reviews use the user's installed CodeRabbit CLI. The
  `autofix` skill uses GitHub CLI (`gh`) to read review threads and, when
  authorized, post or create a pull request. The `autofix` subagent only reads.
- **Data sent**: local reviews send selected changes and required repository
  context to CodeRabbit. MCP tools exchange requested account and repository
  data with CodeRabbit; `autofix` exchanges pull-request data with GitHub.
  Setup alone does not authorize an upload or start a review.
- **Credentials**: Claude manages connector OAuth. The standalone CLI and `gh`
  manage their own logins. The plugin does not read Claude's OAuth store or
  copy credentials between the connector and the CLI.
- **Policy**: see the [CodeRabbit Privacy Policy](https://www.coderabbit.ai/privacy-policy)
  for handling and retention, or contact <support@coderabbit.ai>.

The `coderabbit-config` skill runs local CLI configuration commands. The CLI
fetches the public configuration schema over HTTPS and validates YAML locally;
it does not submit repository code for review. Approved saves change the local
configuration file, with commit and push left to the requested workflow.

## Resources

- [Documentation](https://docs.coderabbit.ai/cli)
- [Support](https://docs.coderabbit.ai/support)
- [Privacy Policy](https://www.coderabbit.ai/privacy-policy)
- [Terms of Service](https://www.coderabbit.ai/legal/terms-of-service)
- [CodeRabbit Documentation](https://coderabbit.ai/docs)
- [Vercel Skills CLI](https://github.com/vercel-labs/skills)
- [Agent Skills Specification](https://agentskills.io/specification)
- [Gemini CLI Extension Documentation](https://geminicli.com/docs/extensions/reference/)
- [Antigravity CLI Plugin Documentation](https://antigravity.google/docs/cli-plugins)

## License

MIT
