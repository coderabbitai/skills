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
This standalone mod intentionally defaults to `uncommitted`; the separate
code-review skill follows the CLI's broader default. Use `/coderabbit-review all`
to select that scope explicitly.
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
When the CLI explicitly says no fresh analysis ran, **Run fresh review…** suggests
the same scope and base with `--fresh` in an empty prompt. Accept the suggestion
with Tab, then press Enter to start it, using your review allowance. Claude shows
no suggestion while the prompt contains text, a turn is running, or no prompt is
available. The mod does not read your draft. Each run gets its own conversation
card; the previous result stays intact. An existing draft is left untouched.
Other skips, failures, and rate limits do not offer this action. The **×** dismisses the bar without
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
invents diagnoses or patches. **Fix with Claude** appends a request
and the selected finding to the prompt without sending it or replacing existing
text. A short confirmation tells you the request was added. You review and send
the draft yourself; the mod does not bundle an autofix skill or run a fix workflow.

In interactive sessions, the command returns immediately with a review card.
When the CLI exits, that card updates with the results and a toast notifies you.
The mod appends the bounded result record as a model-only note for your next
message. Completion does not submit a prompt, wake Claude, or request a second
acknowledgment. The review card is the completion message.
The note stays in model context. Review cards restore from the plugin store after a reload. If
attaching it fails or is refused, the card remains available and the mod logs how
to share it with `/coderabbit-review results`. Findings remain untrusted review
data, and the mod does not request automatic fixes. Your prompt draft is left
intact. You can ask Claude about the findings or use **Fix with Claude** when
you want it to act. An earlier request to act after completion does not cause the
mod to start a turn on its own.

Completed background cards are saved in Claude's plugin-owned store, one record
per review, keyed by the review id that the card itself carries. When Claude draws
a CodeRabbit card, including after a reload, `/resume`, or `/branch`, the mod reads
only that card's record. It does not read the session id or conversation history.
Cards saved by earlier builds under session-keyed records, or only in the
transcript, cannot be restored by this version; their model-context notes remain
in that conversation. Headless `-p` reviews wait for completion and print the structured
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
delivered context notes follow the host's transcript retention. Stored cards follow
Claude's plugin-store retention, described below.
Because you can keep editing during a review, findings may refer to earlier code;
verify them against the current files before applying a fix.

## Outcomes and recovery

Finding cards use the CLI's human-readable title, explanation, and line range when
supplied; in that case, agent instructions stay behind **Fix with Claude**.
When older CLI versions omit the human fields, the card instead shows the complete
instruction text with severity and location. The mod does not invent a title or
split sentences to make one.

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
Desktop attaches its interface after its SDK session starts; the mod notes that
attachment when Desktop asks the mod to draw the band above the prompt.
Headless runs, which nothing draws for, still wait.

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

## What this mod runs, reads, and sends

This section is the mod's disclosure for directory review. Every program, data
flow, and hook below is in `hooks/register.js`.

### Programs it runs

The mod runs exactly one program: **your installed official CodeRabbit CLI**, to
perform the code review you asked for. It runs nothing else, invokes no shell,
searches no PATH, and installs nothing.

- **The call:** `$.process.spawn({ argv: [options.cli_path, ...args] })` in
  `hooks/register.js`. It runs only when you type `/coderabbit-review` (or accept
  the **Run fresh review…** suggestion and send it). Edits, ordinary chat
  messages, session start, and other commands never start it.
- **Why the command is not fixed text:** the program path is `cli_path`, the
  absolute path you set in this plugin's configuration (user or managed
  settings, never project settings), because the CLI installs to a different
  place on each machine. The arguments come from `reviewArgs` in
  `hooks/review.js`, which accepts only the options listed here and rejects
  everything else before any process starts. Each option and the branch name are
  separate argv entries, never shell text.
- **Every command it can run**, where `/path/to/coderabbit` is your `cli_path`:

  | You type | The mod runs |
  | :- | :- |
  | `/coderabbit-review` or `/coderabbit-review uncommitted` | `/path/to/coderabbit review --agent --uncommitted` |
  | `/coderabbit-review committed` | `/path/to/coderabbit review --agent --committed` |
  | `/coderabbit-review all` | `/path/to/coderabbit review --agent` |
  | add `--include-untracked` (not with `committed`) | the same, plus `--include-untracked` |
  | add `--base <branch>` | the same, plus `--base` and `<branch>`: one branch name, no spaces or quotes |
  | add `--fresh` | the same, plus `--fresh` |

  `help`, `--help`, and `results` start no program. Conversation text, findings,
  prompt drafts, and session data are never passed as arguments.
- **Lifetime:** one review at a time, closed after 10 minutes, on session end,
  or when an output stream exceeds 4,194,304 characters. The mod reads the CLI's
  newline-delimited JSON output as it arrives.

### What it reads and sends, and where

- **Sent to CodeRabbit, by the CLI:** the CodeRabbit CLI reads the selected
  changes and the repository context it needs from the session's working
  directory and sends them to CodeRabbit's review service with your existing CLI
  login.
