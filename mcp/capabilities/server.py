from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from mcp.server.fastmcp import FastMCP

STOPWORDS = {
    "about",
    "after",
    "and",
    "are",
    "before",
    "for",
    "from",
    "how",
    "into",
    "the",
    "this",
    "that",
    "with",
}


def load_catalog(path: Path) -> dict:
    if not path.exists():
        return {"capabilities": [], "chains": []}
    return json.loads(path.read_text(encoding="utf-8"))


def task_terms(task: str) -> set[str]:
    return {term for term in re.findall(r"[a-z0-9_-]{3,}", task.lower()) if term not in STOPWORDS}


def score_items(items: list[dict], task: str, keys: list[str]) -> list[dict]:
    terms = task_terms(task)
    scored = []
    for item in items:
        haystack = " ".join(str(item.get(key, "")) for key in keys).lower()
        score = sum(1 for term in terms if term in haystack)
        if score:
            scored.append((score, item))
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored]


def make_app(catalog_path: Path) -> FastMCP:
    app = FastMCP(
        "newswiki-capabilities",
        instructions="Recommend local agent capabilities before work starts.",
    )

    @app.tool()
    def list_capabilities(limit: int = 50) -> str:
        catalog = load_catalog(catalog_path)
        return json.dumps({"capabilities": catalog.get("capabilities", [])[:limit]}, ensure_ascii=False, indent=2)

    @app.tool()
    def recommend_capabilities(task: str, top: int = 5) -> str:
        catalog = load_catalog(catalog_path)
        results = score_items(catalog.get("capabilities", []), task, ["id", "name", "description", "tags"])
        return json.dumps({"task": task, "results": results[:top]}, ensure_ascii=False, indent=2)

    @app.tool()
    def get_skill_chain(task: str, top: int = 1) -> str:
        catalog = load_catalog(catalog_path)
        chains = score_items(catalog.get("chains", []), task, ["id", "name", "intents", "steps"])
        return json.dumps({"task": task, "chains": chains[:top]}, ensure_ascii=False, indent=2)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="examples/capabilities.example.json")
    args = parser.parse_args()
    make_app(Path(args.catalog).resolve()).run()


if __name__ == "__main__":
    main()
