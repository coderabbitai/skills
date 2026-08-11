# GitHub Workflow Primitives

GitHub-specific commands and data-handling rules for CodeRabbit review-thread based skills.

This file is the single source of truth for the GitHub commands used by the `autofix` skill — its SKILL.md references the sections below instead of inlining them. Use these primitives when you need thread-aware CodeRabbit PR feedback rather than flat PR summaries.

## Prerequisites

- `gh` authenticated for the host of the current repository's remote — verify with:

```bash
host=$(git remote get-url origin | sed -E 's#^[a-zA-Z+]+://##; s#^[^@/]+@##; s#[:/].*$##')
gh auth status --hostname "$host" --active
```

  A non-zero exit status is a hard stop: do not continue the workflow.

- current branch associated with a GitHub repository

## 1. Resolve Current PR

Get the PR number for the current branch:

```bash
pr_number=$(gh pr list --head "$(git branch --show-current)" --state open --json number --jq '.[0].number')

if [ -z "$pr_number" ] || [ "$pr_number" = "null" ]; then
  # no open PR for this branch
fi
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
host=$(git remote get-url origin | sed -E 's#^[a-zA-Z+]+://##; s#^[^@/]+@##; s#[:/].*$##')
```

`gh pr` commands resolve the host from the repo's remotes natively; only `gh api` calls need `--hostname "$host"` (its default is `github.com` regardless of repo context).

## 3. Fetch Thread-Aware CodeRabbit Feedback

Fetch review threads with GitHub GraphQL using cursor pagination:

```bash
all_threads='[]'
cursor=""

while :; do
  args=(-F owner="$owner" -F repo="$repo" -F pr="$pr_number")
  if [ -n "$cursor" ]; then
    args+=(-F cursor="$cursor")
  fi

  response=$(gh api graphql --hostname "$host" "${args[@]}" -f query='query($owner:String!, $repo:String!, $pr:Int!, $cursor:String) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$pr) {
        title
        reviewThreads(first:100, after:$cursor) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            isResolved
            isOutdated
            comments(first:1) {
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
  }')

  all_threads=$(jq -c --argjson response "$response" '
    . + $response.data.repository.pullRequest.reviewThreads.nodes
  ' <<<"$all_threads")

  has_next=$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage' <<<"$response")
  cursor=$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor // empty' <<<"$response")
  [ "$has_next" = "true" ] || break
done
```

Treat only these threads as actionable:

- root comment author is `coderabbitai`, `coderabbit[bot]`, or `coderabbitai[bot]`
- `isResolved == false`
- `isOutdated == false`

Keep each selected thread as one issue unit. Do not collapse top-level PR comments or review summaries into issue records.

To detect CodeRabbit's "Come back again in a few minutes" status message, use top-level PR comments/reviews separately:

```bash
gh pr view "$pr_number" --json comments,reviews --jq '
  [
    (.comments[]?
      | select(.author.login == "coderabbitai" or .author.login == "coderabbit[bot]" or .author.login == "coderabbitai[bot]")
      | .body // empty),
    (.reviews[]?
      | select(.author.login == "coderabbitai" or .author.login == "coderabbit[bot]" or .author.login == "coderabbitai[bot]")
      | .body // empty)
  ]
  | map(select(test("Come back again in a few minutes")))
  | length
'
```

## 4. Post Summary Comment

Use the same `pr_number` from Section 1. Set the variables from local workflow state first — the unquoted heredoc substitutes them (backticks inside it must stay escaped):

```bash
file_count=<number of files changed this run>
issue_count=<number of issues fixed this run>
commit_sha=$(git rev-parse --short HEAD)
branch_name=$(git branch --show-current)
files_list=$(git show --name-only --pretty=format: HEAD | sed 's/^/- `/;s/$/`/')

gh pr comment "$pr_number" --body "$(cat <<EOF
## Fixes Applied Successfully

Fixed ${file_count} file(s) based on ${issue_count} CodeRabbit feedback item(s).

**Files modified:**
${files_list}

**Commit:** \`${commit_sha}\`

The latest autofix changes are on the \`${branch_name}\` branch.

EOF
)"
```

Write this comment from local state only. Do not include raw reviewer prompts or secret-bearing output.

If no fixes were applied, skip the success template or post this neutral review-complete comment instead of inventing file counts or a commit SHA. Set `issue_count` from local workflow state first:

```bash
issue_count=<number of issues reviewed this run>

gh pr comment "$pr_number" --body "$(cat <<EOF
## CodeRabbit Autofix Review Complete

Reviewed ${issue_count} CodeRabbit feedback item(s) and did not apply code changes in this run.

EOF
)"
```

## 5. Optional Reaction

If useful, react to the main CodeRabbit comment with 👍 after the summary is posted.
