---
name: setup
description: Set up CodeRabbit for local code reviews by checking CLI availability, guiding browser sign-in, and continuing a requested first review. Use when the user runs plugin setup or asks to get started with CodeRabbit; use code-review for review-only requests.
---

# CodeRabbit Setup

Help the user reach a working local review workflow. Reuse completed setup and
preserve explicit user restrictions. This skill runs from Codex plugin setup
or a direct setup request; reading it is not authorization to
install software, sign in, or submit code.

## Keep the user's task

If setup follows a review request, retain its repository, directory, scope,
base, and other selectors through installation and sign-in. If the user only
asked for setup, prepare the CLI and offer a first review without starting one.
Ask for a repository only when it is needed for a requested review; CLI setup
can finish without one.

Local reviews do not require setting up the CodeRabbit GitHub App or creating
`.coderabbit.yaml`. Do not install another copy of the plugin or its skills,
change review policies, or enable recurring reviews as part of this flow.

## Find a working CLI

Resolve the official host-installed `coderabbit` using the user's normal shell,
checking `~/.local/bin/coderabbit` if lookup fails. Validate its canonical target;
reject repository, workspace, temporary, alias, or untrusted wrapper executables.
Use the quoted trusted absolute path for every CLI command. Examples below use
`"/absolute/path/to/coderabbit"` to stand for that verified path.

Run `--version` and any needed `--help` in the agent's normal execution context. A missing runtime,
a signature error, or a killed process is an execution problem,
not evidence that the user is signed out. Explain the specific prerequisite.
If the CLI is missing, use the [official installation guide](https://docs.coderabbit.ai/cli)
and obtain installation authorization unless already given. For a new macOS or
Linux installation, use the official installer:

```sh
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

For Windows, follow the official guide's platform-specific instructions. Preserve
the requested region: EU users should skip installer sign-in if it does not offer
a region choice, then use explicit EU login below.
Recheck availability after installation. Do not upgrade a working installation
just to complete setup; check installed help before using an unfamiliar option.

## Check sign-in in the right environment

In a local agent sandbox, use the harness's command-scoped host execution for
the trusted CLI's `auth status --agent`, an authorized `auth login --agent`, and
the requested review, using that agent's own permission controls and a
command-specific justification. Use one direct CLI command;
do not wrap it in a shell or change global permissions. If unavailable or denied,
report the blocker. Host-native agents use their normal execution context.

Remote agents use only the CLI and authentication available in their own
environment. They cannot reach a user's local credentials through escalation.
Never retrieve, copy, print, or request credentials, tokens, or callback codes.

Run `"/absolute/path/to/coderabbit" auth status --agent` in that context:

- A successful `authenticated: true` skips login. Keep the existing account and
  organization unless the user asks to change them.
- A successful `authenticated: false` needs sign-in. A sandbox result alone is
  not proof of host logout. `credentials_unavailable` and
  `callback_listener_unavailable` indicate an access problem.
- Failed or malformed output means unknown. Report the error instead of starting
  login or repeatedly retrying.

For explicitly requested setup, explain that browser sign-in is the next step
and run `"/absolute/path/to/coderabbit" auth login --agent` when needed. Check
installed `auth login --help` first; if agent login is unsupported, give the
supported terminal login command instead of passing an unknown flag. Honor
setup-only restrictions such as "check readiness without signing in". Preserve
a requested SaaS region using the login command's supported `--region` option.
For API-key or self-hosted setup, consult the existing
[authentication modes](../code-review/references/cli-workflows.md) and the official
docs; do not replace the user's chosen mode with browser OAuth.

Show the CLI's sign-in URL promptly and keep that same login process alive while
the user completes the browser flow. Do not request a pasted token or callback
URL. Agent login needs a browser that can reach that process's localhost callback;
if that is unavailable, explain the boundary and give the exact supported terminal
login command. Cancellation or failure is not success and must not trigger a
login loop. After successful login, verify `auth status --agent` in the same
execution context before continuing.

## Continue the first review

When a review was requested and authentication is confirmed, follow the packaged
[code-review skill](../code-review/SKILL.md) with the original repository and
selectors. Confirm the directory is in a Git working tree. Explain that selected
code is sent to CodeRabbit and check it for secrets without printing them.
Setup does not authorize extra credit spending or broader review scope.

Keep the review process alive through its expected duration; use the CLI's
duration guidance when available. Use a background process or a timeout of at
least fifteen minutes, and do not restart a healthy review just because time
passed. Report actual findings and completion,
distinguishing a skipped review, partial results, and failure. Never create a
synthetic change or force a fresh review just to demonstrate setup.

Close with what is ready, whether a review actually completed, and any remaining
blocker. For setup without a review request, offer: "Review my current changes
with CodeRabbit." A verified login alone is not a completed first review.
