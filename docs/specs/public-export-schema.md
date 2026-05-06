# Public Export Schema

Newswiki hosted services must read only public-safe export files.

Internal systems may contain private paths, notes, raw article bodies, session state, and unpublished judgments. Hosted MCP and REST endpoints must never read those internal stores directly. They read `exports/public/`-style files that pass validation.

## Export Files

Required alpha files:

- `signals.json`
- `knowledge_pages.json`
- `tool_cards.json`
- `briefs.json`
- `topics.json`

Each file is a JSON object with one top-level array:

```json
{
  "signals": []
}
```

## Common Item Fields

Every item exposed to hosted service consumers must include:

- `id`: stable string
- `title`: human-readable string
- `summary`: short original summary
- `source_urls`: non-empty array of public URLs
- `topics`: non-empty array of topic ids
- `updated_at`: ISO-like timestamp string
- `freshness`: one of `live`, `daily`, `weekly`, `archival`
- `confidence`: one of `low`, `medium`, `high`
- `public_safe`: must be `true`

## Type-Specific Fields

### Signal

Recommended fields:

- `published_at`
- `category`
- `impact`
- `why_it_matters`

### Knowledge Page

Recommended fields:

- `slug`
- `kind`
- `key_points`
- `related_tools`

### Tool Card

Recommended fields:

- `tool_type`
- `homepage_url`
- `use_cases`
- `agent_fit`
- `install_hint`

### Brief

Recommended fields:

- `period`
- `headline`
- `signals`
- `knowledge`
- `tools`

### Topic

Recommended fields:

- `description`
- `aliases`
- `parent_topic`

## Forbidden Content

Public exports must not include:

- local absolute paths
- private source notes
- browser profile or session references
- raw NotebookLM state
- full article bodies
- private wiki control notes
- unpublished personal workflow notes
- API keys, tokens, credentials, or passwords
- item fields named like `body`, `raw_content`, `full_text`, `private_notes`, `internal_notes`, `local_path`

## Validator

Run:

```powershell
python scripts\validate_public_export.py examples\public
```

The validator returns a machine-readable JSON report:

```json
{
  "ok": true,
  "files": [],
  "errors": []
}
```

Hosted deploys should block when `ok` is false.
