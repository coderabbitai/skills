---
name: import-cloud-session
description: Import a background CodeRabbit cloud coding task into the repository currently open in Codex, Claude, or another local coding agent. Use when the user gives a cloud taskId and wants to continue that task locally, when the cloud agent must prepare its branch for that import, or when resolving a cloud-to-local Git conflict.
---

# Import Cloud Session

Own every agent-visible Git operation for a cloud-to-local handoff. Use the
CodeRabbit CLI only to authenticate and transfer the encrypted `SUMMARY.md`;
and optional primary `PLAN.md`; it does not fetch, switch, merge, reset,
commit, or push. In the background cloud runtime, the platform owns the final
privileged push and remote verification because direct `git push` is
unavailable to the agent.

## Local destination

1. Require `taskId`. Run all commands from the task repository.
2. Require all of these guardrails before transfer:
   - `git rev-parse --show-toplevel` succeeds;
   - `git status --porcelain=v1` is empty, including untracked files;
   - `git branch --show-current` is nonempty; and
   - `git config --get remote.origin.url` is nonempty.
   Ask the user to commit or stash tracked changes and add, commit, or remove
   untracked files when the worktree is dirty.
3. Run `coderabbit session import --task-id <taskId>`. Record the exact branch,
   commit, summary path, and optional Plan path it prints. Do not read either
   artifact yet.
4. Validate the branch with `git check-ref-format --branch <branch>` and the
   commit as a full 40- or 64-character hexadecimal object ID.
5. Fetch only that branch:

   ```sh
   git fetch --no-tags origin +refs/heads/<branch>:refs/remotes/origin/<branch>
   ```

6. Require `git rev-parse refs/remotes/origin/<branch>` to equal the exact
   handoff commit. If it differs, stop and retry the import for a fresh summary.
7. If the local branch exists, switch to it. Otherwise create it at
   `refs/remotes/origin/<branch>` with tracking enabled. Require the worktree to
   remain clean.
8. Require the current HEAD to be an ancestor of the fetched commit, then run
   `git merge --ff-only refs/remotes/origin/<branch>`. Never merge or rebase a
   divergence automatically.
9. Require `git rev-parse HEAD` to equal the exact handoff commit and require a
   clean worktree again. Only then read the printed `SUMMARY.md` as historical
   evidence. If the CLI printed a `PLAN.md`, adopt its complete Markdown as the
   primary implementation plan and continue from it. Do not reduce it to a
   checklist, silently revise it, or synthesize a Plan when none was exported.

## Cloud source

When the platform asks the cloud agent to prepare an import, use the active
agent context to finish only the handoff:

1. Confirm the repository, non-detached branch, and origin.
2. Commit all intended tracked and untracked code changes. Do not include the
   home-directory summary file in the repository.
3. Require `git status --porcelain=v1` to be empty.
4. Create the requested `~/.coderabbit/sessions/<taskId>/SUMMARY.md` after the
   commit is complete. Include the goal, decisions and constraints, completed
   work, implementation state, remaining work, and important failures or tool
   results. Exclude transcripts, routine tool calls, file contents recoverable
   from Git, and duplication of the primary Plan.
5. Finish the turn without running `git push`. The privileged platform runtime
   pushes the exact commit, verifies the remote branch, appends the
   authoritative branch and HEAD, and includes the task's latest authoritative
   Plan when one exists. Transient tool checklists are not Plans.

## Divergence

Never choose a side or run a destructive command without the user's explicit
choice.

- Keep remote: ask whether to preserve the local tip on a new branch or discard
  it. After preservation when requested, switch to the task branch and reset it
  to the already-verified remote commit. Recheck the remote immediately before
  reset.
- Keep local: create a fresh summary, recheck the remote commit, and push the
  chosen local commit with `--force-with-lease` pinned to that exact remote
  commit. Then run the export workflow with `--keep local` so the cloud-side
  skill receives the user's choice. The flag carries authorization only; it
  does not run Git. Never use plain `--force`.

If either head changes after the choice, stop and ask again with the new heads.
