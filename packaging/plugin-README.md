# CodeRabbit local review pilot

Review local changes from Claude Code or Codex using your CodeRabbit connection.
This pilot includes the native CLI. MCP authorizes a review, then the package's
launcher runs the normal CLI review. The assistant uses complete CLI output
when visible and `get_code_review` to retrieve the same saved findings otherwise.
MCP reviews do not need a global CLI or a second CodeRabbit login.

Local MCP launch currently supports macOS and Linux. To keep using your existing
standalone CLI and sign-in, explicitly ask **“Review with my existing CodeRabbit
CLI only.”** The included original CLI guide handles that separate route before
any MCP reservation; it is never an automatic retry for an MCP review.

The connection requests account, usage, pull-request read access, and review
permission together so the available MCP tools can use the same connection.

For MCP reviews, install this package and ask **“Set up CodeRabbit.”**
Connect CodeRabbit through the browser when prompted.

{{REVIEW_LAUNCH}}

Setup can also help tailor review settings and path instructions to your
repository, showing the proposed configuration changes before saving them.
Then ask “Review my changes.” Git is required. Codex hook packages are unavailable
until plugin server identity can be verified;
the hosted connector alone cannot collect files from your laptop. This pilot
also requires a compatible CodeRabbit review service.

{{RELEASE_NOTES}}[Privacy policy](https://www.coderabbit.ai/privacy-policy)
