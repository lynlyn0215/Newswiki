from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PublicItem:
    id: str
    title: str
    summary: str
    source_urls: list[str]
    topics: list[str]
    updated_at: str
    freshness: str
    confidence: str
    kind: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContextPack:
    task: str
    answer: str
    signals: list[PublicItem]
    knowledge: list[PublicItem]
    tools: list[PublicItem]
    sources: list[str]
    freshness: str
    confidence: str
    suggested_next_queries: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "answer": self.answer,
            "signals": [item_to_dict(item) for item in self.signals],
            "knowledge": [item_to_dict(item) for item in self.knowledge],
            "tools": [item_to_dict(item) for item in self.tools],
            "sources": self.sources,
            "freshness": self.freshness,
            "confidence": self.confidence,
            "suggested_next_queries": self.suggested_next_queries,
        }


def item_to_dict(item: PublicItem) -> dict[str, Any]:
    data = {
        "id": item.id,
        "title": item.title,
        "summary": item.summary,
        "source_urls": item.source_urls,
        "topics": item.topics,
        "updated_at": item.updated_at,
        "freshness": item.freshness,
        "confidence": item.confidence,
        "kind": item.kind,
    }
    data.update(item.extra)
    return data
