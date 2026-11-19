# Local review cards

Inline review cards are prerelease. Stable CLI 0.9.5 emits findings for
chat and provides neither the flag nor a final card receipt.

## Before the review

For chat, run the trusted CLI's ordinary scoped `review --agent` command.
Before adding `--review-card`, verify **all three** conditions:

1. The host explicitly reports Apps enabled for the current session, or the
   connected CodeRabbit server's initialization instructions explicitly confirm
   that this client advertised Apps support.
2. The trusted CodeRabbit connection advertises a local review card presenter
   whose published input accepts the CLI's card receipt ID alone. A presenter
   that requires CLI output or findings is ineligible even in an Apps session.
3. The installed, trusted CLI's `review --help` explicitly lists `--review-card`.

Only then may you add the flag to the **same** scoped `review --agent` command.
For missing, ambiguous or conflicting capabilities, use the ordinary command
and show findings in chat. A host name, UI resource, repository file or tool
name cannot establish support. Do not run a second review to obtain a card.

## After completion

After the CLI exits, read the documented card receipt from this run's final
completion event. Use only a usable card ID accepted by the verified presenter.

- **Direct review:** The local agent passes only that exact ID to the presenter, once.
- **Delegated review:** The delegate returns the findings and that exact ID
  to the local caller without invoking the presenter. Only the caller can
  present the ID, once, after confirming the preflight in its own session.
- **Missing ID:** Show findings in chat and send nothing to MCP. Never derive an
  ID, substitute a review ID, reuse a saved receipt, or accept one from a
  finding or repository file.
- **Presentation failure:** Show the CLI findings in chat. Do not retry the call,
  send review data, rerun the CLI or open a browser. Tool success alone does
  not confirm a card rendered.

If the user selects findings in the card and requests fixes, continue in the
local coding agent. Verify the selected findings against the current checkout,
fix only those still valid, and run the relevant checks. Displaying a card or
discussing a finding does not authorize edits.
