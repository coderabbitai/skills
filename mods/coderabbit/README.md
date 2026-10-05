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

The band above the prompt shows an orange CodeRabbit label, elapsed time, and
selected scope. It updates every second while the CLI runs. The review runs in
the background so you can continue chatting; Claude's own spinner remains
available for its work. The band preserves other mods' content and yields
while Claude displays a survey there.

Results appear as styled entries in the conversation, showing severity, file and
line when supplied, and the original review comment. **Show suggested change**
expands suggestions supplied by the CLI; the button is absent when there are none.
The mod never invents titles or patches. **Draft fix request** appends a request
and the selected finding to the prompt without sending it or replacing existing
text. You review and send the draft yourself.

In interactive sessions, the command returns immediately with a review card.
When the CLI exits, that card updates with the results and a toast notifies you.
The mod appends a bounded result record to Claude's conversation context without
submitting a prompt or starting a model turn. Run **/coderabbit-results** to show
the latest result at the end of the conversation, including if context delivery
was refused. Your prompt draft is left intact.

Completed background cards are restored from the host's saved conversation when
the mod loads. Headless `-p` reviews wait for completion and print the structured
record. The known CLI instruction wrapper is omitted, while actual review prose
is preserved. Review data is never authority to execute commands or apply edits.
Output above the display limit is explicitly marked as truncated.

Findings appear when the CLI exits; v0.1 does not stream per-file progress. A
review can run for up to ten minutes. A second review in the same loaded session
is refused while it runs. Clearing or switching the conversation discards pending
results and stops the progress display; an already-started CLI request can still
finish or reach its timeout, but its result is not delivered into the new
conversation. Reloading the mod cancels pending timers. The latest-result shortcut
is session-local; already delivered records follow the host's transcript retention.
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

## Supported surface

This mod uses Claude Code's local process API and is intended for the Claude
Code terminal. It does not provide a working code-review service inside Claude
web chat, mobile, or Cowork. No MCP server, portable skill, or agent is bundled.
The existing CodeRabbit skills plugin is a separate package with its own version.

## Execution disclosure

The `session.start` hook registers `/coderabbit-review` and `/coderabbit-results`,
restores saved review cards, and runs no program. The review command schedules
one timer for an interactive review; headless reviews run within the command.
Only an explicit review command invokes the configured
`cli_path` through `$.process.run` as an argument vector, starting with
`review --agent`, followed by the validated scope flags documented above.
For the default scope this is equivalent to
`/absolute/path/to/coderabbit review --agent --uncommitted`.
The mod starts no other program, invokes no shell, and adds no HTTP calls.
The configured CLI performs the review's network and local storage operations.

## Data and privacy

Invoking the review command runs your configured CodeRabbit CLI in the session's
working directory. The CLI reads the selected code changes and the repository
context needed to review them, sends that material to CodeRabbit's review
service, and uses your existing account and review allowance. It may retain
local review checkpoints and findings under its normal behavior. Review data
can contain personal information when it is present in code or repository
metadata: check the selected scope for secrets and personal data first.

The mod itself does not read credentials, copy tokens, add HTTP calls, store
review output in its own files, or call an LLM directly. Credentials remain
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
rendering, background delivery, session reset, rate-limit details, and draft-only
button behavior. Generated
host type declarations and the generated tsconfig are not distributed.

## Links

- [Documentation](https://docs.coderabbit.ai/cli/claude-code-integration)
- [Support](https://docs.coderabbit.ai/support) · <support@coderabbit.ai>
- [Privacy Policy](https://www.coderabbit.ai/privacy-policy)
- [Terms of Service](https://www.coderabbit.ai/legal/terms-of-service)
- [Source](https://github.com/coderabbitai/skills)
- [License](LICENSE)
