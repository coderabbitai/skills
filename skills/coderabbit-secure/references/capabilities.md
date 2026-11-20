# What can I do with CodeRabbit Secure over MCP?

Use this guide to choose an action or explain which part of a dashboard workflow
is available in chat. Check the connected server's tool list and input schema
before acting. Tool discovery, OAuth consent, repository access, and product
eligibility are separate checks.

## Repositories, cost and scans

| Ask in chat | What the agent can do | Limits and next steps |
| --- | --- | --- |
| Which repositories can I scan? | Find an accessible installed repository with `list_repositories` or look up a known provider ID with `get_repository`. Use scoped findings and scan history for the selected repo. | Compare finding totals and coverage across repositories in the Security inventory. |
| How much would a full scan cost? | `get_security_scan_quote` returns the estimate in cents, its freshness and the available Deep Scan credit when known. It can generate a missing estimate. | Request a fresh calculation when an estimate already exists, including a stale one. |
| What would I pay, and can I use my first-scan offer? | Compare the full-scan estimate with known credits. A paid start can carry the authorized spend limit and confirmation. | Inspect eligible free allowances, redeem a first-scan offer or retry a failed offer. Keep a credit-gap estimate separate from the final charge. |
| Can I preview a delta scan? | Look up previous runs with `list_security_scans`. The service checks baseline eligibility when a requested delta starts. | Preview the delta estimate and eligible baseline. Starting a run to answer a pricing or eligibility question can incur charges. |
| Run a full or delta scan for these repos. | `start_security_scans` accepts the code target and up to 100 repository IDs per request. Report the result per repository. Use each accepted `codeScanId` with `get_security_scan` to follow that exact run. | A blocked or skipped repository has no newly accepted run to follow. |
| Where has the scan got to? | `list_security_scans` pages through history and supports repository, scan, date and caller filters. `get_security_scan` returns recorded status, timing, findings, coverage and investigation counts when available. | The dashboard visualizes scan activity. Missing counts in a tool response remain unknown. |
| Can we continue an interrupted scan? | `recover_security_scan` retries an eligible failed run with its saved kind, or resumes an eligible partial run with an explicit spend limit. Track the new run ID. | Inspect the reported block when recovery is ineligible. |
| Show, change or remove our scheduled scan. | `get_security_scan_schedule` returns the existing rule and revision. Use `save_security_scan_schedule` to create or edit it and `delete_security_scan_schedule` for a requested removal. Full schedules use a cron and timezone. Delta schedules add one trigger: cron, coverage target, commits or days since the last scan. | Edit legacy multi-target schedules in the app. |

For billing, recovery and concurrency details, read [scan operations](scans.md).

## Findings, fixes and evidence

| Ask in chat | What the agent can do | Limits and next steps |
| --- | --- | --- |
| Which findings or secrets are open? | `list_security_findings` searches and filters by repository, scan, severity, state, kind and text. With kind `secret`, filter the saved validation status. Page through results; report saved publication, reachability and coverage evidence where present. | Use advanced dashboard filters, the finding timeline, grouped views or the in-app code viewer. |
| Why does this finding matter? Is it already being fixed? | `get_security_finding` reads the selected finding's location, recommendation, evidence, disposition and available fix task, PR or tracker links. Inspect existing evidence before recommending a change. | Open richer source context and activity history. |
| Change severity, dismiss or reopen this finding. | Use `set_security_finding_severity`, `dismiss_security_finding` or `reopen_security_finding` for the selected finding. The current hosted dismissal schema has no reason field. | Use the app when a recorded reason is part of the request and the connected tool cannot store it. |
| The fix merged. Can you mark it fixed or recheck it? | The current hosted catalog has no single-finding resolve or recheck tool. Read the current state and fix PR from the finding detail. If discovery later exposes these actions, follow the advertised schema and distinguish an accepted recheck from its result. | Mark fixed with supporting context, request a recheck, or act on a group in the app when the requested action is unavailable over MCP. |
| Request a fix and tell me when there is a PR. | `fix_security_finding` requests one AI fix. Follow the same finding with `get_security_finding` for the task status and PR. | Review the delivered change before merging. |
| Draft a Jira or Linear ticket. | `preview_security_finding_ticket` returns proposed content, priority and available destination. Finding detail can report an existing delivery. A separate authorized tracker connector can file the draft directly. | Edit and file via CodeRabbit's integrated ticket workflow, or configure ticket automation. |
| Do we have runtime evidence for this finding? | `get_security_runtime_validation_capability` supplies the canonical identity when available. Pass it to `list_security_runtime_validations` and use an attempt's ID with `get_security_runtime_validation` to read its saved outcome and evidence manifest. | Start or cancel a validation, or download available evidence files. A manifest is a record of evidence, not the file contents. |
| Export open findings from one scan. | `export_security_findings_csv` applies the finding filters and paginates the CSV. Preserve the first header and append each subsequent chunk verbatim. | Choose JSON, SARIF or a PDF report where the app offers that format. |

For ticket delivery, stored validation evidence and fix status, read
[finding follow-up](findings.md).

## Learning from feedback

| Ask in chat | MCP action |
| --- | --- |
| Teach future scans how to handle this finding. | `create_security_finding_learning` records suppression feedback or a severity change. State whether the feedback applies to this finding or the repository. Changing the current finding's severity is a separate request. |
| What have we taught scans for this repository? | `list_security_learnings` returns the 100 most recent Security learnings, with saved finding context where available. |
| Edit or remove this learning. | Select its ID from the repository list. `update_security_learning` replaces its text. `delete_security_learning` permanently removes that learning. Use the user's chosen target and action. |

## Other Security dashboard requests

| Request | Available route |
| --- | --- |
| Explore the attack surface, attack paths, posture maps or coverage trends. | Use the Security dashboard. An individual scan's coverage or a finding's saved reachability evidence can answer a narrower question. |
| Inspect PR Security findings or remediation analytics. | For a known GitHub Cloud PR, `get_pull_request` with threads can show its existing feedback; `get_pull_request_review` reads review state. Use the app for the dedicated PR Security inventory and remediation analytics. |
| Configure Security checks, linked scan context, runtime verification, reachability zones or fix automation. | Use repository Security settings in the app. Editing a scan schedule is a separate MCP workflow. |
| Change Security email notification preferences. | Use Security notification preferences in the app. |
