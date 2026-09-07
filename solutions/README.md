# Opt-in assisted onboarding

`onboard`, `config`, and `connect` are optional assisted-engagement skills, not
part of ordinary skills discovery, native plugins, or the CodeRabbit CLI's
default skill release archive. Install only a skill the user explicitly asks
for, using its exact repository path and `--skill` name. See the repository's
[distribution guide](../DISTRIBUTION_CHANNELS.md) for installation commands.

## CLI prerequisite

Use an engagement-approved CLI candidate that implements the guided
`coderabbit config` flow, human-driven `--detailed` mode, and configuration
protocol v1. Record the candidate version and build provenance; do not assume
the latest public release supports these operations.

```bash
coderabbit --version
coderabbit config --help
coderabbit config inspect --help
coderabbit config apply --help
coderabbit config validate --help
```

On an existing YAML fixture, `inspect --json` must report `protocolVersion: 1`
and a base hash. On a new repository, it must identify guided creation as
required. Missing capabilities are a candidate blocker, not permission for an
agent-authored fallback. Standard and both human-driven lanes require a real
interactive terminal; an agent must leave choices to the human.

## Four acceptance lanes

Use disposable repositories and the approved candidate. Exercise each lane
with both a new repository and an existing sparse YAML file containing comments,
an explicit parent/inheritance setting, and an unrelated non-default setting.
Do not submit reviews, install host skills, authorize integrations, or modify
product settings as part of these checks.

| Lane | Entry point | Required observation |
| --- | --- | --- |
| Standard `/config` | Invoke `$config` and choose Standard. | Opens `coderabbit config` in a PTY; the human owns source/style choices and preview approval. Preserves parent configuration unless the human deliberately changes it. |
| Detailed `/config` | Invoke `$config` and choose Detailed. Supply a few explicit preferences upfront. | Considers the detailed sections without re-asking settled choices; asks only material unknowns, at most three together. Uses inspect → proposal → validate → hash-checked dry-run → one approval → exact apply → re-inspect. |
| Human-driven Standard | Run `coderabbit config` directly. | Completes the quick guided flow and preview without agent-authored YAML. Existing parent/inheritance behavior is preserved unless explicitly changed. |
| Human-driven Detailed | Run `coderabbit config --detailed` directly. | The human drives the CLI's core-settings wizard. This is not the agent's schema-wide Detailed discovery workflow. |

For new repositories, both skill lanes must let the guided CLI check central
configuration and create the initial file before any agent proposal. Re-inspect
after creation. Without a PTY, provide the exact human command and stop. If the
guided flow leaves no active local file, do not proceed to apply. For existing
YAML, preserve comments, unrelated settings, and sparse inheritance; never
materialize defaults or a resolved configuration.

Additional failure cases:

- Valid YAML with a schema-invalid value: `/onboard` must run validation and
  report `Needs action`, even when inspection returns `ok: true`.
- Install only `/connect`, then request repository integration settings with no
  local YAML: use guided creation first; never propose an `apply --base none`.
- Change the repository YAML after a Detailed dry-run: the old-hash apply must
  fail without replacing the changed file. Re-inspect, rebase, and obtain fresh
  approval for the revised proposal.
- TypeScript, delegated, symlinked, or ambiguous authority: no local apply.
- No supported connection-status response: `/connect` reports `Unknown` or
  `Configured, verification pending`, not a completed live connection.

Record the candidate version/build, fixture, lane, exact commands, observed
exit codes, before/after diff, and pass/fail or blocker. A passing packaging
check below does not establish that these interactive lanes passed.

## Repeatable packaging checks

From the repository root:

```bash
node --test solutions/tests/distribution.test.mjs
git diff --check
```

The test checks the current default source directory and the committed `HEAD`
archive used by release packaging. Re-run after committing packaging changes.
It does not install skills or call the network.

With an already available Skills CLI, use local listing only:

```bash
DISABLE_TELEMETRY=1 skills add . --list
DISABLE_TELEMETRY=1 skills add . --all --list
DISABLE_TELEMETRY=1 skills add ./solutions/onboard --skill onboard --list
DISABLE_TELEMETRY=1 skills add ./solutions/config --skill config --list
DISABLE_TELEMETRY=1 skills add ./solutions/connect --skill connect --list
```

The first two must expose only `autofix` and `code-review`; each direct path
must expose only its named skill. If no Skills CLI is already available, record
that limitation rather than installing it on the host just for this check.
