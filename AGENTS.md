# Newswiki Agent Rules

## Role

This repository is a public template for building a private Newswiki instance.

Do not treat this repo as a user's personal data store. It contains docs, templates, fake examples, and skeleton code only.

## Startup Protocol

Before non-trivial work, query startup context in this order when the tools exist:

1. Capability MCP: choose relevant skills, plugins, MCP tools, CLIs, and workflow chains.
2. Wiki MCP: retrieve past knowledge, prior decisions, patterns, known pitfalls, and gaps.
3. Newsfeed MCP: retrieve recent news only when the task benefits from current information.

Then plan or execute.

## Safety

- Do not commit real feeds, real wiki pages, browser sessions, local tokens, or private reports.
- Do not hard-code personal paths.
- Do not make Qwen, NotebookLM, AgentSearch, Vercel, or any provider mandatory.
- Do not publish or push to GitHub without explicit user confirmation.
- Do not copy files from a private Newswiki instance into this public template.

## Expected Checks

Before calling the public template ready:

```powershell
python scripts/privacy_scan.py
```

If code changes touch pipeline behavior, also add focused tests and run them.
