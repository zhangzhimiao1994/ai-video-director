import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CinematicModeDocsTests(unittest.TestCase):
    def read(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def contract_line(self, text, field):
        return next((line for line in text.splitlines() if field in line), "")

    def test_skill_identity_is_aibiandao(self):
        skill = self.read("SKILL.md")
        agent_metadata = self.read("agents/openai.yaml")
        self.assertTrue(skill.startswith("---\nname: aibiandao\n"))
        self.assertIn('display_name: "aibiandao"', agent_metadata)
        self.assertIn("$aibiandao", agent_metadata)
        self.assertNotIn("$ai-video-director", agent_metadata)

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
            "只允许引用 `sequence` 更小的镜头",
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

    def test_cinematic_job_source_contract_binds_lock_and_aspect_direction(self):
        prompt_contract = self.read("references/prompt-compiler.md")
        output_contract = self.read("references/output-contract.md")
        for document in (prompt_contract, output_contract):
            for token in (
                "global_lock_source",
                "direction_source",
                "composition_16x9",
                "legacy-only",
            ):
                with self.subTest(token=token):
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

    def test_cinematic_direction_defines_genre_aware_motion_and_coverage(self):
        reference = self.read("references/cinematic-directing.md")
        for token in (
            "genre-aware shot density",
            "coverage_role",
            "action",
            "reaction",
            "consequence",
            "kinetic_profile",
            "subject",
            "performance",
            "camera",
            "environment",
            "intentional_hold",
            "hold_reason",
            "evidence_refs",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_story_direction_requires_action_reaction_consequence_and_sound_cause(self):
        reference = self.read("references/story-directing.md")
        for token in (
            "action",
            "reaction",
            "consequence",
            "sound_trigger",
            "audio_presence_and_structure",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_storyboard_owns_coverage_transition_and_identity_contracts(self):
        reference = self.read("references/continuity-storyboard.md")
        for token in (
            "coverage_role",
            "kinetic_profile",
            "transition_contract",
            "visual_precondition",
            "audio_bridge_cue_id",
            "fallback",
            "fulfillment_status",
            "identity_profile",
            "identity_profile_id",
            "face_anchors",
            "body_anchors",
            "hair_anchors",
            "fixed_accessories",
            "signature_effect_anchors",
            "reference_asset_ids",
            "forbidden_drift",
            "approval_status",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_prompt_compiler_owns_performance_physics_and_model_lock(self):
        reference = self.read("references/prompt-compiler.md")
        for token in (
            "body path",
            "weight shift",
            "reaction",
            "counterforce",
            "environment response",
            "static poster",
            "character_model_bindings",
            "identity_profile_id",
            "model_family",
            "model_version",
            "identity_binding_method",
            "reference_input_ids",
            "lock_status",
            "A/B",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_skill_failure_matrix_contains_all_cinematic_recovery_rows(self):
        skill = self.read("SKILL.md")
        expected_rows = (
            ("static poster poses", "`action`/`reaction`/`consequence`", "Block and regenerate"),
            ("storyboard transition dropped", "tested fallback", "Do not normalize every boundary"),
            ("missing movie audio", "cleared audio structure", "silent_form_authorization"),
            ("particles/background-only motion", "subject/performance evidence", "Block the cinematic master"),
            ("rough cut relabeled final", "Preserve the rough version", "Never copy or rename"),
            ("face/body/hair/accessory drift", "approved identity profile", "Block affected jobs and edit units"),
            ("model version/subject-binding drift", "approved migration A/B test", "Never mix unverified"),
        )
        skill_lines = skill.splitlines()
        for trigger, repair, blocked_outcome in expected_rows:
            with self.subTest(trigger=trigger):
                row = next((line for line in skill_lines if trigger in line), "")
                self.assertIn(repair, row)
                self.assertIn(blocked_outcome, row)

    def test_storyboard_coverage_role_lists_the_complete_directing_vocabulary(self):
        reference = self.read("references/continuity-storyboard.md")
        coverage_contract = self.contract_line(reference, "`coverage_role`")
        for role in (
            "setup",
            "anticipation",
            "action",
            "impact",
            "reaction",
            "consequence",
            "transition",
            "aftermath",
        ):
            with self.subTest(role=role):
                self.assertIn(f"`{role}`", coverage_contract)

    def test_storyboard_kinetic_profile_names_every_declared_motion_field(self):
        reference = self.read("references/continuity-storyboard.md")
        kinetic_contract = self.contract_line(reference, "`kinetic_profile`")
        for field in (
            "subject_motion",
            "performance_change",
            "camera_motion",
            "environment_motion",
            "motion_layers_required",
            "intentional_hold",
            "hold_reason",
            "acceptance_evidence",
        ):
            with self.subTest(field=field):
                self.assertIn(f"`{field}`", kinetic_contract)

    def test_storyboard_transition_contract_declares_intent_not_edit_fulfillment(self):
        reference = self.read("references/continuity-storyboard.md")
        transition_contract = self.contract_line(reference, "`transition_contract`")
        for field in (
            "type",
            "visual_precondition",
            "incoming_match",
            "duration_frames",
            "audio_bridge_cue_id",
            "story_reason",
            "fallback",
        ):
            with self.subTest(field=field):
                self.assertIn(f"`{field}`", transition_contract)
        self.assertNotIn("fulfillment_status", transition_contract)
        self.assertNotIn("evidence_refs", transition_contract)
        self.assertIn("storyboard declaration layer", reference)
        self.assertIn("editing fulfillment layer", reference)
        self.assertIn("`fulfillment_status` and `evidence_refs`", reference)

    def test_output_contract_places_storyboard_directing_fields_on_storyboard(self):
        output_contract = self.read("references/output-contract.md")
        storyboard_start = output_contract.index("## 7. `storyboard`")
        storyboard_end = output_contract.index("## 8.", storyboard_start)
        storyboard_section = output_contract[storyboard_start:storyboard_end]
        for field in ("coverage_role", "kinetic_profile", "transition_contract"):
            with self.subTest(field=field):
                self.assertIn(f"`{field}`", storyboard_section)
        self.assertIn("`acceptance_evidence` is a non-empty string", storyboard_section)
        self.assertNotIn("`fulfillment_status`", storyboard_section)

    def test_continuity_identity_distinguishes_concept_draft_from_production(self):
        reference = self.read("references/continuity-storyboard.md")
        identity_line = self.contract_line(reference, "`identity_profile`")
        self.assertIn("concept draft", identity_line)
        self.assertIn("production cinematic package", identity_line)
        self.assertIn("`validate_package`", identity_line)
        self.assertIn("`approved`", identity_line)
        self.assertIn("pending", identity_line)
        self.assertIn("cannot be `approved`", identity_line)

    def test_cinematic_direction_uses_storyboard_acceptance_evidence(self):
        reference = self.read("references/cinematic-directing.md")
        kinetic_line = self.contract_line(reference, "`kinetic_profile`")
        self.assertIn("`acceptance_evidence`", kinetic_line)
        self.assertNotIn("`evidence_refs`", kinetic_line)
        self.assertIn("editing audit", reference)
        self.assertIn("`evidence_refs`", reference)


if __name__ == "__main__":
    unittest.main()
