# Antigravity release and QA

Antigravity 1.3.0 adds hosted MCP to the existing `coderabbit` listing. It uses
the same local CLI workflows and remote endpoint as Claude 1.3.0 and the
OpenAI MCP 1.3.0 candidate. These are independently published channels;
matching source versions do not establish live marketplace parity.

The current source preserves the separate-sign-in workflow introduced in 1.3.0. MCP-authorized CLI
handoffs are deferred and are not a release requirement for this candidate.
Google's broader discovered OAuth grant, starter-prompt routing and unavailable
inline presentation tool remain explicit differences; this is workflow parity,
not identical host behavior or permissions.

## Package contract

- `plugin.json` at the repository root is Google's version source. Do not
  shadow it with `.antigravity-plugin/plugin.json`.
- `mcp_config.json` declares `https://mcp.coderabbit.ai/` using `serverUrl`.
  Antigravity discovers OAuth through the server's public metadata. The host
  manages consent, organization selection and credentials.
- `.antigravity-plugin/README.md` provides the Google-specific marketplace
  setup guide. Local App installation currently renders the root `README.md`
  as its overview, so its quickstart must cover Antigravity too; verify which
  overview Google's marketplace packager serves. The packager omits hidden
  skill directories. Keep the shared skills, including `coderabbit-secure`, under
  the default `skills/` directory so they also ship in Marketplace ZIPs.
- Local reviews use the separately authenticated CodeRabbit CLI. There is
  no automatic review hook, bundled CLI, or MCP-to-CLI credential transfer.
- `commands/` remains for Claude and Gemini. Native `agy plugin validate`
  reports its expected warning. With 1.5.11, installation reported conversion
  but exposed none of those commands as installed skills. Google setup uses
  `coderabbit-setup` explicitly; review uses `code-review`. Do not depend on
  command conversion or remove other hosts' commands to silence the warning.

