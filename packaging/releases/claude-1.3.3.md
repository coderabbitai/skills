# Claude MCP plugin 1.3.3 — staged hook update

Do not merge or publish this follow-up until hook-free 1.3.2 is live and the
separate Anthropic review/approval for the hook-enabled update is obtained.

- Restore MCP-authorized local review through the Claude plugin's qualified
  post-tool hook and pinned CLI 0.9.3 runtime. Setup prepares the runtime and
  uses Claude's browser connection without a separate local CLI sign-in.
- Keep review and upload permission, native hook trust, and one-review handoff
  boundaries. Missing hooks or failed MCP launches never switch automatically
  to another launcher or standalone review.
- Keep explicit CLI-only review, portable skills, other host plugins, and the
  separate Mod available. MCP and hook declarations remain Claude-only.
- Source availability, directory validation, policy approval and publication
  remain separate. This staged source does not change or publish the hook-free 1.3.2 candidate.
