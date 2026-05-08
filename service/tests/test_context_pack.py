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
        self.assertEqual(pack["brief_type"], "pre_plan")
        self.assertFalse(pack["needs_fresh_facts"])
        self.assertIn("external_signals", pack["retrieval_decision"])
        self.assertTrue(pack["relevant_signals"])
        self.assertTrue(pack["relevant_knowledge"])
        self.assertEqual(pack["stale_assumption_warnings"], [])
        self.assertTrue(pack["what_not_to_assume"])
        self.assertTrue(pack["suggested_verification_steps"])
        self.assertTrue(pack["signals"])
        self.assertTrue(pack["knowledge"])
        self.assertEqual(pack["tools"], [])
        self.assertTrue(pack["sources"])
        self.assertIn(pack["confidence"], {"low", "medium", "high"})
        self.assertTrue(pack["freshness"])
        self.assertTrue(pack["hosted_signals"])
        self.assertTrue(pack["curated_knowledge"])
        self.assertEqual(pack["recommended_templates"], [])
        self.assertEqual(pack["signals"][0]["source_type"], "newswiki_hosted")
        self.assertEqual(pack["knowledge"][0]["source_type"], "newswiki_curated")
        self.assertIn("privacy_level", pack["signals"][0])
        self.assertIn("actionability", pack["signals"][0])
        self.assertNotIn("hosted signals are demo fixtures, not market evidence", pack["data_limits"])

    def test_context_pack_handles_empty_results(self) -> None:
        repository = PublicExportRepository(ROOT / "examples" / "public")
        builder = ContextPackBuilder(SearchService(repository), LayerConfig(enabled=()))
        pack = builder.build("unmatched phrase", topic="missing-topic").to_dict()

        self.assertEqual(pack["signals"], [])
        self.assertEqual(pack["knowledge"], [])
        self.assertEqual(pack["tools"], [])
        self.assertEqual(pack["sources"], [])
        self.assertEqual(pack["confidence"], "low")
        self.assertEqual(pack["brief_type"], "pre_plan")
        self.assertEqual(pack["relevant_signals"], [])
        self.assertIn("No external signal matched; avoid claims about current market state.", pack["stale_assumption_warnings"])

    def test_context_pack_respects_enabled_layers(self) -> None:
        repository = PublicExportRepository(ROOT / "examples" / "public")
        builder = ContextPackBuilder(SearchService(repository), LayerConfig(enabled=("newswiki_hosted",)))

        pack = builder.build("Which tool should I use to design hosted MCP service?", topic="mcp").to_dict()

        self.assertTrue(pack["hosted_signals"])
        self.assertEqual(pack["curated_knowledge"], [])
        self.assertEqual(pack["recommended_templates"], [])
        self.assertEqual(pack["knowledge"], [])
        self.assertEqual(pack["tools"], [])
        self.assertEqual(pack["enabled_layers"], ["newswiki_hosted"])

    def test_context_pack_detects_fresh_fact_tasks(self) -> None:
        pack = self.builder.build("latest Claude release impact", topic="mcp").to_dict()

        self.assertTrue(pack["needs_fresh_facts"])
        self.assertEqual(pack["retrieval_decision"]["external_signals"]["status"], "queried")

    def test_context_pack_detects_platform_change_tasks(self) -> None:
        pack = self.builder.build(
            "Should Newswiki keep Skill MCP after Claude and Hermes added stronger native skill systems?",
            topic="ai-agents",
        ).to_dict()

        self.assertTrue(pack["needs_fresh_facts"])

    def test_context_pack_detects_external_signal_tasks(self) -> None:
        pack = self.builder.build(
            "Which external signals should influence the next Newswiki roadmap decision?",
            topic="product-strategy",
        ).to_dict()

        self.assertTrue(pack["needs_fresh_facts"])

    def test_context_pack_falls_back_when_topic_is_too_broad(self) -> None:
        pack = self.builder.build(
            "Should Newswiki keep Skill MCP as a core product feature after Claude and Hermes added stronger native skill systems?",
            topic="ai-agents",
        ).to_dict()

        self.assertTrue(pack["signals"])
        self.assertTrue(any("codex" in signal["id"] or "cursor" in signal["id"] for signal in pack["signals"]))

    def test_context_pack_skips_external_signals_for_trivial_local_tasks(self) -> None:
        pack = self.builder.build("rename a local variable").to_dict()

        self.assertEqual(pack["signals"], [])
        self.assertEqual(pack["knowledge"], [])
        self.assertEqual(pack["retrieval_decision"]["external_signals"]["status"], "skipped")
        self.assertEqual(pack["retrieval_decision"]["durable_knowledge"]["status"], "skipped")
        self.assertNotIn("user_private wiki layer is not connected", pack["data_limits"])
        self.assertNotIn("local capability layer is not connected", pack["data_limits"])
        self.assertEqual(pack["stale_assumption_warnings"], [])

    def test_context_pack_queries_tools_only_for_tool_routing_tasks(self) -> None:
        pack = self.builder.build("Which MCP setup command should I run for Claude Code?", topic="mcp").to_dict()

        self.assertTrue(pack["tools"])
        self.assertEqual(pack["retrieval_decision"]["capability_routing"]["status"], "queried")

    def test_context_pack_routes_skill_workflow_language_to_capabilities(self) -> None:
        pack = self.builder.build("Which skill should I use for this workflow?").to_dict()

        self.assertEqual(pack["retrieval_decision"]["capability_routing"]["status"], "queried")
        self.assertIn("local capability layer is not connected", pack["data_limits"])

    def test_context_pack_does_not_route_strategy_mentions_of_skill_mcp_to_capabilities(self) -> None:
        pack = self.builder.build("Should Newswiki keep Skill MCP as a core product feature?").to_dict()

        self.assertEqual(pack["retrieval_decision"]["capability_routing"]["status"], "skipped")
        self.assertEqual(pack["tools"], [])

    def test_context_pack_does_not_route_product_surface_mcp_language_to_capabilities(self) -> None:
        product_tasks = [
            "Should Newswiki use MCP as the hosted product surface?",
            "Should Newswiki recommend MCP as a core product feature?",
        ]

        for task in product_tasks:
            with self.subTest(task=task):
                pack = self.builder.build(task, topic="product-strategy").to_dict()

                self.assertEqual(pack["retrieval_decision"]["capability_routing"]["status"], "skipped")
                self.assertEqual(pack["tools"], [])

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
                title="Wiki MCP tool",
                summary="Tool route for wiki_past_knowledge before planning hosted MCP work.",
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

        pack = builder.build("Which tool should I use to design hosted MCP service?", topic="mcp").to_dict()

        self.assertEqual(pack["private_memory"][0]["source_type"], "user_private")
        self.assertEqual(pack["local_capabilities"][0]["source_type"], "local_capability")
        self.assertNotIn("user_private wiki layer is not connected", pack["data_limits"])
        self.assertNotIn("local capability layer is not connected", pack["data_limits"])


if __name__ == "__main__":
    unittest.main()
