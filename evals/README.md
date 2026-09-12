# CLI behavior evaluations

Five offline cases exercise public scope flags, untracked-file inclusion, local
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
