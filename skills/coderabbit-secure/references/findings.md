# Investigate and act on a finding

**Evidence.** Read the selected repository and finding with
`get_security_finding`. Compare the described path and recommendation with the
source and controls the host can actually inspect. For “has this been verified
at runtime?”, use `get_security_runtime_validation_capability`. If available,
pass its `findingIdentityId` as `finding_identity_id` to
`list_security_runtime_validations`. Inspect the relevant attempt with
`get_security_runtime_validation` and summarize the recorded outcome and
environment. An unavailable capability, absent attempt or null evidence
manifest leaves a gap. These tools read existing attempts.

**Tickets.** Check the finding's existing ticket status and links first.
`preview_security_finding_ticket` takes the repository, finding and requested
Jira or Linear destination. Show the draft title, destination, suggested
priority and actionable description. If the preview omits part of the draft,
compose that part from the finding and distinguish it from the returned fields.
A preview creates no ticket. If the
user wants to file it, use an available authorized tracker tool for that
destination, check for existing delivery, and report a ticket only after
receiving its ID or link. Otherwise leave a ready-to-copy draft. For ticket
preview, fix and dismiss operations, the current tool schema requires
`finding_kind: "vulnerability"` even for a Deep Scan secret. The listing
filter for secrets is `finding_kind: "secret"`.

**Fixes.** For a request to *explain* a fix, give the recommendation.
For an authorized CodeRabbit fix, read the current fix status first and reuse
an existing task or PR. Request `fix_security_finding` once. Pending or running
means the service accepted work. Follow `get_security_finding` for the
result. If a response is lost, read the finding again before considering
another request.

**Disposition.** Use `set_security_finding_severity`,
`dismiss_security_finding` or `reopen_security_finding` when the user selects
that change. A lower triage priority alone does not justify dismissal. If the
user asks to teach future scans, `create_security_finding_learning` saves
suppression or severity feedback. Explain its future scope and use the
requested finding or repository scope. Editing the current finding and
saving a learning are independent actions. To inspect existing feedback, use
`list_security_learnings`. For a requested edit or deletion, use the selected
learning ID and its current text to identify the change. Report which future
scans it applies to when the service supplies that scope.

**Export.** For a CSV request, use `export_security_findings_csv`. Save the
first page's content, then append each continuation verbatim with identical
filters and limit. Only the first page supplies headers. Mark an interrupted
export as partial and give the final path only after the requested pages are
written. In a chat-only host, report the available delivery options.
