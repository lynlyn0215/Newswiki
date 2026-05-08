# Agent Setup Protocol

This file is for an AI agent helping a user build their own private Newswiki from this public template.

The user should be able to say:

```text
Clone Newswiki and set up my local Newswiki instance.
```

Then the agent should follow this protocol.

## Operating Principle

Treat this repository as a public-safe template. Create a separate private instance for user data.

Do not copy private user data into this repository.

## Read First

1. `AGENTS.md`
2. `newswiki.setup.json`
3. `docs/privacy.md`
4. `docs/agent-checklist.md`
5. `templates/config/mcp.example.toml`

## Confirm Before

Ask the user before:

- creating or overwriting the private instance directory
- installing dependencies
- editing external MCP config files
- copying private data sources
- publishing or pushing to GitHub

For normal read-only inspection and validation commands, proceed.

## Default Setup Path

Default private instance:

```text
~/Newswiki-private
```

Preferred cross-platform setup:

```bash
python scripts/agent_setup_newswiki.py --target ~/Newswiki-private
```

Windows PowerShell fallback:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/agent_setup_newswiki.ps1 -Target "$HOME\Newswiki-private"
```

The setup script:

- installs Python dependencies unless skipped
- initializes a private instance
- builds `capabilities.json`
- validates `examples/public`
- runs the privacy scan
- runs the hosted MCP smoke test
- writes a setup report inside the private instance

## Runtime Context Protocol

After setup, the user's agent should not force every MCP into every task.

Preferred product path:

1. Build a Newswiki pre-plan brief with `get_context_for_task` when the task may benefit from external signals, durable knowledge, or capability routing.
2. Use the returned `retrieval_decision` to explain which layers were queried or skipped.
3. Fall back to direct input-layer MCP calls only when testing local setup or debugging a specific connector.

Input-layer rules:

- Wiki MCP is for prior decisions, reusable patterns, known pitfalls, and gaps.
- Newsfeed MCP is for recent external information, market context, or source freshness.
- Capability MCP is only for tool choice, workflow routing, MCP setup, CLI availability, or automation selection.

If Capability MCP returns a generic or irrelevant chain, report that limitation and continue from stronger evidence.

## Manual Setup Path

If the setup script cannot run, perform these steps:

```powershell
python -m pip install -r requirements.txt
.\scripts\init_newswiki.ps1 -Target "$HOME\Newswiki-private"
python .\scripts\build_capabilities.py --output "$HOME\Newswiki-private\capabilities.json"
python .\scripts\validate_public_export.py examples\public
python .\scripts\privacy_scan.py
python .\scripts\smoke_mcp_client.py --api-key local-key --export-dir examples/public
```

## MCP Configuration

Use:

```text
~/Newswiki-private/config/mcp.example.toml
```

Before editing any config, detect the user's actual MCP client. Do not call every MCP client Codex.

Examples:

- Codex may use `~/.codex/config.toml`.
- Claude Code may use its own MCP command or config path.
- Claude Desktop and other clients may use JSON-style config.

Replace:

- `PATH_TO_NEWSWIKI_REPO`
- `PATH_TO_PRIVATE_INSTANCE`

Then ask before editing the user's real MCP config.

## Success Check

A setup is successful when:

- private instance exists
- `AGENTS.md` exists inside the private instance
- `capabilities.json` exists
- `wiki/` control pages exist
- `data/news/` contains fake demo data or user-approved private exports
- public export validator passes
- privacy scan passes
- hosted MCP smoke test returns `ok: true`
- the user has MCP config snippets ready to copy or approve

## Failure Handling

If a step fails:

1. Stop.
2. Report the failing command and short error.
3. Do not continue into config edits or data copying.
4. Suggest the smallest next fix.

Do not hide failed MCP or privacy checks.
