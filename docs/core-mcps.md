# The Three Core MCPs

Newswiki is MCP-first.

The three core MCPs sit at the same layer. They are all queried before important work starts.

## Capability MCP

Question: what can this agent use?

It lists and recommends:

- skills
- plugins
- MCP tools
- CLI tools
- automations
- project workflows

Typical use:

```text
Task: publish a new research brief
-> Capability MCP returns: wiki memory, newsfeed query, web export, deployment checklist
```

## Wiki MCP

Question: what do we already know?

It reads and updates the private Knowledge Wiki:

- decisions
- patterns
- learnings
- gaps
- topic pages
- recent changes

This is the durable memory layer. It is inspired by Karpathy's LLM Wiki pattern, with MCP tools added for agent startup.

## Newsfeed MCP

Question: what happened recently?

It exposes:

- latest articles
- source health
- trend summaries
- wiki candidates
- run reports

This MCP is read-only by default. It gives the agent current context without dumping raw news data into the prompt.

## Startup Order

```text
Capability MCP
  -> Wiki MCP
  -> Newsfeed MCP when current information matters
  -> plan/work
  -> optional Wiki MCP write-back
```

This is the core product. Collection, LLM processing, NotebookLM, search connectors, browser automation, and web publishing are replaceable modules.
