# Newswiki Hosted MCP Contract

This contract describes the alpha hosted MCP tools backed by the public-safe export layer.

The MCP adapter must read only validated public-safe exports. If validation fails, tools return a structured error instead of serving partial data.

## Authentication

Alpha tools accept an `api_key` argument. The key must match one of the configured `NEWSWIKI_API_KEYS` values.

Invalid or missing keys return:

```json
{
  "ok": false,
  "error": "invalid API key"
}
```

## Tools

### `latest_signals`

Input:

```json
{
  "api_key": "local-key",
  "topic": "mcp",
  "days": 7,
  "limit": 10
}
```

Output:

```json
{
  "ok": true,
  "signals": []
}
```

### `search_news`

Input:

```json
{
  "api_key": "local-key",
  "query": "hosted MCP",
  "topic": "mcp",
  "days": 30,
  "limit": 10
}
```

Output:

```json
{
  "ok": true,
  "signals": []
}
```

### `search_knowledge`

Input:

```json
{
  "api_key": "local-key",
  "query": "public-safe export",
  "topic": "mcp",
  "limit": 10
}
```

Output:

```json
{
  "ok": true,
  "knowledge": []
}
```

### `recommend_agent_tools`

Input:

```json
{
  "api_key": "local-key",
  "task": "build a context pack service",
  "environment": "Codex on Windows",
  "limit": 10
}
```

Output:

```json
{
  "ok": true,
  "tools": []
}
```

### `get_topic_brief`

Input:

```json
{
  "api_key": "local-key",
  "topic": "mcp",
  "depth": "standard"
}
```

Output:

```json
{
  "ok": true,
  "topic": "mcp",
  "depth": "standard",
  "briefs": []
}
```

### `get_context_for_task`

Input:

```json
{
  "api_key": "local-key",
  "task": "design a hosted MCP service",
  "topic": "mcp",
  "token_budget": 1200
}
```

Output:

```json
{
  "ok": true,
  "task": "design a hosted MCP service",
  "answer": "",
  "signals": [],
  "knowledge": [],
  "tools": [],
  "sources": [],
  "freshness": "",
  "confidence": "low",
  "suggested_next_queries": []
}
```

## Safety Rules

- Do not return full article bodies or private notes.
- Include source URLs on public-safe items.
- Preserve freshness and confidence metadata.
- Fail closed when export validation fails.
- Keep REST and MCP behavior backed by the same service core.
