from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from service.app.context_pack import ContextPackBuilder
from service.app.repository import PublicExportRepository
from service.app.search import SearchService


LABEL_LEAK_REPLACEMENTS = {
    "Newswiki-context": "context-assisted",
    "newswiki-context": "context-assisted",
    "Baseline": "comparison answer",
    "baseline": "comparison answer",
    "Treatment": "material-assisted answer",
    "treatment": "material-assisted answer",
    "A/B": "paired comparison",
    "a/b": "paired comparison",
}


def load_fixture(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not data.get("id") or not data.get("task"):
        raise ValueError(f"{path} must include id and task")
    return data


def write_text(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n", encoding="utf-8")


def neutral_materials_prompt(fixture: dict[str, Any], materials: dict[str, Any]) -> str:
    materials_json = json.dumps(materials, ensure_ascii=False, indent=2)
    return f"""
# Eval Prompt

You are evaluating a product/architecture question.

Task:
{fixture["task"]}

Task materials:

```json
{materials_json}
```

Requirements:
- Use this structure:
  - Recommendation
  - Evidence used
  - Freshness/current-fact uncertainty
  - Data limits
  - Verification steps
  - Whether the provided material changed or could change the recommendation
- Use the provided material only when it is relevant.
- If the material is empty or incomplete, say what would need verification.
- Do not invent recent facts. If current platform facts matter and you are not sure, say what would need verification.
- Cite only sources you actually know or can verify in this session. Do not invent citations.
- Respect `data_limits`, `stale_assumption_warnings`, and `what_not_to_assume` when present.
- Keep the answer concise enough to compare against the paired answer.
"""


def control_materials() -> dict[str, Any]:
    return {
        "task_material": {
            "brief_type": "pre_plan",
            "signals": [],
            "knowledge": [],
            "tools": [],
            "sources": [],
            "data_limits": ["No task-specific source material was provided."],
            "stale_assumption_warnings": [],
            "what_not_to_assume": [],
            "suggested_verification_steps": ["Verify current facts if they affect the recommendation."],
            "retrieval_decision": {
                "external_signals": {"status": "not_provided", "needed": None},
                "durable_knowledge": {"status": "not_provided", "needed": None},
                "capability_routing": {"status": "not_provided", "needed": None},
            },
        },
        "data_limits": ["No task-specific source material was provided."],
        "verification_steps": ["Verify current facts if they affect the recommendation."],
    }


def context_materials(pack: dict[str, Any]) -> dict[str, Any]:
    task_material = {
        "brief_type": pack.get("brief_type", "pre_plan"),
        "signals": pack.get("signals", []),
        "knowledge": pack.get("knowledge", []),
        "tools": pack.get("tools", []),
        "sources": pack.get("sources", []),
        "data_limits": pack.get("data_limits", []),
        "stale_assumption_warnings": pack.get("stale_assumption_warnings", []),
        "what_not_to_assume": pack.get("what_not_to_assume", []),
        "suggested_verification_steps": pack.get("suggested_verification_steps", []),
        "retrieval_decision": pack.get("retrieval_decision", {}),
    }
    data_limits = pack.get("data_limits", [])
    verification_steps = pack.get("suggested_verification_steps", [])
    return sanitize_for_scorer(
        {
            "task_material": task_material,
            "data_limits": data_limits,
            "verification_steps": verification_steps,
        }
    )


def sanitize_for_scorer(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize_for_scorer(child) for key, child in value.items()}
    if isinstance(value, list):
        sanitized = [sanitize_for_scorer(child) for child in value]
        return [child for child in sanitized if not is_meta_eval_string(child)]
    if isinstance(value, str):
        sanitized = value
        for old, new in LABEL_LEAK_REPLACEMENTS.items():
            sanitized = sanitized.replace(old, new)
        return sanitized
    return value


def is_meta_eval_string(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return (
        "score" in lowered
        and ("answer a" in lowered or "answer b" in lowered or "a/b" in lowered or "paired comparison" in lowered)
        and ("comparison answer" in lowered or "context-assisted" in lowered)
    )


def scorecard(fixture: dict[str, Any]) -> str:
    return f"""
# Manual A/B Eval Result

Task ID: {fixture["id"]}
Task: {fixture["task"]}
Agent:
Date:

## Scores

| Dimension | Answer A 0-2 | Answer B 0-2 | Notes |
|---|---:|---:|---|
| Task relevance |  |  |  |
| Freshness |  |  |  |
| Source use |  |  |  |
| Stale assumption avoided |  |  |  |
| Decision impact |  |  |  |
| Data limits honesty |  |  |  |
| Total |  |  |  |

Winner: A/B/tie
Improved: yes/no
Stale assumption avoided: yes/no
Decision changed: yes/no
Unblinded after scoring: yes/no

## Context Items Used

-

## Sources Cited

-

## Answer A Summary

-

## Answer B Summary

-

## Human Notes

-
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare a manual Newswiki A/B evaluation run directory.")
    parser.add_argument("fixture", type=Path, help="Path to eval/tasks/*.json")
    parser.add_argument("--export-dir", type=Path, default=ROOT / "examples" / "public")
    parser.add_argument("--out-dir", type=Path, default=ROOT / "eval" / "runs")
    parser.add_argument("--token-budget", type=int, default=1200)
    args = parser.parse_args()

    fixture = load_fixture(args.fixture)
    repository = PublicExportRepository(args.export_dir)
    builder = ContextPackBuilder(SearchService(repository))
    pack = builder.build(fixture["task"], topic=fixture.get("topic"), token_budget=args.token_budget).to_dict()

    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    run_dir = args.out_dir / f"{stamp}-{fixture['id']}"
    run_dir.mkdir(parents=True, exist_ok=False)

    prompts = [
        ("control", neutral_materials_prompt(fixture, control_materials())),
        ("context", neutral_materials_prompt(fixture, context_materials(pack))),
    ]
    random.shuffle(prompts)
    label_key = {f"answer_{index}": label for index, (label, _prompt) in zip(("a", "b"), prompts)}
    audit_dir = run_dir / "_audit"
    audit_dir.mkdir()

    (run_dir / "fixture.json").write_text(json.dumps(fixture, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (audit_dir / "context_material.json").write_text(json.dumps(pack, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_text(audit_dir / "control_prompt.md", neutral_materials_prompt(fixture, control_materials()))
    write_text(audit_dir / "context_prompt.md", neutral_materials_prompt(fixture, context_materials(pack)))
    for index, (_label, prompt) in zip(("a", "b"), prompts):
        write_text(run_dir / f"answer_{index}_prompt.md", prompt)
    (audit_dir / "label_key.json").write_text(json.dumps(label_key, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_text(run_dir / "scorecard.md", scorecard(fixture))

    print(
        json.dumps(
            {
                "ok": True,
                "run_dir": str(run_dir),
                "blind_prompts": ["answer_a_prompt.md", "answer_b_prompt.md"],
                "label_key": "_audit/label_key.json",
                "signals": len(pack["signals"]),
                "sources": len(pack["sources"]),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
