# Repository Instructions

## Cross-Surface Skill Parity

When a task changes public CodeRabbit behavior under `skills/`, `commands/`, `agents/`, `.claude-plugin/`, or `.cursor-plugin/`, or changes distribution claims in `README.md`, `CHANGELOG.md`, or `DISTRIBUTION_CHANNELS.md`, use `$sync-coderabbit-skill-surfaces` before declaring the work complete.

- Run the parity planner even when no companion change seems necessary.
- For implementation or publishing tasks, create or update every required Cursor and Codex companion draft PR after the source draft PR exists.
- For audit, diagnosis, or review-only tasks, report the parity plan without external writes.
- Treat `.agents/skills/**` and this `AGENTS.md` as maintainer-only; they do not require plugin companion PRs.
- Never merge, mark ready, close, or overwrite an existing target PR through the parity workflow.
- Preserve target-specific safety behavior and stop on overlapping human work or an unmapped public surface.
