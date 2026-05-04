# Architecture

Newswiki is an agent startup context system.

The core loop:

```text
User task
  -> Capability MCP: what tools/skills should the agent use?
  -> Wiki MCP: what prior knowledge should affect this work?
  -> Newsfeed MCP: what recent information is relevant?
  -> Agent plan/work
  -> Optional write-back to wiki when durable learning emerges
```

## Core MCP Layer

### Capability MCP

Scans the local agent workstation:

- skills
- plugins
- MCP servers
- CLI tools
- automations
- project workflows

It answers:

- `recommend_capabilities(task)`
- `get_skill_chain(task)`
- `list_capabilities()`

### Wiki MCP

Exposes a private Markdown wiki:

- `wiki_search(query)`
- `wiki_past_knowledge(task)`
- `wiki_write_learning(kind, title, content, links)`
- `wiki_recent_changes(days)`

The wiki keeps durable decisions, patterns, learnings, gaps, and topic pages.

### Newsfeed MCP

Exposes recent information:

- latest articles
- source health
- trend summaries
- wiki candidates
- run reports

It is read-only by default.

## Optional Pipeline Layer

Collectors gather candidate items from RSS, URLs, manual inboxes, browser automation, or search connectors.

Processors classify, summarize, translate, and decide which outputs each item deserves.

Storage can be SQLite, JSON files, Markdown, or a remote database. The template uses simple local files and SQLite-compatible schemas.

## Optional Knowledge Bridge

A NotebookLM bridge can evaluate long articles and prepare accepted wiki pages. It is optional and provider-specific.

The public template documents this bridge but does not include sessions, browser profiles, state files, or real results.

## Optional Web Layer

The `web/` folder is a reading interface skeleton. It can run locally or deploy to Vercel.

The web layer is not the product. It is one possible output surface.
