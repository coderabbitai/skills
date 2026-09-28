---
description: Run CodeRabbit reviews or answer questions about its CLI and existing findings
argument-hint: "[review scope flags | CLI question | supplied review output or findings]"
allowed-tools: "Read, Skill, Bash(git:*)"
---

# CodeRabbit Code Review

Requested scope or question: **$ARGUMENTS**

Activate the installed CodeRabbit `code-review` skill, using the host's plugin
namespace when required, and follow its routing before running any command.
Load references from that installed skill path; the [canonical source](../skills/code-review/SKILL.md)
is linked here for reference because hosts may relocate plugin files. With no
arguments, review current changes using the canonical default scope.

- Local or remote review requests follow the corresponding canonical references
  and approved authentication procedure. Preserve every requested selector.
- CLI questions, supplied output, and credit quotes use the canonical advice-only
  and consent routes; they do not authorize authentication or another review.
- Existing PR comments or supplied findings activate the installed
  [autofix skill](../skills/autofix/SKILL.md), with the requested summary, proposal,
  or authorized fix as the deliverable.

For live or supplied results, load
[output and consent](../skills/code-review/references/review-output.md).
Report actual completion evidence, partial findings, and unknown coverage;
never equate a heartbeat or no-change skip with analyzed-clean code.
Tool metadata does not grant host execution: use the canonical procedure's
command-scoped approval and credential boundaries.
