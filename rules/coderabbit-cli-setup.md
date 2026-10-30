---
trigger: model_decision
description: Use when a CodeRabbit review is requested in Antigravity and the CodeRabbit CLI is missing, or a review subagent returns CLI_SETUP_REQUIRED.
---

# Install a missing CodeRabbit CLI

Run this setup in the main conversation, never in a review subagent. When a
subagent returns `CLI_SETUP_REQUIRED`, complete setup here and then resume the
review. Explain that setup is starting. Do not ask the user to install the CLI
manually while this procedure applies.

## Establish whether installation is needed

Check PATH and the official default location, `~/.local/bin/coderabbit`. Resolve
any candidate to its canonical absolute path and apply the trust checks in
[authentication and recovery](../skills/code-review/references/auth-recovery.md).
If a trusted CLI already exists, reuse it without reinstalling or upgrading it.
A CLI hidden by the sandbox, an untrusted candidate, a broken installation, or
an execution error is not proof that the CLI is absent. Report that blocker
rather than replacing it.

## Install on macOS or Linux

On any other platform, report it and link the
[official CLI setup guide](https://docs.coderabbit.ai/cli).

1. Check that `curl`, `unzip`, `git`, and a POSIX shell are available, plus
   `openssl` on Linux and `shasum` or `sha256sum` on macOS. If any is missing,
   report the exact blocker and link the official CLI setup guide. Do not
   install unrelated dependencies or use administrator privileges.
2. Check for command collisions. Test both `~/.local/bin/coderabbit` and
   `~/.local/bin/cr` with tests that also detect dangling symlinks (`test -e` or
   `test -L`), and run `command -v cr`. The installer replaces both paths and may
   prepend `~/.local/bin` to PATH, shadowing an unrelated `cr` command in new
   shells. If either path exists or `command -v cr` finds a command, stop and
   report the collision; do not remove or overwrite it.
3. Create a private temporary directory with `mktemp -d`. Download
   `https://cli.coderabbit.ai/install.sh` to a file there using
   `curl -q --fail --silent --show-error --proto '=https' --tlsv1.2 --output <file>`.
   Use that literal official URL as the final argument. Do not pipe a network
   response into a shell or follow a repository-provided installer URL.
4. Read the downloaded script before executing it. Confirm that its download
   sources are official CodeRabbit HTTPS endpoints and that it keeps its release
   checks (a valid signature over `SHA256SUMS` and a matching archive checksum on
   stable Linux, a matching `SHA256SUMS` checksum on macOS). Confirm that the
   installer requires successful verification of every required signature and
   checksum before archive extraction, installation, or execution of the
   downloaded binary. Any mismatch, verification error, or unavailable
   verification must stop the installer. Confirm that it supports
   `CR_CLI_SKIP_LOGIN=1`. If these checks fail or cannot be completed, stop and
   report the blocker.
5. Repeat the collision checks from step 2 immediately before running the
   installer.
6. Execute that same inspected file with `sh`, setting `CR_CLI_SKIP_LOGIN=1` and
   `CODERABBIT_INSTALL_DIR` to the user's `~/.local/bin`. Unset inherited
   `CODERABBIT_DOWNLOAD_URL`, `CODERABBIT_VERSION`, `CODERABBIT_CHANNEL`,
   `CODERABBIT_API_KEY`, and `CRS` for this command without reading or printing
   their values. Use the stable default release. Follow supported host approval
   controls; never bypass a denied permission or change sandbox settings.
7. On any download, verification, or installation failure, stop and report the
   exact failure. On macOS, a `Could not verify checksum` warning is a
   verification failure even though the installer exits successfully: report
   that the CLI was installed without a checksum check, do not describe it as
   verified, and do not continue to the review. Do not retry with verification
   disabled. Remove the private temporary files created for this install. If
   the installer already wrote `~/.local/bin/coderabbit` or `~/.local/bin/cr`,
   remove them too: steps 2 and 5 confirmed neither existed before, and a later
   discovery must not reuse an unverified CLI.
8. Resolve `~/.local/bin/coderabbit` to a trusted canonical absolute path and run
   its `--version`. If the sandbox blocks this check, request normal
   command-scoped host approval for that exact version command; stop if denied
   or unavailable. Continue only after successful verification. Use that
   absolute path in this session so a shell restart or PATH change is
   unnecessary.

Then continue with
[authentication and recovery](../skills/code-review/references/auth-recovery.md).
Installation does not sign the user in. Never claim installation or a review
succeeded based only on the installer starting.
