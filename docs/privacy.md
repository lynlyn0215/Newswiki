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

## Red Flags

Run the privacy scan before committing:

```powershell
python scripts/privacy_scan.py
```

The scan looks for local paths, secrets, private runtime files, and personal-instance names. It is not a guarantee. Review diffs manually too.
