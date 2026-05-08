from __future__ import annotations

from dataclasses import dataclass

from service.app.models import ContextPack, PublicItem
from service.app.search import SearchService
from service.app.settings import LayerConfig


CONFIDENCE_ORDER = {"low": 0, "medium": 1, "high": 2}
FRESH_FACT_TERMS = {
    "added",
    "after",
    "change",
    "changed",
    "current",
    "external",
    "launch",
    "launched",
    "latest",
    "market",
    "new",
    "recent",
    "release",
    "support",
    "supports",
    "today",
    "trend",
    "signals",
    "update",
    "version",
}
CAPABILITY_TERMS = {
    "available",
    "cli",
    "command",
    "commands",
    "configure",
    "install",
    "setup",
    "tool",
    "tools",
}
ROUTING_OBJECT_TERMS = {"skill", "skills", "workflow", "workflows", "mcp", "mcps"}
ROUTING_INTENT_TERMS = {"best", "choose", "pick", "recommend", "route", "select", "use"}
PRODUCT_STRATEGY_TERMS = {"core", "feature", "hosted", "product", "roadmap", "service", "surface"}
OPERATOR_ROUTING_TERMS = CAPABILITY_TERMS | {"which", "workflow", "workflows"}
CONTEXT_DOMAIN_TERMS = {
    "agent",
    "agents",
    "architecture",
    "context",
    "mcp",
    "newswiki",
    "platform",
    "product",
    "roadmap",
    "service",
}


