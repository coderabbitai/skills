# MCP upload contract

This package requires the matching hosted upload protocol. A connected server
without these tools is not compatible; do not imitate missing tools or use the
older local-daemon protocol.

1. Call `create_upload` with `{selection: {...}}` containing the requested selection. It returns a descriptor:
   `protocolVersion: 1`, `uploadUrl`, `uploadToken`, and `selection`. The selection
   includes `scope` and any requested `directory`, `baseBranch`, `baseCommit`,
   `includeUntracked`, or `light` values. Verify the returned selection preserves
   the user's request. Do not replace a returned endpoint or add credentials.
2. Invoke the bundled executable with **only** the `mcp-upload` subcommand. Pass
   the returned descriptor as one JSON object on standard input, with EOF after
   it. The CLI collects and uploads directly. Do not read source into MCP tool
   arguments or construct an alternate archive yourself.
3. Pass the JSON through the host tool's standard-input channel where available.
   If only shell input is available, serialize valid JSON and use a **quoted
   here-document delimiter that does not occur as a line anywhere in that
   serialized JSON**. Never interpolate descriptor values into command syntax,
   expand variables in the body, use an unquoted here-document, or store the
   descriptor in a temporary file. Preserve input values exactly, including
   paths containing spaces, quotes, dollar signs, and backticks.
4. The token is a short-lived upload-only capability, not a CodeRabbit login
   credential. It necessarily passes through MCP/tool context. Do not echo it,
   include it in command arguments or user-facing output, or persist it. Never
   retrieve or relay MCP access tokens, CLI credentials, or keychain entries.
5. Read the safe collector receipt: `uploadId`, `payloadDigest`, and `files`.
   A successful upload is not a completed review. If collection/upload fails or
   its outcome is uncertain, report the failure; do not blindly collect again or
   create a second upload to infer what happened.
6. Call `preview_review` with `uploadId`. Verify the files and requested scope.
   The preview refers to uploaded bytes, not current files on disk. If it shows
   unexpected files, stop before starting a review.
7. Call `start_review` with that `uploadId` and a unique `operationKey`; preserve
   both when recovering the same start request. Follow `get_review` using its
   `reviewId` until a terminal result or actionable failure.

Do not run `auth login`, pass `--use-credits`, invoke the old `review --agent`
command, or fetch source files through MCP as a workaround.
