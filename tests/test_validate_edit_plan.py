import copy
import io
import json
import math
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURES_DIR = ROOT / "tests" / "fixtures" / "editing"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_edit_plan import main, validate_edit_plan


def load_plan(name="valid_plan.json"):
    with (FIXTURES_DIR / name).open("r", encoding="utf-8") as plan_file:
        return json.load(plan_file)


def timeline(plan, timeline_id):
    return next(
        item for item in plan["timelines"] if item["timeline_id"] == timeline_id
    )


def units(plan, timeline_id):
    return timeline(plan, timeline_id)["video_tracks"][0]["edit_units"]


def delivery(plan, delivery_id):
    return next(
        item
        for item in plan["delivery_specs"]
        if item["delivery_id"] == delivery_id
    )


def asset(plan, asset_id):
    return next(
        item for item in plan["media_bindings"] if item["asset_id"] == asset_id
    )


def prepare_ffmpeg_final(plan, delivery_id="D16"):
    final_delivery = delivery(plan, delivery_id)
    final_delivery["version_role"] = "final_master"
    final_delivery["status"] = "dry_run_passed"
    final_delivery["ready"] = False
    final_delivery["subtitle_mode"] = "none"
    final_delivery["audio_mode"] = "none"
    final_delivery["look_mode"] = "none"
    final_delivery["render_backend"] = "ffmpeg"
    return final_delivery


def post_asset(asset_id="PA01"):
    return {
        "asset_id": asset_id,
        "binding_scope": "project",
        "target_id": "PKG-001",
        "source_type": "post_asset",
        "path_or_uri": f"media/{asset_id}.wav",
        "file_status": "online",
        "rights_status": "cleared",
        "probe_status": "verified",
        "selection_reason": "approved post asset",
        "acceptance_status": "approved",
    }


