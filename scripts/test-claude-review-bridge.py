import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import time
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("bridge", Path(__file__).resolve().parent.parent / "pilot/claude-review.py")
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)


class BridgeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.session = "11111111-1111-4111-8111-111111111111"
        self.review = "22222222-2222-4222-8222-222222222222"
        self.path = self.root / (self.session + ".jsonl")
        self.options = {"scope": "uncommitted", "dir": str(self.root), "instructions": "literal $(touch nope) `never`"}
        self.handoff = {"version": 1, "review_id": self.review, "credential": "synthetic-only-not-a-real-credential", "options": self.options, "launch_expires_at": int(time.time() * 1000) + 60000}
        self.call = {"type": "tool_use", "id": "tool_1", "name": "mcp__coderabbit__start_code_review", "input": self.options}
        self.result = {"type": "tool_result", "tool_use_id": "tool_1", "content": json.dumps({"review_id": self.review, "handoff": self.handoff})}

    def write(self, *blocks):
        self.path.write_text("".join(json.dumps({"sessionId": self.session, "message": {"content": [b]}}) + "\n" for b in blocks))

    def read(self):
        return json.loads(bridge.read_handoff(self.path, self.session, self.review, self.root))

    def test_exact_handoff_and_replayed_records(self):
        self.write(self.call, self.result, self.call, self.result)
        self.assertEqual(self.read(), self.handoff)

    def test_content_block_encoding(self):
        self.result["content"] = [{"type": "text", "text": self.result["content"]}]
        self.write(self.call, self.result)
        self.assertEqual(self.read(), self.handoff)

    def test_conflicting_replay(self):
        changed = copy.deepcopy(self.result)
        changed["content"] = "{}"
        self.write(self.call, self.result, changed)
        with self.assertRaises(bridge.Invalid): self.read()

    def test_wrong_tool(self):
        self.call["name"] = "mcp__other__start_code_review"
        self.write(self.call, self.result)
        with self.assertRaises(bridge.Invalid): self.read()

    def test_wrong_workspace(self):
        self.write(self.call, self.result)
        with self.assertRaises(bridge.Invalid):
            bridge.read_handoff(self.path, self.session, self.review, self.root.parent)

    def test_changed_options(self):
        self.call = copy.deepcopy(self.call)
        self.call["input"]["scope"] = "all"
        self.write(self.call, self.result)
        with self.assertRaises(bridge.Invalid): self.read()

    def test_error_result(self):
        self.result["is_error"] = True
        self.write(self.call, self.result)
        with self.assertRaises(bridge.Invalid): self.read()

    def test_expired(self):
        self.handoff["launch_expires_at"] = 1
        self.result["content"] = json.dumps({"review_id": self.review, "handoff": self.handoff})
        self.write(self.call, self.result)
        with self.assertRaises(bridge.Invalid): self.read()

    def test_symlink(self):
        other = self.root / "other"
        other.write_text("")
        self.path.symlink_to(other)
        with self.assertRaises(bridge.Invalid): self.read()

    def test_unrelated_messages_and_partial_tail(self):
        self.write(self.call, self.result)
        with self.path.open("a") as f:
            f.write(json.dumps({"sessionId": self.session, "message": {"content": "unrelated user prompt"}}) + "\n")
            f.write('{"partial":')
        self.assertEqual(self.read(), self.handoff)

    def test_launch_uses_separate_stdin_and_preserves_exit_code(self):
        self.write(self.call, self.result)
        binary = self.root / "verified-cli"
        argv = ["bridge", "--cli", str(binary), "--sha256", "a" * 64,
                "--dir", str(self.root), "--transcript", str(self.path),
                "--session-id", self.session, "--review-id", self.review]
        before = set(self.root.iterdir())
        with mock.patch.object(bridge.sys, "argv", argv), \
             mock.patch.object(bridge, "verify_cli"), \
             mock.patch.object(bridge.subprocess, "run", return_value=mock.Mock(returncode=7)) as run:
            self.assertEqual(bridge.main(), 7)
        args, kwargs = run.call_args
        self.assertEqual(args[0], [str(binary), "review", "--agent", "--mcp-stdin", "--dir", str(self.root)])
        self.assertEqual(json.loads(kwargs["input"]), self.handoff)
        self.assertNotIn("shell", kwargs)
        self.assertNotIn("env", kwargs)
        self.assertEqual(set(self.root.iterdir()), before)

    def test_cli_checksum_failure(self):
        binary = self.root / "cli"
        binary.write_text("synthetic executable")
        binary.chmod(0o700)
        with self.assertRaises(bridge.Invalid):
            bridge.verify_cli(binary, "a" * 64)


if __name__ == "__main__": unittest.main()
