---
id: agent-guidance-structure
name: Agent guidance structure
mode: error
report: coderabbit
enabled: true
---
Pass when the pull request does not change skills, agent guidance,
native commands, or their manifests. Otherwise require all of these:
- SKILL.md files keep activation, routing, domain context, and workflow
  framing concise.
- Detailed material is loaded through focused references when needed,
  and repeatable deterministic operations use scripts or tools when
  practical.
- Referenced files, scripts, tools, commands, and options exist and
  agree with the repository and current public documentation.
- Changes follow the Agent Skills specification, the AGENTS.md open
  format, and current public guidance for each declared host agent.
- Native commands and agents that wrap a canonical skill, and their
  manifests, remain behaviorally aligned with that skill.
- A standalone mod with its own command and no bundled or delegated
  canonical skill follows its own documented contract. Require its
  parser, help, README, and tests to agree on defaults and scopes,
  and require differences from related skills to be explicit. Shared
  branding or use of the same CLI alone does not make it a skill wrapper.
