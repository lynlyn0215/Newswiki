from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from service.app.main import app


AUTH_VALUE = "dev-newswiki-key"


class RoutesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_requires_api_key(self) -> None:
        response = self.client.get("/v1/signals")

        self.assertEqual(response.status_code, 401)

    def test_health_with_api_key(self) -> None:
        response = self.client.get("/v1/health", headers={"x-api-key": AUTH_VALUE})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["ok"])

    def test_latest_signals(self) -> None:
        response = self.client.get("/v1/signals?topic=mcp", headers={"x-api-key": AUTH_VALUE})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["signals"]), 1)
        self.assertEqual(data["signals"][0]["id"], "signal-demo-001")

    def test_search_knowledge(self) -> None:
        response = self.client.get(
            "/v1/knowledge/search",
            params={"query": "public-safe export"},
            headers={"x-api-key": AUTH_VALUE},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["knowledge"])

    def test_recommend_tools(self) -> None:
        response = self.client.post(
            "/v1/tools/recommend",
            json={"task": "build context pack", "limit": 3},
            headers={"x-api-key": AUTH_VALUE},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["tools"])

    def test_context_pack_endpoint(self) -> None:
        response = self.client.post(
            "/v1/context",
            json={"task": "design hosted MCP service", "topic": "mcp", "token_budget": 1000},
            headers={"x-api-key": AUTH_VALUE},
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["task"], "design hosted MCP service")
        self.assertTrue(data["signals"])
        self.assertTrue(data["sources"])

    def test_usage_records_events(self) -> None:
        self.client.get("/v1/signals", headers={"x-api-key": AUTH_VALUE})
        response = self.client.get("/v1/usage", headers={"x-api-key": AUTH_VALUE})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["events"])

    def test_invalid_public_export_returns_503(self) -> None:
        original_export_dir = os.environ.get("NEWSWIKI_PUBLIC_EXPORT_DIR")
        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp)
            (export_dir / "signals.json").write_text(
                json.dumps(
                    {
                        "signals": [
                            {
                                "id": "bad-signal",
                                "title": "Bad signal",
                                "summary": "This should never be served.",
                                "source_urls": ["https://example.com/bad"],
                                "topics": ["mcp"],
                                "updated_at": "2026-01-02T10:00:00Z",
                                "freshness": "daily",
                                "confidence": "medium",
                                "public_safe": True,
                                "private_notes": "do not expose",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            os.environ["NEWSWIKI_PUBLIC_EXPORT_DIR"] = str(export_dir)
            response = self.client.get("/v1/signals", headers={"x-api-key": AUTH_VALUE})

        if original_export_dir is None:
            os.environ.pop("NEWSWIKI_PUBLIC_EXPORT_DIR", None)
        else:
            os.environ["NEWSWIKI_PUBLIC_EXPORT_DIR"] = original_export_dir

        self.assertEqual(response.status_code, 503)
        self.assertFalse(response.json()["ok"])


if __name__ == "__main__":
    unittest.main()
