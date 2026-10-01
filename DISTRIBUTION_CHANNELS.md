# Distribution Channels

Last verified: 2026-10-01

This file is the repository's operating inventory for where CodeRabbit skills and adjacent agent integrations are distributed. Public user-facing install guidance belongs in `README.md`; in-development and maintainer-only channels should stay here until they are ready to launch.

## Channels

| Channel | Status | Source of truth | Notes |
| --- | --- | --- | --- |
| Skills package (`npx skills add coderabbitai/skills`) | Live | `README.md`, `skills/` | Canonical multi-agent distribution path for 35+ skills-compatible agents. |
| Tagged GitHub release archive (`coderabbit skills`) | Live; `v1.2.0` pending | `.github/workflows/release.yml`, [skills install docs](https://docs.coderabbit.ai/cli/skills) | CLI installs the latest published release after manifest and checksum verification. As of 2026-09-30, Latest is `v1.1.1`; publish `v1.2.0` to deliver the merged updates. |
| Claude Code plugin marketplace | Live | `.claude-plugin/plugin.json`, `commands/`, `agents/` | Official marketplace source: `coderabbitai/skills`. Migration from the legacy `coderabbitai/claude-plugin` repository completed on 2026-05-01. |
| Claude directory (claude.ai, desktop, Cowork) | Submission in progress | `.claude-plugin/plugin.json`, `README.md` | Submitted from the CodeRabbit claude.ai organization through the developer portal at claude.ai/directory/manage; tracks `main`. |
| Cursor native plugin marketplace | Repo-packaged, publication should be verified | `.cursor-plugin/plugin.json` | Repo contains marketplace manifest; treat public listing as separate verification work. |
| Gemini CLI native extension | Repo-packaged, release pending | `gemini-extension.json`, `skills/`, `commands/coderabbit/review.toml`, `agents/` | Publish direct installation after `v1.2.0`; verify gallery listing separately. |
| Antigravity CLI native plugin | GitHub-installable | `plugin.json`, `skills/` | Install directly with `agy plugin install https://github.com/coderabbitai/skills`; treat marketplace publication as separate verification work. |
| Codex plugin marketplace | Live; native integration repo-packaged, upload pending | `.codex-plugin/plugin.json`, `skills/`, `assets/`; [published listing](https://chatgpt.com/plugins/plugins~Plugin_4a6d3426bf5081918d5d976ff7e5aef5) | Portal currently publishes `1.1.4`. The repository integrates Codex with the shared `code-review` and `autofix` skills at `1.2.0`. Merging does not update the listing; see the submission checkpoint below. |
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

## Codex submission

Codex follows the same repository layout as the other native integrations:
`.codex-plugin/plugin.json` references `./skills/`. The listing logo lives in
`assets/`; skill icons live in `skills/code-review/assets/` so standalone skill
installs retain their UI assets. There is one shared `code-review` skill and one shared `autofix` skill.
Codex-specific execution and reactive authentication instructions are a reference
inside `skills/code-review`; other agents keep their existing pre-review auth
check. The shared output reference preserves completion, partial coverage, and
spending-consent rules from the former Codex skill.

The migration source is
[`coderabbitai/codex-plugin` at `8b9b6cc`](https://github.com/coderabbitai/codex-plugin/tree/8b9b6cc3eeba14adcc4b9a6dc1e8085d9035ef81/plugins/coderabbit).
The integrated ZIP intentionally differs: `coderabbit-review` becomes the
canonical `code-review` directory, existing `autofix` is included, shared CLI
workflows remain available, and the manifest version aligns with this
repository's `1.2.0`. Existing artwork is preserved. No separate package source
or filename transformation is maintained.

After committing the reviewed changes, export directly from the same source:

```bash
git archive --format=zip --output=/tmp/coderabbit-codex.zip HEAD \
  .codex-plugin skills assets LICENSE
```

The ZIP root contains the Codex manifest, shared skills, their references, and
assets. Compare this ZIP with the original repository's ZIP before upload.
This command excludes other host manifests and maintainer files; it does not
publish anything or create a new source tree.

Before an approved upload, shorten the retained 51-character subtitle to at
most 30 characters and replace the retained 32 x 32 composer icon with one at
least 48 x 48. Validate both skills in Codex and use the
[OpenAI submission guide](https://developers.openai.com/plugins/deploy/submission)
to update the existing listing. The original repository and published listing
remain in place until the cutover is verified.
