# CodeRabbit Review Mod v0.1.0 submission notes

## Source

- Repository: `coderabbitai/skills`
- Plugin folder: `mods/coderabbit`
- Release source: `main` after the candidate PR is merged
- Manifest name: `coderabbit-mod`
- Display name: CodeRabbit Review Mod
- Version: `0.1.0`
- Intended hosts: Claude Code terminal (2.1.289 or later) and Local Code sessions
  in a mod-enabled Claude Desktop app

Use the candidate PR branch only to preview validation. A saved directory draft
locks its repository, folder, and branch; do not save a release submission against
a temporary branch. The existing repository-root CodeRabbit plugin is a separate
package and must not be replaced or downgraded to publish this mod.

## Listing text

Run CodeRabbit reviews from Claude Code with `/coderabbit-review`. Choose tracked,
committed, or uncommitted changes, see when the review is running, and bring the
original findings into your conversation while you keep chatting. Completion
updates the review card, shows a toast, and saves the result as context without
starting a Claude turn. Requires the official CodeRabbit CLI
and an authenticated account. Reviews start only when you invoke the command.

Links and the icon are bundled in the mod's README.md and `.claude-plugin/icon.png`.

## Validation recorded

- 2026-10-07 candidate refinement: remains a standalone mod with no bundled skills,
  agents, or autofix workflow. One review command with a `results` action, live progress, conversation
  findings, and a draft-only handoff to Claude form the v0.1 scope.
- The band, card, and toast share outcome wording. The CLI's known no-fresh-analysis
  completion notice now yields “Review skipped”; partial failures keep received
  findings visible without claiming completion. Diagnostics expand on demand.
- `--fresh` is opt-in and preserves the selected scope. Its help was verified with
  the installed official CodeRabbit CLI 0.8.2. Real Claude Code 2.1.289 headless
  execution with an explicitly synthetic offline CLI verified argument forwarding
  and no-fresh outcome handling without contacting a review service.
- Claude Code 2.1.289: `claude plugin validate mods/coderabbit --strict` passed.
- Current Desktop embedded engine 2.1.289: strict validation passed.
- Claude Code 2.1.289: `claude plugin test mods/coderabbit` passed, 89 tests.
- A real non-interactive Claude 2.1.289 session loaded the module and ran
  `/coderabbit-review --help` successfully.
- CodeRabbit CLI 0.8.2 `review --help` exposes every review option used here.
- Claude Desktop with embedded engine 2.1.286: an offline 12-second process
  fixture verified the branded running band, immediate command return, a second
  command while the review ran, an editable draft preserved through completion,
  the updated finding card, and the completion toast. The fixture was explicitly
  labeled synthetic; no review service was called. The official CLI path was
  restored afterward. Desktop needed configuration under the bare plugin name
  in user settings because it loaded the local plugin as a directory.
- The streaming update passed strict validation in terminal 2.1.289 and Desktop
  engine 2.1.286. A labeled offline Desktop fixture showed live phase changes in
  one row, then one finding, the completion toast, and expandable scope/severity/
  reviewed-file details. No review service was called; the official CLI path was
  restored afterward.
- Completion now stores a model-only result note without submitting a prompt or
  starting an assistant turn. The card, toast, and status band report the outcome.
  Tests cover context storage, denial, errors, and session reset, with no prompt
  submission even when storing the result succeeds. The obsolete wake-up and
  submitted-message rendering paths were removed.
- Tests use synthetic process responses. An authenticated end-to-end review
  against a development service has **not** been exercised. Do not describe
  the test suite as proof of service authentication or review quality.

## Live portal validation

The candidate subfolder passed all seven source checks on 2026-10-04 and was
recognized as one mod, with all six listing links populated. The directory
correctly limited installation to Claude Code. Local CLI execution, dynamic
executable selection, and local-read/outbound-data capability require human
policy review. The publisher name also requires ownership review against the
existing CodeRabbit listing. These are review holds, not a technical validation
failure or an approval.

The portal's compliance form still requires a declaration that no code executes
outside declared MCP servers, including for a package it recognizes as a mod.
This package cannot truthfully make that declaration. It remains unsubmitted.

## Data-handling review

The CLI sends selected code and repository context to CodeRabbit. Findings enter
the Claude conversation, and the CLI can save local review state. A background
completion saves model context without queuing a Claude turn. The mod does
not read credentials or persist its own review files. Personal data may be
present in selected code or metadata. The README discloses this path and links to
CodeRabbit's Privacy Policy.

A service owner must confirm the portal's personal-data and retention selections
against the applicable account settings and current policy. Do not claim “not
retained” solely because the mod itself writes no files.

## Submission gates

1. Merge the reviewed source before selecting `main` for a release submission.
2. Validate this exact subfolder in the live directory portal; its rules can
   differ from the CLI validator, particularly for executable mods.
3. Confirm that the portal accepts the declared local CLI execution. A declaration
   that no code executes outside MCP servers does not describe this package:
   it uses `$.process.spawn` and declares no MCP server. Resolve any such conflicting
   attestation with Anthropic before submitting; never tick an inaccurate claim.
4. An authorized publisher must review data-handling answers and accept directory
   terms. Local validation is not submission, approval, or publication.

Official references:

- [Create a mod](https://code.claude.com/docs/en/plugins/mods/create)
- [Mods API](https://code.claude.com/docs/en/plugins/mods/api)
- [Test a mod](https://code.claude.com/docs/en/plugins/mods/test)
- [Publish a plugin](https://code.claude.com/docs/en/plugins/publish)
