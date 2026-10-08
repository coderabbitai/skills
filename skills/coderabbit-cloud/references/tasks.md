# Find and inspect cloud tasks

`code ls` and `code show` only read. You can run them again at any time.

## List tasks

```sh
coderabbit code ls --agent
coderabbit code ls --agent --status needs_attention
coderabbit code ls --agent --repo .
coderabbit code ls --agent --all
```

- The command lists the 20 most recently updated tasks in the selected
  organization. It has no paging option.
- By default it lists only the user's tasks. `--all` adds the tasks of other
  people that the user can see.
- Archived tasks and automation tasks are not listed.
- `--repo <path>` lists only the tasks of the repository that the `origin`
  remote of the checkout at `<path>` matches. The checkout does not have to
  be clean.
- `--status` filters by the web task list state. The values are
  `needs_attention`, `ready_for_review`, `running`, `completed`, and
  `canceled`.

The command writes one `task` record for each task, with the fields under
`task`. Then it writes `complete` with `status: "tasks_listed"`, `count`,
`totalCount`, and `hasMore`.

Read these task fields: `taskId`, `url`, `title`, `status`, `state`,
`turnStatus`, `repository.name`, `requestedBy`, and `updatedAt`. The list
shows stored values. Use `code show` for the current values. If `hasMore` is
true, tell the user that more tasks are in the web app.

## Show one task

```sh
coderabbit code show <task> --agent
```

`<task>` is a task ID or a task URL that ends in `/code/tasks/<id>`. The CLI
takes only the ID from a URL. It reads the task from the region and the
organization of the current login.

The last record is `complete` with `status: "task_shown"`, `task`, and
`warnings`. Read these fields:

- State: `status`, `taskStatus`, `turnStatus`, `patchStatus`, `planStatus`,
  `deliveryStatus`, `collaborationMode`, `pendingReason`, and
  `cancellationPending`.
- Work: `patch` (`fileCount`, `revision`), `plan` (`version`), and
  `resultSummary` or `errorSummary`.
- Delivery: `result` (`deliveryMode`, `branchName`, `commitSha`,
  `stackedPrNumber`, `stackedPrUrl`), and `deliveryError`. When
  `deliveryStatus` is `"failed"`, report `errorSummary`, or `deliveryError`
  when `errorSummary` is `null`: it is the git reason from the trace, for
  example GitHub's rejection of a workflow file change. Then `resultSummary`
  can still name the step that was running, so do not report it as the
  result. `deliveryError` is `null` when no reason is known.
- Pull request: `prHealth` (`state`, `checks`, `conflicts`,
  `requestedChanges`, `isInMergeQueue`, `url`). It is `null` when the task
  has no pull request.

A warning with `code: "pr_health_unavailable"` means that the pull request
health read failed. The command still succeeded. Tell the user.

## Next action

- `tasks_listed` or `task_shown`: report the result. Then use the task state:
  - A turn runs: report it. Follow it with `resume --agent` only if the
    user asks ([follow.md](follow.md)).
  - The agent waits for an answer: see [follow.md](follow.md).
  - A plan or a patch is ready: see [deliver.md](deliver.md).
- `task_not_found`: the task is not in this organization and region. A URL
  from another region, for example EU, is still read from the region of the
  current login. Tell the user. Logging in to the other region, for example
  with `coderabbit auth login --region eu`, is the user's decision.
- `task_in_other_organization`: the user must run `coderabbit auth org` in
  an interactive terminal to switch.
- `repository_not_resolved`: the path is not a Git checkout, has no `origin`
  remote, or its `origin` matches no repository of the organization. Report
  the `message`.
- `list_failed` or `show_failed`: report the `message`. You can run the
  command again.
- Other errors: see [SKILL.md](../SKILL.md#shared-handling).
