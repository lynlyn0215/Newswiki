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

## 5. Configure MCPs

Start with [templates/config/mcp.example.toml](../templates/config/mcp.example.toml).

Configure:

- Wiki MCP
- Capability MCP
- Newsfeed MCP

## 6. Configure Sources

Start with [templates/config/sources.example.yaml](../templates/config/sources.example.yaml).

Use fake examples first. Add private sources only inside your private instance.

## 7. Agent Startup

Add the private instance `AGENTS.md` rules to your agent workspace. The agent should query Capability MCP, Wiki MCP, and Newsfeed MCP before non-trivial work.

## 8. Optional Web UI

Use [web/docs/localhost.md](../web/docs/localhost.md) for local preview or [web/docs/vercel.md](../web/docs/vercel.md) for Vercel deployment.

For the longer walkthrough, continue to [build-your-own.md](build-your-own.md).
