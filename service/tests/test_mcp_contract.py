from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from service.app.mcp_server import HostedMCPService, dumps, make_app
from service.app.settings import Settings


ROOT = Path(__file__).resolve().parents[2]
AUTH_VALUE = "dev-newswiki-key"


class MCPContractTest(unittest.TestCase):
    def setUp(self) -> None:
        settings = Settings(public_export_dir=ROOT / "examples" / "public", api_keys=(AUTH_VALUE,))
        self.service = HostedMCPService(settings_factory=lambda: settings)

    def test_make_app_constructs_fastmcp_server(self) -> None:
        app = make_app()

        self.assertIsNotNone(app)

    def test_latest_signals_requires_api_key(self) -> None:
        result = self.service.latest_signals(api_key=None)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "invalid API key")

    def test_latest_signals_returns_public_items(self) -> None:
        result = self.service.latest_signals(api_key=AUTH_VALUE, topic="mcp", limit=5)

        self.assertTrue(result["ok"])
        self.assertEqual(result["signals"][0]["id"], "signal-demo-001")
        self.assertIn("source_urls", result["signals"][0])

    def test_search_news_handles_empty_results(self) -> None:
        result = self.service.search_news(api_key=AUTH_VALUE, query="definitely unmatched", limit=5)

        self.assertTrue(result["ok"])
        self.assertEqual(result["signals"], [])

    def test_search_knowledge_returns_public_safe_knowledge(self) -> None:
        result = self.service.search_knowledge(api_key=AUTH_VALUE, query="public-safe export")

        self.assertTrue(result["ok"])
        self.assertTrue(result["knowledge"])

    def test_recommend_agent_tools_returns_tools(self) -> None:
        result = self.service.recommend_agent_tools(api_key=AUTH_VALUE, task="build context pack")

        self.assertTrue(result["ok"])
        self.assertTrue(result["tools"])

    def test_get_topic_brief_returns_brief_shape(self) -> None:
        result = self.service.get_topic_brief(api_key=AUTH_VALUE, topic="mcp")

        self.assertTrue(result["ok"])
        self.assertEqual(result["topic"], "mcp")
        self.assertIn("briefs", result)

    def test_get_context_for_task_matches_context_pack_schema(self) -> None:
        result = self.service.get_context_for_task(
            api_key=AUTH_VALUE,
            task="design hosted MCP service",
            topic="mcp",
            token_budget=1000,
        )

        self.assertTrue(result["ok"])
        for key in [
            "task",
            "answer",
            "signals",
            "knowledge",
            "tools",
            "sources",
            "freshness",
            "confidence",
            "suggested_next_queries",
        ]:
            self.assertIn(key, result)

    def test_invalid_public_export_fails_closed(self) -> None:
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
                                "full_text": "private article body",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            settings = Settings(public_export_dir=export_dir, api_keys=(AUTH_VALUE,))
            service = HostedMCPService(settings_factory=lambda: settings)

            result = service.latest_signals(api_key=AUTH_VALUE)

        self.assertFalse(result["ok"])
        self.assertEqual(result["error"], "public export validation failed")

    def test_tool_result_serializes_as_json_string(self) -> None:
        result = self.service.latest_signals(api_key=AUTH_VALUE, topic="mcp")
        payload = json.loads(dumps(result))

        self.assertTrue(payload["ok"])
        self.assertIn("signals", payload)


if __name__ == "__main__":
    unittest.main()