- **Sent to Claude, by Claude Code:** the review result the mod adds to this
  conversation, as the card and as a model-only note (`$.session.append`), is
  part of the conversation. Claude Code sends it to Claude with your next
  message, as it does the rest of the conversation.
- **Nothing else:** the mod itself makes no HTTP calls, sends no telemetry, and
  calls no model. The two routes above are the only ways review data leaves the
  machine.
- **Read by the mod:** the CLI's output, and the CodeRabbit records it saved in
  Claude's plugin store, one per review id. It calls no `$.session` method to
  read session facts: no session id, attached surfaces, conversation history,
  prompt drafts, credentials, or environment variables. Nothing it reads is
  passed to the CLI as an argument.
- **Written by the mod, locally:** the review result goes into this
  conversation as the review card, as a model-only note (`$.session.append`), and
  as a record in the plugin store (`$.store`, at most the 50 newest reviews).
  Nothing it stores is forwarded to the CLI.
- **Prompt actions:** `$.prompt.suggest()` offers a fresh-review command and
  `$.prompt.fill()` adds a selected finding's fix request to the prompt box. Both
  leave sending to you; neither reads your draft.

### Hooks

- **`command.run`**, filtered to `/coderabbit-review` only: answers `help` and
  `results` without starting a program, or validates the requested scope and
  starts the CLI as described above. It does not see, change, or block any other
  command, and the mod never calls `$.command.run` itself.
- **`session.start`**: registers the `/coderabbit-review` command and runs no
  program. **`session.end`**: cancels a running review and clears session-local
  state, including on `/clear`, `/resume`, and `/branch`.
- **`ui.render`** on `AbovePrompt` and on `CommandOutput` rows of
  `/coderabbit-review`: draws the progress band and review cards, and loads a
  card's saved record. When an app other than the terminal, such as Desktop,
  asks for the band, the mod notes that someone can see a background review; a
  headless `-p` run, which nothing draws for, waits for the result instead.
  **`ui.press`**, filtered to the band's own
  `review-again` button: suggests the fresh-review command.
- The mod registers no `classic.*` hooks, no tools, and no agents, and does not
  rewrite settings, instructions, tool descriptions, prompts, or other hooks.

The CLI's own network, credential, and storage behavior is CodeRabbit's review
service, described below. These disclosures do not claim that the CLI is
sandboxed.

## Data and privacy

Invoking the review command runs your configured CodeRabbit CLI in the session's
working directory. The CLI reads the selected code changes and the repository
context needed to review them, sends that material to CodeRabbit's review
service, and uses your existing account and review allowance. It may retain
local review checkpoints and findings under its normal behavior. Review data
can contain personal information when it is present in code or repository
metadata: check the selected scope for secrets and personal data first.

The mod itself does not read credentials, copy tokens, add HTTP calls, or call an
LLM directly. It saves completed review output (including code excerpts in findings)
in Claude's plugin-owned JSON store under `~/.claude/plugins/store/`, one record
per review id, keeping the 50 newest. It stores no conversation history, prompt
drafts, or session ids there. Claude
removes the store after no session reads or writes it for `cleanupPeriodDays`;
this is an inactivity policy, not a per-record expiry. The host caps the entire
store at 4 MiB. If saving fails, results remain visible in the current session
and the mod reports that they may not restore after reload. Its completion notification
does not start a Claude turn. Credentials remain
managed by the CLI. Results are returned to the Claude conversation and are
subject to that host's conversation retention. CodeRabbit service retention is
governed by the [Privacy Policy](https://www.coderabbit.ai/privacy-policy) and
your account's settings; this mod makes no zero-retention guarantee.

## Development

### API compatibility evidence

Checked against the official documentation on 2026-10-07:

- [Mod files and reference](https://code.claude.com/docs/en/plugins/mods/reference):
  `.claude-plugin/plugin.json`, `hooks/hooks.json` with `modules`, and the exported
  `register(on, options)` entry point match this package. The reference lists
  the session, prompt, process, clock, command, and UI namespaces used here.
  For exact signatures, it identifies the declarations generated by the installed
  Claude Code version as authoritative over an older published copy.
- [Mods API](https://code.claude.com/docs/en/plugins/mods/api): command registration
  in `session.start` and handling through `command.run`, background clock callbacks,
  streaming processes through `$.process.spawn`, and toasts without a new model
  turn are documented. This mod uses those mechanisms, not shell-command hooks.
- [Interface rendering](https://code.claude.com/docs/en/plugins/mods/interface):
  `AbovePrompt` is the band above the input; `CommandOutput` is the command's
  conversation row. The mod preserves the next renderer when composing its band.
- [CodeRabbit CLI reference](https://docs.coderabbit.ai/cli/reference):
  `review --agent`, `--uncommitted`, `--committed`, `--include-untracked`,
  `--base`, and `--fresh` are documented options. The mod maps `all` to a review
  with no scope flag; its intentional default explicitly adds `--uncommitted`.

Claude Code 2.1.289 strict validation and the native test runner check the actual
host declarations and behavior. Public documentation alone does not establish
successful authentication or review-service coverage.

### Local checks

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
