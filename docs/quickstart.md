# Quickstart

## 1. Clone

```bash
git clone https://github.com/YOUR_USER/Newswiki.git
cd Newswiki
```

## 2. Install Dependencies

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. Create a Private Instance

Windows:

```powershell
.\scripts\init_newswiki.ps1 -Target "$HOME\Newswiki-private"
```

macOS/Linux can copy the `templates/` folder manually until a shell initializer is added.

## 4. Build Your Capability Catalog

The initializer writes `capabilities.json` once. Rebuild it whenever your local skills, MCPs, or CLIs change:

```powershell
python .\scripts\build_capabilities.py --output "$HOME\Newswiki-private\capabilities.json"
```

The scanner checks common local skill roots, common CLI tools, and your Codex MCP config by default. You can add explicit roots:

```powershell
python .\scripts\build_capabilities.py `
  --output "$HOME\Newswiki-private\capabilities.json" `
  --skill-root "$HOME\.codex\skills" `
  --mcp-config "$HOME\.codex\config.toml"
```

## 5. Configure the Pre-Plan Brief MCP

Start with [templates/config/mcp.example.toml](../templates/config/mcp.example.toml).

Primary agent-facing entry:

- `get_context_for_task`

Optional input/support layers:

- Wiki MCP: durable memory when prior decisions or project memory matter.
- Newsfeed MCP: current external signals when fresh facts, market movement, or platform changes matter.
- Capability MCP: setup, tool choice, local availability, commands, or workflow routing only.

## 6. Configure Sources

Start with [templates/config/sources.example.yaml](../templates/config/sources.example.yaml).

Use fake examples first. Add private sources only inside your private instance.

## 7. Agent Startup

Add the private instance `AGENTS.md` rules to your agent workspace. The agent should build a pre-plan brief before non-trivial work and query only the layers that fit the task:

- external signals when current facts or platform changes matter
- wiki/durable knowledge when prior decisions or project memory matter
- capability routing only for setup, tool choice, local availability, or workflow routing

## 8. Optional Web UI

Use [web/docs/localhost.md](../web/docs/localhost.md) for local preview or [web/docs/vercel.md](../web/docs/vercel.md) for Vercel deployment.

For the longer walkthrough, continue to [build-your-own.md](build-your-own.md).
