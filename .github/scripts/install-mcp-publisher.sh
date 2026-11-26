#!/usr/bin/env bash
set -euo pipefail

# Fixed Linux runner asset, independent of user-supplied workflow inputs.
readonly publisher_version=v1.8.16
readonly publisher_archive=mcp-publisher_linux_amd64.tar.gz
readonly publisher_sha256=6e2f799550cf843c6fd3350498d56cc49be3dc0af1e6237eb0e6435c7a9d5c05
readonly publisher_base="https://github.com/modelcontextprotocol/registry/releases/download/${publisher_version}"
readonly publisher_dir="${RUNNER_TEMP:?}/coderabbit-mcp-publisher"

mkdir -p "$publisher_dir"
cd "$publisher_dir"
curl --fail --location --silent --show-error --output "$publisher_archive" "$publisher_base/$publisher_archive"
curl --fail --location --silent --show-error --output "$publisher_archive.sigstore.json" "$publisher_base/$publisher_archive.sigstore.json"
printf '%s  %s\n' "$publisher_sha256" "$publisher_archive" | sha256sum --check --strict
cosign verify-blob \
  --bundle "$publisher_archive.sigstore.json" \
  --certificate-identity "https://github.com/modelcontextprotocol/registry/.github/workflows/release.yml@refs/tags/${publisher_version}" \
  --certificate-oidc-issuer https://token.actions.githubusercontent.com \
  "$publisher_archive"
tar xzf "$publisher_archive" mcp-publisher
printf '%s\n' "$publisher_dir" >> "${GITHUB_PATH:?}"
