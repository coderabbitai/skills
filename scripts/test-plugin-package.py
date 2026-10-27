#!/usr/bin/env python3
"""Offline packaging boundary tests; synthetic native headers are never executed."""
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("assemble_plugin", ROOT / "scripts/assemble-plugin.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CLIENT = "claude" if (ROOT / ".claude-plugin").is_dir() else "codex"


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="plugin package spaces ")
        self.root = Path(self.temp.name)
        self.native = self.root / "native fixture"
        self.native.write_bytes(b"\xcf\xfa\xed\xfe\x0c\x00\x00\x01" + bytes(64))
        self.checksum = hashlib.sha256(self.native.read_bytes()).hexdigest()
        self.manifest = self.root / "artifacts.json"
        self.manifest.write_text(json.dumps({"version": "0.9.0", "artifacts": [{
            "platform": "darwin-arm64", "path": str(self.native), "sha256": self.checksum}]}))
        self.output = self.root / "installed package"

    def tearDown(self):
        self.temp.cleanup()

    def assemble(self, endpoint="https://fixture.invalid/mcp", client=CLIENT):
        return module.assemble(ROOT, client, self.manifest, endpoint, self.output)

    def test_native_bundle_manifest_and_spaces(self):
        self.assemble("https://fixture.invalid/cli/mcp/mcp")
        self.assertEqual(module.digest(self.output / "bin/darwin-arm64/coderabbit"), self.checksum)
        self.assertEqual(json.loads((self.output / ".mcp.json").read_text())["mcpServers"]["coderabbit"]["url"], "https://fixture.invalid/cli/mcp/mcp")
        meta = ".claude-plugin" if CLIENT == "claude" else ".codex-plugin"
        manifest = json.loads((self.output / meta / "plugin.json").read_text())
        setup = manifest["extensions"]["com.openai"]["onboardingSkill"] if CLIENT == "codex" else "./skills/setup/SKILL.md"
        self.assertTrue((self.output / setup).is_file())
        inventory = (self.output / "bin/manifest.json").read_text()
        self.assertNotIn(str(self.root), inventory)
        hook = json.loads((self.output / "hooks/hooks.json").read_text())["hooks"]
        self.assertEqual(list(hook), ["PostToolUse"])
        self.assertEqual(hook["PostToolUse"][0]["hooks"][0]["command"], '"${CLAUDE_PLUGIN_ROOT}/bin/coderabbit" mcp-hook')
        self.assertFalse((self.output / "scripts").exists())

    def test_both_hosts_request_review_scope_and_bundle_automatic_hook(self):
        for client in ("claude", "codex"):
            with self.subTest(client=client):
                self.assemble(client=client)
                config = json.loads((self.output / (".mcp.json" if client == "claude" else "mcp.json")).read_text())["mcpServers"]["coderabbit"]
                scopes = config["oauth"]["scopes"].split() if client == "claude" else config["extensions"]["com.openai"]["auth"]["baseScopes"]
                self.assertEqual(scopes, ["connection", "account:read", "usage:read", "pull_requests:read", "review"])
                self.assertEqual((self.output / "bin/mcp-url").read_text().strip(), config["url"])
                self.assertTrue((self.output / "hooks/hooks.json").is_file())
                skill_name = "code-review" if client == "claude" else "coderabbit-review"
                self.assertTrue((self.output / "skills" / skill_name / "SKILL.md").is_file())
                shutil.rmtree(self.output)

    def test_root_and_path_endpoints_are_preserved(self):
        for endpoint in ("https://fixture.invalid", "https://fixture.invalid/", "https://fixture.invalid/mcp"):
            with self.subTest(endpoint=endpoint):
                self.assemble(endpoint)
                configured = json.loads((self.output / ".mcp.json").read_text())["mcpServers"]["coderabbit"]["url"]
                self.assertEqual(configured, endpoint)
                shutil.rmtree(self.output)

    def test_bad_digest_has_no_partial_output(self):
        self.native.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "checksum mismatch"):
            self.assemble()
        self.assertFalse(self.output.exists())

    def test_rejects_runtime_dependent_script_even_with_valid_hash(self):
        self.native.write_text("#!/bin/sh\nexit 0\n")
        manifest = json.loads(self.manifest.read_text())
        manifest["artifacts"][0]["sha256"] = module.digest(self.native)
        self.manifest.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "native"):
            self.assemble()

    def test_endpoint_and_existing_output_fail_closed(self):
        for endpoint in ("http://fixture.invalid/mcp", "https://user:password@fixture.invalid/mcp", "https://fixture.invalid/mcp?token=x", "https:///mcp", "https://fixture.invalid/#fragment", "https://fixture.invalid/ with-space"):
            with self.assertRaises(ValueError):
                self.assemble(endpoint)
        self.output.mkdir()
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.assemble()

    def launcher_fixture(self):
        directory = self.root / "launcher package/bin"
        directory.mkdir(parents=True)
        launcher = directory / "coderabbit"
        shutil.copyfile(ROOT / "scripts/coderabbit", launcher)
        launcher.chmod(0o755)
        system = {"Darwin": "darwin", "Linux": "linux"}.get(platform.system())
        arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64"}.get(platform.machine())
        if not system or not arch:
            self.skipTest("Launcher supports macOS and Linux")
        target = directory / f"{system}-{arch}"
        target.mkdir()
        binary = target / "coderabbit"
        # Deliberately a test double for launcher forwarding, never a release artifact.
        binary.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\ncat\n')
        binary.chmod(0o755)
        checksum = target / "coderabbit.sha256"
        checksum.write_text(module.digest(binary) + "\n")
        (directory / "mcp-url").write_text("https://fixture.invalid/mcp\n")
        return launcher, binary, checksum

    def test_launcher_forwards_stdin_and_spaces_without_global_cli(self):
        launcher, _, _ = self.launcher_fixture()
        descriptor = '{"directory":"space and $name and `literal`"}\n'
        for command in ("mcp-upload", "mcp-hook"):
            with self.subTest(command=command):
                result = subprocess.run([str(launcher), command], input=descriptor, text=True, capture_output=True, env={"PATH": "/nonexistent"})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, command + "\n" + descriptor)

    def test_missing_endpoint_prevents_collector_execution(self):
        launcher, _, _ = self.launcher_fixture()
        (launcher.parent / "mcp-url").unlink()
        result = subprocess.run([str(launcher), "mcp-hook"], input="{}", capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing its MCP endpoint", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_launcher_rejects_corruption_missing_binary_and_other_commands(self):
        launcher, binary, checksum = self.launcher_fixture()
        checksum.write_text("0" * 64 + "\n")
        result = subprocess.run([str(launcher), "--version"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("integrity check", result.stderr)
        binary.unlink()
        result = subprocess.run([str(launcher), "--version"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("does not contain", result.stderr)
        result = subprocess.run([str(launcher), "auth", "login"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("mcp-upload\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
