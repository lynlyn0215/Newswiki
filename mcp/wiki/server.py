from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP


def make_app(wiki_root: Path) -> FastMCP:
    wiki_dir = wiki_root / "wiki"
    control_files = {
        "learning": wiki_dir / "learnings.md",
        "pattern": wiki_dir / "patterns.md",
        "decision": wiki_dir / "decisions.md",
        "gap": wiki_dir / "gaps.md",
    }

    app = FastMCP(
        "newswiki-wiki",
        instructions="Private Markdown wiki memory for agent startup context.",
    )

    def pages() -> list[Path]:
        if not wiki_dir.exists():
            return []
        return sorted(p for p in wiki_dir.rglob("*.md") if p.is_file())

    def read(path: Path) -> str:
        return path.read_text(encoding="utf-8", errors="ignore")

    @app.tool()
    def wiki_search(query: str, limit: int = 5) -> str:
        terms = [t.lower() for t in query.split() if t.strip()]
        scored: list[tuple[int, Path, str]] = []
        for path in pages():
            text = read(path)
            lower = text.lower()
            score = sum(lower.count(term) for term in terms)
            if score:
                excerpt = " ".join(text.split())[:500]
                scored.append((score, path, excerpt))
        scored.sort(key=lambda item: item[0], reverse=True)
        data = [
            {"path": str(path.relative_to(wiki_root)), "score": score, "excerpt": excerpt}
            for score, path, excerpt in scored[:limit]
        ]
        return json.dumps({"results": data}, ensure_ascii=False, indent=2)

    @app.tool()
    def wiki_past_knowledge(task: str, limit: int = 5) -> str:
        search = json.loads(wiki_search(task, limit))
        packet: dict[str, Any] = {
            "task": task,
            "relevant_pages": search["results"],
            "prior_decisions": read(control_files["decision"])[:1200] if control_files["decision"].exists() else "",
            "reusable_patterns": read(control_files["pattern"])[:1200] if control_files["pattern"].exists() else "",
            "known_pitfalls": read(control_files["learning"])[:1200] if control_files["learning"].exists() else "",
            "gaps": read(control_files["gap"])[:1200] if control_files["gap"].exists() else "",
            "required_output": [
                "Relevant pages",
                "Prior decisions",
                "Reusable patterns",
                "Known pitfalls",
                "Gaps / unknowns",
                "How this changes the plan",
            ],
        }
        return json.dumps(packet, ensure_ascii=False, indent=2)

    @app.tool()
    def wiki_write_learning(kind: str, title: str, content: str, links: list[str] | None = None) -> str:
        if kind not in control_files:
            return json.dumps({"ok": False, "error": f"kind must be one of {sorted(control_files)}"})
        path = control_files[kind]
        path.parent.mkdir(parents=True, exist_ok=True)
        links = links or []
        entry = [
            "",
            f"## {title}",
            "",
            content.strip(),
            "",
        ]
        if links:
            entry.extend(["Links:", *[f"- {link}" for link in links], ""])
        with path.open("a", encoding="utf-8") as handle:
            handle.write("\n".join(entry))
        return json.dumps({"ok": True, "path": str(path.relative_to(wiki_root))}, ensure_ascii=False)

    @app.tool()
    def wiki_recent_changes(days: int = 7, limit: int = 10) -> str:
        cutoff = datetime.now().timestamp() - days * 86400
        changed = [
            {
                "path": str(path.relative_to(wiki_root)),
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(timespec="seconds"),
            }
            for path in pages()
            if path.stat().st_mtime >= cutoff
        ]
        changed.sort(key=lambda item: item["modified"], reverse=True)
        return json.dumps({"results": changed[:limit]}, ensure_ascii=False, indent=2)

    return app


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wiki-root", default=".")
    args = parser.parse_args()
    app = make_app(Path(args.wiki_root).resolve())
    app.run()


if __name__ == "__main__":
    main()
