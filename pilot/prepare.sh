#!/bin/bash
# Prepare the pinned Apple Silicon pilot locally; no login or review is started.
set -euo pipefail
PATH=/usr/bin:/bin:/usr/sbin:/sbin
export PATH
umask 077
pilot_root="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
fail() { printf 'CodeRabbit pilot: %s\n' "$*" >&2; exit 1; }
[ "$#" -eq 0 ] || fail 'Usage: ./pilot/prepare.sh'
[ "$(uname -s):$(uname -m)" = Darwin:arm64 ] || fail 'This pilot supports macOS Apple Silicon only.'
cli_version=0.9.2-nightly.main.20261102.268.1
archive_sha=e0d53455c1a96095272eba001c81f9c826111bc412dec3b5d5e697ce1c80d58c
native_sha=2f9663d6cf3ebef80da0a0c36a26d0010dba02ae87e19b8162446966a01c2470
digest() { shasum -a 256 "$1" | cut -d ' ' -f 1; }
packages=("$pilot_root/claude-plugin" "$pilot_root/codex-marketplace/plugins/coderabbit")
missing=0
for package in "${packages[@]}"; do
  binary="$package/bin/darwin-arm64/coderabbit"
  [ -d "$package/bin/darwin-arm64" ] || fail 'Incomplete kit; clone the pilot branch again.'
  [ ! -L "$binary" ] || fail "Refusing a symbolic link: $binary"
  if [ -e "$binary" ]; then
    [ -f "$binary" ] && [ "$(digest "$binary")" = "$native_sha" ] || fail "Existing binary is invalid. Remove $binary and rerun preparation."
  else
    missing=1
  fi
done
if [ "$missing" -eq 1 ]; then
  pilot_tmp="$(mktemp -d "${TMPDIR:-/tmp}/coderabbit-pilot.XXXXXX")"
  trap 'rm -rf -- "$pilot_tmp"' EXIT
  printf 'Downloading CodeRabbit %s (about 42 MB)…\n' "$cli_version"
  curl --fail --silent --show-error --location --proto '=https' --proto-redir '=https' \
    --connect-timeout 30 --max-time 300 --max-filesize 104857600 \
    --output "$pilot_tmp/native.zip" \
    "https://cli.coderabbit.ai/releases/nightly/$cli_version/coderabbit-darwin-arm64.zip"
  [ "$(digest "$pilot_tmp/native.zip")" = "$archive_sha" ] || fail 'Download checksum mismatch; nothing was installed.'
  # Extract only the named executable from the exact verified archive.
  unzip -p "$pilot_tmp/native.zip" coderabbit > "$pilot_tmp/coderabbit"
  [ "$(digest "$pilot_tmp/coderabbit")" = "$native_sha" ] || fail 'Native checksum mismatch; nothing was installed.'
  for package in "${packages[@]}"; do
    binary="$package/bin/darwin-arm64/coderabbit"
    if [ ! -e "$binary" ]; then
      install -m 755 "$pilot_tmp/coderabbit" "$binary"
    fi
  done
fi
for package in "${packages[@]}"; do
  chmod 755 "$package/bin/darwin-arm64/coderabbit"
done
printf 'Prepared both plugins. Follow pilot/README.md to connect your client.\n'
