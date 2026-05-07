# Newswiki Claude Code Instructions

This repository is a public-safe template. Do not put private user data, real feeds, private wiki pages, tokens, browser sessions, or local-only reports into this repo.

## Newswiki Startup Protocol

For non-trivial work in this workspace, use local Newswiki MCP servers when they add real context:

1. Use Wiki MCP to retrieve past project knowledge, prior decisions, reusable patterns, known pitfalls, and gaps.
2. Use Newsfeed MCP when recent signals, market context, or current information may affect the answer.
3. Use Capability MCP only when tool routing matters, such as choosing skills, plugins, MCP tools, CLIs, automations, or workflow chains.

Do not merely list the MCP tools. Use their results to shape the plan, answer, or next step.

Do not force Capability MCP into every task. If it returns only generic or irrelevant chains, state that limitation and continue from stronger evidence.

When reporting back, include:

- which Newswiki MCP tools were called
- what useful context they returned
- how that context changed the plan, conclusion, or next step

If any Newswiki MCP server is unavailable, say which one failed and continue with the best fallback.

## Product-Value Tests

For product-value tests, do not answer from general knowledge alone. At minimum, call Wiki MCP before giving recommendations. Use Newsfeed MCP when the task involves market, news, timing, or current ecosystem signals. Use Capability MCP only when the test concerns tool choice, workflow routing, MCP setup, or local capability availability.

Be explicit about data quality:

- A fresh private instance may have an empty wiki.
- Example news files are demo fixtures, not market evidence.
- A generic capability chain means the capability catalog may not be useful for this task; do not let it override source evidence.

## Setup Boundaries

If the user asks you to set up Newswiki, follow:

1. `newswiki.setup.json`
2. `docs/agent-setup-protocol.md`
3. `docs/agent-checklist.md`

Create or use a separate private instance outside this public repo. Ask before installing dependencies, overwriting target directories, editing external MCP config, copying private data, publishing, or pushing.
