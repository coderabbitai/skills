---
description: Run CodeRabbit AI code review on your changes
argument-hint: "[type] [--base <branch>] [--dir <path>]"
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
```

**If CLI not found**, tell user:
> CodeRabbit CLI is not installed. Install it from the official docs:
>
> <https://www.coderabbit.ai/cli>
>
> Prefer a package manager or a verified binary, then restart your shell and try again.

### Run Review

Once prerequisites are met, run review directly; it starts browser authentication when needed. Honor no-login restrictions and use the host flow if a sandbox hides credentials; never read credential files or request pasted tokens.

```bash
# type defaults to "all"; use a public scope option only when requested
args=(review --agent)
case "${type:-all}" in
  committed) args+=(--committed) ;;
  uncommitted) args+=(--uncommitted) ;;
  all) ;;
  *) printf 'Unsupported review type: %s\n' "$type" >&2; exit 2 ;;
esac
[ -n "${base:-}" ] && args+=(--base "$base")
[ -n "${dir:-}" ] && args+=(--dir "$dir")
coderabbit "${args[@]}"
```

Where `type`, `base`, and `dir` come from `$ARGUMENTS`:

- `all` (default) - All tracked changes
- `committed` - Committed changes only
- `uncommitted` - Staged changes and unstaged edits to tracked files

Raw untracked files are excluded by default; staged new files are included. Add `--include-untracked` only when requested; it conflicts with `--committed` but can combine with `--uncommitted`. Never combine committed and uncommitted selectors or silently shrink the requested scope.

Append any requested `--include-untracked`, `--light`, or `--base-commit <commit>` option to the argument array; do not discard these when translating `$ARGUMENTS`. Add `--base <branch>` only when a base branch is specified.
Add `--dir <path>` only when a review directory is specified. The directory must be inside an initialized Git working tree; verify it first:

```bash
git -C "$dir" rev-parse --is-inside-work-tree
```

### Present Results

Parse `--agent` as NDJSON and preserve the returned severity (`critical`, `major`, `minor`, `trivial`, `info`, or `none`). Heartbeats are liveness only. A `complete` event with `status: review_skipped` is not a clean review.

Offer to apply fixes from the `--agent` findings when the output includes actionable remediation details.
