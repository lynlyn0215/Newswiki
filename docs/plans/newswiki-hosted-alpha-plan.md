---
title: Newswiki Hosted Alpha Plan
status: active
created: 2026-05-05
---

# Newswiki Hosted Alpha Plan

## Problem Frame

Newswiki has strong local assets: a newsfeed pipeline, Knowledge Wiki, Capability Graph, MCP tools, and a public template. To sell this as a service, the product must stop looking like scattered scripts and start behaving like an agent context platform.

The first commercial target is not a general news product. It is a hosted, read-only context layer for AI agent builders:

```text
Recent signals + durable knowledge + tool routing -> agent-ready context
```

Honcho is the reference pattern: package agent context as service primitives, background derivations, API/MCP endpoints, SDK/docs, and a dashboard. Newswiki should borrow that product shape while keeping a different domain: external-world intelligence and tool route guidance, not user conversation memory.

## Product Positioning

Newswiki is an Agent Intelligence Context Layer.

It lets an agent ask:

- What changed recently in AI agents, coding agents, MCP, and devtools?
- What durable knowledge exists about this topic?
- Which tools, skills, MCPs, or workflows should I consider?
- What concise context pack should I use before starting this task?

Avoid positioning:

- "news reader"
- "RSS summarizer"
- "personal wiki hosting"
- "MCP server marketplace"

## Scope

### Alpha In Scope

- Public-safe read-only hosted MCP.
- REST API parity for the same tools.
- Simple web dashboard/playground.
- API key auth and per-user usage logging.
- Public-safe export layer from existing internal systems.
- Narrow domain: AI agents, coding agents, MCP, devtools.
- Context-pack endpoint inspired by Honcho context retrieval.

### Out Of Scope

- User write-back into hosted knowledge base.
- Private customer knowledge ingestion.
- Billing automation.
- Team roles.
- Full-source article redistribution.
- General search engine replacement.
- Migrating all current local projects into one monorepo.

## Architecture Decision

Do not reorganize existing local projects first.

Create a thin service boundary:

```text
Internal local systems
  -> public-safe export
  -> newswiki-service
  -> hosted MCP / REST / UI
```

Rationale:

- Existing local systems work.
- Large cleanup risks breaking the pipeline.
- Commercial risk is data boundary and service packaging, not folder aesthetics.
- A thin service lets us test demand quickly.

## Honcho-Inspired Primitives

Newswiki service should expose stable primitives:

| Primitive | Meaning |
| --- | --- |
| `Tenant` | Customer or workspace. |
| `ApiKey` | Auth credential and quota owner. |
| `Topic` | Curated domain such as `mcp`, `coding-agents`, `ai-devtools`. |
| `Signal` | Time-sensitive news or market movement. |
| `KnowledgePage` | Durable distilled knowledge. |
| `ToolCard` | Public tool, skill, MCP, repo, or workflow recommendation. |
| `Brief` | Daily/weekly synthesis. |
| `QuerySession` | One user/agent query event. |
| `ContextPack` | Task-specific bundle of signals, knowledge, and tools. |

## Public-Safe Export Contract

Existing systems should export only sanitized data into `exports/public/`.

### Files

- `exports/public/signals.json`
- `exports/public/knowledge_pages.json`
- `exports/public/tool_cards.json`
- `exports/public/briefs.json`
- `exports/public/topics.json`

### Required Metadata

Every exported item must include:

- `id`
- `title`
- `summary`
- `source_urls`
- `topics`
- `updated_at`
- `freshness`
- `confidence`
- `public_safe: true`

### Forbidden Fields

- local absolute paths
- private source notes
- raw NotebookLM session data
- full article bodies
- private wiki control notes
- private workflow references
- API keys or tokens
- unpublished personal opinions not intended for customers

## Hosted MCP Tools

Alpha MCP tools:

```text
latest_signals(topic?, days?, limit?)
search_news(query, topic?, days?, limit?)
search_knowledge(query, topic?, limit?)
recommend_agent_tools(task, environment?, limit?)
get_topic_brief(topic, depth?)
get_context_for_task(task, topic?, token_budget?)
```

`get_context_for_task` is the flagship tool. It should return a context pack, not raw search results.

### Context Pack Shape

```json
{
  "task": "...",
  "answer": "...",
  "signals": [],
  "knowledge": [],
  "tools": [],
  "sources": [],
  "freshness": "2026-05-05T00:00:00Z",
  "confidence": "medium",
  "suggested_next_queries": []
}
```

## REST API

REST should mirror MCP tools:

- `GET /v1/signals`
- `GET /v1/news/search`
- `GET /v1/knowledge/search`
- `POST /v1/tools/recommend`
- `GET /v1/topics/{topic}/brief`
- `POST /v1/context`

This keeps the product usable outside MCP clients.

## Web UI

Alpha UI should be a product control surface, not a marketing page.

Pages:

- `/onboarding`: choose topics, language, use case, agent client.
- `/dashboard`: today's signals, freshness, quota.
- `/topics`: subscriptions and filters.
- `/playground`: test a task and inspect the context pack.
- `/mcp`: endpoint, API key, copyable config snippets.
- `/knowledge`: search public-safe knowledge.
- `/tools`: browse tool cards and recommendations.

Most important page:

```text
Playground -> "What would my agent receive for this task?"
```

