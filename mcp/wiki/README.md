# Wiki MCP

Read/write MCP for a private Markdown knowledge wiki.

Tools:

- `wiki_search(query, limit)`
- `wiki_past_knowledge(task, limit)`
- `wiki_write_learning(kind, title, content, links)`
- `wiki_recent_changes(days, limit)`

The public template is minimal. Your private instance owns the real `wiki/` directory.

Run:

```bash
python mcp/wiki/server.py --wiki-root ./templates/wiki
```
