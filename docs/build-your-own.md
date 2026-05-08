# Build Your Own Newswiki

This guide turns the template into a private local Newswiki.

Goal:

```text
Your task
  -> get_context_for_task
      -> current signals when facts may be stale
      -> durable knowledge when history matters
      -> capability routing only for setup/tool tasks
  -> agent plans with a source-backed brief
```

## 1. Install

```powershell
git clone https://github.com/YOUR_USER/Newswiki.git
cd Newswiki
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Create Your Private Instance

```powershell
.\scripts\init_newswiki.ps1 -Target "$HOME\Newswiki-private"
```

This creates:

- `wiki/` - private Knowledge Wiki
- `data/news/` - demo news JSON
- `config/` - source, pipeline, and MCP examples
- `capabilities.json` - generated local capability catalog
- `AGENTS.md` - private instance rules

Do not publish this private instance.

## 3. Configure MCP Input Layers

Open:

```text
$HOME\Newswiki-private\config\mcp.example.toml
```

Replace:

- `PATH_TO_NEWSWIKI_REPO`
- `PATH_TO_PRIVATE_INSTANCE`

Then copy the blocks into your agent's MCP config.

## 4. Smoke Test The Pre-Plan Brief

Ask your agent:

```text
Before planning, build a Newswiki pre-plan brief for this task. Query external signals, wiki memory, or capability routing only if the task needs them:
"Help me design a weekly research workflow."
```

Expected behavior:

- The agent explains which context layers it used or skipped.
- Capability routing runs only if the task needs tools or setup.
- Newsfeed/current signals run only if recent facts matter.
- Wiki/durable knowledge runs when prior context matters.

If that works, the skeleton is alive.

## 5. Replace Fake News With Your Sources

Edit:

```text
$HOME\Newswiki-private\config\sources.example.yaml
```

Start small:

- one RSS feed
- one manual inbox
- one search connector

Keep source config private if it reveals your interests.

## 6. Choose Processing Mode

You have three practical options:

### Qwen API

Good default when your workflow is Chinese-heavy:

- classification
- Chinese summaries
- translation
- low token cost

### Other LLM Provider

Use OpenAI, Anthropic, Gemini, local models, or anything else.

### Agent Automation Session

Skip provider integration at first. Let an agent process a batch in a normal session and write JSON/Markdown outputs.

This is slower but simpler.

## 7. Grow The Knowledge Wiki

Your private wiki starts with:

- `architecture.md`
- `decisions.md`
- `patterns.md`
- `learnings.md`
- `gaps.md`
- `search-map.md`

When the agent learns something reusable, write it back through Wiki MCP in your private/local workflow. Write-back is not a hosted v1 default.

Do not write raw run logs into control pages.

## 8. Add Optional Connectors

Add only what you need:

- AgentSearch for self-hosted search/read/extract.
- Browser automation for interactive or client-rendered pages.
- NotebookLM for long article evaluation and token savings.
- Web UI for local reading or public-safe publishing.

Each connector is optional.

## 9. Add The Web UI

Use `web/` when you want a reading interface.

Local:

```text
web/docs/localhost.md
```

Vercel:

```text
web/docs/vercel.md
```

Only export public-safe JSON into the web app.

## 10. Keep It Safe

Before committing anything to the public template:

```powershell
python scripts\privacy_scan.py
```

Before publishing your own web output, manually review:

- article titles
- summaries
- source URLs
- tags
- briefings
- system reports

The private instance is allowed to know you. The public repo is not.
