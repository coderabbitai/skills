---
name: review
description: Run a CodeRabbit AI code review on the current changes. Invoked as the `/coderabbit:review` command in Antigravity; hands off to the `code-review` skill, applying any scope or extra instruction the user gives with the command.
---

# CodeRabbit Review Command

Command entry point for hosts that load plugin commands as skills, such as
Antigravity. It mirrors the Gemini CLI command defined in this repository at
`commands/coderabbit/review.toml`.

Activate the `code-review` skill and follow its workflow to review the current
changes.

If the user gave a scope or extra instruction with the command (for example
`/coderabbit:review only uncommitted changes` or
`/coderabbit:review focus on security`), apply it to that workflow. Otherwise,
use the `code-review` skill's default scope.
