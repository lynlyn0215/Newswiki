from __future__ import annotations

import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from service.app.connectors import ConnectorExportError, ConnectorRepository
from service.app.context_pack import ContextPackBuilder
from service.app.repository import PublicExportError, PublicExportRepository
from service.app.routes import router
from service.app.search import SearchService
from service.app.settings import Settings


app = FastAPI(title="Newswiki Hosted Alpha", version="0.1.0")
app.include_router(router)


@app.exception_handler(PublicExportError)
def public_export_error_handler(_request, exc: PublicExportError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"ok": False, "error": str(exc)})


@app.exception_handler(ConnectorExportError)
def connector_export_error_handler(_request, exc: ConnectorExportError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"ok": False, "error": str(exc)})


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "Newswiki Hosted Alpha", "status": "ok"}


def build_context_for_task(task: str, *, topic: str | None = None, token_budget: int = 1200) -> dict:
    settings = Settings.from_env()
    repository = PublicExportRepository(settings.public_export_dir)
    search = SearchService(repository)
    private_memory = []
    local_capabilities = []
    if settings.allows_user_private():
        private_memory = ConnectorRepository(settings.user_memory_dir).load("private_memory")
    if settings.allows_local_capability():
        local_capabilities = ConnectorRepository(settings.local_capability_dir).load("local_capabilities")
    builder = ContextPackBuilder(
        search,
        settings.layers,
        private_memory=private_memory,
        local_capabilities=local_capabilities,
    )
    return builder.build(task, topic=topic, token_budget=token_budget).to_dict()


def main() -> None:
    pack = build_context_for_task("design a hosted MCP context service", topic="mcp")
    print(json.dumps(pack, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