def rendered_plan():
    plan = load_plan()
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
    for requested_delivery in plan["delivery_specs"]:
        delivery_id = requested_delivery["delivery_id"]
        output_ref = requested_delivery["destination"]
        tool_id = f"TOOL-{delivery_id}"
        probe_id = f"PROBE-{delivery_id}"
        requested_delivery["status"] = "rendered"
        requested_delivery["ready"] = True
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
                "output_ref": output_ref,
                "status": "passed",
            }
        )
        plan["execution"]["rendered_outputs"].append(
            {
                "delivery_id": delivery_id,
                "output_ref": output_ref,
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
    return plan


def authorized_plan():
    plan = load_plan()
    plan["plan_status"] = "authorized"
    plan["execution"].update(
        {
            "operation_authorization": "approved",
            "authorized_manifest_id": "MAN-001",
            "authorized_version_directory": "edit/v001",
            "steps": [
                {
                    "step_id": "STEP-D16",
                    "delivery_id": "D16",
                    "status": "pending",
                }
            ],
        }
    )
    for requested_delivery in plan["delivery_specs"]:
        requested_delivery["status"] = "authorized"
    return plan


def run_cli(args):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = main([str(arg) for arg in args])
    return exit_code, stdout.getvalue(), stderr.getvalue()


class ValidateEditPlanTests(unittest.TestCase):
    def test_valid_dual_aspect_plan_has_no_errors(self):
        self.assertEqual(validate_edit_plan(load_plan()), [])

    def test_jianying_manual_target_is_valid(self):
        self.assertEqual(
            validate_edit_plan(load_plan("jianying_plan.json")), []
        )

    def test_gap_is_rejected(self):
        plan = load_plan()
        units(plan, "TL-16")[1]["timeline_in_seconds"] = 2.5

        self.assertIn(
            "timeline TL-16: gap before E16-02", validate_edit_plan(plan)
        )

    def test_overlap_fixture_is_rejected(self):
        self.assertIn(
            "timeline TL-16: overlap before E16-02",
            validate_edit_plan(load_plan("overlap_plan.json")),
        )

    def test_source_range_cannot_exceed_media_duration(self):
        plan = load_plan()
        asset(plan, "A01")["source_out_seconds"] = 4

        self.assertIn(
            "asset A01: source range exceeds media duration",
            validate_edit_plan(plan),
        )

    def test_placeholder_blocks_final_master(self):
        plan = load_plan("missing_media_plan.json")
        final_delivery = delivery(plan, "D16")
        final_delivery["version_role"] = "final_master"
        final_delivery["ready"] = True
        final_delivery["status"] = "dry_run_passed"

        self.assertIn(
            "final master D16: placeholder media is not allowed",
            validate_edit_plan(plan, require_final=True),
        )

    def test_locked_events_must_be_complete_and_ordered_per_timeline(self):
        plan = load_plan()
        vertical_units = units(plan, "TL-9")
        vertical_units[0]["locked_event_ids"] = ["EV02"]
        vertical_units[1]["locked_event_ids"] = ["EV01"]

        self.assertIn(
            "timeline TL-9: locked events are missing or reordered",
            validate_edit_plan(plan),
        )

    def test_execution_requires_operation_authorization(self):
        self.assertIn(
            "execution: operation authorization is required",
            validate_edit_plan(load_plan(), for_execution=True),
        )

    def test_empty_execution_cannot_bypass_execution_requirements(self):
        plan = load_plan()
        plan["execution"] = {}

        errors = validate_edit_plan(plan, for_execution=True)

        self.assertIn("execution: missing required field dry_run_status", errors)
        self.assertIn("execution: dry-run status must be passed", errors)
        self.assertIn("execution: operation authorization is required", errors)
        self.assertIn("execution: version_policy must be create_new", errors)
        self.assertIn("execution: authorized_manifest_id is required", errors)
        self.assertIn(
            "execution: authorized_version_directory is required", errors
        )

    def test_execution_authorization_must_match_manifest(self):
        plan = load_plan()
        plan["execution"].update(
            {
                "operation_authorization": "approved",
                "authorized_manifest_id": "MAN-OTHER",
                "authorized_version_directory": "edit/v001",
            }
        )

        self.assertIn(
            "execution: authorization does not match dry-run manifest",
            validate_edit_plan(plan, for_execution=True),
        )

    def test_execution_authorization_must_match_version_directory(self):
        plan = load_plan()
        plan["execution"].update(
            {
                "operation_authorization": "approved",
                "authorized_manifest_id": "MAN-001",
                "authorized_version_directory": "edit/v999",
            }
        )

        self.assertIn(
            "execution: authorization does not match version directory",
            validate_edit_plan(plan, for_execution=True),
        )

    def test_execution_rejects_raw_ffmpeg_look_filters(self):
        plan = authorized_plan()
        delivery(plan, "D16")["look_mode"] = "approved"
        plan["look_plan"]["ffmpeg_filters"] = [
            "movie=../../source/secret.mp4"
        ]

        self.assertIn(
            "look_plan.ffmpeg_filters: raw filter strings are not allowed",
            validate_edit_plan(plan, for_execution=True),
        )

    def test_execution_rejects_malformed_or_unsupported_ffmpeg_look_filters(self):
        cases = (
            (
                {"name": "movie", "params": {}},
                "look_plan.ffmpeg_filters: unsupported filter movie",
            ),
            (
                {"name": "eq", "params": "contrast=1.1"},
                "look_plan.ffmpeg_filters: filter eq params must be an object",
            ),
        )
        for filter_value, expected in cases:
            with self.subTest(filter_value=filter_value):
                plan = authorized_plan()
                delivery(plan, "D16")["look_mode"] = "approved"
                plan["look_plan"]["ffmpeg_filters"] = [filter_value]

                self.assertIn(
                    expected, validate_edit_plan(plan, for_execution=True)
                )

    def test_version_directory_cannot_escape_output_root(self):
        plan = load_plan()
        plan["execution"]["version_directory"] = "../source"

        self.assertIn(
            "execution: version_directory must not contain '..' segments",
            validate_edit_plan(plan),
        )

    def test_authorized_media_roots_require_normalized_strings(self):
        plan = load_plan()
        plan["execution"]["authorized_media_roots"] = [{}]

        self.assertIn(
            "execution.authorized_media_roots item 1: must be a non-empty string",
            validate_edit_plan(plan),
        )

    def test_local_media_must_be_within_authorized_media_roots(self):
        plan = load_plan()
        asset(plan, "A01")["path_or_uri"] = "source/SH01_T01.mp4"

        self.assertIn(
            "asset A01: path_or_uri is outside authorized_media_roots",
            validate_edit_plan(plan),
        )

    def test_execution_delivery_destination_must_be_within_locked_version_directory(self):
        cases = (
            "source/SH01_T01.mp4",
            "edit/v001",
            r"C:\edit\v001\D16.mp4",
        )
        for destination in cases:
            with self.subTest(destination=destination):
                plan = authorized_plan()
                delivery(plan, "D16")["destination"] = destination

                self.assertIn(
                    "delivery D16: destination must be a strict child of "
                    "authorized_version_directory",
                    validate_edit_plan(plan, for_execution=True),
                )

    def test_pending_execution_step_selects_delivery_destination(self):
        plan = authorized_plan()
        selected_delivery = delivery(plan, "D16")
        selected_delivery["ready"] = False
        selected_delivery["status"] = "dry_run_passed"
        selected_delivery["destination"] = "source/selected.mp4"

        self.assertIn(
            "delivery D16: destination must be a strict child of "
            "authorized_version_directory",
            validate_edit_plan(plan, for_execution=True),
        )

    def test_referenced_alternate_local_media_must_be_within_authorized_roots(self):
        plan = load_plan()
        binding = asset(plan, "A01")
        binding["runtime_role"] = "alternate"
        binding["path_or_uri"] = "source/SH01_T01.mp4"

        self.assertIn(
            "asset A01: path_or_uri is outside authorized_media_roots",
            validate_edit_plan(plan),
        )

    def test_referenced_fallback_local_media_must_be_within_authorized_roots(self):
        plan = load_plan()
        fallback = copy.deepcopy(asset(plan, "A01"))
        fallback.update(
            {
                "asset_id": "A01-FALLBACK",
                "take_id": "T02",
                "runtime_role": "alternate",
                "path_or_uri": "source/SH01_T02.mp4",
            }
        )
        plan["media_bindings"].append(fallback)
        asset(plan, "A01")["fallback_asset_id"] = "A01-FALLBACK"

        self.assertIn(
            "asset A01-FALLBACK: path_or_uri is outside authorized_media_roots",
            validate_edit_plan(plan),
        )

    def test_unreferenced_alternate_local_media_need_not_be_within_authorized_roots(self):
        plan = load_plan()
        alternate = copy.deepcopy(asset(plan, "A01"))
        alternate.update(
            {
                "asset_id": "A01-UNUSED",
                "take_id": "T99",
                "runtime_role": "alternate",
                "path_or_uri": "source/unused.mp4",
            }
        )
        plan["media_bindings"].append(alternate)

        self.assertEqual(validate_edit_plan(plan), [])

    def test_output_root_and_version_directory_must_form_strict_subdirectory(self):
        cases = (
            ("/", "/v001", "execution: output_root must not be a filesystem root"),
            (
                "edit",
                "edit",
                "execution: version_directory must be a strict child of output_root",
            ),
        )
        for output_root, version_directory, expected in cases:
            with self.subTest(output_root=output_root, version_directory=version_directory):
                plan = load_plan()
                plan["execution"]["output_root"] = output_root
                plan["execution"]["version_directory"] = version_directory
                self.assertIn(expected, validate_edit_plan(plan))

    def test_absolute_windows_and_posix_roots_are_allowed_lexically(self):
        cases = (
            (
                r"C:\renders",
                r"C:\renders\v001",
                r"C:\media",
                (r"C:\media\SH01_T01.mp4", r"C:\media\SH02_T01.mp4"),
            ),
            (
                "/renders",
                "/renders/v001",
                "/media",
                ("/media/SH01_T01.mp4", "/media/SH02_T01.mp4"),
            ),
        )
        for output_root, version_directory, media_root, media_paths in cases:
            with self.subTest(output_root=output_root):
                plan = load_plan()
                plan["execution"].update(
                    {
                        "output_root": output_root,
                        "version_directory": version_directory,
                        "authorized_media_roots": [media_root],
                    }
                )
                asset(plan, "A01")["path_or_uri"] = media_paths[0]
                asset(plan, "A02")["path_or_uri"] = media_paths[1]
                self.assertEqual(validate_edit_plan(plan), [])

    def test_delivery_must_reference_an_existing_timeline(self):
        plan = load_plan()
        delivery(plan, "D16")["timeline_id"] = "TL-MISSING"

        self.assertIn(
            "delivery D16: unknown timeline_id TL-MISSING",
            validate_edit_plan(plan),
        )

    def test_delivery_and_timeline_export_refs_are_bidirectional(self):
        plan = load_plan()
        timeline(plan, "TL-16")["export_refs"] = []

        self.assertIn(
            "delivery D16: timeline export_refs do not reference delivery",
            validate_edit_plan(plan),
        )

    def test_timeline_export_ref_must_resolve_to_delivery(self):
        plan = load_plan()
        timeline(plan, "TL-16")["export_refs"].append("D404")

        self.assertIn(
            "timeline TL-16: unknown delivery_id D404 in export_refs",
            validate_edit_plan(plan),
        )

    def test_timeline_export_ref_cannot_cross_bind_deliveries(self):
        plan = load_plan()
        timeline(plan, "TL-16")["export_refs"].append("D9")

        self.assertIn(
            "timeline TL-16: delivery D9 is bound to timeline TL-9",
            validate_edit_plan(plan),
        )

    def test_timeline_export_refs_cannot_duplicate_a_delivery(self):
        plan = load_plan()
        timeline(plan, "TL-16")["export_refs"].append("D16")

        self.assertIn(
            "timeline TL-16: duplicate delivery_id D16 in export_refs",
            validate_edit_plan(plan),
        )

    def test_rendered_aggregate_requires_every_requested_delivery_rendered(self):
        plan = load_plan()
        plan["plan_status"] = "rendered"
        first_delivery = delivery(plan, "D16")
        first_delivery["status"] = "rendered"
        first_delivery["ready"] = True
        second_delivery = delivery(plan, "D9")
        second_delivery["status"] = "authorized"
        second_delivery["ready"] = False

        self.assertIn(
            "plan_status rendered: plan cannot be rendered before every "
            "requested delivery is rendered and ready",
            validate_edit_plan(plan),
        )

    def test_rendered_aggregate_requires_structured_success_evidence(self):
        plan = load_plan()
        plan["plan_status"] = "rendered"
        for requested_delivery in plan["delivery_specs"]:
            requested_delivery["status"] = "rendered"
            requested_delivery["ready"] = True
        plan["execution"]["tool_evidence"] = [
            {"tool_evidence_id": "TE-PENDING", "status": "pending"}
        ]
        plan["execution"]["rendered_outputs"] = [
            {"delivery_id": "D16"},
            {"delivery_id": "D9"},
        ]
        plan["edit_validation"]["ready"] = True

        errors = validate_edit_plan(plan)

        self.assertIn(
            "plan_status rendered: execution.tool_evidence must contain "
            "verified successful evidence",
            errors,
        )
        self.assertIn(
            "plan_status rendered: delivery D16 rendered output requires "
            "output_ref or path",
            errors,
        )
        self.assertIn(
            "plan_status rendered: delivery D16 rendered output requires "
            "tool_evidence_ref",
            errors,
        )
        self.assertIn(
            "plan_status rendered: delivery D16 rendered output requires "
            "probe_evidence_ref",
            errors,
        )
        self.assertIn(
            "plan_status rendered: delivery D16 per-delivery validation "
            "status must be passed",
            errors,
        )

    def test_complete_rendered_evidence_chain_is_valid(self):
        self.assertEqual(validate_edit_plan(rendered_plan()), [])

    def test_rendered_outputs_require_success_statuses(self):
        plan = rendered_plan()
        for output in plan["execution"]["rendered_outputs"]:
            output["tool_status"] = "failed"
            output["probe_status"] = "failed"

        errors = validate_edit_plan(plan)

        self.assertIn(
            "execution.rendered_outputs D16: tool_status must be a successful status",
            errors,
        )
        self.assertIn(
            "execution.rendered_outputs D16: probe_status must be a successful status",
            errors,
        )

    def test_rendered_rough_cut_allows_unverified_probe_with_complete_other_evidence(self):
        plan = rendered_plan()
        for output in plan["execution"]["rendered_outputs"]:
            output["probe_status"] = "unverified"

        self.assertEqual(validate_edit_plan(plan), [])

    def test_rendered_fine_and_final_still_reject_unverified_probe(self):
        for role in ("fine_cut", "final_master"):
            with self.subTest(role=role):
                plan = rendered_plan()
                delivery(plan, "D16")["version_role"] = role
                next(
                    output
                    for output in plan["execution"]["rendered_outputs"]
                    if output["delivery_id"] == "D16"
                )["probe_status"] = "unverified"

                self.assertIn(
                    "execution.rendered_outputs D16: probe_status must be a successful status",
                    validate_edit_plan(plan),
                )

    def test_rendered_aggregate_requires_current_authorization(self):
        plan = rendered_plan()
        plan["execution"].update(
            {
                "operation_authorization": "not_requested",
                "authorized_manifest_id": None,
                "authorized_version_directory": None,
            }
        )

        self.assertIn(
            "plan_status rendered: operation authorization must be approved",
            validate_edit_plan(plan),
        )

    def test_rendered_aggregate_yields_to_blocker_precedence(self):
        plan = rendered_plan()
        plan["edit_validation"]["blocking_errors"] = ["legal hold"]

        self.assertIn(
            "plan_status rendered: blockers require aggregate status blocked",
            validate_edit_plan(plan),
        )

    def test_failed_or_blocked_execution_step_has_blocker_precedence(self):
        for step_status in ("failed", "blocked"):
            with self.subTest(step_status=step_status):
                plan = rendered_plan()
                plan["execution"]["steps"] = [
                    {
                        "step_id": "STEP-D16",
                        "delivery_id": "D16",
                        "status": step_status,
                    }
                ]

                self.assertIn(
                    "plan_status rendered: blockers require aggregate status blocked",
                    validate_edit_plan(plan),
                )

    def test_complete_rendered_plan_allows_passed_execution_steps(self):
        plan = rendered_plan()
        plan["execution"]["steps"] = [
            {
                "step_id": f"STEP-{delivery_id}",
                "delivery_id": delivery_id,
                "status": "passed",
            }
            for delivery_id in ("D16", "D9")
        ]

        self.assertEqual(validate_edit_plan(plan), [])

    def test_final_ready_requires_rendered_status_and_complete_evidence(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["ready"] = True

        self.assertIn(
            "final master D16: ready requires rendered status and complete evidence",
            validate_edit_plan(plan, require_final=True),
        )

    def test_authorized_aggregate_requires_current_authorization(self):
        cases = (
            (
                {
                    "operation_authorization": "not_requested",
                    "authorized_manifest_id": None,
                    "authorized_version_directory": None,
                },
                "plan_status authorized: operation authorization must be approved",
            ),
            (
                {
                    "operation_authorization": "approved",
                    "authorized_manifest_id": "MAN-OTHER",
                    "authorized_version_directory": "edit/v999",
                },
                "plan_status authorized: authorization does not match dry-run manifest",
            ),
        )
        for execution_update, expected in cases:
            with self.subTest(expected=expected):
                plan = load_plan()
                plan["plan_status"] = "authorized"
                plan["execution"].update(execution_update)
                self.assertIn(expected, validate_edit_plan(plan))

    def test_authorized_aggregate_requires_pending_or_running_execution_step(self):
        cases = (
            (
                "rendered",
                [
                    {
                        "step_id": "STEP-D16",
                        "delivery_id": "D16",
                        "status": "passed",
                    }
                ],
            ),
            ("dry_run_passed", []),
        )
        for delivery_status, steps in cases:
            with self.subTest(delivery_status=delivery_status):
                plan = authorized_plan()
                for requested_delivery in plan["delivery_specs"]:
                    requested_delivery["status"] = delivery_status
                plan["execution"]["steps"] = steps

                self.assertIn(
                    "plan_status authorized: at least one requested delivery "
                    "requires a pending or running execution step",
                    validate_edit_plan(plan),
                )

    def test_authorized_aggregate_accepts_pending_execution_step(self):
        self.assertEqual(validate_edit_plan(authorized_plan()), [])

    def test_present_execution_steps_are_structurally_validated(self):
        cases = (
            (
                [None],
                "execution.steps item 1: expected object",
            ),
            (
                [{}],
                "execution step item-1: missing required field step_id",
            ),
            (
                [
                    {
                        "step_id": "STEP-UNKNOWN",
                        "delivery_id": "D404",
                        "status": "pending",
                    }
                ],
                "execution step STEP-UNKNOWN: unknown delivery_id D404",
            ),
            (
                [
                    {
                        "step_id": "STEP-D16",
                        "delivery_id": "D16",
                        "status": "pending",
                    },
                    {
                        "step_id": "STEP-D16",
                        "delivery_id": "D9",
                        "status": "running",
                    },
                ],
                "execution.steps: duplicate step_id STEP-D16",
            ),
            (
                [
                    {
                        "step_id": "STEP-D16",
                        "delivery_id": "D16",
                        "status": "queued",
                    }
                ],
                "execution step STEP-D16: status must be pending, running, "
                "passed, failed, or blocked",
            ),
        )
        for steps, expected in cases:
            with self.subTest(expected=expected):
                plan = authorized_plan()
                plan["execution"]["steps"] = steps

                self.assertIn(expected, validate_edit_plan(plan))

    def test_blocked_aggregate_requires_a_real_blocker(self):
        plan = load_plan()
        plan["plan_status"] = "blocked"

        self.assertIn(
            "plan_status blocked: no blocking requested delivery or shared dependency",
            validate_edit_plan(plan),
        )

    def test_trust_me_evidence_cannot_make_plan_rendered(self):
        plan = rendered_plan()
        plan["execution"]["tool_evidence"] = [
            {"tool_evidence_id": "TRUST-ME", "status": "verified"}
        ]
        plan["execution"]["probe_evidence"] = [
            {"probe_evidence_id": "TRUST-ME", "status": "passed"}
        ]
        for output in plan["execution"]["rendered_outputs"]:
            output["tool_evidence_ref"] = "TRUST-ME"
            output["probe_evidence_ref"] = "TRUST-ME"

        errors = validate_edit_plan(plan)

        self.assertIn(
            "execution.tool_evidence TRUST-ME: tool must be a non-empty string",
            errors,
        )
        self.assertIn(
            "execution.probe_evidence TRUST-ME: delivery_id must be a non-empty string",
            errors,
        )

    def test_rendered_output_and_validation_results_must_resolve(self):
        plan = load_plan()
        plan["execution"]["rendered_outputs"] = [
            {"delivery_id": "D404", "path": "edit/v001/missing.mp4"}
        ]
        plan["edit_validation"]["per_delivery_results"][0][
            "delivery_id"
        ] = "D405"
        errors = validate_edit_plan(plan)

        self.assertIn(
            "execution.rendered_outputs: unknown delivery_id D404", errors
        )
        self.assertIn(
            "edit_validation.per_delivery_results: unknown delivery_id D405",
            errors,
        )

    def test_rendered_output_path_must_match_delivery_destination(self):
        for output_field in ("output_ref", "path"):
            with self.subTest(output_field=output_field):
                plan = rendered_plan()
                output = next(
                    item
                    for item in plan["execution"]["rendered_outputs"]
                    if item["delivery_id"] == "D16"
                )
                output.pop("output_ref", None)
                output[output_field] = "source/escaped.mp4"
                probe = next(
                    item
                    for item in plan["execution"]["probe_evidence"]
                    if item["delivery_id"] == "D16"
                )
                probe["output_ref"] = "source/escaped.mp4"

                self.assertIn(
                    "execution.rendered_outputs D16: output must match or be "
                    "within delivery destination",
                    validate_edit_plan(plan),
                )

    def test_project_scoped_post_asset_does_not_require_shot_id(self):
        plan = load_plan()
        plan["media_bindings"].append(post_asset())

        self.assertEqual(validate_edit_plan(plan), [])

    def test_shot_asset_requires_shot_scope(self):
        plan = load_plan()
        asset(plan, "A01")["binding_scope"] = "project"

        self.assertIn(
            "asset A01: shot-derived media must use binding_scope shot",
            validate_edit_plan(plan),
        )

    def test_shot_asset_target_must_equal_shot_id(self):
        plan = load_plan()
        asset(plan, "A01")["target_id"] = "SH02"

        self.assertIn(
            "asset A01: target_id must equal shot_id",
            validate_edit_plan(plan),
        )

    def test_edit_unit_shot_id_must_match_shot_media_binding(self):
        plan = load_plan()
        units(plan, "TL-16")[0]["shot_id"] = "SH-WRONG"

        self.assertIn(
            "edit unit E16-01: shot_id must match asset A01 binding shot_id SH01",
            validate_edit_plan(plan),
        )

    def test_timeline_scoped_post_asset_target_must_resolve(self):
        plan = load_plan()
        binding = post_asset()
        binding["binding_scope"] = "timeline"
        binding["target_id"] = "TL-MISSING"
        plan["media_bindings"].append(binding)

        self.assertIn(
            "asset PA01: unknown timeline target_id TL-MISSING",
            validate_edit_plan(plan),
        )

    def test_timeline_scoped_audio_asset_cannot_cross_timelines(self):
        plan = load_plan()
        binding = post_asset("PA-TL9")
        binding["binding_scope"] = "timeline"
        binding["target_id"] = "TL-9"
        plan["media_bindings"].append(binding)
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC-TL9",
                "asset_id": "PA-TL9",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 2,
            }
        ]
        units(plan, "TL-16")[0]["audio_cue_ids"] = ["AC-TL9"]

        self.assertIn(
            "edit unit E16-01 audio cue AC-TL9: asset PA-TL9 binding_scope "
            "timeline target_id TL-9 does not match current timeline TL-16",
            validate_edit_plan(plan),
        )

    def test_edit_unit_scoped_asset_cannot_be_used_by_another_unit(self):
        plan = load_plan()
        binding = post_asset("PA-E9")
        binding["binding_scope"] = "edit_unit"
        binding["target_id"] = "E9-01"
        plan["media_bindings"].append(binding)
        units(plan, "TL-16")[0]["asset_id"] = "PA-E9"

        self.assertIn(
            "edit unit E16-01: asset PA-E9 binding_scope edit_unit target_id "
            "E9-01 does not match current edit_unit E16-01",
            validate_edit_plan(plan),
        )

    def test_edit_unit_scoped_text_cue_asset_cannot_cross_units(self):
        plan = load_plan()
        binding = post_asset("PA-TEXT-E9")
        binding["binding_scope"] = "edit_unit"
        binding["target_id"] = "E9-01"
        plan["media_bindings"].append(binding)
        plan["text_tracks"][0]["cues"] = [
            {"text_cue_id": "TC-E9", "asset_id": "PA-TEXT-E9"}
        ]
        units(plan, "TL-16")[0]["text_cue_ids"] = ["TC-E9"]

        self.assertIn(
            "edit unit E16-01 text cue TC-E9: asset PA-TEXT-E9 binding_scope "
            "edit_unit target_id E9-01 does not match current edit_unit E16-01",
            validate_edit_plan(plan),
        )

    def test_project_scoped_post_asset_can_cross_timelines(self):
        plan = load_plan()
        plan["media_bindings"].append(post_asset("PA-PROJECT"))
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC-PROJECT",
                "asset_id": "PA-PROJECT",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 2,
            }
        ]
        units(plan, "TL-16")[0]["audio_cue_ids"] = ["AC-PROJECT"]
        units(plan, "TL-9")[0]["audio_cue_ids"] = ["AC-PROJECT"]

        self.assertEqual(validate_edit_plan(plan), [])

    def test_mounted_audio_track_cue_asset_cannot_cross_timeline_scope(self):
        plan = load_plan()
        binding = post_asset("PA-TRACK-TL9")
        binding["binding_scope"] = "timeline"
        binding["target_id"] = "TL-9"
        plan["media_bindings"].append(binding)
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC-TRACK-TL9",
                "asset_id": "PA-TRACK-TL9",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 2,
            }
        ]

        self.assertIn(
            "timeline TL-16 audio track AT01 cue AC-TRACK-TL9: asset "
            "PA-TRACK-TL9 binding_scope timeline target_id TL-9 does not match "
            "current timeline TL-16",
            validate_edit_plan(plan),
        )

    def test_mounted_text_track_cue_asset_cannot_cross_timeline_scope(self):
        plan = load_plan()
        binding = post_asset("PA-TEXT-TRACK-TL9")
        binding["binding_scope"] = "timeline"
        binding["target_id"] = "TL-9"
        plan["media_bindings"].append(binding)
        plan["text_tracks"][0]["cues"] = [
            {
                "text_cue_id": "TC-TRACK-TL9",
                "asset_id": "PA-TEXT-TRACK-TL9",
            }
        ]

        self.assertIn(
            "timeline TL-16 text track TT01 cue TC-TRACK-TL9: asset "
            "PA-TEXT-TRACK-TL9 binding_scope timeline target_id TL-9 does not "
            "match current timeline TL-16",
            validate_edit_plan(plan),
        )

    def test_edit_unit_scoped_track_cue_requires_unique_explicit_unit_owner(self):
        plan = load_plan()
        binding = post_asset("PA-TRACK-E9")
        binding["binding_scope"] = "edit_unit"
        binding["target_id"] = "E9-01"
        plan["media_bindings"].append(binding)
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC-TRACK-E9",
                "asset_id": "PA-TRACK-E9",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 2,
            }
        ]

        self.assertIn(
            "timeline TL-9 audio track AT01 cue AC-TRACK-E9: edit_unit-scoped "
            "asset PA-TRACK-E9 must be explicitly referenced by its unique "
            "target unit E9-01",
            validate_edit_plan(plan),
        )

    def test_project_scoped_track_cue_assets_are_valid_across_timelines(self):
        plan = load_plan()
        plan["media_bindings"].extend(
            [post_asset("PA-TRACK-AUDIO"), post_asset("PA-TRACK-TEXT")]
        )
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC-TRACK-PROJECT",
                "asset_id": "PA-TRACK-AUDIO",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 2,
            }
        ]
        plan["text_tracks"][0]["cues"] = [
            {
                "text_cue_id": "TC-TRACK-PROJECT",
                "asset_id": "PA-TRACK-TEXT",
            }
        ]

        self.assertEqual(validate_edit_plan(plan), [])

    def test_unit_audio_cue_must_belong_to_referenced_timeline_track(self):
        plan = load_plan()
        plan["media_bindings"].append(post_asset("PA-AUDIO"))
        second_track = copy.deepcopy(plan["audio_tracks"][0])
        second_track["audio_track_id"] = "AT02"
        second_track["cues"] = [
            {
                "audio_cue_id": "AC02",
                "asset_id": "PA-AUDIO",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 2,
            }
        ]
        plan["audio_tracks"].append(second_track)
        units(plan, "TL-16")[0]["audio_cue_ids"] = ["AC02"]

        self.assertIn(
            "edit unit E16-01: audio_cue_id AC02 belongs to unreferenced "
            "audio track AT02",
            validate_edit_plan(plan),
        )

    def test_unit_text_cue_must_belong_to_referenced_timeline_track(self):
        plan = load_plan()
        second_track = copy.deepcopy(plan["text_tracks"][0])
        second_track["text_track_id"] = "TT02"
        second_track["cues"] = [{"text_cue_id": "TC02"}]
        plan["text_tracks"].append(second_track)
        units(plan, "TL-16")[0]["text_cue_ids"] = ["TC02"]

        self.assertIn(
            "edit unit E16-01: text_cue_id TC02 belongs to unreferenced "
            "text track TT02",
            validate_edit_plan(plan),
        )

    def test_timeline_track_refs_cannot_duplicate_tracks(self):
        cases = (
            (
                "audio_track_refs",
                "AT01",
                "timeline TL-16: duplicate audio_track_id AT01 in audio_track_refs",
            ),
            (
                "text_track_refs",
                "TT01",
                "timeline TL-16: duplicate text_track_id TT01 in text_track_refs",
            ),
        )
        for field, track_id, expected in cases:
            with self.subTest(field=field):
                plan = load_plan()
                timeline(plan, "TL-16")[field].append(track_id)
                self.assertIn(expected, validate_edit_plan(plan))

    def test_duplicate_asset_id_is_rejected(self):
        plan = load_plan()
        plan["media_bindings"].append(copy.deepcopy(asset(plan, "A01")))

        self.assertIn(
            "media_bindings: duplicate asset_id A01", validate_edit_plan(plan)
        )

    def test_unresolved_asset_reference_is_rejected(self):
        plan = load_plan()
        units(plan, "TL-16")[0]["asset_id"] = "A404"

        self.assertIn(
            "edit unit E16-01: unknown asset_id A404", validate_edit_plan(plan)
        )

    def test_fallback_asset_reference_must_resolve(self):
        plan = load_plan()
        asset(plan, "A01")["fallback_asset_id"] = "A404"

        self.assertIn(
            "asset A01: unknown fallback_asset_id A404",
            validate_edit_plan(plan),
        )

    def test_aspect_set_must_be_exactly_dual_aspect(self):
        plan = load_plan()
        plan["timelines"] = [timeline(plan, "TL-16")]

        self.assertIn(
            "timelines: aspect ratios must equal 16:9 and 9:16",
            validate_edit_plan(plan),
        )

    def test_v1_sequence_must_be_contiguous_from_one(self):
        plan = load_plan()
        units(plan, "TL-16")[1]["sequence"] = 3

        self.assertIn(
            "timeline TL-16: V1 sequence must be contiguous from 1",
            validate_edit_plan(plan),
        )

    def test_timeline_duration_must_match_target(self):
        plan = load_plan()
        timeline(plan, "TL-16")["duration_seconds"] = 5

        self.assertIn(
            "timeline TL-16: duration_seconds must equal target duration",
            validate_edit_plan(plan),
        )

    def test_edit_unit_duration_must_match_timeline_range(self):
        plan = load_plan()
        units(plan, "TL-16")[0]["duration_seconds"] = 1

        self.assertIn(
            "edit unit E16-01: timeline range must equal duration_seconds",
            validate_edit_plan(plan),
        )

    def test_final_timeline_out_must_match_target_duration(self):
        plan = load_plan()
        plan["target_duration_seconds"] = 5

        self.assertIn(
            "timeline TL-16: final out must equal target duration",
            validate_edit_plan(plan),
        )

    def test_top_level_fields_and_container_shapes_are_required(self):
        plan = load_plan()
        del plan["look_plan"]
        plan["timelines"] = "not-a-list"
        errors = validate_edit_plan(plan)

        self.assertIn("edit plan: missing required field look_plan", errors)
        self.assertIn("timelines: expected list", errors)

    def test_empty_look_plan_requires_canonical_fields(self):
        plan = load_plan()
        plan["look_plan"] = {}

        errors = validate_edit_plan(plan)

        self.assertIn("look_plan: missing required field input_color_space", errors)
        self.assertIn("look_plan: missing required field output_color_space", errors)
        self.assertIn("look_plan: missing required field matching_status", errors)
        self.assertIn("look_plan: missing required field instructions", errors)
        self.assertIn("look_plan: missing required field ffmpeg_filters", errors)

    def test_empty_edit_validation_requires_canonical_fields(self):
        plan = load_plan()
        plan["edit_validation"] = {}

        errors = validate_edit_plan(plan)

        self.assertIn("edit_validation: missing required field ready", errors)
        self.assertIn("edit_validation: missing required field checks", errors)
        self.assertIn(
            "edit_validation: missing required field blocking_errors", errors
        )
        self.assertIn(
            "edit_validation: missing required field per_delivery_results", errors
        )

    def test_unhashable_enum_values_are_rejected_without_crashing(self):
        mutations = (
            ("plan status", lambda plan: plan.update({"plan_status": []})),
            (
                "media source type",
                lambda plan: asset(plan, "A01").update({"source_type": {}}),
            ),
            (
                "timeline aspect",
                lambda plan: timeline(plan, "TL-16").update(
                    {"aspect_ratio": []}
                ),
            ),
            (
                "delivery subtitle mode",
                lambda plan: delivery(plan, "D16").update(
                    {"subtitle_mode": []}
                ),
            ),
        )
        for label, mutate in mutations:
            with self.subTest(label=label):
                plan = load_plan()
                mutate(plan)
                self.assertTrue(validate_edit_plan(plan))

    def test_malformed_nested_reference_lists_do_not_crash(self):
        mutations = (
            lambda plan: timeline(plan, "TL-16").update(
                {"audio_track_refs": None}
            ),
            lambda plan: units(plan, "TL-16")[0].update(
                {"audio_cue_ids": None}
            ),
            lambda plan: timeline(plan, "TL-16").update({"export_refs": None}),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                plan = load_plan()
                mutate(plan)
                self.assertTrue(validate_edit_plan(plan))

    def test_unhashable_reference_id_is_rejected_without_crashing(self):
        plan = load_plan()
        delivery(plan, "D16")["timeline_id"] = {}

        self.assertTrue(validate_edit_plan(plan, require_final=True))

    def test_numeric_edge_cases_are_rejected_without_crashing(self):
        invalid_values = [
            True,
            "NaN",
            "Infinity",
            float("nan"),
            float("inf"),
            "not-a-number",
            0,
            -1,
        ]
        for value in invalid_values:
            with self.subTest(value=repr(value)):
                plan = load_plan()
                plan["target_duration_seconds"] = value
                self.assertIn(
                    "target_duration_seconds must be a positive finite number",
                    validate_edit_plan(plan),
                )

    def test_duration_and_speed_must_be_positive_finite_numbers(self):
        for field, value, expected in (
            (
                "duration_seconds",
                0,
                "edit unit E16-01: duration_seconds must be a positive "
                "finite number",
            ),
            (
                "duration_seconds",
                -1,
                "edit unit E16-01: duration_seconds must be a positive "
                "finite number",
            ),
            (
                "speed",
                0,
                "edit unit E16-01: speed must be a positive finite number",
            ),
            (
                "speed",
                "broken",
                "edit unit E16-01: speed must be a positive finite number",
            ),
        ):
            with self.subTest(field=field, value=value):
                plan = load_plan()
                units(plan, "TL-16")[0][field] = value
                self.assertIn(expected, validate_edit_plan(plan))

    def test_require_final_blocks_offline_or_unverified_media(self):
        plan = load_plan()
        prepare_ffmpeg_final(plan)
        asset(plan, "A01")["file_status"] = "offline"
        asset(plan, "A01")["probe_status"] = "unverified"

        self.assertIn(
            "asset A01: final delivery requires online verified media",
            validate_edit_plan(plan, require_final=True),
        )

    def test_require_final_blocks_uncleared_rights(self):
        plan = load_plan()
        prepare_ffmpeg_final(plan)
        asset(plan, "A01")["rights_status"] = "pending"

        self.assertIn(
            "asset A01: final delivery requires cleared rights",
            validate_edit_plan(plan, require_final=True),
        )

    def test_require_final_blocks_subtitle_safe_area_failure(self):
        plan = load_plan()
        prepare_ffmpeg_final(plan)
        plan["text_tracks"][0]["safe_area_status"] = "failed"

        self.assertIn(
            "text track TT01: safe area must pass for final delivery",
            validate_edit_plan(plan, require_final=True),
        )

    def test_require_final_blocks_failed_look_matching(self):
        plan = load_plan()
        prepare_ffmpeg_final(plan)
        plan["look_plan"]["matching_status"] = "failed"

        self.assertIn(
            "look_plan: matching must pass for final delivery",
            validate_edit_plan(plan, require_final=True),
        )

    def test_ready_final_master_is_rejected_when_blockers_remain(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["ready"] = True
        asset(plan, "A01")["file_status"] = "offline"

        self.assertIn(
            "final master D16: ready cannot be true while final blockers remain",
            validate_edit_plan(plan, require_final=True),
        )

    def test_delivery_mode_enums_are_validated(self):
        enum_cases = {
            "subtitle_mode": (
                {"none", "sidecar", "burn_in"},
                "none, sidecar, or burn_in",
            ),
            "audio_mode": (
                {"temporary_or_silent", "final_mix", "none"},
                "temporary_or_silent, final_mix, or none",
            ),
            "look_mode": ({"none", "approved"}, "none or approved"),
            "render_backend": (
                {
                    "ffmpeg",
                    "premiere",
                    "resolve",
                    "jianying_capcut",
                    "ai_editor",
                    "manual",
                },
                "ffmpeg, premiere, resolve, jianying_capcut, ai_editor, or manual",
            ),
        }
        for field, (allowed, rendered_allowed) in enum_cases.items():
            with self.subTest(field=field):
                plan = load_plan()
                delivery(plan, "D16")[field] = "unsupported"
                self.assertIn(
                    f"delivery D16: {field} must be {rendered_allowed}",
                    validate_edit_plan(plan),
                )
                for value in allowed:
                    valid_plan = load_plan()
                    delivery(valid_plan, "D16")[field] = value
                    enum_errors = [
                        error
                        for error in validate_edit_plan(valid_plan)
                        if error.startswith(f"delivery D16: {field} must be")
                    ]
                    self.assertEqual(enum_errors, [])

    def test_ffmpeg_final_rejects_unsupported_transition(self):
        plan = load_plan()
        prepare_ffmpeg_final(plan)
        units(plan, "TL-16")[0]["transition_out"] = "dissolve"

        self.assertIn(
            "final master D16: ffmpeg does not support transition dissolve "
            "in E16-01",
            validate_edit_plan(plan, require_final=True),
        )

    def test_ffmpeg_final_rejects_unsupported_effect(self):
        plan = load_plan()
        prepare_ffmpeg_final(plan)
        units(plan, "TL-16")[0]["effects"] = [{"type": "glow"}]

        self.assertIn(
            "final master D16: ffmpeg does not support effect glow in E16-01",
            validate_edit_plan(plan, require_final=True),
        )

    def test_ffmpeg_final_rejects_raw_filter_strings(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["look_mode"] = "approved"
        plan["look_plan"]["ffmpeg_filters"] = ["eq=contrast=1.1"]

        self.assertIn(
            "look_plan.ffmpeg_filters: raw filter strings are not allowed",
            validate_edit_plan(plan, require_final=True),
        )

    def test_ffmpeg_final_accepts_structured_safe_look_filters(self):
        safe_filters = (
            ({"filter": "eq", "params": {"contrast": 1.1}}, None),
            (
                {"name": "curves", "params": {"preset": "medium_contrast"}},
                None,
            ),
            (
                {"name": "lut3d", "params": {"asset_id": "LUT-01"}},
                "LUT-01",
            ),
        )
        for filter_value, lut_asset_id in safe_filters:
            with self.subTest(filter_value=filter_value):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery["look_mode"] = "approved"
                if lut_asset_id is not None:
                    lut = post_asset(lut_asset_id)
                    lut["path_or_uri"] = "media/approved.cube"
                    plan["media_bindings"].append(lut)
                plan["look_plan"]["ffmpeg_filters"] = [filter_value]
                self.assertEqual(
                    validate_edit_plan(plan, require_final=True), []
                )

    def test_ffmpeg_filter_requires_an_exact_discriminator_shape(self):
        malformed_filters = (
            {"name": "eq", "filter": "movie", "params": {}},
            {"name": "eq", "filter": "eq", "params": {}},
            {"name": "eq", "params": {}, "extra": "ignored"},
        )
        for filter_value in malformed_filters:
            with self.subTest(filter_value=filter_value):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery["look_mode"] = "approved"
                plan["look_plan"]["ffmpeg_filters"] = [filter_value]

                self.assertIn(
                    "look_plan.ffmpeg_filters: item 1 must have exact shape "
                    "{name, params} or {filter, params}",
                    validate_edit_plan(plan, require_final=True),
                )

    def test_ffmpeg_lut3d_rejects_lexically_unsafe_asset_path(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["look_mode"] = "approved"
        lut = post_asset("LUT-UNSAFE")
        lut["path_or_uri"] = "media/a' :interp=foo.cube"
        plan["media_bindings"].append(lut)
        plan["look_plan"]["ffmpeg_filters"] = [
            {"name": "lut3d", "params": {"asset_id": "LUT-UNSAFE"}}
        ]

        self.assertIn(
            "look_plan.ffmpeg_filters: filter lut3d asset LUT-UNSAFE must use "
            "a safe .cube path",
            validate_edit_plan(plan, require_final=True),
        )

    def test_ffmpeg_lut3d_accepts_authorized_absolute_paths_lexically(self):
        cases = (
            (
                r"C:\renders",
                r"C:\renders\v001",
                r"C:\media",
                r"C:\media\look.cube",
                (r"C:\media\SH01_T01.mp4", r"C:\media\SH02_T01.mp4"),
            ),
            (
                "/renders",
                "/renders/v001",
                "/media",
                "/media/look.cube",
                ("/media/SH01_T01.mp4", "/media/SH02_T01.mp4"),
            ),
        )
        for output_root, version_directory, media_root, lut_path, media_paths in cases:
            with self.subTest(lut_path=lut_path):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery["look_mode"] = "approved"
                plan["execution"].update(
                    {
                        "output_root": output_root,
                        "version_directory": version_directory,
                        "authorized_media_roots": [media_root],
                    }
                )
                asset(plan, "A01")["path_or_uri"] = media_paths[0]
                asset(plan, "A02")["path_or_uri"] = media_paths[1]
                lut = post_asset("LUT-ABS")
                lut["path_or_uri"] = lut_path
                plan["media_bindings"].append(lut)
                plan["look_plan"]["ffmpeg_filters"] = [
                    {"name": "lut3d", "params": {"asset_id": "LUT-ABS"}}
                ]

                self.assertEqual(validate_edit_plan(plan, require_final=True), [])

    def test_ffmpeg_lut3d_rejects_raw_or_unsafe_params(self):
        cases = (
            (
                {"name": "lut3d", "params": {"file": "evil.cube;movie=x"}},
                "look_plan.ffmpeg_filters: filter lut3d has unsupported param file",
            ),
            (
                {"name": "lut3d", "params": {"asset_id": "LUT;[evil]"}},
                "look_plan.ffmpeg_filters: filter lut3d asset_id contains unsafe characters",
            ),
        )
        for filter_value, expected in cases:
            with self.subTest(filter_value=filter_value):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery["look_mode"] = "approved"
                plan["look_plan"]["ffmpeg_filters"] = [filter_value]
                self.assertIn(expected, validate_edit_plan(plan, require_final=True))

    def test_ffmpeg_eq_rejects_non_numeric_or_out_of_range_params(self):
        cases = (
            (
                {"name": "eq", "params": {"brightness": "1;movie=x"}},
                "look_plan.ffmpeg_filters: filter eq param brightness must be a finite number",
            ),
            (
                {"name": "eq", "params": {"contrast": 3}},
                "look_plan.ffmpeg_filters: filter eq param contrast must be between 0 and 2",
            ),
        )
        for filter_value, expected in cases:
            with self.subTest(filter_value=filter_value):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery["look_mode"] = "approved"
                plan["look_plan"]["ffmpeg_filters"] = [filter_value]
                self.assertIn(expected, validate_edit_plan(plan, require_final=True))

    def test_ffmpeg_curves_rejects_raw_curve_syntax(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["look_mode"] = "approved"
        plan["look_plan"]["ffmpeg_filters"] = [
            {"name": "curves", "params": {"preset": "0/0 0.5/0.8 1/1"}}
        ]

        self.assertIn(
            "look_plan.ffmpeg_filters: filter curves preset must be a safe named preset",
            validate_edit_plan(plan, require_final=True),
        )

    def test_ffmpeg_final_rejects_unknown_or_malformed_look_filters(self):
        for filter_value in (
            {"name": "unsharp", "params": {}},
            {"name": "eq", "params": "contrast=1.1"},
        ):
            with self.subTest(filter_value=filter_value):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery["look_mode"] = "approved"
                plan["look_plan"]["ffmpeg_filters"] = [filter_value]
                self.assertTrue(
                    any(
                        error.startswith("look_plan.ffmpeg_filters:")
                        for error in validate_edit_plan(
                            plan, require_final=True
                        )
                    )
                )

    def test_audio_cue_requires_authorized_local_post_binding(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["audio_mode"] = "final_mix"
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC01",
                "asset_id": "A404",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 4,
            }
        ]

        self.assertIn(
            "final master D16: audio cue AC01 asset_id A404 is not an "
            "authorized local/post binding",
            validate_edit_plan(plan, require_final=True),
        )

    def test_active_audio_cue_asset_must_resolve_during_normal_validation(self):
        plan = load_plan()
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC01",
                "asset_id": "A404",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 2,
            }
        ]
        units(plan, "TL-16")[0]["audio_cue_ids"] = ["AC01"]

        self.assertIn(
            "audio cue AC01: unknown asset_id A404",
            validate_edit_plan(plan),
        )

    def test_audio_cue_accepts_authorized_local_post_binding(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["audio_mode"] = "final_mix"
        plan["media_bindings"].append(post_asset("PA-MUSIC"))
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC01",
                "asset_id": "PA-MUSIC",
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 4,
            }
        ]

        self.assertEqual(validate_edit_plan(plan, require_final=True), [])

    def test_unhashable_audio_asset_reference_does_not_crash(self):
        plan = load_plan()
        final_delivery = prepare_ffmpeg_final(plan)
        final_delivery["audio_mode"] = "final_mix"
        plan["audio_tracks"][0]["cues"] = [
            {
                "audio_cue_id": "AC01",
                "asset_id": {},
                "timeline_in_seconds": 0,
                "timeline_out_seconds": 4,
            }
        ]

        self.assertTrue(validate_edit_plan(plan, require_final=True))

    def test_unhashable_final_render_backend_is_rejected_without_crashing(self):
        plan = load_plan()
        final_delivery = delivery(plan, "D16")
        final_delivery["version_role"] = "final_master"
        final_delivery["render_backend"] = {}

        self.assertIn(
            "delivery D16: render_backend must be ffmpeg, premiere, resolve, "
            "jianying_capcut, ai_editor, or manual",
            validate_edit_plan(plan, require_final=True),
        )

    def test_unhashable_software_target_status_is_rejected_without_crashing(self):
        plan = rendered_plan()
        final_delivery = delivery(plan, "D16")
        final_delivery["version_role"] = "final_master"
        final_delivery["subtitle_mode"] = "none"
        final_delivery["audio_mode"] = "none"
        generic_target = next(
            item for item in plan["software_targets"] if item["target"] == "generic"
        )
        generic_target["status"] = {}

        self.assertIn(
            "software target item 1: status must be a non-empty string",
            validate_edit_plan(plan, require_final=True),
        )

    def test_unhashable_ffmpeg_modes_are_rejected_without_crashing(self):
        cases = (
            (
                "subtitle_mode",
                "delivery D16: subtitle_mode must be none, sidecar, or burn_in",
            ),
            (
                "audio_mode",
                "delivery D16: audio_mode must be temporary_or_silent, final_mix, "
                "or none",
            ),
        )
        for field, expected in cases:
            with self.subTest(field=field):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery[field] = {}

                self.assertIn(
                    expected, validate_edit_plan(plan, require_final=True)
                )

    def test_unhashable_rendered_output_reference_does_not_crash(self):
        plan = load_plan()
        plan["plan_status"] = "rendered"
        for requested_delivery in plan["delivery_specs"]:
            requested_delivery["status"] = "rendered"
            requested_delivery["ready"] = True
        plan["execution"]["tool_evidence"] = [{"status": "passed"}]
        plan["execution"]["rendered_outputs"] = [
            {"delivery_id": {}},
            {"delivery_id": "D9"},
        ]
        plan["edit_validation"]["ready"] = True

        self.assertTrue(validate_edit_plan(plan))

    def test_unhashable_render_evidence_status_does_not_crash(self):
        plan = load_plan()
        plan["plan_status"] = "rendered"
        for requested_delivery in plan["delivery_specs"]:
            requested_delivery["status"] = "rendered"
            requested_delivery["ready"] = True
        plan["execution"]["tool_evidence"] = [
            {"tool_evidence_id": "TE-001", "status": {}}
        ]
        plan["execution"]["rendered_outputs"] = [
            {
                "delivery_id": delivery_id,
                "output_ref": f"OUT-{delivery_id}",
                "tool_evidence_ref": "TE-001",
                "tool_status": "passed",
                "probe_evidence_ref": f"PROBE-{delivery_id}",
                "probe_status": "passed",
            }
            for delivery_id in ("D16", "D9")
        ]
        for result in plan["edit_validation"]["per_delivery_results"]:
            result["status"] = "passed"
        plan["edit_validation"]["ready"] = True

        self.assertTrue(validate_edit_plan(plan))

    def test_ffmpeg_final_rejects_unsupported_delivery_configurations(self):
        cases = (
            (
                "subtitle_mode",
                "sidecar",
                "final master D16: ffmpeg subtitle configuration is unsupported",
            ),
            (
                "audio_mode",
                "temporary_or_silent",
                "final master D16: ffmpeg audio configuration is unsupported",
            ),
            (
                "look_mode",
                "approved",
                "final master D16: ffmpeg look configuration is unsupported",
            ),
            (
                "render_backend",
                "manual",
                "final master D16: render backend manual is not executable",
            ),
        )
        for field, value, expected in cases:
            with self.subTest(field=field):
                plan = load_plan()
                final_delivery = prepare_ffmpeg_final(plan)
                final_delivery[field] = value
                self.assertIn(
                    expected, validate_edit_plan(plan, require_final=True)
                )

    def test_final_ready_backend_requires_supported_software_target(self):
        cases = (
            (
                "manual_or_unverified",
                "final master D16: software target jianying_capcut must be "
                "supported or verified",
            ),
            (
                "blocked",
                "final master D16: software target jianying_capcut must be "
                "supported or verified",
            ),
        )
        for status, expected in cases:
            with self.subTest(status=status):
                plan = rendered_plan()
                final_delivery = delivery(plan, "D16")
                final_delivery["version_role"] = "final_master"
                final_delivery["render_backend"] = "jianying_capcut"
                plan["software_targets"].append(
                    {"target": "jianying_capcut", "status": status}
                )

                self.assertIn(
                    expected, validate_edit_plan(plan, require_final=True)
                )

    def test_final_ready_backend_rejects_missing_software_target(self):
        plan = rendered_plan()
        final_delivery = delivery(plan, "D16")
        final_delivery["version_role"] = "final_master"
        final_delivery["render_backend"] = "jianying_capcut"

        self.assertIn(
            "final master D16: missing software target jianying_capcut",
            validate_edit_plan(plan, require_final=True),
        )

    def test_final_ready_backend_target_mapping(self):
        target_by_backend = {
            "ffmpeg": "generic",
            "premiere": "premiere",
            "resolve": "resolve",
            "jianying_capcut": "jianying_capcut",
            "ai_editor": "ai_editor",
        }
        for backend, target in target_by_backend.items():
            with self.subTest(backend=backend):
                plan = rendered_plan()
                final_delivery = delivery(plan, "D16")
                final_delivery["version_role"] = "final_master"
                final_delivery["render_backend"] = backend
                if backend == "ffmpeg":
                    final_delivery["subtitle_mode"] = "none"
                    final_delivery["audio_mode"] = "none"
                if not any(
                    item["target"] == target
                    for item in plan["software_targets"]
                ):
                    plan["software_targets"].append(
                        {"target": target, "status": "supported"}
                    )

                self.assertEqual(
                    validate_edit_plan(plan, require_final=True), []
                )

    def test_non_ffmpeg_final_ready_still_requires_render_evidence(self):
        plan = load_plan()
        final_delivery = delivery(plan, "D16")
        final_delivery["version_role"] = "final_master"
        final_delivery["render_backend"] = "resolve"
        final_delivery["status"] = "rendered"
        final_delivery["ready"] = True
        plan["software_targets"].append(
            {"target": "resolve", "status": "supported"}
        )

        self.assertIn(
            "final master D16: ready requires rendered status and complete evidence",
            validate_edit_plan(plan, require_final=True),
        )

    def test_cli_valid_plan_returns_zero(self):
        code, stdout, stderr = run_cli([FIXTURES_DIR / "valid_plan.json"])

        self.assertEqual(code, 0)
        self.assertEqual(stdout, "Edit plan is valid.\n")
        self.assertEqual(stderr, "")

    def test_cli_validation_errors_return_one_and_are_listed(self):
        code, stdout, stderr = run_cli([FIXTURES_DIR / "overlap_plan.json"])

        self.assertEqual(code, 1)
        self.assertIn("- timeline TL-16: overlap before E16-02\n", stdout)
        self.assertTrue(
            all(line.startswith("- ") for line in stdout.splitlines())
        )
        self.assertEqual(stderr, "")

    def test_cli_missing_file_returns_two(self):
        code, stdout, stderr = run_cli([FIXTURES_DIR / "missing.json"])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("could not read", stderr)

    def test_cli_invalid_json_returns_two(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid_path = Path(temp_dir) / "invalid.json"
            invalid_path.write_text("{not-json", encoding="utf-8")
            code, stdout, stderr = run_cli([invalid_path])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("invalid JSON", stderr)

    def test_cli_deeply_nested_json_returns_two_without_traceback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            deep_path = Path(temp_dir) / "deep.json"
            deep_path.write_text(
                "[" * 20000 + "0" + "]" * 20000,
                encoding="utf-8",
            )
            try:
                code, stdout, stderr = run_cli([deep_path])
            except RecursionError as exc:
                self.fail(f"CLI leaked RecursionError: {exc}")

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("invalid JSON", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_cli_json_memory_error_returns_two_without_traceback(self):
        with mock.patch("validate_edit_plan.json.load", side_effect=MemoryError):
            try:
                code, stdout, stderr = run_cli(
                    [FIXTURES_DIR / "valid_plan.json"]
                )
            except MemoryError as exc:
                self.fail(f"CLI leaked MemoryError: {exc}")

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("invalid JSON", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_cli_rejects_plan_larger_than_ten_mib_without_reading_it(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            oversized_path = Path(temp_dir) / "oversized.json"
            with oversized_path.open("wb") as oversized_file:
                oversized_file.seek(10 * 1024 * 1024)
                oversized_file.write(b" ")
            code, stdout, stderr = run_cli([oversized_path])

        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("exceeds maximum size of 10 MiB", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_identical_errors_are_deduplicated_in_first_seen_order(self):
        plan = load_plan()
        plan["execution"]["output_root"] = None
        plan["execution"]["version_directory"] = None

        self.assertEqual(
            validate_edit_plan(plan),
            [
                "execution: output_root must be a non-empty string",
                "execution: version_directory must be a non-empty string",
            ],
        )

    def test_cli_supports_require_final_and_for_execution_flags(self):
        final_code, final_stdout, _ = run_cli(
            [FIXTURES_DIR / "missing_media_plan.json", "--require-final"]
        )
        execution_code, execution_stdout, _ = run_cli(
            [FIXTURES_DIR / "valid_plan.json", "--for-execution"]
        )

        self.assertEqual(final_code, 1)
        self.assertIn("placeholder media is not allowed", final_stdout)
        self.assertEqual(execution_code, 1)
        self.assertIn("operation authorization is required", execution_stdout)


if __name__ == "__main__":
    unittest.main()
