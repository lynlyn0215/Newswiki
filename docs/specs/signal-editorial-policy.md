# Signal Editorial Policy

Newswiki v1 should not become an RSS summary pile. A signal enters the index only when it can improve a coding agent's pre-plan judgment.

## Scope

Initial topic:

```text
AI agents / MCP / devtools / model releases
```

## Admission Criteria

A signal can enter the v1 index when it meets all required criteria:

- It may change an agent product, architecture, workflow, model, or tool-choice decision.
- It has at least one public source URL.
- It names affected entities, products, projects, or standards.
- It includes a concrete `why_it_matters`.
- It maps to one or more `affected_tasks`.
- It has `last_verified_at`, `freshness`, `confidence`, and `stale_after` metadata.

## Reject Criteria

Reject or defer:

- generic AI hype
- source-free claims
- raw article dumps
- duplicate announcements with no new decision impact
- old version news with no current relevance
- private source lists that expose user interests
- rumors unless labeled low-confidence and useful for monitoring

## Required Fields

```json
{
  "id": "signal-001",
  "title": "Short source-backed signal",
  "summary": "What happened.",
  "why_it_matters": "Why this may affect an agent's plan.",
  "entities": ["Claude", "Hermes", "MCP"],
  "affected_tasks": ["agent product strategy", "MCP architecture review"],
  "decision_impact": "May weaken generic skill-index positioning.",
  "source_urls": ["https://example.com/source"],
  "topics": ["ai-agents", "mcp"],
  "updated_at": "2026-05-07T00:00:00Z",
  "last_verified_at": "2026-05-07T00:00:00Z",
  "freshness": "daily",
  "confidence": "high",
  "source_confidence": "high",
  "time_sensitivity": "high",
  "source_claim": "The source-backed factual claim.",
  "newswiki_interpretation": "Newswiki's interpretation of the product impact.",
  "observed_at": "2026-05-07",
  "stale_after": "2026-06-07T00:00:00Z",
  "data_limits": [],
  "public_safe": true
}
```

## Editorial Notes

- Prefer 15 strong signals over 50 weak ones.
- Summaries should separate source fact from Newswiki interpretation.
- `why_it_matters` must name a task or decision it could affect.
- Stale signals should be downranked or returned with `stale_warning`.
- Demo signals must say they are demo data and must not be treated as market evidence.
- Internal Newswiki docs may be durable knowledge, but they are not external market evidence.
