# Newswiki Product-Value Eval — 2026-05-09

## Summary

Newswiki's `get_context_for_task` passed a 10-task A/B product-value eval.

- Batch: `eval/runs/20260509T1033`
- Scorer: Claude Code
- Result: 10/10 context wins
- Average context score: 12.7 / 14
- Average control score: 5.1 / 14
- Average lift: +7.6

This supports continuing to productize `get_context_for_task` as the v1 flagship surface.

## Method

Each fixture in `eval/tasks/` generated two blind prompts:

- Control: task-only prompt without Newswiki context.
- Context: task prompt plus `get_context_for_task` materials.

The scorer answered both prompts, scored them with `eval/rubric.md`, then opened each run's `_audit/label_key.json` only after scoring.

Runs `001` and `002` used the earlier 12-point rubric. Runs `003` through `010` used the updated 14-point rubric, which separates data-limit disclosure from data-limit impact.

## Decision Gate

| Gate | Required | Actual | Result |
|---|---:|---:|---|
| Context wins | 6 / 10 | 10 / 10 | Pass |
| Stale assumptions avoided | 4 / 10 | 10 / 10 | Pass |
| Useful decision changes | 3 / 10 | 10 / 10 | Pass |
| Fixable gaps surfaced | 1+ | 3 | Pass |

Decision: continue productizing `get_context_for_task`.

## What Worked

- Context changed recommendations, not only confidence.
- Source-backed signals were most useful when they mapped directly to platform, model, or MCP changes.
- Internal durable knowledge was useful for framing, especially the evaluation gate and pre-plan brief contract.
- Explicit data limits helped distinguish product evidence from internal framing.

## Gaps Found

1. `model-releases` coverage was too narrow. Runs `003` and `006` mainly retrieved Codex signals, missing Claude and Hermes model-release context.
2. An unnamed "this-week devtool" task is structurally mismatched with a curated signal index unless the tool name or source is supplied.
3. `open-core`, `ai-devtools`, and `model-releases` need better durable-knowledge topic taxonomy to avoid fallback retrieval.

## Follow-Up

Before building write-back, billing, or client-specific adapters:

1. Add Claude and Hermes model-release signals to the public export.
2. Expand durable knowledge topic taxonomy for `open-core`, `ai-devtools`, and `model-releases`.
3. Collect external customer or demand evidence for hosted MCP productization.

## Local Artifacts

- Batch report: `eval/runs/20260509T1033-final-report.md`
- Batch scoreboard: `eval/runs/20260509T1033-batch-scoreboard.md`
- Rubric: `eval/rubric.md`

`eval/runs/` is ignored by git. This document is the tracked summary.