@dataclass(frozen=True)
class SearchOutcome:
    items: list[PublicItem]
    status: str
    reason: str
    topic: str | None
    topic_matched: bool
    fallback_used: bool
    result_count: int


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
        needs_fresh_facts = task_needs_fresh_facts(task)
        should_query_signals = task_should_query_external_signals(task, topic=topic, needs_fresh_facts=needs_fresh_facts)
        signals_outcome = skipped_outcome(
            topic=topic,
            reason="Task does not depend on current external or domain context.",
        )
        if should_query_signals:
            signals_outcome = search_with_topic_fallback(
                self.search,
                "signals",
                task,
                topic=topic,
                limit=per_group,
                reason=external_signal_reason(needs_fresh_facts=needs_fresh_facts, topic=topic, task=task),
            )
            if not signals_outcome.items:
                latest = self.search.latest_signals(topic=topic, limit=min(1, per_group))
                if latest:
                    signals_outcome = SearchOutcome(
                        items=latest,
                        status="latest_fallback",
                        reason="No search result matched; returned latest signals for situational awareness.",
                        topic=topic,
                        topic_matched=bool(topic and all(topic in item.topics for item in latest)),
                        fallback_used=True,
                        result_count=len(latest),
                    )
                elif topic:
                    latest = self.search.latest_signals(limit=min(1, per_group))
                    signals_outcome = SearchOutcome(
                        items=latest,
                        status="global_latest_fallback" if latest else "no_results",
                        reason="No topic result matched; returned global latest signals only as weak background context.",
                        topic=topic,
                        topic_matched=False,
                        fallback_used=bool(latest),
                        result_count=len(latest),
                    )
        capability_needed = task_needs_capability_routing(task)
        knowledge_needed = task_needs_durable_knowledge(
            task,
            topic=topic,
            needs_fresh_facts=needs_fresh_facts,
            capability_needed=capability_needed,
            should_query_signals=should_query_signals,
        )
        knowledge_outcome = skipped_outcome(
            topic=topic,
            reason="Task does not need durable project or product context.",
        )
        if knowledge_needed:
            knowledge_outcome = search_with_topic_fallback(
                self.search,
                "knowledge_pages",
                task,
                topic=topic,
                limit=per_group,
                reason="Task may benefit from durable Newswiki product or architecture context.",
            )
        tools_outcome = skipped_outcome(
            topic=topic,
            reason="Task is not asking to choose, install, configure, or route local tools.",
        )
        if capability_needed:
            tools_outcome = search_with_topic_fallback(
                self.search,
                "tool_cards",
                task,
                topic=topic,
                limit=per_group,
                reason="Task asks about tool setup, local availability, commands, or workflow routing.",
            )
        signals = filter_enabled(signals_outcome.items, self.layers)
        knowledge = filter_enabled(knowledge_outcome.items, self.layers)
        tools = filter_enabled(tools_outcome.items, self.layers)
        signals_outcome = with_filtered_items(signals_outcome, signals, self.layers.allows("newswiki_hosted"))
        knowledge_outcome = with_filtered_items(knowledge_outcome, knowledge, self.layers.allows("newswiki_curated"))
        tools_outcome = with_filtered_items(tools_outcome, tools, self.layers.allows("recommended_template"))
        private_memory = []
        if knowledge_needed:
            private_memory = filter_enabled(rank_items(self.private_memory, task, topic=topic, limit=per_group), self.layers)
        local_capabilities = []
        if capability_needed:
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
        data_limits = context_data_limits(
            signals=signals,
            private_memory=private_memory,
            local_capabilities=local_capabilities,
            layers=self.layers,
            retrieval_outcomes=[signals_outcome, knowledge_outcome, tools_outcome],
            knowledge_needed=knowledge_needed,
            capability_needed=capability_needed,
        )
        confidence = aggregate_confidence(all_items, data_limits=data_limits)
        next_queries = suggested_queries(task, topic)
        retrieval_decision = build_retrieval_decision(
            needs_fresh_facts=needs_fresh_facts,
            should_query_signals=should_query_signals,
            knowledge_needed=knowledge_needed,
            capability_needed=capability_needed,
            signals=signals_outcome,
            knowledge=knowledge_outcome,
            tools=tools_outcome,
            task=task,
        )
        stale_warnings = stale_assumption_warnings(
            signals=signals,
            knowledge=knowledge,
            data_limits=data_limits,
            should_query_signals=should_query_signals,
            knowledge_needed=knowledge_needed,
        )
        what_not_to_assume = assumptions_to_avoid(data_limits=data_limits, signals=signals)
        verification_steps = suggested_verification_steps(
            needs_fresh_facts=needs_fresh_facts,
            sources=sources,
            data_limits=data_limits,
        )
        answer = summarize_context(
            task,
            signals=signals,
            knowledge=knowledge,
            tools=tools,
            data_limits=data_limits,
            retrieval_decision=retrieval_decision,
        )
        return ContextPack(
            task=task,
            answer=answer,
            brief_type="pre_plan",
            needs_fresh_facts=needs_fresh_facts,
            retrieval_decision=retrieval_decision,
            relevant_signals=hosted_signals,
            relevant_knowledge=[*curated_knowledge, *private_memory],
            stale_assumption_warnings=stale_warnings,
            what_not_to_assume=what_not_to_assume,
            suggested_verification_steps=verification_steps,
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


def skipped_outcome(*, topic: str | None, reason: str) -> SearchOutcome:
    return SearchOutcome(
        items=[],
        status="skipped",
        reason=reason,
        topic=topic,
        topic_matched=False,
        fallback_used=False,
        result_count=0,
    )


def search_with_topic_fallback(
    search: SearchService,
    collection: str,
    task: str,
    *,
    topic: str | None,
    limit: int,
    reason: str,
) -> SearchOutcome:
    results = search.search(collection, task, topic=topic, limit=limit)
    if results:
        return SearchOutcome(
            items=results,
            status="queried",
            reason=reason,
            topic=topic,
            topic_matched=bool(topic),
            fallback_used=False,
            result_count=len(results),
        )
    if not topic:
        return SearchOutcome(
            items=[],
            status="no_results",
            reason=reason,
            topic=topic,
            topic_matched=False,
            fallback_used=False,
            result_count=0,
        )
    fallback = search.search(collection, task, limit=limit)
    return SearchOutcome(
        items=fallback,
        status="fallback_used" if fallback else "no_results",
        reason=f"{reason} Topic-specific search returned no results; used global fallback." if fallback else reason,
        topic=topic,
        topic_matched=False,
        fallback_used=bool(fallback),
        result_count=len(fallback),
    )


def with_filtered_items(outcome: SearchOutcome, items: list[PublicItem], layer_enabled: bool) -> SearchOutcome:
    if not layer_enabled and outcome.status not in {"skipped", "no_results"}:
        return SearchOutcome(
            items=[],
            status="disabled",
            reason=f"{outcome.reason} Layer is disabled.",
            topic=outcome.topic,
            topic_matched=outcome.topic_matched,
            fallback_used=outcome.fallback_used,
            result_count=0,
        )
    if len(items) == outcome.result_count:
        return outcome
    return SearchOutcome(
        items=items,
        status=outcome.status if items else "filtered_empty",
        reason=outcome.reason,
        topic=outcome.topic,
        topic_matched=outcome.topic_matched,
        fallback_used=outcome.fallback_used,
        result_count=len(items),
    )


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


def aggregate_confidence(items: list[PublicItem], *, data_limits: list[str] | None = None) -> str:
    if not items:
        return "low"
    values = [CONFIDENCE_ORDER.get(item.confidence, 0) for item in items]
    average = sum(values) / len(values)
    if data_limits and any("fallback" in limit.lower() or "not external market evidence" in limit.lower() for limit in data_limits):
        average -= 0.8
    if average >= 1.7:
        return "high"
    if average >= 0.7:
        return "medium"
    return "low"


def summarize_context(
    task: str,
    *,
    signals: list[PublicItem],
    knowledge: list[PublicItem],
    tools: list[PublicItem],
    data_limits: list[str],
    retrieval_decision: dict[str, dict[str, object]],
) -> str:
    parts = [f"Pre-plan brief for task: {task}."]
    if signals:
        signal = signals[0]
        parts.append(f"Strongest external signal: {signal.title}.")
        if signal.extra.get("decision_impact"):
            parts.append(f"Decision impact: {signal.extra['decision_impact']}")
    if knowledge:
        knowledge_item = knowledge[0]
        parts.append(f"Relevant durable knowledge: {knowledge_item.title}.")
        if knowledge_item.extra.get("why_it_matters"):
            parts.append(f"Why it matters: {knowledge_item.extra['why_it_matters']}")
    if tools:
        parts.append(f"Tool route only if needed: {tools[0].title}.")
    if retrieval_decision["external_signals"].get("fallback_used"):
        parts.append("External signal retrieval used fallback; treat returned signals as weaker background context.")
    if data_limits:
        parts.append(f"Limits: {'; '.join(data_limits[:2])}.")
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
    retrieval_outcomes: list[SearchOutcome],
    knowledge_needed: bool,
    capability_needed: bool,
) -> list[str]:
    limits: list[str] = []
    if knowledge_needed and "user_private" not in layers.enabled:
        limits.append("user_private wiki layer is not connected")
    elif knowledge_needed and not private_memory and "user_private" in layers.enabled:
        limits.append("user_private wiki layer returned no memory")
    if capability_needed and "local_capability" not in layers.enabled:
        limits.append("local capability layer is not connected")
    elif capability_needed and not local_capabilities and "local_capability" in layers.enabled:
        limits.append("local capability layer returned no tools")
    if signals and all("demo" in item.id for item in signals):
        limits.append("hosted signals are demo fixtures, not market evidence")
    for outcome in retrieval_outcomes:
        if outcome.fallback_used:
            limits.append(f"{outcome.topic or 'untagged'} retrieval used fallback; do not treat results as direct topic evidence")
    for outcome in retrieval_outcomes:
        for item in outcome.items:
            for limit in item.extra.get("data_limits", []):
                if isinstance(limit, str) and limit not in limits:
                    limits.append(limit)
    for item in [*private_memory, *local_capabilities]:
        for limit in item.extra.get("data_limits", []):
            if isinstance(limit, str) and limit not in limits:
                limits.append(limit)
    return limits


