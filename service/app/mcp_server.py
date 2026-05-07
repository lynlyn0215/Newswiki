from __future__ import annotations

import argparse
import json
import secrets
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable

from mcp.server.fastmcp import FastMCP

from service.app.connectors import ConnectorExportError, ConnectorRepository
from service.app.context_pack import ContextPackBuilder
from service.app.models import PublicItem, item_to_dict
from service.app.repository import PublicExportError, PublicExportRepository
from service.app.search import SearchService
from service.app.settings import Settings
from service.app.usage import usage_log


ToolResult = dict[str, Any]


class HostedMCPService:
    def __init__(self, settings_factory: Callable[[], Settings] = Settings.from_env) -> None:
        self.settings_factory = settings_factory

    def latest_signals(
        self,
        *,
        api_key: str | None,
        topic: str | None = None,
        days: int | None = None,
        limit: int = 10,
    ) -> ToolResult:
        return self._run_tool(
            "latest_signals",
            api_key,
            lambda search, _builder: {
                "signals": [
                    item_to_dict(item)
                    for item in filter_by_days(
                        search.latest_signals(topic=topic, limit=bounded_limit(limit)),
                        days,
                    )
                ]
            },
        )

    def search_news(
        self,
        *,
        api_key: str | None,
        query: str,
        topic: str | None = None,
        days: int | None = None,
        limit: int = 10,
    ) -> ToolResult:
        return self._run_tool(
            "search_news",
            api_key,
            lambda search, _builder: {
                "signals": [
                    item_to_dict(item)
                    for item in filter_by_days(
                        search.search("signals", query, topic=topic, limit=bounded_limit(limit)),
                        days,
                    )
                ]
            },
        )

    def search_knowledge(
        self,
        *,
        api_key: str | None,
        query: str,
        topic: str | None = None,
        limit: int = 10,
    ) -> ToolResult:
        return self._run_tool(
            "search_knowledge",
            api_key,
            lambda search, _builder: {
                "knowledge": [
                    item_to_dict(item)
                    for item in search.search("knowledge_pages", query, topic=topic, limit=bounded_limit(limit))
                ]
            },
        )

    def recommend_agent_tools(
        self,
        *,
        api_key: str | None,
        task: str,
        environment: str | None = None,
        limit: int = 10,
    ) -> ToolResult:
        query = task if not environment else f"{task} {environment}"
        return self._run_tool(
            "recommend_agent_tools",
            api_key,
            lambda search, _builder: {
                "tools": [
                    item_to_dict(item)
                    for item in search.search("tool_cards", query, limit=bounded_limit(limit))
                ]
            },
        )

    def get_topic_brief(
        self,
        *,
        api_key: str | None,
        topic: str,
        depth: str = "standard",
    ) -> ToolResult:
        return self._run_tool(
            "get_topic_brief",
            api_key,
            lambda search, _builder: {
                "topic": topic,
                "depth": depth,
                "briefs": [
                    item_to_dict(item)
                    for item in search.search("briefs", topic, topic=topic, limit=1)
                ],
            },
        )

    def get_context_for_task(
        self,
        *,
        api_key: str | None,
        task: str,
        topic: str | None = None,
        token_budget: int = 1200,
    ) -> ToolResult:
        return self._run_tool(
            "get_context_for_task",
            api_key,
            lambda _search, builder: builder.build(task, topic=topic, token_budget=token_budget).to_dict(),
        )

    def _run_tool(
        self,
        tool: str,
        api_key: str | None,
        handler: Callable[[SearchService, ContextPackBuilder], ToolResult],
    ) -> ToolResult:
        if not self._authorized(api_key):
            usage_log.record(tool=tool, status="unauthorized")
            return {"ok": False, "error": "invalid API key"}
        try:
            settings = self.settings_factory()
            repository = PublicExportRepository(settings.public_export_dir)
            search = SearchService(repository)
            private_memory = ConnectorRepository(settings.user_memory_dir).load("private_memory")
            local_capabilities = ConnectorRepository(settings.local_capability_dir).load("local_capabilities")
            builder = ContextPackBuilder(
                search,
                settings.layers,
                private_memory=private_memory,
                local_capabilities=local_capabilities,
            )
            result = handler(search, builder)
        except (ConnectorExportError, PublicExportError) as exc:
            usage_log.record(tool=tool, status="degraded")
            return {"ok": False, "error": str(exc)}
        result_count = count_result_items(result)
        usage_log.record(tool=tool, status="ok", result_count=result_count)
        return {"ok": True, **result}

    def _authorized(self, api_key: str | None) -> bool:
        if not api_key:
            return False
        return any(secrets.compare_digest(api_key, allowed) for allowed in self.settings_factory().api_keys)


def bounded_limit(limit: int) -> int:
    return max(1, min(limit, 50))


def filter_by_days(items: list[PublicItem], days: int | None) -> list[PublicItem]:
    if days is None:
        return items
    cutoff = datetime.now(timezone.utc) - timedelta(days=max(0, days))
    filtered: list[PublicItem] = []
    for item in items:
        updated_at = parse_updated_at(item.updated_at)
        if updated_at is None or updated_at >= cutoff:
            filtered.append(item)
    return filtered


def parse_updated_at(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def count_result_items(result: ToolResult) -> int:
    total = 0
    for value in result.values():
        if isinstance(value, list):
            total += len(value)
    return total


def dumps(data: ToolResult) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def make_app() -> FastMCP:
    service = HostedMCPService()
    app = FastMCP(
        "newswiki-hosted-alpha",
        instructions="Read-only hosted Newswiki context tools for agent startup and task planning.",
    )

    @app.tool()
    def latest_signals(api_key: str, topic: str | None = None, days: int | None = None, limit: int = 10) -> str:
        return dumps(service.latest_signals(api_key=api_key, topic=topic, days=days, limit=limit))

    @app.tool()
    def search_news(
        api_key: str,
        query: str,
        topic: str | None = None,
        days: int | None = None,
        limit: int = 10,
    ) -> str:
        return dumps(service.search_news(api_key=api_key, query=query, topic=topic, days=days, limit=limit))

    @app.tool()
    def search_knowledge(api_key: str, query: str, topic: str | None = None, limit: int = 10) -> str:
        return dumps(service.search_knowledge(api_key=api_key, query=query, topic=topic, limit=limit))

    @app.tool()
    def recommend_agent_tools(
        api_key: str,
        task: str,
        environment: str | None = None,
        limit: int = 10,
    ) -> str:
        return dumps(service.recommend_agent_tools(api_key=api_key, task=task, environment=environment, limit=limit))

    @app.tool()
    def get_topic_brief(api_key: str, topic: str, depth: str = "standard") -> str:
        return dumps(service.get_topic_brief(api_key=api_key, topic=topic, depth=depth))

    @app.tool()
    def get_context_for_task(
        api_key: str,
        task: str,
        topic: str | None = None,
        token_budget: int = 1200,
    ) -> str:
        return dumps(service.get_context_for_task(api_key=api_key, task=task, topic=topic, token_budget=token_budget))

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--export-dir")
    parser.add_argument("--api-keys")
    args = parser.parse_args()
    if args.export_dir:
        import os

        os.environ["NEWSWIKI_PUBLIC_EXPORT_DIR"] = str(Path(args.export_dir).resolve())
    if args.api_keys:
        import os

        os.environ["NEWSWIKI_API_KEYS"] = args.api_keys
    make_app().run()


if __name__ == "__main__":
    main()
