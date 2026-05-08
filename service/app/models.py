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
    source_type: str
    privacy_level: str
    actionability: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ContextPack:
    task: str
    answer: str
    brief_type: str
    needs_fresh_facts: bool
    retrieval_decision: dict[str, dict[str, Any]]
    relevant_signals: list[PublicItem]
    relevant_knowledge: list[PublicItem]
    stale_assumption_warnings: list[str]
    what_not_to_assume: list[str]
    suggested_verification_steps: list[str]
    signals: list[PublicItem]
    knowledge: list[PublicItem]
    tools: list[PublicItem]
    private_memory: list[PublicItem]
    hosted_signals: list[PublicItem]
    curated_knowledge: list[PublicItem]
    local_capabilities: list[PublicItem]
    recommended_templates: list[PublicItem]
    sources: list[str]
    freshness: str
    confidence: str
    enabled_layers: list[str]
    data_limits: list[str]
    suggested_next_queries: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task": self.task,
            "answer": self.answer,
            "brief_type": self.brief_type,
            "needs_fresh_facts": self.needs_fresh_facts,
            "retrieval_decision": self.retrieval_decision,
            "relevant_signals": [item_to_dict(item) for item in self.relevant_signals],
            "relevant_knowledge": [item_to_dict(item) for item in self.relevant_knowledge],
            "stale_assumption_warnings": self.stale_assumption_warnings,
            "what_not_to_assume": self.what_not_to_assume,
            "suggested_verification_steps": self.suggested_verification_steps,
            "signals": [item_to_dict(item) for item in self.signals],
            "knowledge": [item_to_dict(item) for item in self.knowledge],
            "tools": [item_to_dict(item) for item in self.tools],
            "private_memory": [item_to_dict(item) for item in self.private_memory],
            "hosted_signals": [item_to_dict(item) for item in self.hosted_signals],
            "curated_knowledge": [item_to_dict(item) for item in self.curated_knowledge],
            "local_capabilities": [item_to_dict(item) for item in self.local_capabilities],
            "recommended_templates": [item_to_dict(item) for item in self.recommended_templates],
            "sources": self.sources,
            "freshness": self.freshness,
            "confidence": self.confidence,
            "enabled_layers": self.enabled_layers,
            "data_limits": self.data_limits,
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
        "source_type": item.source_type,
        "privacy_level": item.privacy_level,
        "actionability": item.actionability,
    }
    data.update(item.extra)
    return data
