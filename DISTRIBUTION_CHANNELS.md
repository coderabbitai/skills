# Distribution Channels

Last verified: 2026-10-01

This file is the repository's operating inventory for where CodeRabbit skills and adjacent agent integrations are distributed. Public user-facing install guidance belongs in `README.md`; in-development and maintainer-only channels should stay here until they are ready to launch.

## Channels

| Channel | Status | Source of truth | Notes |
| --- | --- | --- | --- |
| Skills package (`npx skills add coderabbitai/skills`) | Live | `README.md`, `skills/` | Canonical multi-agent distribution path for 35+ skills-compatible agents. |
| Tagged GitHub release archive (`coderabbit skills`) | Live; `v1.2.0` pending | `.github/workflows/release.yml`, [skills install docs](https://docs.coderabbit.ai/cli/skills) | CLI installs the latest published release after manifest and checksum verification. As of 2026-09-30, Latest is `v1.1.1`; publish `v1.2.0` to deliver the merged updates. |
| Claude Code plugin marketplace | Live | `.claude-plugin/plugin.json`, `skills/`, `agents/` | Official marketplace source: `coderabbitai/skills`. Migration from the legacy `coderabbitai/claude-plugin` repository completed on 2026-05-01. |
| Claude directory (claude.ai, desktop, Cowork) | Submission in progress | `.claude-plugin/plugin.json`, `skills/`, `agents/`, `README.md` | Submitted from the CodeRabbit claude.ai organization through the developer portal at claude.ai/directory/manage; tracks `main`. |
| Claude Code review mod | v0.1.0 candidate; not submitted | `mods/coderabbit/` | Separate executable mod for explicit local reviews. Requires Claude Code 2.1.289; directory acceptance must be verified before publication. |
| Cursor native plugin marketplace | Repo-packaged, publication should be verified | `.cursor-plugin/plugin.json` | Repo contains marketplace manifest; treat public listing as separate verification work. |
| Gemini CLI native extension | Repo-packaged, release pending | `gemini-extension.json`, `skills/`, `commands/coderabbit/review.toml`, `agents/` | Publish direct installation after `v1.2.0`; verify gallery listing separately. |
| Antigravity CLI native plugin | GitHub-installable | `plugin.json`, `skills/` | Install directly with `agy plugin install https://github.com/coderabbitai/skills`; treat marketplace publication as separate verification work. |
| Codex plugin marketplace | Live; native source added, upload pending | `.codex-plugin/plugin.json`, `skills/`, `assets/` | The root manifest uses the existing review and autofix skills at `1.2.0`. The portal still publishes `1.1.4`; merging does not update it. Native agent loading, runtime validation, and submission preparation remain separate follow-ups. |
| VS Code / Cursor / Windsurf IDE extension | Live, separate distribution | CodeRabbit IDE extension docs | Complements skills; not a replacement for `SKILL.md` installs. |
| GitHub Marketplace app (PR reviews) | Live, separate product channel | CodeRabbit GitHub Marketplace listing | Product distribution, not a skills install path. |

## Maintenance checklist

- When README install text changes, verify this table still matches the recommended paths.
- When the release workflow or asset names change, update the tagged GitHub release archive row and its verification note.
- When a new marketplace manifest is added, record whether it is only packaged in-repo or publicly published.
- When the Gemini manifest or bundled components change, rerun `gemini extensions validate .`.
- When the Antigravity manifest or plugin schema changes, rerun `agy plugin validate .`.
- If a channel moves to another repository, keep the status here and link the new owner repo in the note.
- If a channel is deprecated, keep it in this file until all docs and install references are removed.
