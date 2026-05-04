# Pipeline Skeleton

The pipeline is optional. The MCP startup protocol is the core.

Use the pipeline when you want automated collection and processing:

```text
collect -> process -> store -> report -> optional web export -> optional wiki candidates
```

Provider choices are replaceable. See `pipeline/providers/`.
