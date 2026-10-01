# CodeRabbit execution in Codex

## Execution Context and Authentication

1. Confirm the working directory is inside a git repository.
2. Resolve the trusted, host-installed `coderabbit` executable from the user's
   normal shell. If shell lookup finds nothing, check the installer's default
   `~/.local/bin/coderabbit` before concluding it is missing. Do not use a
   repository- or workspace-controlled executable, alias, wrapper, or symlink
   target. Use the resolved absolute path for all commands below.
3. Run `coderabbit --version`. If no trusted host installation is found, ask
   the user for its installed path; if there is none, ask them to install the
   CLI from <https://www.coderabbit.ai/cli>. Do not install
   it automatically. A killed process or signature error is an execution
   failure, not missing authentication. Commands below use `coderabbit` for
   readability; invoke the resolved absolute path.

Codex Cloud and other remote environments cannot reuse a local host credential
store, and escalation there does not reach it. In those environments, use only
the CLI and authentication configured inside that environment and direct the
user to the official CLI documentation when setup is required. Never ask the
user to paste an API key into the conversation.

For local Codex sessions (desktop or CLI, including worktrees), execute the
resolved CodeRabbit CLI with the harness's command-scoped sandbox escalation so
that exact process runs on the host with network access. Sandbox network
permission alone is insufficient because the CLI also needs its host credential
store and its `~/.coderabbit` state. Apply the same execution context to
`coderabbit review` and any reactive authentication command. `--version` and
`--help` need no host access; run them in the sandbox. Do not change global
sandbox settings or run repository-provided commands outside the sandbox.

If the session already runs with full access, run the CLI directly. Otherwise,
when the shell tool exposes `sandbox_permissions`, use `require_escalated` for
the resolved absolute CLI command with a command-specific justification. Run it
as one plain command: the resolved path and its arguments, with no environment
assignments, pipes, redirects, or command substitution. Default to one-time
approval: omit `prefix_rule` unless the user asks to allow future runs. When
requested, propose a `prefix_rule` of the resolved path plus its subcommand, such as
`["/path/to/coderabbit", "review"]` or
`["/path/to/coderabbit", "auth", "status"]`, so the user can choose to allow
future runs. Never propose a program-only or shell prefix. A saved prefix lets
matching commands run outside the sandbox in any repository and with any flags,
including `--use-credits`; say so in the justification. It is not consent for a
new review or for spending, and managed policy may still ignore it. Request the
harness's normal approval when needed. If host execution is unavailable or
denied, report that prerequisite and stop; do not silently fall back to the
sandbox or broaden permissions.

Never query, copy, print, or inject a credential from macOS Keychain or another
host credential store. The trusted CodeRabbit CLI must access its credential
directly. A Git worktree or repository change does not require a separate login.

Do not proactively check authentication before every review. Start the requested
review directly. After a pre-review authentication failure, use this bounded
recovery sequence:

1. Recognize `status: "credentials_unavailable"` or
   `status: "callback_listener_unavailable"` as local access failures, not proof
   that the user is signed out. Older CLIs may instead emit an auth error or
   `authentication_failed` with `Failed to start server. Is port 0 in use?`.
   That legacy callback message does not establish a port collision.
2. Run the trusted CLI's `auth status --agent` through approved host execution.
   A sandbox's `authenticated: false` is not authoritative for host credentials.
3. If host status reports `authenticated: true` and the failed review ran in the
   sandbox, retry the original review once on the host. Preserve its working
   directory and all review arguments. Never retry a review already running,
   completed, or failed after remote analysis began. Do not use this recovery for
   network, rate-limit, billing, or review failures.
4. If host status reports `authenticated: false`, ask the user to run
   `coderabbit auth login --agent` in their host terminal. Do not start login
   automatically. After the user confirms login, check `auth status --agent` on
   the host again and resume the original review if it reports authenticated.
   If host status itself fails or credentials remain unavailable, report the
   exact failure and stop. Do not blindly retry a review that failed on the host
   with valid credentials.

Structured statuses are additive: do not require an upgrade to recognize the
legacy failure path, and do not infer missing authentication from an absent
status field alone.

## Review context and active sessions

If `AGENTS.md`, `.coderabbit.yaml`, or `CLAUDE.md` exists, pass relevant
instruction files with `-c` when starting the requested review.

While a review is active, avoid repetitive polling commentary. A tool result
that returns a session ID means the review is still running: keep polling that
same session until the CLI exits, retaining partial NDJSON lines across chunks.
Allow at least ten minutes before declaring a timeout, and do not kill or
restart a live review just because time passed. A terminal error ends that
wait: use the recovery procedure above for a pre-review auth failure, and
report other failures. Never replace a failed CodeRabbit review with an
unlabelled manual review.
