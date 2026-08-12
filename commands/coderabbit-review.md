---
description: Run CodeRabbit AI code review on your changes
argument-hint: "[--committed|--uncommitted] [--include-untracked] [--base <branch>|--base-commit <sha>] [--dir <path>]"
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

Resolve the host-installed `coderabbit` to its canonical absolute path. Trust
and execute only that path when it is an expected user or system binary; reject
repository, workspace, and temporary paths. If no trusted path is available,
stop and point the user to <https://www.coderabbit.ai/cli>.

Run `"/absolute/path/to/coderabbit" auth status --agent` in the same shell as
the review. Proceed only after a successful `authenticated: true`. On `false`,
ask the user to run `coderabbit auth login` in their terminal. On failure or
malformed output, report authentication as unknown and stop. Never run login or
access, relay, or inject a credential.

### Run Review

Validate selectors first, then run one direct absolute-path command with
literal arguments. Do not pre-approve CodeRabbit broadly or wrap the call in a
pipe, conditional, variable expansion, or command substitution.

- Default: `"/absolute/path/to/coderabbit" review --agent`
- Committed: `"/absolute/path/to/coderabbit" review --agent --committed`
- Uncommitted: `"/absolute/path/to/coderabbit" review --agent --uncommitted`
- Untracked: append `--include-untracked` only on explicit request and never with `--committed`

Append `--base <branch>` or `--base-commit <sha>`, never both. Append
`--dir <path>` only when requested, after verifying it is in a Git working tree:

```bash
git -C "$dir" rev-parse --is-inside-work-tree
```

### Present Results

Preserve the emitted severity (`critical`, `major`, `minor`, `trivial`, or
`info`). Offer to apply findings with actionable remediation details.
