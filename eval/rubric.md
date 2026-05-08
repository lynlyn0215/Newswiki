# Newswiki A/B Evaluation Rubric

Score each dimension from 0 to 2.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Task relevance | Context is irrelevant | Partly relevant | Directly changes task framing |
| Freshness | Stale or unclear | Date present | Freshness changes confidence or decision |
| Source use | No source used | Source cited | Source verifies or qualifies a claim |
| Stale assumption avoided | No | Possible | Clearly avoided |
| Decision impact | None | Small wording change | Plan or recommendation changed |
| Data limits honesty | Ignored | Mentioned | Materially shaped conclusion |

Maximum score: 12.

## Pass Threshold

A task counts as improved when:

- Newswiki answer scores at least 3 points higher than baseline, and
- the cited Newswiki context is directly relevant to the task, and
- fallback or data-limit warnings are disclosed when present.

It can also count as improved when Newswiki avoids a material stale assumption or changes the decision, but only if the answer cites directly relevant source-backed context.

## Hard Fail Conditions

A task does not count as improved when:

- Newswiki cites broad fallback context as direct evidence.
- The context pack misses required `expected_context` coverage.
- Source-use improvement comes only from prompt structure rather than relevant context.
- Internal Newswiki docs are treated as external market validation.
- Data limits or stale warnings are present but ignored.

## Required Notes

For each task, record:

- context items used
- sources cited
- stale assumptions avoided
- decision changed: yes/no
- human notes
