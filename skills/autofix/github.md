# GitHub Workflow Primitives

GitHub-specific commands and data-handling rules for CodeRabbit review-thread based skills.

Use this helper when a skill needs thread-aware CodeRabbit PR feedback, not flat PR summaries. The `autofix` skill mirrors the required execution flow in `SKILL.md`; this file exists as a reusable companion for other skills.

## Prerequisites

- `gh` authenticated (`gh auth status`)
- current branch associated with a GitHub repository

## 1. Resolve Current PR

A branch name alone does not identify a PR: any fork can open a PR from a branch with the same name. Match the PR's head repository to the branch's push or upstream remote:

```bash
branch=$(git branch --show-current)
remote=$(git config "branch.$branch.pushRemote" || git config remote.pushDefault || git config "branch.$branch.remote")

if [ -z "$remote" ]; then
  # no push or upstream remote: stop and ask the user
fi

head_repo=$(gh repo view "$(git remote get-url "$remote")" --json nameWithOwner --jq '.nameWithOwner')

candidates=$(gh pr list --head "$branch" --state open --limit 100 \
  --json number,url,title,author,baseRefName,headRepository,headRepositoryOwner,headRefName,headRefOid |
  jq -c --arg repo "$head_repo" '
    map(select((.headRepository.nameWithOwner // "" | ascii_downcase) == ($repo | ascii_downcase)))
  ')

count=$(jq 'length' <<<"$candidates")
```

Never pick a PR by list position:

- `count == 0`: no PR for this branch. Name any ignored PRs from other repositories.
- `count > 1`: show each candidate's URL, author, head repository, and base branch, and ask the user to pick one from the list. Do not choose.
- `count == 1`: use that candidate.

Set `pr_number` and `pr_url` from the chosen candidate.

Then compare its `headRefOid` with `git rev-parse HEAD` and `git rev-parse '@{upstream}'`. If it matches neither, report the three SHAs and continue only if the user explicitly confirms.

Before fetching threads, show the PR's number, URL, author, and head repository.

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

Fetch review threads with GitHub GraphQL using cursor pagination:

```bash
all_threads='[]'
cursor=""

while :; do
  args=(-F owner="$owner" -F repo="$repo" -F pr="$pr_number")
  if [ -n "$cursor" ]; then
    args+=(-F cursor="$cursor")
  fi

  response=$(gh api graphql "${args[@]}" -f query='query($owner:String!, $repo:String!, $pr:Int!, $cursor:String) {
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

Post only after the user explicitly approves. First show the target PR number and URL from Section 1 and the exact comment text. If the user declines, post nothing and add no reaction.

On approval, post exactly the text shown, to the same PR URL:

```bash
gh pr comment "$pr_url" --body "$(cat <<'EOF'
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

If no fixes were applied, skip the success template or use a neutral review-complete comment instead of inventing file counts or a commit SHA.

## 5. Optional Reaction

If useful, after the summary is posted, ask separately whether to react to the main CodeRabbit comment on that PR with 👍. React only on explicit approval.
