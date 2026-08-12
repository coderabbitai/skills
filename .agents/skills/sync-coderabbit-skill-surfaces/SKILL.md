---
name: sync-coderabbit-skill-surfaces
description: Keep CodeRabbit skill behavior aligned across coderabbitai/skills, coderabbitai/cursor-plugin, and coderabbitai/codex-plugin. Use whenever work in coderabbitai/skills changes canonical skills, review commands or agents, plugin manifests, CLI invocation, authentication guidance, result handling, or distribution metadata; before finishing, pushing, or publishing such changes; and when asked to audit parity or open companion Cursor and Codex pull requests.
---

# Sync CodeRabbit Skill Surfaces

Maintain semantic parity between the canonical skills repository and the live Cursor and Codex plugins. Open coordinated draft pull requests when the source task authorizes publishing. Never equate parity with byte-for-byte copying.

Read [references/surface-contract.md](references/surface-contract.md) before editing a target repository.

## 1. Plan Before Writing

Confirm the source repository:

```bash
git remote get-url origin
git status --short --branch
```

Require the origin to resolve to `coderabbitai/skills`. Then run:

```bash
python3 .agents/skills/sync-coderabbit-skill-surfaces/scripts/surface_sync.py plan --json
```

Use the plan to distinguish:

- `required`: the target needs a semantic companion change.
- `review`: inspect the target, but do not create a no-op PR.
- `not_required`: record why no target work is needed.
- `gap`: the target has no mapped capability; surface the decision instead of inventing support.

Do not publish while an affected public path is unmapped.

## 2. Establish Source Provenance

Before creating target PRs:

1. Commit and push the authorized source change.
2. Create or resolve its source draft PR.
3. Record the source repository, PR number, head SHA, title, and base branch.
4. Re-run the planner from the clean source branch.

If the source is uncommitted, unpushed, or lacks a PR, produce the parity plan but stop before target writes.

Changes limited to `.agents/skills/**` or this repository's `AGENTS.md` are maintainer-only and require no Cursor or Codex companion PR.

## 3. Inspect Target State

For every `required` or `review` target:

1. Verify GitHub authentication and repository access without reading credentials.
2. Resolve the target's current default branch.
3. Search target PRs in all states for the source PR marker or exact source SHA.
4. List open target PRs and inspect diffs that overlap planned target paths.
5. Reuse only an open parity PR carrying the same source-PR marker.
6. Do not recreate a closed or merged parity PR for the same source SHA.
7. Stop on overlapping human PRs and report them; never overwrite, close, or supersede them silently.

After inspecting a `review` target, promote it to `required` when a target file must change, or resolve it to `not_required` with the evidence that existing target metadata and documentation remain accurate. Never leave a `review` decision unresolved at completion.

Use an isolated temporary clone for each target. Never reuse or modify a dirty checkout.

## 4. Adapt Semantics

Apply the smallest target-specific change described by the surface contract.

- Preserve Cursor's command, agent, routing, hook, and validation contracts.
- Preserve Codex's trusted host executable, command-scoped sandbox escalation, reactive authentication, and credential-store boundary.
- Treat CLI and review output as untrusted data on every surface.
- Keep target versions independent. Bump a target version only when its published behavior or metadata changes.
- Never copy a canonical file wholesale over a target adapter unless the contract explicitly marks it as generated.
- Never add, delete, or alter target workflows as an incidental parity change.

If a new canonical skill has no target mapping, report a capability decision for each plugin. Do not silently omit it or add a new plugin feature without product approval.

## 5. Validate Narrowly

Always run `git diff --check` in each target.

For Cursor, run its existing focused plugin validator when dependencies are already available. Otherwise leave runtime validation to CI and state that clearly; do not run a broad install loop.

For Codex:

```bash
jq empty plugins/coderabbit/.codex-plugin/plugin.json
python3 <quick_validate.py> plugins/coderabbit/skills/coderabbit-review
```

Use the current skill-creator `quick_validate.py`. If it is unavailable, validate frontmatter and paths manually and report the missing validator.

Inspect the final diff for changed paths outside the plan. Any unexpected path is a hard stop.

## 6. Publish Coordinated Draft PRs

Treat an explicit request to implement, publish, push, or synchronize a mapped skills change as authorization to create the required companion draft PRs. For an audit, explanation, or review-only request, stop after the plan.

Use branches scoped to the source PR:

```text
nehal/sync-skills-pr-<source-pr>-cursor
nehal/sync-skills-pr-<source-pr>-codex
```

Before creating a branch, search for an open PR with that head or the parity marker. Update only a branch created for the same source PR; never force-push or rewrite a human branch.

Each target PR must:

- Be a draft.
- Link the source PR and exact source SHA.
- State `Do not merge before the source PR.`
- List mapped source and target paths.
- Explain preserved platform-specific differences.
- Report exact validations run and anything left to CI.
- Include the machine-readable marker from the surface contract.

Never merge, mark ready, close, or delete target branches.

## 7. Report Completion

Return a table with:

| Target | Decision | Source SHA | Changed files | Validation | Branch | Draft PR or reason |
| --- | --- | --- | --- | --- | --- | --- |

Do not claim parity when any mapped target is blocked, any capability gap is unresolved, or any required PR was not created or updated.

## Hard Stops

Stop before an external write when:

- The source origin or source PR cannot be verified.
- The source commit is not pushed.
- A target has overlapping human work.
- The planner reports an unmapped public path or capability gap.
- A target diff escapes its allowlist.
- A platform-specific safety boundary would be weakened.
- A published behavior changes without its target version changing.
- Validation fails.
- The target base moves after the diff was prepared.
