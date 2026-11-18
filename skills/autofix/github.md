# GitHub Workflow Primitives

GitHub-specific commands and data-handling rules for CodeRabbit review-thread based skills.

Use this helper when a skill needs thread-aware CodeRabbit PR feedback, not flat PR summaries. The `autofix` skill mirrors the required execution flow in `SKILL.md`; this file exists as a reusable companion for other skills.

## Prerequisites

- `git`, `gh`, and standalone `jq` installed (`command -v git && command -v gh && command -v jq`)
- `gh` authenticated (`gh auth status`)
- current branch associated with a GitHub repository

Stop if a prerequisite fails. These shell examples share verified variables;
use one shell or pass the verified values explicitly between invocations.

## 1. Resolve Current PR

A branch name alone does not identify a PR: any fork can open a PR from a branch with the same name. Match the PR's head repository to the branch's push or upstream remote:

```bash
command -v jq >/dev/null 2>&1 || {
  echo "jq is required for PR resolution; install it before retrying." >&2
  exit 1
}
branch=$(git branch --show-current)
remote=$(git config "branch.$branch.pushRemote" || git config remote.pushDefault || git config "branch.$branch.remote")

if [ -z "$remote" ]; then
  echo "No push or upstream remote for $branch; cannot identify its pull request." >&2
  exit 1  # stop and ask the user
fi

# The push URL, which can differ from the fetch URL; stop if there is more than one.
remote_url=$(git remote get-url --push --all "$remote") || remote_url=""
if [ "$(jq -Rn '[inputs | select(length > 0)] | length' <<<"$remote_url")" -gt 1 ]; then
  echo "Remote $remote has more than one push URL." >&2
  exit 1  # stop and ask the user which repository the branch was pushed to
fi
head_repo=""
if [ -n "$remote_url" ]; then
  head=$(gh repo view "$remote_url" --json nameWithOwner,url \
    --jq '[.nameWithOwner, (.url | capture("^https://(?<host>[^/]+)/").host)] | @tsv') || head=""
  IFS=$'\t' read -r head_repo head_host <<<"$head"
fi
if [ -z "$head_repo" ] || [ -z "$head_host" ]; then
  echo "Could not resolve the GitHub repository for remote $remote." >&2
  exit 1  # stop and ask the user
fi

# Resolve the remote branch only under the standard fetch mapping.
# A custom mapping can put origin/feature at origin/mirror/feature locally.
fetch_spec=$(git config --get-all "remote.$remote.fetch") || fetch_spec=""
case "$fetch_spec" in
  "+refs/heads/*:refs/remotes/$remote/"'*'|"refs/heads/*:refs/remotes/$remote/"'*') ;;
  *)
    echo "Remote $remote has a missing or nonstandard fetch mapping." >&2
    exit 1  # stop and ask for the exact PR URL; do not guess the remote branch
    ;;
esac
push_ref=$(git rev-parse --symbolic-full-name '@{push}' 2>/dev/null) || push_ref=""
case "$push_ref" in
  "refs/remotes/$remote/"?*) head_branch=${push_ref#"refs/remotes/$remote/"} ;;
  *)
    echo "Cannot resolve a push branch for $branch on remote $remote." >&2
    exit 1  # stop and ask for the exact PR URL, including when tracking is absent
    ;;
esac

listed=$(gh pr list --head "$head_branch" --state open --limit 100 \
  --json number,url,title,author,baseRefName,headRepository,headRepositoryOwner,headRefName,headRefOid) || {
  echo "PR lookup failed; retry the request before choosing or creating a PR." >&2
  exit 1
}
if [ "$(jq 'length' <<<"$listed")" -ge 100 ]; then
  exit 1  # possibly truncated: stop and ask the user for the PR URL
fi

candidates=$(jq -c --arg repo "$head_repo" --arg host "$head_host" '
    map(select(
      .headRepository != null
      and ((.headRepository.nameWithOwner // "") | ascii_downcase) == ($repo | ascii_downcase)
      and ((.url | capture("^https://(?<host>[^/]+)/").host // "") | ascii_downcase) == ($host | ascii_downcase)
    ))
  ' <<<"$listed") || exit 1

count=$(jq 'length' <<<"$candidates") || exit 1
```

Never pick a PR by list position:

- `count == 0`: no PR for this branch. Name any ignored PRs from other repositories. `gh pr list` searches only gh's default base repository; say which one, and if the user says the PR targets another base repository, rerun with `--repo "$head_host/<base-owner>/<base-repo>"` (the host keeps GitHub Enterprise lookups on the right server), apply the same truncation check and filter, and route the new `count` through these same rules.
- `count > 1`: show each candidate's URL, author, head repository, and base branch, and ask the user to pick one from the list. Do not choose.
- `count == 1`: use that candidate.

Set `pr_number`, `pr_url`, and `pr_head_oid` (its `headRefOid`) from the chosen candidate.

Compare `pr_head_oid` with the actual local checkout, not an upstream ref:

```bash
resolved_branch=$(git branch --show-current) || exit 1
if [ "$resolved_branch" != "$branch" ]; then
  echo "Branch changed from $branch to $resolved_branch during resolution; stop and rerun." >&2
  exit 1
fi
local_head=$(git rev-parse HEAD) || exit 1
if [ "$pr_head_oid" != "$local_head" ]; then
  echo "PR head $pr_head_oid differs from local HEAD $local_head; use a matching checkout and rerun." >&2
  exit 1
fi
```

