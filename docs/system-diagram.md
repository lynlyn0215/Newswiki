# System Diagram

Newswiki is a local-first agent information system.

```mermaid
flowchart TB
    Task["User task"] --> Startup["Agent startup protocol"]

    Startup --> CapMCP["Capability MCP"]
    Startup --> WikiMCP["Wiki MCP"]
    Startup --> NewsMCP["Newsfeed MCP"]

    CapMCP --> CapCatalog["capabilities.json"]
    CapCatalog --> Skills["Skills"]
    CapCatalog --> Plugins["Plugins"]
    CapCatalog --> MCPs["MCP servers"]
    CapCatalog --> CLIs["CLI tools"]
    CapCatalog --> Automations["Automations"]

    WikiMCP --> Wiki["Private Knowledge Wiki"]
    Wiki --> Decisions["Decisions"]
    Wiki --> Patterns["Patterns"]
    Wiki --> Learnings["Learnings"]
    Wiki --> Gaps["Gaps"]
    Wiki --> Topics["Topic pages"]

    NewsMCP --> NewsStore["Recent News Store"]
    NewsStore --> Articles["Articles"]
    NewsStore --> SourceHealth["Source health"]
    NewsStore --> Trends["Trend summaries"]
    NewsStore --> Candidates["Wiki candidates"]

    Sources["Sources"] --> Collect["Collectors"]
    Collect --> Process["Process / summarize / translate"]
    Process --> NewsStore
    Process --> Candidates

    Candidates --> OptionalBridge["Optional NotebookLM bridge"]
    OptionalBridge --> Wiki

    NewsStore --> OptionalWeb["Optional Web UI"]
    OptionalWeb --> Localhost["localhost"]
    OptionalWeb --> Vercel["Vercel"]

    CapMCP --> Work["Agent plan/work"]
    WikiMCP --> Work
    NewsMCP --> Work
    Work --> WriteBack["Optional durable write-back"]
    WriteBack --> WikiMCP
```

## What Is Core

- Capability MCP
- Wiki MCP
- Newsfeed MCP
- startup protocol

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
Public repo:
  docs, templates, fake examples, skeleton code

Private instance:
  real wiki, real sources, real news, sessions, reports, state, databases
```
