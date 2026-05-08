# Context Layer Contract

Newswiki context packs combine provider-owned and user-owned context. Every returned item must identify its layer so an agent can judge privacy, freshness, and actionability.

## Source Types

| `source_type` | Owner | Meaning |
|---|---|---|
| `newswiki_hosted` | Newswiki | hosted signals and news context |
| `newswiki_curated` | Newswiki | curated public knowledge and methods |
| `recommended_template` | Newswiki | workflow/tool templates that may need install or config |
| `user_private` | User | private wiki memory, decisions, and project knowledge |
| `local_capability` | User | tools available on the user's machine |

## Connector Files

Local connectors are JSON files. They are optional. Hosted/public mode does not load them.

To enable private connector layers in a self-hosted deployment, set:

```powershell
$env:NEWSWIKI_CONTEXT_MODE="local"
```

User memory:

```text
private_memory.json
```

Local capabilities:

```text
local_capabilities.json
```

Set paths with:

```powershell
$env:NEWSWIKI_USER_MEMORY_DIR="C:\path\to\connector-export"
$env:NEWSWIKI_LOCAL_CAPABILITY_DIR="C:\path\to\connector-export"
```

## Common Item Shape

```json
{
  "id": "memory-001",
  "title": "Short title",
  "summary": "Summary safe to show to the user's agent.",
  "source_urls": [],
  "topics": ["mcp"],
  "updated_at": "2026-01-02T10:00:00Z",
  "freshness": "weekly",
  "confidence": "high",
  "source_type": "user_private",
  "privacy_level": "private",
  "actionability": "remember",
  "why_it_matters": "Explains why this context may change the agent's plan.",
  "affected_tasks": ["hosted MCP planning"],
  "decision_impact": "May change product positioning.",
  "last_verified_at": "2026-01-02T10:00:00Z",
  "stale_after": "2026-02-02T10:00:00Z",
  "stale_warning": ""
}
```

## Pre-Plan Brief Shape

`get_context_for_task` should return a pre-plan brief. The brief explains what the agent should know before planning, not just what text matched a query.

Required v1 fields:

- `brief_type`: `pre_plan`
- `needs_fresh_facts`
- `retrieval_decision`
- `relevant_signals`
- `relevant_knowledge`
- `stale_assumption_warnings`
- `what_not_to_assume`
- `suggested_verification_steps`
- `data_limits`
- `sources`
- `freshness`
- `confidence`

Legacy aliases such as `signals`, `knowledge`, and `tools` can remain for compatibility.

`retrieval_decision` is a nested object. Each layer reports:

- `status`: `queried`, `skipped`, `no_results`, `fallback_used`, `latest_fallback`, `disabled`, or `filtered_empty`
- `needed`
- `reason`
- `topic`
- `topic_matched`
- `fallback_used`
- `result_count`

Fallback is never silent. If fallback is used, the context pack must lower confidence or add a data limit/warning so the agent does not treat broad results as direct topic evidence.

Forbidden connector fields:

- raw article body
- full text
- tokens, passwords, API keys, credentials
- private notes
- local paths
- browser/session state

Connector exports should contain concise summaries and metadata, not raw private working files.
