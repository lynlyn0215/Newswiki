from __future__ import annotations

import unittest
from pathlib import Path

from service.app.context_pack import ContextPackBuilder
from service.app.repository import PublicExportRepository
from service.app.search import SearchService


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

    def test_context_pack_handles_empty_results(self) -> None:
        pack = self.builder.build("unmatched phrase", topic="missing-topic").to_dict()

        self.assertEqual(pack["signals"], [])
        self.assertEqual(pack["knowledge"], [])
        self.assertEqual(pack["tools"], [])
        self.assertEqual(pack["sources"], [])
        self.assertEqual(pack["confidence"], "low")


if __name__ == "__main__":
    unittest.main()
