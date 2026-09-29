"""Exercise the configured hook command against disposable Git repositories."""

import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


PLUGIN = Path(__file__).resolve().parents[1]
COMMAND = json.loads((PLUGIN / "hooks/hooks.json").read_text())["hooks"]["Stop"][0]["hooks"][0]["command"]


class ReviewReminderTest(unittest.TestCase):
    def test_reminder_boundaries(self):
        with tempfile.TemporaryDirectory(prefix="review reminder ") as directory:
            repo = Path(directory)
            env = {**os.environ, "CODERABBIT_REVIEW_REMINDER": "1", "CLAUDE_PLUGIN_ROOT": str(PLUGIN)}
            event = {"hook_event_name": "Stop", "stop_hook_active": False, "cwd": directory}

            def run(payload=event, enabled="1"):
                result = subprocess.run(
                    COMMAND, shell=True, input=json.dumps(payload), text=True,
                    capture_output=True, env={**env, "CODERABBIT_REVIEW_REMINDER": enabled},
                    timeout=5,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, "")
                return json.loads(result.stdout) if result.stdout else None

            def git(*args):
                subprocess.run(["git", *args], cwd=repo, check=True, capture_output=True)

            self.assertIsNone(run())  # Outside Git.
            git("init")
            (repo / "new.py").write_text("print('hello')\n")
            self.assertIsNone(run())  # Raw untracked files are excluded.
            git("add", "new.py")
            self.assertEqual(run()["decision"], "block")  # Unborn branch, staged file.
            self.assertIsNone(run(enabled=""))
            self.assertIsNone(run(enabled="0"))
            self.assertIsNone(run({**event, "stop_hook_active": True}))
            self.assertIsNone(run({**event, "permission_mode": "plan"}))
            self.assertIsNone(run({**event, "hook_event_name": "SessionStart"}))
            self.assertIsNone(run({**event, "cwd": "relative/path"}))
            self.assertIsNone(run([]))
            self.assertIsNone(run({}))
            git("-c", "user.name=Hook Test", "-c", "user.email=hook@example.invalid",
                "-c", "commit.gpgsign=false", "-c", "core.hooksPath=/dev/null", "commit", "-m", "fixture")
            self.assertIsNone(run())  # Clean, committed changes do not trigger.
            (repo / "new.py").write_text("print('changed')\n")
            self.assertEqual(run()["decision"], "block")  # Tracked unstaged edit.
            git("add", "new.py")
            self.assertEqual(run()["decision"], "block")  # Staged edit.
            (repo / "new.py").unlink()
            self.assertEqual(run()["decision"], "block")  # Tracked deletion.


if __name__ == "__main__":
    unittest.main()
