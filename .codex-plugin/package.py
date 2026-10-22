"""Build a Codex submission ZIP without exposing setup to shared skill discovery."""

import argparse
import io
import json
from pathlib import Path
import subprocess
import zipfile


def build(repo: Path, revision: str, output: Path) -> None:
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", "--end-of-options", f"{revision}^{{commit}}"],
        cwd=repo,
        text=True,
    ).strip()
    archive = subprocess.check_output(
        [
            "git", "archive", "--format=zip", commit,
            ".codex-plugin/plugin.json", ".codex-plugin/setup.md",
            "skills", "assets", "LICENSE",
        ],
        cwd=repo,
    )
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        manifest = json.loads(source.read(".codex-plugin/plugin.json"))
        setup_path = "skills/setup/SKILL.md"
        if setup_path in source.namelist():
            raise ValueError("Setup must not exist in the shared skills directory")
        manifest.setdefault("extensions", {}).setdefault("com.openai", {})[
            "onboardingSkill"
        ] = f"./{setup_path}"
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as target:
            for entry in source.infolist():
                data = source.read(entry)
                if entry.filename == ".codex-plugin/setup.md":
                    entry.filename = setup_path
                elif entry.filename == ".codex-plugin/plugin.json":
                    data = (json.dumps(manifest, indent=2) + "\n").encode()
                target.writestr(entry, data)
    print(f"Built {output} from {commit}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", default="HEAD", help="Committed revision to package")
    parser.add_argument("--output", required=True, type=Path, help="Output ZIP path")
    args = parser.parse_args()
    build(Path(__file__).resolve().parent.parent, args.ref, args.output)