def task_terms(task: str) -> set[str]:
    return {term.strip(".,?!:;()[]{}").lower() for term in task.split() if term.strip()}


def task_needs_fresh_facts(task: str) -> bool:
    return bool(task_terms(task) & FRESH_FACT_TERMS)


def task_needs_capability_routing(task: str) -> bool:
    terms = task_terms(task)
    if terms & CAPABILITY_TERMS:
        return True
    if "newswiki" in terms and terms & PRODUCT_STRATEGY_TERMS and not (terms & OPERATOR_ROUTING_TERMS):
        return False
    return bool((terms & ROUTING_OBJECT_TERMS) and (terms & ROUTING_INTENT_TERMS))


def task_needs_durable_knowledge(
    task: str,
    *,
    topic: str | None,
    needs_fresh_facts: bool,
    capability_needed: bool,
    should_query_signals: bool,
) -> bool:
    if topic or needs_fresh_facts or capability_needed or should_query_signals:
        return True
    return bool(task_terms(task) & CONTEXT_DOMAIN_TERMS)


def task_should_query_external_signals(task: str, *, topic: str | None, needs_fresh_facts: bool) -> bool:
    if needs_fresh_facts or topic:
        return True
    return bool(task_terms(task) & CONTEXT_DOMAIN_TERMS)


