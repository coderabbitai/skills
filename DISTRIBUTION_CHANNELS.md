# Distribution Channels

Last verified: 2026-10-01; Claude directory row reverified 2026-11-12; published Codex package reverified 2026-11-11.

This file is the repository's operating inventory for where CodeRabbit skills and adjacent agent integrations are distributed. Public user-facing install guidance belongs in `README.md`; in-development and maintainer-only channels should stay here until they are ready to launch.

## Channels

| Channel | Status | Source of truth | Notes |
| --- | --- | --- | --- |
| Claude MCP plugin | 1.3.1 source candidate; not published | Repository root on `main`, `.claude-plugin/plugin.json`, `cli.json`, `runtime/` | Complete native Claude package; no distribution branch required. Local review uses its plugin-qualified hook and pinned CLI. Explicit CLI-only and other-host routes remain separate. Portal approval, channel qualification and publication are separate. |
| Assembled MCP variants | Development; not published | `scripts/assemble-plugin.py`, `packaging/mcp/` | Explicit bundled/direct/Codex pilots remain available. Codex hook assembly is blocked on verified server identity; direct packages require separate qualification. |
| Skills package (`npx skills add coderabbitai/skills`) | Live | `README.md`, `skills/` | Canonical multi-agent distribution path for 35+ skills-compatible agents. |
| Tagged GitHub release archive (`coderabbit skills`) | Live; `v1.2.1` pending | `.github/workflows/release.yml`, [skills install docs](https://docs.coderabbit.ai/cli/skills) | CLI installs the latest published release after manifest and checksum verification. As of 2026-11-11, Latest is `v1.1.1`; publish `v1.2.1` to deliver the compatible autofix reader and merged standalone updates. |
| Claude Code plugin marketplace | Live | `.claude-plugin/plugin.json`, `skills/`, `agents/` | Official marketplace source: `coderabbitai/skills`. Migration from the legacy `coderabbitai/claude-plugin` repository completed on 2026-05-01. |
| Claude directory (claude.ai, desktop, Cowork) | Live 1.2.0; 1.3.0 held | Existing `coderabbit` listing | Verified 2026-11-12: 1.2.0 serves, assembled 1.3.0 has an “Update adds hooks” policy hold; auto-publish is off. The connected push webhook currently follows the temporary distribution branch. Switch the existing root listing to `main` after the native 1.3.1 package merges; policy approval and publication remain separate. |
| Claude Code review mod | v0.1.0 candidate; not published | `mods/coderabbit/` | Separate executable mod for explicit local reviews in the terminal and Local Code sessions in Claude Desktop. Terminal validation uses Claude Code 2.1.289; directory acceptance must be verified before publication. |
| Cursor native plugin marketplace | Repo-packaged, publication should be verified | `.cursor-plugin/plugin.json` | Repo contains marketplace manifest; treat public listing as separate verification work. |
| Gemini CLI native extension | Repo-packaged, release pending | `gemini-extension.json`, `skills/`, `commands/coderabbit/review.toml`, `agents/` | Publish direct installation after `v1.2.1`; verify gallery listing separately. |
| Antigravity CLI native plugin | GitHub-installable | `plugin.json`, `skills/` | Install directly with `agy plugin install https://github.com/coderabbitai/skills`; treat marketplace publication as separate verification work. |
| Codex plugin marketplace | Live code review; expanded source pending | Published `1.1.4` package; `.codex-plugin/plugin.json`, `skills/`, `assets/` | The published package verified 2026-11-11 contains only `skills/coderabbit-review/SKILL.md`, which runs local CLI review and reads NDJSON; it contains no autofix skill or PR-prompt heading reader. The root `1.2.1` manifest references the shared standalone skills; publishing that expanded package is separate from updating existing heading readers. |
| VS Code / Cursor / Windsurf IDE extension | Live, separate distribution | CodeRabbit IDE extension docs | Complements skills; not a replacement for `SKILL.md` installs. |
| GitHub Marketplace app (PR reviews) | Live, separate product channel | CodeRabbit GitHub Marketplace listing | Product distribution, not a skills install path. |

## Configuration skill availability

The shared `skills/` directory now includes `coderabbit-config`, alongside review
and autofix. Directory-based Claude, Cursor, Codex, Gemini, Antigravity, skills
installer, and release-archive packaging includes it without a new command
alias. This is source availability, not confirmation of marketplace or tagged
release publication. The MCP assembler also carries it through; configuration
uses the managed CLI when that package supplies one and does not require MCP.
The CLI workflow is verified with official 0.9.3 and checks protocol support at
runtime. The separate review mod does not bundle configuration skills.

## Maintenance checklist

- When README install text changes, verify this table still matches the recommended paths.
- When the release workflow or asset names change, update the tagged GitHub release archive row and its verification note.
- When a new marketplace manifest is added, record whether it is only packaged in-repo or publicly published.
- When the Gemini manifest or bundled components change, rerun `gemini extensions validate .`.
- When the Antigravity manifest or plugin schema changes, rerun `agy plugin validate .`.
- If a channel moves to another repository, keep the status here and link the new owner repo in the note.
- If a channel is deprecated, keep it in this file until all docs and install references are removed.
