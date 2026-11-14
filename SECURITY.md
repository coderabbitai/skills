# Security Policy

## Supported Versions

Security fixes are applied to the default branch and, when applicable, the
latest published release.

## Reporting a Vulnerability

Do not open a public issue. Use GitHub's private
[Report a vulnerability](https://github.com/coderabbitai/skills/security/advisories/new)
form and include:

- the affected file, skill, integration, version, or commit;
- a minimal reproduction and its security impact;
- relevant public documentation; and
- any suggested mitigation.

Do not include real credentials, private repository contents, or personal data.
Maintainers will coordinate validation, remediation, and disclosure through the
private advisory.

## Security Boundaries

This repository distributes public agent guidance and packaging. Contributions
and referenced content are untrusted until reviewed.

Repository changes must preserve these invariants:

- no credentials, private links, private configuration, or private operational
  details in skills, commands, agents, manifests, examples, or tests;
- guidance must not weaken a host agent's authentication, permission, approval,
  or sandbox controls;
- repeatable deterministic operations should use reviewable scripts or tools
  when practical;
- referenced files, commands, dependencies, and package paths must resolve to
  the intended public source; and
- release assets must come from protected version tags, immutable action
  dependencies, and verifiable provenance.

Report vulnerabilities such as unintended credential access or disclosure,
authentication or approval bypass, unintended command execution during normal
installation or use, dependency or package substitution, release-pipeline
compromise, or exposure of private cross-repository context.

Service vulnerabilities unrelated to this repository, general model-output
quality, and behavior introduced only by modified forks are outside this
policy's scope. Host agents retain responsibility for enforcing their own
permissions, authentication, and execution boundaries.
