# Claude MCP plugin 1.3.1

- Install the complete Claude MCP plugin directly from the repository root on
  `main`; no assembled distribution branch is required.
- Use the existing plugin-qualified review hook and pinned CLI 0.9.3. Setup
  verifies the CLI before review; browser sign-in remains owned by Claude.
- Keep standalone skills, other host plugins, explicit CLI-only review and the
  separate review Mod available. Their release versions remain independent.
- Directory review and publication remain separate from source availability.
