from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.validate_public_export import validate


ROOT = Path(__file__).resolve().parents[1]


def valid_signal(**overrides: object) -> dict:
    item = {
        "id": "signal-test-001",
        "title": "A valid signal",
        "summary": "Short public-safe summary.",
        "source_urls": ["https://example.com/signal"],
        "topics": ["mcp"],
        "updated_at": "2026-01-02T10:00:00Z",
        "freshness": "daily",
        "confidence": "medium",
        "public_safe": True,
    }
    item.update(overrides)
    return item


class PublicExportSchemaTest(unittest.TestCase):
    def test_examples_pass_validation(self) -> None:
        report = validate(ROOT / "examples" / "public")

        self.assertTrue(report["ok"], report["errors"])
        self.assertGreaterEqual(len(report["files"]), 5)

    def test_rejects_missing_source_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signals.json"
            path.write_text(json.dumps({"signals": [valid_signal(source_urls=[])]}), encoding="utf-8")

            report = validate(path)

        self.assertFalse(report["ok"])
        self.assertIn("source_urls", report["errors"][0]["path"])

    def test_rejects_public_safe_false(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signals.json"
            path.write_text(json.dumps({"signals": [valid_signal(public_safe=False)]}), encoding="utf-8")

            report = validate(path)

        self.assertFalse(report["ok"])
        self.assertEqual(report["errors"][0]["path"], "signals[0].public_safe")

    def test_rejects_private_path_marker(self) -> None:
        private_path = "C:" + "\\Users" + "\\example\\Desktop\\secret.md"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signals.json"
            path.write_text(json.dumps({"signals": [valid_signal(summary=private_path)]}), encoding="utf-8")

            report = validate(path)

        self.assertFalse(report["ok"])
        self.assertIn("local absolute path", report["errors"][0]["message"])

    def test_rejects_forbidden_full_body_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signals.json"
            path.write_text(json.dumps({"signals": [valid_signal(full_text="too much article text")]}), encoding="utf-8")

            report = validate(path)

        self.assertFalse(report["ok"])
        self.assertIn("forbidden field", report["errors"][0]["message"])

    def test_rejects_secret_like_assignment(self) -> None:
        secret_like = "api" + "_key=" + "a" * 20
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "signals.json"
            path.write_text(json.dumps({"signals": [valid_signal(summary=secret_like)]}), encoding="utf-8")

            report = validate(path)

        self.assertFalse(report["ok"])
        self.assertIn("secret-like", report["errors"][0]["message"])


if __name__ == "__main__":
    unittest.main()
