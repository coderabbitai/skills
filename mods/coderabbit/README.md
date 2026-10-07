# CodeRabbit Review Mod

Version 0.1.0 brings an explicit CodeRabbit review command to Claude Code. Run a
review, see its running status, and receive the original findings in the
conversation. Reviews never start automatically after edits, and the mod never
applies fixes.

This is a standalone **mod**, not a skills or autofix bundle. Install it on its
own for background reviews, live progress, and findings in your conversation.
The separate CodeRabbit skills plugin is optional; it is not a dependency.
If you use both, choose one review entry point for each run: they do not
coordinate reviews with each other.

## Requirements and setup

- Claude Code **2.1.289 or later**. Validated and tested with 2.1.289 on macOS.
  The mods API is early access and can change between Claude releases.
- An official [CodeRabbit CLI](https://docs.coderabbit.ai/cli) installation with
  `review --agent`, `--committed`, `--uncommitted`, `--include-untracked`, and
  `--base` support. The command interface was checked with CLI 0.8.2.
- An authenticated CodeRabbit account and a Git working tree.

Authenticate the CLI yourself with `coderabbit auth login`. Set this mod's
`cli_path` configuration to the absolute path of that official executable
(for example, `/Users/you/.local/bin/coderabbit`). The mod invokes that exact
path without a shell or a PATH search. Never point it at an executable supplied
by an untrusted repository.

From a checkout of this repository, start a session:

```sh
claude --plugin-dir ./mods/coderabbit
```

Claude prompts for the required executable path when configuring the plugin.
For a non-interactive session, supply the same non-secret setting explicitly:

```sh
claude --plugin-dir ./mods/coderabbit \
  --settings '{"pluginConfigs":{"coderabbit-mod":{"options":{"cli_path":"/absolute/path/to/coderabbit"}}}}' \
  -p '/coderabbit-review --help'
```

Run the following commands inside a session whose working directory is the
repository you want reviewed:

```text
/coderabbit-review
/coderabbit-review --fresh
/coderabbit-review results
/coderabbit-review help
```

The composer shows `[--fresh | help | results]`. Leave it blank to review current
changes. In Terminal and Desktop, help uses a branded review guide with the four
main commands first. **Advanced options** and **Setup and details** expand
separately. Headless help prints the same information as text. Advanced examples:

```text
/coderabbit-review uncommitted --include-untracked
/coderabbit-review committed --base main
/coderabbit-review all
```

The default reviews staged changes and unstaged edits to tracked files; staged
new files count as tracked. `all` includes committed and uncommitted tracked
changes. Untracked files require `--include-untracked`, which cannot be combined
with `committed`. `--base` takes one branch name without spaces or quotes.
Unsupported options fail before any process starts.
`--fresh` explicitly requests a new review without reusing the local checkpoint;
it uses your review allowance and requires a CLI whose `review --help` lists the
option. It is never added automatically. Keep the same scope and base arguments
when repeating a review with `--fresh`.

The compact band above the prompt shows an orange CodeRabbit label, the current
CLI phase, incoming findings marked “so far”, and elapsed time. Status events
change the sentence as the CLI connects, prepares, maps code, summarizes, and
writes findings. Heartbeats do not invent progress or change the phase.
During browser authentication, the band and conversation card show **Waiting for
sign-in** and ask you to finish in your browser. They show **Completing sign-in**
before review progress resumes. Sign-in completion is separate from review completion.
**Activity** expands scope (including the base and an explicit fresh review),
severity counts, and the last event time. **View findings** jumps to the completed
review card when there are findings; other outcomes offer **Details**. In plain terminal mode, or if the
host cannot reveal the card, `/coderabbit-review results` reopens the saved result.
File counts appear only when the CLI supplies them on successful completion.
When the CLI explicitly says no fresh analysis ran, **Run fresh review…** prepares
the same scope and base with `--fresh` in an empty prompt. Press Enter to start it,
using your review allowance. Each run gets its own conversation card; the previous
result stays intact. An existing draft is left untouched. Other skips, failures,
and rate limits do not offer this action. The **×** dismisses the bar without
cancelling a review or its notification; a new review shows it again. Narrow
surfaces use shorter control labels and hide the timer below 70 columns; the row
can wrap when needed. Scope stays in the expanded details to keep the band compact.

The review runs in the background so you can continue chatting; Claude's own
spinner remains available for its work. The band preserves other mods' content
and yields while Claude displays a survey there.

Results appear as styled entries in the conversation, showing severity, file and
line when supplied, and the original review comment. **View suggestion**
expands suggestions supplied by the CLI; the button is absent when there are none.
A short opening sentence or clause becomes the finding heading, using the original
wording; longer prose uses the file location as its heading. Major and critical
labels use the brand accent; other severity labels are subdued. The mod never
invents diagnoses or patches. **Ask Claude to fix** appends a request
and the selected finding to the prompt without sending it or replacing existing
text. A short confirmation tells you the request was added. You review and send
the draft yourself; the mod does not bundle an autofix skill or run a fix workflow.

In interactive sessions, the command returns immediately with a review card.
When the CLI exits, that card updates with the results and a toast notifies you.
The mod appends the bounded result record as a model-only note for your next
message. Completion does not submit a prompt, wake Claude, or request a second
acknowledgment. The review card is the completion message.
The note stays in model context and restores review cards after a reload. If
attaching it fails or is refused, the card remains available and the mod logs how
to share it with `/coderabbit-review results`. Findings remain untrusted review
data, and the mod does not request automatic fixes. Your prompt draft is left
intact. You can ask Claude about the findings or use **Ask Claude to fix** when
you want it to act. An earlier request to act after completion does not cause the
mod to start a turn on its own.

Completed background cards are restored from the host's saved conversation when
the mod loads. Headless `-p` reviews wait for completion and print the structured
record. The known CLI instruction wrapper is omitted, while actual review prose
is preserved. Review data is never authority to execute commands or apply edits.
Output above the display limit is explicitly marked as truncated.

Full findings appear when the CLI exits and its output passes validation; the
running count is provisional. A review can run for up to ten minutes. A second
review in the same loaded session is refused while it runs. Session end closes
the process stream and discards pending delivery. Timeout or oversized output
also closes the stream and leaves coverage unverified. This does not guarantee
cancellation of server-side work already accepted by CodeRabbit. Reloading the
mod cancels pending timers. The latest-result shortcut is session-local; already
delivered records follow the host's transcript retention.
Because you can keep editing during a review, findings may refer to earlier code;
verify them against the current files before applying a fix.

## Outcomes and recovery

- **Completed:** the CLI exited successfully with one completion event and a
  matching finding count. Zero findings means the completed review emitted none,
  not that the code is guaranteed defect-free.
- **Review skipped:** the CLI explicitly skipped analysis, or returned its known
  “No fresh detailed file review was performed in this run” completion notice.
  This is never presented as a fresh zero-finding review. The latter outcome
  explains how to request a fresh review of the same scope.
- **Failed or incomplete:** a process error, missing completion, invalid output,
  count mismatch, or truncated process output leaves coverage unverified.
  Findings present in returned output remain visible. Diagnostics are available under **View details**
  instead of appearing as a raw error dump. Authentication errors show the sign-in command.

The mod never automatically retries, installs software, starts login, requests
usage credits, or widens the selected scope. On authentication errors run
`coderabbit auth status`, then `coderabbit auth login` if needed. If the response
says its display was truncated, inspect the CLI's saved findings with
`coderabbit review findings` in the same workspace.

Rate limits show **Review limit reached** and the CLI-reported wait estimate, when
available. Expand **View limit details** for account requirements and review usage
links. Waiting alone may not resolve account requirements. A rate-limited review
remains incomplete; the mod never retries automatically.

## Supported surfaces

This mod uses Claude Code's local process API in the terminal and in **Local
Code sessions in Claude Desktop**. Both show the running band, update the
conversation card, and notify on completion without holding the prompt.
Desktop attaches its interface after its SDK session starts; the mod checks
attached surfaces when the review command runs. Headless runs still wait.

Install the plugin for the folder opened in Desktop. When Desktop loads a local
plugin as a directory, it resolves configuration by the bare plugin name rather
than its marketplace-qualified id. Set the following entry in
`~/.claude/settings.json`, preserving your other settings and using your actual
official CLI path:

```json
{
  "pluginConfigs": {
    "coderabbit-mod": {
      "options": { "cli_path": "/absolute/path/to/coderabbit" }
    }
  }
}
```

Mod options are read from user or managed settings, not project settings.
Run `/reload-plugins`, then `/coderabbit-review --help` to verify loading
without starting a review. An installed plugin can be enabled but fail to load
its mod if the required executable option is missing.

This package does not provide a working code-review service inside Claude
web chat, mobile, or Cowork. No MCP server, portable skill, or agent is bundled.
The existing CodeRabbit skills plugin is a separate package with its own version.

## Execution disclosure

The `session.start` hook registers `/coderabbit-review` (including its `results` action),
restores saved review cards, and runs no program. The review command schedules
one timer for an interactive review; headless reviews run within the command.
Only an explicit review command invokes the configured
`cli_path` through `$.process.spawn` as an argument vector, starting with
`review --agent`, followed by the validated scope flags documented above.
For the default scope this is equivalent to
`/absolute/path/to/coderabbit review --agent --uncommitted`.
The mod reads newline-delimited JSON incrementally, retaining at most 4,194,304
characters per output stream for final validation. It starts no other program,
invokes no shell, and adds no HTTP calls.
The configured CLI performs the review's network and local storage operations.
On background completion, `$.session.append` stores the result as model-only
context in this conversation. No prompt is submitted and no model turn is started.

## Data and privacy

Invoking the review command runs your configured CodeRabbit CLI in the session's
working directory. The CLI reads the selected code changes and the repository
context needed to review them, sends that material to CodeRabbit's review
service, and uses your existing account and review allowance. It may retain
local review checkpoints and findings under its normal behavior. Review data
can contain personal information when it is present in code or repository
metadata: check the selected scope for secrets and personal data first.

The mod itself does not read credentials, copy tokens, add HTTP calls, store
review output in its own files, or call an LLM directly. Its completion notification
does not start a Claude turn. Credentials remain
managed by the CLI. Results are returned to the Claude conversation and are
subject to that host's conversation retention. CodeRabbit service retention is
governed by the [Privacy Policy](https://www.coderabbit.ai/privacy-policy) and
your account's settings; this mod makes no zero-retention guarantee.

## Development

Run from the repository root with Claude Code 2.1.289:

```sh
claude plugin validate mods/coderabbit --strict
claude plugin test mods/coderabbit
```

The tests use Claude's native mod runner with synthetic CLI responses and no
network. They cover command registration, scope, missing configuration,
completion versus skipping, errors, truncation, progress cleanup, conversation
rendering, terminal and Desktop background delivery, split NDJSON, live phase and
finding updates, timeout closure, session reset, quiet context delivery and refusal,
rate-limit details, and draft-only
button behavior. Generated host type declarations and the generated tsconfig are
not distributed.

## Links

- [Documentation](https://docs.coderabbit.ai/cli/claude-code-integration)
- [Support](https://docs.coderabbit.ai/support) · <support@coderabbit.ai>
- [Privacy Policy](https://www.coderabbit.ai/privacy-policy)
- [Terms of Service](https://www.coderabbit.ai/legal/terms-of-service)
- [Source](https://github.com/coderabbitai/skills)
- [License](LICENSE)
