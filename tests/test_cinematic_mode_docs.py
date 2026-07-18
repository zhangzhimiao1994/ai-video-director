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


if __name__ == "__main__":
    unittest.main()
