#!/usr/bin/env python3
"""Plan CodeRabbit skill parity work without modifying any repository."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


EXPECTED_ORIGIN = "coderabbitai/skills"

TARGETS: dict[str, dict[str, Any]] = {
    "cursor": {
        "repository": "coderabbitai/cursor-plugin",
        "publication_paths": [
            ".cursor-plugin/marketplace.json",
            ".cursor-plugin/plugin.json",
            "package.json",
            "package-lock.json",
            "README.md",
        ],
        "review_paths": [
            ".cursor-plugin/marketplace.json",
            ".cursor-plugin/plugin.json",
            "skills/code-review/SKILL.md",
            "commands/coderabbit-review.md",
            "agents/code-reviewer.md",
            "rules/code-review-routing.mdc",
            "hooks/post-review-context.mjs",
            "package.json",
            "package-lock.json",
            "README.md",
        ],
        "autofix_paths": [
            ".cursor-plugin/marketplace.json",
            ".cursor-plugin/plugin.json",
            "skills/autofix/SKILL.md",
            "commands/coderabbit-autofix.md",
            "package.json",
            "package-lock.json",
            "README.md",
        ],
    },
    "codex": {
        "repository": "coderabbitai/codex-plugin",
        "publication_paths": [
            "plugins/coderabbit/.codex-plugin/plugin.json",
            "README.md",
        ],
        "review_paths": [
            "plugins/coderabbit/.codex-plugin/plugin.json",
            "plugins/coderabbit/skills/coderabbit-review/SKILL.md",
            "README.md",
        ],
    },
}

INTERNAL_PATTERNS = (
    ".agents/**",
    ".github/**",
    ".gitignore",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "LICENSE",
    "SECURITY.md",
)

REVIEW_PATTERNS = (
    "skills/code-review/**",
    "commands/coderabbit-review.md",
    "commands/coderabbit/review.toml",
    "agents/code-reviewer.md",
)

AUTOFIX_PATTERNS = ("skills/autofix/**",)
CURSOR_PACKAGE_PATTERNS = (".cursor-plugin/**",)
CLAUDE_PACKAGE_PATTERNS = (".claude-plugin/**",)
METADATA_REVIEW_PATTERNS = (
    "README.md",
    "CHANGELOG.md",
    "DISTRIBUTION_CHANNELS.md",
)
PUBLIC_ROOTS = ("skills/", "commands/", "agents/", ".cursor-plugin/")


class GitError(RuntimeError):
    pass


def git(repo: Path, *args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise GitError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def matches(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def normalize_github_origin(url: str) -> str | None:
    value = url.strip().removesuffix("/")
    patterns = (
        r"https://github\.com/([^/]+/[^/]+?)(?:\.git)?",
        r"git@github\.com:([^/]+/[^/]+?)(?:\.git)?",
        r"ssh://git@github\.com/([^/]+/[^/]+?)(?:\.git)?",
    )
    for pattern in patterns:
        match = re.fullmatch(pattern, value)
        if match:
            return match.group(1)
    return None


def resolve_base(repo: Path, requested: str | None) -> str:
    if requested:
        git(repo, "rev-parse", "--verify", requested)
        return requested
    for candidate in ("origin/main", "main", "HEAD^"):
        if git(repo, "rev-parse", "--verify", candidate, check=False):
            return candidate
    raise GitError("could not resolve a base ref; pass --base-ref")


def changed_files(
    repo: Path,
    base_ref: str,
    head_ref: str,
    include_worktree: bool,
) -> list[str]:
    paths: set[str] = set()
    committed = git(
        repo,
        "diff",
        "--name-only",
        "--diff-filter=ACMRD",
        f"{base_ref}...{head_ref}",
    )
    paths.update(line for line in committed.splitlines() if line)

    if include_worktree:
        for args in (
            ("diff", "--name-only", "--diff-filter=ACMRD"),
            ("diff", "--cached", "--name-only", "--diff-filter=ACMRD"),
            ("ls-files", "--others", "--exclude-standard"),
        ):
            output = git(repo, *args)
            paths.update(line for line in output.splitlines() if line)

    return sorted(paths)


def new_target(name: str) -> dict[str, Any]:
    return {
        "repository": TARGETS[name]["repository"],
        "decision": "not_required",
        "surfaces": [],
        "source_paths": [],
        "target_paths": [],
        "gaps": [],
    }


def raise_decision(target: dict[str, Any], decision: str) -> None:
    rank = {"not_required": 0, "review": 1, "required": 2, "gap": 3}
    if rank[decision] > rank[target["decision"]]:
        target["decision"] = decision


def add_mapping(
    target: dict[str, Any],
    decision: str,
    surface: str,
    source_path: str,
    target_paths: list[str] | None = None,
    gap: str | None = None,
) -> None:
    raise_decision(target, decision)
    target["surfaces"].append(surface)
    target["source_paths"].append(source_path)
    if target_paths:
        target["target_paths"].extend(target_paths)
    if gap:
        target["gaps"].append(gap)


def classify(paths: list[str]) -> dict[str, Any]:
    targets = {name: new_target(name) for name in TARGETS}
    internal: list[str] = []
    source_only: list[str] = []
    unmapped: list[str] = []

    for path in paths:
        if matches(path, INTERNAL_PATTERNS):
            internal.append(path)
            continue

        if matches(path, REVIEW_PATTERNS):
            add_mapping(
                targets["cursor"],
                "required",
                "code-review",
                path,
                TARGETS["cursor"]["review_paths"],
            )
            add_mapping(
                targets["codex"],
                "required",
                "code-review",
                path,
                TARGETS["codex"]["review_paths"],
            )
            continue

        if matches(path, AUTOFIX_PATTERNS):
            add_mapping(
                targets["cursor"],
                "required",
                "autofix",
                path,
                TARGETS["cursor"]["autofix_paths"],
            )
            add_mapping(
                targets["codex"],
                "gap",
                "autofix",
                path,
                gap="Codex has no mapped autofix surface; require a product decision.",
            )
            continue

        if matches(path, CURSOR_PACKAGE_PATTERNS):
            add_mapping(
                targets["cursor"],
                "required",
                "cursor-package",
                path,
                TARGETS["cursor"]["publication_paths"],
            )
            continue

        if matches(path, CLAUDE_PACKAGE_PATTERNS):
            source_only.append(path)
            continue

        if matches(path, METADATA_REVIEW_PATTERNS):
            add_mapping(
                targets["cursor"],
                "review",
                "metadata",
                path,
                TARGETS["cursor"]["publication_paths"],
            )
            add_mapping(
                targets["codex"],
                "review",
                "metadata",
                path,
                TARGETS["codex"]["publication_paths"],
            )
            continue

        if path.startswith(PUBLIC_ROOTS):
            unmapped.append(path)
            for target in targets.values():
                add_mapping(
                    target,
                    "gap",
                    "unmapped-public-surface",
                    path,
                    gap=f"No mapping exists for {path}.",
                )
            continue

        internal.append(path)

    for target in targets.values():
        for key in ("surfaces", "source_paths", "target_paths", "gaps"):
            target[key] = sorted(set(target[key]))

    return {
        "targets": targets,
        "internal_paths": sorted(set(internal)),
        "source_only_paths": sorted(set(source_only)),
        "unmapped_public_paths": sorted(set(unmapped)),
    }


def build_plan(args: argparse.Namespace) -> dict[str, Any]:
    if args.changed_file:
        paths = sorted(set(args.changed_file))
        source = {
            "repository": EXPECTED_ORIGIN,
            "origin": "supplied-paths",
            "base_ref": args.base_ref,
            "head_ref": args.head_ref,
            "head_sha": None,
            "worktree_clean": None,
            "provenance_checked": False,
            "publishing_requires": ["pushed_source_commit", "source_pull_request"],
        }
    else:
        repo = Path(args.repo).resolve()
        root = Path(git(repo, "rev-parse", "--show-toplevel"))
        origin = git(root, "remote", "get-url", "origin")
        normalized = normalize_github_origin(origin)
        if normalized != EXPECTED_ORIGIN:
            raise GitError(
                f"expected origin {EXPECTED_ORIGIN}, found {origin or '<empty>'}"
            )
        base_ref = resolve_base(root, args.base_ref)
        paths = changed_files(root, base_ref, args.head_ref, not args.no_worktree)
        head_sha = git(root, "rev-parse", args.head_ref)
        clean = not bool(git(root, "status", "--porcelain"))
        source = {
            "repository": EXPECTED_ORIGIN,
            "origin": origin,
            "base_ref": base_ref,
            "head_ref": args.head_ref,
            "head_sha": head_sha,
            "worktree_clean": clean,
            "provenance_checked": False,
            "publishing_requires": ["pushed_source_commit", "source_pull_request"],
        }

    classification = classify(paths)
    return {
        "schema_version": 1,
        "source": source,
        "changed_paths": paths,
        **classification,
        "fully_mapped": not classification["unmapped_public_paths"]
        and all(
            target["decision"] != "gap"
            for target in classification["targets"].values()
        ),
    }


def print_markdown(plan: dict[str, Any]) -> None:
    source = plan["source"]
    print("# CodeRabbit skill surface parity plan")
    print()
    print(f"- Source: `{source['repository']}`")
    print(f"- Base: `{source.get('base_ref')}`")
    print(f"- Head SHA: `{source.get('head_sha')}`")
    print(f"- Clean source: `{source.get('worktree_clean')}`")
    print(f"- Provenance checked: `{source.get('provenance_checked')}`")
    print(f"- Fully mapped: `{plan['fully_mapped']}`")
    print()
    print("| Target | Decision | Surfaces | Target paths | Gaps |")
    print("| --- | --- | --- | --- | --- |")
    for name, target in plan["targets"].items():
        surfaces = ", ".join(target["surfaces"]) or "-"
        target_paths = "<br>".join(f"`{p}`" for p in target["target_paths"]) or "-"
        gaps = "<br>".join(target["gaps"]) or "-"
        print(
            f"| {name} | {target['decision']} | {surfaces} | {target_paths} | {gaps} |"
        )
    if plan["unmapped_public_paths"]:
        print()
        print("Unmapped public paths:")
        for path in plan["unmapped_public_paths"]:
            print(f"- `{path}`")


def self_test() -> None:
    review = classify(["skills/code-review/SKILL.md"])
    assert review["targets"]["cursor"]["decision"] == "required"
    assert review["targets"]["codex"]["decision"] == "required"

    autofix = classify(["skills/autofix/SKILL.md"])
    assert autofix["targets"]["cursor"]["decision"] == "required"
    assert autofix["targets"]["codex"]["decision"] == "gap"

    internal = classify([".agents/skills/example/SKILL.md", "AGENTS.md"])
    assert internal["targets"]["cursor"]["decision"] == "not_required"
    assert internal["targets"]["codex"]["decision"] == "not_required"

    unknown = classify(["skills/config/SKILL.md"])
    assert unknown["unmapped_public_paths"] == ["skills/config/SKILL.md"]
    assert unknown["targets"]["cursor"]["decision"] == "gap"
    assert unknown["targets"]["codex"]["decision"] == "gap"

    manifest = classify([".cursor-plugin/plugin.json"])
    assert manifest["targets"]["cursor"]["decision"] == "required"
    assert ".cursor-plugin/marketplace.json" in manifest["targets"]["cursor"]["target_paths"]
    assert "package.json" in manifest["targets"]["cursor"]["target_paths"]
    assert "package-lock.json" in manifest["targets"]["cursor"]["target_paths"]
    assert manifest["targets"]["codex"]["decision"] == "not_required"

    metadata = classify(["DISTRIBUTION_CHANNELS.md"])
    assert metadata["targets"]["cursor"]["decision"] == "review"
    assert "README.md" in metadata["targets"]["cursor"]["target_paths"]
    assert metadata["targets"]["codex"]["decision"] == "review"

    assert normalize_github_origin("https://github.com/coderabbitai/skills.git") == EXPECTED_ORIGIN
    assert normalize_github_origin("git@github.com:coderabbitai/skills.git") == EXPECTED_ORIGIN
    assert normalize_github_origin("ssh://git@github.com/coderabbitai/skills") == EXPECTED_ORIGIN
    assert normalize_github_origin("coderabbitai/skills.git") is None
    assert normalize_github_origin("https://github.com.evil.test/coderabbitai/skills") is None

    print("surface_sync self-test passed")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Plan cross-repository CodeRabbit skill parity work."
    )
    parser.add_argument("command", nargs="?", default="plan", choices=("plan",))
    parser.add_argument("--repo", default=".", help="Path to coderabbitai/skills")
    parser.add_argument("--base-ref", help="Base ref; defaults to origin/main")
    parser.add_argument("--head-ref", default="HEAD", help="Head ref to compare")
    parser.add_argument(
        "--no-worktree",
        action="store_true",
        help="Exclude staged, unstaged, and untracked paths",
    )
    parser.add_argument(
        "--changed-file",
        action="append",
        help="Classify an explicit path; may be repeated and skips git discovery",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    parser.add_argument("--strict", action="store_true", help="Fail on parity gaps")
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.self_test:
        self_test()
        return 0
    try:
        plan = build_plan(args)
    except GitError as exc:
        print(f"surface_sync: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    else:
        print_markdown(plan)
    if args.strict and not plan["fully_mapped"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
