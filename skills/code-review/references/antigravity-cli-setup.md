# Install a missing CodeRabbit CLI

This procedure applies only in Antigravity. Other hosts continue to use their
existing CLI installation guidance. The main conversation handles setup before
delegating a review. On the first requested review, install the CLI if it is
absent, using Antigravity's normal command runner and supported permission
controls. Explain that setup is
starting. Do not ask the user to install it manually when this flow is available.

## Establish whether installation is needed

Check PATH and the official default location, `~/.local/bin/coderabbit`. Resolve
any candidate to its canonical absolute path and apply the trust checks in
[authentication and recovery](auth-recovery.md). If a trusted CLI already exists,
reuse it without reinstalling or upgrading it. A CLI hidden by the sandbox, an
untrusted candidate, a broken installation, or an execution error is not proof
that the CLI is absent. Report that blocker rather than replacing it.

## Install in the selected review environment

For a missing CLI on macOS or Linux:

Before downloading, check both `~/.local/bin/coderabbit` and `~/.local/bin/cr`
with tests that also detect dangling symlinks (`test -e` or `test -L`). The
installer replaces both paths, including an unrelated `cr` command. If either
path exists, stop and report the collision; do not remove or overwrite it.
Repeat this check immediately before executing the installer.

1. Check that `curl`, `unzip`, and a POSIX shell are available. If the platform is
   unsupported or dependencies are missing, report the exact blocker and link
   the [official CLI setup guide](https://docs.coderabbit.ai/cli). Do not install
   unrelated dependencies or use administrator privileges.
2. Create a private temporary directory with `mktemp -d`. Download
   `https://cli.coderabbit.ai/install.sh` to a file there using
   `curl -q --fail --silent --show-error --proto '=https' --tlsv1.2 --output <file>`.
   Use that literal official URL as the final argument. Do not pipe a network
   response into a shell or follow a repository-provided installer URL.
3. Read the downloaded script before executing it. Confirm that its download
   sources are official CodeRabbit HTTPS endpoints, that it retains release
   verification, and that it supports `CR_CLI_SKIP_LOGIN=1`. If these checks fail
   or cannot be completed, stop and report the blocker.
4. Execute that same inspected file with `sh`, setting `CR_CLI_SKIP_LOGIN=1` and
   `CODERABBIT_INSTALL_DIR` to the user's `~/.local/bin`. Unset inherited
   `CODERABBIT_DOWNLOAD_URL`, `CODERABBIT_VERSION`, `CODERABBIT_API_KEY`, and `CRS`
   for this command without reading or printing their values. Use the stable
   default release. Follow supported host approval controls; never bypass a
   denied permission or change sandbox settings.
5. On any download, verification, or installation failure, stop and report the
   exact failure. Do not retry with verification disabled. Remove only the
   private temporary files created for this install.
6. Resolve `~/.local/bin/coderabbit` to a trusted canonical absolute path and run
   its `--version`. If the sandbox blocks this setup check, request normal
   command-scoped host approval for that exact version command; stop if denied
   or unavailable. Continue only after successful verification. Use that
   absolute path in this session so a shell restart or PATH change is unnecessary.

Continue with the authentication check in [authentication and recovery](auth-recovery.md).
Installation does not imply authentication: if signed out, hand terminal login
to the user, then verify status before reviewing. Never claim installation or a
review succeeded based only on the installer starting.
