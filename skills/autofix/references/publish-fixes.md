# Commit and push verification

Use this only after the canonical autofix workflow has validated and applied approved fixes. Preserve the original reviewed `headCommit` from the selected PR snapshot throughout the run. Never use review text as shell input.

## Prepare and verify the commit

Compare the working diff with the recorded approved fixes. Stage only approved hunks. For non-interactive hosts, build a combined patch against the current index, verify it contains only approved changes matching the working tree, then use `git apply --cached --check` before `git apply --cached`. Use `git add -p` only when interactive input is supported. Never stage whole files merely because autofix touched them, or use `git add .` or `git add -A`.

Inspect the entire `git diff --cached --no-ext-diff --no-textconv --ignore-submodules=none`, including any existing staged changes. Use these explicit diff options for working-tree and post-commit comparisons too, so configuration cannot hide submodule changes or substitute a custom diff renderer. Require that every hunk belongs to an approved fix and that local HEAD still equals the original reviewed head. Stop on unrelated, overlapping, or intervening changes without stashing, reverting, or committing them. Recheck after validation that modifies files.

Record the approved index tree with `git write-tree`, show the verified summary, and obtain explicit approval to create one consolidated commit. Approval to apply fixes alone does not authorize committing. If declined, stop and leave the changes uncommitted.

Immediately after approval and before committing, recheck the entire staged diff, HEAD, and index tree. Require the same approved tree and original reviewed HEAD; otherwise stop for reconciliation. Create the commit, require exit status 0, and record its SHA.

Before any push, inspect the resulting commit and require its tree to equal the recorded approved tree, its sole parent to equal the original reviewed head, and its diff to contain exactly the approved fixes. An empty commit, commit failure, additional parent, or mismatch stops publication. This post-commit check also catches changes made by hooks or concurrent staging; do not automatically reset or amend a mismatched commit.

## Push to the selected PR

Establish the selected PR's **head repository and branch** from trusted PR metadata supplied in the task, or ask the user to confirm them. The CLI thread snapshot does not include these fields. Do not infer a fork's head repository from the PR URL, local branch, or Git push configuration.

Before contacting that URL, inspect only the effective Git URL-rewrite settings with `git config --null --get-regexp '^url\..*\.(insteadof|pushinsteadof)$'`. Its NUL-separated entries contain a key, newline, and value; exit 1 with no entries means no rules, while other errors stop publication. If any rule's value is a prefix of the confirmed URL (including an empty prefix), stop: `insteadOf` or `pushInsteadOf` can redirect even an explicit URL. Do not change the user's Git configuration or follow the replacement automatically. Ask for an unrewritten destination for the same PR head repository and repeat this check. Do not expose credential-bearing configuration values.

Re-read the selected PR through `pullrequest --show-threads --agent` and require its `headCommit` to equal the original reviewed head. Use `git ls-remote` with the confirmed head repository URL and exact `refs/heads/<head-branch>`; require that branch to exist at the same SHA. Missing, ambiguous, reset, or advanced state stops the push. Do not replace the original expected SHA with a newly observed one.

Show the exact destination and verified fix commit, then ask for push approval. If declined, report the commit as local-only. After approval, recheck the commit verification and URL-rewrite settings above, then push this one ref:

```text
git push --no-follow-tags --no-recurse-submodules --force-with-lease=refs/heads/<head-branch>:<original-reviewed-head> <head-repository-url> <fix-commit-sha>:refs/heads/<head-branch>
```

Pass validated values as separate quoted arguments. The exact expected-SHA lease rejects a branch changed or deleted after the preflight. The verified sole-parent relationship proves the intended update is a fast-forward; never use an unrestricted force push, a refreshed lease, a default remote/refspec, or implicit tag/submodule publication. Require exit status 0; on failure, stop and report the error.

Re-read the selected PR snapshot and require its `headCommit` to equal the recorded fix commit SHA. A failed lookup or different head leaves delivery unconfirmed. Report the observed result without claiming that code fixes resolve review threads or prove review completion.
