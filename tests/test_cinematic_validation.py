import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures" / "editing"
sys.path.insert(0, str(SCRIPTS_DIR))

from cinematic_validation import validate_cinematic_plan
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


def rendered_cinematic_plan():
    plan = load_plan("cinematic_valid_plan.json")
    plan["plan_status"] = "rendered"
    plan["execution"].update(
        {
            "operation_authorization": "approved",
            "authorized_manifest_id": "MAN-001",
            "authorized_version_directory": "edit/v001",
            "tool_evidence": [],
            "probe_evidence": [],
            "rendered_outputs": [],
        }
    )
    delivery_ids = []
    for delivery in plan["delivery_specs"]:
        delivery_id = delivery["delivery_id"]
        delivery_ids.append(delivery_id)
        tool_id = f"TOOL-{delivery_id}"
        probe_id = f"PROBE-{delivery_id}"
        delivery["status"] = "rendered"
        delivery["ready"] = True
        plan["execution"]["tool_evidence"].append(
            {
                "tool_evidence_id": tool_id,
                "tool": "ffmpeg 6.1",
                "status": "verified",
            }
        )
        plan["execution"]["probe_evidence"].append(
            {
                "probe_evidence_id": probe_id,
                "delivery_id": delivery_id,
                "output_ref": delivery["destination"],
                "status": "passed",
            }
        )
        plan["execution"]["rendered_outputs"].append(
            {
                "delivery_id": delivery_id,
                "output_ref": delivery["destination"],
                "status": "rendered",
                "tool_evidence_ref": tool_id,
                "tool_status": "passed",
                "probe_evidence_ref": probe_id,
                "probe_status": "passed",
            }
        )
    for result in plan["edit_validation"]["per_delivery_results"]:
        result["status"] = "passed"
        result["validation_status"] = "passed"
    plan["edit_validation"]["ready"] = True
    review = plan["cinematic_validation"]["source_motion_review"]
    review.update(
        {
            "actual_output_review_status": "passed",
            "reviewed_delivery_ids": delivery_ids,
            "frame_change_evidence_refs": ["FRAME-CHANGE-D16", "FRAME-CHANGE-D9"],
            "contact_sheet_evidence_refs": ["CONTACT-16", "CONTACT-9"],
        }
    )
    plan["cinematic_validation"]["cinematic_ready"] = True
    return plan


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

    def test_cinematic_validation_rejects_non_object_shapes(self):
        for value in (7, "cinematic", [], None):
            with self.subTest(value=value):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                plan["cinematic_validation"] = value

                self.assert_deterministic_errors(
                    plan,
                    ("cinematic_validation: must be an object",),
                )

    def test_audit_objects_reject_non_object_shapes_under_auto_gate(self):
        for audit in AUDIT_FIELDS:
            for value in ([], "passed", 7, None):
                with self.subTest(audit=audit, value=value):
                    plan = copy.deepcopy(
                        load_plan("cinematic_valid_plan.json")
                    )
                    plan["cinematic_validation"][audit] = value

                    self.assert_deterministic_errors(
                        plan,
                        (f"cinematic_validation.{audit}: must be an object",),
                        require_cinematic=False,
                    )

    def test_nested_audit_collections_reject_non_array_shapes(self):
        collection_paths = (
            ("action_reaction_coverage", "events"),
            ("kinetic_profile_audit", "edit_units"),
            ("transition_fulfillment", "boundaries"),
        )
        for audit, field in collection_paths:
            for value in ({}, "items", 7, None):
                with self.subTest(audit=audit, field=field, value=value):
                    plan = copy.deepcopy(
                        load_plan("cinematic_valid_plan.json")
                    )
                    plan["cinematic_validation"][audit][field] = value

                    self.assert_deterministic_errors(
                        plan,
                        (
                            f"cinematic_validation.{audit}.{field}: "
                            "must be an array",
                        ),
                    )

    def test_nested_audit_collection_items_must_be_objects(self):
        collection_paths = (
            ("action_reaction_coverage", "events"),
            ("kinetic_profile_audit", "edit_units"),
            ("transition_fulfillment", "boundaries"),
        )
        for audit, field in collection_paths:
            for value in ("item", 7, None):
                with self.subTest(audit=audit, field=field, value=value):
                    plan = copy.deepcopy(
                        load_plan("cinematic_valid_plan.json")
                    )
                    plan["cinematic_validation"][audit][field] = [value]

                    self.assert_deterministic_errors(
                        plan,
                        (
                            f"cinematic_validation.{audit}.{field} item 1: "
                            "must be an object",
                        ),
                    )

    def test_evidence_collection_containers_reject_non_array_shapes(self):
        collection_paths = (
            (("ppt_risk_flags",), "cinematic_validation.ppt_risk_flags"),
            (("evidence_refs",), "cinematic_validation.evidence_refs"),
            (
                ("content_consistency", "locked_event_ids"),
                "cinematic_validation.content_consistency.locked_event_ids",
            ),
            (
                ("content_consistency", "evidence_refs"),
                "cinematic_validation.content_consistency.evidence_refs",
            ),
            (
                ("character_identity_integrity", "identity_profile_ids"),
                "cinematic_validation.character_identity_integrity."
                "identity_profile_ids",
            ),
            (
                ("character_identity_integrity", "model_lock_refs"),
                "cinematic_validation.character_identity_integrity."
                "model_lock_refs",
            ),
            (
                ("character_identity_integrity", "drift_conflicts"),
                "cinematic_validation.character_identity_integrity."
                "drift_conflicts",
            ),
            (
                ("character_identity_integrity", "evidence_refs"),
                "cinematic_validation.character_identity_integrity."
                "evidence_refs",
            ),
            (
                (
                    "action_reaction_coverage",
                    "events",
                    0,
                    "required_roles",
                ),
                "cinematic_validation.action_reaction_coverage.events item "
                "1.required_roles",
            ),
            (
                (
                    "action_reaction_coverage",
                    "events",
                    0,
                    "edit_unit_ids",
                ),
                "cinematic_validation.action_reaction_coverage.events item "
                "1.edit_unit_ids",
            ),
            (
                (
                    "kinetic_profile_audit",
                    "edit_units",
                    0,
                    "motion_layers",
                ),
                "cinematic_validation.kinetic_profile_audit.edit_units item "
                "1.motion_layers",
            ),
            (
                (
                    "kinetic_profile_audit",
                    "edit_units",
                    0,
                    "evidence_refs",
                ),
                "cinematic_validation.kinetic_profile_audit.edit_units item "
                "1.evidence_refs",
            ),
            (
                (
                    "transition_fulfillment",
                    "boundaries",
                    0,
                    "evidence_refs",
                ),
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.evidence_refs",
            ),
            (
                ("audio_presence_and_structure", "track_types"),
                "cinematic_validation.audio_presence_and_structure.track_types",
            ),
            (
                ("audio_presence_and_structure", "evidence_refs"),
                "cinematic_validation.audio_presence_and_structure."
                "evidence_refs",
            ),
            (
                ("static_hold_audit", "intentional_holds"),
                "cinematic_validation.static_hold_audit.intentional_holds",
            ),
            (
                ("static_hold_audit", "evidence_refs"),
                "cinematic_validation.static_hold_audit.evidence_refs",
            ),
            (
                ("source_motion_review", "reviewed_asset_ids"),
                "cinematic_validation.source_motion_review.reviewed_asset_ids",
            ),
            (
                ("source_motion_review", "evidence_refs"),
                "cinematic_validation.source_motion_review.evidence_refs",
            ),
        )
        for path, label in collection_paths:
            for value in ({}, "items", 7, None):
                with self.subTest(path=label, value=value):
                    plan = copy.deepcopy(
                        load_plan("cinematic_valid_plan.json")
                    )
                    target = plan["cinematic_validation"]
                    for component in path[:-1]:
                        target = target[component]
                    target[path[-1]] = value

                    self.assert_deterministic_errors(
                        plan,
                        (f"{label}: must be an array",),
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

    def test_cinematic_coverage_collections_cannot_be_empty(self):
        cases = (
            (
                "action_reaction_coverage",
                "events",
                "cinematic_validation.action_reaction_coverage.events: "
                "must not be empty",
            ),
            (
                "kinetic_profile_audit",
                "edit_units",
                "cinematic_validation.kinetic_profile_audit.edit_units: "
                "must not be empty",
            ),
            (
                "transition_fulfillment",
                "boundaries",
                "cinematic_validation.transition_fulfillment.boundaries: "
                "must not be empty when timelines have adjacent edit units",
            ),
        )
        for audit, field, expected in cases:
            with self.subTest(audit=audit):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                plan["cinematic_validation"][audit][field] = []

                self.assert_deterministic_errors(plan, (expected,))

    def test_action_event_edit_units_are_unique_and_resolve(self):
        cases = (
            (
                ["E16-01", "E16-01"],
                "cinematic_validation.action_reaction_coverage.events item "
                "1.edit_unit_ids: duplicate edit_unit_id E16-01",
            ),
            (
                ["E16-01", "E-MISSING"],
                "cinematic_validation.action_reaction_coverage.events item "
                "1.edit_unit_ids: unknown edit_unit_id E-MISSING",
            ),
        )
        for edit_unit_ids, expected in cases:
            with self.subTest(edit_unit_ids=edit_unit_ids):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                event = plan["cinematic_validation"][
                    "action_reaction_coverage"
                ]["events"][0]
                event["edit_unit_ids"] = edit_unit_ids

                self.assert_deterministic_errors(plan, (expected,))

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

    def test_kinetic_records_bind_exactly_once_to_real_edit_units(self):
        cases = (
            (
                "missing",
                "cinematic_validation.kinetic_profile_audit.edit_units: "
                "missing edit_unit_id E9-02",
            ),
            (
                "duplicate",
                "cinematic_validation.kinetic_profile_audit.edit_units item "
                "5.edit_unit_id: duplicate edit_unit_id E16-01",
            ),
            (
                "extra",
                "cinematic_validation.kinetic_profile_audit.edit_units item "
                "5.edit_unit_id: unknown edit_unit_id E-MISSING",
            ),
        )
        for case, expected in cases:
            with self.subTest(case=case):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                records = plan["cinematic_validation"][
                    "kinetic_profile_audit"
                ]["edit_units"]
                if case == "missing":
                    records.pop()
                else:
                    record = copy.deepcopy(records[0])
                    if case == "extra":
                        record["edit_unit_id"] = "E-MISSING"
                    records.append(record)

                self.assert_deterministic_errors(plan, (expected,))

    def test_transition_boundaries_require_all_contract_fields(self):
        fields = (
            "boundary_id",
            "from_edit_unit_id",
            "to_edit_unit_id",
            "type",
            "story_reason",
            "visual_precondition",
            "incoming_match",
            "duration_frames",
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

    def test_transition_incoming_match_and_duration_are_typed(self):
        cases = (
            (
                "incoming_match",
                None,
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.incoming_match: must be a non-empty string",
            ),
            (
                "incoming_match",
                "",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.incoming_match: must be a non-empty string",
            ),
            (
                "duration_frames",
                True,
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.duration_frames: must be a non-negative integer",
            ),
            (
                "duration_frames",
                -1,
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.duration_frames: must be a non-negative integer",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field, value=value):
                plan = load_plan("cinematic_valid_plan.json")
                plan["cinematic_validation"]["transition_fulfillment"][
                    "boundaries"
                ][0][field] = value
                self.assert_deterministic_errors(plan, (expected,))

    def test_transition_contract_values_must_be_non_empty_strings(self):
        fields = (
            "boundary_id",
            "from_edit_unit_id",
            "to_edit_unit_id",
            "type",
            "story_reason",
            "visual_precondition",
            "fallback",
        )
        for field in fields:
            for value in (None, ""):
                with self.subTest(field=field, value=value):
                    plan = copy.deepcopy(
                        load_plan("cinematic_valid_plan.json")
                    )
                    boundary = plan["cinematic_validation"][
                        "transition_fulfillment"
                    ]["boundaries"][0]
                    boundary[field] = value

                    self.assert_deterministic_errors(
                        plan,
                        (
                            "cinematic_validation.transition_fulfillment."
                            f"boundaries item 1.{field}: must be a non-empty "
                            "string",
                        ),
                    )

        for value in (None, ""):
            with self.subTest(field="audio_bridge_cue_id", value=value):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                boundary = plan["cinematic_validation"][
                    "transition_fulfillment"
                ]["boundaries"][0]
                boundary["audio_bridge_cue_id"] = value

                self.assert_deterministic_errors(
                    plan,
                    (
                        "cinematic_validation.transition_fulfillment."
                        "boundaries item 1.audio_bridge_cue_id: must identify "
                        "a cue or explicit none",
                    ),
                )

    def test_transition_boundaries_resolve_to_actual_adjacent_pairs(self):
        cases = (
            (
                "dangling",
                "E-MISSING",
                "E16-02",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1.from_edit_unit_id: unknown edit_unit_id E-MISSING",
            ),
            (
                "non_adjacent",
                "E16-02",
                "E16-01",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1: E16-02 -> E16-01 is not an actual adjacent pair",
            ),
            (
                "cross_timeline",
                "E16-01",
                "E9-02",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "1: E16-01 -> E9-02 crosses timelines",
            ),
        )
        for case, from_id, to_id, expected in cases:
            with self.subTest(case=case):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                boundary = plan["cinematic_validation"][
                    "transition_fulfillment"
                ]["boundaries"][0]
                boundary["from_edit_unit_id"] = from_id
                boundary["to_edit_unit_id"] = to_id

                self.assert_deterministic_errors(plan, (expected,))

    def test_transition_boundary_ids_pairs_and_coverage_are_exact(self):
        cases = (
            (
                "missing",
                "cinematic_validation.transition_fulfillment.boundaries: "
                "missing adjacent pair E9-01 -> E9-02",
            ),
            (
                "duplicate_pair",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "3: duplicate adjacent pair E16-01 -> E16-02",
            ),
            (
                "duplicate_boundary_id",
                "cinematic_validation.transition_fulfillment.boundaries item "
                "2.boundary_id: duplicate boundary_id TR01",
            ),
        )
        for case, expected in cases:
            with self.subTest(case=case):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                boundaries = plan["cinematic_validation"][
                    "transition_fulfillment"
                ]["boundaries"]
                if case == "missing":
                    boundaries.pop()
                elif case == "duplicate_pair":
                    duplicate = copy.deepcopy(boundaries[0])
                    duplicate["boundary_id"] = "TR-DUP"
                    boundaries.append(duplicate)
                else:
                    boundaries[1]["boundary_id"] = boundaries[0][
                        "boundary_id"
                    ]

                self.assert_deterministic_errors(plan, (expected,))

    def test_single_unit_timelines_allow_empty_transition_boundaries(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        retained_ids = {"E16-01", "E9-01"}
        for timeline in plan["timelines"]:
            units = timeline["video_tracks"][0]["edit_units"]
            timeline["video_tracks"][0]["edit_units"] = [units[0]]
        action_events = plan["cinematic_validation"][
            "action_reaction_coverage"
        ]["events"]
        for event in action_events:
            event["edit_unit_ids"] = ["E16-01"]
        kinetic_records = plan["cinematic_validation"][
            "kinetic_profile_audit"
        ]["edit_units"]
        plan["cinematic_validation"]["kinetic_profile_audit"][
            "edit_units"
        ] = [
            record
            for record in kinetic_records
            if record["edit_unit_id"] in retained_ids
        ]
        plan["cinematic_validation"]["transition_fulfillment"][
            "boundaries"
        ] = []

        self.assertEqual(
            validate_cinematic_plan(plan, required=True),
            [],
        )

    def test_malformed_timelines_do_not_crash_cinematic_helper(self):
        malformed_timelines = (
            None,
            "timelines",
            [None, 7],
            [
                {
                    "timeline_id": [],
                    "video_tracks": [
                        {
                            "track_id": "V1",
                            "runtime_role": "active",
                            "release_role": "first_release",
                            "edit_units": [
                                {"edit_unit_id": [], "sequence": {}},
                                None,
                            ],
                        }
                    ],
                }
            ],
        )
        for timelines in malformed_timelines:
            with self.subTest(timelines=timelines):
                plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
                plan["timelines"] = timelines

                first = validate_cinematic_plan(plan, required=True)
                second = validate_cinematic_plan(plan, required=True)

                self.assertIsInstance(first, list)
                self.assertEqual(first, second)

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
                "cinematic_validation.ppt_risk_flags: must be an array",
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
                if value == ["poster_pose"]:
                    plan["cinematic_validation"]["cinematic_ready"] = True

                self.assert_deterministic_errors(plan, (expected,))

    def test_any_blocker_conflicts_with_cinematic_ready(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        plan["cinematic_validation"]["static_hold_audit"][
            "status"
        ] = "failed"
        plan["cinematic_validation"]["cinematic_ready"] = True

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

    def test_blocked_plan_accepts_cinematic_blocker_as_real_blocker(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        plan["cinematic_validation"]["static_hold_audit"][
            "status"
        ] = "failed"
        plan["cinematic_validation"]["cinematic_ready"] = False
        plan["plan_status"] = "blocked"
        plan["edit_validation"]["ready"] = False
        for delivery in plan["delivery_specs"]:
            delivery["ready"] = False

        errors = self.assert_deterministic_errors(
            plan,
            (
                "cinematic_validation.static_hold_audit: status failed blocks "
                "cinematic readiness",
            ),
        )
        self.assertNotIn(
            "plan_status blocked: no blocking requested delivery or shared "
            "dependency",
            errors,
        )

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
        self.assertFalse(cinematic["cinematic_ready"])

    def test_complete_cinematic_evidence_passes(self):
        self.assertEqual(
            validate_edit_plan(
                load_plan("cinematic_valid_plan.json"),
                require_cinematic=True,
            ),
            [],
        )

    def test_rendered_cinematic_plan_with_actual_output_evidence_is_ready(self):
        self.assertEqual(
            validate_edit_plan(rendered_cinematic_plan(), require_cinematic=True),
            [],
        )

    def test_non_rendered_plan_states_cannot_claim_cinematic_ready(self):
        for status in ("dry_run_passed", "authorized", "draft"):
            with self.subTest(status=status):
                plan = load_plan("cinematic_valid_plan.json")
                plan["plan_status"] = status
                plan["cinematic_validation"]["cinematic_ready"] = True
                errors = validate_edit_plan(plan, require_cinematic=True)
                self.assertIn(
                    "cinematic_validation.cinematic_ready: requires plan_status rendered",
                    errors,
                )

    def test_ready_claim_requires_delivery_edit_and_execution_evidence(self):
        cases = (
            (
                "delivery",
                lambda plan: plan["delivery_specs"][0].update(ready=False),
                "cinematic_validation.cinematic_ready: every requested delivery "
                "must be rendered and ready",
            ),
            (
                "edit_validation",
                lambda plan: plan["edit_validation"].update(ready=False),
                "cinematic_validation.cinematic_ready: requires "
                "edit_validation.ready true",
            ),
            (
                "tool_evidence",
                lambda plan: plan["execution"].update(tool_evidence=[]),
                "cinematic_validation.cinematic_ready: requires non-empty "
                "execution.tool_evidence",
            ),
            (
                "probe_evidence",
                lambda plan: plan["execution"].update(probe_evidence=[]),
                "cinematic_validation.cinematic_ready: requires non-empty "
                "execution.probe_evidence",
            ),
            (
                "rendered_outputs",
                lambda plan: plan["execution"].update(rendered_outputs=[]),
                "cinematic_validation.cinematic_ready: requires non-empty "
                "execution.rendered_outputs",
            ),
        )
        for case, mutate, expected in cases:
            with self.subTest(case=case):
                plan = rendered_cinematic_plan()
                mutate(plan)
                self.assertIn(
                    expected,
                    validate_edit_plan(plan, require_cinematic=True),
                )

    def test_ready_source_motion_review_requires_actual_output_evidence(self):
        cases = (
            (
                "actual_output_review_status",
                "failed",
                "cinematic_validation.source_motion_review."
                "actual_output_review_status: must be passed",
            ),
            (
                "reviewed_delivery_ids",
                ["D16"],
                "cinematic_validation.source_motion_review.reviewed_delivery_ids: "
                "must match requested delivery IDs exactly",
            ),
            (
                "frame_change_evidence_refs",
                [],
                "cinematic_validation.source_motion_review."
                "frame_change_evidence_refs: must be a non-empty list of strings",
            ),
            (
                "contact_sheet_evidence_refs",
                None,
                "cinematic_validation.source_motion_review."
                "contact_sheet_evidence_refs: must be an array",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                plan = rendered_cinematic_plan()
                plan["cinematic_validation"]["source_motion_review"][field] = value
                self.assertIn(
                    expected,
                    validate_edit_plan(plan, require_cinematic=True),
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

    def test_cli_reports_malformed_cinematic_shape_without_traceback(self):
        plan = copy.deepcopy(load_plan("cinematic_valid_plan.json"))
        plan["cinematic_validation"]["kinetic_profile_audit"] = [
            "not-an-object"
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            malformed_path = Path(temp_dir) / "malformed-cinematic.json"
            malformed_path.write_text(
                json.dumps(plan),
                encoding="utf-8",
            )
            code, stdout, stderr = run_cli(
                [malformed_path, "--require-cinematic"]
            )

        self.assertEqual(code, 1)
        self.assertIn(
            "- cinematic_validation.kinetic_profile_audit: must be an object\n",
            stdout,
        )
        self.assertNotIn("Traceback", stdout)
        self.assertNotIn("Traceback", stderr)


if __name__ == "__main__":
    unittest.main()
