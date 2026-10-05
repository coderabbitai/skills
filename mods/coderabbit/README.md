# CodeRabbit Review Mod

Version 0.1.0 brings an explicit CodeRabbit review command to Claude Code. Run a
review, see its running status, and receive the original findings in the
conversation. Reviews never start automatically after edits, and the mod never
applies fixes.

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
/coderabbit-review --help
/coderabbit-review
/coderabbit-results
/coderabbit-review uncommitted --include-untracked
/coderabbit-review committed --base main
/coderabbit-review all
```

The default reviews staged changes and unstaged edits to tracked files; staged
new files count as tracked. `all` includes committed and uncommitted tracked
changes. Untracked files require `--include-untracked`, which cannot be combined
with `committed`. `--base` takes one branch name without spaces or quotes.
Unsupported options fail before any process starts.

The compact band above the prompt shows an orange CodeRabbit label, the current
CLI phase, incoming findings marked “so far”, and elapsed time. Status events
change the sentence as the CLI connects, prepares, maps code, summarizes, and
writes review comments. Heartbeats do not invent progress or change the phase.
**Activity** expands scope, severity counts, and the last event time. The final
outcome stays visible with **Details**; file counts appear only when the CLI
supplies them on successful completion. The **×** dismisses the bar without
cancelling a review or its notification; a new review shows it again. Narrow
surfaces wrap the row.

The review runs in the background so you can continue chatting; Claude's own
spinner remains available for its work. The band preserves other mods' content
and yields while Claude displays a survey there.

Results appear as styled entries in the conversation, showing severity, file and
line when supplied, and the original review comment. **Show suggested change**
expands suggestions supplied by the CLI; the button is absent when there are none.
A short opening sentence or clause becomes the finding heading, using the original
wording; longer prose uses the file location as its heading. Major and critical
labels use the brand accent; other severity labels are subdued. The mod never
invents diagnoses or patches. **Ask Claude to fix** appends a request
and the selected finding to the prompt without sending it or replacing existing
text. You review and send the draft yourself.

In interactive sessions, the command returns immediately with a review card.
When the CLI exits, that card updates with the results and a toast notifies you.
The mod submits a bounded result record as a plugin-attributed prompt, waking
Claude into a new turn once the session is idle. The internal delivery row is
hidden from the conversation view; the CodeRabbit card and Claude's reply remain.
Claude is asked to acknowledge completion in one short sentence without repeating
the findings or changing their severities, unless you have already requested action.
The stored record and model context keep the original payload and provenance.
Desktop marks this delivery as SDK-originated, so its render hook also requires
the exact CodeRabbit frame and a matching known result before hiding it.
It does not interrupt a running turn or fill your prompt box. Each completed review attempt, including a failure
or rate limit, can therefore use your normal Claude model allowance. Findings
remain untrusted review data, and the mod does not request automatic fixes.
Run **/coderabbit-results** to show the latest result again, including if a hook
refused the wake-up prompt. Your prompt draft is left intact.

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
- **Skipped:** the CLI performed no new analysis, including a review it skipped
  because no selected changes needed reviewing.
- **Failed or incomplete:** a process error, missing completion, invalid output,
  count mismatch, or truncated process output leaves coverage unverified.

The mod never automatically retries, installs software, starts login, requests
usage credits, or widens the selected scope. On authentication errors run
`coderabbit auth status`, then `coderabbit auth login` if needed. If the response
says its display was truncated, inspect the CLI's saved findings with
`coderabbit review findings` in the same workspace.

Rate limits appear as a compact “Taking a breather” card with the CLI-reported
wait estimate. Expand **Limit details** for account requirements and review usage
links. A rate-limited review remains incomplete; the mod never retries automatically.

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

The `session.start` hook registers `/coderabbit-review` and `/coderabbit-results`,
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
On background completion, `$.prompt.submit` queues one result notification in
this same conversation, using the host's normal model turn and plugin attribution.

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
starts a normal Claude turn through the host. Credentials remain
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
finding updates, timeout closure, session reset, wake-up delivery and refusal,
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
