# Distribution Channels

Last verified: 2026-04-28

This file is the repository's operating inventory for where CodeRabbit skills and adjacent agent integrations are distributed. Public user-facing install guidance belongs in `README.md`; in-development and maintainer-only channels should stay here until they are ready to launch.

## Channels

| Channel | Status | Source of truth | Notes |
| --- | --- | --- | --- |
| Skills package (`npx skills add coderabbitai/skills`) | Live | `README.md`, `skills/` | Canonical multi-agent distribution path for 35+ skills-compatible agents. |
| Tagged GitHub release archive for binary installers | In development, not user-facing | `.github/workflows/release.yml` | Workflow publishes a versioned tarball, SHA-256 file, and release manifest on `v*` tags, but this channel is not part of public install guidance yet. |
| Claude Code plugin marketplace | Live, source migration pending | `.claude-plugin/plugin.json`, `commands/`, `agents/` | In-repo packaging is active; official marketplace source is being moved from `coderabbitai/claude-plugin` to this repository. |
| Cursor native plugin marketplace | Repo-packaged, publication should be verified | `.cursor-plugin/plugin.json` | Repo contains marketplace manifest; treat public listing as separate verification work. |
| Codex plugin marketplace | Live, separate repo | CodeRabbit docs + `coderabbitai/codex-plugin` | Not packaged from this repository today. |
| VS Code / Cursor / Windsurf IDE extension | Live, separate distribution | CodeRabbit IDE extension docs | Complements skills; not a replacement for `SKILL.md` installs. |
| GitHub Marketplace app (PR reviews) | Live, separate product channel | CodeRabbit GitHub Marketplace listing | Product distribution, not a skills install path. |

## Maintenance checklist

- When README install text changes, verify this table still matches the recommended paths.
- When the release workflow or asset names change, update the binary-installer row and its verification note.
- When a new marketplace manifest is added, record whether it is only packaged in-repo or publicly published.
- If a channel moves to another repository, keep the status here and link the new owner repo in the note.
- If a channel is deprecated, keep it in this file until all docs and install references are removed.
