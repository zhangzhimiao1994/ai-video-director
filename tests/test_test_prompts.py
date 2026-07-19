import json
import unittest
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1] / "test-prompts.json"


class PromptCatalogContractTests(unittest.TestCase):
    def setUp(self):
        self.prompts = json.loads(CATALOG.read_text(encoding="utf-8"))
        self.prompts_by_id = {record["id"]: record for record in self.prompts}

    def test_prompt_ids_are_unique_and_records_are_complete(self):
        ids = [record["id"] for record in self.prompts]
        self.assertEqual(len(ids), len(set(ids)))
        for record in self.prompts:
            with self.subTest(prompt_id=record["id"]):
                self.assertIsInstance(record["id"], str)
                self.assertTrue(record["id"].strip())
                self.assertIsInstance(record["prompt"], str)
                self.assertTrue(record["prompt"].strip())
                self.assertIsInstance(record["expected"], str)
                self.assertTrue(record["expected"].strip())

    def test_catalog_declares_all_cinematic_contract_cases(self):
        ids = {record["id"] for record in self.prompts}
        self.assertTrue(
            {
                "P4-cinematic-concept-dual-aspect",
                "P5-cinematic-screenplay-adaptation",
                "P6-cinematic-novel-reserved",
                "P7-cinematic-hard-gates",
            }.issubset(ids)
        )

    def test_catalog_cinematic_records_declare_required_semantics(self):
        required_tokens = {
            "P4-cinematic-concept-dual-aspect": {
                "prompt": (
                    "concept_mode",
                    "45秒",
                    "16:9",
                    "9:16",
                    "Kling",
                    "Seedance",
                    "HappyHorse",
                ),
                "expected": ("rhythm preset A", "manual-only", "ready为false"),
            },
            "P5-cinematic-screenplay-adaptation": {
                "prompt": (
                    "动机",
                    "因果",
                    "行动",
                    "对白",
                    "妹妹主动留下",
                    "哥哥独自逃生",
                ),
                "expected": (
                    "screenplay_mode",
                    "压缩",
                    "锁定事实",
                    "A/B/C",
                    "对白含义",
                    "事件顺序",
                    "结局不被改写",
                ),
            },
            "P6-cinematic-novel-reserved": {
                "prompt": ("三十万字小说全文",),
                "expected": (
                    "novel_mode_reserved",
                    "只问一个实质问题",
                    "自包含",
                    "不提前编造",
                ),
            },
            "P7-cinematic-hard-gates": {
                "prompt": ("白发少年", "红发成年女人", "左手", "右手", "Seedance"),
                "expected": (
                    "硬门",
                    "Canon",
                    "narrative_clarity",
                    "continuity_integrity",
                    "不生成最终平台提示词",
                    "draft/blocked",
                    "blocked/non_executable",
                    "Seedance字段不猜测",
                ),
            },
        }

        for prompt_id, fields in required_tokens.items():
            record = self.prompts_by_id[prompt_id]
            for field, tokens in fields.items():
                with self.subTest(prompt_id=prompt_id, field=field):
                    for token in tokens:
                        self.assertIn(token, record[field])

    def test_catalog_declares_finished_film_contract_cases(self):
        required_tokens = {
            "P8-finished-film-dual-aspect": (
                "media_bindings",
                "edit_master_plan",
                "16:9",
                "9:16",
            ),
            "P9-finished-film-missing-media": (
                "rough cut",
                "final master",
                "阻断",
            ),
            "P10-finished-film-multi-nle-ai": (
                "剪映",
                "OTIO/FCPXML",
                "dry-run",
                "操作授权",
            ),
        }

        for prompt_id, tokens in required_tokens.items():
            expected = self.prompts_by_id[prompt_id]["expected"]
            with self.subTest(prompt_id=prompt_id):
                for token in tokens:
                    self.assertIn(token, expected)


if __name__ == "__main__":
    unittest.main()
