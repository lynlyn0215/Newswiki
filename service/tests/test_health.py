from __future__ import annotations

import tempfile
import unittest
import json
from pathlib import Path

from service.app.repository import PublicExportError, PublicExportRepository


ROOT = Path(__file__).resolve().parents[2]


def write_minimal_collection(export_dir: Path, collection: str, file_name: str | None = None) -> None:
    name = file_name or f"{collection}.example.json"
    export_dir.joinpath(name).write_text(
        json.dumps(
            {
                collection: [
                    {
                        "id": f"{collection}-1",
                        "title": f"{collection} item",
                        "summary": "Public-safe summary.",
                        "source_urls": ["https://example.com/item"],
                        "topics": ["mcp"],
                        "updated_at": "2026-01-02T10:00:00Z",
                        "freshness": "weekly",
                        "confidence": "medium",
                        "public_safe": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def write_required_non_signal_collections(export_dir: Path) -> None:
    for collection in ["knowledge_pages", "tool_cards", "briefs", "topics"]:
        write_minimal_collection(export_dir, collection)


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

    def test_empty_export_dir_is_degraded(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repository = PublicExportRepository(Path(tmp))

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
            write_required_non_signal_collections(export_dir)
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
                "affected_tasks": ["mcp-product-positioning"],
                "data_limits": [],
                "decision_impact": "Prefer real export over example export.",
                "entities": ["MCP"],
                "last_verified_at": "2026-01-02",
                "newswiki_interpretation": "Real exports should override examples.",
                "observed_at": "2026-01-02",
                "source_claim": "Public-safe signal.",
                "source_confidence": "medium",
                "source_published_at": "2026-01-02",
                "stale_after": "2026-02-02",
                "time_sensitivity": "medium",
                "why_it_matters": "Prevents demo data from shadowing real exports.",
            }
            (export_dir / "signals.example.json").write_text(
                json.dumps({"signals": [dict(common, id="example-signal")]}),
                encoding="utf-8",
            )
            (export_dir / "signals.json").write_text(
                json.dumps({"signals": [dict(common, id="real-signal")]}),
                encoding="utf-8",
            )
            write_required_non_signal_collections(export_dir)
            repository = PublicExportRepository(export_dir)

            items = repository.load_collection("signals")

        self.assertEqual([item.id for item in items], ["real-signal"])

    def test_public_export_rejects_private_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            export_dir = Path(tmp)
            common = {
                "id": "bad-private-signal",
                "title": "Signal",
                "summary": "Short public-safe summary.",
                "source_urls": ["https://example.com/signal"],
                "topics": ["mcp"],
                "updated_at": "2026-01-02T10:00:00Z",
                "freshness": "daily",
                "confidence": "medium",
                "public_safe": True,
                "source_type": "user_private",
                "privacy_level": "private",
                "affected_tasks": ["mcp-product-positioning"],
                "data_limits": [],
                "decision_impact": "Should not be served.",
                "entities": ["MCP"],
                "last_verified_at": "2026-01-02",
                "newswiki_interpretation": "Private provenance should fail validation.",
                "observed_at": "2026-01-02",
                "source_claim": "Private signal.",
                "source_confidence": "medium",
                "source_published_at": "2026-01-02",
                "stale_after": "2026-02-02",
                "time_sensitivity": "medium",
                "why_it_matters": "Prevents private data from crossing the hosted boundary.",
            }
            (export_dir / "signals.json").write_text(json.dumps({"signals": [common]}), encoding="utf-8")
            write_required_non_signal_collections(export_dir)
            repository = PublicExportRepository(export_dir)

            health = repository.health()

        self.assertFalse(health["ok"])


if __name__ == "__main__":
    unittest.main()
