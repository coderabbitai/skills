#!/bin/bash
set -euo pipefail
pilot_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
[ -x "$pilot_root/claude-plugin/bin/darwin-arm64/coderabbit" ] || {
  echo 'Run pilot/prepare.sh before starting Claude.' >&2
  exit 1
}
pilot_claude="$(command -v claude || true)"
if [ -z "$pilot_claude" ] && [ -x "$HOME/.local/bin/claude" ]; then
  pilot_claude="$HOME/.local/bin/claude"
fi
[ -n "$pilot_claude" ] || { echo 'Install Claude Code first.' >&2; exit 127; }
exec "$pilot_claude" --plugin-dir "$pilot_root/claude-plugin" "$@"
