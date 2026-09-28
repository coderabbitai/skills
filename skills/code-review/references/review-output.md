# Review output and spending consent

## Interpret saved output

Separate what was observed from what is unknown:

| Evidence | Supported conclusion |
| --- | --- |
| Heartbeat, then disconnect with no terminal event | The connection was alive. Completion and the amount analyzed are unknown. Do not claim zero analysis or that the whole diff was unreviewed. |
| Findings, then disconnect | Retain those findings as partial evidence; full coverage and the final result are unknown. |
| Completion with exit 1, failed outcome, or unreviewed files | The process reported an end state, but the review failed or has incomplete coverage. |
| Exit 0, completed with warnings, zero unreviewed files | Completed coverage; report any findings and warnings. Warnings alone do not imply failure. |
| Successful no-change skip | Nothing was reviewed; this is not an analyzed-clean result. |

A terminal event and a successful, fully covered review are different claims. Do not infer either from a heartbeat or the absence of findings.

For CLI 0.7.7+, inspect the process exit code and the completion event's
`outcome`, `message`, and `unreviewedFileCount` when present. `type: complete`
or `status: review_completed` alone does not prove success. When a field needed
to establish completion or coverage is absent, report that property as unknown.

Keep conclusions per run, including in the closing summary. Combining an interrupted run with a skipped run must not turn the interrupted run's unknown coverage into "neither analyzed any code" or "the entire diff was unreviewed." Check that the summary preserves each row's known and unknown facts.

For a brief transcript summary, give each run's result and remaining uncertainty once, within the user's requested length. Do not add a redundant recap that changes the meaning or exceeds that limit.

## Interpret credit confirmation

For `action_required` / `awaiting_confirmation`, state the billable-file count and quoted maximum price, then request explicit approval before rerunning the returned command with `--use-credits`. No consent is implied by wanting the review eventually. In the explanation, make both limits explicit: **changed content requires fresh approval, and starting another review requires fresh approval even for unchanged content or price**. Never carry the flag forward automatically.

`confirmationHeadCommitId` identifies the quoted content; it is not a `--confirm` argument. Agent mode returns a decision to the caller instead of waiting for an interactive prompt. Quote the supported command for review; execute it only after spending is authorized. See [usage-based reviews and consent](https://docs.coderabbit.ai/cli#usage-based-reviews-and-consent).
