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

## User Setup Requests

If the user asks to set up, build, install, configure, or bootstrap their own Newswiki from this repo, treat the user as delegating to an AI agent. Follow:

1. `newswiki.setup.json`
2. `docs/agent-setup-protocol.md`
3. `docs/agent-checklist.md`

Default to creating a separate private instance, not writing user data into this repo.

Prefer the cross-platform bootstrap:

```bash
python scripts/agent_setup_newswiki.py --target ~/Newswiki-private
```

On Windows, PowerShell fallback:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/agent_setup_newswiki.ps1 -Target "$HOME\Newswiki-private"
```

Ask before installing dependencies, overwriting a target directory, editing external MCP config, copying private data, publishing, or pushing.

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

## Learning Gate

Before finishing any substantial task, run a concise learning gate:

1. Ask whether this session produced a reusable lesson, pattern, decision, or gap.
2. Write only durable, high-confidence items that would help a future agent avoid a mistake or choose a better path.
3. Skip raw logs, temporary status, obvious implementation details, praise, apologies, and low-confidence guesses.
4. Prefer the `session-learnings-to-wiki` skill or Wiki MCP write-back when available.

Classify write-backs as:

- `learning`: execution lesson, pitfall, or discovered failure mode.
- `pattern`: reusable workflow, checklist, or repeatable method.
- `decision`: durable user-approved product, architecture, or workflow choice.
- `gap`: missing coverage, uncertainty, or future research need.

For Newswiki work, pay special attention to public/private data boundaries, MCP contracts, startup capability discovery, wiki memory retrieval, export validation, deployment reality, and connector/tool limitations.
