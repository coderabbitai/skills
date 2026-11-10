# CodeRabbit MCP plugin changelog

## 1.3.0

### Added

- Connect CodeRabbit once through the host's browser sign-in. Review local
  changes without installing a global CLI or signing in to the CLI separately.
- Set up a verified, version-pinned CLI dependency on macOS or Linux. This
  release uses CodeRabbit CLI 0.9.3 on ARM64 and x64.
- Start an approved local review through the Claude plugin's post-tool hook,
  receive findings in the conversation, and recover the same saved review in a
  later session without another upload or review.
- Inspect and preview repository review configuration before approving a save.

### Changed

- Ordinary review requests use the connected MCP workflow. Explicit CLI-only
  requests can still use the existing standalone workflow before any MCP review
  starts; failed or uncertain MCP reviews never switch routes automatically.
- The launcher preserves the caller's Git and SSH tool paths while using system
  helpers to verify the pinned executable.
- Automatic hooks accept only the Claude plugin-owned review tool. A manually
  configured connection that shadows it must be resolved through native setup.

### Requirements

- Local review requires Claude Code with permitted local execution, Git, network
  access and native hook approval. Initial runtime preparation also uses curl,
  unzip and a SHA-256 utility. Hooks never download software.
- Authorized local reviews send selected source and repository context to
  CodeRabbit. See the [privacy policy](https://www.coderabbit.ai/privacy-policy).
- Claude Chat and hosts without local execution can use available remote tools;
  the hosted connector alone cannot review files on a laptop.
- Codex hook packages are unavailable pending verified plugin server identity.
  The standalone Codex plugin and the separate Review Mod retain their existing
  versions and distribution channels.
