# Automatic collection and recovery

This integration requires both the hosted review tools and a complete local
plugin with its trusted `PostToolUse` hook. The flow is:

1. `start_code_review` authenticates the connection and returns a server-generated
   `review_id` in `awaiting_upload`, with a short-lived upload-only ticket.
2. After the host permits that call, the hook runs the bundled native collector.
   It verifies that the returned selection matches the original request, collects
   local source, and uploads directly to the packaged CodeRabbit endpoint.
3. `get_code_review` reads the same review's progress and findings.

The agent does not invoke shell commands or pass upload tickets to the CLI. A
denied start call must not cause an upload. Hook trust is a separate local setup
step; installation does not automatically grant it. CodeRabbit receives the
selected source when the review runs.

The ticket can appear in host tool context or transcripts. It is not the
connector's OAuth token. Do not echo or persist it, inspect credential stores,
or substitute a destination. The collector may retry the same captured bytes;
the agent must not recollect changed files under an uncertain existing review.

## Recovery

- Missing review tools: the connected server is not compatible with this package.
- `awaiting_upload` after a hook failure: report the collector or hook failure.
  Do not claim a review started executing or create another review automatically.
- Uncertain upload: fetch the existing review by its ID. Preserve uncertainty if
  the server cannot establish whether the upload was accepted.
- Expired authorization: use the host's Connect or Reconnect browser flow.
- Missing or corrupt bundled executable: reinstall the complete package. Do not
  use a global CLI, download a runtime, or run CLI authentication as a fallback.

This hook integration is for Claude Code and manually installed Codex desktop
plugins. Hook-containing packages are not currently eligible for the Codex public
plugin directory. Other connector surfaces do not gain local filesystem access
from OAuth alone.

References: [Claude hooks](https://code.claude.com/docs/en/hooks),
[Codex hooks](https://learn.chatgpt.com/docs/hooks),
[Codex plugin packaging](https://developers.openai.com/plugins/build/plugins).
