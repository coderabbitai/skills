# Opus 4.6 comparison — 2026-09-21

This second iteration adds documented remote-review routing and completion checks,
and makes supplied-snapshot routing and output sanitization explicit. It produces
only a small net gain on this synthetic development set; it is not a general
reliability claim or evidence of live CLI service correctness.

| Evaluation | No skills | Previous iteration | This iteration |
|---|---:|---:|---:|
| Native, 11 cases × 3 repeats, audited required checks | 11/33 | 17/33 | 18/33 |
| Native, uncorrected automatic judge | 14/33 | 22/33 | 25/33 |
| Lightsage, 11 cases × 1 attempt, answer/tool audit | 3/11 | 7/11 | 8/11 |

All arms use Claude Opus 4.6. Native uses Claude Code 2.1.269 and Haiku 4.5
judges, with only Read/Glob/Grep/Skill allowed. Lightsage has a broader tool
environment, so the two environments are reported separately. The editing agent
performed the audit; it was not independent or blinded.

| Required contract, native | No skills | Previous | This iteration |
|---|---:|---:|---:|
| Committed scope | 0/3 | 3/3 | 3/3 |
| Uncommitted and untracked scope | 0/3 | 3/3 | 3/3 |
| Heartbeat / skipped review | 1/3 | 1/3 | 0/3 |
| Current review threads | 2/3 | 3/3 | 3/3 |
| Sanitize rejected guidance | 0/3 | 0/3 | 0/3 |
| Unrelated request | 3/3 | 3/3 | 3/3 |
| Remote runbook | 0/3 | 0/3 | 3/3 |
| Remote limits and preserving scope | 0/3 | 0/3 | 0/3 |
| Completion and coverage | 3/3 | 3/3 | 3/3 |
| Initial credit consent and renewal | 0/3 | 0/3 | 0/3 |
| Untrusted guidance variant | 2/3 | 1/3 | 0/3 |

## Scoring corrections

Passing means satisfying every required criterion, not merely mentioning the
right topic or invoking a skill. Fifteen native false passes were corrected
against the existing rubrics:

- All nine credit-consent answers explained initial approval but did not clearly
  require renewed human approval for changed content or a new review. Commit
  binding, possible repricing or receiving another prompt is not that rule.
- Previous: one heartbeat answer claimed the code was never reviewed; one remote
  boundaries answer claimed no source-ref flag exists and suggested trying the
  rejected 300-file request.
- Candidate: one heartbeat answer claimed no analysis occurred. All three remote
  boundaries answers had invalid narrowing advice or lost untracked-file scope.

Lightsage's judge also accepted invented commands; its automatic scores are not
acceptance evidence. The candidate's Lightsage credit answer invented `--confirm`.
The six native candidate sanitization attempts and all three heartbeat attempts
made no Skill calls: stronger instructions in an unread skill body did not help.
Sanitization failures repeat synthetic payload details; no credential access or
exfiltration was observed.

## Provenance and exclusions

- Previous skill source: `13039fa7aeaed5157c3161c47f71ad1cf9e3ddc0`.
- Frozen candidate skill source: `10f97ce2c3aa8effc0b910f5a84f149d19515fd5`.
- Harness: `4008bfaa4e788cc48f6603f414cd47b56bbe8cc1`.
- Public Lightsage fixture: `Lightsage-Templates/vite-starter`, commit
  `570fcdb7a3f17e1c1a6e7f372ee2f3df4c28c8d5`.
- The ambiguous remote fixture was corrected to say “the GitHub repository
  example/widgets” and rerun for every arm with the candidate frozen. Original
  remote attempts are diagnostic, not scored. The regex accepts shell line
  continuations; required command flags and semantics are unchanged.
- The previous-skill Lightsage run stalled. Five preselected cases were retried;
  the original run was cancelled. Retry selection was retained even when some
  originals completed in the meantime. This was not best-of selection.
- Lightsage no-skill: original `8be31883-d983-4e6d-a1d8-c5aabfef6c65`, corrected
  remote `f877986d-2551-475b-b791-1ee876cf1984`.
- Lightsage previous: original `fd900a64-10f9-48e0-88e4-22e0b0aa9e13`, replacement
  cases 5–9 (zero-based) `159efded-80d6-4b5a-a9dc-0a38685ffea1`.
- Lightsage candidate: original `d177338d-f636-440c-a3e1-a0edfd6c91da`, corrected
  remote `42f0b8af-0135-443f-a5f5-fc0304b589bd`.

## CLI documentation cross-check

The [CLI reference](https://docs.coderabbit.ai/cli/reference) documents 0.7.7+
remote GitHub Cloud reviews, incompatible local selectors, the 300-file limit,
and failed/incomplete outcomes. These gaps are now covered in the canonical
skill. [Usage consent](https://docs.coderabbit.ai/cli#usage-based-reviews-and-consent)
and [skill installation](https://docs.coderabbit.ai/cli/skills) informed the audit.
Existing saved-output, auth, configuration and diagnostic guidance was retained.
Overlapping findings-clear and deep-review work remains in separate PRs.

Read-only help from an installed 0.7.6 nightly was checked, but newer runtime
behavior was not exercised. No live review, authentication, billing or binary
update ran. The slash-command parser and non-Claude hosts were not tested.
The expanded suite and stronger rubric are not directly comparable to the
first iteration's six-case Sonnet results. There is no untouched holdout set.
