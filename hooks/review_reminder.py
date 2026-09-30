"""Remind the agent once to review its own code changes with CodeRabbit.

On by default; set CODERABBIT_REVIEW_REMINDER=0 to turn it off. The hook never
runs CodeRabbit and grants no permission for uploads, login, spending, or fixes.

  prompt  UserPromptSubmit: start a new turn with an empty record
  mark    PostToolUse on Edit/Write/MultiEdit/NotebookEdit: record changed code files
  seen    PostToolUse on Bash: a `coderabbit ... review` run marks the turn reviewed
  stop    Stop: if code changed this turn and no review ran, block once with a reminder

A turn is reminded at most once, and edits after a review in the same turn
(fixing its findings) don't trigger another.
"""

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

DOC_SUFFIXES = {".md", ".mdx", ".markdown", ".rst", ".txt", ".adoc"}
REVIEW = re.compile(r"\bcoderabbit\b\S*\s+(?:\S+\s+)*?review\b")
MAX_LISTED = 5


def state_path(session_id):
    safe = re.sub(r"[^A-Za-z0-9_-]", "", str(session_id))[:128]
    if not safe:
        return None
    root = os.environ.get("CLAUDE_PLUGIN_DATA") or os.path.join(tempfile.gettempdir(), "coderabbit-review-reminder")
    return Path(root) / f"{safe}.json"


def load(path):
    try:
        state = json.loads(path.read_text())
        files = [f for f in state.get("files", []) if isinstance(f, str)]
        return files, state.get("done") is True
    except (OSError, ValueError, AttributeError):
        return [], False


def save(path, files, done=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"files": files, "done": done}))


def clear(path):
    try:
        path.unlink()
    except OSError:
        pass


def git_env():
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")}
    env["GIT_OPTIONAL_LOCKS"] = "0"
    return env


def in_git_repo(cwd):
    result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=cwd,
                            capture_output=True, text=True, timeout=3, env=git_env())
    return result.returncode == 0 and result.stdout.strip() == "true"


def cli_installed():
    return bool(shutil.which("coderabbit")) or (Path.home() / ".local/bin/coderabbit").is_file()


def mark(event, path):
    tool_input = event.get("tool_input")
    if not isinstance(tool_input, dict):
        return
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not isinstance(target, str) or Path(target).suffix.lower() in DOC_SUFFIXES:
        return
    files, done = load(path)
    if not done and target not in files:
        save(path, files + [target])


def seen(event, path):
    tool_input = event.get("tool_input")
    command = tool_input.get("command") if isinstance(tool_input, dict) else None
    if isinstance(command, str) and REVIEW.search(command):
        save(path, [], done=True)


def prompt(event, path):
    clear(path)


def stop(event, path):
    if event.get("stop_hook_active") is not False or event.get("permission_mode") == "plan":
        return
    files, done = load(path)
    if done or not files:
        return
    save(path, [], done=True)
    cwd = event.get("cwd")
    if not isinstance(cwd, str) or not os.path.isabs(cwd) or not in_git_repo(cwd) or not cli_installed():
        return
    listed = ", ".join(os.path.relpath(f, cwd) if os.path.isabs(f) else f for f in files[:MAX_LISTED])
    if len(files) > MAX_LISTED:
        listed += f", and {len(files) - MAX_LISTED} more"
    print(json.dumps({
        "decision": "block",
        "reason": (
            f"CodeRabbit review reminder: you changed code ({listed}) and haven't reviewed it "
            "with CodeRabbit. Use the CodeRabbit review skill (coderabbit-review) to review those changes "
            "before you finish (usually --uncommitted; add --include-untracked for new files), "
            "unless the user said not to. If CodeRabbit can't run, say so and finish. "
            "This reminder appears once and does not authorize credits, login, or retries."
        ),
    }))


def main():
    if os.environ.get("CODERABBIT_REVIEW_REMINDER") == "0":
        return
    action = sys.argv[1] if len(sys.argv) > 1 else "stop"
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            return
        path = state_path(event.get("session_id"))
        if path is None:
            return
        {"prompt": prompt, "mark": mark, "seen": seen, "stop": stop}.get(action, lambda *_: None)(event, path)
    except (ValueError, OSError, subprocess.SubprocessError):
        return


if __name__ == "__main__":
    main()
