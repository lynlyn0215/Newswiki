# Newswiki

Newswiki is a local-first personal agent information system template.

中文说明见 [README.zh-CN.md](README.zh-CN.md).

It helps an agent answer three questions before it starts work:

1. What can I use? -> Capability MCP
2. What do I already know? -> Wiki MCP
3. What happened recently? -> Newsfeed MCP

Most people can build a feed, a wiki, or a small website. Newswiki's core idea is the startup protocol: give the agent a clean way to query capabilities, durable memory, and recent information before choosing a plan.

## Core MCPs

### Wiki MCP

The Wiki MCP exposes a private Markdown knowledge wiki to agents. It is inspired by Andrej Karpathy's LLM Wiki pattern and related public implementations.

References:

- [karpathy/llm-wiki.md](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)
- [Pratiyush/llm-wiki](https://github.com/Pratiyush/llm-wiki)

### Capability MCP

The Capability MCP reads a local capability catalog generated from skills, MCP servers, CLI tools, and other workstation metadata. It lets the agent ask which capability chain fits the task before doing work.

This sits beside Wiki MCP. Both are startup context, not application features.

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

For the central design, read [docs/core-mcps.md](docs/core-mcps.md).

For a practical walkthrough, read [docs/build-your-own.md](docs/build-your-own.md).

For the visual map, read [docs/system-diagram.md](docs/system-diagram.md).

## Repository Shape

- `mcp/` - three core MCP server templates.
- `templates/` - private instance templates.
- `pipeline/` - optional collection, processing, storage, and report skeletons.
- `connectors/` - optional integrations.
- `web/` - optional public/local frontend skeleton.
- `examples/` - fake data only.

## Privacy Rule

This repo is public-safe. Real personal data belongs in the private instance created from templates, not in this repository.

Read [docs/privacy.md](docs/privacy.md) before adding any data.
