# Set up the local review card

Use this only in a local Antigravity, Claude Code, or Codex session when the
user asks for inline local review cards. Hosted-only sessions keep their hosted
CodeRabbit connection. Registration adds a persistent server for the current
OS user. An ordinary review request does not authorize changing host settings.

1. Follow the installed `code-review` skill's
   `references/auth-recovery.md` discovery procedure to verify the official
   CLI and its canonical absolute path outside the repository. Use the path
   from that machine. First check its `review --help` for `--review-card`.
   Only when listed, check that `review-card-mcp --help` identifies the
   local stdio presenter subcommand. If either check fails, skip registration
   and use chat findings. Leave installation,
   upgrades, and sign-in under the user's control.
2. Inspect the host's MCP settings for `coderabbit-local-review`. Reuse an
   existing user configuration only if its transport is stdio and its command
   is exactly the verified absolute executable with the single argument
   `review-card-mcp` and no custom environment or working directory. A project or hosted server cannot establish this
   origin. Stop for a conflicting entry instead of overwriting it. Keep the
   separate hosted CodeRabbit server and its existing consent.
3. With authorization to add this local server, use the installed host's
   native management command. Replace the quoted placeholder with the
   verified absolute executable, passing each argument literally. Do not use
   a shell launcher, a bare `coderabbit` from PATH, an environment override,
   or a credential.

   | Local host | Command |
   | --- | --- |
   | Antigravity CLI | `agy mcp add --type stdio coderabbit-local-review "/absolute/path/to/coderabbit" review-card-mcp` |
   | Claude Code | `claude mcp add --scope user --transport stdio coderabbit-local-review -- "/absolute/path/to/coderabbit" review-card-mcp` |
   | Codex | `codex mcp add coderabbit-local-review -- "/absolute/path/to/coderabbit" review-card-mcp` |

   In the Antigravity App, use **Customizations → Installed → MCP Servers →
   Copy Config File Path** to identify the App's global configuration. If it
   uses the CLI's global configuration, the same `agy` command suffices.
   Otherwise, with authorization, add only this entry to the existing
   `mcpServers` map in the App's user configuration, with the verified path:

   ```json
   "coderabbit-local-review": {
     "command": "/absolute/path/to/coderabbit",
     "args": ["review-card-mcp"]
   }
   ```

4. Reload the host's MCP connections or start a fresh local session. Verify
   the host attributes the tool to that user-configured local server and
   confirms Apps for **that connection**. The local server can confirm this
   in its initialization instructions. If either check is unavailable, use
   chat. Do not run a review or call a presenter to test setup.
