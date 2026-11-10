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


def assemble(source, client, artifact_manifest, endpoint, output, launcher="hook", delivery="bundled"):
    if launcher not in {"hook", "direct"}:
        raise ValueError("Launcher must be hook or direct")
    if delivery not in {"bundled", "download"}:
        raise ValueError("CLI delivery must be bundled or download")
    url = urlparse(endpoint)
    if (url.scheme != "https" or not url.hostname or url.username or url.password
            or url.query or url.fragment
            or any(character.isspace() for character in endpoint)):
        raise ValueError("Use the verified HTTPS MCP URL without credentials, query, or fragment")
    if output.exists():
        raise ValueError("Output already exists; choose a new directory")
    manifest = json.loads(artifact_manifest.read_text())
    if not isinstance(manifest, dict):
        raise ValueError("Artifact manifest must be a JSON object")
    version = manifest.get("version", "")
    artifacts = manifest.get("artifacts", [])
    if not isinstance(version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version):
        raise ValueError("Artifact manifest must pin a CLI version")
    if not isinstance(artifacts, list) or not artifacts:
        raise ValueError("Artifact manifest must contain at least one native CLI artifact")
    checked = []
    seen = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            raise ValueError("Each artifact must be a JSON object")
        platform = artifact.get("platform")
        checksum = artifact.get("sha256", "")
        if platform not in PLATFORMS or platform in seen:
            raise ValueError("Artifact platform is unsupported or duplicated")
        if not isinstance(checksum, str) or not re.fullmatch(r"[a-f0-9]{64}", checksum):
            raise ValueError("Every artifact needs an exact lowercase SHA-256")
        try:
            path = Path(artifact["path"]).expanduser()
        except RuntimeError as error:
            raise ValueError(f"Invalid artifact path: {error}") from error
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
        archive_checksum = artifact.get("archive_sha256", "")
        if delivery == "download" and (not isinstance(archive_checksum, str) or
                not re.fullmatch(r"[a-f0-9]{64}", archive_checksum)):
            raise ValueError("Download delivery requires a pinned archive SHA-256 for every platform")
        checked.append((platform, path, checksum, archive_checksum))
        seen.add(platform)
    manifest_directory = ".claude-plugin" if client == "claude" else ".codex-plugin"
    plugin_manifest = json.loads((source / manifest_directory / "plugin.json").read_text())
    plugin_version = manifest.get("plugin_version", plugin_manifest.get("version"))
    if delivery == "download" and "plugin_version" not in manifest:
        raise ValueError("Download delivery requires an explicit plugin_version for host update caches")
    if not isinstance(plugin_version, str) or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", plugin_version):
        raise ValueError("Plugin version must be an exact semantic version")
    plugin_manifest["version"] = plugin_version
    if client == "claude" and delivery == "download":
        plugin_manifest["privacyPolicyUrl"] = "https://www.coderabbit.ai/privacy-policy"
        plugin_manifest["icon"] = "./assets/coderabbit-small.png"
    review_skill = "code-review" if (source / "skills/code-review").is_dir() else "coderabbit-review"
    pilot = source / "packaging/mcp"
    for skill in ("setup", review_skill):
        template_skill = "code-review" if skill == review_skill else skill
        if not (pilot / "skills" / template_skill / "SKILL.md").is_file():
            raise ValueError(f"Required MCP plugin skill is missing: {skill}")
    pilot_agent = pilot / "agents/code-reviewer.md"
    if client == "claude" and (not pilot_agent.is_file() or pilot_agent.is_symlink()):
        raise ValueError("Required MCP review agent is missing")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".coderabbit-package-", dir=output.parent) as staging:
        package = Path(staging) / "coderabbit"
        package.mkdir()
        for name in ("skills", "assets") + (("agents",) if client == "claude" else ()):
            if (source / name).is_dir():
                copy_tree(source / name, package / name)
        # Shared installations retain the released CLI workflow. Only a complete
        # assembled pilot receives the MCP-specific review and setup instructions.
        for skill in ("setup", review_skill):
            destination = package / "skills" / skill
            if destination.exists():
                shutil.rmtree(destination)
            template_skill = "code-review" if skill == review_skill else skill
            copy_tree(pilot / "skills" / template_skill, destination)
        if client == "claude":
            (package / "agents").mkdir(exist_ok=True)
            shutil.copyfile(pilot_agent, package / "agents/code-reviewer.md")
        if client == "codex" and review_skill == "code-review":
            skill = package / "skills/code-review"
            entry = skill / "SKILL.md"
            entry.write_text(entry.read_text().replace("name: code-review\n", "name: coderabbit-review\n", 1))
            skill.rename(package / "skills/coderabbit-review")
        installed_review_skill = "coderabbit-review" if client == "codex" else review_skill
        legacy = package / "skills" / installed_review_skill / "references/standalone-cli"
        copy_tree(source / "skills" / review_skill, legacy)
        # Keep the original workflow and relative references without registering
        # another broad review skill that competes with the route selector.
        (legacy / "SKILL.md").rename(legacy / "guide.md")
        cli_path = "bin/coderabbit" if delivery == "bundled" else "scripts/coderabbit"
        (package / "cli.json").write_text(json.dumps({
            "launcher": "./" + cli_path, "delivery": delivery,
            "version": version, "launchMode": launcher,
        }, indent=2) + "\n")
        (package / manifest_directory).mkdir()
        if client == "codex":
            plugin_manifest.setdefault("extensions", {}).setdefault("com.openai", {})["onboardingSkill"] = "./skills/setup/SKILL.md"
            plugin_manifest["mcpServers"] = "./mcp.json"
            if launcher == "hook":
                plugin_manifest["hooks"] = "./hooks/hooks.json"
            else:
                plugin_manifest.pop("hooks", None)
        (package / manifest_directory / "plugin.json").write_text(json.dumps(plugin_manifest, indent=2) + "\n")
        # A portable root manifest takes precedence over the compatibility
        # manifest, but the shipped Codex loader skips hooks for that format.
        if client == "codex" and launcher == "direct":
            portable = {key: value for key, value in plugin_manifest.items()
                        if key not in {"interface", "skills", "mcpServers", "hooks", "extensions"}}
            openai = dict(plugin_manifest["extensions"]["com.openai"])
            openai["interface"] = plugin_manifest["interface"]
            portable["$schema"] = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
            portable["extensions"] = {"com.openai": openai}
            (package / "plugin.json").write_text(json.dumps(portable, indent=2) + "\n")
        if client == "claude":
            mcp = {"mcpServers": {"coderabbit": {"type": "http", "url": endpoint, "oauth": {"scopes": " ".join(SCOPES)}}}}
            mcp_file = ".mcp.json"
        else:
            # The shipped Codex loader rejects transport-level auth extensions.
            # It discovers OAuth scopes from the verified server's metadata.
            mcp = {"$schema": "https://agent-plugins.org/schemas/1.0.0/mcp.schema.json", "mcpServers": {"coderabbit": {
                "type": "streamable-http", "url": endpoint,
            }}}
            mcp_file = "mcp.json"
        (package / mcp_file).write_text(json.dumps(mcp, indent=2) + "\n")
        if launcher == "hook":
            (package / "hooks").mkdir()
            plugin_root = "CLAUDE_PLUGIN_ROOT" if client == "claude" else "PLUGIN_ROOT"
            (package / "hooks/hooks.json").write_text(json.dumps({"hooks": {"PostToolUse": [{
                "matcher": "^mcp__(?:coderabbit|plugin_coderabbit_coderabbit)__start_code_review$",
                # Allow the 5m launch window + 30m execution + terminal persistence/cleanup.
                # This adapter now runs a whole review, not just source collection.
                "hooks": [{"type": "command", "command": '"${' + plugin_root + '}/' + cli_path + '" mcp-hook', "timeout": 2400}],
            }]}}, indent=2) + "\n")
        metadata = package / ("bin" if delivery == "bundled" else "runtime")
        metadata.mkdir()
        (metadata / "mcp-url").write_text(endpoint + "\n")
        (metadata / "launch-mode").write_text(launcher + "\n")
        (metadata / "version").write_text(version + "\n")
        adapter = package / cli_path
        adapter.parent.mkdir(exist_ok=True)
        shutil.copyfile(source / "scripts" / ("coderabbit" if delivery == "bundled" else "coderabbit-runtime"), adapter)
        adapter.chmod(0o755)
        inventory = []
        for platform, path, checksum, archive_checksum in checked:
            if delivery == "bundled":
                directory = metadata / platform
                directory.mkdir()
                shutil.copyfile(path, directory / "coderabbit")
                (directory / "coderabbit").chmod(0o755)
                if digest(directory / "coderabbit") != checksum:
                    raise ValueError("CLI changed during package assembly")
                (directory / "coderabbit.sha256").write_text(checksum + "\n")
            else:
                channel = "nightly/" if "-nightly." in version else ""
                archive_url = f"https://cli.coderabbit.ai/releases/{channel}{version}/coderabbit-{platform}.zip"
                (metadata / f"{platform}.url").write_text(archive_url + "\n")
                (metadata / f"{platform}.sha256").write_text(checksum + "\n")
                (metadata / f"{platform}.archive.sha256").write_text(archive_checksum + "\n")
            inventory.append({"platform": platform, "sha256": checksum})
        (metadata / "manifest.json").write_text(json.dumps({"version": version, "artifacts": inventory}, indent=2) + "\n")
        for name in ("LICENSE",):
            if (source / name).is_file():
                shutil.copyfile(source / name, package / name)
        readme = "plugin-README.md" if delivery == "bundled" else "runtime-README.md"
        launch_guidance = (
            "This package uses one post-tool hook. Review and trust the CodeRabbit "
            "hook through your host's native controls during setup. The hook "
            "launches only after an approved CodeRabbit review start; you do not "
            "choose or run a launcher. If hook setup fails, resolve that setup "
            "before starting a review."
            if launcher == "hook" else
            "This package contains no hooks. Setup verifies that the host can "
            "run the packaged CLI and deliver its review authorization through "
            "stdin separately from command text. If the host cannot do that, "
            "local review is unavailable; do not start a review."
        )
        readme_text = (source / "packaging" / readme).read_text(encoding="utf-8")
        (package / "README.md").write_text(
            readme_text.replace("{{REVIEW_LAUNCH}}", launch_guidance), encoding="utf-8"
        )
        package.rename(output)
    return {"package": str(output), "client": client, "launcher": launcher, "delivery": delivery, "pluginVersion": plugin_version, "cliVersion": version, "platforms": sorted(seen)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--client", choices=["claude", "codex"], required=True)
    parser.add_argument("--artifacts", type=Path, required=True, help="Local artifact manifest with version, platform, path, sha256")
    parser.add_argument("--mcp-url", required=True, help="Verified HTTPS endpoint for this package")
    parser.add_argument("--launcher", choices=["hook", "direct"], default="hook",
                        help="Prefer hook on supported trusted hosts; direct is the hook-free channel fallback")
    parser.add_argument("--delivery", choices=["bundled", "download"], default="bundled",
                        help="Bundle native files for manual pilots, or prepare the pinned dependency during setup")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parent.parent
    try:
        print(json.dumps(assemble(source, args.client, args.artifacts.resolve(), args.mcp_url, args.output.resolve(), args.launcher, args.delivery)))
    except (ValueError, OSError, KeyError, TypeError) as error:
        parser.exit(1, f"Cannot assemble CodeRabbit plugin: {error}\n")


if __name__ == "__main__":
    main()
