# Codex package source

`codex/` preserves the existing Codex plugin from
[`coderabbitai/codex-plugin` at `8b9b6cc`](https://github.com/coderabbitai/codex-plugin/tree/8b9b6cc3eeba14adcc4b9a6dc1e8085d9035ef81/plugins/coderabbit).
Its package version remains `1.1.5`; this is independent of the portable skills
release version. The only payload change in the migration is the manifest's
`repository` URL, which now points to `coderabbitai/skills`.

## Build

From the repository root, with Python 3.9 or newer:

```bash
python3 scripts/build_codex_plugin.py --output /tmp/coderabbit-skills.zip
```

The ZIP contains the package contents at its root, including
`.codex-plugin/plugin.json`. Do not ZIP the entire repository for submission.
The exporter fixes file order, timestamps, and permissions for reproducible
comparisons in the same Python/zlib environment. `--source` can point to the
original `plugins/coderabbit` directory to build a comparison ZIP.

## Discovery and behavior boundaries

The Codex entrypoint is stored as `SKILL.md.source` and becomes `SKILL.md` only
inside the ZIP. The [generic skills installer](https://github.com/vercel-labs/skills/blob/main/src/skills.ts)
recursively discovers files named `SKILL.md`; a second entrypoint here would
introduce another review skill. Keep generated or extracted packages outside
the repository. The existing whole-repository release archive includes these
sources, but the Codex entrypoint is not a discoverable portable skill.

`skills/code-review` remains the portable skill. Codex keeps its existing
sandbox, authentication, session polling, output, and approval instructions.
This move does not reconcile those behavioral differences or alter Claude,
Cursor, Gemini, or Antigravity manifests. Future shared behavior changes should
check both entrypoints explicitly.

## Publication checkpoint

Building a ZIP does not publish it. Follow the
[OpenAI submission guide](https://developers.openai.com/plugins/deploy/submission)
when a new upload is approved, updating the existing listing rather than
creating another plugin. Do not retire the old repository until the cutover is
verified.

This migration deliberately retains two known submission gaps in the source:
its 51-character subtitle exceeds the 30-character submission limit, and its
32 x 32 composer icon is below the 48 x 48 minimum. Fix and validate those in a
separate publication-preparation change. Package comparison establishes source
parity, not portal acceptance or a live runtime test.
