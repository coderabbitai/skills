#!/usr/bin/env python3
"""Assemble a local plugin package from explicitly pinned native CLI artifacts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import tempfile
from urllib.parse import urlparse

PLATFORMS = {"darwin-arm64", "darwin-x64", "linux-arm64", "linux-x64"}
SCOPES = ["connection", "account:read", "usage:read", "pull_requests:read", "review"]


def digest(path):
    checksum = hashlib.sha256()
    with path.open("rb") as artifact:
        for chunk in iter(lambda: artifact.read(1024 * 1024), b""):
            checksum.update(chunk)
    return checksum.hexdigest()


def copy_tree(source, destination):
    for entry in source.rglob("*"):
        if entry.is_symlink():
            raise ValueError(f"Package source contains a symlink: {entry}")
    shutil.copytree(source, destination)


def assemble(source, client, artifact_manifest, endpoint, output):
    url = urlparse(endpoint)
    if (url.scheme != "https" or not url.hostname or url.username or url.password
            or url.query or url.fragment
            or any(character.isspace() for character in endpoint)):
        raise ValueError("Use the verified HTTPS MCP URL without credentials, query, or fragment")
    if output.exists():
        raise ValueError("Output already exists; choose a new directory")
    manifest = json.loads(artifact_manifest.read_text())
    version = manifest.get("version", "")
    artifacts = manifest.get("artifacts", [])
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version):
        raise ValueError("Artifact manifest must pin a CLI version")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("Artifact manifest must contain at least one native CLI artifact")
    checked = []
    seen = set()
    for artifact in artifacts:
        platform = artifact.get("platform")
        checksum = artifact.get("sha256", "")
        if platform not in PLATFORMS or platform in seen:
            raise ValueError("Artifact platform is unsupported or duplicated")
        if not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum):
            raise ValueError("Every artifact needs an exact lowercase SHA-256")
        path = Path(artifact["path"]).expanduser()
        if not path.is_absolute():
            path = artifact_manifest.parent / path
        if not path.is_file() or path.is_symlink() or digest(path) != checksum:
            raise ValueError(f"Native CLI artifact missing or checksum mismatch: {platform}")
        with path.open("rb") as handle:
            header = handle.read(20)
        # Reject scripts and JS bundles: the installed package must not need a runtime.
        if platform.startswith("darwin-"):
            cpu = 0x0100000C if platform.endswith("arm64") else 0x01000007
            native = header[:4] == b"\xcf\xfa\xed\xfe" and int.from_bytes(header[4:8], "little") == cpu
        else:
            machine = 183 if platform.endswith("arm64") else 62
            native = (header[:6] == b"\x7fELF\x02\x01" and len(header) >= 20
                      and int.from_bytes(header[18:20], "little") == machine)
        if not native:
            raise ValueError(f"Artifact must be a native {platform} executable")
        checked.append((platform, path, checksum))
        seen.add(platform)
    manifest_directory = ".claude-plugin" if client == "claude" else ".codex-plugin"
    plugin_manifest = json.loads((source / manifest_directory / "plugin.json").read_text())
    review_skill = "code-review" if (source / "skills/code-review").is_dir() else "coderabbit-review"
    for skill in ("setup", review_skill):
        if not (source / "skills" / skill / "SKILL.md").is_file():
            raise ValueError(f"Required plugin skill is missing: {skill}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".coderabbit-package-", dir=output.parent) as staging:
        package = Path(staging) / "coderabbit"
        package.mkdir()
        for name in ("skills", "assets") + (("agents",) if client == "claude" else ()):
            if (source / name).is_dir():
                copy_tree(source / name, package / name)
        if client == "codex" and review_skill == "code-review":
            skill = package / "skills/code-review"
            entry = skill / "SKILL.md"
            entry.write_text(entry.read_text().replace("name: code-review\n", "name: coderabbit-review\n", 1))
            skill.rename(package / "skills/coderabbit-review")
        (package / manifest_directory).mkdir()
        if client == "codex":
            plugin_manifest.setdefault("extensions", {}).setdefault("com.openai", {})["onboardingSkill"] = "./skills/setup/SKILL.md"
            plugin_manifest["mcpServers"] = "./mcp.json"
            plugin_manifest["hooks"] = "./hooks/hooks.json"
        (package / manifest_directory / "plugin.json").write_text(json.dumps(plugin_manifest, indent=2) + "\n")
        if client == "claude":
            mcp = {"mcpServers": {"coderabbit": {"type": "http", "url": endpoint, "oauth": {"scopes": " ".join(SCOPES)}}}}
            mcp_file = ".mcp.json"
        else:
            mcp = {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "mcpServers": {"coderabbit": {
                "type": "streamable-http", "url": endpoint,
                "extensions": {"com.openai": {"auth": {"type": "oauth", "client": {"mode": "dcr"}, "baseScopes": SCOPES}}},
            }}}
            mcp_file = "mcp.json"
        (package / mcp_file).write_text(json.dumps(mcp, indent=2) + "\n")
        (package / "hooks").mkdir()
        (package / "hooks/hooks.json").write_text(json.dumps({"hooks": {"PostToolUse": [{
            "matcher": "^mcp__(?:coderabbit|plugin_coderabbit_coderabbit)__start_code_review$",
            "hooks": [{"type": "command", "command": '"${CLAUDE_PLUGIN_ROOT}/bin/coderabbit" mcp-hook', "timeout": 300}],
        }]}}, indent=2) + "\n")
        (package / "bin").mkdir()
        (package / "bin/mcp-url").write_text(endpoint + "\n")
        shutil.copyfile(source / "scripts" / "coderabbit", package / "bin" / "coderabbit")
        (package / "bin" / "coderabbit").chmod(0o755)
        inventory = []
        for platform, path, checksum in checked:
            directory = package / "bin" / platform
            directory.mkdir()
            shutil.copyfile(path, directory / "coderabbit")
            (directory / "coderabbit").chmod(0o755)
            if digest(directory / "coderabbit") != checksum:
                raise ValueError("CLI changed during package assembly")
            (directory / "coderabbit.sha256").write_text(checksum + "\n")
            inventory.append({"platform": platform, "sha256": checksum})
        (package / "bin" / "manifest.json").write_text(json.dumps({"version": version, "artifacts": inventory}, indent=2) + "\n")
        for name in ("LICENSE",):
            if (source / name).is_file():
                shutil.copyfile(source / name, package / name)
        shutil.copyfile(source / "packaging/plugin-README.md", package / "README.md")
        package.rename(output)
    return {"package": str(output), "client": client, "cliVersion": version, "platforms": sorted(seen)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=["claude", "codex"], required=True)
    parser.add_argument("--artifacts", type=Path, required=True, help="Local artifact manifest with version, platform, path, sha256")
    parser.add_argument("--mcp-url", required=True, help="Verified HTTPS endpoint for this package")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent
    try:
        print(json.dumps(assemble(source, args.client, args.artifacts.resolve(), args.mcp_url, args.output.resolve())))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"Cannot assemble CodeRabbit plugin: {error}\n")


if __name__ == "__main__":
    main()
