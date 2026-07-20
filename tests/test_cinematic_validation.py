import copy
import io
import json
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures" / "editing"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_edit_plan import main, validate_edit_plan


CINEMATIC_FIELDS = (
    "declared_mode",
    "genre",
    "content_consistency",
    "character_identity_integrity",
    "action_reaction_coverage",
    "kinetic_profile_audit",
    "shot_scale_and_composition_variety",
    "transition_fulfillment",
    "audio_presence_and_structure",
    "static_hold_audit",
    "source_motion_review",
    "ppt_risk_flags",
    "evidence_refs",
    "cinematic_ready",
)

AUDIT_FIELDS = (
    "content_consistency",
    "character_identity_integrity",
    "action_reaction_coverage",
    "kinetic_profile_audit",
    "shot_scale_and_composition_variety",
    "transition_fulfillment",
    "audio_presence_and_structure",
    "static_hold_audit",
    "source_motion_review",
)


def load_plan(name):
    with (FIXTURES / name).open("r", encoding="utf-8") as source:
        return json.load(source)


def edit_units(plan, timeline_index=0):
    return plan["timelines"][timeline_index]["video_tracks"][0][
        "edit_units"
    ]


def all_edit_unit_ids(plan):
    return {
        unit["edit_unit_id"]
        for timeline in plan["timelines"]
        for unit in timeline["video_tracks"][0]["edit_units"]
    }


def all_boundary_pairs(plan):
    pairs = set()
    for timeline in plan["timelines"]:
        units = timeline["video_tracks"][0]["edit_units"]
        pairs.update(
            (left["edit_unit_id"], right["edit_unit_id"])
            for left, right in zip(units, units[1:])
        )
    return pairs


def run_cli(args):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        try:
            exit_code = main([str(arg) for arg in args])
        except SystemExit as exc:
            exit_code = exc.code
    return exit_code, stdout.getvalue(), stderr.getvalue()


