from __future__ import annotations

import unittest
from pathlib import Path

from service.app.context_pack import ContextPackBuilder
from service.app.models import PublicItem
from service.app.repository import PublicExportRepository
from service.app.search import SearchService
from service.app.settings import LayerConfig


ROOT = Path(__file__).resolve().parents[2]


class ContextPackTest(unittest.TestCase):
    def setUp(self) -> None:
        repository = PublicExportRepository(ROOT / "examples" / "public")
        self.builder = ContextPackBuilder(SearchService(repository))

    def test_context_pack_combines_sources(self) -> None:
        pack = self.builder.build("design hosted MCP service", topic="mcp").to_dict()

        self.assertEqual(pack["task"], "design hosted MCP service")
        self.assertTrue(pack["signals"])
        self.assertTrue(pack["knowledge"])
        self.assertTrue(pack["tools"])
        self.assertTrue(pack["sources"])
        self.assertIn(pack["confidence"], {"low", "medium", "high"})
        self.assertTrue(pack["freshness"])
        self.assertTrue(pack["hosted_signals"])
        self.assertTrue(pack["curated_knowledge"])
        self.assertTrue(pack["recommended_templates"])
        self.assertEqual(pack["signals"][0]["source_type"], "newswiki_hosted")
        self.assertEqual(pack["knowledge"][0]["source_type"], "newswiki_curated")
        self.assertEqual(pack["tools"][0]["source_type"], "recommended_template")
        self.assertIn("privacy_level", pack["signals"][0])
        self.assertIn("actionability", pack["signals"][0])
        self.assertIn("hosted signals are demo fixtures, not market evidence", pack["data_limits"])

    def test_context_pack_handles_empty_results(self) -> None:
        pack = self.builder.build("unmatched phrase", topic="missing-topic").to_dict()

        self.assertEqual(pack["signals"], [])
        self.assertEqual(pack["knowledge"], [])
        self.assertEqual(pack["tools"], [])
        self.assertEqual(pack["sources"], [])
        self.assertEqual(pack["confidence"], "low")

    def test_context_pack_respects_enabled_layers(self) -> None:
        repository = PublicExportRepository(ROOT / "examples" / "public")
        builder = ContextPackBuilder(SearchService(repository), LayerConfig(enabled=("newswiki_hosted",)))

        pack = builder.build("design hosted MCP service", topic="mcp").to_dict()

        self.assertTrue(pack["hosted_signals"])
        self.assertEqual(pack["curated_knowledge"], [])
        self.assertEqual(pack["recommended_templates"], [])
        self.assertEqual(pack["knowledge"], [])
        self.assertEqual(pack["tools"], [])
        self.assertEqual(pack["enabled_layers"], ["newswiki_hosted"])

    def test_context_pack_composes_user_private_and_local_capability_layers(self) -> None:
        repository = PublicExportRepository(ROOT / "examples" / "public")
        private_memory = [
            PublicItem(
                id="memory-1",
                title="Hosted MCP decision",
                summary="Use user private memory as the default wiki layer.",
                source_urls=[],
                topics=["mcp"],
                updated_at="2026-01-03T10:00:00Z",
                freshness="weekly",
                confidence="high",
                kind="private_memory",
                source_type="user_private",
                privacy_level="private",
                actionability="remember",
            )
        ]
        local_capabilities = [
            PublicItem(
                id="capability-1",
                title="Wiki MCP",
                summary="Call wiki_past_knowledge before planning hosted MCP work.",
                source_urls=[],
                topics=["mcp"],
                updated_at="2026-01-03T10:00:00Z",
                freshness="weekly",
                confidence="high",
                kind="local_capabilities",
                source_type="local_capability",
                privacy_level="private",
                actionability="call",
            )
        ]
        builder = ContextPackBuilder(
            SearchService(repository),
            LayerConfig(
                enabled=(
                    "newswiki_hosted",
                    "newswiki_curated",
                    "recommended_template",
                    "user_private",
                    "local_capability",
                )
            ),
            private_memory=private_memory,
            local_capabilities=local_capabilities,
        )

        pack = builder.build("design hosted MCP service", topic="mcp").to_dict()

        self.assertEqual(pack["private_memory"][0]["source_type"], "user_private")
        self.assertEqual(pack["local_capabilities"][0]["source_type"], "local_capability")
        self.assertNotIn("user_private wiki layer is not connected", pack["data_limits"])
        self.assertNotIn("local capability layer is not connected", pack["data_limits"])


if __name__ == "__main__":
    unittest.main()
