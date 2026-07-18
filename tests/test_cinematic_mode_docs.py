import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CinematicModeDocsTests(unittest.TestCase):
    def read(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_routes_cinematic_mode(self):
        skill = self.read("SKILL.md")
        self.assertIn("## Cinematic Mode Router", skill)
        self.assertIn("references/cinematic-directing.md", skill)
        self.assertIn("rhythm preset A", skill)

    def test_cinematic_reference_contains_approved_contract(self):
        reference = self.read("references/cinematic-directing.md")
        required_tokens = (
            "concept_mode",
            "screenplay_mode",
            "novel_mode_reserved",
            "narrative_clarity",
            "continuity_integrity",
            "16:9",
            "9:16",
            "A narrative-first cinematic",
            "B spectacle-heavy",
            "C performance-first",
            "key_shot_review",
            "local_repair",
        )
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_stage_references_expose_the_cinematic_contract(self):
        expected_tokens = {
            "references/story-directing.md": (
                "cinematic_six_beats",
                "concept_mode",
                "screenplay_mode",
            ),
            "references/continuity-storyboard.md": (
                "rhythm_role",
                "state_dependencies",
                "state_before",
                "state_after",
                "composition_16x9",
                "recomposition_9x16",
                "platform_capability_needs",
            ),
            "references/prompt-compiler.md": (
                "global_lock_block",
                "shot_direction_block",
                "platform_compile_block",
                "direction_variants",
                "approval_status",
            ),
            "references/output-contract.md": (
                "project_brief.cinematic_mode",
                "narrative_clarity",
                "continuity_integrity",
                "direction_variants",
                "non_executable",
            ),
        }
        for path, tokens in expected_tokens.items():
            content = self.read(path)
            for token in tokens:
                with self.subTest(path=path, token=token):
                    self.assertIn(token, content)

    def test_stage_contract_requires_dag_handoff_and_precompile_gates(self):
        continuity = self.read("references/continuity-storyboard.md")
        for token in (
            "有向无环图",
            "只允许引用更早的镜头",
            "state_after",
            "state_before",
            "依赖交接冲突",
        ):
            with self.subTest(document="continuity", token=token):
                self.assertIn(token, continuity)

        for relative_path in (
            "references/prompt-compiler.md",
            "references/output-contract.md",
        ):
            document = self.read(relative_path)
            for token in (
                "direction_variants",
                "approval_status",
                "draft",
                "blocked",
                "final",
                "approved",
            ):
                with self.subTest(document=relative_path, token=token):
                    self.assertIn(token, document)

    def test_cinematic_duration_is_limited_to_thirty_to_sixty_seconds(self):
        for relative_path in ("SKILL.md", "references/cinematic-directing.md"):
            with self.subTest(relative_path=relative_path):
                document = self.read(relative_path)
                self.assertIn("30–60", document)
                self.assertNotIn("30–90", document)

    def test_happyhorse_adapter_is_verified_and_mode_specific(self):
        adapters = self.read("references/model-adapters.md")
        required_tokens = (
            "## HappyHorse on Alibaba Cloud Model Studio",
            "happyhorse-1.1-t2v",
            "happyhorse-1.1-i2v",
            "happyhorse-1.1-r2v",
            "create_task_then_poll",
            "result_url_valid_for_24_hours",
            "i2v_request_schema",
            "r2v_request_schema",
        )
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, adapters)

        self.assertIn("3–15 秒", adapters)
        self.assertNotIn("3–5 秒", adapters)

        manual_only_status = (
            "**cinematic_adapter_status**："
            "`manual_only_until_official_request_schema_is_readable`。"
        )
        self.assertEqual(adapters.count(manual_only_status), 2)


if __name__ == "__main__":
    unittest.main()
