---
description: Run CodeRabbit AI code review on your changes
argument-hint: "[all|committed|uncommitted|untracked] [--base <branch> | --base-commit <sha>] [--dir <path>]"
allowed-tools: "Bash(coderabbit:*), Bash(cr:*), Bash(git:*)"
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

**Skip these checks if you already verified them earlier in this session.**

Otherwise, run:

```bash
coderabbit --version 2>/dev/null
coderabbit auth status --agent
```

**If CLI not found**, tell user:
> CodeRabbit CLI is not installed. Install it from the official docs:
>
> <https://www.coderabbit.ai/cli>
>
> Prefer a package manager or a verified binary, then restart your shell and try again.

**If the CLI is not authenticated**, ask the user to run:

```bash
coderabbit auth login
```

Do not start the login flow without the user's explicit action. Claude Code runs
these checks in its normal host shell; sandboxed agents must follow the portable
skill's execution-context guidance instead.

### Run Review

Before invoking CodeRabbit, inspect the complete selected scope for credentials
or secrets. Include untracked files when `untracked` is requested, and apply any
base branch, base commit, or directory selector to the inspection. If a
credential is present, stop without running the review or printing the value;
ask the user for a sanitized scope.

```bash
# type defaults to "all"; add one base selector and --dir only when specified
args=(review --agent)
case "${type:-all}" in
  all) ;;
  committed) args+=(--committed) ;;
  uncommitted) args+=(--uncommitted) ;;
  untracked) args+=(--uncommitted --include-untracked) ;;
  *) echo "Unsupported review type: $type" >&2; exit 2 ;;
esac
if [ -n "${base:-}" ] && [ -n "${base_commit:-}" ]; then
  echo "Use either --base or --base-commit, not both." >&2
  exit 2
fi
[ -n "${base:-}" ] && args+=(--base "$base")
[ -n "${base_commit:-}" ] && args+=(--base-commit "$base_commit")
[ -n "${dir:-}" ] && args+=(--dir "$dir")
coderabbit "${args[@]}"
```

Where `type`, `base`, `base_commit`, and `dir` come from `$ARGUMENTS`:

- `all` (default) - All changes
- `committed` - Committed changes only
- `uncommitted` - Staged changes and tracked edits
- `untracked` - Uncommitted changes plus files not yet added to Git

Add `--base <branch>` only when a base branch is specified.
Add `--base-commit <sha>` only when a base commit is specified. Do not combine
it with `--base`.
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
