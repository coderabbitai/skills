import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("check_antigravity", Path(__file__).parents[1] / "check_antigravity.py")
checks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checks)


class ReleaseGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.git("init", "-q")
        self.write("plugin.json", json.dumps({"version": "1.3.0"}))
        self.write("skills/review/SKILL.md", "initial skill")
        self.write("agents/reviewer.md", "initial agent")
        self.git("add", ".")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com", "-c", "commit.gpgsign=false", "commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_unchanged_package_needs_no_bump(self):
        checks.check_version(self.root, self.base)

    def test_shared_skill_change_requires_bump(self):
        self.write("skills/review/SKILL.md", "changed behavior")
        with self.assertRaisesRegex(ValueError, "increment beyond"):
            checks.check_version(self.root, self.base)

    def test_deleted_agent_requires_bump(self):
        (self.root / "agents/reviewer.md").unlink()
        with self.assertRaises(ValueError):
            checks.check_version(self.root, self.base)

    def test_new_mcp_config_requires_bump(self):
        self.write("mcp_config.json", "{}")
        self.git("add", "mcp_config.json")
        with self.assertRaises(ValueError):
            checks.check_version(self.root, self.base)

    def test_other_host_changes_do_not_require_bump(self):
        self.write(".claude-plugin/plugin.json", '{"version":"1.4.0"}')
        self.git("add", ".claude-plugin")
        checks.check_version(self.root, self.base)

    def test_root_helper_requires_bump(self):
        self.write("scripts/helper.py", "print('helper')")
        self.git("add", "scripts")
        with self.assertRaisesRegex(ValueError, "increment beyond"):
            checks.check_version(self.root, self.base)

    def test_patch_bump_allows_shared_changes(self):
        self.write("skills/review/SKILL.md", "changed behavior")
        self.write("plugin.json", '{"version":"1.3.1"}')
        checks.check_version(self.root, self.base)

    def test_numeric_version_order(self):
        self.write("plugin.json", '{"version":"1.10.0"}')
        checks.check_version(self.root, self.base)

    def test_downgrade_rejected(self):
        self.write("plugin.json", '{"version":"1.2.9"}')
        with self.assertRaises(ValueError):
            checks.check_version(self.root, self.base)

    def test_invalid_base_fails_closed(self):
        with self.assertRaises(subprocess.CalledProcessError):
            checks.check_version(self.root, "missing-ref")


class NativeReportTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "manifest": "plugin.json", "name": "coderabbit",
            "components": {"skills": 4, "agents": 2, "mcpServers": 1, "hooks": 0, "rules": 0, "sidecars": 0},
            "findings": [{"severity": "warning", "file": "commands", "message": "never loaded: plugins have no commands. Make each one a skill"}],
        }

    def test_known_commands_warning_allowed(self):
        checks.check_report(self.report)

    def test_new_warning_rejected(self):
        self.report["findings"].append({"severity": "warning", "file": "mcp_config.json", "message": "unknown OAuth field"})
        with self.assertRaises(ValueError):
            checks.check_report(self.report)

    def test_errors_in_known_directory_still_fail(self):
        self.report["findings"][0]["severity"] = "error"
        with self.assertRaises(ValueError):
            checks.check_report(self.report)

    def test_missing_mcp_and_extra_hooks_fail(self):
        for field, value in (("mcpServers", 0), ("hooks", 1), ("skills", 3)):
            with self.subTest(field=field):
                report = copy.deepcopy(self.report)
                report["components"][field] = value
                with self.assertRaises(ValueError):
                    checks.check_report(report)

    def test_shadow_manifest_rejected(self):
        self.report["manifest"] = ".antigravity-plugin/plugin.json"
        with self.assertRaises(ValueError):
            checks.check_report(self.report)

    def test_failed_native_validation_preserves_findings(self):
        output = json.dumps({"findings": [{"severity": "error", "message": "Missing skill directory"}]})
        result = subprocess.CompletedProcess(["agy"], 1, stdout=output, stderr="")
        with patch.object(checks.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "Missing skill directory"):
                checks.validate_native(Path("."))

    def test_failed_native_validation_reports_stderr_without_json(self):
        result = subprocess.CompletedProcess(["agy"], 2, stdout="", stderr="Cannot read plugin.json")
        with patch.object(checks.subprocess, "run", return_value=result):
            with self.assertRaisesRegex(ValueError, "Cannot read plugin.json"):
                checks.validate_native(Path("."))


if __name__ == "__main__":
    unittest.main()
