# Newswiki Hosted MCP Contract

This contract describes the alpha hosted MCP tools backed by the public-safe export layer.

The MCP adapter must read only validated public-safe exports. If validation fails, tools return a structured error instead of serving partial data.

Hosted mode is public-only. Private memory and local capability connector layers are loaded only when `NEWSWIKI_CONTEXT_MODE=local` is explicitly set for a self-hosted deployment.

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

This is the flagship v1 tool. It should return an agent pre-plan brief, not raw search results.

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
  "brief_type": "pre_plan",
  "needs_fresh_facts": false,
  "retrieval_decision": {
    "external_signals": {
      "status": "queried",
      "needed": true,
      "reason": "Task provided topic=mcp, so external signals may provide domain context.",
      "topic": "mcp",
      "topic_matched": true,
      "fallback_used": false,
      "result_count": 3,
      "needs_fresh_facts": false
    },
    "durable_knowledge": {
      "status": "queried",
      "needed": true,
      "reason": "Task may benefit from durable Newswiki product or architecture context.",
      "topic": "mcp",
      "topic_matched": true,
      "fallback_used": false,
      "result_count": 2
    },
    "capability_routing": {
      "status": "skipped",
      "needed": false,
      "reason": "Product/context question does not require local tool routing.",
      "topic": "mcp",
      "topic_matched": false,
      "fallback_used": false,
      "result_count": 0
    }
  },
  "answer": "Short pre-plan summary.",
  "relevant_signals": [],
  "relevant_knowledge": [],
  "stale_assumption_warnings": [],
  "what_not_to_assume": [],
  "suggested_verification_steps": [],
  "data_limits": [],
  "sources": [],
  "freshness": "",
  "confidence": "low",
  "suggested_next_queries": [],
  "signals": [],
  "knowledge": [],
  "tools": []
}
```

Compatibility note: `signals`, `knowledge`, and `tools` may remain as legacy aliases while clients migrate to the pre-plan brief fields.

`tools` should be empty unless the task asks to choose, install, configure, or route tools/workflows. Product strategy mentions of "MCP" or "skill" are not by themselves capability-routing requests.

## Safety Rules

- Do not return full article bodies or private notes.
- Include source URLs on public-safe items.
- Preserve freshness and confidence metadata.
- Fail closed when export validation fails.
- Keep REST and MCP behavior backed by the same service core.
- Do not load private connector layers in hosted mode.
