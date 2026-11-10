# Prepare the pinned plugin CLI

Use this only when the installed `cli.json` says `delivery: download`.
The submitted plugin contains a readable launcher and checksums, not a compiled
executable. Setup downloads one pinned native CLI from `https://cli.coderabbit.ai`
and checks both the archive and executable hashes before running it. It also
checks local MCP-command support before installing the candidate. This is a
plugin dependency; it does not update or replace the user's standalone CLI.

Run the absolute launcher resolved by setup with `--prepare`, using the host's
normal download and execution permissions. Preparation requires curl, unzip and
a SHA-256 utility. It does not sign in, collect source, reserve a review or upload
code. If permission is denied, stop before reserving a review.

The default runtime location is
`${XDG_CACHE_HOME:-$HOME/.cache}/coderabbit/plugin-runtime/<version>/<platform>/`.
The launcher uses the same versioned cache in setup and hooks. No credentials or
repository files are stored there. Plugin updates with a new CLI pin get a new
runtime directory, and every execution rechecks its pinned executable digest.
The launcher marks only its child process as a managed installation using the
CLI's existing update settings, so a stable runtime cannot self-update away from
its reviewed hash. Standalone CLI update behavior and configuration are unchanged.
Uninstalling the plugin does not delete this shared runtime cache; the user can
remove it separately when no installed CodeRabbit plugin needs it.

On success, require the reported CLI version to match `cli.json`, then verify
`--version` through the same launcher. With a valid cached runtime, preparation
performs no download. A failed transfer, invalid archive or checksum mismatch
does not install or execute the downloaded candidate. Report the concrete error.
Re-running preparation after the user fixes that setup problem is safe; it is
not a retry of a review. Do not use a global CLI or a mutable `latest` download.

Only explicit preparation can download. A missing/corrupt runtime during a hook
fails without downloading or starting a fallback review; recover any existing
review ID through MCP. Prepare again before a newly authorized review.
