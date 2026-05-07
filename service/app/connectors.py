from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from service.app.models import PublicItem


CONNECTOR_FILES = {
    "private_memory": ("private_memory.json", "user_private", "private", "remember"),
    "local_capabilities": ("local_capabilities.json", "local_capability", "private", "call"),
}

FORBIDDEN_CONNECTOR_FIELDS = {
    "api_key",
    "body",
    "content",
    "credential",
    "credentials",
    "full_text",
    "local_path",
    "password",
    "private_notes",
    "raw_content",
    "secret",
    "session_state",
    "token",
}


class ConnectorExportError(RuntimeError):
    pass


class ConnectorRepository:
    def __init__(self, root: Path | None) -> None:
        self.root = root

    def load(self, collection: str) -> list[PublicItem]:
        if self.root is None:
            return []
        if collection not in CONNECTOR_FILES:
            raise ConnectorExportError(f"unknown connector collection: {collection}")
        file_name, source_type, privacy_level, actionability = CONNECTOR_FILES[collection]
        path = self.root / file_name
        if not path.exists():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
        items = data.get(collection)
        if not isinstance(items, list):
            raise ConnectorExportError(f"{file_name} must contain {collection} array")
        return [
            to_connector_item(raw, collection, source_type, privacy_level, actionability)
            for raw in items
        ]


def to_connector_item(
    raw: dict[str, Any],
    kind: str,
    source_type: str,
    privacy_level: str,
    actionability: str,
) -> PublicItem:
    ensure_connector_safe(raw)
    required = ["id", "title", "summary", "topics", "updated_at", "freshness", "confidence"]
    missing = [field for field in required if not raw.get(field)]
    if missing:
        raise ConnectorExportError(f"{kind} item missing fields: {', '.join(missing)}")
    common = {
        "id",
        "title",
        "summary",
        "source_urls",
        "topics",
        "updated_at",
        "freshness",
        "confidence",
        "source_type",
        "privacy_level",
        "actionability",
    }
    extra = {key: value for key, value in raw.items() if key not in common}
    return PublicItem(
        id=raw["id"],
        title=raw["title"],
        summary=raw["summary"],
        source_urls=list(raw.get("source_urls", [])),
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


def ensure_connector_safe(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in FORBIDDEN_CONNECTOR_FIELDS:
                raise ConnectorExportError(f"connector export uses forbidden field: {key}")
            ensure_connector_safe(child)
    elif isinstance(value, list):
        for child in value:
            ensure_connector_safe(child)