## Background Workers

Move expensive work out of request time:

- collect raw signals
- summarize and translate
- classify topics
- derive trend briefs
- update tool cards
- generate topic representations
- run public-safe export validation
- refresh search indexes

MCP requests should read precomputed data.

## Topic Representations

Borrow Honcho's representation idea.

Create generated summaries for:

- topic state
- important players
- recent changes
- opportunities
- risks
- canonical tools
- unresolved questions

Examples:

- `topic_representation("MCP")`
- `topic_representation("coding agents")`
- `tool_representation("Claude Code")`

These become high-value inputs to `get_context_for_task`.

## Data Storage

Alpha can start simple:

- Postgres for tenants, API keys, query logs, usage events.
- Static JSON or Postgres tables for public-safe exports.
- Full-text search via Postgres FTS first.
- Vector search later only if lexical quality is insufficient.

Avoid adding vector infra before the first customer feedback loop.

## Auth And Usage

Alpha requirements:

- API key per tenant.
- Hash API keys at rest.
- Rate limit per key.
- Log each query with tool name, latency, result counts, and status.
- Do not log raw customer secrets.
- Return useful 401/429 errors.

## Safety And Compliance

Rules:

- Never return full copyrighted article bodies.
- Always include source links for news-derived claims.
- Mark freshness and confidence.
- Keep internal private wiki separate from public-safe knowledge.
- Run export validation before deployment.
- Maintain a denylist for private terms, local paths, and internal-only pages.

## Implementation Units

### Unit 1: Public-Safe Export Spec

Files:

- `docs/specs/public-export-schema.md`
- `examples/public/signals.example.json`
- `examples/public/knowledge_pages.example.json`
- `examples/public/tool_cards.example.json`

Tests:

- `tests/test_public_export_schema.py`

Scenarios:

- Accept valid public-safe item.
- Reject local path.
- Reject missing source URL.
- Reject `public_safe: false`.
- Reject full-body fields.

### Unit 2: Export Validator

Files:

- `scripts/validate_public_export.py`
- `tests/test_validate_public_export.py`

Scenarios:

- Validate all example exports.
- Fail on private path.
- Fail on token-like string.
- Fail on unexpected forbidden field.
- Print machine-readable report.

### Unit 3: Service Skeleton

Files:

- `service/README.md`
- `service/app/main.py`
- `service/app/models.py`
- `service/app/settings.py`
- `service/requirements.txt`

Tests:

- `service/tests/test_health.py`

Scenarios:

- Health endpoint returns ok.
- Settings load from env.
- Missing data directory returns degraded state.

### Unit 4: Read-Only Query Layer

Files:

- `service/app/repository.py`
- `service/app/search.py`
- `service/tests/test_search.py`

Scenarios:

- Search news by query.
- Filter by topic.
- Enforce limit.
- Return freshness metadata.

### Unit 5: Context Pack Builder

Files:

- `service/app/context_pack.py`
- `service/tests/test_context_pack.py`

Scenarios:

- Combines signals, knowledge, and tool cards.
- Respects token budget approximately.
- Includes source links.
- Returns confidence and suggested next queries.

### Unit 6: Hosted MCP Adapter

Files:

- `service/app/mcp_server.py`
- `service/tests/test_mcp_contract.py`

Scenarios:

- Exposes six alpha tools.
- Tool output matches context pack schema.
- Handles empty results.
- Rejects unauthenticated calls.

### Unit 7: REST API Adapter

Files:

- `service/app/routes.py`
- `service/tests/test_routes.py`

Scenarios:

- REST mirrors MCP behavior.
- API key required.
- 429 returned after quota.
- Errors are structured.

### Unit 8: Alpha UI

Files:

- `app/`
- `app/playground/`
- `app/mcp/`
- `app/topics/`

Tests:

- `tests/ui/test_playground_smoke.py`

Scenarios:

- User can copy MCP config.
- User can submit a task and see a context pack.
- Empty state explains missing topic data.

## Sequencing

1. Write public-safe export schema.
2. Build validator.
3. Produce first sanitized export from current local system.
4. Build service skeleton.
5. Implement read-only search and context pack.
6. Add hosted MCP adapter.
7. Add API key auth and usage logging.
8. Add minimal playground UI.
9. Test with one real agent client.
10. Invite 3-5 design partners.

## Alpha Success Criteria

- A user can connect an agent to hosted Newswiki with an API key.
- `get_context_for_task` returns useful context for at least 10 real AI-agent/devtool tasks.
- Responses include source links, freshness, confidence.
- No private local data appears in service responses.
- Query latency is acceptable for interactive agent use.
- At least 3 design partners use it repeatedly over one week.

## Risks

- Content leakage from private wiki.
- Copyright issues from over-returning article text.
- Tool recommendations too generic.
- Too much infra before demand is proven.
- MCP client compatibility differences.
- Query quality depends on public-safe export quality.

## Open Questions

- Should the first hosted service live inside this repo or a new private `newswiki-service` repo?
- Which auth provider should alpha use?
- Which MCP transport should be primary for remote clients?
- How much of the current wiki is safe to export?
- Should alpha support Chinese-first users only, or bilingual from day one?

## Recommended First Step

Start with Unit 1 and Unit 2.

Do not build UI or hosted MCP until public-safe export is strict. The export contract is the product boundary.
