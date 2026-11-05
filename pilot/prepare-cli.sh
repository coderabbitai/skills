#!/bin/bash
# Prepare only the standalone, pinned review CLI. No login or review is started.
set -euo pipefail
PATH=/usr/bin:/bin:/usr/sbin:/sbin
export PATH
umask 077
pilot_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
fail() { printf 'CodeRabbit pilot: %s\n' "$*" >&2; exit 1; }
[ "$#" -eq 0 ] || fail 'Usage: bash pilot/prepare-cli.sh'
[ "$(uname -s):$(uname -m)" = Darwin:arm64 ] || fail 'This pinned review candidate supports macOS Apple Silicon only.'
cli_version=0.9.2-nightly.main.20261102.268.1
archive_sha=e0d53455c1a96095272eba001c81f9c826111bc412dec3b5d5e697ce1c80d58c
native_sha=2f9663d6cf3ebef80da0a0c36a26d0010dba02ae87e19b8162446966a01c2470
digest() { shasum -a 256 "$1" | cut -d ' ' -f 1; }
binary="$pilot_root/.runtime/coderabbit"
[ ! -L "$pilot_root/.runtime" ] && [ ! -L "$binary" ] || fail 'Refusing a symbolic link in the installation target.'
if [ -e "$binary" ]; then
  [ -f "$binary" ] && [ "$(digest "$binary")" = "$native_sha" ] || fail 'Existing CLI differs from the pinned candidate; inspect it before replacing it.'
else
  pilot_tmp="$(mktemp -d "${TMPDIR:-/tmp}/coderabbit-cli-pilot.XXXXXX")"
  trap 'rm -rf -- "$pilot_tmp"' EXIT
  curl --fail --silent --show-error --location --proto '=https' --proto-redir '=https' \
    --connect-timeout 30 --max-time 300 --max-filesize 104857600 \
    --output "$pilot_tmp/native.zip" \
    "https://cli.coderabbit.ai/releases/nightly/$cli_version/coderabbit-darwin-arm64.zip"
  [ "$(digest "$pilot_tmp/native.zip")" = "$archive_sha" ] || fail 'Download checksum mismatch; nothing was installed.'
  unzip -p "$pilot_tmp/native.zip" coderabbit > "$pilot_tmp/coderabbit"
  [ "$(digest "$pilot_tmp/coderabbit")" = "$native_sha" ] || fail 'Native checksum mismatch; nothing was installed.'
  mkdir -p "$pilot_root/.runtime"
  install -m 700 "$pilot_tmp/coderabbit" "$binary"
fi
[ -x "$binary" ] || fail 'The verified CLI is not executable; inspect its permissions.'
"$binary" --version
printf 'Prepared standalone review CLI: %s\n' "$binary"
