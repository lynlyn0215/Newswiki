from __future__ import annotations

import argparse
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP


def load_catalog(path: Path) -> dict:
    if not path.exists():
        return {"capabilities": [], "chains": []}
    return json.loads(path.read_text(encoding="utf-8"))


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
        terms = {term.lower() for term in task.split()}
        scored = []
        for item in catalog.get("capabilities", []):
            haystack = " ".join(str(item.get(key, "")) for key in ["id", "name", "description", "tags"]).lower()
            score = sum(1 for term in terms if term in haystack)
            if score:
                scored.append((score, item))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return json.dumps({"task": task, "results": [item for _, item in scored[:top]]}, ensure_ascii=False, indent=2)

    @app.tool()
    def get_skill_chain(task: str, top: int = 1) -> str:
        catalog = load_catalog(catalog_path)
        terms = {term.lower() for term in task.split()}
        scored = []
        for chain in catalog.get("chains", []):
            haystack = " ".join(str(chain.get(key, "")) for key in ["id", "name", "intents", "steps"]).lower()
            score = sum(1 for term in terms if term in haystack)
            if score:
                scored.append((score, chain))
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return json.dumps({"task": task, "chains": [chain for _, chain in scored[:top]]}, ensure_ascii=False, indent=2)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--catalog", default="examples/capabilities.example.json")
    args = parser.parse_args()
    make_app(Path(args.catalog).resolve()).run()


if __name__ == "__main__":
    main()
