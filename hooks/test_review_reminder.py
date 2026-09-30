"""Exercise the configured hook commands against disposable Git repositories."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
HOOKS = json.loads((PLUGIN / "hooks/hooks.json").read_text())["hooks"]
COMMANDS = {
    "prompt": HOOKS["UserPromptSubmit"][0]["hooks"][0]["command"],
    "mark": HOOKS["PostToolUse"][0]["hooks"][0]["command"],
    "seen": HOOKS["PostToolUse"][1]["hooks"][0]["command"],
    "stop": HOOKS["Stop"][0]["hooks"][0]["command"],
}


class ReviewReminderTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="review reminder ")
        root = Path(self.tmp.name)
        self.repo, self.home, self.data, self.bin = (root / n for n in ("repo", "home", "data", "bin"))
        for d in (self.repo, self.home, self.data, self.bin):
            d.mkdir()
        (self.bin / "python3").symlink_to(sys.executable)
        self.env = {
            "PATH": f"{self.bin}:/usr/bin:/bin", "HOME": str(self.home),
            "CLAUDE_PLUGIN_ROOT": str(PLUGIN), "CLAUDE_PLUGIN_DATA": str(self.data),
            # Inherited Git variables must not redirect the hook's repository checks.
            "GIT_DIR": str(root / "elsewhere"), "GIT_WORK_TREE": str(root), "GIT_INDEX_FILE": str(root / "index"),
        }
        self.session = "session-1"

    def tearDown(self):
        self.tmp.cleanup()

    def install_cli(self):
        cli = self.home / ".local/bin/coderabbit"
        cli.parent.mkdir(parents=True)
        cli.write_text("#!/bin/sh\n")
        cli.chmod(0o755)

    def git(self, *args):
        env = {k: v for k, v in self.env.items() if not k.startswith("GIT_")}
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, env=env)

    def hook(self, action, payload, **env):
        result = subprocess.run(COMMANDS[action], shell=True, input=json.dumps(payload), text=True,
                                capture_output=True, env={**self.env, **env}, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout) if result.stdout else None

    def edit(self, path, **env):
        return self.hook("mark", {"session_id": self.session, "hook_event_name": "PostToolUse",
                                  "tool_name": "Edit", "tool_input": {"file_path": str(self.repo / path)}}, **env)

    def bash(self, command):
        return self.hook("seen", {"session_id": self.session, "hook_event_name": "PostToolUse",
                                  "tool_name": "Bash", "tool_input": {"command": command}})

    def prompt(self):
        return self.hook("prompt", {"session_id": self.session, "hook_event_name": "UserPromptSubmit"})

    def stop(self, **fields):
        event = {"session_id": self.session, "hook_event_name": "Stop", "stop_hook_active": False,
                 "cwd": str(self.repo), **fields}
        return self.hook("stop", event)

    def test_reminds_once_after_code_edits(self):
        self.install_cli()
        self.git("init")
        self.assertIsNone(self.stop())  # Nothing edited yet.
        self.edit("src/app.py")
        self.edit("src/app.py")
        reply = self.stop()
        self.assertEqual(reply["decision"], "block")
        self.assertIn("src/app.py", reply["reason"])
        self.edit("src/app.py")
        self.assertIsNone(self.stop(stop_hook_active=True))  # Continuation after the block.
        self.assertIsNone(self.stop())  # At most one reminder per turn.
        self.prompt()
        self.edit("src/other.py")
        self.assertIn("src/other.py", self.stop()["reason"])  # A new turn starts fresh.

    def test_review_clears_and_docs_do_not_count(self):
        self.install_cli()
        self.git("init")
        self.edit("README.md")
        self.edit("docs/guide.mdx")
        self.assertIsNone(self.stop())
        self.edit("lib/format.js")
        self.bash("git status")
        self.bash("/home/me/.local/bin/coderabbit --version")
        self.bash('"/home/me/.local/bin/coderabbit" review --agent --uncommitted')
        self.edit("lib/format.js")  # Fixing the review's findings.
        self.assertIsNone(self.stop())

    def test_skips_without_git_cli_or_consent(self):
        self.edit("a.py")
        self.assertIsNone(self.stop())  # Not a Git repository.
        self.git("init")
        self.prompt()
        self.edit("a.py")
        self.assertIsNone(self.stop())  # CLI not installed.
        self.install_cli()
        self.prompt()
        self.edit("a.py")
        self.assertIsNone(self.stop(permission_mode="plan"))
        self.edit("a.py", CODERABBIT_REVIEW_REMINDER="0")
        self.assertIsNone(self.hook("stop", {"session_id": self.session, "hook_event_name": "Stop",
                                             "stop_hook_active": False, "cwd": str(self.repo)},
                                    CODERABBIT_REVIEW_REMINDER="0"))
        self.assertEqual(self.stop()["decision"], "block")  # The plan-mode stop kept the record.

    def test_ignores_malformed_input(self):
        for action in COMMANDS:
            for payload in ([], {}, {"session_id": "../../etc"}, {"session_id": self.session, "tool_input": "x"}):
                self.assertIsNone(self.hook(action, payload))
        self.assertIsNone(self.stop(cwd="relative/path"))


if __name__ == "__main__":
    unittest.main()
