# Changelog

All notable changes to this repository are documented in this file.

## [1.2.0] - Unreleased

### Added

- The review skill and `code-reviewer` agent now say how long a CodeRabbit
  review takes and to run it in the background or with a timeout of at least
  15 minutes, and how to handle an `interrupted` review. Short default tool
  timeouts were stopping most reviews before they finished.
- Agent-started login now uses `auth login --agent`, which signs in through the
  browser callback without a terminal prompt.
- When the CLI reports an update, the review skill tells the user to run
  `coderabbit update`.

- Added a Claude directory listing icon and a README "Data and Privacy"
  section that discloses what the plugin runs and sends.
- Added the read-only `autofix` subagent, which collects and checks
  unresolved CodeRabbit review threads and returns a fix plan for the `autofix`
  skill to apply with per-change approval.
- Set the Claude plugin's `author.name` to "CodeRabbit".
- Added `displayName` to `.claude-plugin/plugin.json` and README links for
  documentation, support, privacy policy, and terms of service, which the
  Claude directory shows on the listing.
- Added public contribution guidance, structured issue forms, and a pull-request
  template for agent-skill and integration changes.
- Added a self-contained, assertive repository-level CodeRabbit policy with
  draft and continuous incremental reviews, a strict request-changes workflow,
  blocking pre-merge checks, public-repository knowledge boundaries, and focused
  guidance for skills, native packaging, and public documentation.
- Added native Gemini CLI extension packaging via `gemini-extension.json`,
  including the `/coderabbit:review` command and existing portable skills.
- Added native Antigravity CLI plugin packaging via the repository-root
  `plugin.json` manifest, with direct GitHub installation guidance.
- Documented CodeRabbit CLI `--dir <path>` support for directory-scoped
  reviews in the review skill and Claude Code review helpers.
- Added `name` frontmatter to the Claude Code `code-reviewer` subagent.
- Added a repository `.gitignore` for local Claude settings, virtualenvs, and
  dependency directories.

### Changed

- The Claude plugin now ships the `code-review` and `autofix` skills and the
  `code-reviewer` and `autofix` subagents. It no longer includes the
  `/coderabbit:coderabbit-review` command, because skills supersede commands
  in Claude; run `/coderabbit:code-review` instead. Gemini CLI and Antigravity
  CLI keep their review commands.
- Removed the duplicate Markdown review command `commands/coderabbit-review.md`.
  Antigravity CLI and Gemini CLI both use `/coderabbit:review` from
  `commands/coderabbit/review.toml`, and the Claude manifest no longer needs a
  `commands` key to hide it.
- Rewrote the `code-reviewer` subagent description so Claude knows when to
  delegate to it.
- Hardened review authentication with trusted CLI paths, command-scoped host
  permissions, and one bounded retry for pre-review sandbox auth failures.

- Updated review guidance to use the public `--committed` and `--uncommitted`
  selectors, allow `--dir` paths inside a Git working tree, and rely on the
  review command's built-in authentication flow. Documented untracked-file scope,
  NDJSON completion and severities, saved prompts, and current configuration and
  account-command contracts.
- Aligned the shared code-review subagent metadata with Gemini CLI's schema.
- Removed alternate detailed-output guidance so review agents use `--agent`
  exclusively.
- Reframed the README as the canonical home for CodeRabbit skills and plugin
  packaging across supported agents.
- Aligned Claude Code and Cursor plugin versions with the planned `1.2.0`
  release and Gemini CLI manifest.
- Recorded tagged release archives as the live source for `coderabbit skills`;
  publishing `v1.2.0` is still required to deliver these changes through the CLI.
- Quoted Claude Code command frontmatter values so standard YAML parsers can
  validate them.

## [1.1.1] - 2026-04-22

### Added

- GitHub release workflow that builds a tagged source archive, SHA-256 checksum,
  and `release-manifest.json` for binary consumers.

### Changed

- Documented the tag-pinned, checksum-verified install contract for binary
  installers in `README.md`.
- Added the tagged release archive channel to `DISTRIBUTION_CHANNELS.md`.

## [1.1.0] - 2026-04-21

### Added

- Claude Code plugin packaging in this repository via `.claude-plugin/plugin.json`.
- In-repo `agents/code-reviewer.md` component for Claude Code.
- In-repo `commands/coderabbit-review.md` component for Claude Code.
- Cursor marketplace packaging via `.cursor-plugin/plugin.json`.
- Official CodeRabbit brand asset at `assets/coderabbit-logomark.svg` for marketplace display.
- Claude Code and Cursor plugin installation notes in `README.md`.

### Changed

- Restored the Claude plugin manifest version to `1.1.0` after repo consolidation.
- Updated Claude plugin command and agent docs after moving them into this repository.
- Updated `skills/code-review` to use the CodeRabbit CLI `--agent` flag instead of the deprecated `--prompt-only` flag, and documented the CLI version requirement.
- Simplified `README.md` install guidance so the CLI docs are the primary path, while keeping short links for skills installer, Claude Code, Cursor, and Codex installation flows.

## [1.0.0] - 2026-01-30

### Added

- Initial `code-review` skill release for multi-agent CodeRabbit reviews.
- Repository README, MIT license, and cross-agent installation guidance.
- `autofix` skill for unresolved CodeRabbit GitHub review threads.
- README documentation for the `autofix` workflow.

### Changed

- Hardened installation guidance to point users to the official CLI source instead of shell-piped install commands.
- Expanded `skills/code-review` security guidance around trusted installation, secrets in diffs, token handling, and untrusted review output.
- Refined the `code-review` skill description and documentation for clearer agent use.
