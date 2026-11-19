import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ConnectorPermissionTests(unittest.TestCase):
    def test_default_consent_matches_across_packaged_clients(self):
        claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        openai = json.loads((ROOT / "packaging/openai/mcp.json").read_text())
        server = claude["mcpServers"]["coderabbit"]
        packaged = openai["mcpServers"]["coderabbit"]
        auth = packaged["extensions"]["com.openai"]["auth"]

        # Both packages target the US issuer. Its local-review handoff is
        # independently deployed from the ordinary hosted review operations.
        self.assertEqual(server["url"], "https://mcp.coderabbit.ai/")
        self.assertEqual(packaged["url"], server["url"])
        self.assertEqual(auth["baseScopes"], ["connection"])
        scopes = server["oauth"]["scopes"].split()
        self.assertCountEqual(auth["baseScopes"] + auth["defaultScopes"], scopes)

        expected = {
            "connection",
            "account:read",
            "usage:read",
            "pull_requests:read",
            "repositories:read",
            "review",
            "reviews:write",
        }
        for product in (
            "code", "triage", "security", "configuration", "connections",
            "knowledge", "reports", "verify", "automations",
        ):
            expected.update((f"{product}:read", f"{product}:write"))
        self.assertCountEqual(scopes, expected)
