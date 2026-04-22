# Distribution Channels

Last verified: 2026-04-22

This file is the repository's operating inventory for where CodeRabbit skills and adjacent agent integrations are distributed. Update it whenever a channel is launched, deprecated, moved, or repackaged.

## Channels

| Channel | Status | Source of truth | Notes |
| --- | --- | --- | --- |
| Skills package (`npx skills add coderabbitai/skills`) | Live | `README.md`, `skills/` | Canonical multi-agent distribution path for 35+ skills-compatible agents. |
| Tagged GitHub release archive for binary installers | Repo-configured, publish on `v*` tag push | `.github/workflows/release.yml`, `README.md` | Publishes a versioned tarball, SHA-256 file, and release manifest; consumers should pin tags and reject checksum mismatch. |
| Claude Code plugin marketplace | Live | `.claude-plugin/plugin.json`, `commands/`, `agents/` | In-repo packaging is active and documented. |
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
