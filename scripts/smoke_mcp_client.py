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
    text = result.content[0].text
    return json.loads(text)


async def run_smoke(args: argparse.Namespace) -> dict[str, Any]:
    export_dir = Path(args.export_dir).resolve()
    server = StdioServerParameters(
        command=sys.executable,
        args=[
            "-m",
            "service.app.mcp_server",
            "--export-dir",
            str(export_dir),
            "--api-keys",
            args.api_key,
        ],
        cwd=ROOT,
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            tool_names = sorted(tool.name for tool in tools.tools)
            required = {
                "latest_signals",
                "search_news",
                "search_knowledge",
                "recommend_agent_tools",
                "get_topic_brief",
                "get_context_for_task",
            }
            missing = sorted(required - set(tool_names))
            if missing:
                raise RuntimeError(f"Missing MCP tools: {', '.join(missing)}")

            result = await session.call_tool(
                "get_context_for_task",
                {
                    "api_key": args.api_key,
                    "task": args.task,
                    "topic": args.topic,
                    "token_budget": args.token_budget,
                },
            )
            payload = parse_json_tool_result(result)
            if payload.get("ok") is not True:
                raise RuntimeError(f"MCP tool failed: {payload}")
            for key in ["signals", "knowledge", "tools", "sources"]:
                if key not in payload:
                    raise RuntimeError(f"Context pack missing {key}")
            return {
                "ok": True,
                "tools": tool_names,
                "context_pack": {
                    "task": payload["task"],
                    "signals": len(payload["signals"]),
                    "knowledge": len(payload["knowledge"]),
                    "tools": len(payload["tools"]),
                    "sources": len(payload["sources"]),
                    "confidence": payload["confidence"],
                    "freshness": payload["freshness"],
                },
            }


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test the Newswiki hosted MCP adapter through stdio.")
    parser.add_argument("--export-dir", default="examples/public")
    parser.add_argument("--api-key", default="local-key")
    parser.add_argument("--task", default="Design a hosted MCP context service")
    parser.add_argument("--topic", default="mcp")
    parser.add_argument("--token-budget", type=int, default=1200)
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
