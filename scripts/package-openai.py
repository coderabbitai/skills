#!/usr/bin/env python3
"""Build the OpenAI MCP package from explicit manifests and shared skills."""

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def codex_manifests(manifest, connection):
    fields = ("name", "version", "description", "author", "homepage", "repository", "license", "keywords")
    native = {key: manifest[key] for key in fields}
    native["skills"] = "./skills/"
    native["mcpServers"] = "./.mcp.json"
    native["interface"] = manifest["extensions"]["com.openai"]["interface"]
    server = connection["mcpServers"]["coderabbit"]
    auth = server["extensions"]["com.openai"]["auth"]
    if (
        server["type"] != "streamable-http"
        or auth["type"] != "oauth"
        or auth["client"] != {"mode": "dcr"}
        or auth["defaultScopes"]
        or not auth["baseScopes"]
    ):
        raise ValueError("Review native Codex OAuth mapping for this connection")
    mcp = {"mcpServers": {"coderabbit": {"url": server["url"], "scopes": auth["baseScopes"]}}}
    return {".codex-plugin/plugin.json": native, ".mcp.json": mcp}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--codex-native", action="store_true",
        help="Build the local Codex compatibility package instead of the portable directory ZIP",
    )
    args = parser.parse_args()
    source = ROOT / "packaging/openai"
    manifest = json.loads((source / "plugin.json").read_text())
    connection = json.loads((source / "mcp.json").read_text())
    generated = {}
    files = {"LICENSE": ROOT / "LICENSE"}
    if args.codex_native:
        generated = codex_manifests(manifest, connection)
    else:
        files.update({"plugin.json": source / "plugin.json", "mcp.json": source / "mcp.json"})
    for name in ("code-review", "autofix", "coderabbit-config", "coderabbit-setup"):
        for path in sorted((ROOT / "skills" / name).rglob("*.md")):
            files[path.relative_to(ROOT).as_posix()] = path
    interface = manifest["extensions"]["com.openai"]["interface"]
    for field in ("composerIcon", "composerIconDark", "logo", "logoDark"):
        if asset := interface.get(field):
            relative = Path(asset)
            if relative.is_absolute() or ".." in relative.parts:
                raise ValueError(f"{field} must use a path inside the plugin")
            files[relative.as_posix()] = ROOT / relative
    # Exclusive creation avoids accidentally replacing a previously reviewed ZIP.
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(args.output, "x", ZIP_DEFLATED) as archive:
        for destination, data in generated.items():
            archive.writestr(destination, json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        for destination, path in sorted(files.items()):
            archive.write(path, destination)
    print(f"Built {manifest['name']} {manifest['version']}: {args.output}")
    print(f"{len(files) + len(generated)} files; no hooks, runtime binaries, or credential files")


if __name__ == "__main__":
    main()
