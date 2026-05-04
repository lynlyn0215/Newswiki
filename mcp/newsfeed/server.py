from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


def load_json(path: Path, fallback: Any) -> Any:
    if not path.exists():
        return fallback
    return json.loads(path.read_text(encoding="utf-8"))


def make_app(data_dir: Path) -> FastMCP:
    app = FastMCP(
        "newswiki-newsfeed",
        instructions="Read-only recent news and trend context for agent startup.",
    )

    def articles() -> list[dict[str, Any]]:
        data = load_json(data_dir / "articles.example.json", {"articles": []})
        return data.get("articles", [])

    @app.tool()
    def latest_articles(category: str | None = None, limit: int = 10, wiki_only: bool = False) -> str:
        items = articles()
        if category:
            items = [item for item in items if item.get("category") == category]
        if wiki_only:
            items = [item for item in items if item.get("wiki_candidate")]
        return json.dumps({"articles": items[:limit]}, ensure_ascii=False, indent=2)

    @app.tool()
    def search_articles(query: str, limit: int = 10) -> str:
        terms = [term.lower() for term in query.split()]
        results = []
        for item in articles():
            haystack = json.dumps(item, ensure_ascii=False).lower()
            if all(term in haystack for term in terms):
                results.append(item)
        return json.dumps({"articles": results[:limit]}, ensure_ascii=False, indent=2)

    @app.tool()
    def source_health() -> str:
        return json.dumps(load_json(data_dir / "source-health.example.json", {"sources": []}), ensure_ascii=False, indent=2)

    @app.tool()
    def trend_summary() -> str:
        return json.dumps(load_json(data_dir / "trend-summary.example.json", {"headline": ""}), ensure_ascii=False, indent=2)

    @app.tool()
    def wiki_candidates(limit: int = 10) -> str:
        items = [item for item in articles() if item.get("wiki_candidate")]
        return json.dumps({"articles": items[:limit]}, ensure_ascii=False, indent=2)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", default="examples/news")
    args = parser.parse_args()
    make_app(Path(args.data_dir).resolve()).run()


if __name__ == "__main__":
    main()
