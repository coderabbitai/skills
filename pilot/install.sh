#!/bin/bash
# Register only the hosted MCP connector in the selected client's user profile.
set -euo pipefail
fail() { printf 'CodeRabbit connector: %s\n' "$*" >&2; exit 1; }
[ "$#" -eq 1 ] || fail 'Usage: pilot/install.sh claude|codex'
case "$1" in
  claude|codex) pilot_client="$(command -v "$1" || true)" ;;
  *) fail 'Usage: pilot/install.sh claude|codex' ;;
esac
if [ -z "$pilot_client" ]; then
  case "$1" in
    claude) pilot_client="$HOME/.local/bin/claude" ;;
    codex) pilot_client=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex ;;
  esac
fi
[ -x "$pilot_client" ] || fail "Install $1 first."
"$pilot_client" mcp add --help >/dev/null
if "$pilot_client" mcp get coderabbit >/dev/null 2>&1; then
  fail 'A coderabbit MCP entry already exists. Inspect it with the native client; this installer will not replace it.'
fi
case "$1" in
  claude)
    "$pilot_client" mcp add --transport http --scope user coderabbit https://mcp.coderabbit.ai/
    ;;
  codex)
    "$pilot_client" mcp add coderabbit --url https://mcp.coderabbit.ai/
    ;;
esac
printf 'Registered the standalone CodeRabbit MCP connector. Start a fresh client session and complete native browser authentication.\n'
printf 'Claude desktop Code sessions use this configuration. Claude Chat/Cowork account connectors require the separate UI setup in pilot/README.md.\n'
