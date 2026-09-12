# Contributing

Thanks for helping improve CodeRabbit's public agent skills and plugin packaging.

## Before You Start

Open an issue before proposing a new skill, a new distribution channel, or a
behavioral change that affects several supported agents. Small corrections can
go directly to a pull request.

Report security vulnerabilities through GitHub's private
[Report a vulnerability](https://github.com/coderabbitai/skills/security/advisories/new)
form, not through a public issue.

## Repository Structure

- `skills/` contains the canonical portable skills.
- `commands/` and `agents/` contain native command and agent packaging that must
  remain behaviorally aligned with the corresponding canonical skill.
- `.claude-plugin/`, `.cursor-plugin/`, `gemini-extension.json`, and
  `plugin.json` describe host-specific packaging.
- `DISTRIBUTION_CHANNELS.md` records which channels are live, packaged, or still
  in development.

## Designing Agent Guidance

Follow the [Agent Skills specification](https://agentskills.io/specification)
and the [AGENTS.md open format](https://agents.md/), plus the current public
documentation for every agent or plugin host named by the change.

- Keep `SKILL.md` focused on activation, routing, domain context, and workflow
  framing.
- Use progressive disclosure: move details needed only in some workflows into
  focused files under `references/` and say when to read each one.
- Put repeatable deterministic operations in `scripts/` or tools when practical.
- Keep referenced files one level from `SKILL.md` when possible, and verify that
  every referenced file, command, option, and tool exists.
- Explain host-specific behavior explicitly instead of assuming every agent has
  the same filesystem, sandbox, authentication, or command model.
- Update every affected native command, agent, manifest, README section, and
  distribution record in the same pull request.

## Validation

Run the checks that match your change:

```bash
git diff --check
jq empty .claude-plugin/plugin.json .cursor-plugin/plugin.json gemini-extension.json plugin.json
```

When changing `.coderabbit.yaml`, also run:

```bash
coderabbit config validate .coderabbit.yaml
```

When changing host-specific packaging, run its official validator when
available, including `gemini extensions validate .` or
`agy plugin validate .`.

Include the exact commands and results in the pull-request description. If a
validator is unavailable, state that clearly instead of claiming it passed.

## Pull Requests

- Keep each pull request centered on one reviewable outcome.
- Link the issue or public authoritative documentation that establishes the
  behavior being changed.
- Call out every supported distribution surface affected by the change.
- Do not include credentials, private links, private configuration, or private
  operational details.
- Resolve review comments and keep the branch current until required checks and
  maintainer approval pass on the latest commit.

By contributing, you agree that your contribution is licensed under this
repository's [MIT License](LICENSE).
