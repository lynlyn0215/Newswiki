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

Local connectors are JSON files. They are optional and read-only in the hosted alpha.

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
  "actionability": "remember"
}
```

Forbidden connector fields:

- raw article body
- full text
- tokens, passwords, API keys, credentials
- private notes
- local paths
- browser/session state

Connector exports should contain concise summaries and metadata, not raw private working files.
