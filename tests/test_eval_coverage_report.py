from __future__ import annotations

import unittest

from eval.coverage_report import explicit_check_match


class CoverageReportTest(unittest.TestCase):
    def test_explicit_check_does_not_pass_on_field_presence_alone(self) -> None:
        item = {
            "id": "signal-1",
            "title": "Unrelated signal",
            "stale_after": "2026-06-01",
        }
        check = {
            "label": "stale metadata",
            "fields_present": ["stale_after"],
        }

        self.assertFalse(explicit_check_match(check, item))

    def test_explicit_check_requires_terms_and_fields_when_both_are_present(self) -> None:
        item = {
            "id": "signal-1",
            "title": "Codex release changes workflow assumptions",
            "decision_impact": "Verify model release behavior before changing the roadmap.",
        }
        check = {
            "label": "model release impact",
            "all_terms": ["codex", "workflow"],
            "fields_present": ["decision_impact"],
        }

        self.assertTrue(explicit_check_match(check, item))


if __name__ == "__main__":
    unittest.main()
