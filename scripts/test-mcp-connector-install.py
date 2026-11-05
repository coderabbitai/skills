#!/usr/bin/env python3
"""Exercise connector-only installation boundaries without network or user config."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class ConnectorInstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="connector install spaces ")
        self.root = Path(self.temp.name)
        self.script = self.root / "install.sh"
        shutil.copy2(ROOT / "pilot/install.sh", self.script)
        self.log = self.root / "calls"
        for client in ("claude", "codex"):
            executable = self.root / client
            executable.write_text('''#!/bin/sh
printf '%s\\n' "$0" "$@" >> "$CONNECTOR_TEST_LOG"
if [ "$2" = get ]; then exit "${CONNECTOR_TEST_EXISTS:-1}"; fi
if [ "$2" = add ] && [ "$3" != --help ]; then exit "${CONNECTOR_TEST_ADD_EXIT:-0}"; fi
''')
            executable.chmod(0o755)
        self.env = {**os.environ, "PATH": str(self.root) + os.pathsep + os.environ.get("PATH", ""),
                    "CONNECTOR_TEST_LOG": str(self.log)}

    def tearDown(self):
        self.temp.cleanup()

    def run_installer(self, client, **env):
        self.log.write_text("")
        result = subprocess.run([str(self.script), client], env={**self.env, **env},
                                text=True, capture_output=True)
        return result, self.log.read_text().splitlines()

    def test_registers_only_selected_mcp_without_plugin_or_download(self):
        for client in ("claude", "codex"):
            with self.subTest(client=client):
                result, calls = self.run_installer(client)
                self.assertEqual(result.returncode, 0, result.stderr)
                executable = str(self.root / client)
                expected = [executable, "mcp", "add", "--help", executable, "mcp", "get", "coderabbit",
                            executable, "mcp", "add"]
                expected += (["--transport", "http", "--scope", "user", "coderabbit"]
                             if client == "claude" else ["coderabbit", "--url"])
                expected += ["https://mcp.coderabbit.ai/"]
                self.assertEqual(calls, expected)

    def test_existing_entry_is_not_overwritten(self):
        for client in ("claude", "codex"):
            result, calls = self.run_installer(client, CONNECTOR_TEST_EXISTS="0")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("will not replace", result.stderr)
            self.assertEqual(calls.count("add"), 1)  # Help only; no mutation.

    def test_native_add_failure_does_not_report_success(self):
        for client in ("claude", "codex"):
            result, _ = self.run_installer(client, CONNECTOR_TEST_ADD_EXIT="7")
            self.assertEqual(result.returncode, 7)
            self.assertNotIn("Registered", result.stdout)

    def test_invalid_client_has_no_side_effects(self):
        result, calls = self.run_installer("unsupported")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(calls, [])


if __name__ == "__main__":
    unittest.main()
