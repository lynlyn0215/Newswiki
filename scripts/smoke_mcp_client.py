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
            tools_by_name = {tool.name: tool for tool in tools.tools}
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
            default_description = (tools_by_name["get_context_for_task"].description or "").lower()
            if "pre-plan brief" not in default_description:
                raise RuntimeError("get_context_for_task must be described as the pre-plan brief default")
            for support_tool in ["latest_signals", "search_news", "search_knowledge", "recommend_agent_tools", "get_topic_brief"]:
                description = (tools_by_name[support_tool].description or "").lower()
                if "support/debug" not in description or "prefer get_context_for_task" not in description:
                    raise RuntimeError(f"{support_tool} must be described as support/debug, not the default workflow")

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
            for key in ["brief_type", "retrieval_decision", "relevant_signals", "stale_assumption_warnings", "signals", "knowledge", "tools", "sources"]:
                if key not in payload:
                    raise RuntimeError(f"Context pack missing {key}")
            external_decision = payload["retrieval_decision"].get("external_signals", {})
            if not isinstance(external_decision, dict) or "status" not in external_decision:
                raise RuntimeError("Context pack retrieval_decision must use nested layer objects")
            return {
                "ok": True,
                "tools": tool_names,
                "context_pack": {
                    "task": payload["task"],
                    "brief_type": payload["brief_type"],
                    "needs_fresh_facts": payload["needs_fresh_facts"],
                    "external_signal_status": external_decision["status"],
                    "external_fallback_used": external_decision.get("fallback_used", False),
                    "signals": len(payload["signals"]),
                    "knowledge": len(payload["knowledge"]),
                    "tools": len(payload["tools"]),
                    "stale_assumption_warnings": len(payload["stale_assumption_warnings"]),
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
