from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from service.app.connectors import ConnectorExportError, ConnectorRepository


class ConnectorRepositoryTest(unittest.TestCase):
    def test_missing_connector_dir_returns_empty_items(self) -> None:
        repository = ConnectorRepository(None)

        self.assertEqual(repository.load("private_memory"), [])

    def test_loads_private_memory_connector(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "private_memory.json").write_text(
                json.dumps(
                    {
                        "private_memory": [
                            {
                                "id": "memory-1",
                                "title": "Decision",
                                "summary": "Use layered context.",
                                "topics": ["mcp"],
                                "updated_at": "2026-01-02T10:00:00Z",
                                "freshness": "weekly",
                                "confidence": "high",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            items = ConnectorRepository(root).load("private_memory")

        self.assertEqual(items[0].source_type, "user_private")
        self.assertEqual(items[0].privacy_level, "private")
        self.assertEqual(items[0].actionability, "remember")

    def test_connector_rejects_forbidden_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "private_memory.json").write_text(
                json.dumps(
                    {
                        "private_memory": [
                            {
                                "id": "memory-1",
                                "title": "Bad",
                                "summary": "Bad",
                                "topics": ["mcp"],
                                "updated_at": "2026-01-02T10:00:00Z",
                                "freshness": "weekly",
                                "confidence": "high",
                                "full_text": "raw private note",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaises(ConnectorExportError):
                ConnectorRepository(root).load("private_memory")


if __name__ == "__main__":
    unittest.main()
