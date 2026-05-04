# Capability MCP

Startup MCP for local agent capabilities.

It answers:

- What skills/plugins/MCP/CLI tools exist?
- Which chain should the agent use for this task?
- What is optional, risky, or unavailable?

This template reads a generated `capabilities.json` catalog.

Build it with:

```bash
python scripts/build_capabilities.py --output PATH_TO_PRIVATE_INSTANCE/capabilities.json
```

The scanner covers common local skill roots, MCP config, and common CLI tools. Extend it for your workstation.
