"""Offline regression checks for command graders, using their real fixtures."""

import json
from pathlib import Path
import re
import unittest


EVALS_DIR = Path(__file__).resolve().parent


def load_pattern(case_name, grader_name):
    """Compile the named fixture grader with its declared regex flags."""
    case = json.loads((EVALS_DIR / case_name / "case.yaml").read_text(encoding="utf-8"))
    grader = next(item for item in case["graders"] if item["name"] == grader_name)
    flags = 0
    for flag in grader.get("flags", ""):
        flags |= {"i": re.IGNORECASE, "m": re.MULTILINE}[flag]
    return re.compile(grader["pattern"], flags)


class EuAuthCommandTests(unittest.TestCase):
    """Verify EU login and review commands against the bundled grader patterns."""

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
        """Load EU login and saved-region review graders once for the test class."""
        cls.login = load_pattern("review-eu-auth", "eu-agent-login")
        cls.review = load_pattern("review-eu-auth", "review-saved-region")

    def assert_supported_executables(self, pattern, arguments):
        """Check bare and quoted executable forms across common prose prefixes."""
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
        """Accept executable names, quoted paths, and prose for EU agent login."""
        self.assert_supported_executables(self.login, " auth login --agent --region eu")

    def test_review_accepts_executables_and_prose_prefixes(self):
        """Accept executable names, quoted paths, and prose for committed review."""
        self.assert_supported_executables(self.review, " review --committed --agent")

    def test_unmatched_and_mixed_executable_quotes_are_rejected(self):
        """Reject unbalanced or mismatched quotes around executable names and paths."""
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
        """Require agent mode and the explicit EU region on login commands."""
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
        """Require committed agent reviews to use the saved region without an override."""
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
        """Keep required flags on the command line while accepting fenced commands."""
        examples = (
            (self.login, "coderabbit auth login\n--agent --region eu", False),
            (self.review, "coderabbit review\n--committed --agent", False),
            (self.login, "```sh\ncoderabbit auth login --agent --region eu\n```", True),
            (self.review, "```sh\ncoderabbit review --committed --agent\n```", True),
        )
        for pattern, example, expected in examples:
            with self.subTest(example=example):
                self.assertEqual(bool(pattern.search(example)), expected)

    def test_flags_stay_in_the_selected_command_segment(self):
        """Keep flags within their command across shell and Markdown boundaries."""
        for separator in (";", "&&", "&", "||", "|", "\n", "`"):
            examples = (
                (self.login, "coderabbit auth login --agent", "echo --region eu", False),
                (self.login, "coderabbit auth login --region eu", "echo --agent", False),
                (self.review, "coderabbit review --committed", "echo --agent", False),
                (self.review, "coderabbit review --agent", "echo --committed", False),
                (
                    self.review,
                    "coderabbit review --committed --agent",
                    "echo --region eu",
                    True,
                ),
                (
                    self.login,
                    "coderabbit auth login --agent --region eu",
                    "echo status",
                    True,
                ),
            )
            for pattern, command, following, expected in examples:
                for spacing in ("", " "):
                    example = command + spacing + separator + spacing + following
                    with self.subTest(example=example):
                        self.assertEqual(bool(pattern.search(example)), expected)

    def test_prefix_flags_do_not_satisfy_command_requirements(self):
        """Ignore flags in prose or commands before the selected command."""
        examples = (
            (self.login, "--region eu: coderabbit auth login --agent", False),
            (self.login, "--agent: coderabbit auth login --region eu", False),
            (self.login, "--agent --region eu: coderabbit auth login", False),
            (self.review, "--agent: coderabbit review --committed", False),
            (self.review, "--committed: coderabbit review --agent", False),
            (
                self.review,
                "--region eu belongs to login; coderabbit review --committed --agent",
                True,
            ),
        )
        for pattern, example, expected in examples:
            with self.subTest(example=example):
                self.assertEqual(bool(pattern.search(example)), expected)

    def test_command_and_flag_tokens_match_exactly(self):
        """Reject flag and value prefixes, other subcommands, and split command names."""
        examples = (
            (self.login, "coderabbit auth login --agent --region eu-west"),
            (self.login, "coderabbit auth login --agent --region eu_other"),
            (self.login, "coderabbit auth login --agent --region eu.example"),
            (self.login, "coderabbit auth login --agent --region eu/other"),
            (self.login, "coderabbit auth login --agent-other --region eu"),
            (self.login, "coderabbit auth login prefix--agent --region eu"),
            (self.login, "coderabbit auth login --agent --regional eu"),
            (self.login, "coderabbit auth login-other --agent --region eu"),
            (self.login, "coderabbit\n auth login --agent --region eu"),
            (self.login, "coderabbit auth\n login --agent --region eu"),
            (self.review, "coderabbit review --committed-other --agent"),
            (self.review, "coderabbit review --committed --agent-other"),
            (self.review, "coderabbit review prefix--agent --committed"),
            (self.review, "coderabbit review --committed --agent --region=eu"),
            (self.review, "coderabbit review-other --committed --agent"),
        )
        for pattern, example in examples:
            with self.subTest(example=example):
                self.assertNotRegex(example, pattern)


if __name__ == "__main__":
    unittest.main()