class CinematicValidationTests(unittest.TestCase):
    def assert_deterministic_errors(
        self, plan, expected_errors, *, require_cinematic=True
    ):
        kwargs = (
            {"require_cinematic": True} if require_cinematic else {}
        )
        first = validate_edit_plan(copy.deepcopy(plan), **kwargs)
        second = validate_edit_plan(copy.deepcopy(plan), **kwargs)

        self.assertEqual(first, second)
        for expected in expected_errors:
            self.assertIn(expected, first)
        cinematic = plan.get("cinematic_validation")
        if (
            isinstance(cinematic, dict)
            and cinematic.get("cinematic_ready") is True
            and first
        ):
            self.assertIn(
                "cinematic_validation: cinematic_ready cannot be true while "
                "cinematic blockers remain",
                first,
            )
        return first

    def test_legacy_plan_remains_valid_without_cinematic_gate(self):
        self.assertEqual(validate_edit_plan(load_plan("valid_plan.json")), [])

    def test_require_cinematic_needs_canonical_object(self):
        self.assert_deterministic_errors(
            load_plan("valid_plan.json"),
            ("cinematic_validation: required for cinematic delivery",),
        )

    def test_all_cinematic_fields_are_required(self):
        self.assertEqual(len(CINEMATIC_FIELDS), 14)
        for field in CINEMATIC_FIELDS:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                del plan["cinematic_validation"][field]

                self.assert_deterministic_errors(
                    plan,
                    (f"cinematic_validation: missing field {field}",),
                )

    def test_mode_genre_and_top_level_evidence_are_strict(self):
        cases = (
            (
                "declared_mode",
                "social",
                "cinematic_validation.declared_mode: must be cinematic",
            ),
            (
                "genre",
                "",
                "cinematic_validation.genre: must be a non-empty string",
            ),
            (
                "evidence_refs",
                [],
                "cinematic_validation.evidence_refs: must be a non-empty "
                "list of strings",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                plan["cinematic_validation"][field] = value

                self.assert_deterministic_errors(plan, (expected,))

    def test_every_audit_status_is_required_valid_and_blocking(self):
        for audit in AUDIT_FIELDS:
            cases = (
                (
                    "missing",
                    None,
                    f"cinematic_validation.{audit}: missing field status",
                ),
                (
                    "invalid",
                    "approved",
                    f"cinematic_validation.{audit}.status: must be passed, "
                    "failed, or manual_review_required",
                ),
                (
                    "failed",
                    "failed",
                    f"cinematic_validation.{audit}: status failed blocks "
                    "cinematic readiness",
                ),
                (
                    "manual_review_required",
                    "manual_review_required",
                    f"cinematic_validation.{audit}: status "
                    "manual_review_required blocks cinematic readiness",
                ),
            )
            for case_name, status, expected in cases:
                with self.subTest(audit=audit, case=case_name):
                    plan = copy.deepcopy(
                        load_plan("cinematic_valid_plan.json")
                    )
                    audit_object = plan["cinematic_validation"][audit]
                    if case_name == "missing":
                        del audit_object["status"]
                    else:
                        audit_object["status"] = status

                    self.assert_deterministic_errors(plan, (expected,))

    def test_content_consistency_requires_traceable_locked_events(self):
        cases = (
            (
                "locked_event_ids",
                "cinematic_validation.content_consistency.locked_event_ids: "
                "must be a non-empty list of strings",
            ),
            (
                "evidence_refs",
                "cinematic_validation.content_consistency.evidence_refs: "
                "must be a non-empty list of strings",
            ),
        )
        for field, expected in cases:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                plan["cinematic_validation"]["content_consistency"][field] = []

                self.assert_deterministic_errors(plan, (expected,))

    def test_character_identity_requires_locks_evidence_and_no_drift(self):
        cases = (
            (
                "identity_profile_ids",
                [],
                "cinematic_validation.character_identity_integrity."
                "identity_profile_ids: must be a non-empty list of strings",
            ),
            (
                "model_lock_refs",
                [],
                "cinematic_validation.character_identity_integrity."
                "model_lock_refs: must be a non-empty list of strings",
            ),
            (
                "evidence_refs",
                [],
                "cinematic_validation.character_identity_integrity."
                "evidence_refs: must be a non-empty list of strings",
            ),
            (
                "drift_conflicts",
                ["face_drift"],
                "cinematic_validation.character_identity_integrity."
                "drift_conflicts: must be empty",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                identity = plan["cinematic_validation"][
                    "character_identity_integrity"
                ]
                identity[field] = value

                self.assert_deterministic_errors(plan, (expected,))

    def test_action_events_require_all_key_fields(self):
        fields = ("event_id", "required_roles", "edit_unit_ids", "status")
        for field in fields:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                event = plan["cinematic_validation"][
                    "action_reaction_coverage"
                ]["events"][0]
                del event[field]

                self.assert_deterministic_errors(
                    plan,
                    (
                        "cinematic_validation.action_reaction_coverage.events "
                        f"item 1: missing field {field}",
                    ),
                )

    def test_action_events_require_action_reaction_and_consequence(self):
        for missing_role in ("action", "reaction", "consequence"):
            with self.subTest(missing_role=missing_role):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                event = plan["cinematic_validation"][
                    "action_reaction_coverage"
                ]["events"][0]
                event["required_roles"].remove(missing_role)

                self.assert_deterministic_errors(
                    plan,
                    (
                        "cinematic_validation.action_reaction_coverage.events "
                        "item 1.required_roles: must include action, reaction, "
                        "and consequence",
                    ),
                )

    def test_kinetic_layers_must_be_distinct_and_valid(self):
        cases = (
            ("single", ["environment"]),
            ("duplicate", ["environment", "environment"]),
            ("invalid", ["environment", "particles"]),
        )
        expected = (
            "cinematic_validation.kinetic_profile_audit.edit_units item 1."
            "motion_layers: requires at least two distinct valid motion layers "
            "unless intentional_hold is evidenced"
        )
        for case_name, layers in cases:
            with self.subTest(case=case_name):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                record = plan["cinematic_validation"][
                    "kinetic_profile_audit"
                ]["edit_units"][0]
                record["motion_layers"] = layers
                record["intentional_hold"] = False
                record["hold_reason"] = None

                self.assert_deterministic_errors(plan, (expected,))

    def test_evidenced_intentional_hold_is_allowed(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        record = plan["cinematic_validation"]["kinetic_profile_audit"][
            "edit_units"
        ][0]
        record["motion_layers"] = ["environment"]
        record["intentional_hold"] = True
        record["hold_reason"] = "hold for the reaction beat"
        record["evidence_refs"] = ["STORY-BEAT-HOLD-01"]

        self.assertEqual(
            validate_edit_plan(plan, require_cinematic=True),
            [],
        )

    def test_intentional_hold_requires_reason_and_evidence(self):
        cases = (
            ("hold_reason", None),
            ("evidence_refs", []),
        )
        expected = (
            "cinematic_validation.kinetic_profile_audit.edit_units item 1."
            "intentional_hold: hold_reason and evidence_refs are required"
        )
        for field, value in cases:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                record = plan["cinematic_validation"][
                    "kinetic_profile_audit"
                ]["edit_units"][0]
                record["motion_layers"] = ["environment"]
                record["intentional_hold"] = True
                record["hold_reason"] = "hold for the reaction beat"
                record["evidence_refs"] = ["STORY-BEAT-HOLD-01"]
                record[field] = value

                self.assert_deterministic_errors(plan, (expected,))

    def test_transition_boundaries_require_all_contract_fields(self):
        fields = (
            "boundary_id",
            "from_edit_unit_id",
            "to_edit_unit_id",
            "type",
            "story_reason",
            "visual_precondition",
            "audio_bridge_cue_id",
            "fallback",
            "fulfillment_status",
            "evidence_refs",
        )
        for field in fields:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                boundary = plan["cinematic_validation"][
                    "transition_fulfillment"
                ]["boundaries"][0]
                del boundary[field]

                self.assert_deterministic_errors(
                    plan,
                    (
                        "cinematic_validation.transition_fulfillment.boundaries "
                        f"item 1: missing field {field}",
                    ),
                )

    def test_transition_bridge_and_fulfillment_must_be_explicit(self):
        cases = (
            (
                "audio_bridge_cue_id",
                "",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.audio_bridge_cue_id: must identify a cue or explicit none",
            ),
            (
                "fulfillment_status",
                "failed",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.fulfillment_status: must be passed",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                boundary = plan["cinematic_validation"][
                    "transition_fulfillment"
                ]["boundaries"][0]
                boundary[field] = value

                self.assert_deterministic_errors(plan, (expected,))

    def test_missing_audio_requires_silent_form_authorization(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        audio = plan["cinematic_validation"]["audio_presence_and_structure"]
        audio["audio_stream_status"] = "missing"
        audio["silent_form_authorization"] = None

        self.assert_deterministic_errors(
            plan,
            (
                "cinematic_validation: missing audio requires silent-form "
                "authorization",
            ),
        )

    def test_authorized_silent_form_passes_when_visual_audits_pass(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        audio = plan["cinematic_validation"]["audio_presence_and_structure"]
        audio["audio_stream_status"] = "missing"
        audio["track_types"] = ["silence"]
        audio["silent_form_authorization"] = "USER-APPROVAL-SILENT-01"

        self.assertEqual(
            validate_edit_plan(plan, require_cinematic=True),
            [],
        )

    def test_authorized_silent_form_still_requires_passed_visual_audits(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        audio = plan["cinematic_validation"]["audio_presence_and_structure"]
        audio["audio_stream_status"] = "missing"
        audio["track_types"] = ["silence"]
        audio["silent_form_authorization"] = "USER-APPROVAL-SILENT-01"
        plan["cinematic_validation"]["source_motion_review"][
            "status"
        ] = "failed"

        self.assert_deterministic_errors(
            plan,
            (
                "cinematic_validation.audio_presence_and_structure: "
                "silent-form authorization requires passed visual audits",
            ),
        )

    def test_ppt_risk_flags_are_typed_and_block_ready(self):
        cases = (
            (
                {"poster_pose": True},
                "cinematic_validation.ppt_risk_flags: must be a list of strings",
            ),
            (
                ["poster_pose", 7],
                "cinematic_validation.ppt_risk_flags: must be a list of strings",
            ),
            (
                ["poster_pose"],
                "cinematic_validation: PPT risk flags must be empty before ready",
            ),
        )
        for value, expected in cases:
            with self.subTest(value=value):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                plan["cinematic_validation"]["ppt_risk_flags"] = value

                self.assert_deterministic_errors(plan, (expected,))

    def test_any_blocker_conflicts_with_cinematic_ready(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        plan["cinematic_validation"]["static_hold_audit"][
            "status"
        ] = "failed"

        self.assert_deterministic_errors(
            plan,
            (
                "cinematic_validation: cinematic_ready cannot be true while "
                "cinematic blockers remain",
            ),
        )

    def test_declared_cinematic_mode_enables_gate_without_flag(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        plan["cinematic_validation"]["static_hold_audit"][
            "status"
        ] = "failed"

        self.assert_deterministic_errors(
            plan,
            (
                "cinematic_validation.static_hold_audit: status failed blocks "
                "cinematic readiness",
            ),
            require_cinematic=False,
        )

    def test_cinematic_blockers_reject_aggregate_and_ready_claims(self):
        cases = (
            (
                "plan_status",
                "plan_status rendered: cinematic blockers require aggregate "
                "status blocked",
            ),
            (
                "edit_validation.ready",
                "edit_validation.ready: cannot be true while cinematic "
                "blockers remain",
            ),
            (
                "delivery.ready",
                "delivery D16: ready cannot be true while cinematic blockers "
                "remain",
            ),
        )
        for claim, expected in cases:
            with self.subTest(claim=claim):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                plan["cinematic_validation"]["static_hold_audit"][
                    "status"
                ] = "failed"
                plan["plan_status"] = "dry_run_passed"
                plan["edit_validation"]["ready"] = False
                for delivery in plan["delivery_specs"]:
                    delivery["ready"] = False

                if claim == "plan_status":
                    plan["plan_status"] = "rendered"
                elif claim == "edit_validation.ready":
                    plan["edit_validation"]["ready"] = True
                else:
                    plan["delivery_specs"][0]["ready"] = True

                self.assert_deterministic_errors(plan, (expected,))

    def test_ppt_fixture_captures_both_timelines_and_reported_failure(self):
        plan = load_plan("cinematic_ppt_plan.json")
        cinematic = plan["cinematic_validation"]

        for timeline_index, timeline in enumerate(plan["timelines"]):
            with self.subTest(timeline=timeline["timeline_id"]):
                units = edit_units(plan, timeline_index)
                self.assertEqual(len(units), 8)
                self.assertEqual(
                    sum(
                        unit["duration_seconds"] for unit in units
                    ) / len(units),
                    7.5,
                )
                self.assertEqual(
                    [unit["transition_out"] for unit in units[:-1]],
                    ["hard_cut"] * 7,
                )

        kinetic_ids = {
            record["edit_unit_id"]
            for record in cinematic["kinetic_profile_audit"]["edit_units"]
        }
        audited_pairs = {
            (
                boundary["from_edit_unit_id"],
                boundary["to_edit_unit_id"],
            )
            for boundary in cinematic["transition_fulfillment"]["boundaries"]
        }
        self.assertSetEqual(kinetic_ids, all_edit_unit_ids(plan))
        self.assertSetEqual(audited_pairs, all_boundary_pairs(plan))
        self.assertEqual(len(kinetic_ids), 16)
        self.assertEqual(len(audited_pairs), 14)
        self.assertTrue(
            all(
                record["motion_layers"] == ["environment"]
                for record in cinematic["kinetic_profile_audit"]["edit_units"]
            )
        )
        self.assertEqual(plan["audio_tracks"], [])
        self.assertTrue(
            all(not timeline["audio_track_refs"] for timeline in plan["timelines"])
        )
        self.assertEqual(cinematic["content_consistency"]["status"], "passed")
        self.assertEqual(
            cinematic["character_identity_integrity"]["status"], "passed"
        )
        self.assertTrue(cinematic["cinematic_ready"])

    def test_static_silent_hard_cut_plan_cannot_claim_cinematic_ready(self):
        errors = self.assert_deterministic_errors(
            load_plan("cinematic_ppt_plan.json"),
            (
                "cinematic_validation: PPT risk flags must be empty before ready",
                "cinematic_validation: missing audio requires silent-form "
                "authorization",
                "cinematic_validation: cinematic_ready cannot be true while "
                "cinematic blockers remain",
            ),
        )

        for dimension in (
            "action_reaction_coverage",
            "kinetic_profile_audit",
            "shot_scale_and_composition_variety",
            "transition_fulfillment",
            "audio_presence_and_structure",
            "static_hold_audit",
            "source_motion_review",
        ):
            with self.subTest(dimension=dimension):
                self.assertTrue(
                    any(dimension in error for error in errors),
                    f"missing cinematic failure dimension: {dimension}",
                )

    def test_valid_fixture_audits_both_timelines_and_intentional_hold(self):
        plan = load_plan("cinematic_valid_plan.json")
        cinematic = plan["cinematic_validation"]
        holds = [
            unit
            for unit in cinematic["kinetic_profile_audit"]["edit_units"]
            if unit["intentional_hold"]
        ]
        kinetic_ids = {
            record["edit_unit_id"]
            for record in cinematic["kinetic_profile_audit"]["edit_units"]
        }
        audited_pairs = {
            (
                boundary["from_edit_unit_id"],
                boundary["to_edit_unit_id"],
            )
            for boundary in cinematic["transition_fulfillment"]["boundaries"]
        }

        self.assertSetEqual(kinetic_ids, all_edit_unit_ids(plan))
        self.assertSetEqual(audited_pairs, all_boundary_pairs(plan))
        self.assertEqual(len(holds), 1)
        self.assertTrue(holds[0]["hold_reason"])
        self.assertTrue(holds[0]["evidence_refs"])
        self.assertEqual(cinematic["ppt_risk_flags"], [])
        self.assertTrue(cinematic["cinematic_ready"])

    def test_complete_cinematic_evidence_passes(self):
        self.assertEqual(
            validate_edit_plan(
                load_plan("cinematic_valid_plan.json"),
                require_cinematic=True,
            ),
            [],
        )

    def test_cli_require_cinematic_rejects_legacy_and_accepts_complete_plan(self):
        legacy_code, legacy_stdout, legacy_stderr = run_cli(
            [FIXTURES / "valid_plan.json", "--require-cinematic"]
        )
        valid_code, valid_stdout, valid_stderr = run_cli(
            [FIXTURES / "cinematic_valid_plan.json", "--require-cinematic"]
        )

        self.assertEqual(legacy_code, 1)
        self.assertIn(
            "- cinematic_validation: required for cinematic delivery\n",
            legacy_stdout,
        )
        self.assertEqual(legacy_stderr, "")
        self.assertEqual(valid_code, 0)
        self.assertEqual(valid_stdout, "Edit plan is valid.\n")
        self.assertEqual(valid_stderr, "")


if __name__ == "__main__":
    unittest.main()
