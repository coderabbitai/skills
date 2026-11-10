# CodeRabbit connected code review

Connect CodeRabbit once through your host's browser sign-in. Account, usage and
pull-request tools use that connection. MCP reviews use a pinned native CLI
prepared during setup, without another login or a global CLI installation.

Local MCP launch currently supports macOS and Linux. To keep using your existing
standalone CLI and sign-in, explicitly ask **“Review with my existing CodeRabbit
CLI only.”** The included original CLI guide handles that separate route before
any MCP reservation; it is never an automatic retry for an MCP review.

To enable MCP reviews, ask setup to prepare the CLI and verify the connected organization.
Setup downloads the exact platform archive from `https://cli.coderabbit.ai`,
verifies the archive and executable SHA-256 values shipped in this plugin, and
stores the runtime in the user's versioned CodeRabbit cache. A valid cache is
reused. The plugin rechecks the executable on every run and uses the CLI's existing
managed-install settings for this dependency; plugin releases own its updates.
It requires curl, unzip,
a SHA-256 utility and Git. Preparation alone never uploads source.

{{REVIEW_LAUNCH}}

On a host that permits local execution, ask **“Review my changes.”** After an
approved MCP review start, this package runs the prepared CLI.
Host execution, network and source-upload permissions still apply. A hook never
downloads software or switches to another launcher after a failure. Missing or
later-session output is retrieved through MCP with the same review ID.

Claude Chat and other hosts without local execution can use remote account and
PR tools, but cannot review files on your laptop. Local CLI preparation and
review require an execution-capable host. Supported native platforms are listed
in `runtime/manifest.json`; other platforms fail before review execution.

The plugin does not alter the standalone CodeRabbit CLI or its authentication.
Uninstalling the plugin leaves the shared runtime cache available to other
CodeRabbit plugin versions; it can be removed separately when no longer needed.
Downloads send a normal artifact request to CodeRabbit's CLI CDN. Authorized
reviews send the selected source to the CodeRabbit review service. The host may
retain the short-lived review handoff in its own transcript.

[Privacy policy](https://www.coderabbit.ai/privacy-policy)

[Release notes](CHANGELOG.md) · [Documentation](https://docs.coderabbit.ai/cli/claude-code-integration)
· [Support](mailto:support@coderabbit.ai)
