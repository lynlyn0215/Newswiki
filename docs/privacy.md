# Privacy

Newswiki separates the public template from the private instance.

## Public Template

Safe to publish:

- docs
- templates
- fake examples
- skeleton code
- provider-neutral instructions
- empty schemas
- public-safe export examples with summaries and source URLs only
- hosted alpha service code that reads validated public-safe exports

## Private Instance

Never publish:

- real articles
- real source lists if they reveal interests
- wiki pages
- raw NotebookLM output
- browser sessions
- local paths
- API keys
- database files
- pipeline reports
- automation state
- Vercel project IDs

## Hosted Alpha Boundary

The hosted alpha service must read from public-safe exports only.

Safe export items include:

- title
- short summary
- source URLs
- topics
- freshness
- confidence
- `public_safe: true`

Unsafe export items include:

- full article text
- private wiki notes
- raw browser or NotebookLM state
- local absolute paths
- unpublished personal notes
- tokens, credentials, or provider account metadata

If validation fails, REST and MCP adapters should fail closed instead of serving partial data.

## Red Flags

Run the privacy scan before committing:

```powershell
python scripts/privacy_scan.py
```

The scan looks for local paths, secrets, private runtime files, and personal-instance names. It is not a guarantee. Review diffs manually too.
