# CLI behavior evaluations

Six offline cases exercise public scope flags, default and uncommitted untracked-file inclusion, local
versus PR prompt retrieval, EU browser authentication, and incomplete/skipped
review output. No shell, writes, network tools, or production reviews are granted.

With Claude Code 2.1.269+ and an authenticated account, run from the plugin root:

```sh
claude plugin eval . --tag cli-parity --runs 1 --ablation with-without --no-publish --max-cost-usd 10 --keep-temp
```

Pin `--model` for comparisons. Positive skill activation is diagnostic and does
not contribute to the outcome score. Deterministic graders check specific command
contracts; advisory LLM graders are with-only and excluded from the ablation
score. Inspect the actual answers and retained transcripts: regex checks and LLM
judges do not establish complete semantic correctness. One run per arm is a smoke
evaluation, not a reliable effect-size estimate. Results stay under ignored
`evals/results/`; do not commit account metadata or private source provenance.

See the [official evaluator documentation](https://code.claude.com/docs/en/plugin-evals).

## Compare published skills, a candidate, and no skills

`prepare_comparison.py` prepares eleven shared cases: the original six
(committed scope, untracked scope, stream outcomes, thread selection, rejected
guidance, and an unrelated control), plus remote review syntax and boundaries,
completion/coverage outcomes, credit consent, and a second untrusted snapshot.
It copies only the two canonical skills and their references into clean plugin
snapshots. It does not change your installed plugin or launch paid runs.

Use `--suite extended` to include the eight `fresh-*` development cases and four
`validation-*` cases added in the next iteration (23 cases total). The validation
cases were first evaluated after freezing that candidate; once used for tuning,
they are no longer an untouched set. Preserve their hashes and author new cases
before claiming another fresh validation. Native runs evaluate all selected
cases; Lightsage requests are split into batches of at most 20 prompts, with
case mappings in `manifest.json`.

```sh
python3 evals/prepare_comparison.py \
  --baseline 3e8763d24d543b48615b82535d02288de3ddae40 \
  --candidate HEAD --agent claude-code:claude-opus-4-6 --output /tmp/skills-comparison

claude plugin eval /tmp/skills-comparison/published \
  --runs 3 --ablation with-without --model claude-opus-4-6 \
  --judge-model claude-haiku-4-5 --max-cost-usd 20 --concurrency 2 \
  --no-publish --no-scaffold --keep-temp --trust-plugin \
  --output-dir /tmp/skills-comparison/results-published

claude plugin eval /tmp/skills-comparison/candidate \
  --runs 3 --ablation none --model claude-opus-4-6 \
  --judge-model claude-haiku-4-5 --max-cost-usd 10 --concurrency 2 \
  --no-publish --no-scaffold --keep-temp --trust-plugin \
  --output-dir /tmp/skills-comparison/results-candidate
```

Generated snapshots use identical outcome graders; positive activation checks and
with-only advisory LLM graders are removed. Required semantic graders remain
in both arms, including cases that also have regex checks. Keep the negative control's zero-Skill
check. Count a case attempt as passing only when all its outcome graders pass;
do not report a weighted average as a full pass. Inspect answers and tool calls
alongside scores: the regex checks cover specific contracts, not every assertion.
The sanitization case measures repetition of synthetic payload details, not actual
credential access. Three repeats are a pilot, not a reliable general effect size.
Inspect tool arguments and intermediate commentary too: a clean final answer can
still copy rejected raw reviewer instructions into a Skill invocation. The native
regex grader alone did not catch that in one iteration. Treat the received
findings, completion evidence, requested refs and local-only files as independent
requirements; a generally cautious answer can still contradict one of them.

### Lightsage

The three `lightsage-*.json` files are ready for the connected Lightsage MCP's
`evals-run` operation. Each defaults to eleven attempts; `--runs N` changes that
fanout. Use an agent included in your plan; no account or plan changes are needed.
The candidate SHA must be publicly fetchable before launching. Only public skill
source and synthetic fixtures are uploaded; no local credentials are passed.

Skill installation pins the skill commit. For the public fixture, create a saved
Lightsage repository with `ref` set to
`570fcdb7a3f17e1c1a6e7f372ee2f3df4c28c8d5`, verify that saved ref before launch,
and pass its ID to `prepare_comparison.py --repository <repository-id>`, or use
a saved configuration referencing it. The default direct URL does not enforce
the fixture pin. Do not run a fixture `git checkout` in `clis`: that installation
stage can precede workspace creation and made all attempts fail before agent output.

Single-line `clis`
installation commands copy skills to both `/home/daytona/.claude/skills` and the
repository's `.claude/skills`: the observed runner starts in `/home/daytona`.
`setup_commands` was accepted but did not run in the tested direct-run path.
Verify installed hashes against `manifest.json` and inspect Skill calls before
accepting scores. Recheck these runner assumptions when the service changes.

Save each returned eval ID and a configuration pointing to the pinned fixture
repository for later runs. Keep IDs, account metadata, outputs, and raw traces
outside version control. Separate infrastructure/installation failures from skill
quality. The API's estimated cost is not a dollar cost cap. Review the fanout and
account budget before launching; the native commands above have explicit caps.

Fetch `evals-trace` pages until exhausted. The tested endpoint capped pages at 500
events and could return `has_more=false` on a full page; continue with
`next_after_id` when a page is full. Keep tool calls and assistant text. Run the
same deterministic checks and manually review semantic criteria; Lightsage's
LLM judge passed known-invalid commands in the pilot, so its score alone is not
acceptance evidence. Report different model/runner results separately.

The CLI contract check uses [the official reference](https://docs.coderabbit.ai/cli/reference).
Remote review and failed/incomplete completion handling require CLI 0.7.7+.
Record the model, source SHAs, case hashes, actual command help/version, and docs
retrieval date with each experiment. To measure one iteration, set `--baseline`
to the previous candidate commit; label that arm as the previous iteration rather
than published main. Keep older six-case results separate from the expanded suite.
