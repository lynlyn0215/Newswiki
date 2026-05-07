from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.validate_public_export import validate
from service.app.models import PublicItem


COLLECTION_FILES = {
    "signals": "signals.example.json",
    "knowledge_pages": "knowledge_pages.example.json",
    "tool_cards": "tool_cards.example.json",
    "briefs": "briefs.example.json",
    "topics": "topics.example.json",
}

DEFAULT_PROVENANCE = {
    "signals": ("newswiki_hosted", "public", "read"),
    "knowledge_pages": ("newswiki_curated", "public", "reference"),
    "tool_cards": ("recommended_template", "public", "install_or_configure"),
    "briefs": ("newswiki_curated", "public", "reference"),
    "topics": ("newswiki_curated", "public", "reference"),
}


class PublicExportError(RuntimeError):
    pass


class PublicExportRepository:
    def __init__(self, export_dir: Path) -> None:
        self.export_dir = export_dir
        self._validation_report: dict[str, Any] | None = None

    def health(self) -> dict[str, object]:
        if not self.export_dir.exists():
            return {"ok": False, "status": "degraded", "reason": "export directory missing"}
        report = validate(self.export_dir)
        return {"ok": report["ok"], "status": "ok" if report["ok"] else "degraded", "errors": report["errors"]}

    def load_all(self) -> dict[str, list[PublicItem]]:
        self._ensure_valid()
        return {collection: self.load_collection(collection) for collection in COLLECTION_FILES}

    def load_collection(self, collection: str) -> list[PublicItem]:
        self._ensure_valid()
        path = self._collection_path(collection)
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        return [to_public_item(raw, collection) for raw in data.get(collection, [])]

    def _ensure_valid(self) -> None:
        if self._validation_report is None:
            self._validation_report = validate(self.export_dir)
        if not self._validation_report["ok"]:
            raise PublicExportError("public export validation failed")

    def _collection_path(self, collection: str) -> Path:
        file_name = COLLECTION_FILES[collection]
        real_path = self.export_dir / file_name.replace(".example", "")
        if real_path.exists():
            return real_path
        return self.export_dir / file_name


def to_public_item(raw: dict[str, Any], kind: str) -> PublicItem:
    common = {
        "id",
        "title",
        "summary",
        "source_urls",
        "topics",
        "updated_at",
        "freshness",
        "confidence",
        "public_safe",
        "source_type",
        "privacy_level",
        "actionability",
    }
    extra = {key: value for key, value in raw.items() if key not in common}
    source_type, privacy_level, actionability = DEFAULT_PROVENANCE.get(kind, ("newswiki_curated", "public", "reference"))
    return PublicItem(
        id=raw["id"],
        title=raw["title"],
        summary=raw["summary"],
        source_urls=list(raw["source_urls"]),
        topics=list(raw["topics"]),
        updated_at=raw["updated_at"],
        freshness=raw["freshness"],
        confidence=raw["confidence"],
        kind=kind,
        source_type=raw.get("source_type", source_type),
        privacy_level=raw.get("privacy_level", privacy_level),
        actionability=raw.get("actionability", actionability),
        extra=extra,
    )
