#!/usr/bin/env python3
"""Offline packaging boundary tests; synthetic native headers are never executed."""
import hashlib
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import platform
import queue
import re
import shlex
import shutil
import subprocess
import tempfile
import threading
import unittest
import zipfile
from unittest.mock import patch

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
        self.manifest.write_text(json.dumps({"version": "0.9.0", "plugin_version": "1.3.0-mcp.1", "artifacts": [{
            "platform": "darwin-arm64", "path": str(self.native), "sha256": self.checksum}]}))
        self.output = self.root / "installed package"

    def tearDown(self):
        self.temp.cleanup()

    def assemble(self, endpoint="https://fixture.invalid/mcp", client=CLIENT, launcher="hook", delivery="bundled"):
        return module.assemble(ROOT, client, self.manifest, endpoint, self.output, launcher, delivery)

    def test_download_packages_omit_native_files_without_changing_shared_cli(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["artifacts"][0]["archive_sha256"] = "a" * 64
        self.manifest.write_text(json.dumps(manifest))
        shared = (ROOT / "skills/code-review/SKILL.md").read_bytes()
        for client in ("claude", "codex"):
            for launcher in (("hook", "direct") if client == "claude" else ("direct",)):
                with self.subTest(client=client, launcher=launcher):
                    self.assemble(client=client, launcher=launcher, delivery="download")
                    config = json.loads((self.output / "cli.json").read_text())
                    self.assertEqual(config["launcher"], "./scripts/coderabbit")
                    self.assertEqual(config["launchMode"], launcher)
                    metadata = ".claude-plugin" if client == "claude" else ".codex-plugin"
                    self.assertEqual(json.loads((self.output / metadata / "plugin.json").read_text())["version"], "1.3.0-mcp.1")
                    self.assertFalse((self.output / "bin").exists())
                    for path in self.output.rglob("*"):
                        if path.is_file():
                            self.assertLess(path.stat().st_size, 5 * 1024 * 1024)
                            self.assertNotEqual(path.read_bytes(), self.native.read_bytes())
                    self.assertEqual((self.output / "runtime/darwin-arm64.url").read_text(),
                                     "https://cli.coderabbit.ai/releases/0.9.0/coderabbit-darwin-arm64.zip\n")
                    self.assertEqual((ROOT / "skills/code-review/SKILL.md").read_bytes(), shared)
                    if launcher == "hook":
                        hook = json.loads((self.output / "hooks/hooks.json").read_text())
                        command = hook["hooks"]["PostToolUse"][0]["hooks"][0]["command"]
                        self.assertIn("/scripts/coderabbit", command)
                    shutil.rmtree(self.output)

    def test_download_package_requires_archive_and_plugin_version_pins(self):
        with self.assertRaisesRegex(ValueError, "archive SHA-256"):
            self.assemble(delivery="download")
        self.assertFalse(self.output.exists())
        manifest = json.loads(self.manifest.read_text())
        manifest["artifacts"][0]["archive_sha256"] = "a" * 64
        del manifest["plugin_version"]
        self.manifest.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValueError, "explicit plugin_version"):
            self.assemble(delivery="download")
        self.assertFalse(self.output.exists())

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

    def test_claude_hook_matches_only_plugin_owned_review_start(self):
        self.assemble(client="claude")
        config = json.loads((self.output / ".mcp.json").read_text())["mcpServers"]["coderabbit"]
        self.assertEqual(config["oauth"]["scopes"].split(),
                         ["connection", "account:read", "usage:read", "pull_requests:read", "review"])
        self.assertEqual((self.output / "bin/mcp-url").read_text().strip(), config["url"])
        hook = json.loads((self.output / "hooks/hooks.json").read_text())["hooks"]["PostToolUse"][0]
        self.assertIsNotNone(re.fullmatch(hook["matcher"], "mcp__plugin_coderabbit_coderabbit__start_code_review"))
        for name in ("mcp__coderabbit__start_code_review", "mcp__other__start_code_review",
                     "mcp__plugin_other_coderabbit__start_code_review",
                     "mcp__plugin_coderabbit_coderabbit__get_code_review"):
            with self.subTest(tool=name):
                self.assertIsNone(re.search(hook["matcher"], name))

    def test_codex_hook_assembly_fails_before_writing_a_package(self):
        for delivery in ("bundled", "download"):
            with self.subTest(delivery=delivery):
                with self.assertRaisesRegex(ValueError, "verified plugin server identity"):
                    self.assemble(client="codex", launcher="hook", delivery=delivery)
                self.assertFalse(self.output.exists())

    def test_direct_channel_has_no_hook_and_preserves_review_skill(self):
        for client in ("claude", "codex"):
            with self.subTest(client=client):
                result = self.assemble(client=client, launcher="direct")
                self.assertEqual(result["launcher"], "direct")
                self.assertFalse((self.output / "hooks").exists())
                meta = ".claude-plugin" if client == "claude" else ".codex-plugin"
                manifest = json.loads((self.output / meta / "plugin.json").read_text())
                self.assertNotIn("hooks", manifest)
                if client == "codex":
                    portable = json.loads((self.output / "plugin.json").read_text())
                    self.assertEqual(portable["$schema"], "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json")
                    self.assertNotIn("hooks", portable["extensions"]["com.openai"])
                self.assertEqual((self.output / "bin/launch-mode").read_text().strip(), "direct")
                skill = "code-review" if client == "claude" else "coderabbit-review"
                self.assertIn("--mcp-stdin", (self.output / "skills" / skill / "SKILL.md").read_text())
                shutil.rmtree(self.output)

    @unittest.skipUnless(os.environ.get("CODEX_TEST_BIN"), "Set CODEX_TEST_BIN for native loader validation")
    def test_codex_native_direct_discovery(self):
        """Read assembled packages through Codex without installing or executing them."""
        executable = Path(os.environ["CODEX_TEST_BIN"])
        self.assertTrue(executable.is_absolute() and executable.is_file())
        artifacts = json.loads(self.manifest.read_text())
        artifacts["artifacts"][0]["archive_sha256"] = "a" * 64
        self.manifest.write_text(json.dumps(artifacts))
        for launcher, delivery in ((mode, delivery) for delivery in ("bundled", "download")
                                   for mode in ("direct",)):
            with self.subTest(launcher=launcher, delivery=delivery):
                self.assemble(client="codex", launcher=launcher, delivery=delivery)
                marketplace = self.root / "marketplace"
                (marketplace / ".claude-plugin").mkdir(parents=True, exist_ok=True)
                manifest = marketplace / ".claude-plugin/marketplace.json"
                shutil.move(self.output, marketplace / "plugin")
                manifest.write_text(json.dumps({"name": "native-package-check",
                    "owner": {"name": "CodeRabbit"},
                    "plugins": [{"name": "coderabbit", "source": "./plugin"}]}))
                profile = self.root / "codex-profile"
                profile.mkdir(exist_ok=True)
                process = subprocess.Popen([str(executable), "app-server", "--stdio"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                    text=True, env={**os.environ, "CODEX_HOME": str(profile)})
                responses = queue.Queue()
                def read_responses():
                    for line in process.stdout:
                        responses.put(line)
                    responses.put(None)
                reader = threading.Thread(target=read_responses, daemon=True)
                reader.start()
                def request(request_id, method, params):
                    process.stdin.write(json.dumps({"id": request_id, "method": method, "params": params}) + "\n")
                    process.stdin.flush()
                    for _ in range(50):
                        line = responses.get(timeout=15)
                        self.assertIsNotNone(line, "Codex app-server exited before completing the loader check")
                        response = json.loads(line)
                        if response.get("id") == request_id:
                            self.assertNotIn("error", response)
                            return response["result"]
                    self.fail("Native loader did not return the requested response")
                try:
                    request(1, "initialize", {"clientInfo": {"name": "coderabbit-package-test", "version": "1"},
                        "capabilities": {"experimentalApi": True}})
                    process.stdin.write(json.dumps({"method": "initialized", "params": {}}) + "\n")
                    process.stdin.flush()
                    plugin = request(2, "plugin/read", {"marketplacePath": str(manifest),
                        "pluginName": "coderabbit"})["plugin"]
                    self.assertEqual(plugin["mcpServers"], ["coderabbit"])
                    self.assertEqual({skill["name"] for skill in plugin["skills"]},
                        {"coderabbit:setup", "coderabbit:coderabbit-review", "coderabbit:autofix"})
                    self.assertEqual([hook["eventName"] for hook in plugin["hooks"]],
                        [])
                finally:
                    process.stdin.close()
                    try:
                        process.wait(timeout=3)
                    except subprocess.TimeoutExpired:
                        process.terminate()
                        process.wait(timeout=3)
                    reader.join(timeout=3)
                    process.stdout.close()
                    shutil.rmtree(marketplace / "plugin")

    @unittest.skipUnless(os.environ.get("CODEX_TEST_BIN"), "Set CODEX_TEST_BIN for native install validation")
    def test_codex_retains_cli_only_guide_without_mcp_connection(self):
        artifacts = json.loads(self.manifest.read_text())
        artifacts["artifacts"][0]["archive_sha256"] = "a" * 64
        self.manifest.write_text(json.dumps(artifacts))
        self.assemble(client="codex", launcher="direct", delivery="download")
        marketplace = self.root / "marketplace"
        (marketplace / ".agents/plugins").mkdir(parents=True)
        shutil.move(self.output, marketplace / "plugin")
        (marketplace / ".agents/plugins/marketplace.json").write_text(json.dumps({
            "name": "cli-only-install-check", "plugins": [{"name": "coderabbit",
                "source": {"source": "local", "path": "./plugin"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                "category": "Developer Tools"}]}))
        home = self.root / "home"
        home.mkdir()
        profile = home / ".codex"
        profile.mkdir()
        env = {**os.environ, "HOME": str(home), "CODEX_HOME": str(profile),
               "XDG_CONFIG_HOME": str(home / "config"), "XDG_CACHE_HOME": str(home / "cache")}
        executable = os.environ["CODEX_TEST_BIN"]
        registration = subprocess.run([executable, "plugin", "marketplace", "add", str(marketplace)],
                                      env=env, cwd=home, capture_output=True, text=True, timeout=20)
        self.assertEqual(registration.returncode, 0, registration.stderr)
        result = subprocess.run([executable, "plugin", "add", "coderabbit@cli-only-install-check", "--json"],
                                env=env, cwd=home, capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        installed = Path(json.loads(result.stdout)["installedPath"])
        installed.resolve().relative_to(profile.resolve())
        legacy = installed / "skills/coderabbit-review/references/standalone-cli"
        self.assertEqual((legacy / "guide.md").read_bytes(), (ROOT / "skills/code-review/SKILL.md").read_bytes())
        self.assertEqual((legacy / "references/auth-recovery.md").read_bytes(),
                         (ROOT / "skills/code-review/references/auth-recovery.md").read_bytes())

    def test_pilot_instructions_do_not_replace_shared_cli_consumers(self):
        shared_paths = [ROOT / "skills/code-review/SKILL.md", ROOT / "agents/code-reviewer.md"]
        shared = {path: path.read_bytes() for path in shared_paths}
        for content in shared.values():
            self.assertIn(b"review --agent", content)
            self.assertNotIn(b"start_code_review", content)
        for client in ("claude", "codex"):
            for launcher in (("hook", "direct") if client == "claude" else ("direct",)):
                with self.subTest(client=client, launcher=launcher):
                    self.assemble(client=client, launcher=launcher)
                    skill_name = "code-review" if client == "claude" else "coderabbit-review"
                    skill = self.output / "skills" / skill_name
                    self.assertIn("start_code_review", (skill / "SKILL.md").read_text())
                    self.assertIn("references/standalone-cli/guide.md", (skill / "SKILL.md").read_text())
                    legacy = skill / "references/standalone-cli"
                    self.assertEqual((legacy / "guide.md").read_bytes(), shared[ROOT / "skills/code-review/SKILL.md"])
                    self.assertFalse((legacy / "SKILL.md").exists())
                    for reference in (ROOT / "skills/code-review/references").rglob("*"):
                        if reference.is_file():
                            self.assertEqual((legacy / "references" / reference.relative_to(ROOT / "skills/code-review/references")).read_bytes(), reference.read_bytes())
                    self.assertTrue((skill / "references/mcp-upload.md").is_file())
                    self.assertFalse((skill / "references/auth-recovery.md").exists())
                    self.assertTrue((self.output / "skills/setup/SKILL.md").is_file())
                    if client == "claude":
                        self.assertIn("start_code_review", (self.output / "agents/code-reviewer.md").read_text())
                    self.assertEqual({path: path.read_bytes() for path in shared_paths}, shared)
                    shutil.rmtree(self.output)

    def test_nonobject_manifest_or_artifact_has_no_partial_package(self):
        for root in (None, [], "manifest", 1):
            with self.subTest(root=root):
                self.manifest.write_text(json.dumps(root))
                with self.assertRaisesRegex(ValueError, "manifest must be a JSON object"):
                    self.assemble()
                self.assertFalse(self.output.exists())
        for entry in (None, [], "artifact", 1):
            with self.subTest(entry=entry):
                self.manifest.write_text(json.dumps({"version": "0.9.0", "artifacts": [entry]}))
                with self.assertRaisesRegex(ValueError, "artifact must be a JSON object"):
                    self.assemble()
                self.assertFalse(self.output.exists())

    def test_unresolved_artifact_user_reports_clean_error_without_partial_output(self):
        manifest = json.loads(self.manifest.read_text())
        manifest["artifacts"][0]["path"] = "~missing-artifact-user/native"
        self.manifest.write_text(json.dumps(manifest))
        stderr = StringIO()
        argv = ["assemble-plugin.py", "--client", CLIENT,
                "--artifacts", str(self.manifest), "--mcp-url", "https://fixture.invalid/mcp",
                "--output", str(self.output)]
        with patch("sys.argv", argv), patch("sys.stderr", stderr), patch.object(
            Path, "expanduser", side_effect=RuntimeError("Could not determine home directory.")
        ):
            with self.assertRaises(SystemExit) as raised:
                module.main()
        self.assertEqual(raised.exception.code, 1)
        self.assertEqual(stderr.getvalue(),
                         "Cannot assemble CodeRabbit plugin: Invalid artifact path: Could not determine home directory.\n")
        self.assertFalse(self.output.exists())

    def test_unknown_launcher_has_no_partial_output(self):
        with self.assertRaisesRegex(ValueError, "Launcher"):
            self.assemble(launcher="automatic")
        self.assertFalse(self.output.exists())

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
        binary.write_text('#!/bin/sh\nprintf "%s\\n" "$@"\n/bin/cat\n')
        binary.chmod(0o755)
        checksum = target / "coderabbit.sha256"
        checksum.write_text(module.digest(binary) + "\n")
        (directory / "mcp-url").write_text("https://fixture.invalid/mcp\n")
        return launcher, binary, checksum

    def runtime_fixture(self, native=None):
        # The shell executable is a forwarding test double, not a release CLI.
        root = self.root / "download package"
        (root / "scripts").mkdir(parents=True)
        (root / "runtime").mkdir()
        launcher = root / "scripts/coderabbit"
        shutil.copyfile(ROOT / "scripts/coderabbit-runtime", launcher)
        launcher.chmod(0o755)
        system = {"Darwin": "darwin", "Linux": "linux"}.get(platform.system())
        arch = {"arm64": "arm64", "aarch64": "arm64", "x86_64": "x64"}.get(platform.machine())
        if not system or not arch:
            self.skipTest("Runtime adapter supports macOS and Linux")
        target = f"{system}-{arch}"
        if native is None:
            native = b'#!/bin/sh\nprintf "%s\\n" "$@"\ncat\n'
        archive = self.root / "native.zip"
        with zipfile.ZipFile(archive, "w") as zipped:
            zipped.writestr("coderabbit", native)
        metadata = root / "runtime"
        (metadata / "version").write_text("0.9.0\n")
        (metadata / "mcp-url").write_text("https://fixture.invalid/mcp\n")
        (metadata / f"{target}.sha256").write_text(hashlib.sha256(native).hexdigest() + "\n")
        (metadata / f"{target}.archive.sha256").write_text(module.digest(archive) + "\n")
        (metadata / f"{target}.url").write_text(f"https://cli.coderabbit.ai/releases/0.9.0/coderabbit-{target}.zip\n")
        mocks = self.root / "mock tools"
        mocks.mkdir()
        # Change only tool resolution in this copied adapter to keep the
        # installer offline. Production always uses system curl/hash tools.
        launcher.write_text(launcher.read_text().replace(
            "PATH=/usr/bin:/bin:/usr/sbin:/sbin",
            "PATH=" + shlex.quote(str(mocks) + ":/usr/bin:/bin"), 1))
        curl = mocks / "curl"
        curl.write_text('#!/bin/sh\nprintf "download\\n" >> "$CODERABBIT_TEST_CURL_LOG"\n'
                        'while [ "$#" -gt 0 ]; do\n'
                        '  if [ "$1" = --output ]; then output=$2; shift; fi\n'
                        '  shift\ndone\ncp "$CODERABBIT_TEST_ARCHIVE" "$output"\n')
        curl.chmod(0o755)
        global_cli = mocks / "coderabbit"
        global_cli.write_text('#!/bin/sh\necho unexpected-global-cli\nexit 99\n')
        global_cli.chmod(0o755)
        log = self.root / "downloads.log"
        env = {**os.environ, "PATH": str(mocks) + ":/usr/bin:/bin",
               "CODERABBIT_TEST_ARCHIVE": str(archive), "CODERABBIT_TEST_CURL_LOG": str(log)}
        data = self.root / "persistent data"
        binary = data / "0.9.0" / target / "coderabbit"
        def run(*args, stdin=""):
            return subprocess.run([str(launcher), "--data-dir", str(data), *args],
                                  input=stdin, text=True, capture_output=True, env=env, timeout=10)
        return run, binary, metadata, target, log

    def test_preparation_installs_pinned_runtime_reuses_cache_and_forwards_stdin(self):
        run, binary, _, _, log = self.runtime_fixture()
        first = run("--prepare")
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertTrue(binary.is_file())
        self.assertEqual(first.stdout, "--version\n")
        self.assertEqual(run("--prepare").returncode, 0)
        self.assertEqual(log.read_text(), "download\n")
        handoff = '{"instructions":"literal $(command) and `text`"}\n'
        result = run("mcp-hook", stdin=handoff)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "mcp-hook\n" + handoff)
        self.assertEqual(log.read_text(), "download\n")

    def test_review_does_not_prepare_missing_corrupt_runtime_or_use_global_cli(self):
        run, binary, _, _, log = self.runtime_fixture()
        missing = run("mcp-hook", stdin="{}")
        self.assertNotEqual(missing.returncode, 0)
        self.assertFalse(log.exists())
        self.assertEqual(missing.stdout, "")
        self.assertEqual(run("--prepare").returncode, 0)
        binary.write_text("corrupt")
        failed = run("review", "--agent", "--mcp-stdin", stdin="{}")
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(failed.stdout, "")
        self.assertEqual(log.read_text(), "download\n")
        self.assertNotEqual(run("auth", "login").returncode, 0)
        self.assertNotEqual(run("review", "--agent", "--mcp-stdin", "--host-url", "https://other.invalid").returncode, 0)

    def test_cli_preserves_caller_git_without_using_caller_checksum_helpers(self):
        caller = self.root / "caller tools"
        caller.mkdir()
        git = caller / "git"
        git.write_text('#!/bin/sh\necho caller-git-selected\n')
        git.chmod(0o755)
        global_cli = caller / "coderabbit"
        global_cli.write_text('#!/bin/sh\necho unexpected-global-cli\nexit 99\n')
        global_cli.chmod(0o755)
        helper_log = self.root / "unexpected-checksum-helper"
        for name in ("shasum", "sha256sum"):
            helper = caller / name
            helper.write_text('#!/bin/sh\ntouch ' + shlex.quote(str(helper_log)) + '\nexit 0\n')
            helper.chmod(0o755)
        native = b'#!/bin/sh\ncase "$1" in\n mcp-hook) exit 0;;\n --version) echo 0.9.0;;\n config) git --version;;\nesac\n'
        env = {**os.environ, "PATH": str(caller) + ":/usr/bin:/bin"}
        for delivery in ("bundled", "download"):
            with self.subTest(delivery=delivery):
                if delivery == "download":
                    prepare, binary, _, _, _ = self.runtime_fixture(native)
                    self.assertEqual(prepare("--prepare").returncode, 0)
                    command = [str(self.root / "download package/scripts/coderabbit"),
                               "--data-dir", str(self.root / "persistent data")]
                else:
                    launcher, binary, checksum = self.launcher_fixture()
                    binary.write_bytes(native)
                    checksum.write_text(module.digest(binary) + "\n")
                    command = [str(launcher)]
                result = subprocess.run(command + ["config", "--agent"], env=env,
                                        text=True, capture_output=True, timeout=10)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "caller-git-selected\n")
                binary.write_text("corrupt")
                rejected = subprocess.run(command + ["--version"], env=env,
                                          text=True, capture_output=True, timeout=10)
                self.assertNotEqual(rejected.returncode, 0)
                self.assertFalse(helper_log.exists())

    def test_bad_archive_or_native_hash_never_installs_candidate(self):
        run, binary, metadata, target, _ = self.runtime_fixture()
        archive_hash = metadata / f"{target}.archive.sha256"
        original = archive_hash.read_text()
        archive_hash.write_text("0" * 64 + "\n")
        rejected = run("--prepare")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(rejected.stdout, "")
        self.assertFalse(binary.exists())
        self.assertEqual(list(binary.parent.glob(".prepare.*")), [])
        archive_hash.write_text(original)
        (metadata / f"{target}.sha256").write_text("0" * 64 + "\n")
        rejected = run("--prepare")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertEqual(rejected.stdout, "")
        self.assertFalse(binary.exists())
        self.assertEqual(list(binary.parent.glob(".prepare.*")), [])

    def test_matching_hash_without_mcp_support_does_not_install(self):
        run, binary, _, _, _ = self.runtime_fixture(
            b'#!/bin/sh\nif [ "$1" = mcp-hook ]; then exit 1; fi\necho 0.9.2\n')
        rejected = run("--prepare")
        self.assertNotEqual(rejected.returncode, 0)
        self.assertIn("does not support MCP review", rejected.stderr)
        self.assertEqual(rejected.stdout, "")
        self.assertFalse(binary.exists())
        self.assertEqual(list(binary.parent.glob(".prepare.*")), [])

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

    def test_local_config_preserves_arguments_without_mcp_endpoint(self):
        launcher, _, _ = self.launcher_fixture()
        (launcher.parent / "mcp-url").unlink()
        proposal = str(self.root / "proposal with spaces.yaml")
        for args in (["config", "--agent"],
                     ["config", "apply", proposal, "--agent", "--dry-run", "--base", "none"]):
            with self.subTest(args=args):
                result = subprocess.run([str(launcher), *args], input="", text=True,
                                        capture_output=True, env={"PATH": "/nonexistent"})
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "\n".join(args) + "\n")

    def test_direct_review_forwards_only_scoped_mode_and_literal_stdin(self):
        launcher, _, _ = self.launcher_fixture()
        handoff = '{"instructions":"literal $(command) and `text`"}\n'
        args = ["review", "--agent", "--mcp-stdin", "--dir", str(self.root / "workspace spaces")]
        result = subprocess.run([str(launcher), *args], input=handoff, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "\n".join(args) + "\n" + handoff)
        for invalid in (["review"], ["review", "--agent"],
                        ["review", "--agent", "--mcp-stdin", "--host-url", "https://other.invalid"],
                        ["review", "--agent", "--mcp-stdin", "--dir"],
                        ["review", "--agent", "--mcp-stdin", "--base", "main"]):
            rejected = subprocess.run([str(launcher), *invalid], input=handoff, text=True, capture_output=True)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertEqual(rejected.stdout, "")

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
