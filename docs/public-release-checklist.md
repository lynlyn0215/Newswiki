# Public Release Checklist

Use this before making the repository public or tagging an alpha release.

## Repository Positioning

- README explains Newswiki as a local-first personal agent information system template.
- README explains the hosted alpha as a product skeleton, not a live hosted service.
- Chinese README has the same core positioning and links.
- Core MCPs are clear: Capability MCP, Wiki MCP, Newsfeed MCP.
- Hosted alpha path is clear: public-safe export -> REST API -> MCP adapter -> playground.

## Privacy

- Run:

```powershell
python scripts\privacy_scan.py
```

- Manually inspect the final diff.
- No real articles, private wiki pages, browser sessions, local tokens, database files, Vercel project IDs, or private reports.
- Public export examples contain summaries and source links only.
- Hosted service reads only validated public-safe exports.

## Fresh Clone Verification

Run:

```powershell
python -m pip install -r requirements.txt
python scripts\validate_public_export.py examples\public
python scripts\privacy_scan.py
python scripts\smoke_mcp_client.py --api-key local-key --export-dir examples/public
python -m unittest tests.test_public_export_schema service.tests.test_health service.tests.test_search service.tests.test_context_pack service.tests.test_routes service.tests.test_mcp_contract
```

Agent-native setup smoke:

```powershell
python scripts\agent_setup_newswiki.py --target "$env:TEMP\Newswiki-private-smoke" --skip-install
```

Windows PowerShell fallback:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\agent_setup_newswiki.ps1 -Target "$env:TEMP\Newswiki-private-smoke" -SkipInstall
```

Optional web check:

```powershell
python -m http.server 8765 --directory web
```

Open:

```text
http://127.0.0.1:8765/index.html
```

## GitHub Settings

Suggested description:

```text
MCP-first personal agent information system template with public-safe Newswiki hosted alpha.
```

Suggested topics:

```text
mcp, agents, knowledge-wiki, newsfeed, personal-ai, agent-tools, context-engineering
```

Recommended release tag:

```text
v0.1.0-alpha
```

## Before Public

- Keep the repo private until final manual review is complete.
- Confirm examples are fake.
- Confirm docs do not imply Qwen, NotebookLM, Vercel, AgentSearch, or any vendor is required.
- Confirm no private source folders were copied into this template.
