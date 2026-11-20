"""Build the connected listing and native Codex candidate from the same skills."""

import argparse
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("profile", choices=("portal", "native"))
    parser.add_argument("output", type=Path, help="new ZIP path")
    args = parser.parse_args()
    source = Path(__file__).resolve().parent
    root = source.parent.parent
    manifest = json.loads((source / "plugin.json").read_text())
    mcp = json.loads((source / "mcp.json").read_text())
    skills = ("code-review", "autofix", "coderabbit-config", "coderabbit-setup", "coderabbit-secure")
    tracked = subprocess.check_output(
        ["git", "ls-files", "-z", "--", *(f"skills/{name}/" for name in skills)],
        cwd=root,
    ).decode().split("\0")
    files = ["LICENSE", "assets/logo.png", "assets/coderabbit-small.png"]
    files.extend(path for path in tracked if path)
    with ZipFile(args.output, "x", compression=ZIP_DEFLATED) as package:
        for path in files:
            package.write(root / path, path)
        if args.profile == "portal":
            for name in ("plugin.json", "mcp.json"):
                package.write(source / name, name)
        else:
            del manifest["$schema"]
            openai = manifest.pop("extensions")["com.openai"]
            manifest["interface"] = openai["interface"]
            manifest["onboardingSkill"] = openai["onboardingSkill"]
            manifest.update(skills="./skills/", mcpServers="./.mcp.json")
            hosted = mcp["mcpServers"]["coderabbit"]
            auth = hosted["extensions"]["com.openai"]["auth"]
            native = {"mcpServers": {"coderabbit": {
                "url": hosted["url"], "scopes": auth["baseScopes"] + auth["defaultScopes"],
            }}}
            for path, data in ((".codex-plugin/plugin.json", manifest), (".mcp.json", native)):
                package.writestr(path, json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
