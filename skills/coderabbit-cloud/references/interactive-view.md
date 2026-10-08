# The interactive view and its slash commands

`coderabbit code resume <task>` without `--agent` opens an interactive view
of the task in the user's terminal. It shows the task live and has an input
line for messages and slash commands. You cannot use this view: it needs a
person at a terminal. Use it to tell the user what to type when they want to
watch a task, or when an action has no `--agent` command.

```sh
coderabbit code resume <task>
coderabbit code resume --last
```

## Rules for you

- Never start the view yourself, and never try to type into it.
- When the user asks for an action that has an `--agent` command, run that
  command (see the other references). Recommend a slash command only when the
  action has no `--agent` command, or when the user wants to watch the task.
- Name the exact command, for example: "Run `coderabbit code resume <task>`,
  then type `/rename Fix the retry test`."
- The side-effect rules in [SKILL.md](../SKILL.md#side-effects) still apply.
  Recommend a command that creates billed work or changes shared state only
  when the user asked for that action.

## Typing in the view

- Text that does not start with `/` is a message. It queues behind a running
  turn, or starts a turn. Each turn is billed. `//text` sends a message that starts with `/`.
- Type `/` to see suggestions: the best match shows as dim text after the
  cursor, and the matches with a short description show on the input line.
  Tab, or → at the end of the line, accepts the suggestion. Enter never runs a
  partial name.
- Suggestions show only the commands that are available now. A command that
  is not available prints its reason, for example `Push needs a ready patch.`
- A command that cannot run now prints its reason in one muted row. A
  failed server request prints one red `✗` row. The view stays open.
- On an older CodeRabbit server, a command that the server does not support
  prints `This command needs a newer CodeRabbit server.`

## Commands

`Agent mode` names the `--agent` command for the same action, if one exists.

### Turns and messages

| Command                         | What it does                                                               | Agent mode                |
| ------------------------------- | -------------------------------------------------------------------------- | ------------------------- |
| `/steer <text>`                 | Adds guidance to the running turn.                                         | `resume --agent --steer`  |
| `/answer`                       | Answers the agent's question.                                              | `resume --agent --answer` |
| `/cancel` (`/stop`)             | Asks first, then stops the running turn and drops queued messages.         | `cancel`                  |
| `/queue`                        | Lists the queued messages.                                                 | None                      |
| `/queue edit\|delete\|send <n>` | Changes, deletes, or sends now queued message `n`.                         | None                      |
| `/upload <path>…`               | Attaches files to the next message.                                        | None                      |
| `/side <text>`, `/side close`   | Asks a side question while the turn runs, or closes the side chat. Billed. | `ask`                     |
| `/skills [<name> [text]]`       | Lists the library skills, or runs one. Running one is billed.              | None                      |

### Plans

| Command                   | What it does                                           | Agent mode       |
| ------------------------- | ------------------------------------------------------ | ---------------- |
| `/plan`, `/plan comments` | Shows the latest plan, or counts its open comments.    | `plan`           |
| `/approve`                | Approves the latest plan. Not for the task's author.   | `plan --approve` |
| `/implement`              | Switches to code mode and implements the plan. Billed. | None             |
| `/revise <text>`          | Asks the agent to rewrite the plan. Billed.            | None             |
| `/mode [plan\|code]`      | Shows the mode, or switches the mode.                  | None             |

### Delivery and the pull request

| Command                                       | What it does                                                     | Agent mode          |
| --------------------------------------------- | ---------------------------------------------------------------- | ------------------- |
| `/push`                                       | Commits and pushes the changes at once, with no question.        | `push`              |
| `/push --stacked`                             | Opens a new pull request with the changes.                       | `push --stacked`    |
| `/pr`                                         | Shows the health of the pull request.                            | `show` (`prHealth`) |
| `/fix ci\|comments\|conflicts`                | Asks the agent to fix CI, review comments, or conflicts. Billed. | None                |
| `/update-branch`                              | Asks the agent to merge new upstream commits. Billed.            | None                |
| `/autopilot [on\|off\|resume\|status] [--pr]` | Shows or changes Autopilot.                                      | `autopilot`         |

### Task settings

| Command                  | What it does                                                                                         | Agent mode |
| ------------------------ | ---------------------------------------------------------------------------------------------------- | ---------- |
| `/rename <title>`        | Renames the task.                                                                                    | None       |
| `/review [on\|off]`      | Shows, or turns on or off, the CodeRabbit review of the changes.                                     | None       |
| `/access [manual\|full]` | Shows or changes repository access. Full access asks first, then needs a GitHub step in the browser. | None       |
| `/share [private\|team]` | Asks first, then changes who can see the task.                                                       | None       |
| `/subscribe [on\|off]`   | Shows or changes the user's Slack notifications.                                                     | None       |
| `/pin`, `/unpin`         | Pins or unpins the task in the user's task list.                                                     | None       |
| `/archive`, `/unarchive` | Archives the task (asks first; the view becomes read-only), or unarchives it.                        | None       |

### Environment, files, and links

| Command                                | What it does                                                          | Agent mode     |
| -------------------------------------- | --------------------------------------------------------------------- | -------------- |
| `/services`                            | Lists the dev servers of the task.                                    | None           |
| `/start-services`, `/restart-services` | Asks the agent to start or restart the dev servers. Billed.           | None           |
| `/schedule`, `/schedule delete <n>`    | Lists the schedules, or deletes one (asks first).                     | None           |
| `/outputs [save <n>]`                  | Lists the output files, or saves one in the current directory.        | None           |
| `/attachments [save <n>]`              | Lists the attached files, or saves one in the current directory.      | None           |
| `/show`                                | Shows the task details.                                               | `show`         |
| `/web [pr\|slack]` (`/open`)           | Opens the task, its pull request, or its Slack thread in the browser. | `show` (`url`) |
| `/diff`                                | Opens the changes of the task in the browser.                         | None           |
| `/help`                                | Lists the commands.                                                   | None           |
| `/exit`                                | Closes the view. The task keeps running.                              | None           |

A saved file never overwrites an existing file.

## Shell completion

The user can turn on completion of `coderabbit` and `cr` commands, options,
and recent task IDs. Give the line for their shell; do not edit their shell
files yourself.

```sh
eval "$(coderabbit completion bash)"   # ~/.bashrc
eval "$(coderabbit completion zsh)"    # ~/.zshrc, after compinit
coderabbit completion fish | source    # ~/.config/fish/config.fish
coderabbit completion powershell | Out-String | Invoke-Expression  # $PROFILE
```
