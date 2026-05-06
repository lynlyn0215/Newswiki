from __future__ import annotations

import unittest
from pathlib import Path

from service.app.repository import PublicExportRepository
from service.app.search import SearchService


ROOT = Path(__file__).resolve().parents[2]


class SearchServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        repository = PublicExportRepository(ROOT / "examples" / "public")
        self.search = SearchService(repository)

    def test_search_signals_by_query(self) -> None:
        results = self.search.search("signals", "hosted MCP", limit=5)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, "signal-demo-001")

    def test_filters_by_topic(self) -> None:
        results = self.search.search("signals", "hosted", topic="missing-topic", limit=5)

        self.assertEqual(results, [])

    def test_latest_signals_returns_updated_items(self) -> None:
        results = self.search.latest_signals(limit=1)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].kind, "signals")


if __name__ == "__main__":
    unittest.main()
