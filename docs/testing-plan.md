# Newswiki Product Testing Plan

This plan tests Newswiki as an agent-native product, not just as a Python project.

## Test Layers

### 1. Fresh Clone Smoke

Goal: prove a clean clone can install, validate, run MCP smoke, and create a private instance.

Command:

```powershell
python scripts\fresh_clone_smoke.py --source https://github.com/lynlyn0215/Newswiki.git
```

For local preflight before pushing:

```powershell
python scripts\fresh_clone_smoke.py --source .
```

If the GitHub repo is still private and the test environment is not authenticated, use a local path as `--source`.

Pass criteria:

- clone succeeds
- `newswiki.setup.json` is valid JSON
- public export validator passes
- privacy scan passes
- hosted MCP smoke returns `ok: true`
- agent-native setup creates a private instance
- service tests pass

### 2. Claude Code Agent-Native Setup Test

Goal: verify a different coding agent can read the repo and set up Newswiki without hand-holding.

Use [claude-code-test.md](claude-code-test.md).

Pass criteria:

- Claude Code reads `AGENTS.md`, `newswiki.setup.json`, and setup docs before acting
- it identifies confirmation boundaries
- it creates a private instance outside the public repo
- it runs setup validation
- it does not copy private data into the public repo
- it reports remaining manual MCP config steps clearly
- it does not call itself Codex unless the detected client is actually Codex

### 3. Claude Code Product-Value MCP Test

Goal: verify Claude Code can use Newswiki MCP context to shape a real product judgment, not just connect to servers.

Use the Product-Value MCP Test prompt in [claude-code-test.md](claude-code-test.md).

Pass criteria:

- it calls Wiki MCP before product recommendations
- it calls Newsfeed MCP when judging market/current signals
- it calls Capability MCP only when the task requires tool/workflow routing, or explicitly says it is unnecessary
- it distinguishes fresh private-instance templates from real history
- it distinguishes demo news fixtures from real market evidence
- it explains how MCP context changed or limited the recommendation

Known useful failure signal:

- If Capability MCP only returns `startup.default`, treat that as a weak routing signal, not as a product judgment input.
- If Wiki MCP returns only empty control pages, seed or import durable decisions before relying on past-knowledge recommendations.
- If Newsfeed MCP returns only demo articles, do not treat the result as market validation.

### 4. Core Local MCP Client Test

Goal: verify the optional local input-layer MCP servers can be used by a client through stdio.

Command:

```powershell
python scripts\smoke_core_mcp_client.py --private-instance "$HOME\Newswiki-private-claude-test"
```

Pass criteria:

- Wiki MCP lists tools and `wiki_past_knowledge` returns pages.
- Capability MCP lists tools and `get_skill_chain` returns a chain.
- Newsfeed MCP lists tools and `latest_articles` returns demo or private articles.

### 5. Pre-Plan Brief Product Quality Test

Goal: verify `get_context_for_task` is useful as a product surface.

Run 10 real tasks through the MCP smoke path or a real MCP client:

1. Design a hosted MCP context service.
2. Research current coding agent trends.
3. Pick tools for browser automation.
4. Prepare an AI workflow reliability article.
5. Evaluate an MCP server product idea.
6. Plan a public-safe export pipeline.
7. Recommend tools for a local-first agent workspace.
8. Build a weekly devtools briefing workflow.
9. Compare self-hosted vs hosted agent infrastructure.
10. Draft onboarding for an agent-native repo.

Score each context pack:

- recent signals present
- durable knowledge present
- tool recommendations present only when capability routing is relevant
- source links present
- freshness and confidence present
- retrieval decisions explain queried/skipped layers
- data limits prevent overclaiming
- answer helps the agent plan the next step

### 6. Privacy Release Test

Goal: prove the public repo and public-safe exports do not leak private data.

Run:

```powershell
python scripts\privacy_scan.py
python scripts\validate_public_export.py examples\public
```

Manually inspect:

- README files
- `docs/`
- `examples/`
- `templates/config/`
- setup manifests
- generated images

Fail on:

- real articles
- private wiki pages
- browser sessions
- tokens or credentials
- Vercel project IDs
- private source lists
- raw NotebookLM state

### 7. Design Partner Interview

Goal: test whether the hosted service value proposition is clear.

Show the user:

- [open-core.md](open-core.md)
- [quickstart-hosted-alpha.md](quickstart-hosted-alpha.md)
- the static playground

Ask:

- Would you self-host this, connect a hosted MCP, or both?
- Which topics would make the hosted MCP worth trying?
- What would you least want to maintain yourself?
- Which delivery channel matters: MCP only, email, Slack, Discord, dashboard?
- What would make you pay?

## Release Gate

Before public release, pass:

- Fresh clone smoke
- Claude Code setup test
- Claude Code product-value MCP test
- Core local MCP client test
- Privacy release test
- Pre-plan brief product quality test with at least 7 of 10 useful context packs
- Manual README/open-core positioning review
