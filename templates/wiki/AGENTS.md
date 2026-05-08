# Private Newswiki Instance Rules

## Context Protocol

Before non-trivial work, build a Newswiki pre-plan brief when available:

1. Call `get_context_for_task(task, topic?, token_budget?)`.
2. Read `retrieval_decision` and explain which context layers were queried or skipped.
3. Use Newsfeed/current signals only when current facts, market signals, or platform changes matter.
4. Use Wiki/durable knowledge only when prior decisions, patterns, pitfalls, or gaps may affect the work.
5. Use Capability routing only for tool choice, setup, local availability, commands, or workflow routing.

If `get_context_for_task` is unavailable, call the input-layer MCPs directly only when their layer is relevant to the task.

## Write-Back Rule

Write back only durable learning:

- reusable pattern
- decision
- pitfall
- gap

Do not write raw logs or uncertain one-off notes into control pages.

## Privacy

This private instance may contain personal information. Do not push it to a public repository.
