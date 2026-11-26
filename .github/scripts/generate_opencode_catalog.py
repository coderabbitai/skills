"""Generate OpenCode's HTTP catalog from the canonical skill directories."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SKILLS = ROOT / "skills"
IGNORED_DIRECTORIES = {"__pycache__", "node_modules"}


def main():
    entries = []
    for manifest in sorted(SKILLS.glob("*/SKILL.md")):
        directory = manifest.parent
        if directory.is_symlink():
            raise ValueError(f"Skill directory must not be a symlink: {directory}")
        files = []
        digest = hashlib.sha256()
        for path in sorted(directory.rglob("*")):
            relative = path.relative_to(directory)
            if any(part.startswith(".") or part in IGNORED_DIRECTORIES for part in relative.parts):
                continue
            if path.is_symlink():
                raise ValueError(f"Catalog files must not be symlinks: {path}")
            if not path.is_file():
                continue
            name = relative.as_posix()
            content = path.read_bytes()
            files.append(name)
            digest.update(name.encode("utf-8") + b"\0")
            digest.update(len(content).to_bytes(8, "big"))
            digest.update(content)
        entries.append({
            "name": directory.name,
            "version": "sha256-" + digest.hexdigest(),
            "files": files,
        })
    output = SKILLS / "index.json"
    output.write_text(json.dumps({"skills": entries}, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {output.relative_to(ROOT)} with {len(entries)} skills")


if __name__ == "__main__":
    main()
