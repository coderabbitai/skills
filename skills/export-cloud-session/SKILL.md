---
name: export-cloud-session
description: Export the current Codex, Claude, or other local coding-agent session to CodeRabbit Cloud. Use when continuing committed local work in an existing background task, creating a new cloud task when no taskId is supplied, or resolving a local-to-cloud Git conflict.
---

# Export Cloud Session

Own every Git operation for a local-to-cloud handoff. Use the CodeRabbit CLI
only to authenticate and transfer the encrypted `SUMMARY.md` and optional
primary `PLAN.md`; it does not fetch, switch, merge, reset, commit, or push.

## Local source

1. Run all commands from the repository being handed off. Accept an existing
   `taskId` when supplied; otherwise create a new cloud task from the current
   branch through the CLI flow below.
2. Require a repository with a nonempty origin and a non-detached branch.
3. Require `git status --porcelain=v1` to be empty, including untracked files.
   Ask the user to commit or stash tracked changes and add, commit, or remove
   untracked files before continuing. Never silently commit local user work.
4. When `taskId` is present, read
   `~/.coderabbit/sessions/<taskId>/state.json` to obtain the task branch
   from the preceding import. If it is absent, run
   `coderabbit session import --task-id <taskId>` to obtain authenticated task
   metadata, but do not read that summary or change Git. Validate the returned
   branch with `git check-ref-format --branch`.
5. With an existing `taskId`, require the current branch to equal the task
   branch. If it does not, stop and
   ask the user how the committed work should be moved; do not merge, cherry-pick,
   rebase, or reset automatically.
6. With an existing `taskId`, fetch only the task branch and record its exact
   remote commit. Require that remote commit to be an ancestor of local HEAD.
   On divergence, use the conflict workflow below. Without a `taskId`, use the
   current attached branch as the new task branch; a normal non-force push must
   succeed, so any existing non-fast-forward remote state stops the export.
7. Push the exact local HEAD without force:

   ```sh
   git push origin <head>:refs/heads/<branch>
   ```

8. Require `git ls-remote origin refs/heads/<branch>` to equal the same exact
   local HEAD. Stop without uploading a summary if verification fails.
9. From the active agent context, overwrite
   `~/.coderabbit/sessions/<taskId>/SUMMARY.md` for an existing task. For a new
   task, create `SUMMARY.md` in a private temporary directory and remove that
   directory after the CLI succeeds. Include the goal, decisions and
   constraints, completed work, implementation state, remaining tasks,
   important failures or tool results, and exact branch and HEAD. Exclude
   transcripts, routine tool calls, and file contents recoverable from Git.
10. If the active agent context has a primary implementation plan, write
    `PLAN.md` beside the summary with that complete Markdown Plan.
    Preserve its goals, approach, sequencing, key decisions, and validation
    strategy. A Plan is not a task/status checklist: do not export transient
    tool TODOs, completed-step bookkeeping, or a plan invented only for the
    handoff. If no primary Plan exists, remove any stale `PLAN.md` and omit the
    Plan flag.
11. For an existing task, run one of:

    ```sh
    coderabbit session export --task-id <taskId> --summary-file ~/.coderabbit/sessions/<taskId>/SUMMARY.md
    coderabbit session export --task-id <taskId> --summary-file ~/.coderabbit/sessions/<taskId>/SUMMARY.md --plan-file ~/.coderabbit/sessions/<taskId>/PLAN.md
    ```

    For a new task, omit `--task-id` and use the temporary evidence paths:

    ```sh
    coderabbit session export --summary-file <temporary-summary-path>
    coderabbit session export --summary-file <temporary-summary-path> --plan-file <temporary-plan-path>
    ```

    The CLI resolves the current origin inside the signed-in organization and
    creates an idempotent branch-backed cloud task. It waits for the task's
    no-change bootstrap turn, then encrypts and uploads the handoff through the
    same signed-URL flow as an existing-task export. Finalization supplies the
    summary as historical context, seeds the exact Plan into the dedicated Plan
    section, starts the continuation turn, and prints the new `taskId`. Never
    use `--keep` when creating a task.

Report the task ID, branch, and HEAD, plus the published revision for an
existing task. If an existing cloud turn is running, stop and ask the user to
retry after it finishes.

## Cloud destination

When the platform announces a local export, do not read its staged summary
until the code is synchronized:

1. Record the exact task branch and handoff commit from the platform message.
2. Require the cloud worktree to be clean, including untracked files, and HEAD
   to be attached. If dirty, stop; do not discard cloud work.
3. Validate and fetch only the task branch. Require the fetched remote ref to
   equal the exact handoff commit.
4. Switch to the existing task branch or create it with tracking at that remote
   ref. Allow only `git merge --ff-only`; never reconstruct, merge, or rebase a
   divergent tree.
5. Require HEAD to equal the exact handoff commit and the worktree to remain
   clean. Only then read the staged summary as historical evidence. When a Plan
   was transferred, the platform publishes its exact Markdown in the dedicated
   Plan section; adopt it as the primary implementation plan and continue from
   it without converting it into a checklist.

## Divergence

Never choose a side for the user.

- Keep local: recheck the remote head, then use `--force-with-lease` pinned to
  that exact commit to push the chosen local HEAD. Run the CLI export with
  `--keep local` so the cloud-side skill receives the user's choice. The flag
  carries authorization only; it does not run Git. Never use plain `--force`.
- Keep remote: ask whether to preserve the local tip on a new branch or discard
  it. Recheck the remote before switching/resetting to the chosen remote commit.

If either head changes after the user chooses, stop and ask again with the new
heads. Upload or consume a summary only after the chosen Git state is exact and
the worktree is clean.

When the platform message says the user already chose local, do not ask again.
Recheck that the fetched remote ref equals the exact handoff commit, then reset
the clean cloud task branch to that commit and perform the final HEAD and
worktree checks before reading the summary.
