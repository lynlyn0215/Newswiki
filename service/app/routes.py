from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from service.app.auth import require_api_key
from service.app.connectors import ConnectorRepository
from service.app.context_pack import ContextPackBuilder
from service.app.models import item_to_dict
from service.app.repository import PublicExportRepository
from service.app.search import SearchService
from service.app.settings import Settings
from service.app.usage import usage_log


router = APIRouter(prefix="/v1", dependencies=[Depends(require_api_key)])


class ContextRequest(BaseModel):
    task: str
    topic: str | None = None
    token_budget: int = 1200


class ToolRecommendRequest(BaseModel):
    task: str
    environment: str | None = None
    limit: int = 10


def public_services() -> tuple[PublicExportRepository, SearchService, Settings]:
    settings = Settings.from_env()
    repository = PublicExportRepository(settings.public_export_dir)
    search = SearchService(repository)
    return repository, search, settings


def context_builder(settings: Settings, search: SearchService) -> ContextPackBuilder:
    private_memory = []
    local_capabilities = []
    if settings.allows_user_private():
        private_memory = ConnectorRepository(settings.user_memory_dir).load("private_memory")
    if settings.allows_local_capability():
        local_capabilities = ConnectorRepository(settings.local_capability_dir).load("local_capabilities")
    return ContextPackBuilder(
        search,
        settings.layers,
        private_memory=private_memory,
        local_capabilities=local_capabilities,
    )


@router.get("/health")
def health() -> dict[str, object]:
    repository, _, _ = public_services()
    data = repository.health()
    usage_log.record(tool="health", status="ok" if data["ok"] else "degraded")
    return data


@router.get("/signals")
def latest_signals(topic: str | None = None, limit: int = Query(default=10, ge=1, le=50)) -> dict[str, object]:
    _, search, _ = public_services()
    items = search.latest_signals(topic=topic, limit=limit)
    usage_log.record(tool="latest_signals", status="ok", result_count=len(items))
    return {"signals": [item_to_dict(item) for item in items]}


@router.get("/news/search")
def search_news(query: str, topic: str | None = None, limit: int = Query(default=10, ge=1, le=50)) -> dict[str, object]:
    _, search, _ = public_services()
    items = search.search("signals", query, topic=topic, limit=limit)
    usage_log.record(tool="search_news", status="ok", result_count=len(items))
    return {"signals": [item_to_dict(item) for item in items]}


@router.get("/knowledge/search")
def search_knowledge(query: str, topic: str | None = None, limit: int = Query(default=10, ge=1, le=50)) -> dict[str, object]:
    _, search, _ = public_services()
    items = search.search("knowledge_pages", query, topic=topic, limit=limit)
    usage_log.record(tool="search_knowledge", status="ok", result_count=len(items))
    return {"knowledge": [item_to_dict(item) for item in items]}


@router.post("/tools/recommend")
def recommend_tools(request: ToolRecommendRequest) -> dict[str, object]:
    _, search, _ = public_services()
    query = request.task if not request.environment else f"{request.task} {request.environment}"
    items = search.search("tool_cards", query, limit=max(1, min(request.limit, 50)))
    usage_log.record(tool="recommend_tools", status="ok", result_count=len(items))
    return {"tools": [item_to_dict(item) for item in items]}


@router.get("/topics/{topic}/brief")
def topic_brief(topic: str, depth: str = "standard") -> dict[str, object]:
    _, search, _ = public_services()
    briefs = search.search("briefs", topic, topic=topic, limit=1)
    usage_log.record(tool="topic_brief", status="ok", result_count=len(briefs))
    return {"topic": topic, "depth": depth, "briefs": [item_to_dict(item) for item in briefs]}


@router.post("/context")
def context_for_task(request: ContextRequest) -> dict[str, object]:
    _, search, settings = public_services()
    builder = context_builder(settings, search)
    pack = builder.build(request.task, topic=request.topic, token_budget=request.token_budget).to_dict()
    result_count = len(pack["signals"]) + len(pack["knowledge"]) + len(pack["tools"])
    usage_log.record(tool="context", status="ok", result_count=result_count)
    return pack


@router.get("/usage")
def usage(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, object]:
    return {"events": usage_log.recent(limit)}
