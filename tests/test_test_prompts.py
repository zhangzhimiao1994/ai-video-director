import json
import unittest
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1] / "test-prompts.json"


class TestPromptCatalogTests(unittest.TestCase):
    def setUp(self):
        self.prompts = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_prompt_ids_are_unique_and_records_are_complete(self):
        ids = [record["id"] for record in self.prompts]
        self.assertEqual(len(ids), len(set(ids)))
        for record in self.prompts:
            with self.subTest(prompt_id=record["id"]):
                self.assertIsInstance(record["prompt"], str)
                self.assertTrue(record["prompt"].strip())
                self.assertIsInstance(record["expected"], str)
                self.assertTrue(record["expected"].strip())

    def test_cinematic_regression_prompts_are_present(self):
        ids = {record["id"] for record in self.prompts}
        self.assertTrue(
            {
                "P4-cinematic-concept-dual-aspect",
                "P5-cinematic-screenplay-adaptation",
                "P6-cinematic-novel-reserved",
                "P7-cinematic-hard-gates",
            }.issubset(ids)
        )


if __name__ == "__main__":
    unittest.main()
