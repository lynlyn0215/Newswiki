import unittest
import importlib.util
from pathlib import Path

from scripts.build_capabilities import build_chains


REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("capabilities_server", REPO / "mcp/capabilities/server.py")
capabilities_server = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(capabilities_server)

score_items = capabilities_server.score_items
task_terms = capabilities_server.task_terms


class CapabilityRecommendationTests(unittest.TestCase):
    def test_task_terms_ignores_short_words_and_stopwords(self):
        self.assertEqual(task_terms("I want to test the hosted SaaS product"), {"want", "test", "hosted", "saas", "product"})

    def test_product_query_prefers_product_capability_over_unrelated_design(self):
        items = [
            {
                "id": "skill.algorithmic-art",
                "name": "Algorithmic Art",
                "description": "Create visual sketches and generative art.",
                "tags": ["design", "art"],
            },
            {
                "id": "skill.product-discovery",
                "name": "Product Discovery",
                "description": "Evaluate SaaS product ideas, customer scenarios, and validation tests.",
                "tags": ["product", "saas", "market", "research"],
            },
        ]

        results = score_items(items, "hosted SaaS product validation", ["id", "name", "description", "tags"])

        self.assertEqual(results[0]["id"], "skill.product-discovery")

    def test_build_chains_adds_product_discovery_when_research_skills_exist(self):
        chains = build_chains(
            [
                {
                    "id": "skill.deep-research",
                    "name": "Deep Research",
                    "description": "Research competitors and market signals.",
                    "tags": ["research", "market"],
                }
            ]
        )

        self.assertIn("product.discovery", {chain["id"] for chain in chains})


if __name__ == "__main__":
    unittest.main()
