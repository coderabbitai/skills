# Changelog

All notable changes to this repository are documented in this file.

## Unreleased

### Added

- Added `name` frontmatter to the Claude Code `code-reviewer` subagent.
- Added a repository `.gitignore` for local Claude settings, virtualenvs, and
  dependency directories.

### Changed

- Reframed the README as the canonical home for CodeRabbit skills and plugin
  packaging across supported agents.
- Removed public README guidance for tagged release archives while that channel
  remains in development.
- Marked the tagged release archive channel as in development in
  `DISTRIBUTION_CHANNELS.md`.
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
