# CLI behavior evaluations

The seven `mcp-review-*` cases evaluate agent guidance and authorization decisions,
including a user-stated spending-cap condition, not a backend-enforced cap. Select
`--tag mcp-parity` to evaluate those cases; `--tag cli-parity` retains the
existing CLI runbook cases. The MCP cases are offline and grant no shell,
network, writes, or review execution. They do not test binary launch, artifact
integrity, CLI/MCP result parity, installation or live authentication. Inspect
retained transcripts; model graders are advisory.
Evaluate MCP cases against an assembled pilot with the templates from
`packaging/mcp`; the shared source skill continues to use the released CLI.

Six released-CLI cases exercise public scope flags, default and uncommitted untracked-file inclusion, local
versus PR prompt retrieval, EU browser authentication, and incomplete/skipped
review output. No shell, writes, network tools, or production reviews are granted.

With Claude Code 2.1.269+ and an authenticated account, run the released CLI cases from the source plugin root:

```sh
claude plugin eval . --tag cli-parity --runs 1 --ablation with-without --no-publish --max-cost-usd 10 --keep-temp
```

For the seven MCP cases, copy `evals/` into the assembled Claude pilot package,
then run from that package root so the evaluator uses its MCP skill templates:

```sh
claude plugin eval . --tag mcp-parity --runs 1 --ablation with-without --no-publish --max-cost-usd 10 --keep-temp
```

Pin `--model` for comparisons. Positive skill activation is diagnostic and does
not contribute to the outcome score. Deterministic graders check specific command
contracts; advisory LLM graders are with-only and excluded from the ablation
score. Inspect the actual answers and retained transcripts: regex checks and LLM
judges do not establish complete semantic correctness. One run per arm is a smoke
evaluation, not a reliable effect-size estimate. Results stay under ignored
`evals/results/`; do not commit account metadata or private source provenance.

See the [official evaluator documentation](https://code.claude.com/docs/en/plugin-evals).
