# Distribution Channels

Last verified: 2026-10-01; Claude directory row reverified 2026-11-12; published Codex package reverified 2026-11-11; tagged archive reverified for `v1.2.2`.

This file is the repository's operating inventory for where CodeRabbit skills and adjacent agent integrations are distributed. Public user-facing install guidance belongs in `README.md`; in-development and maintainer-only channels should stay here until they are ready to launch.

All active source manifests and skills share [`VERSION`](VERSION); see the
[version policy](docs/versioning.md). Versions below describe historical or
observed publication where stated. A source bump does not update those records.

## Channels

| Channel | Status | Source of truth | Notes |
| --- | --- | --- | --- |
| Claude MCP plugin | Source candidate; publication separate | Repository root on `main`, `.claude-plugin/plugin.json` | Remote MCP tools plus standalone CLI local reviews, with separate sign-ins. No automatic review hook or managed local runtime. Portal validation and publication remain separate. |
| Assembled MCP variants | Paused; not published | `packaging/mcp/` (assembler and launchers removed in 1.3.0; see git history at `f0629e0`) | Bundled/direct/Codex pilots can no longer be assembled from `main`. Codex hook assembly is blocked on verified server identity; direct packages require separate qualification. |
| Skills package (`npx skills add coderabbitai/skills`) | Live | `README.md`, `skills/` | Canonical multi-agent distribution path for 35+ skills-compatible agents. |
| Tagged GitHub release archive (`coderabbit skills`) | Live; `v1.2.2` | [Latest release](https://github.com/coderabbitai/skills/releases/tag/v1.2.2), `.github/workflows/release.yml`, [skills install docs](https://docs.coderabbit.ai/cli/skills) | Released from standalone maintenance commit `0b18e5b7c498f614cd5a496215525535a4338d96`. Archive/checksum verification and the CLI catalog passed for review, autofix, and configuration. `v1.2.1` was withdrawn from Latest after the CLI rejected missing configuration-skill version metadata. |
| Claude Code plugin marketplace | Live | `.claude-plugin/plugin.json`, `skills/`, `agents/` | Official marketplace source: `coderabbitai/skills`. Migration from the legacy `coderabbitai/claude-plugin` repository completed on 2026-05-01. |
| Claude directory (claude.ai, desktop, Cowork) | Live 1.2.0; 1.3.0 held | Existing `coderabbit` listing | Verified 2026-11-12: 1.2.0 serves, assembled 1.3.0 has an “Update adds hooks” policy hold; auto-publish is off. The existing root listing now follows the default branch (`main`); policy approval and publication remain separate. |
| Cursor native plugin marketplace | Repo-packaged, publication should be verified | `.cursor-plugin/plugin.json` | Repo contains marketplace manifest; treat public listing as separate verification work. |
| Gemini CLI native extension | Released source in `v1.2.2` | `gemini-extension.json`, `skills/`, `commands/coderabbit/review.toml`, `agents/` | Install the published tag using the [README instructions](README.md#gemini-cli-extension); verify gallery listing separately. |
| Antigravity App / CLI plugin | Existing Marketplace listing; current source in `VERSION` | Root `plugin.json`, `mcp_config.json`, `.antigravity-plugin/README.md`, shared `skills/` and `agents/` on `main` | The 1.3.0 source passed installed OAuth, account/usage/PR and CLI review checks on 2026-11-18. The 1.3.1 package puts setup in the shared skills directory for Marketplace ZIPs. Google's weekly crawler reads versioned changes on `main`. See [release and QA](docs/antigravity-release.md). |
| Connected Codex listing | Source candidate; publication unverified | [Connected package profiles](packaging/codex-connected/README.md) | Portable and native packages share five skills and the hosted five-scope connection. Compatible desktops can register the local CLI presenter during setup. |
| Codex plugin marketplace | Live code review; expanded source pending | Published `1.1.4` package; `.codex-plugin/plugin.json`, `skills/`, `assets/` | The published package verified 2026-11-11 contains only `skills/coderabbit-review/SKILL.md`, which runs local CLI review and reads NDJSON; it contains no autofix skill or PR-prompt heading reader. The current root manifest references the shared standalone skills; publishing that expanded package is separate from updating existing heading readers. |
| VS Code / Cursor / Windsurf IDE extension | Live, separate distribution | CodeRabbit IDE extension docs | Complements skills; not a replacement for `SKILL.md` installs. |
| GitHub Marketplace app (PR reviews) | Live, separate product channel | CodeRabbit GitHub Marketplace listing | Product distribution, not a skills install path. |

## CodeRabbit Secure availability

The source package includes `skills/coderabbit-secure/`. Claude and Antigravity
declare hosted MCP connections. A portable installation uses the host's
configured CodeRabbit server. The source change does not establish a tagged
release or marketplace publication. See the [connection guide](docs/mcp.md#coderabbit-secure).

## Configuration skill availability

The shared `skills/` directory and published [standalone `v1.2.2` archive](https://github.com/coderabbitai/skills/releases/tag/v1.2.2)
include `coderabbit-config`, alongside review and autofix. Source packages for
Claude, Cursor, Codex, Gemini, Antigravity, and the skills installer reference the
shared skill without a new command alias. Marketplace publication remains
channel-specific. The former MCP assembler is archived. Current configuration workflows use
the separately installed CLI and do not require MCP.
The CLI workflow is verified with official 0.9.3 and checks protocol support at
runtime.

## Maintenance checklist

- When README install text changes, verify this table still matches the recommended paths.
- When the release workflow or asset names change, update the tagged GitHub release archive row and its verification note.
- When a new marketplace manifest is added, record whether it is only packaged in-repo or publicly published.
- When the Gemini manifest or bundled components change, rerun `gemini extensions validate .`.
- When the Antigravity manifest or plugin schema changes, rerun `agy plugin validate .`.
- If a channel moves to another repository, keep the status here and link the new owner repo in the note.
- If a channel is deprecated, keep it in this file until all docs and install references are removed.
