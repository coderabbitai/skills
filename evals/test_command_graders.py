"""Offline regression checks for command graders, using their real fixtures."""

import json
from pathlib import Path
import re
import unittest


EVALS_DIR = Path(__file__).resolve().parent


def load_pattern(case_name, grader_name):
    case = json.loads((EVALS_DIR / case_name / "case.yaml").read_text(encoding="utf-8"))
    grader = next(item for item in case["graders"] if item["name"] == grader_name)
    flags = 0
    for flag in grader.get("flags", ""):
        flags |= {"i": re.IGNORECASE, "m": re.MULTILINE}[flag]
    return re.compile(grader["pattern"], flags)


class EuAuthCommandTests(unittest.TestCase):
    UNQUOTED_EXECUTABLES = (
        "coderabbit",
        "cr",
        "/absolute/path/to/coderabbit",
        "/absolute/path/to/cr",
    )
    QUOTABLE_EXECUTABLES = (
        *UNQUOTED_EXECUTABLES,
        "/Applications/Code Rabbit/coderabbit",
        "/Applications/Code Rabbit/cr",
    )
    PREFIXES = (
        "",
        "Here's the command: ",
        "Don't forget: ",
        "Users' command: ",
        "Developer's command: ",
        "Run `",
    )

    @classmethod
    def setUpClass(cls) -> None:
        cls.login = load_pattern("review-eu-auth", "eu-agent-login")
        cls.review = load_pattern("review-eu-auth", "review-saved-region")

    def assert_supported_executables(self, pattern, arguments):
        executables = (
            *self.UNQUOTED_EXECUTABLES,
            *(
                quote + executable + quote
                for executable in self.QUOTABLE_EXECUTABLES
                for quote in ("'", '"')
            ),
        )
        for executable in executables:
            for prefix in self.PREFIXES:
                suffix = "`" if prefix.endswith("`") else ""
                example = prefix + executable + arguments + suffix
                with self.subTest(example=example):
                    self.assertRegex(example, pattern)

    def test_login_accepts_executables_and_prose_prefixes(self):
        self.assert_supported_executables(self.login, " auth login --agent --region eu")

    def test_review_accepts_executables_and_prose_prefixes(self):
        self.assert_supported_executables(self.review, " review --committed --agent")

    def test_unmatched_and_mixed_executable_quotes_are_rejected(self):
        examples = [
            malformed
            for executable in self.QUOTABLE_EXECUTABLES
            for malformed in (
                "'" + executable,
                '"' + executable,
                executable + "'",
                executable + '"',
                "'" + executable + '"',
                '"' + executable + "'",
            )
        ]
        examples.extend(
            [
                '"unfinished quoted text coderabbit',
                "'unfinished quoted text cr",
                '"/Applications/Code Rabbit /coderabbit',
                "'/Applications/Code Rabbit /cr",
                "'\"coderabbit\"",
                '\"\'cr\'',
            ]
        )
        for pattern, arguments in (
            (self.login, " auth login --agent --region eu"),
            (self.review, " review --committed --agent"),
        ):
            for executable in examples:
                example = executable + arguments
                with self.subTest(example=example):
                    self.assertNotRegex(example, pattern)

    def test_login_requires_agent_and_eu_region(self):
        for example in (
            "coderabbit auth login --agent --region eu",
            "cr auth login --region eu --agent",
        ):
            with self.subTest(example=example):
                self.assertRegex(example, self.login)
        for example in (
            "coderabbit auth login --region eu",
            '"/Applications/Code Rabbit/coderabbit" auth login --agent',
            "cr auth login --agent --region us",
            "coderabbit auth login --agentless --region eu",
            "coderabbit review --agent --region eu",
        ):
            with self.subTest(example=example):
                self.assertNotRegex(example, self.login)

    def test_review_requires_agent_committed_scope_and_saved_region(self):
        for example in (
            "coderabbit review --committed --agent",
            "cr review --agent --committed",
        ):
            with self.subTest(example=example):
                self.assertRegex(example, self.review)
        for example in (
            "coderabbit review --committed",
            '"/Applications/Code Rabbit/coderabbit" review --agent',
            "cr review --uncommitted --agent",
            "coderabbit review --committed --agent --region eu",
            '"/Applications/Code Rabbit/coderabbit" review --committed --agent --region eu',
            "coderabbit review --committed --agentless",
        ):
            with self.subTest(example=example):
                self.assertNotRegex(example, self.review)

    def test_flags_stay_on_their_command_line(self):
        examples = (
            (self.login, "coderabbit auth login\n--agent --region eu", False),
            (self.review, "coderabbit review\n--committed --agent", False),
            (self.login, "```sh\ncoderabbit auth login --agent --region eu\n```", True),
            (self.review, "```sh\ncoderabbit review --committed --agent\n```", True),
        )
        for pattern, example, expected in examples:
            with self.subTest(example=example):
                self.assertEqual(bool(pattern.search(example)), expected)


if __name__ == "__main__":
    unittest.main()
