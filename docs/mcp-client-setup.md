# MCP Client Setup

Newswiki hosted alpha runs as a stdio MCP server for local testing.

## Command

From the repository root:

```powershell
python -m service.app.mcp_server --export-dir examples/public --api-keys local-key
```

This starts the server and waits for an MCP client over stdio.

## Detect Your Client First

Do not assume every MCP client is Codex.

Before editing config, identify the user's actual client:

- Codex may use a `~/.codex/config.toml` style config.
- Claude Code may use its own MCP configuration command or config location.
- Claude Desktop and other MCP clients may use JSON-style config.

If you are an AI agent doing setup, state which client/config file you found before editing anything. Ask before changing external config files.

## Generic Client Config

Use absolute paths in real client configs.

```json
{
  "mcpServers": {
    "newswiki-hosted-alpha": {
      "command": "python",
      "args": [
        "-m",
        "service.app.mcp_server",
        "--export-dir",
        "C:\\Users\\YOUR_USER\\path\\to\\Newswiki\\examples\\public",
        "--api-keys",
        "local-key"
      ],
      "cwd": "C:\\Users\\YOUR_USER\\path\\to\\Newswiki"
    }
  }
}
```

## TOML-Style Client Example

```toml
[mcp_servers.newswiki-hosted-alpha]
command = "python"
args = [
  "-m",
  "service.app.mcp_server",
  "--export-dir",
  "C:\\Users\\YOUR_USER\\path\\to\\Newswiki\\examples\\public",
  "--api-keys",
  "local-key",
]
cwd = "C:\\Users\\YOUR_USER\\path\\to\\Newswiki"
```

## Tool Calls

The alpha tools require an `api_key` argument:

```json
{
  "api_key": "local-key",
  "task": "Design a hosted MCP context service",
  "topic": "mcp",
  "token_budget": 1200
}
```

Call:

```text
get_context_for_task
```

Use `get_context_for_task` as the default entry point for non-trivial tasks. The other tools are support/debug surfaces for direct inspection of one input layer.

Expected response:

```json
{
  "ok": true,
  "task": "Design a hosted MCP context service",
  "brief_type": "pre_plan",
  "answer": "...",
  "retrieval_decision": {
    "external_signals": {"status": "queried"},
    "durable_knowledge": {"status": "queried"},
    "capability_routing": {"status": "skipped"}
  },
  "signals": [{"title": "..."}],
  "knowledge": [{"title": "..."}],
  "tools": [],
  "sources": ["https://..."],
  "freshness": "...",
  "confidence": "medium",
  "data_limits": ["..."],
  "suggested_next_queries": []
}
```

## Troubleshooting

- Run `python scripts\smoke_mcp_client.py --api-key local-key` before configuring a real client.
- Use absolute paths if the client cannot find `examples/public`.
- Keep `cwd` set to the repository root so Python can import `service.app.mcp_server`.
- If tools return `invalid API key`, confirm the tool argument matches `--api-keys`.
- If tools return `public export validation failed`, run `python scripts\validate_public_export.py examples\public`.
