#!/bin/bash
# Install into the selected client's user profile; native OAuth/trust stays native.
set -euo pipefail
pilot_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
fail() { printf 'CodeRabbit pilot: %s\n' "$*" >&2; exit 1; }
[ "$#" -eq 1 ] || fail 'Usage: pilot/install.sh claude|codex'
case "$1" in
  claude)
    pilot_client="$(command -v claude || true)"
    if [ -z "$pilot_client" ] && [ -x "$HOME/.local/bin/claude" ]; then
      pilot_client="$HOME/.local/bin/claude"
    fi
    [ -n "$pilot_client" ] || fail 'Install Claude Code first.'
    ;;
  codex)
    pilot_client="$(command -v codex || true)"
    if [ -z "$pilot_client" ] && [ -x /Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex ]; then
      pilot_client=/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex
    fi
    [ -n "$pilot_client" ] || fail 'Install Codex CLI first.'
    ;;
  *) fail 'Usage: pilot/install.sh claude|codex' ;;
esac
"$pilot_client" plugin --help >/dev/null
"$pilot_root/prepare.sh"
case "$1" in
  claude)
    "$pilot_client" plugin marketplace add --scope user "$pilot_root"
    "$pilot_client" plugin install --scope user coderabbit@coderabbit-mcp-team-pilot
    ;;
  codex)
    "$pilot_client" plugin marketplace add "$pilot_root/codex-marketplace"
    "$pilot_client" plugin add coderabbit@coderabbit-mcp-team-pilot
    ;;
esac
printf 'Installed. Start a fresh %s session in your repository and ask: Set up CodeRabbit for this repository.\n' "$1"
printf 'Complete browser consent and native hook trust yourself. No review has been requested by this installer.\n'
