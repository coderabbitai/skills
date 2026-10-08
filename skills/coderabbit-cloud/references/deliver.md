# Review plans, push changes, and control Autopilot

For `plan`, `push`, and `autopilot`, the exit code is 0 for `complete`
(including `push_in_progress`) and 1 for `error` and `action_required`.

## Review and approve a plan

```sh
coderabbit code plan <task> --agent
coderabbit code plan <task> --agent --approve
```

Without `--approve`, the command only reads. It shows the latest finalized
plan of a Plan-mode task.

The last record is `complete` with `status` `plan_shown` or `plan_approved`.
Read `plan.version`, `plan.markdown` (the full plan), `plan.approvals[]`, and
`viewer` (`isAuthor`, `hasApproved`).

`--approve` has no version option, so you cannot bind the approval to the
version that the user reviewed. The command approves the latest finalized
version at the time of the run. A newer version can finish between your last
read and the approval. If `viewer.isAuthor` is true, do not run it: the user
started the task and cannot approve its plan.

1. Record the `plan.version` that the user reviewed.
2. Tell the user that the command approves the latest version at the time of
   the run, which can be newer than the reviewed version. Run `--approve` only
   if the user accepts this. Otherwise, the user approves the plan on the
   cloud task page.
3. Just before you approve, run `coderabbit code plan <task> --agent`. If
   `plan.version` differs, show the new plan to the user and ask again.
4. Run `coderabbit code plan <task> --agent --approve`.
5. After `plan_approved`, compare `plan.version` with the version that the
   user reviewed. If they differ, tell the user at once that you approved a
   newer version, and show it with `coderabbit code plan <task> --agent`.

Approval does not start implementation. Do not implement the plan
yourself, for example with a `-m` message. The user implements it with
`/implement` in the interactive view
([interactive-view.md](interactive-view.md)) or on the cloud task page, and
that work is billed.

- `plan_shown`: show or summarize the plan for the user. Report the version
  and the approvals.
- `plan_approved`: report the approved version.
- `plan_not_found`: the task has no finalized plan yet. Follow the plan turn
  with `resume --agent` ([follow.md](follow.md)), then try again. If the
  `message` says that the task runs in code mode, a retry does not help.
- `plan_stale`: the plan changed. Run the command without `--approve`, show
  the new version to the user, and ask again before you approve it.
- `plan_author_cannot_approve`: a teammate must approve the plan, or the
  user implements it with `/implement` in the interactive view or on the
  task page. The `message` has the URL.
