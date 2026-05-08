# Hosted Alpha Quickstart

This guide verifies the hosted Newswiki alpha path from a fresh clone:

```text
public-safe export -> REST API -> MCP adapter -> static playground
```

The examples use fake public-safe data only.

## 1. Install

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 2. Validate the Public Export

```powershell
python scripts\validate_public_export.py examples\public
python scripts\privacy_scan.py
```

Both commands should pass before serving data.

## 3. Run the REST API

PowerShell:

```powershell
$env:NEWSWIKI_PUBLIC_EXPORT_DIR="examples/public"
$env:NEWSWIKI_API_KEYS="local-key"
uvicorn service.app.main:app --reload
```

In another terminal:

```powershell
curl.exe -H "x-api-key: local-key" http://127.0.0.1:8000/v1/signals
```

Expected shape:

```json
{
  "signals": []
}
```

## 4. Smoke Test the MCP Adapter

Run the stdio MCP smoke test:

```powershell
python scripts\smoke_mcp_client.py --api-key local-key --export-dir examples/public
```

Expected shape:

```json
{
  "ok": true,
  "tools": ["get_context_for_task", "..."],
  "context_pack": {
    "brief_type": "pre_plan",
    "signals": 3,
    "knowledge": 2,
    "tools": 0,
    "sources": 5
  }
}
```

This starts the MCP server as a child process, lists tools, calls `get_context_for_task`, and checks that the returned context pack has the required sections.

## 5. Configure an MCP Client

Use [mcp-client-setup.md](mcp-client-setup.md) for client configuration snippets. The client should call `get_context_for_task` first for non-trivial work; direct signal/knowledge/tool search is for support and debugging.

## 6. Open the Static Playground

Open:

```text
web/index.html
```

Or serve it locally:

```powershell
python -m http.server 8765 --directory web
```

Then visit:

```text
http://127.0.0.1:8765/index.html
```

## Success Criteria

A local alpha is connected when:

- Public export validation passes.
- Privacy scan passes.
- REST `/v1/signals` returns data with an API key.
- MCP smoke test returns `ok: true`.
- The static playground opens and shows a context pack.
