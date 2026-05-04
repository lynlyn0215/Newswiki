# NotebookLM Connector

NotebookLM is optional.

Reasons to use it:

- long-page fetching and evaluation
- browser/session-based reading
- token cost reduction for expensive ingestion
- human-reviewable source grounding

Reasons to skip it:

- extra session management
- browser profile state
- provider-specific workflow
- not needed for simple feeds

Never commit:

- browser session files
- browser profile directories
- NotebookLM result JSON
- pipeline state
- accepted private wiki drafts

See `templates/bridge-config.example.json`.
