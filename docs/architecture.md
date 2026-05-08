# Architecture

Newswiki is a source-backed pre-plan context system for coding agents.

The v1 core loop:

```text
User task
  -> get_context_for_task
      -> decide whether current external signals are needed
      -> retrieve durable knowledge when project/domain context matters
      -> retrieve capability routing only for setup/tool/workflow tasks
      -> return a pre-plan brief with sources, freshness, confidence, data limits, and retrieval decisions
  -> Agent plan/work
```

## Core Service Layer

The hosted alpha service reads only validated public-safe exports by default.

Primary surface:

- `get_context_for_task(task, topic?, token_budget?)`

Support/debug retrieval surfaces may remain available:

- latest signals
- news search
- knowledge search
- tool recommendations
- topic brief

These support tools are not the v1 success surface. V1 is judged by whether the pre-plan brief improves agent answers.

## Input Layers

### External Signals

Signals are source-backed public context about AI agents, MCP, devtools, model releases, and related platform changes.

Every real signal should separate:

- source claim
- Newswiki interpretation
- decision impact
- entities
- freshness/staleness
- data limits

### Durable Knowledge

Curated knowledge can include public product contracts, architecture patterns, and evaluation gates.

Internal Newswiki docs are durable context. They are not external market evidence.

Private wiki memory is available only in local/self-hosted mode.

### Capability Routing

Capability routing is conditional. It should run only when the task asks to choose, install, configure, or route tools, CLIs, MCP servers, skills, or workflows.

A product-strategy task mentioning "MCP" or "skill" is not automatically a capability-routing task.

## Hosted vs Local Mode

Default hosted mode:

```text
NEWSWIKI_CONTEXT_MODE=hosted
```

Hosted mode loads public exports only.

Local/self-hosted mode:

```text
NEWSWIKI_CONTEXT_MODE=local
```

Local mode may load optional connector exports such as private memory and local capability catalogs.

## Deferred

Write-back, private hosted tenant storage, billing, admin UI, and cross-agent adapter generation are deferred until the pre-plan brief proves value through evaluation.
