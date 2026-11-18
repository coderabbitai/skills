#!/usr/bin/env python3
"""Build the OpenAI MCP package from explicit manifests and shared skills."""

import argparse
import json
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = ROOT / "packaging/openai"
    manifest = json.loads((source / "plugin.json").read_text())
    json.loads((source / "mcp.json").read_text())
    files = {
        "plugin.json": source / "plugin.json",
        "mcp.json": source / "mcp.json",
        "LICENSE": ROOT / "LICENSE",
    }
    for name in ("code-review", "autofix", "coderabbit-config"):
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
        for destination, path in sorted(files.items()):
            archive.write(path, destination)
    print(f"Built {manifest['name']} {manifest['version']}: {args.output}")
    print(f"{len(files)} files; no hooks, runtime binaries, or credential files")


if __name__ == "__main__":
    main()
