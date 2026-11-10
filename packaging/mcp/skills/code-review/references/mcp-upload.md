# Launch and recovery

The host keeps connector OAuth. `start_code_review` returns a server-generated
review ID and a short-lived, provider-free handoff. The pinned CLI uses that
authority for its existing collection, submission and review stream. It never
reads the host's OAuth store or needs a second login. Source goes to Reviewer;
MCP retrieves the same saved findings when local delivery is unavailable.

## Use the installed launcher

For `launchMode: hook`, use the installed and trusted post-tool hook.
The hook consumes the approved start result automatically. A pre-hook must not
upload ahead of approval. Installation alone does not grant hook trust.

Use permitted direct CLI execution only in a `launchMode: direct` package.
An unavailable hook requires setup, not a change of execution path.
The package's `cli.json` identifies its launcher and configured adapter. Do not run a
direct command while an enabled hook may also launch. Do not switch adapters to
circumvent a denied execution or source-upload decision.

For direct execution, resolve the `launcher` in `cli.json` under the installed plugin root as an absolute path.
Run `review --agent --mcp-stdin --dir <absolute workspace root>`. Send only the
returned `handoff` object as JSON on stdin, unchanged. Use a process tool that
accepts stdin separately from its command arguments. Quote executable/workspace
paths. Never interpolate instructions or the
credential into executable shell text, command-line flags, environment variables
or persistent files, including a shell heredoc. If safe stdin delivery is
unavailable, report the limit.

The handoff is a bearer capability and may be visible in the host transcript;
stdin is not a secret vault. Do not echo it, include it in the user-facing result,
persist it, or substitute a destination. The native candidate pins its allowed
Reviewer endpoint. Do not use `--host-url` or a global CLI to bypass that check.

## Read and recover

Retain the review ID and the host process handle, if available. Never infer
failure to launch from missing hook stdout. Read the original review with
`get_code_review` after uncertain launch, lost output, timeout or disconnection.
Do not recollect changed files or submit a new review to repair result delivery.

The CLI's terminal envelope includes `review_id`, `status`, `complete`,
`finding_count` and canonical findings. Validate the ID, terminal status, complete
flag and distinct finding count. A host truncation marker or malformed output
also requires MCP retrieval. Follow returned pagination, keeping finding IDs
stable across both paths. `complete` describes delivery, not analysis coverage;
partial, skipped, failed and expired reviews never establish clean code.

- Missing review tools: use a compatible connection and packaged candidate.
- Hook does not match the active Claude connection: check setup for a shadowing
  manual connection. Require the plugin-qualified connection; let the user
  disable a shadowing duplicate through native controls, even at the same endpoint.
  Preserve entries and unrelated integrations; do not widen matchers.
- Endpoint mismatch: use the matching pinned package and server. Do not
  rewrite the handoff or disable validation.
- Awaiting launch after a hook failure: report the failure and existing review
  state. Do not claim the engine ran or automatically start again.
- Expired/revoked authorization: use the host's Connect or Reconnect browser flow.
- Lost start response: recover its ID from the host tool record if available;
  otherwise report the uncertain start without inventing an ID or resubmitting.
- Missing/corrupt executable: follow setup for the installed delivery mode.
  No global CLI or CLI login fallback; never prepare or relaunch to recover an
  uncertain review.

A remote session reviews its own checkout. Connector authorization does not grant
access to a laptop or override the host's execution and network permissions.
