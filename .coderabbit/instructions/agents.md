---
id: agents
paths:
  - agents/**/*.md
enabled: true
---
Keep agent workflows behaviorally aligned with the corresponding canonical skill and commands.
Keep `autofix` read-only: it must not edit files, commit, push, create pull requests, or post comments.
Flag conflicting prerequisites, review scopes, or remediation guidance.
