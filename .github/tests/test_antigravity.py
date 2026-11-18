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
        self.empty_hooks = self.root / ".git" / "test-empty-hooks"
        self.empty_hooks.mkdir()
        empty_excludes = self.root / ".git" / "test-empty-excludes"
        empty_excludes.touch()
        self.git("config", "core.excludesFile", str(empty_excludes))
        self.write("plugin.json", json.dumps({"version": "1.3.0"}))
        self.write("skills/review/SKILL.md", "initial skill")
        self.write("agents/reviewer.md", "initial agent")
        self.git("add", ".")
        self.commit()
        self.base = self.git("rev-parse", "HEAD").strip()

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], text=True)

    def commit(self):
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "-c", "commit.gpgsign=false", "-c", f"core.hooksPath={self.empty_hooks}",
                 "commit", "-qm", "base")

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

    def test_untracked_package_addition_requires_bump(self):
        self.write("scripts/helper.py", "print('helper')")
        with self.assertRaisesRegex(ValueError, "increment beyond"):
            checks.check_version(self.root, self.base)

    def test_staging_between_observations_cannot_hide_addition(self):
        self.write("scripts/helper.py", "print('helper')")
        original_git = checks.git
        index_changes = []

        def stage_after_diff(root, *args):
            result = original_git(root, *args)
            if args[0] == "diff":
                self.git("add", "scripts/helper.py")
                index_changes.append("staged")
            return result

        with patch.object(checks, "git", side_effect=stage_after_diff):
            with self.assertRaisesRegex(ValueError, "increment beyond"):
                checks.check_version(self.root, self.base)
        self.assertEqual(index_changes, ["staged"])

    def test_unstaging_between_observations_cannot_hide_addition(self):
        self.write("scripts/helper.py", "print('helper')")
        self.git("add", "scripts/helper.py")
        original_git = checks.git
        index_changes = []

        def unstage_after_diff(root, *args):
            result = original_git(root, *args)
            if args[0] == "diff":
                self.git("reset", "-q", "HEAD", "--", "scripts/helper.py")
                index_changes.append("unstaged")
            return result

        with patch.object(checks, "git", side_effect=unstage_after_diff):
            with self.assertRaisesRegex(ValueError, "increment beyond"):
                checks.check_version(self.root, self.base)
        self.assertEqual(index_changes, ["unstaged"])

    def test_concurrent_commit_requires_rerun(self):
        self.write("skills/review/SKILL.md", "changed behavior")
        self.git("add", "skills/review/SKILL.md")
        original_git = checks.git
        commits = []

        def commit_after_diff(root, *args):
            result = original_git(root, *args)
            if args[0] == "diff":
                self.commit()
                commits.append(self.git("rev-parse", "HEAD").strip())
            return result

        with patch.object(checks, "git", side_effect=commit_after_diff):
            with self.assertRaisesRegex(ValueError, "HEAD changed.*rerun"):
                checks.check_version(self.root, self.base)
        self.assertEqual(len(commits), 1)
        self.assertNotEqual(commits[0], self.base)

    def test_concurrent_version_restore_requires_rerun(self):
        self.write("skills/review/SKILL.md", "changed behavior")
        self.write("plugin.json", '{"version":"1.3.1"}')
        original_git = checks.git
        restores = []

        def restore_after_diff(root, *args):
            result = original_git(root, *args)
            if args[0] == "diff":
                self.write("plugin.json", '{"version":"1.3.0"}')
                restores.append("restored")
            return result

        with patch.object(checks, "git", side_effect=restore_after_diff):
            with self.assertRaisesRegex(ValueError, "plugin.json version changed.*rerun"):
                checks.check_version(self.root, self.base)
        self.assertEqual(restores, ["restored"])

    def test_ignored_package_addition_needs_no_bump(self):
        self.write(".gitignore", "scripts/local-only.py\n")
        self.write("scripts/local-only.py", "print('local')")
        checks.check_version(self.root, self.base)

    def test_untracked_other_host_file_needs_no_bump(self):
        self.write(".claude-plugin/plugin.json", '{"version":"1.4.0"}')
        checks.check_version(self.root, self.base)

    def test_fixture_commit_ignores_configured_hooks(self):
        hook_dir = self.root / ".git" / "rejecting-hooks"
        hook_dir.mkdir()
        hook = hook_dir / "commit-msg"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        self.git("config", "core.hooksPath", str(hook_dir))
        self.write("skills/review/SKILL.md", "changed skill")
        self.git("add", ".")
        self.commit()
        self.assertNotEqual(self.git("rev-parse", "HEAD").strip(), self.base)

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


class PackageManifestTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        setup = self.root / ".antigravity-plugin/skills/coderabbit-setup/SKILL.md"
        setup.parent.mkdir(parents=True)
        setup.write_text("---\nname: coderabbit-setup\ndescription: Set up CodeRabbit\n---\n")
        (self.root / ".antigravity-plugin/README.md").write_text("Setup guide")
        (self.root / "mcp_config.json").write_text(json.dumps({
            "mcpServers": {"coderabbit": {"serverUrl": "https://mcp.coderabbit.ai/"}}
        }))
        self.manifest = {
            "name": "coderabbit", "version": "1.3.0",
            "skills": [".antigravity-plugin/skills"],
        }

    def check_prompts(self, prompts):
        (self.root / "plugin.json").write_text(json.dumps({**self.manifest, "suggestedPrompts": prompts}))
        checks.check_package(self.root)

    def test_valid_prompt_arrays(self):
        for prompts in (["Review my changes"], ["Connect", "Review", "Configure"]):
            with self.subTest(prompts=prompts):
                self.check_prompts(prompts)

    def test_invalid_prompt_values_report_validation_error(self):
        invalid = [None, True, 1, "Review", {"Review": True}, [], ["a"] * 4, [None], [" "]]
        for prompts in invalid:
            with self.subTest(prompts=prompts):
                with self.assertRaisesRegex(ValueError, "one to three actionable"):
                    self.check_prompts(prompts)


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
