# Newswiki Service

Service core for hosted Newswiki alpha.

This layer reads validated public-safe exports, exposes a small REST API, and builds agent-ready context packs. It is the base for the hosted MCP adapter.

Current scope:

- load validated public exports
- search signals, knowledge pages, and tool cards
- build `ContextPack` responses
- serve authenticated `/v1/*` HTTP endpoints
- expose read-only hosted MCP alpha tools
- keep an in-memory usage log for alpha testing

Out of scope for this slice:

- billing
- tenant database

## Setup

Install dependencies from the repository root:

```powershell
python -m pip install -r requirements.txt
```

Optional service-only install:

```powershell
python -m pip install -r service/requirements.txt
```

## Configuration

`NEWSWIKI_PUBLIC_EXPORT_DIR` points at the public-safe export directory. It defaults to `examples/public`.

`NEWSWIKI_API_KEYS` is a comma-separated list of accepted API keys. It defaults to `dev-newswiki-key` for local development.

`NEWSWIKI_ENABLED_LAYERS` is a comma-separated list of context source layers. It defaults to `newswiki_hosted,newswiki_curated,recommended_template`.

`NEWSWIKI_CONTEXT_MODE` is `hosted` by default. Hosted mode loads only public-safe exports. Set it to `local` before loading private connector layers.

`NEWSWIKI_USER_MEMORY_DIR` can point at a connector export directory containing `private_memory.json`.

`NEWSWIKI_LOCAL_CAPABILITY_DIR` can point at a connector export directory containing `local_capabilities.json`.

Example:

```powershell
$env:NEWSWIKI_PUBLIC_EXPORT_DIR="C:\path\to\public-export"
$env:NEWSWIKI_API_KEYS="local-key"
$env:NEWSWIKI_CONTEXT_MODE="local"
$env:NEWSWIKI_ENABLED_LAYERS="newswiki_hosted,newswiki_curated,recommended_template,user_private,local_capability"
$env:NEWSWIKI_USER_MEMORY_DIR="C:\path\to\connector-export"
$env:NEWSWIKI_LOCAL_CAPABILITY_DIR="C:\path\to\connector-export"
```

The service validates the public export before serving data. If validation fails, query endpoints return `503` instead of leaking unsafe fields.

## Run Locally

```powershell
uvicorn service.app.main:app --reload
```

Then call:

```powershell
curl.exe -H "x-api-key: local-key" http://127.0.0.1:8000/v1/signals
```

Primary endpoint:

- `POST /v1/context`

Support/debug endpoints:

- `GET /v1/health`
- `GET /v1/signals`
- `GET /v1/news/search?query=hosted%20MCP`
- `GET /v1/knowledge/search?query=public-safe`
- `POST /v1/tools/recommend`
- `GET /v1/topics/{topic}/brief`
- `GET /v1/usage`

## Context Layers

Hosted context packs label every item by source boundary:

- `newswiki_hosted`: Newswiki-hosted signals and news context.
- `newswiki_curated`: curated public knowledge and methods.
- `recommended_template`: workflow or tool templates that may need install/config.
- `user_private`: user-owned private wiki memory.
- `local_capability`: tools available on the user's own machine.

The alpha service ships with hosted/curated/template public examples. User-private wiki and local-capability layers are connector contracts, not hosted defaults. Context packs include `data_limits` so agents can see when a layer is empty, disconnected, or demo-only.

See [context-layer-contract.md](../docs/specs/context-layer-contract.md) for connector file shapes.

## Run MCP Locally

The alpha MCP adapter exposes the same read-only context tools as the REST API. For local stdio usage:

```powershell
python -m service.app.mcp_server --export-dir examples/public --api-keys local-key
```

Primary alpha tool:

- `get_context_for_task(api_key, task, topic?, token_budget?)`

Support/debug tools:

- `latest_signals(api_key, topic?, days?, limit?)`
- `search_news(api_key, query, topic?, days?, limit?)`
- `search_knowledge(api_key, query, topic?, limit?)`
- `recommend_agent_tools(api_key, task, environment?, limit?)`
- `get_topic_brief(api_key, topic, depth?)`

The `api_key` argument must match one of the configured `NEWSWIKI_API_KEYS` values. Invalid keys return a structured error instead of data.

Smoke test the MCP path:

```powershell
python scripts\smoke_mcp_client.py --api-key local-key --export-dir examples/public
```

For full setup instructions, see [docs/quickstart-hosted-alpha.md](../docs/quickstart-hosted-alpha.md) and [docs/mcp-client-setup.md](../docs/mcp-client-setup.md).
