# Manual A/B Protocol

Use this protocol before building more product surface.

## Goal

Measure whether the generated task material improves a coding agent's answer without revealing which side received it until after scoring.

## Steps

1. Pick one task fixture from `eval/tasks/`.
2. Prepare a run directory:

```powershell
python eval\prepare_ab_run.py eval\tasks\001-skill-mcp-positioning.json
```

3. Paste `answer_a_prompt.md` into a fresh target-agent session.
4. Paste `answer_b_prompt.md` into another fresh session with the same target agent and model.
5. Score both answers with `eval/rubric.md` before opening `_audit/label_key.json`.
6. Open `_audit/label_key.json` only after scoring to reveal which answer was control vs context.
7. Record whether the context material changed the decision, avoided a stale assumption, or improved source use in `scorecard.md`.

Before running all tasks, check fixture coverage:

```powershell
python eval\coverage_report.py
```

## Controls

- Use the same agent and model when possible.
- Do not score from files under `_audit/`; use only the randomized A/B prompts.
- Keep answer order hidden from the scorer until after numeric scoring and notes are written.
- Do not treat demo data as market evidence.
- Record data limits even when the brief is weak.

## Result Template

```markdown
# Manual A/B Eval Result

Task:
Agent:
Date:

Answer A score:
Answer B score:
Improved: yes/no
Stale assumption avoided: yes/no
Decision changed: yes/no
Unblinded after scoring: yes/no

Context items used:
- 

Sources cited:
- 

Notes:
- 
```
