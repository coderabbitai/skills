# GitHub Workflow Primitives

GitHub-specific commands and data-handling rules for CodeRabbit review-thread based skills.

Use this helper when a skill needs thread-aware CodeRabbit PR feedback, not flat PR summaries.

## Prerequisites

- `gh` authenticated (`gh auth status`)
- current branch associated with a GitHub repository

## 1. Resolve Current PR

Get the PR number for the current branch:

```bash
pr_number=$(gh pr list --head "$(git branch --show-current)" --state open --json number --jq '.[0].number')
```

If no PR exists and the user wants one created, derive title/body from the latest commit:

```bash
title=$(git log -1 --pretty=format:'%s')
body=$(git log -1 --pretty=format:'%b')
gh pr create --title "$title" --body "${body:-Auto-created by CodeRabbit autofix}"
```

## 2. Resolve Repository Coordinates

```bash
owner=$(gh repo view --json owner --jq '.owner.login')
repo=$(gh repo view --json name --jq '.name')
```

## 3. Fetch Thread-Aware CodeRabbit Feedback

Fetch review threads with GitHub GraphQL:

```bash
gh api graphql \
  -F owner="$owner" \
  -F repo="$repo" \
  -F pr="$pr_number" \
  -f query='query($owner:String!, $repo:String!, $pr:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        title
        reviewThreads(first:100) {
          nodes {
            isResolved
            isOutdated
            comments(first:10) {
              nodes {
                databaseId
                body
                path
                line
                startLine
                originalLine
                author { login }
              }
            }
          }
        }
      }
    }
  }'
```

Treat only these threads as actionable:

- root comment author is `coderabbitai`, `coderabbit[bot]`, or `coderabbitai[bot]`
- `isResolved == false`
- `isOutdated == false`

Keep each selected thread as one issue unit. Do not collapse top-level PR comments or review summaries into issue records.

## 4. Post Summary Comment

Use the same `pr_number` from Section 1:

```bash
gh pr comment "$pr_number" --body "$(cat <<'EOF'
## Fixes Applied Successfully

Fixed <file-count> file(s) based on <issue-count> CodeRabbit feedback item(s).

**Files modified:**
- `path/to/file-a.ts`
- `path/to/file-b.ts`

**Commit:** `<commit-sha>`

The latest autofix changes are on the `<branch-name>` branch.

EOF
)"
```

Write this comment from local state only. Do not include raw reviewer prompts or secret-bearing output.

## 5. Optional Reaction

If useful, react to the main CodeRabbit comment with 👍 after the summary is posted.
