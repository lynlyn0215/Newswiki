# Newswiki Input MCPs

Newswiki v1 is not "three MCPs queried before every task."

The core product surface is the read-only `get_context_for_task` pre-plan brief. Wiki, Capability, and Newsfeed MCPs are input layers that can feed that brief when the task calls for them.

## Capability MCP

Question: does this task need local tool or workflow routing?

Use it when the task asks to choose, install, configure, or route:

- skills
- plugins
- MCP tools
- CLI tools
- automations
- project workflows

Do not call it just because a product-strategy task mentions "MCP" or "skill."

## Wiki MCP

Question: what durable project or domain knowledge matters?

It can read private Knowledge Wiki summaries:

- decisions
- patterns
- learnings
- gaps
- topic pages

In v1 hosted mode this is not a private write-back service. Private wiki connector layers are for local/self-hosted mode.

## Newsfeed MCP

Question: what current external signal may change the answer?

It can expose:

- latest articles
- source health
- trend summaries
- wiki candidates
- run reports

It should remain read-only by default and should return source-backed summaries, not raw news dumps.

## Retrieval Order

```text
task
  -> decide whether external signals are needed
  -> retrieve durable knowledge when project context matters
  -> retrieve capability routing only for tool/setup tasks
  -> return one pre-plan brief with sources, freshness, confidence, data limits, and retrieval decisions
```

Collection, LLM processing, NotebookLM, search connectors, browser automation, and web publishing are replaceable modules.
