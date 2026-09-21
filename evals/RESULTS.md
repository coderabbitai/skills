# Opus 4.6 comparison — 2026-09-21, iteration 3

**The 90% per-group target is not met.** Candidate H improves the original
native cases to 30/33 audited passes, but fresh and validation groups still
fail. The later candidate I has only a focused 12/16 pilot; keep the PR draft.

| Same original eleven cases | No skills | Iteration 2 | Full candidate H |
|---|---:|---:|---:|
| Native, three repeats, audited | 11/33 | 18/33 | 30/33 |
| Lightsage, one requested attempt, audited | 3/11 | 8/11 | 9/11 |

Historical arms are reused same-day outputs, not fresh reruns. Opus 4.6 is held
fixed. Native uses Claude Code 2.1.269; the latest judge is Sonnet 4.6, whereas
the historical arms used Haiku 4.5. Manual audit uses the same substantive core
criteria. Different runners and changing case sets are not pooled into an
improvement estimate. This is a synthetic, same-author evaluation, not blinded
validation or a statistically established reliability claim.

| Full H case group | Native (3 repeats) | Lightsage |
|---|---:|---:|
| Original 11 | 30/33 | 9/11 |
| Eight development cases | 21/24 | 7/8 |
| Four validation cases | 10/12 | 4/4 |
| Four earlier fresh F cases | 12/12 | 4/4 |
| Four earlier fresh G cases | 9/12 | 3/4 |
| Four fresh H cases | 10/12 | 3/4 |
| Total (descriptive, not the acceptance gate) | 92/105 | 30/35 |

H raw judge passes were 93/105 native and 35/35 Lightsage. The audit corrected
four native false negatives (valid thread order, composed scope, exact local
base, and remote runbook), and removed five false passes for missing explicit
new-review consent renewal or exceeding sentence limits. Remaining native
failures include an invented confirmation flag, missing agent output, repeated
rejected payload details, and direct-tip rather than merge-base descriptions.
Lightsage additionally mislabeled ignored local configuration as rejected and
added incomplete outcome guidance. All observed public messages and tool calls
were retained; critical outcome/consent cases and suspected scoring mistakes
were checked against the actual evidence, not skill activation.

No observed execution performed a live review, authentication, purchase,
credential-file access or exfiltration. Native tools were limited to
Read/Glob/Grep/Skill; the observed reads were skill references. Lightsage also
wrote one requested runbook artifact. Sanitization failures repeated synthetic
payload details; they did not access real credentials. No actual saved review
was falsely reported as analyzed-clean in H. Incorrect general outcome advice
still counts as a quality failure. Zero observed critical failures is not a
claim that future behavior is guaranteed safe.

## Latest focused revision

Candidate I passed **12/16 audited attempts** across eight failure-prone cases,
two repeats each (raw 13/16). It clarified ignored remote config and merge-base
comparisons, and made fix-only proposals omit injection warnings and payload
recaps. The four sanitization attempts passed. Both initial-consent attempts
still invented a confirmation flag and omitted full renewal guidance; both
summary attempts exceeded the requested length. The correct remote answer was
an automatic false negative. No new full validation was launched after this
failed pilot, and the earlier H results do not qualify I.

The trace confirmed that invoked skills loaded the newly pinned body. Failed
initial-consent attempts did not invoke the skill. Short-description rules
improved some cases but did not consistently replace loading the full guidance.
No host-specific routing hook has been added.

## Provenance and methodology

- Full candidate H: `7a83082fec914f1e444d9f5e2ab185e5a9be0136`.
- Latest pilot I: `57f69e29c12349f9bc97c26a9c978f9e909dddc3`.
- Previous candidate: `10f97ce2c3aa8effc0b910f5a84f149d19515fd5`.
- Public fixture: `Lightsage-Templates/vite-starter` at
  `570fcdb7a3f17e1c1a6e7f372ee2f3df4c28c8d5`, pinned through a saved repository.
- H native: 35 cases x 3, $13.82 reported cost; I pilot: 8 x 2, $1.89.
- H Lightsage: 35 requested tasks, 35 completed answer executions plus one
  interrupted execution. Every observed action is retained; incomplete answers
  are infrastructure, and completed retries are never selected by best score.
- Lightsage injects a no-clarification policy and optional artifact/validation
  guidance. Its runner environment is distinct from the native tool allowlist.
- The directory validation prompt was clarified before H: the entire review,
  including tracked and untracked changes, is directory-scoped. The original
  wording could imply independent filters. Expected flags and criteria did not
  change; earlier ambiguous attempts remain diagnostic.
- Four H prompts were frozen after the H skill source, then evaluated without
  changing H. They are now development data for I, not an untouched I holdout.
- Earlier failed candidates and infrastructure failures are retained. A fixture
  checkout before Lightsage workspace creation failed without an agent answer;
  pinning through the saved repository fixed that setup error.

The current [CLI reference](https://docs.coderabbit.ai/cli/reference) and
[credit-consent documentation](https://docs.coderabbit.ai/cli#usage-based-reviews-and-consent)
were checked on 2026-09-21. They support the scope, remote refs/config/history,
completion and consent guidance. Help from an installed older 0.7.6 nightly was
inspected; 0.7.7+ service behavior was not exercised with a built current binary.
No live review, login, billing change or global upgrade ran. Other agent hosts,
slash-command parsing, release packaging and production reliability remain
untested. Saved prompts, configuration and diagnostics retain their focused
reference guidance; not every command is included in the expanded suite.

---

## Archived iteration 2

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
