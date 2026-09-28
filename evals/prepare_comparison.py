#!/usr/bin/env python3
"""Prepare pinned skill snapshots and portable Lightsage requests; never launch runs."""
import argparse
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
CASES = ["review-scope", "review-untracked", "review-stream-outcome",
         "autofix-current-threads", "autofix-untrusted-guidance", "unrelated-request",
         "review-remote-runbook", "review-remote-boundaries", "review-completion-outcome",
         "review-credits-consent", "autofix-untrusted-variant"]
SKILL_DIRS = ["skills/autofix", "skills/code-review"]
SOURCE = "https://github.com/coderabbitai/skills.git"
FIXTURE = "https://github.com/Lightsage-Templates/vite-starter"
FIXTURE_SHA = "570fcdb7a3f17e1c1a6e7f372ee2f3df4c28c8d5"


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args])


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n")


def saved_repository(record):
    """Validate exported repository metadata; this is not a live API check."""
    identifier = record.get("id")
    if not isinstance(identifier, str) or not identifier.strip() or "://" in identifier:
        raise ValueError("saved repository metadata must contain an ID, not a URL")
    if record.get("url") != FIXTURE or record.get("ref") != FIXTURE_SHA:
        raise ValueError("saved repository URL and ref must match the public pinned fixture")
    return identifier


def install_command(sha):
    # Lightsage starts Claude in /home/daytona, outside /home/daytona/app.
    # A single-line CLI installation command was verified in the runner;
    # setup_commands did not execute in the tested direct-run path.
    return " && ".join([
        f"git clone --quiet {SOURCE} /tmp/coderabbit-skill-source",
        f"git -C /tmp/coderabbit-skill-source checkout --quiet {shlex.quote(sha)}",
        "mkdir -p /home/daytona/.claude/skills /home/daytona/app/.claude/skills",
        "cp -R /tmp/coderabbit-skill-source/skills/autofix /tmp/coderabbit-skill-source/skills/code-review /home/daytona/.claude/skills/",
        "cp -R /tmp/coderabbit-skill-source/skills/autofix /tmp/coderabbit-skill-source/skills/code-review /home/daytona/app/.claude/skills/",
        "rm -rf /tmp/coderabbit-skill-source",
    ])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, help="Published source commit")
    parser.add_argument("--candidate", default="HEAD", help="Candidate source commit")
    parser.add_argument("--output", type=Path, required=True, help="New output directory")
    parser.add_argument("--agent", default="claude-code:claude-sonnet-4-6")
    parser.add_argument("--repository-record", type=Path,
                        help="Exported saved repository JSON with id, url and exact ref; omit for local snapshots only")
    parser.add_argument("--runs", type=int, default=1, help="Lightsage repeats per case")
    parser.add_argument("--suite", choices=["core", "extended"], default="core",
                        help="Core eleven cases, or core plus fresh and validation cases")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    if args.output.exists():
        parser.error("--output must not exist; keep earlier experiment evidence")
    repository = None
    repository_record_hash = None
    if args.repository_record:
        try:
            record_bytes = args.repository_record.read_bytes()
            repository = saved_repository(json.loads(record_bytes))
            repository_record_hash = hashlib.sha256(record_bytes).hexdigest()
        except (OSError, ValueError, AttributeError) as error:
            parser.error(str(error))
    refs = {arm: git("rev-parse", "--verify", ref + "^{commit}").decode().strip()
            for arm, ref in [("published", args.baseline), ("candidate", args.candidate)]}
    case_names = list(CASES)
    if args.suite == "extended":
        case_names += sorted(p.parent.name for p in (ROOT / "evals").glob("*/case.yaml")
                             if p.parent.name.startswith(("fresh-", "validation-", "holdout-")))
    cases = [json.loads((ROOT / "evals" / name / "case.yaml").read_text()) for name in case_names]
    # Use identical outcome graders in both plugin snapshots. Activation is a
    # separate trace diagnostic, except the negative-control zero-call contract.
    for case in cases:
        graders = case["graders"]
        if case["name"] != "unrelated-request":
            graders = [g for g in graders
                       if not (g["type"] == "tool_used" and g.get("tool") == "Skill"
                               and g.get("max") != 0)]
        graders = [g for g in graders
                   if not (g["type"] == "llm" and g.get("arm") == "with-only")]
        case["graders"] = graders
    manifest = {"source": SOURCE, "refs": refs, "fixture": FIXTURE,
                "fixture_sha": FIXTURE_SHA, "repository": repository,
                "repository_record_sha256": repository_record_hash,
                "fixture_pin_note": "Exported metadata is checked offline. Recheck the saved repository's current ref in the dashboard before launch.",
                "agent": args.agent, "runs": args.runs,
                "cases": case_names, "skill_hashes": {}, "lightsage_batches": {}}
    manifest["case_hashes"] = {c["name"]: hashlib.sha256(
        json.dumps(c, sort_keys=True).encode()).hexdigest() for c in cases}
    for arm, sha in refs.items():
        dest = args.output / arm
        hashes = {}
        # Copy references added by either revision, not just a stale fixed list.
        names = git("ls-tree", "-r", "--name-only", sha, "--", *SKILL_DIRS).decode().splitlines()
        for name in names:
            data = git("show", f"{sha}:{name}")
            target = dest / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            hashes[name] = hashlib.sha256(data).hexdigest()
        manifest["skill_hashes"][arm] = hashes
        write_json(dest / ".claude-plugin/plugin.json", {"name": "coderabbit", "version": "1.1.1"})
        for case in cases:
            write_json(dest / "evals" / case["name"] / "case.yaml", case)
    judges = (ROOT / "evals/lightsage-judge.txt").read_text()
    for arm in (["none", "published", "candidate"] if repository else []):
        # CLI installation can run before the fixture worktree exists. Pin the
        # fixture through the saved repository's ref, not a checkout here.
        clis = []
        if arm != "none":
            clis.append(install_command(refs[arm]))
        request = {"name": f"CodeRabbit skills comparison: {arm}", "repository": repository,
                   "agent": [args.agent], "runs": args.runs,
                   "prompts": [c["execution"]["prompt"] for c in cases],
                   "judges": [judges], "clis": clis, "skills": [], "mcps": [],
                   "setup_commands": [], "cleanup_commands": [],
                   "tags": ["coderabbit-skills", "offline", "pinned-source"]}
        # The current Lightsage endpoint accepts at most twenty prompts per run.
        for start in range(0, len(cases), 20):
            suffix = "" if len(cases) <= 20 else f"-{start // 20 + 1}"
            filename = f"lightsage-{arm}{suffix}.json"
            batch = {**request, "prompts": request["prompts"][start:start + 20]}
            write_json(args.output / filename, {"request": batch})
            manifest["lightsage_batches"][filename] = case_names[start:start + 20]
    write_json(args.output / "manifest.json", manifest)
    print(f"Prepared {len(cases)} cases and 2 local skill snapshots in {args.output.resolve()}")
    if repository:
        print(f"Lightsage fanout: {len(cases) * 3 * args.runs} attempts. Nothing launched.")
        print(f"Before launch, recheck the saved repository's current ref is {FIXTURE_SHA} in the dashboard.")
    else:
        print("No Lightsage requests generated; supply --repository-record for pinned remote requests.")


if __name__ == "__main__":
    main()
