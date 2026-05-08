# Agent Context Protocol

For any non-trivial task, start by building a Newswiki pre-plan brief:

1. Call `get_context_for_task(task, topic?, token_budget?)` when available.
2. Read `retrieval_decision` before planning.
3. Use external signals only when current facts, market signals, or platform changes matter.
4. Use durable wiki knowledge only when prior decisions, patterns, pitfalls, or gaps may affect the work.
5. Use capability routing only when the task asks for tool choice, setup, local availability, commands, or workflow routing.
6. Plan or execute with the brief's sources, freshness, confidence, and data limits.
7. Write back durable learning only when something reusable emerged.

Direct Wiki MCP, Newsfeed MCP, or Capability MCP calls are for connector debugging, local setup tests, or cases where `get_context_for_task` is unavailable.
