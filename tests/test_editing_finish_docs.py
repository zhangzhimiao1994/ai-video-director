import unittest
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from cinematic_validation import CINEMATIC_FIELDS


class EditingFinishDocsTests(unittest.TestCase):
    def read_required(self, relative_path):
        path = ROOT / relative_path
        self.assertTrue(path.is_file(), f"missing required file: {relative_path}")
        return path.read_text(encoding="utf-8")

    def assert_contract_tokens(self, text, tokens):
        missing = [token for token in tokens if token not in text]
        self.assertFalse(missing, f"missing contract tokens: {missing}")

    def section(self, text, heading):
        self.assertIn(heading, text, f"missing required section: {heading}")
        start = text.index(heading) + len(heading)
        next_heading = text.find("\n### ", start)
        next_major_heading = text.find("\n## ", start)
        candidates = [index for index in (next_heading, next_major_heading) if index >= 0]
        end = min(candidates) if candidates else len(text)
        return text[start:end]

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

    def test_output_contract_cinematic_field_set_matches_validator_constant(self):
        output_contract = self.read_required("references/output-contract.md")
        extension = self.section(output_contract, "## Optional Finished-Film Extension")
        field_sentence = next(
            line for line in extension.splitlines() if "exactly 14 required fields" in line
        )
        documented = tuple(
            token
            for token in re.findall(r"`([^`]+)`", field_sentence)
            if token in CINEMATIC_FIELDS
        )
        self.assertEqual(documented, CINEMATIC_FIELDS)

    def test_cinematic_acceptance_separates_plan_checks_from_actual_film_evidence(self):
        reference = self.read_required("references/editing-finish.md")
        plan_acceptance = self.section(reference, "### Plan acceptance")
        self.assert_contract_tokens(
            plan_acceptance,
            (
                "timeline structure",
                "coverage",
                "cut points",
                "transitions",
                "audio",
                "prohibited items",
            ),
        )

        actual_acceptance = self.section(reference, "### Actual-film acceptance")
        self.assert_contract_tokens(
            actual_acceptance,
            (
                "ffprobe",
                "FFmpeg or equivalent output probe",
                "streams",
                "duration",
                "cut/frame change",
                "contact sheet",
                "visual review",
                "character action",
                "performance change",
                "repeated poses",
                "actual transitions",
            ),
        )

    def test_actual_motion_review_rejects_decorative_pixel_change(self):
        reference = self.read_required("references/editing-finish.md")
        actual_acceptance = self.section(reference, "### Actual-film acceptance")
        self.assertIn("pixel change is not performance", actual_acceptance)
        for false_positive in ("particles", "light beams", "background motion"):
            with self.subTest(false_positive=false_positive):
                self.assertIn(false_positive, actual_acceptance)
        self.assertIn("cannot alone pass `source_motion_review`", actual_acceptance)

    def test_actual_master_blocks_when_required_review_tools_are_unavailable(self):
        reference = self.read_required("references/editing-finish.md")
        actual_acceptance = self.section(reference, "### Actual-film acceptance")
        self.assertIn("tooling is unavailable", actual_acceptance)
        self.assertIn("`blocked` or `manual_review_required`", actual_acceptance)
        self.assertIn("never claim actual-film acceptance", actual_acceptance)

    def test_actual_film_acceptance_names_executable_readiness_evidence(self):
        reference = self.read_required("references/editing-finish.md")
        plan_acceptance = self.section(reference, "### Plan acceptance")
        actual_acceptance = self.section(reference, "### Actual-film acceptance")
        self.assertIn("plan audits passed", plan_acceptance)
        self.assertIn("does not set `cinematic_ready: true`", plan_acceptance)
        for field in (
            "actual_output_review_status",
            "reviewed_delivery_ids",
            "frame_change_evidence_refs",
            "contact_sheet_evidence_refs",
        ):
            with self.subTest(field=field):
                self.assertIn(f"`{field}`", actual_acceptance)
                self.assertNotIn(f"`{field}`", plan_acceptance)
        self.assertIn("`plan_status: rendered`", actual_acceptance)
        self.assertIn("`execution.review_evidence`", actual_acceptance)
        self.assertIn("not free-form strings", actual_acceptance)
        self.assertIn("verified `tool_evidence_ref`", actual_acceptance)
        self.assertIn("each requested delivery", actual_acceptance)

    def test_skill_only_activates_cinematic_gate_for_declared_cinematic_intent(self):
        skill = self.read_required("SKILL.md")
        hard_gate = self.section(skill, "## Cinematic Finish Hard Gate")
        for trigger in ("cinematic", "movie", "blockbuster", "电影感"):
            self.assertIn(trigger, hard_gate)
        self.assertIn("existing `cinematic_mode`", hard_gate)
        self.assertIn("ordinary finished output", hard_gate)
        self.assertIn("does not activate `--require-cinematic`", hard_gate)


if __name__ == "__main__":
    unittest.main()
