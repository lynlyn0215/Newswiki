from __future__ import annotations

import unittest

from eval.prepare_ab_run import context_materials, control_materials, neutral_materials_prompt


class PrepareAbRunTest(unittest.TestCase):
    def test_scorer_facing_prompt_uses_neutral_framing(self) -> None:
        fixture = {"id": "task-1", "task": "Should the product change direction?"}
        prompt = neutral_materials_prompt(fixture, control_materials()).lower()

        forbidden = [
            "without a newswiki context pack",
            "state that no newswiki evidence pack was provided",
            "evidence pack",
            "baseline",
            "newswiki-context",
        ]
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, prompt)

    def test_context_materials_use_same_top_level_envelope_as_control(self) -> None:
        pack = {
            "brief_type": "pre_plan",
            "signals": [],
            "knowledge": [],
            "tools": [],
            "sources": [],
            "data_limits": [],
            "stale_assumption_warnings": [],
            "what_not_to_assume": [],
            "suggested_verification_steps": [],
            "retrieval_decision": {},
        }

        self.assertEqual(set(control_materials()), set(context_materials(pack)))
        self.assertEqual(set(control_materials()["task_material"]), set(context_materials(pack)["task_material"]))

    def test_context_materials_remove_eval_label_leaks(self) -> None:
        fixture = {"id": "task-1", "task": "Should the product change direction?"}
        pack = {
            "brief_type": "pre_plan",
            "signals": [],
            "knowledge": [
                {
                    "id": "knowledge-eval",
                    "title": "Evaluation gate",
                    "key_points": ["Score baseline and Newswiki-context answers separately."],
                    "summary": "Compare baseline with Newswiki-context output.",
                }
            ],
            "tools": [],
            "sources": [],
            "data_limits": [],
            "stale_assumption_warnings": [],
            "what_not_to_assume": [],
            "suggested_verification_steps": [],
            "retrieval_decision": {},
        }
        prompt = neutral_materials_prompt(fixture, context_materials(pack)).lower()

        self.assertNotIn("baseline", prompt)
        self.assertNotIn("newswiki-context", prompt)
        self.assertNotIn("score baseline", prompt)


if __name__ == "__main__":
    unittest.main()