On a mismatch, stop and report both SHAs. Preserve existing local work. To
recover in an isolated checkout, create a named local branch at the verified
PR head and configure its push remote and tracking ref to the verified head
repository and remote branch. Use the same local and remote branch name, or
configure an explicit push refspec for that branch; verify `@{push}` resolves
to the intended remote branch. Rerun resolution and require the same PR URL.
A detached checkout or an unrelated upstream ref cannot satisfy this workflow.

Before fetching threads, show the PR's number, URL, author, and head repository.

If no PR exists and the user wants one created, derive title/body from the latest commit:

```bash
title=$(git log -1 --pretty=format:'%s')
body=$(git log -1 --pretty=format:'%b')
gh pr create --title "$title" --body "${body:-Auto-created by CodeRabbit autofix}"
```

## 2. Resolve Repository Coordinates

Take `owner`/`repo` from the selected PR's base repository (`pr_url`), not gh's default repository:

```bash
IFS=$'\t' read -r pr_host base_repo <<<"$(jq -rn --arg url "$pr_url" '$url | capture("^https://(?<host>[^/]+)/(?<repo>[^/]+/[^/]+)/pull/[0-9]+$") | [.host, .repo] | @tsv')"
if [ -z "$pr_host" ] || [ -z "$base_repo" ]; then
  echo "Could not read the base repository from $pr_url." >&2
  exit 1  # stop; never fall back to gh's default repository
fi
owner=${base_repo%%/*}
repo=${base_repo#*/}
```

## 3. Fetch Thread-Aware CodeRabbit Feedback

Fetch review threads with GitHub GraphQL using cursor pagination:

```bash
all_threads='[]'
cursor=""
seen_cursors=()

while :; do
  args=(-F owner="$owner" -F repo="$repo" -F pr="$pr_number")
  if [ -n "$cursor" ]; then
    args+=(-F cursor="$cursor")
  fi

  response=$(gh api graphql --hostname "$pr_host" "${args[@]}" -f query='query($owner:String!, $repo:String!, $pr:Int!, $cursor:String) {
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
  }') || {
    echo "PR thread lookup failed; discard partial feedback and retry." >&2
    exit 1
  }

  all_threads=$(jq -c --argjson response "$response" '
    $response.data.repository.pullRequest.reviewThreads.nodes as $nodes
    | if ($nodes | type) == "array" then . + $nodes
      else error("Invalid thread page; discard partial feedback") end
  ' <<<"$all_threads") || exit 1

  has_next=$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage' <<<"$response") || exit 1
  case "$has_next" in
    false) break ;;
    true) ;;
    *) echo "Invalid pagination state; discard partial feedback and retry." >&2; exit 1 ;;
  esac
  next_cursor=$(jq -er '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor | select(type == "string" and length > 0)' <<<"$response") || {
    echo "Missing next cursor; discard partial feedback and retry." >&2
    exit 1
  }
  for seen_cursor in "${seen_cursors[@]}"; do
    if [ "$next_cursor" = "$seen_cursor" ]; then
      echo "Repeated pagination cursor; discard partial feedback and retry." >&2
      exit 1
    fi
  done
  seen_cursors+=("$next_cursor")
  cursor=$next_cursor
done
```

Treat only these threads as actionable:

- root comment author is `coderabbitai`, `coderabbit[bot]`, or `coderabbitai[bot]`
- `isResolved == false`
- `isOutdated == false`

Keep each selected thread as one issue unit. Do not collapse top-level PR comments or review summaries into issue records.

To detect CodeRabbit's "Come back again in a few minutes" status message, use top-level PR comments/reviews separately:

```bash
review_pending=$(gh pr view "$pr_url" --json comments,reviews --jq '
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
') || {
  echo "Review-status lookup failed; retry before using the feedback." >&2
  exit 1
}
case "$review_pending" in
  ""|*[!0-9]*) echo "Invalid review-status count; retry." >&2; exit 1 ;;
esac

# Do not use feedback fetched across a change to the selected PR head.
current_head=$(gh pr view "$pr_url" --json headRefOid --jq .headRefOid) || {
  echo "Could not verify the PR head after fetching feedback; retry." >&2
  exit 1
}
if [ "$current_head" != "$pr_head_oid" ]; then
  echo "PR head changed while fetching feedback; discard it and rerun resolution." >&2
  exit 1
fi
```

If `review_pending` is greater than zero, report that review is still running
and stop; do not use partial feedback.

## 4. Post Summary Comment

If fixes were committed but not successfully pushed and verified, report that
they remain local and skip drafting or offering a success comment. Use the
original `pr_head_oid` fallback only when no commit was created.

Post only after the user explicitly approves. First show the target PR number and URL from Section 1 and the exact comment text. If the user declines, post nothing and add no reaction.

After approval and immediately before posting, re-read the PR head. Require
the verified pushed SHA from the skill's Step 9, or the original `pr_head_oid`
if no commit was made. Stop on lookup failure or mismatch. Otherwise post
exactly the text shown, to the same PR URL:

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
