# CodeRabbit local review pilot

Review local changes from Claude Code or Codex using your CodeRabbit connection.
This pilot includes a native collector and a post-hook that automatically uploads
the selected changes after you approve `start_code_review`. The assistant then
uses `get_code_review` for progress and findings. You do not need a global CLI or
a second CodeRabbit login.

The connection requests account, usage, pull-request read access, and review
permission together. Browser consent shows these permissions for the selected
organization so the seven MCP tools can use the same connection.

Install this assembled package, trust its hook using your app's controls, and
run the setup skill to connect CodeRabbit. Then ask “Review my changes.” Git is
required. Codex currently requires manual desktop installation for this package;
the hosted connector alone cannot collect files from your laptop. This pilot
also requires a compatible CodeRabbit review service.

[Privacy policy](https://www.coderabbit.ai/privacy-policy)
