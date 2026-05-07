# Newswiki

Newswiki is a local-first personal agent information system template and hosted MCP alpha skeleton.

中文说明见 [README.zh-CN.md](README.zh-CN.md).

It helps an agent answer the context questions that matter before it starts work:

1. What do I already know? -> Wiki MCP
2. What happened recently? -> Newsfeed MCP
3. What tools or workflows matter for this task? -> Capability MCP, on demand

Most people can build a feed, a wiki, or a small website. Newswiki's core idea is the context protocol: give the agent a clean way to query durable memory and recent external signals before choosing a plan. Capability routing is useful when the task is about tools, workflows, MCP setup, or local availability; it is not forced into every task.

## Hosted Alpha

This repository now includes a public-safe hosted alpha path:

- public-safe export schema and validator
- read-only REST API
- hosted MCP adapter
- real stdio MCP smoke client
- static context-pack playground

Run the full path with [docs/quickstart-hosted-alpha.md](docs/quickstart-hosted-alpha.md).

The hosted alpha uses fake example data by default. It is a product skeleton, not a hosted service account or private data backend.

For the self-hosted vs hosted-service positioning, read [docs/open-core.md](docs/open-core.md).

## Core MCPs

### Wiki MCP

The Wiki MCP exposes a private Markdown knowledge wiki to agents. It is inspired by Andrej Karpathy's LLM Wiki pattern and related public implementations.

References:

- [karpathy/llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Pratiyush/llm-wiki](https://github.com/Pratiyush/llm-wiki)

### Capability MCP

The Capability MCP reads a local capability catalog generated from skills, MCP servers, CLI tools, and other workstation metadata. It lets the agent ask which capability chain fits the task before doing work.

This is an optional routing layer. Use it when choosing tools, workflows, MCP servers, CLIs, or automations. Do not treat a generic capability result as stronger than project memory, source evidence, or current facts.

### Newsfeed MCP

The Newsfeed MCP exposes recent articles, source health, trend summaries, and wiki candidates. It lets the agent ground work in fresh information without dumping raw feeds into context.

## Optional Layers

- Collectors: RSS, URLs, manual inbox, browser tools, or AgentSearch.
- LLM processing: Qwen, OpenAI, Anthropic, Gemini, local models, or an automation session.
- NotebookLM bridge: optional long-page evaluation and token-saving workflow.
- Web UI: optional local or Vercel-published reading interface.

Qwen is a good default for Chinese classification, summary, and translation because the Chinese quality/cost tradeoff is strong. It is not required.

NotebookLM is also optional. It can help with long article fetching, evaluation, and token cost control, but Newswiki should work without it.

## Start

Read [docs/quickstart.md](docs/quickstart.md).

If you want your AI agent to set Newswiki up for you, give it [docs/agent-setup-protocol.md](docs/agent-setup-protocol.md), [docs/agent-checklist.md](docs/agent-checklist.md), and [newswiki.setup.json](newswiki.setup.json).

To verify the hosted alpha service path, read [docs/quickstart-hosted-alpha.md](docs/quickstart-hosted-alpha.md).

For the central design, read [docs/core-mcps.md](docs/core-mcps.md).

For a practical walkthrough, read [docs/build-your-own.md](docs/build-your-own.md).

For the visual map, read [docs/system-diagram.md](docs/system-diagram.md).

To test the product path with another agent, read [docs/testing-plan.md](docs/testing-plan.md).

## Repository Shape

- `mcp/` - three core MCP server templates.
- `service/` - hosted alpha REST and MCP service skeleton.
- `templates/` - private instance templates.
- `pipeline/` - optional collection, processing, storage, and report skeletons.
- `connectors/` - optional integrations.
- `web/` - optional static playground and frontend skeleton.
- `examples/` - fake data only.
- `newswiki.setup.json` - machine-readable setup manifest for agents.

Agent bootstrap:

```bash
python scripts/agent_setup_newswiki.py --target ~/Newswiki-private
```

## Privacy Rule

This repo is public-safe. Real personal data belongs in the private instance created from templates, not in this repository.

Read [docs/privacy.md](docs/privacy.md) before adding any data.
