# Start and follow a cloud task

## Start a task with `code new`

```sh
coderabbit code new --agent "<prompt>"
coderabbit code new --agent --plan "<prompt>"
coderabbit code new --agent --resume "<prompt>"
cat <prompt-file> | coderabbit code new --agent -
```

`code new` creates billed work. It can start the organization's Coding Agent
trial. Run it only when the user asks, and run it once.

- The task starts on the current branch as it is on `origin`: the branch
  that the current branch tracks, or the branch with the same name. Commits
  that are not pushed and uncommitted changes are not included.
- The CLI only warns about local work that is not on `origin`. Before you
  run the command, make sure that the branch is on `origin` and contains the
  local HEAD. If it does not, tell the user. Push only if the user asks.
- A detached HEAD fails with `branch_not_resolved`.
- `--plan` starts in Plan mode: the agent writes a plan instead of changing
  code. Put `--agent` before `--plan`.
- `--resume` follows the first turn, as `code resume --agent` does. Handle
  its last record as in [Follow a task](#follow-a-task-with-code-resume---agent).
- Always pass the prompt, from 1 to 65,536 characters. `-` reads it from
  stdin.

As soon as the server accepts the task, the command writes a `status` record
with `status: "task_submitted"`, the `taskId`, and the `url`. After this
record, never run `code new` again for this request. Report the `taskId` and
the `url`. Check the task with `coderabbit code show <taskId> --agent`.
Follow it with `resume <taskId> --agent` only if the user asks or you passed
`--resume`. Right after this record, `task_not_found` means that the task
index lags. It does not mean another organization or region. Run `show`
again a few seconds later.

After an interrupted run (exit 130 or 143), never rerun `code new`. If a
`task_submitted` record appeared, use its `taskId`. Otherwise, run
`coderabbit code ls --agent --repo .` and report what you find. New tasks
can appear in the list late, so a task that is not in the list can still
exist. Let the user decide.

| Last record                                             | Next action                                                                                                                                                                                                                                               |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `complete`, `task_submitted`                            | Report `taskId`, `url`, and each `warnings[].message`. The warning codes are `unpushed_commits`, `uncommitted_changes`, and `branch_not_on_origin`. Follow only if the user asks.                                                                         |
| `action_required`, `authenticate`                       | Log in (see [SKILL.md](../SKILL.md#login-required)). If a `task_submitted` record appeared, run `show <taskId> --agent`. Otherwise, run `ls --agent --repo .`. An absent task does not prove that creation failed. Rerun `new` only if the CLI explicitly confirms that the request was rejected before creating a task; otherwise report the uncertainty and ask the user. |
| `error`, `billing_required`                             | The user must start a Coding Agent trial or set up billing in the web app. Stop.                                                                                                                                                                          |
| `error`, `billing_unavailable` or `precondition_failed` | Report the `message`. Billing or the user's identity blocks the task. Stop.                                                                                                                                                                               |
| `error`, `task_rejected` with warning `branch_not_on_origin` | Tell the user the branch must be pushed. After they authorize the push, push it normally and retry `new` once.                                                                                                                                            |
| `error`, `new_failed` before `task_submitted`           | The request may have reached CodeRabbit. Run `ls --agent --repo .` and use `show` for any plausible task before considering a retry. An absent list result is not proof; report the uncertainty and ask the user before running `new` again.                 |
| `error`, `repository_not_resolved`                      | The checkout has no `origin`, or `origin` matches no repository of the organization. Report the `message`.                                                                                                                                                |
| `error`, `operation_conflict`                           | CodeRabbit still processes the first request, so the task can exist. Do not rerun `new`. Run `ls --agent --repo .`, report what you find, and let the user decide.                                                                                        |
| Any other `error`                                       | If a `task_submitted` record appeared, report the `taskId` and run `show <taskId> --agent`. Otherwise, report the `message`. Do not rerun `new`.                                                                                                          |

## Follow a task with `code resume --agent`

```sh
coderabbit code resume <task> --agent
coderabbit code resume --last --agent
coderabbit code resume <task> --agent -m "<message>"
coderabbit code resume <task> --agent --steer "<guidance>"
printf '%s' '<answer-json>' | coderabbit code resume <task> --agent --answer -
```

- `<task>` is a task ID or a task URL. `--last` selects the user's most
  recently updated task for the repository in the current directory. Pass
  one of them, not both.
- Without `--agent`, the command opens an interactive view that needs a
  terminal. Always pass `--agent`. The user can open the view themselves; see
  [interactive-view.md](interactive-view.md).
- Pass at most one of `-m`, `--steer`, and `--answer`. `-` reads the value
  from stdin.
- Without a send option (watch mode), the command reports the latest turn
  and waits for it if it still runs. Watch mode only reads.
- `-m` sends a message. It queues behind a running turn, or starts a new
  turn. The run follows the turn of that message.
- `--steer` adds guidance to the running turn and follows that turn.
- Use `-m` by default. Use `--steer` only when the user asks to change the
  running turn.
- `--answer` sends an answer to the agent's pending question. See
  [Answer a question](#answer-a-question).

The run writes records until the turn ends, the agent asks a blocking
question, or 9 minutes pass. `trace` records show the turn. Their `kind` is,
for example, `agent_message`, `command`, `file_change`, `plan`, `question`,
`git_operation`, or `error`. A `question` trace is a question that does not
block the turn. A `git_operation` trace is a push step or the end of a push.
It shows only when a push runs while the command follows the task, because a
push runs after the turn ends. End events were `notice` traces before. For the
reason of a failed push, read the `delivery_failed` message of `code push`, or
`deliveryError` in `code show`.

The run reads again, with a growing wait, after a read that fails for a
moment: a server error, a timeout, a network failure, or a response that is not
JSON, such as a gateway's HTML error page. It never sends again. After five
failed reads in a row, the last record is `resume_failed`. The message
"CodeRabbit returned an unexpected response. Retry the command." means that
the server sent no JSON to a read. In watch mode, rerun the command once. A
send that gets no JSON gives a message that says the request may have reached
CodeRabbit. Then follow the send rules below and do not send again.

### Send records

A `status` record with `status: "message_sent"`, `"steer_sent"`, or
`"answer_sent"` means that the cloud agent received your send. The
`message_sent` record has a `clientOperationId`.

- After a send record, never send the same thing again unless the last record
  is `message_dropped`. That error explicitly means the message was not
  delivered, so send the same message once more. Otherwise, keep following by
  running the command without `-m`, `--steer`, or `--answer`.
- If no send record appeared, you can rerun the same command once only after
  these results: `authenticate`, `task_busy`, `task_stopping`, or
  `steer_not_delivered`. The CLI rejects these before the send, or the server
  did not take it. After `invalid_arguments`, correct the value, then rerun
  once.
- Exit 3 after `-m` or `--steer` with no send record: a blocking question
  waits, and the CLI did not send your text. Handle the question (see
  [Answer a question](#answer-a-question)). Then send the original text once
  with the same option, or tell the user that it was not sent.
- Interrupted run (exit 130 or 143): if a send record appeared, run watch
  mode. If none appeared, do not resend. The send can still have reached the
  server. Run watch mode, look for your `user_message`, `steer_result`, or
  `answer_submitted` trace, then ask the user.
- After `resume_failed` or any other error with no send record, do not rerun
  the send. The send can still have reached the server, and each run sends a
  new operation. Run watch mode and look for a `user_message` trace with
  your text, a `steer_result`, or an `answer_submitted` record. Then ask the
  user.
- An error message that tells you to send again does not change these rules.

### Last record

| Exit | Last record                                                    | Next action                                                                                                                       |
| ---- | -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| 0    | `complete`, `turn_completed`                                   | Report `turn.finalReply`. `turn.outputKind` is `answer`, `patch`, or `plan`. For a patch or a plan, see [deliver.md](deliver.md). |
| 1    | `error`, `turn_failed`, `turn_canceled`, or `turn_interrupted` | Report the `message` and `turn.errorMessage`.                                                                                     |
| 1    | `action_required`, `authenticate`                              | Log in (see [SKILL.md](../SKILL.md#login-required)). Rerun with the send option only if no send record appeared.                  |
| 3    | `action_required`, `answer_question`                           | See [Answer a question](#answer-a-question).                                                                                      |
| 4    | `action_required`, `resume`                                    | The turn still runs. See [Keep following](#keep-following-after-exit-4).                                                          |

`finalReply` keeps at most 4,000 characters. The web app shows the full
reply.

The `complete` and `error` records of a turn also have `agentMinutes`: the
gross agent minutes of the turn, rounded to two decimals, or `null` when the
CLI does not know them. They are not billed minutes, and `null` is not 0.

### Errors

- `task_read_only`: a workspace task, or a task on the previous runtime. The
  user continues it in the web app. The `message` has the URL.
- `unsupported_task`: an automation task. The user opens it in the web app.
- `turn_not_running`: no turn runs, so the steer did not go through. Tell the
  user. A `-m` message starts a new turn, which is new cloud work, so send
  the text with `-m` only if the user agrees.
- `steer_not_delivered`: the steer did not reach the turn. Without a
  `steer_sent` record, you can retry the steer once while the turn runs.
  With a `steer_sent` record, or when the turn ended, ask the user before
  you send anything, including a `-m` message.
- `steer_rejected`: report the reason.
- `message_dropped`: the message left the queue without being delivered, for
  example because someone stopped the turn. Send the same message again once.
- `task_stopping`: a stop is still finishing. Wait a few seconds, then rerun
  the same send once.
- `task_busy`: without a send record, wait a few seconds and rerun once.
- `no_pending_question` or `question_not_active`: no question waits. Run
  watch mode to see the current state.
- `agent_not_running`: the agent cannot take the answer. Tell the user. A
  `-m` message starts a new turn, which is new cloud work. Send the answer as
  a `-m` message only if the user agrees.
- `sensitive_answer_requires_user`: the user must answer the question.
- `billing_required`: the user must start a trial or set up billing in the
  web app.
- `task_closed`, `task_admission_failed`, `turn_active`,
  `pending_queue_exists`, `operation_conflict`, `git_operation_active`, or
  `resume_failed`: report the `message`.

### Keep following after exit 4

Run the returned `command` again. It is watch mode and reports the latest
turn.

1. After `--steer`, `--answer`, or `code new --resume`, the latest turn is
   the turn that you followed.
2. After `-m`, compare `turn.queueItemId` with the `clientOperationId` of
   your `message_sent` record. If they differ, your message has not started
   yet. Wait a few seconds and run the command again.
3. A message that joined the running turn, or left the queue, never gets its
   own turn.
4. If a rerun reports the same `turn.startSeq` again and `task.turnStatus` is
   not `in_progress`, report that turn and stop.
5. Count only the reruns in step 2, where your message has not started.
   After three of them, report the task URL and the current state, and stop.

## Answer a question

The last record is `action_required` with `action: "answer_question"` and
exit code 3. Read `question.questions[]` (`id`, `header`, `question`,
`options[].label`, `isOther`, `isSensitive`), `answerTemplate`, and
`command`.

1. If `answerTemplate` is `null`, do not answer:
   - A question has `isSensitive: true`: never collect or send the answer.
     Ask the user to answer it in `coderabbit code resume <taskId>` in their
     terminal, or in the web app at `url`. After the user says that they
     answered, run `coderabbit code resume <taskId> --agent` only if the user
     wants you to keep following.
   - A workspace task: the user answers it in the web app.
2. Give the question to the user. Answer it yourself only when the user's
   instructions already give the answer.
3. Fill in each value of `answerTemplate.answers`. Keep `interactionId` and
   the question IDs unchanged.
   - Options with `isOther: false`: the answer must match one `label`. The
     match ignores case.
   - `isOther: true`, or no options: any text that is not empty.
4. Send the JSON with `--answer`. Use stdin (`--answer -`) to prevent shell
   quoting problems.
5. If the result is exit 3 again with a new question, the question that you
   answered is no longer pending. Handle the new question.

## Stop a turn with `code cancel`

```sh
coderabbit code cancel <task> --agent
```

The command stops the running turn and drops the queued messages. The task
stays open: a new message starts a new turn. Run it only when the user asks.
It waits up to 60 seconds. The command sends only the task ID, not a turn,
and `code show` does not tell you which turn a pending stop belongs to. So a
rerun can stop a new turn that someone else started, and drop messages that
were queued after your stop. After a `cancel_requested` record, or after an
interrupted run, do not rerun `cancel`. Before any new stop, ask the user.

A `status` record with `status: "cancel_requested"` follows the stop request.
The last record is `complete` with exit code 0:

- `task_canceled`: the turn stopped. Tell the user that queued messages were
  dropped.
- `turn_finished`: the turn completed or failed before it stopped. Run
  `code show` and report the result.
- `cancel_pending`: the turn is still stopping after 60 seconds. Tell the
  user. Check later with the read-only `code show`: the stop is done when
  `cancellationPending` is false and `turnStatus` is not `in_progress`. If a
  turn still runs after that, report it and ask the user before you run
  `cancel` again.
- `not_running`: no turn was running.

Errors: `task_read_only` and `unsupported_task` mean that the user must stop
the turn in the web app. For `cancel_failed`, report the `message`.
