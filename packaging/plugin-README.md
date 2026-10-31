# CodeRabbit local review pilot

Review local changes from Claude Code or Codex using your CodeRabbit connection.
This pilot includes the native CLI. MCP authorizes a review, then a trusted
post-tool hook runs the normal CLI review on supported hosts. Permitted direct
CLI execution is the hook-free fallback. The assistant uses complete CLI output
when visible and `get_code_review` to retrieve the same saved findings otherwise.
You do not need a global CLI or a second CodeRabbit login.

The connection requests account, usage, pull-request read access, and review
permission together. Browser consent shows these permissions for the selected
organization so the seven MCP tools can use the same connection.

Install this assembled package and run setup to select its supported launcher
and connect CodeRabbit. Trust the hook using your app's controls when present.
Then ask “Review my changes.” Git is required. Hook-containing Codex packages
use the supported manual installation channel;
the hosted connector alone cannot collect files from your laptop. This pilot
also requires a compatible CodeRabbit review service.

[Privacy policy](https://www.coderabbit.ai/privacy-policy)
