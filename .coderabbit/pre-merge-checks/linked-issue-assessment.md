---
id: linked-issue-assessment
name: Linked issue assessment
mode: error
report: coderabbit
---
If there are no linked issues, pass this check. Otherwise, compare the diff
with the linked issues. Pass if it addresses the linked requirements without
material out-of-scope changes. Fail if the diff leaves a linked requirement
unaddressed or contains a material out-of-scope change. Report an inconclusive
result if linked issue context is unavailable.
