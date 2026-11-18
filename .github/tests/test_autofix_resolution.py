"""Exercise the documented resolver against real Git tracking configurations."""

import os
from pathlib import Path
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AutofixBranchResolutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
        self.git("init", "-q", "-b", "feature")
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + str(self.root / "no-hooks"),
                 "commit", "--allow-empty", "-qm", "fixture")
        self.git("config", "remote.origin.url", str(self.root / "unused-remote"))
        self.git("config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/*")
        self.git("config", "branch.feature.remote", "origin")
        self.git("config", "branch.feature.merge", "refs/heads/feature")
        self.git("config", "push.default", "upstream")
        self.git("update-ref", "refs/remotes/origin/feature", "HEAD")

    def git(self, *args):
        return subprocess.check_output(["git", *args], cwd=self.root, env=self.env, text=True)

    def check_resolution(self, expected=None):
        for filename in ("skills/autofix/SKILL.md", "skills/autofix/github.md"):
            with self.subTest(document=filename):
                source = (ROOT / filename).read_text()
                snippet = source.split("# Resolve the remote branch only under the standard fetch mapping.\n", 1)[1].split("\nlisted=", 1)[0]
                script = 'branch=$(git branch --show-current)\nremote=origin\n' + snippet + '\nprintf "%s\\n" "$head_branch"\n'
                result = subprocess.run(["bash", "-c", script], cwd=self.root, env=self.env, text=True, capture_output=True)
                if expected is None:
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    self.assertEqual(result.stdout, "")
                else:
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertEqual(result.stdout.strip(), expected)

    def test_standard_mapping_resolves_remote_branch(self):
        self.check_resolution("feature")

    def test_mapping_without_force_prefix_is_supported(self):
        self.git("config", "remote.origin.fetch", "refs/heads/*:refs/remotes/origin/*")
        self.check_resolution("feature")

    def test_local_branch_rename_keeps_remote_name(self):
        self.git("branch", "-m", "local-name")
        self.check_resolution("feature")

    def test_mirrored_tracking_namespace_requires_explicit_pr(self):
        self.git("config", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/mirror/*")
        self.git("update-ref", "refs/remotes/origin/mirror/feature", "HEAD")
        self.assertEqual(self.git("rev-parse", "--abbrev-ref", "@{push}").strip(), "origin/mirror/feature")
        self.check_resolution()

    def test_multiple_fetch_mappings_require_explicit_pr(self):
        self.git("config", "--add", "remote.origin.fetch", "+refs/heads/*:refs/remotes/origin/mirror/*")
        self.check_resolution()

    def test_missing_push_tracking_requires_explicit_pr(self):
        self.git("config", "--unset", "branch.feature.merge")
        self.check_resolution()


if __name__ == "__main__":
    unittest.main()
