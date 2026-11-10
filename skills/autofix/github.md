# GitHub Workflow Primitives

GitHub-specific commands and data-handling rules for CodeRabbit review-thread based skills.

Use this helper when a skill needs thread-aware CodeRabbit PR feedback, not flat PR summaries. The `autofix` skill mirrors the required execution flow in `SKILL.md`; this file exists as a reusable companion for other skills.

## Prerequisites

- `gh` authenticated (`gh auth status`), plus `git` and `jq`
- current branch associated with a GitHub repository

## 1. Resolve Current PR

Get the PR number for the current branch:

```bash
branch=$(git branch --show-current) || exit 1
[ -n "$branch" ] || { echo "Detached HEAD: select a branch first." >&2; exit 1; }
prs=$(gh pr list --head "$branch" --state open --json number) || exit 1
pr_number=$(jq -ser '
  if length != 1 then error("Expected one PR-list response") else .[0] end
  | if type != "array" then error("Invalid PR list")
    elif length == 0 then "none"
    elif length != 1 then error("Multiple open PRs: select the intended PR")
    elif (.[0].number | type) != "number" then error("Invalid PR number")
    elif .[0].number <= 0 or (.[0].number | floor) != .[0].number then error("Invalid PR number")
    else .[0].number end
' <<<"$prs") || exit 1
```

Only `pr_number=none` means no PR exists. Stop on lookup/parse errors or multiple matches and ask the user to select the intended PR; never guess. If no PR exists and the user wants one created, derive title/body from the latest commit:

```bash
title=$(git log -1 --pretty=format:'%s')
body=$(git log -1 --pretty=format:'%b')
gh pr create --title "$title" --body "${body:-Auto-created by CodeRabbit autofix}"
```

After creation (or if declined), stop; rerun the workflow after review completes. Do not continue with an absent PR number.

## 2. Resolve Repository Coordinates

```bash
owner=$(gh repo view --json owner --jq '.owner.login') || exit 1
repo=$(gh repo view --json name --jq '.name') || exit 1
```

## 3. Fetch Thread-Aware CodeRabbit Feedback

Run this block as Bash. Require every page to succeed and validate before using the thread list. On error, discard partial results and stop; never report a failed fetch as no issues:

```bash
all_threads='[]'
cursor=""
seen_cursors=()

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
  }') || exit 1

  page=$(jq -sce '
    if length != 1 then error("Expected one GraphQL response") else .[0] end
    | if type != "object" then error("Invalid GraphQL response")
      elif ((.errors // []) | length) != 0 then error("GraphQL errors")
      else .data.repository.pullRequest.reviewThreads end
    | if type != "object" then error("Missing review threads")
      elif (.nodes | type) != "array" then error("Invalid thread list")
      elif (.pageInfo.hasNextPage | type) != "boolean" then error("Missing pagination state")
      elif .pageInfo.hasNextPage and
        ((.pageInfo.endCursor | type) != "string" or .pageInfo.endCursor == "")
      then error("Missing next cursor")
      elif any(.nodes[];
        (.isResolved | type) != "boolean" or (.isOutdated | type) != "boolean" or
        (.comments.nodes | type) != "array" or (.comments.nodes | length) != 1 or
        (.comments.nodes[0].body | type) != "string" or
        (.comments.nodes[0].databaseId | type) != "number")
      then error("Incomplete thread data") else . end
  ' <<<"$response") || exit 1

  all_threads=$(jq -ce --argjson page "$page" '. + $page.nodes' <<<"$all_threads") || exit 1
  has_next=$(jq -r '.pageInfo.hasNextPage' <<<"$page") || exit 1
  [ "$has_next" = "true" ] || break
  cursor=$(jq -r '.pageInfo.endCursor' <<<"$page") || exit 1
  for seen in "${seen_cursors[@]}"; do
    [ "$cursor" != "$seen" ] || { echo "Repeated pagination cursor." >&2; exit 1; }
  done
  seen_cursors+=("$cursor")
done
```

Treat only these threads as actionable:

- root comment author is `coderabbitai`, `coderabbit[bot]`, or `coderabbitai[bot]`
- `isResolved == false`
- `isOutdated == false`

Keep each selected thread as one issue unit. Do not collapse top-level PR comments or review summaries into issue records.

After the complete fetch succeeds, detect CodeRabbit's "Come back again in a few minutes" status message using top-level PR comments/reviews separately. Stop on failure or malformed output; an empty thread list does not prove review completion:

```bash
review_status=$(gh pr view "$pr_number" --json comments,reviews) || exit 1
jq -se '
  if length != 1 then error("Expected one review-status response") else .[0] end
  | if (.comments | type) != "array" or (.reviews | type) != "array"
    then error("Invalid review status") else . end
  | [
    (.comments[]?
      | select(.author.login == "coderabbitai" or .author.login == "coderabbit[bot]" or .author.login == "coderabbitai[bot]")
      | .body // empty),
    (.reviews[]?
      | select(.author.login == "coderabbitai" or .author.login == "coderabbit[bot]" or .author.login == "coderabbitai[bot]")
      | .body // empty)
  ]
  | map(select(test("Come back again in a few minutes")))
  | length
' <<<"$review_status" || exit 1
```

## 4. Post Summary Comment

Post only when authorized, after `git push` succeeds and the selected PR's `headRefOid` equals the recorded fix commit SHA. Declined/failed pushes or an unverified remote head mean local-only or unconfirmed fixes: report that to the user without a success comment.

Write a temporary Markdown file containing the actual fixed issue count from the approved-fix records, the file list from the verified commit, its full SHA, and the confirmed branch. Read the finished file back before posting. Use literal text, not executable shell interpolation; omit unknown values rather than inventing them. Never post template placeholders, raw reviewer prompts, or secret-bearing output.

Set `summary_file` to that verified file's path and use the selected `pr_number`:

```bash
gh pr comment "$pr_number" --body-file "$summary_file"
```

Check the command's result before claiming the comment was posted, then remove the temporary summary file. If no fixes were applied, report that to the user; an optional neutral comment still requires authorization and real run counts.

## 5. Optional Reaction

If authorized, react to the main CodeRabbit comment with 👍 after the summary is posted.
