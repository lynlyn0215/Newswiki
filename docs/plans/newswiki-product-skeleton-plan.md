---
title: Newswiki Product Skeleton Plan
status: draft
created: 2026-05-06
---

# Newswiki Product Skeleton Plan

## Product Frame

Newswiki is an MCP-first context layer for AI agents.

It should not be positioned as only a news feed, a personal wiki clone, or a generic skill registry. The product value is routing the right context into an agent before work starts:

```text
user private memory
+ Newswiki hosted signals
+ curated external knowledge
+ optional capability routing
= task-ready context pack
```

## Core Boundary

Newswiki must clearly separate provider-owned context from user-owned context.

| Layer | Owner | Default location | Product role |
|---|---|---|---|
| News / signals | Newswiki | Hosted | High-quality current context supplied by the service |
| User private wiki | User | Local or private tenant | The user's durable project memory and decisions |
| Curated wiki | Newswiki | Hosted | Optional public knowledge and methodology layer |
| User capabilities | User | Local machine | Tools, skills, MCPs, CLIs the user's agent can actually call |
| Curated capability templates | Newswiki | Hosted | Recommended workflows and installable patterns |

## Product Principle

Do not make the user's agent depend on the founder's private wiki.

The founder wiki can be a source for creating curated public knowledge packs, but it should not be exposed wholesale as the default Wiki MCP backend.

Reasons:

- private data and personal judgment boundaries are hard to guarantee
- uneven wiki quality would create uneven product quality
- users need their own project memory more than someone else's raw notes
- curated packs can improve over time without leaking private context

## MCP Product Shape

The flagship hosted tool should return a structured context pack.

Example:

```json
{
  "task": "...",
  "private_memory": [],
  "hosted_signals": [],
  "curated_knowledge": [],
  "local_capabilities": [],
  "recommended_templates": [],
  "confidence": "medium",
  "data_limits": []
}
```

Each item should carry provenance:

- `source_type`: `user_private`, `newswiki_hosted`, `newswiki_curated`, `local_capability`, `recommended_template`
- `freshness`
- `confidence`
- `privacy_level`
- `actionability`

## Three Core MCPs

### 1. Newsfeed MCP

Default: Newswiki hosted.

Purpose:

- current AI/product/devtool signals
- trend summaries
- source health
- wiki candidates
- task-specific recent context

Quality bar:

- demo fixtures must never be presented as market evidence
- sources need freshness, reliability, and coverage metadata
- summaries must separate fact, interpretation, and recommendation

### 2. Wiki MCP

Default: user's own wiki.

Optional add-ons:

- Newswiki curated public wiki
- team shared wiki
- user-approved hosted/private tenant wiki

Purpose:

- retrieve durable project memory
- retrieve prior decisions and known pitfalls
- write back reusable learnings

Quality bar:

- empty fresh wiki is a valid state and must be disclosed
- raw founder wiki is not the product
- curated wiki pages need quality review before hosted exposure

### 3. Capability MCP

Default: on demand.

It should merge:

- user's local skills, tools, MCPs, CLIs, automations
- Newswiki recommended workflow templates
- hosted capabilities that Newswiki can perform

Return categories:

- `available_local`: usable now on the user's machine
- `recommended_template`: useful but may need install/config
- `hosted_available`: can be provided by Newswiki service

Quality bar:

- do not recommend unavailable local tools as callable
- generic startup chains are weak signals, not task guidance
- product/research tasks should match product discovery and research capabilities
- skip Capability MCP when tool/workflow routing does not matter

## First Product Skeleton

Build the product around one user-visible promise:

> Ask Newswiki what your agent should know before it starts.

Minimum product surfaces:

1. Hosted MCP endpoint returning task-ready context packs.
2. Local connector that reads user private wiki and local capabilities.
3. Hosted news/signal layer maintained by Newswiki.
4. Curated template layer for workflows and methods.
5. Web UI for user preferences and data-source choices.

## Web UI Scope

The UI should configure context routing, not replace the agent.

Required controls:

- choose topics for hosted signals
- choose whether to include curated wiki packs
- connect or point to private wiki
- scan or import local capabilities
- select allowed hosted capabilities
- view recent context packs and source provenance
- privacy switches for each layer

## Near-Term Build Order

1. Define the context-pack schema and provenance fields. Done in `service/app/models.py` and `service/app/context_pack.py`.
2. Update docs to explain provider vs user context boundaries. Done in `service/README.md`.
3. Add service config for enabled layers. Done through `NEWSWIKI_ENABLED_LAYERS`.
4. Add a local connector contract for private wiki and local capabilities. Done in `docs/specs/context-layer-contract.md`, `service/app/connectors.py`, and `examples/connectors/`.
5. Make hosted MCP compose context from enabled layers. Done in `ContextPackBuilder`, REST, and hosted MCP service.
6. Add product tests for empty wiki, demo news, and missing capabilities. Done in `service/tests/test_context_pack.py`, `service/tests/test_connectors.py`, and `service/tests/test_mcp_contract.py`.
7. Add a simple web UI for layer selection and topic preferences. Done in `web/`.

## Deferrable Work

These are important, but not needed before product skeleton:

- large-scale news quality optimization
- full founder-wiki curation
- advanced personalization ranking
- multi-user billing
- team admin controls
- real-time push notifications

## Open Questions

- Should hosted Newswiki store user private wiki data, or only connect to local/private tenant stores?
- What is the first paid topic pack: AI agents, AI products, devtools, markets, or creator economy?
- Should hosted capability templates be installable packages, documentation, or callable hosted tools?
- How much context routing should happen in the client versus the hosted MCP server?

## Success Criteria

Product skeleton is ready when:

- an agent can request a context pack for a real task
- the pack labels provider/user/curated/local sources clearly
- empty or demo layers are disclosed instead of hidden
- local capabilities are not confused with recommended templates
- the user can configure which layers are active
- tests prove privacy and provenance boundaries
