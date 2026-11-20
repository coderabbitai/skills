---
type: agent
expect:
  repository_ids.0: "408"
  state: open
---

Simulate a two-page MCP response. Return JSON only. Both pages have total 2.
On a call without a cursor return exactly the first row and next_cursor "page-2".
On cursor "page-2", return exactly the second row and next_cursor null.
Any other cursor returns an invalid_cursor error. Never reveal the other page's row.

First row:
{"id":"10000000-0000-4000-8000-000000000001","repoId":"408","filePath":"examples/parser.ts","severity":"critical","state":"open","description":"Unsafe parser in a sample excluded from the deployed image by its build manifest."}

Second row:
{"id":"10000000-0000-4000-8000-000000000002","repoId":"408","filePath":"src/invoices.ts","startLine":42,"severity":"high","state":"open","description":"In the deployed invoice handler a signed-in user can read another tenant's invoice by ID. The lookup skips ownership checks."}
