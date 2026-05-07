from __future__ import annotations

from service.app.models import ContextPack, PublicItem
from service.app.search import SearchService
from service.app.settings import LayerConfig


CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}


class ContextPackBuilder:
    def __init__(
        self,
        search: SearchService,
        layers: LayerConfig | None = None,
        *,
        private_memory: list[PublicItem] | None = None,
        local_capabilities: list[PublicItem] | None = None,
    ) -> None:
        self.search = search
        self.layers = layers or LayerConfig()
        self.private_memory = private_memory or []
        self.local_capabilities = local_capabilities or []

    def build(self, task: str, *, topic: str | None = None, token_budget: int = 1200) -> ContextPack:
        per_group = 2 if token_budget < 900 else 3
        signals = self.search.search("signals", task, topic=topic, limit=per_group)
        if not signals:
            signals = self.search.latest_signals(topic=topic, limit=min(1, per_group))
        knowledge = self.search.search("knowledge_pages", task, topic=topic, limit=per_group)
        tools = self.search.search("tool_cards", task, topic=topic, limit=per_group)
        signals = filter_enabled(signals, self.layers)
        knowledge = filter_enabled(knowledge, self.layers)
        tools = filter_enabled(tools, self.layers)
        private_memory = filter_enabled(rank_items(self.private_memory, task, topic=topic, limit=per_group), self.layers)
        local_capabilities = filter_enabled(
            rank_items(self.local_capabilities, task, topic=topic, limit=per_group),
            self.layers,
        )
        hosted_signals = [item for item in signals if item.source_type == "newswiki_hosted"]
        curated_knowledge = [item for item in knowledge if item.source_type == "newswiki_curated"]
        recommended_templates = [item for item in tools if item.source_type == "recommended_template"]
        all_items = [*signals, *knowledge, *tools, *private_memory, *local_capabilities]
        sources = unique_sources(all_items)
        freshness = latest_updated_at(all_items)
        confidence = aggregate_confidence(all_items)
        answer = summarize_context(task, signals=signals, knowledge=knowledge, tools=tools)
        next_queries = suggested_queries(task, topic)
        data_limits = context_data_limits(
            signals=signals,
            private_memory=private_memory,
            local_capabilities=local_capabilities,
            layers=self.layers,
        )
        return ContextPack(
            task=task,
            answer=answer,
            signals=signals,
            knowledge=knowledge,
            tools=tools,
            private_memory=private_memory,
            hosted_signals=hosted_signals,
            curated_knowledge=curated_knowledge,
            local_capabilities=local_capabilities,
            recommended_templates=recommended_templates,
            sources=sources,
            freshness=freshness,
            confidence=confidence,
            enabled_layers=list(self.layers.enabled),
            data_limits=data_limits,
            suggested_next_queries=next_queries,
        )


def filter_enabled(items: list[PublicItem], layers: LayerConfig) -> list[PublicItem]:
    return [item for item in items if layers.allows(item.source_type)]


def rank_items(items: list[PublicItem], task: str, *, topic: str | None, limit: int) -> list[PublicItem]:
    filtered = items
    if topic:
        filtered = [item for item in filtered if topic in item.topics]
    terms = [term.lower() for term in task.split() if len(term) > 2]
    if not terms:
        return filtered[:limit]
    scored: list[tuple[int, PublicItem]] = []
    for item in filtered:
        haystack = " ".join([item.title, item.summary, " ".join(item.topics)]).lower()
        score = sum(haystack.count(term) for term in terms)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: (pair[0], pair[1].updated_at), reverse=True)
    return [item for _, item in scored[:limit]]


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


def context_data_limits(
    *,
    signals: list[PublicItem],
    private_memory: list[PublicItem],
    local_capabilities: list[PublicItem],
    layers: LayerConfig,
) -> list[str]:
    limits: list[str] = []
    if "user_private" not in layers.enabled:
        limits.append("user_private wiki layer is not connected")
    elif not private_memory:
        limits.append("user_private wiki layer returned no memory")
    if "local_capability" not in layers.enabled:
        limits.append("local capability layer is not connected")
    elif not local_capabilities:
        limits.append("local capability layer returned no tools")
    if signals and all("demo" in item.id for item in signals):
        limits.append("hosted signals are demo fixtures, not market evidence")
    return limits
