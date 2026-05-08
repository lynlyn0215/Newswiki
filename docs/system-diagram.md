# System Diagram

Newswiki is a source-backed pre-plan context system for coding agents.

```mermaid
flowchart TB
    Task["User task"] --> Context["get_context_for_task"]

    Context --> Decision["Retrieval decision"]
    Decision --> SignalsGate["Need current external signals?"]
    Decision --> WikiGate["Need durable knowledge?"]
    Decision --> ToolsGate["Need capability routing?"]

    SignalsGate --> Signals["Public-safe external signals"]
    WikiGate --> Knowledge["Curated durable knowledge"]
    ToolsGate --> ToolCards["Recommended templates / tool cards"]

    Signals --> Brief["Pre-plan brief"]
    Knowledge --> Brief
    ToolCards --> Brief

    Brief --> Agent["Agent plan/work"]
    Brief --> Limits["Sources, freshness, confidence, data limits"]

    Sources["Sources"] --> Collect["Collectors"]
    Collect --> Process["Classify / summarize / translate"]
    Process --> PublicExport["Validated public export"]
    PublicExport --> Signals

    PrivateWiki["Private wiki memory"] --> LocalConnector["Local connector export"]
    LocalCapabilities["Local capability catalog"] --> LocalConnector
    LocalConnector --> Context

    Agent --> OptionalWriteBack["Optional local durable write-back"]
    OptionalWriteBack --> PrivateWiki

    PublicExport --> OptionalWeb["Optional Web UI"]
    OptionalWeb --> Localhost["localhost"]
    OptionalWeb --> Vercel["Vercel"]
```

## What Is Core

- `get_context_for_task`
- source-backed pre-plan brief
- retrieval decision metadata
- public-safe export validation
- freshness, confidence, and data-limit disclosure

## What Is Input Layer

- Newsfeed/current signal exports
- curated public knowledge
- private wiki connector exports in local mode
- local capability connector exports in local mode
- recommended tool/template cards

## What Is Replaceable

- source collectors
- LLM provider
- NotebookLM
- AgentSearch
- browser automation
- web UI
- Vercel

## Privacy Boundary

```text
Hosted/default mode:
  validated public-safe exports only

Local/self-hosted mode:
  optional private wiki and local capability connector exports

Private instance:
  real wiki, real sources, real news, sessions, reports, state, databases
```