- `action_required` with `authenticate`: log in (see
  [SKILL.md](../SKILL.md#login-required)). The approval did not apply.
- `plan_failed`: report the `message`.

## Push the task's changes

```sh
coderabbit code push <task> --agent
coderabbit code push <task> --agent --stacked
```

Run it only when the user asks. Use the mode that the user chose:

- By default, CodeRabbit commits and pushes the ready changes to the task
  branch (`deliveryMode: "commit_to_pr_branch"`).
- `--stacked` opens a new pull request with the changes
  (`deliveryMode: "stacked_pr"`).

The command waits up to 15 minutes for the push. Run it in the background or
with a long timeout. If the run stops early, the push continues in the
cloud.

A rerun joins a push that already runs. If the changes are pushed and no
newer patch is ready, it reports `alreadyPushed: true` and sends no new push.
If a newer patch is ready, a rerun pushes it. So before a rerun, run
`coderabbit code show <task> --agent`. If `patchStatus` is `"ready"` and
`patch.revision` is newer than the changes that the user asked to push, ask
the user first. Otherwise, a rerun under the same user request needs no new
approval.

While it waits, the command writes `status` records with
`status: "delivery_waiting"`, `taskStatus`, `deliveryStatus`, and `gitStep`
(the running git step, for example `pushing`, or `null`), at least every 45
seconds.

| Last record                                 | Next action                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `complete`, `task_pushed`                   | Report `deliveryMode`, `alreadyPushed`, and `task.result` (`branchName`, `commitSha`, `stackedPrUrl`). `deliveryMode` can differ from the mode that you asked for, because the run can join another push.                                                                                                       |
| `complete`, `push_in_progress`              | The push still runs after 15 minutes. Tell the user. Check it later with `code show`.                                                                                                                                                                                                                           |
| `action_required`, `authorize_github`       | Give `url` to the user. See [GitHub authorization](#github-authorization).                                                                                                                                                                                                                                      |
| `action_required`, `authenticate`           | Log in (see [SKILL.md](../SKILL.md#login-required)), then run `push` again. This can also mean that the Git provider connection needs a new login.                                                                                                                                                              |
| `error`, `task_busy` or `turn_active`       | An agent turn runs. Wait for it (`resume --agent` or `show`). Then run `code show`. If the turn produced changes that the user did not ask to push, ask the user. Otherwise, run `push` again.                                                                                                                  |
| `error`, `pending_queue_exists`             | Queued messages must run first. Tell the user. Do not clear the queue yourself. After the queue is empty, check `code show` as for `task_busy`, then run `push` again.                                                                                                                                          |
| `error`, `git_operation_active`             | Another push runs, and the CLI could not read the task. Run `push` again later.                                                                                                                                                                                                                                 |
| `error`, `push_rejected`                    | Report the `message`. Run `code show` to check `patchStatus`.                                                                                                                                                                                                                                                   |
| `error`, `delivery_conflicts`               | The push found merge conflicts. The user resolves them on the task page. The `message` has the URL.                                                                                                                                                                                                             |
| `error`, `delivery_failed` or `push_failed` | Report the `message`. A `delivery_failed` message can name the git reason, for example a GitHub App without the `workflows` permission. Report that reason and its next step to the user. Do not run `push` again until the cause is fixed, for example after the cloud agent removes the workflow file change. |

### GitHub authorization

GitHub can ask the user to authorize CodeRabbit before the first push.

1. Give the `url` to the user. Never open it yourself.
2. Ask the user to open it in a browser that is signed in to CodeRabbit with
   the same GitHub account, and to approve access.
3. The cloud task page then finishes the push.
4. After the user says that they approved, run the returned `command`. If it
   reports `task_busy` or `turn_active`, handle it as in the table.

## Control Autopilot

```sh
coderabbit code autopilot status <task> --agent
coderabbit code autopilot status --pr <number-or-url> --agent
coderabbit code autopilot on <task> --agent
coderabbit code autopilot on --pr <number-or-url> --agent
coderabbit code autopilot resume <task> --agent
coderabbit code autopilot off <task> --agent
```

Autopilot publishes the task's changes when the agent finishes. Then it fixes
CodeRabbit findings, required CI, and merge conflicts.

- `status` only reads.
- `on` starts Autopilot. It checks Coding Agent billing. Run it only when the
  user asks, and never as a retry. `on` does not resume a paused watch.
- `resume` starts a new repair episode after a pause. It checks billing. Run
  it only when the user asks, and never as a retry.
- `off` stops Autopilot. Run it only when the user asks.

Pass a task, or `--pr`, not both. `--pr <number>` names a pull request of the
repository that the `origin` remote of the current checkout matches. `--pr`
also accepts a GitHub pull request URL or a GitLab merge request URL. With
`--pr`, `on` and `resume` can create an Autopilot task for the pull request.
That task is billed.

The last record is `complete` with `status` `autopilot_status`,
`autopilot_enabled`, `autopilot_disabled`, or `autopilot_resumed`. Read:

- `autopilot.available`: whether the repository supports Autopilot. `off`
  without a watch always reports `false`.
- `autopilot.watch`: `null` when no watch exists. Otherwise read `taskId`,
  `url`, `prNumber`, `prUrl`, `enabled`, `state`, `rounds`, and `reason`.

Errors:

- `autopilot_paused`: `on` found a paused watch. Tell the user. Run
  `autopilot resume` with the same target only if the user asks.
- `billing_required`: the user must start a Coding Agent trial or set up
  billing in the web app, or a spend cap or invoice hold blocks the work.
- `access_denied`: the user cannot change Autopilot for this target. Report
  the `message`.
- `action_required` with `authenticate`: log in (see
  [SKILL.md](../SKILL.md#login-required)). The rerun rules there apply.
- `repository_not_resolved`: the checkout or the pull request URL matches no
  repository of the organization.
- `task_not_found`: the task, or the Autopilot task of the pull request, is
  not in this organization.
- `autopilot_failed`: report the `message`. Do not rerun `on` or `resume`
  yourself.