Google's [plugin guide](https://antigravity.google/docs/build-plugins) and
[MCP guide](https://antigravity.google/docs/mcp) define this layout and OAuth
discovery. Do not copy Claude's `oauth.scopes` or OpenAI's auth extension into
Google's config: they are not documented Google scope controls.

### Public documentation verification

Rechecked on 2026-11-18 for the agent-guidance review:

| Contract | Public source and verification |
| --- | --- |
| Skill discovery | Google's [manifest field reference](https://antigravity.google/docs/build-plugins#field-reference) specifies the default `skills/` directory. The native validator discovers all five shared skills there. |
| Server identity | Google's [MCP plugin layout](https://antigravity.google/docs/build-plugins#mcp-servers) namespaces a server with its plugin name. Both names here are `coderabbit`, producing `coderabbit_coderabbit`. |
| Native OAuth | Google's [OAuth guide](https://antigravity.google/docs/mcp#oauth) documents automatic CIMD/DCR discovery with PKCE for a remote `serverUrl`. |
| App sign-in | Google's [authentication steps](https://antigravity.google/docs/mcp#authenticate-a-server) use Customizations > Installed > MCP Servers. The plugin's Accounts tab and successful code entry were separately observed in the App smoke test. |
| CLI management | Google's [slash-command reference](https://antigravity.google/docs/cli/reference/#core-slash-commands) lists `/mcp` for server management and `/plugin` for plugin management. |

Shared skills do not assume that every host package has MCP. The checked-in
Claude manifest declares its remote server; the standalone Codex manifest only
references shared skills. The separately prepared OpenAI MCP candidate is a
distinct package, not evidence of MCP in the standalone Codex distribution.

## Release procedure

1. Use `python3 .github/release.py bump X.Y.Z` for changes to shared skills,
   agents, commands, assets, MCP config or overview. All active packages now
   share the source version; see the [version policy](versioning.md).
   Antigravity publication remains independent of GitHub `v*` archive releases.
2. Fetch canonical main with
   `git fetch https://github.com/coderabbitai/skills.git main`, then immediately run
   `python3 .github/check_antigravity.py --base FETCH_HEAD` and
   `python3 -m unittest discover -s .github/tests -v` before merging. The package
   check requires `agy` and permits only the known commands warning. CI pins
   the official CLI to 1.5.11 with its SHA-512 checksum. Update the pin from
   Google's official updater manifest when qualifying a newer validator.
   Manual CI runs require an explicit comparison base: use `origin/main` on a
   feature branch or the previous release commit when validating a release on
   `main`. Runs with no base explicitly report that version validation was skipped.
   Run on an idle checkout: concurrent editor writes, commits and resets are
   unsupported. Observed state changes require a rerun; the checker does not
   provide transactional isolation from other local processes. CI uses an
   isolated checkout for this reason.
3. Test installation and connection in a dedicated Antigravity test profile.
   Run `agy plugin install /absolute/path/to/skills`, then `agy plugin list --json`.
   Verify version, all five skills, agents and the single
   `coderabbit_coderabbit` MCP server. Inspect the marketplace overview too.
4. Merge the reviewed change into `coderabbitai/skills` **main**. Google
   confirmed on 2026-11-17 that its weekly crawler reads that branch and
   uploads changed plugin versions to the Marketplace. A GitHub tag alone
   does not deliver this update; no new marketplace submission is required
   for the existing listing. The exact crawl day is not specified.
5. When the MCP/OAuth PR lands, notify the Google partner contact with the
   merged PR and version so their QA team can test discovery and consent.
   Sending that message is a separate release action.
6. Observe the Marketplace version and rerun the smoke checks on a fresh
   marketplace install. Record results here before marking the channel live.

## QA cases

| Check | Expected result |
| --- | --- |
| Fresh install | Correct branding, three starter prompts, Google overview, five skills and two agents; exactly one hosted MCP server. |
| OAuth | Native consent succeeds; cancellation stays disconnected; reconnect works. No secrets or codes are pasted into chat. |
| Account and organization | `connection_status` or `get_me` reports the selected organization. A browser success page is insufficient. |
| Scope parity | Inspect actual consent and granted capabilities. The Claude source manifest requests repository and Security access, plus automation and knowledge writes for schedule and learning changes. Google relies on discovery. Check a scoped findings read after sign-in. |
| Remote tools | Usage and an accessible PR can be read; inaccessible repositories remain inaccessible. |
| Local review | In an approved sample Git repo, review the requested changes through the installed CLI, preserving scope and terminal completion status. MCP login alone must not count as CLI login. |
| Findings display | Show the original completed CLI findings as text, preserving severity and coverage without rerunning the review. |
| Autofix | Read current unresolved threads; independently validate proposed fixes; edit only within the user's approval. |
| Configuration | Validate a sample configuration using config protocol v2 without login; a save needs approval. |
| No local execution | Remote tools remain available; local review is reported unavailable. |

## Evidence for 1.3.0

Prepared on 2026-11-18; not yet merged or verified in the Marketplace.
Local native validation with `agy` 1.5.11 discovers four skills, two agents
and one MCP server, with only the documented multi-host commands warning.
An allowlisted temporary copy was installed through `agy plugin install`;
`agy plugin list --json` confirmed version 1.3.0, all four skills (including
`coderabbit-setup`), both agents and the hosted server. Native validation of
the installed copy also passed. That initial validation-only installation was
removed, preserving the profile's pre-existing plugins. The candidate was then
reinstalled for the live App tests below. The 31 package, release-guard and diagnostics regression
tests and skill frontmatter validation passed.

Public discovery metadata was read on 2026-11-18:

- Protected resource matches `https://mcp.coderabbit.ai/` and points to the
  same authorization server.
- Authorization metadata advertises CIMD, DCR (`/register`), authorization
  code and refresh token grants, PKCE `S256`, and public-client auth (`none`).
- The advertised scopes include the five Claude/OpenAI scopes and broader
  product scopes. This is discovery evidence, not proof of Google's actual
  requested or granted scopes.

### App smoke test observations

The Antigravity App displayed version 1.3.0, all four skills, both agents,
three starter prompts, and the hosted connection. The setup skill correctly
reported missing OAuth and surfaced a native sign-in card without running a
review or using the installed mock plugin.

The local detail page rendered root `README.md`, not the Google-specific
overview. The root quickstart was corrected to include Antigravity and remove
the stale claim that only Claude declares MCP. The connection starter prompt
also inserted a `coderabbit-config` mention in the composer; manual invocation
of `coderabbit-setup` worked. This appears to be host prompt routing and needs
Google QA; it is not evidence that the configuration skill handles login.

The real consent screen requested broader read/write scopes than the five
Claude/OpenAI scopes, including code, settings, security, connections and
automations. Browser sign-in used Antigravity's CIMD and PKCE. Do not describe
this as least-privilege scope parity. Approval and authenticated tool discovery
are separate from displaying the consent page.

The first manual code exchange failed with `invalid_grant` / “Invalid
authorization code.” A fresh native sign-in completed successfully and the
App displayed the account as connected. The cause of the first failure was
not established. Do not reuse a rejected
code or claim that the plugin manifest caused this exchange error.

Authenticated `connection_status` and `get_me` calls succeeded through the
real hosted server and identified the selected organization. Organization
membership enumeration was reported as unsupported, rather than empty.

A separate CLI authentication check succeeded using the existing CLI login.
One review of an uncommitted change in a disposable synthetic Git repository
completed with exit code 0 and `review_completed`. CodeRabbit found the
planted percentage-calculation bug as one major finding. The agent preserved
the requested scope and did not edit, commit or push files, start an MCP
review, use mocks, or request paid continuation. With no Git remote, the CLI
reported using its free allowance rather than an organization plan.

The real hosted server did not expose `present_local_review`. Antigravity
displayed the original finding as text without rerunning the review. Inline
review presentation remains unavailable in this tested connection.

The real hosted `get_usage` call succeeded. Some credit fields were forbidden
and included-review counts were unsupported; the agent reported those as
unavailable rather than zero. `get_pull_request` retrieved
`coderabbitai/skills#97`, its successful CodeRabbit check and both resolved
CodeRabbit threads, with complete thread coverage. No review or comment was
created. The response still reported unknown CodeRabbit completion metadata;
the agent preserved that distinction instead of inferring merge readiness.
Separate review-summary/detail tools were not exercised.

The final isolated PR package was installed and validated again. A fresh real
`connection_status` call succeeded with the same organization after replacement,
without another sign-in. The live-test installation remains installed at 1.3.0.
Pending: marketplace
overview/prompt routing, Google QA and the crawler's published version. These
checks do not establish marketplace publication or full QA-matrix coverage.

### MCP-authorized CLI handoff follow-up

The live server exposes `start_code_review` (one-review authorization and
short-lived handoff) and `get_code_review` (saved-result retrieval). This is a
different route from the separately authenticated CLI smoke test above. The
development handoff contract keeps OAuth in the host and sends a scoped
handoff to a compatible CLI through stdin; it does not copy the host's OAuth
token into the CLI login store.

The installed Antigravity package has no `cli.json`, pinned launcher or hook.
No handoff review was reserved or launched. This future integration is deferred;
it would require a qualified host launcher and a completed same-ID CLI/MCP
result comparison. Current Claude 1.3.0 and the OpenAI 1.3.0 candidate also use
separately authenticated local CLI reviews.
