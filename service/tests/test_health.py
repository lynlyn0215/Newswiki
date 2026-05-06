from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

from service.app.repository import PublicExportError, PublicExportRepository


ROOT = Path(__file__).resolve().parents[2]


class ServiceHealthTest(unittest.TestCase):
    def test_examples_health_ok(self) -> None:
        repository = PublicExportRepository(ROOT / "examples" / "public")

        health = repository.health()

        self.assertTrue(health["ok"], health)
        self.assertEqual(health["status"], "ok")

    def test_missing_export_dir_is_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing"
            repository = PublicExportRepository(missing)

            health = repository.health()

        self.assertFalse(health["ok"])
        self.assertEqual(health["status"], "degraded")

    def test_load_collection_rejects_invalid_public_export(self) -> None:
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
            repository = PublicExportRepository(export_dir)

            with self.assertRaises(PublicExportError):
                repository.load_collection("signals")

    def test_real_export_file_takes_precedence_over_example_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp)
            common = {
                "title": "Signal",
                "summary": "Short public-safe summary.",
                "source_urls": ["https://example.com/signal"],
                "topics": ["mcp"],
                "updated_at": "2026-01-02T10:00:00Z",
                "freshness": "daily",
                "confidence": "medium",
                "public_safe": True,
            }
            (export_dir / "signals.example.json").write_text(
                json.dumps({"signals": [dict(common, id="example-signal")]}),
                encoding="utf-8",
            )
            (export_dir / "signals.json").write_text(
                json.dumps({"signals": [dict(common, id="real-signal")]}),
                encoding="utf-8",
            )
            repository = PublicExportRepository(export_dir)

            items = repository.load_collection("signals")

        self.assertEqual([item.id for item in items], ["real-signal"])


if __name__ == "__main__":
    unittest.main()
