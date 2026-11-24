"""Check the native package and main-based Antigravity release version.

Requires the official agy validator; uses only Python's standard library.
This is maintainer CI tooling, not an installed plugin runtime.
Run on an idle checkout; concurrent editor/Git operations are unsupported.
The consistency checks detect observed changes, not transactional isolation.
"""

import argparse
import json
from pathlib import Path
import re
import subprocess


RELEASE_PATHS = (
    "plugin.json", "mcp_config.json", ".antigravity-plugin", "skills",
    "agents", "commands", "assets", "rules", "hooks.json", "README.md",
    "docs/mcp.md", "scripts",
)


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], text=True, stderr=subprocess.PIPE)


def version(value):
    if not isinstance(value, str) or not re.fullmatch(r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)", value):
        raise ValueError("Antigravity releases require a stable MAJOR.MINOR.PATCH version")
    return tuple(map(int, value.split(".")))


def check_version(root, base):
    current = json.loads((root / "plugin.json").read_text())["version"]
    version(current)
    if not base:
        return current, None, None
    # Resolve first so untrusted refs cannot become command options or pathspecs.
    base = git(root, "rev-parse", "--verify", "--end-of-options", base + "^{commit}").strip()
    head = git(root, "rev-parse", "--verify", "HEAD").strip()
    # Keep committed history separate from one combined staged/unstaged/untracked
    # observation, so staging between queries cannot hide a package addition.
    changed = git(root, "diff", "--name-only", base, head, "--", *RELEASE_PATHS)
    local = git(root, "status", "--porcelain=v1", "--untracked-files=all", "--", *RELEASE_PATHS)
    previous = json.loads(git(root, "show", base + ":plugin.json"))["version"]
    if git(root, "rev-parse", "--verify", "HEAD").strip() != head:
        raise ValueError("HEAD changed during version validation; rerun the check")
    if json.loads((root / "plugin.json").read_text())["version"] != current:
        raise ValueError("plugin.json version changed during validation; rerun the check")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all", "--", *RELEASE_PATHS) != local:
        raise ValueError("Package status changed during validation; rerun the check")
    if (changed.strip() or local.strip()) and version(current) <= version(previous):
        raise ValueError(
            f"Antigravity package changed but plugin.json is {current}; "
            f"increment beyond {previous} for Google's main-branch crawler"
        )
    return current, head, local


def check_package(root):
    manifest = json.loads((root / "plugin.json").read_text())
    version(manifest.get("version"))
    if (root / ".antigravity-plugin/plugin.json").exists():
        raise ValueError("Keep root plugin.json authoritative for Google's crawler")
    if manifest.get("name") != "coderabbit":
        raise ValueError("Preserve the existing coderabbit marketplace identity")
    if not (root / ".antigravity-plugin/README.md").is_file():
        raise ValueError("Missing Antigravity marketplace overview")
    expected = {"mcpServers": {"coderabbit": {"serverUrl": "https://mcp.coderabbit.ai/"}}}
    if json.loads((root / "mcp_config.json").read_text()) != expected:
        raise ValueError(
            "Use the hosted MCP URL with native OAuth discovery; "
            "do not add credentials, Claude OAuth fields, or a local launcher"
        )
    prompts = manifest.get("suggestedPrompts", [])
    if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3 or any(not isinstance(p, str) or not p.strip() for p in prompts):
        raise ValueError("Provide one to three actionable marketplace starter prompts")
    setup = root / "skills/coderabbit-setup/SKILL.md"
    if not setup.is_file() or "${CLAUDE_PLUGIN_ROOT}" in setup.read_text():
        raise ValueError("Provide the portable setup skill under skills/coderabbit-setup/")


def check_report(report):
    if report.get("manifest") != "plugin.json" or report.get("name") != "coderabbit":
        raise ValueError("The native loader did not select root plugin.json")
    expected = {"skills": 5, "agents": 2, "mcpServers": 1, "hooks": 0, "rules": 0, "sidecars": 0}
    if report.get("components") != expected:
        raise ValueError(f"Unexpected native components: {report.get('components')}")
    for finding in report.get("findings", []):
        # commands/ belongs to Claude/Gemini; Google has native skills instead.
        known = (
            finding.get("severity") == "warning"
            and finding.get("file") == "commands"
            and finding.get("message", "").startswith("never loaded: plugins have no commands.")
        )
        if finding.get("severity") in {"error", "warning"} and not known:
            raise ValueError(f"Unresolved native validation finding: {finding}")


def validate_native(root):
    result = subprocess.run(
        ["agy", "plugin", "validate", "--json", str(root)],
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        diagnostics = result.stdout.strip() or result.stderr.strip()
        raise ValueError(
            f"Native validator exited {result.returncode}: "
            f"{diagnostics or 'no diagnostics returned'}"
        )
    check_report(json.loads(result.stdout))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--base", help="PR base SHA or previous main SHA for the release bump guard")
    args = parser.parse_args()
    try:
        check_package(args.root)
        release_state = check_version(args.root, args.base)
        validate_native(args.root)
        if check_version(args.root, args.base) != release_state:
            raise ValueError("Release state changed during native validation; rerun the check")
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Antigravity validation failed: {error}\n")
    print("Antigravity package passed: 5 skills, 2 agents, 1 MCP server; only the known commands warning")
    if args.base:
        print("Main-based release version check passed")
    else:
        print("Release version check skipped: no --base supplied")


if __name__ == "__main__":
    main()
