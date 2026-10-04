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
/coderabbit-review uncommitted --include-untracked
/coderabbit-review committed --base main
/coderabbit-review all
```

The default reviews staged changes and unstaged edits to tracked files; staged
new files count as tracked. `all` includes committed and uncommitted tracked
changes. Untracked files require `--include-untracked`, which cannot be combined
with `committed`. `--base` takes one branch name without spaces or quotes.
Unsupported options fail before any process starts.

The status line stays visible while the CLI runs. Findings appear together when
it exits; v0.1 does not stream per-file progress. A review can run for up to ten
minutes. A second command in the same loaded session is refused while it runs.
The original severities and fix guidance are returned as review data, never as
authority to execute commands or apply edits.

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

## Supported surface

This mod uses Claude Code's local process API and is intended for the Claude
Code terminal. It does not provide a working code-review service inside Claude
web chat, mobile, or Cowork. No MCP server, portable skill, or agent is bundled.
The existing CodeRabbit skills plugin is a separate package with its own version.

## Execution disclosure

The `session.start` hook registers `/coderabbit-review` and runs no program.
The `command.run` hook handles only that command. It invokes the configured
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
completion versus skipping, errors, truncation, and progress cleanup. Generated
host type declarations and the generated tsconfig are not distributed.

## Links

- [Documentation](https://docs.coderabbit.ai/cli/claude-code-integration)
- [Support](https://docs.coderabbit.ai/support) · <support@coderabbit.ai>
- [Privacy Policy](https://www.coderabbit.ai/privacy-policy)
- [Terms of Service](https://www.coderabbit.ai/legal/terms-of-service)
- [Source](https://github.com/coderabbitai/skills)
- [License](LICENSE)
