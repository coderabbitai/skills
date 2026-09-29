"""Opt-in, local-only reminder; review execution stays with the agent's skill."""

import json
import os
import subprocess
import sys


def main():
    if os.environ.get("CODERABBIT_REVIEW_REMINDER") != "1":
        return
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict) or event.get("stop_hook_active") is not False:
            return
        if event.get("hook_event_name") != "Stop" or event.get("permission_mode") == "plan":
            return
        cwd = event.get("cwd")
        if not isinstance(cwd, str) or not os.path.isabs(cwd):
            return
        status = subprocess.run(
            ["git", "status", "--porcelain=v1", "--untracked-files=no", "--ignore-submodules=all"],
            cwd=cwd, capture_output=True, timeout=3,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
        )
        if status.returncode != 0 or not status.stdout:
            return
    except (ValueError, OSError, subprocess.TimeoutExpired):
        return

    print(json.dumps({
        "decision": "block",
        "reason": (
            "CodeRabbit review reminder: tracked uncommitted changes exist. "
            "If this task changed code that still needs review, use the CodeRabbit "
            "code-review skill before finishing, preserving the user's scope and permissions. "
            "If review is not authorized, already covers these changes, is unavailable, "
            "or the changes are unrelated to this task, finish without starting a review. "
            "This reminder does not authorize uploads, login, spending, or fixes. "
            "Report skipped or incomplete review honestly; do not retry just for this reminder."
        ),
    }))


if __name__ == "__main__":
    main()
