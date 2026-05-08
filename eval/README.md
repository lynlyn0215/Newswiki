# Newswiki Evaluation

This directory tests whether Newswiki pre-plan briefs improve coding-agent answers.

V1 evaluation is manual first. Automation comes after the task set and rubric prove useful.

## Files

- `tasks/`: benchmark task fixtures.
- `rubric.md`: scoring rubric.
- `manual-ab-protocol.md`: how to run randomized A/B comparisons.
- `context_pack_for_task.py`: generates a Newswiki pre-plan brief for a fixture.
- `prepare_ab_run.py`: creates randomized scorer-facing prompts, audit materials, and a scorecard for one run.
- `coverage_report.py`: checks whether fixtures retrieve enough context.

## Generate A Brief

```powershell
python eval\context_pack_for_task.py eval\tasks\001-skill-mcp-positioning.json
```

## Prepare An A/B Run

```powershell
python eval\prepare_ab_run.py eval\tasks\001-skill-mcp-positioning.json
```

Then paste `answer_a_prompt.md` and `answer_b_prompt.md` into fresh sessions with the same target agent/model. Score A/B before opening `_audit/label_key.json`. The audit directory is only for unblinding after numeric scoring and notes are written.

## Check Coverage

```powershell
python eval\coverage_report.py
```

Before formal A/B runs, optionally verify cited URLs:

```powershell
python eval\coverage_report.py --check-source-urls
```

## Success Gate

Continue product work only if Newswiki context improves at least 7 of 10 benchmark tasks and avoids stale assumptions in at least 5 tasks.

`coverage_report.py` is a retrieval-quality smoke check, not A/B proof. It must pass before a manual run, but it does not prove that Newswiki improves agent answers.

Generated run directories under `eval/runs/` are local scratch artifacts and are gitignored. Commit only reviewed result summaries, not raw temporary run folders.
