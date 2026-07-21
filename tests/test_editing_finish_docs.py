import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EditingFinishDocsTests(unittest.TestCase):
    def read_required(self, relative_path):
        path = ROOT / relative_path
        self.assertTrue(path.is_file(), f"missing required file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def assert_contract_tokens(self, text, tokens):
        missing = [token for token in tokens if token not in text]
        self.assertFalse(missing, f"missing contract tokens: {missing}")

    def test_skill_routes_finished_film_requests(self):
        skill = self.read_required("SKILL.md")
        self.assert_contract_tokens(
            skill,
            (
                "## Finished-Film Editing Router",
                "references/editing-finish.md",
                "edit_master_plan",
                "operation authorization",
            ),
        )

    def test_editing_reference_exposes_complete_contract(self):
        reference = self.read_required("references/editing-finish.md")
        self.assert_contract_tokens(
            reference,
            (
                "media_bindings",
                "timeline_in_seconds",
                "source_in_seconds",
                "cut_reason",
                "audio_tracks",
                "text_tracks",
                "look_plan",
                "16:9",
                "9:16",
                "rough_cut",
                "fine_cut",
                "final_master",
                "jianying_capcut",
                "manual_or_unverified",
            ),
        )

    def test_output_contract_keeps_legacy_package_optional(self):
        output_contract = self.read_required("references/output-contract.md")
        self.assert_contract_tokens(
            output_contract,
            (
                "optional `edit_master_plan`",
                "legacy ten-object package",
                "derived from the same edit Canon",
            ),
        )

    def test_editing_docs_define_handoff_and_canon_refinements(self):
        docs = "\n".join(
            (
                self.read_required("SKILL.md"),
                self.read_required("references/editing-finish.md"),
            )
        )
        self.assert_contract_tokens(
            docs,
            (
                "non-executable handoff artifacts",
                "external media, project, or render writes",
                "manifest and exact version directory",
                "delivery_specs[].version_role",
                "every requested delivery",
                "version_id",
                "artifact_refs",
                "validation_refs",
                "change_summary",
                "standalone project ID",
                "edit-unit `locked_event_ids`",
                "binding_scope",
                "target_id",
            ),
        )

    def test_skill_enforces_cinematic_finish_hard_gate(self):
        skill = self.read_required("SKILL.md")
        self.assert_contract_tokens(
            skill,
            (
                "## Cinematic Finish Hard Gate",
                "--require-cinematic",
                "ppt_risk_flags",
                "cinematic_ready",
                "rendered",
                "rough_cut",
                "story → storyboard → prompt/media regeneration → timeline → sound",
            ),
        )

    def test_editing_reference_separates_render_and_creative_readiness(self):
        reference = self.read_required("references/editing-finish.md")
        self.assert_contract_tokens(
            reference,
            (
                "source media and edit units are separate",
                "transition_fulfillment",
                "audio_presence_and_structure",
                "cinematic_validation",
                "cinematic_ready",
                "ppt_risk_flags",
                "creative_ready: false",
            ),
        )
        self.assertIn("`rendered` does not equal cinematic readiness", reference)

    def test_output_contract_exposes_optional_cinematic_finish_report(self):
        output_contract = self.read_required("references/output-contract.md")
        self.assert_contract_tokens(
            output_contract,
            (
                "optional `cinematic_validation`",
                "14 required fields",
                "character_identity_integrity",
                "identity_integrity",
                "action_reaction_coverage",
                "kinetic_profile_audit",
                "transition_fulfillment",
                "ppt_risk_flags",
                "cinematic_ready",
                "--require-cinematic",
                "legacy compatibility",
            ),
        )


if __name__ == "__main__":
    unittest.main()
