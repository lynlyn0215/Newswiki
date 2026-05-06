from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]


def parse_json_tool_result(result: Any) -> dict[str, Any]:
    if not result.content:
        raise RuntimeError("MCP tool returned no content")
    return json.loads(result.content[0].text)


async def call_server(command_args: list[str], tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    server = StdioServerParameters(command=sys.executable, args=command_args, cwd=ROOT)
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = sorted(tool.name for tool in tools.tools)
            if tool_name not in tool_names:
                raise RuntimeError(f"{tool_name} not found. Available tools: {tool_names}")
            result = await session.call_tool(tool_name, arguments)
            return {
                "tools": tool_names,
                "result": parse_json_tool_result(result),
            }


async def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    private_instance = Path(args.private_instance).expanduser().resolve()
    wiki = await call_server(
        [
            str(ROOT / "mcp/wiki/server.py"),
            "--wiki-root",
            str(private_instance),
        ],
        "wiki_past_knowledge",
        {"task": args.task, "limit": 3},
    )
    capabilities = await call_server(
        [
            str(ROOT / "mcp/capabilities/server.py"),
            "--catalog",
            str(private_instance / "capabilities.json"),
        ],
        "get_skill_chain",
        {"task": args.task, "top": 1},
    )
    newsfeed = await call_server(
        [
            str(ROOT / "mcp/newsfeed/server.py"),
            "--data-dir",
            str(private_instance / "data/news"),
        ],
        "latest_articles",
        {"limit": 3},
    )
    return {
        "ok": True,
        "private_instance": str(private_instance),
        "wiki": {
            "tools": wiki["tools"],
            "relevant_pages": len(wiki["result"].get("relevant_pages", [])),
        },
        "capabilities": {
            "tools": capabilities["tools"],
            "chains": len(capabilities["result"].get("chains", [])),
        },
        "newsfeed": {
            "tools": newsfeed["tools"],
            "articles": len(newsfeed["result"].get("articles", [])),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test Newswiki core local MCP servers through stdio.")
    parser.add_argument("--private-instance", required=True)
    parser.add_argument("--task", default="Design a weekly agent research workflow")
    args = parser.parse_args()
    try:
        report = asyncio.run(run_smoke(args))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
