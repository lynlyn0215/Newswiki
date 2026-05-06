from __future__ import annotations

from service.app.models import ContextPack, PublicItem
from service.app.search import SearchService


CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


class ContextPackBuilder:
    def __init__(self, search: SearchService) -> None:
        self.search = search

    def build(self, task: str, *, topic: str | None = None, token_budget: int = 1200) -> ContextPack:
        per_group = 2 if token_budget < 900 else 3
        signals = self.search.search("signals", task, topic=topic, limit=per_group)
        if not signals:
            signals = self.search.latest_signals(topic=topic, limit=min(1, per_group))
        knowledge = self.search.search("knowledge_pages", task, topic=topic, limit=per_group)
        tools = self.search.search("tool_cards", task, topic=topic, limit=per_group)
        sources = unique_sources([*signals, *knowledge, *tools])
        freshness = latest_updated_at([*signals, *knowledge, *tools])
        confidence = aggregate_confidence([*signals, *knowledge, *tools])
        answer = summarize_context(task, signals=signals, knowledge=knowledge, tools=tools)
        next_queries = suggested_queries(task, topic)
        return ContextPack(
            task=task,
            answer=answer,
            signals=signals,
            knowledge=knowledge,
            tools=tools,
            sources=sources,
            freshness=freshness,
            confidence=confidence,
            suggested_next_queries=next_queries,
        )


def unique_sources(items: list[PublicItem]) -> list[str]:
    seen: set[str] = set()
    sources: list[str] = []
    for item in items:
        for url in item.source_urls:
            if url in seen:
                continue
            seen.add(url)
            sources.append(url)
    return sources


def latest_updated_at(items: list[PublicItem]) -> str:
    if not items:
        return ""
    return max(item.updated_at for item in items)


def aggregate_confidence(items: list[PublicItem]) -> str:
    if not items:
        return "low"
    values = [CONFIDENCE_ORDER.get(item.confidence, 0) for item in items]
    average = sum(values) / len(values)
    if average >= 1.7:
        return "high"
    if average >= 0.7:
        return "medium"
    return "low"


def summarize_context(task: str, *, signals: list[PublicItem], knowledge: list[PublicItem], tools: list[PublicItem]) -> str:
    parts = [f"Context pack for task: {task}."]
    if signals:
        parts.append(f"Recent signal: {signals[0].title}.")
    if knowledge:
        parts.append(f"Relevant knowledge: {knowledge[0].title}.")
    if tools:
        parts.append(f"Tool route: {tools[0].title}.")
    if len(parts) == 1:
        parts.append("No strong matches found in the public export.")
    return " ".join(parts)


def suggested_queries(task: str, topic: str | None) -> list[str]:
    base = topic or "agent infrastructure"
    return [
        f"latest {base} signals",
        f"{base} tool recommendations",
        f"{task} risks and sources",
    ]