def build_retrieval_decision(
    *,
    needs_fresh_facts: bool,
    should_query_signals: bool,
    knowledge_needed: bool,
    capability_needed: bool,
    signals: SearchOutcome,
    knowledge: SearchOutcome,
    tools: SearchOutcome,
    task: str,
) -> dict[str, dict[str, object]]:
    return {
        "external_signals": decision_entry(
            signals,
            status=signals.status if should_query_signals else "skipped",
            reason=signals.reason if should_query_signals else "Task does not need external signal context.",
            needed=should_query_signals,
            extra={"needs_fresh_facts": needs_fresh_facts},
        ),
        "durable_knowledge": decision_entry(
            knowledge,
            status=knowledge.status if knowledge_needed else "skipped",
            reason=knowledge.reason if knowledge_needed else "Task does not need durable project or product context.",
            needed=knowledge_needed,
        ),
        "capability_routing": decision_entry(
            tools,
            status=tools.status if capability_needed else "skipped",
            reason=tools.reason if capability_needed else "Product/context question does not require local tool routing.",
            needed=capability_needed,
        ),
    }


def decision_entry(
    outcome: SearchOutcome,
    *,
    needed: bool,
    status: str | None = None,
    reason: str | None = None,
    extra: dict[str, object] | None = None,
) -> dict[str, object]:
    entry: dict[str, object] = {
        "status": status or outcome.status,
        "needed": needed,
        "reason": reason or outcome.reason,
        "topic": outcome.topic,
        "topic_matched": outcome.topic_matched,
        "fallback_used": outcome.fallback_used,
        "result_count": outcome.result_count,
    }
    if extra:
        entry.update(extra)
    return entry


def external_signal_reason(*, needs_fresh_facts: bool, topic: str | None, task: str) -> str:
    if needs_fresh_facts:
        return "Task includes recent/current/change terms, so external source-backed context may affect the decision."
    if topic:
        return f"Task provided topic={topic}, so external signals may provide domain context."
    return "Task appears to be in Newswiki's agent/product context domain."


def stale_assumption_warnings(
    *,
    signals: list[PublicItem],
    knowledge: list[PublicItem],
    data_limits: list[str],
    should_query_signals: bool,
    knowledge_needed: bool,
) -> list[str]:
    warnings: list[str] = []
    if any("demo fixtures" in limit for limit in data_limits):
        warnings.append("Do not treat hosted demo signals as market evidence.")
    if should_query_signals and not signals:
        warnings.append("No external signal matched; avoid claims about current market state.")
    if knowledge_needed and not knowledge:
        warnings.append("No durable knowledge matched; avoid claiming this reflects prior project decisions.")
    return warnings


def assumptions_to_avoid(*, data_limits: list[str], signals: list[PublicItem]) -> list[str]:
    assumptions = [
        "Do not assume local/private user memory is connected unless present in private_memory.",
        "Do not assume capability routing is needed unless the task is about tools or workflows.",
    ]
    if data_limits:
        assumptions.append("Do not ignore data_limits when forming the recommendation.")
    if signals and all("demo" in item.id for item in signals):
        assumptions.append("Do not cite demo signals as real external validation.")
    return assumptions


def suggested_verification_steps(
    *,
    needs_fresh_facts: bool,
    sources: list[str],
    data_limits: list[str],
) -> list[str]:
    steps: list[str] = []
    if needs_fresh_facts and not sources:
        steps.append("Verify current facts with public sources before deciding.")
    if sources:
        steps.append("Open the cited sources and confirm dates before treating them as current.")
    if data_limits:
        steps.append("Resolve or disclose data limits before making a strong recommendation.")
    return steps
