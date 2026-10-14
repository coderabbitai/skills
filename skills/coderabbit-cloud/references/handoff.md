# Hand off a local session to a new cloud task

`coderabbit code handoff` creates a new cloud task on the current branch. It
uploads a private `SUMMARY.md`, an optional primary `PLAN.md`, and an optional
session transcript. Every run creates a new task.

The command accepts neither `--task-id` nor `--keep`, so it cannot continue an
existing task. To send a message to an existing task, use
`coderabbit code resume <taskId> --agent -m <message>` (see
[follow.md](follow.md)).

You own all local Git operations. The CLI inspects the repository and uploads
the files. It does not fetch, switch branches, merge, reset, commit, or push.
Cloud startup checks out the branch and verifies the exact exported HEAD. If
the remote branch moved, startup fails.

## Procedure

1. Before you change Git state, make sure that `coderabbit code handoff --help`
   lists `--agent`, `--summary`, and `--plan`. If it does not, report that the
   installed CLI does not support handoff, and stop.
2. Require a checked-out branch (not detached HEAD), an `origin` remote, and a
   clean worktree, including untracked files. Complete cleanup that the user
   already authorized. Otherwise, ask the user how to keep the dirty work.
   Never discard or silently commit unrelated changes.
3. Publish the exact local HEAD with a normal push. Do not force-push.

   ```sh
   git push origin <head-sha>:refs/heads/<branch>
   ```

   If the remote branch diverged, stop and report it. Do not force-push or
   choose a side.

4. Make sure that `git ls-remote origin refs/heads/<branch>` shows that exact
   HEAD. If it differs, stop before you write the summary. The summary cannot
   carry code that is not pushed.
5. Write `SUMMARY.md` in a private temporary directory outside the
   repository. From the active session, include:
   - the goal, decisions, and constraints;
   - the completed work and the implementation state;
   - the remaining work;
   - important failures and tool results;
   - the exact branch and HEAD.

   Do not include routine tool calls or content that Git already holds. Do
   not include credentials, tokens, keys, or other secret values in
   `SUMMARY.md` or `PLAN.md`.

6. If a primary implementation plan exists, write its complete Markdown to
   `PLAN.md` beside the summary. Keep its goals, approach, sequence,
   decisions, and validation strategy. Do not use a short checklist instead,
   and do not invent a plan for the handoff. If no plan exists, do not pass
   `--plan`.
7. Run the CLI from the active agent session. Keep `CODEX_THREAD_ID` or
   `CLAUDE_CODE_SESSION_ID`, and any `CODEX_HOME` or `CLAUDE_CONFIG_DIR`
   override, in the environment. The CLI finds the transcript from these. The
   transcript is optional. Do not find or copy transcripts yourself, and do
   not put the transcript in the summary.
8. Run one of these commands:

   ```sh
   coderabbit code handoff --agent --summary <summary-path>
   coderabbit code handoff --agent --summary <summary-path> --plan <plan-path>
   cat <summary-path> | coderabbit code handoff --agent --summary -
   ```

   `--summary` is always necessary; `-` reads it from stdin. `--plan` takes a
   file path. There is no transcript flag. Each file can be at most 25 MiB. A
   summary or plan that is too large stops the handoff before a task is
   created. A transcript that is missing or too large is skipped with a
   warning.

9. Do not commit `SUMMARY.md` or `PLAN.md` to the repository. Remove the
   temporary directory after the task is created.

## Result

- `complete` with `status: "task_created"`: report `taskId`, `url`, `branch`,
  `headCommit`, and any `warnings`. A warning `code` of `transcript_missing`,
  `transcript_too_large`, or `transcript_upload_failed` means the task has no
  transcript. The task is queued; cloud startup runs later.
- `action_required` with `action: "authenticate"`: follow the login steps in
  [SKILL.md](../SKILL.md#login-required). If no `status` record with
  `status: "creating_task"` appeared, no task was created. Rerun the handoff
  once after the login. If that record appeared, a task can exist. Do not
  rerun. Run `coderabbit code ls --agent --repo .`, report what you find,
  and ask the user.
- `error` with `status: "organization_required"`: ask the user to run
  `coderabbit auth org` in an interactive terminal. No task was created, so
  rerun the handoff after the user selects an organization.
- `error` with `status: "unsupported_auth"`: report the `message`. The user
  needs a CodeRabbit SaaS user login.
- `error` with `status: "handoff_failed"`: if a `creating_task` record
  appeared, a task can exist. Do not rerun; run
  `coderabbit code ls --agent --repo .`, report what you find, and ask the
  user. If no `creating_task` record appeared, no task was created. Fix the
  reported cause and rerun the handoff once.
- Any other `error`: report the `message` and keep the local files. Do not
  rerun the command yourself. A new run can create another task.
- Exit 130 or 143: never rerun. A task can exist if a `creating_task` record
  appeared. Run `coderabbit code ls --agent --repo .` and report what you
  find. New tasks can appear in the list late, so a task that is not in the
  list can still exist. Let the user decide.

Follow the new task only when the user asks. Use [follow.md](follow.md).
