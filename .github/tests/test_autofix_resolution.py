"""Exercise the documented resolver against real Git tracking configurations."""

import os
import json
from pathlib import Path
import re
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]


class AutofixBranchResolutionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        self.env.update({"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"})
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

    def resolution_blocks(self):
        for filename in ("skills/autofix/SKILL.md", "skills/autofix/github.md"):
            yield filename, re.findall(r"```bash\n(.*?)```", (ROOT / filename).read_text(), re.S)[0]

    def test_failed_pr_lookup_stops_before_selection(self):
        fake_gh = '''gh() {
          case "$1 $2" in
            "repo view") printf 'acme/app\\tgithub.com\\n' ;;
            "pr list") return 42 ;;
            *) return 99 ;;
          esac
        }
'''
        for filename, block in self.resolution_blocks():
            with self.subTest(document=filename):
                result = subprocess.run(["/bin/bash", "-c", fake_gh + block + '\necho selected'],
                                        cwd=self.root, env=self.env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("PR lookup failed", result.stderr)
                self.assertNotIn("selected", result.stdout)

    def test_missing_jq_stops_before_resolution(self):
        empty_path = self.root / "empty-bin"
        empty_path.mkdir()
        for filename, block in self.resolution_blocks():
            with self.subTest(document=filename):
                result = subprocess.run(["/bin/bash", "-c", block], cwd=self.root,
                                        env={**self.env, "PATH": str(empty_path)}, text=True, capture_output=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn("jq is required", result.stderr)

    def test_same_named_fork_and_other_host_are_filtered(self):
        fixture = self.root / "pr-list.json"
        fixture.write_text(json.dumps([
            {"number": 1, "url": "https://github.com/acme/app/pull/1", "headRepository": {"nameWithOwner": "ACME/App"}},
            {"number": 2, "url": "https://github.com/acme/app/pull/2", "headRepository": {"nameWithOwner": "other/app"}},
            {"number": 3, "url": "https://github.example/acme/app/pull/3", "headRepository": {"nameWithOwner": "acme/app"}},
            {"number": 4, "url": "https://github.com/acme/app/pull/4", "headRepository": None},
        ]))
        fake_gh = '''gh() {
          case "$1 $2" in
            "repo view") printf 'acme/app\\tgithub.com\\n' ;;
            "pr list") cat "$PR_LIST_FIXTURE" ;;
            *) return 99 ;;
          esac
        }
'''
        for filename, block in self.resolution_blocks():
            with self.subTest(document=filename):
                result = subprocess.run(["/bin/bash", "-c", fake_gh + block + '\nprintf "%s\\n" "$candidates"'],
                                        cwd=self.root, env={**self.env, "PR_LIST_FIXTURE": str(fixture)}, text=True, capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual([pr["number"] for pr in json.loads(result.stdout)], [1])

    def check_head_verification(self, response, returncode, expected_message):
        for filename in ("skills/autofix/SKILL.md", "skills/autofix/github.md"):
            with self.subTest(document=filename):
                block = re.search(r"current_head=\$\(gh pr view.*?\nfi\n", (ROOT / filename).read_text(), re.S).group()
                setup = 'pr_url=https://github.com/acme/app/pull/1\npr_head_oid=abc\ngh() { ' + response + '; }\n'
                result = subprocess.run(["/bin/bash", "-c", setup + block + '\necho verified'],
                                        cwd=self.root, env=self.env, text=True, capture_output=True)
                self.assertEqual(result.returncode, returncode, result.stderr)
                self.assertIn(expected_message, result.stderr if returncode else result.stdout)
                if returncode:
                    self.assertNotIn("verified", result.stdout)

    def test_unchanged_pr_head_allows_feedback(self):
        self.check_head_verification('printf "abc\\n"', 0, "verified")

    def test_changed_pr_head_discards_feedback(self):
        self.check_head_verification('printf "def\\n"', 1, "PR head changed")

    def test_failed_head_lookup_discards_feedback(self):
        self.check_head_verification('return 42', 1, "Could not verify the PR head")


    def test_local_checkout_must_match_even_when_upstream_matches(self):
        old_head = self.git("rev-parse", "HEAD").strip()
        self.git("-c", "user.name=Test", "-c", "user.email=test@example.com",
                 "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + str(self.root / "no-hooks"),
                 "commit", "--allow-empty", "-qm", "local-only")
        new_head = self.git("rev-parse", "HEAD").strip()
        self.assertEqual(self.git("rev-parse", "@{upstream}").strip(), old_head)
        for filename in ("skills/autofix/SKILL.md", "skills/autofix/github.md"):
            block = re.search(r"local_head=\$\(git rev-parse HEAD\).*?\nfi\n", (ROOT / filename).read_text(), re.S).group()
            for head, expected in ((old_head, 1), (new_head, 0)):
                with self.subTest(document=filename, head=head):
                    result = subprocess.run(["/bin/bash", "-c", 'pr_head_oid=' + head + '\n' + block],
                                            cwd=self.root, env=self.env, text=True, capture_output=True)
                    self.assertEqual(result.returncode, expected, result.stderr)

    def check_pagination(self, cursors, expected_message=None):
        for index, cursor in enumerate(cursors, 1):
            page = {"nodes": [{"id": index}], "pageInfo": {
                "hasNextPage": cursor is not False,
                "endCursor": cursor if cursor is not False else None,
            }}
            (self.root / f"page-{index}.json").write_text(json.dumps({
                "data": {"repository": {"pullRequest": {"reviewThreads": page}}}
            }))
        setup = '''owner=acme
repo=app
pr_number=1
pr_host=github.com
pr_url=https://github.com/acme/app/pull/1
pr_head_oid=abc
gh() {
  if [ "$1 $2" = "pr view" ]; then printf 'abc\\n'; return; fi
  read -r page < page-count
  page=$((page + 1))
  printf '%s\\n' "$page" > page-count
  cat "page-$page.json"
}
'''
        for filename in ("skills/autofix/SKILL.md", "skills/autofix/github.md"):
            with self.subTest(document=filename):
                (self.root / "page-count").write_text("0\n")
                block = next(block for block in re.findall(r"```bash\n(.*?)```", (ROOT / filename).read_text(), re.S)
                             if block.startswith("all_threads="))
                result = subprocess.run(["/bin/bash", "-c", setup + block + '\nprintf "%s\\n" "$all_threads"'],
                                        cwd=self.root, env=self.env, text=True, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 1 if expected_message else 0, result.stderr)
                if expected_message:
                    self.assertIn(expected_message, result.stderr)
                    self.assertEqual(result.stdout, "")
                else:
                    self.assertEqual(len(json.loads(result.stdout)), len(cursors))

    def test_complete_pagination_collects_every_page(self):
        self.check_pagination(["A", False])

    def test_missing_next_cursor_discards_partial_feedback(self):
        self.check_pagination([None], "Missing next cursor")

    def test_repeated_cursor_discards_partial_feedback(self):
        self.check_pagination(["A", "A"], "Repeated pagination cursor")

    def test_cursor_cycle_discards_partial_feedback(self):
        self.check_pagination(["A", "B", "A"], "Repeated pagination cursor")

    def test_review_status_requires_successful_numeric_response(self):
        for filename in ("skills/autofix/SKILL.md", "skills/autofix/github.md"):
            block = next(block for block in re.findall(r"```bash\n(.*?)```", (ROOT / filename).read_text(), re.S)
                         if block.startswith("review_pending="))
            for response, expected in (("return 42", 1), ("printf nonsense", 1),
                                       ("printf ''", 1), ("printf 0", 0), ("printf 2", 0)):
                with self.subTest(document=filename, response=response):
                    script = 'pr_url=https://github.com/acme/app/pull/1\ngh() { ' + response + '; }\n' + block
                    result = subprocess.run(["/bin/bash", "-c", script], cwd=self.root,
                                            env=self.env, text=True, capture_output=True)
                    self.assertEqual(result.returncode, expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
