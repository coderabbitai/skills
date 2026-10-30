# CLI behavior evaluations

Seven offline cases exercise public scope flags, default and uncommitted untracked-file inclusion, local
versus PR prompt retrieval, EU browser authentication, incomplete/skipped
review output, and missing-CLI handling outside Antigravity. No shell, writes, network tools, or production reviews are granted.

Run the command-grader regression tests without credentials or model calls:

```sh
python3 -B -m unittest discover -s evals -p 'test_*.py'
```

These tests match command examples as text; they do not execute them.

With Claude Code 2.1.269+ and an authenticated account, run from the plugin root:

```sh
claude plugin eval . --tag cli-parity --runs 1 --ablation with-without --no-publish --max-cost-usd 10 --keep-temp
```

Pin `--model` for comparisons. Positive skill activation is diagnostic and does
not contribute to the outcome score. Deterministic graders check specific command
contracts. The missing-CLI semantic grader contributes to both ablation scores;
the remaining advisory LLM graders are with-only and excluded from those scores.
Inspect the actual answers and retained transcripts: regex checks and LLM
judges do not establish complete semantic correctness. One run per arm is a smoke
evaluation, not a reliable effect-size estimate. Results stay under ignored
`evals/results/`; do not commit account metadata or private source provenance.

See the [official evaluator documentation](https://code.claude.com/docs/en/plugin-evals).
