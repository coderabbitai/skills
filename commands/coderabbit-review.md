---
description: Run CodeRabbit AI code review on your changes
argument-hint: "[type] [--base <branch>] [--dir <path>]"
allowed-tools: "Bash(git:*)"
---

# CodeRabbit Code Review

Run an AI-powered code review using CodeRabbit.

## Context

- Current directory: !`pwd`
- Git repo: !`git rev-parse --is-inside-work-tree 2>/dev/null && echo "Yes" || echo "No"`
- Branch: !`git branch --show-current 2>/dev/null || echo "detached HEAD"`
- Has changes: !`git status --porcelain 2>/dev/null | head -1 | grep -q . && echo "Yes" || echo "No"`

## Instructions

Review code based on: **$ARGUMENTS**

### Prerequisites Check

Resolve the host-installed `coderabbit` executable from the user's normal host
environment and use its canonical absolute path rather than an alias or
function. Reject the executable if its path or resolved target is inside the
repository or workspace. Do not request host or elevated execution for path resolution,
`--version`, or `--help`; keep those diagnostics sandboxed when a sandbox is
present.

Run:

```bash
/absolute/path/to/coderabbit --version
```

**If CLI not found**, tell user:
> CodeRabbit CLI is not installed. Install it from the official docs:
>
> <https://www.coderabbit.ai/cli>
>
> Prefer a package manager or a verified binary, then restart your shell and try again.

Run exactly this authentication check from the same authoritative execution
context that will run the review:

```bash
/absolute/path/to/coderabbit auth status --agent
```

For a local sandboxed agent, use command-scoped host execution. In Codex, set
`sandbox_permissions: require_escalated` on that exact tool call. Host-native
agents should use their normal shell. Remote and cloud agents should run it
inside that environment. If required escalation is blocked, the command fails,
or its output is malformed, report authentication as unknown and do not request
login. Only if the authoritative check succeeds and returns
`authenticated: false`, use the instruction for that environment. For a local
or host-native session, ask the user to run `coderabbit auth login --agent` in
their host terminal. For a remote or cloud session, report that authentication
is not configured there and direct the user to the official CLI documentation.
Do not run or elevate login or attempt to reuse a local host credential.

### Run Review

Once prerequisites are met, select and validate the scope arguments in the
sandbox. Then issue one direct absolute-path review command containing only
literal arguments. Do not include assignments, variable expansions,
conditionals, pipes, or command wrappers in the host-executed tool call.

Run exactly one direct command after substituting the resolved path and any
literal, validated selector values:

- Default: `"/absolute/path/to/coderabbit" review --agent -t all`
- Committed: `"/absolute/path/to/coderabbit" review --agent -t committed`
- Uncommitted: `"/absolute/path/to/coderabbit" review --agent -t uncommitted`

Append a literal `--base <branch>` or `--dir <path>` selector only when the user
requested it.

In a local sandboxed runtime, run that requested review command with
command-scoped host execution. In Codex, set
`sandbox_permissions: require_escalated` on that exact tool call. The exact
`auth status --agent` check and the requested `review --agent` command with its
supported scope flags are the only CodeRabbit commands eligible for host
execution. Do not disable the sandbox for the session or elevate another
CodeRabbit subcommand. Do not run any other CodeRabbit subcommand, even inside
the sandbox.

Never retrieve, expose, copy, store, hash, or pass a credential. Let the trusted
CLI access its credential store directly. Remote and cloud agents must use
authentication configured inside that environment and must not attempt to
access a local host credential store.

Where `type`, `base`, and `dir` come from `$ARGUMENTS`:

- `all` (default) - All changes
- `committed` - Committed changes only
- `uncommitted` - Uncommitted only

Add `--base <branch>` only when a base branch is specified.
Add `--dir <path>` only when a review directory is specified. The directory must contain an initialized Git repository; verify it first:

```bash
git -C "$dir" rev-parse --is-inside-work-tree
```

### Present Results

Group findings by severity:

1. **Critical** - Security vulnerabilities, data loss risks, crashes
2. **Warning** - Bugs, performance issues, anti-patterns
3. **Info** - Style issues, suggestions, minor improvements

Offer to apply fixes from the `--agent` findings when the output includes actionable remediation details.
