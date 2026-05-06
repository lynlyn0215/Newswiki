# Agent Setup Checklist

Use this checklist when an AI agent sets up Newswiki for a user.

## Preflight

- [ ] Confirm target private instance path.
- [ ] Confirm before installing dependencies.
- [ ] Confirm before overwriting an existing target directory.
- [ ] Confirm before editing external MCP config.
- [ ] Read `newswiki.setup.json`.
- [ ] Read `docs/privacy.md`.

## Private Instance

- [ ] Run `scripts/agent_setup_newswiki.py` or the Windows PowerShell fallback `scripts/agent_setup_newswiki.ps1`.
- [ ] Confirm private `AGENTS.md` exists.
- [ ] Confirm `wiki/` exists.
- [ ] Confirm `wiki/learnings.md`, `wiki/patterns.md`, `wiki/decisions.md`, and `wiki/gaps.md` exist.
- [ ] Confirm `data/news/` exists.
- [ ] Confirm `config/mcp.example.toml` exists.
- [ ] Confirm `capabilities.json` exists.

## Validation

- [ ] Run `python scripts/validate_public_export.py examples/public`.
- [ ] Run `python scripts/privacy_scan.py`.
- [ ] Run `python scripts/smoke_mcp_client.py --api-key local-key --export-dir examples/public`.
- [ ] Run service tests if service code changed.

## MCP Readiness

- [ ] Prepare Wiki MCP config.
- [ ] Prepare Capability MCP config.
- [ ] Prepare Newsfeed MCP config.
- [ ] Prepare hosted alpha MCP config if the user wants the demo context service.
- [ ] Ask before writing the config to the user's real agent config file.
- [ ] Tell the user whether a session restart or MCP reload is needed.

## Privacy

- [ ] No real articles copied into the public repo.
- [ ] No private wiki pages copied into the public repo.
- [ ] No browser sessions, tokens, database files, or reports copied into the public repo.
- [ ] Source lists stay private when they reveal user interests.

## Completion

- [ ] Summarize created paths.
- [ ] Summarize commands that passed.
- [ ] List any manual follow-up.
- [ ] If a durable setup lesson emerged, write it to the user's Knowledge Wiki when available.
