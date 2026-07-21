import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "editing" / "valid_plan.json"
JIANYING_FIXTURE = (
    ROOT / "tests" / "fixtures" / "editing" / "jianying_plan.json"
)
CINEMATIC_FIXTURE = (
    ROOT / "tests" / "fixtures" / "editing" / "cinematic_valid_plan.json"
)
CINEMATIC_PPT_FIXTURE = (
    ROOT / "tests" / "fixtures" / "editing" / "cinematic_ppt_plan.json"
)
sys.path.insert(0, str(SCRIPTS_DIR))

from build_edit_bundle import BuildError, build_edit_bundle, main, next_version_dir
from cinematic_report import cinematic_report_markdown, cinematic_report_payload
from validate_edit_plan import validate_edit_plan


def load_plan(path=FIXTURE):
    with Path(path).open("r", encoding="utf-8") as source:
        return json.load(source)


def write_plan(directory, plan, name="plan.json"):
    path = Path(directory) / name
    path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


def authorize_plan(plan, version_directory="edit/v001"):
    output_root = version_directory.rsplit("/", 1)[0]
    plan["plan_status"] = "authorized"
    plan["execution"].update(
        {
            "operation_authorization": "approved",
            "output_root": output_root,
            "authorized_manifest_id": "MAN-001",
            "version_directory": version_directory,
            "authorized_version_directory": version_directory,
            "tool_evidence": [
                {
                    "tool_evidence_id": "AUTH-FFMPEG",
                    "tool": "ffmpeg",
                    "path": "ffmpeg-test",
                    "status": "verified",
                },
                {
                    "tool_evidence_id": "AUTH-FFPROBE",
                    "tool": "ffprobe",
                    "path": "ffprobe-test",
                    "status": "verified",
                },
            ],
            "steps": [
                {
                    "step_id": "STEP-D16",
                    "delivery_id": "D16",
                    "status": "pending",
                },
                {
                    "step_id": "STEP-D9",
                    "delivery_id": "D9",
                    "status": "pending",
                },
            ],
        }
    )
    for delivery in plan["delivery_specs"]:
        delivery["status"] = "authorized"
        delivery["destination"] = (
            f"{version_directory}/{delivery['filename']}"
        )
    return plan


def authorized_plan():
    return authorize_plan(load_plan())


def materialize_plan_media(directory, plan):
    """Create only test-owned fake inputs beside the temporary plan."""

    root = Path(directory)
    for binding in plan["media_bindings"]:
        if binding.get("source_type") not in {
            "local_file",
            "post_asset",
            "generated_placeholder",
        }:
            continue
        path = Path(binding["path_or_uri"])
        if path.is_absolute():
            destination = path
        else:
            destination = root / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"test media")


def write_authorized_plan(
    directory,
    plan=None,
    name="plan.json",
    version_directory="edit/v001",
):
    selected = (
        authorize_plan(load_plan(), version_directory)
        if plan is None
        else authorize_plan(plan, version_directory)
    )
    materialize_plan_media(directory, selected)
    return selected, write_plan(directory, selected, name)


def rich_tier_plan(role):
    plan = load_plan()
    plan["media_bindings"].append(
        {
            "asset_id": "AUD01",
            "binding_scope": "project",
            "target_id": "PKG-001",
            "source_type": "post_asset",
            "path_or_uri": "media/music.wav",
            "file_status": "online",
            "rights_status": "cleared",
            "probe_status": "verified",
            "selection_reason": "approved music",
            "acceptance_status": "approved",
        }
    )
    plan["audio_tracks"][0]["cues"] = [
        {
            "audio_cue_id": "AC01",
            "asset_id": "AUD01",
            "timeline_in_seconds": 0,
            "timeline_out_seconds": 4,
            "gain_db": -3,
        }
    ]
    plan["text_tracks"][0]["cues"] = [
        {
            "text_cue_id": "TC01",
            "text": "Approved subtitle",
            "timeline_in_seconds": 0,
            "timeline_out_seconds": 2,
        },
        {
            "text_cue_id": "TC02",
            "text": "Approved closing subtitle",
            "timeline_in_seconds": 2,
            "timeline_out_seconds": 4,
        },
    ]
    for timeline in plan["timelines"]:
        timeline["video_tracks"][0]["edit_units"][0]["audio_cue_ids"] = ["AC01"]
        timeline["video_tracks"][0]["edit_units"][0]["text_cue_ids"] = ["TC01"]
        timeline["video_tracks"][0]["edit_units"][1]["text_cue_ids"] = ["TC02"]
    plan["look_plan"]["ffmpeg_filters"] = [
        {"name": "eq", "params": {"contrast": 1.1}}
    ]
    for delivery in plan["delivery_specs"]:
        delivery["version_role"] = role
        delivery["subtitle_mode"] = "burn_in"
        delivery["audio_mode"] = "final_mix"
        delivery["look_mode"] = "approved" if role == "final_master" else "none"
    return plan


def normalized_commands(delivery_plan, version_dir):
    prefix = str(version_dir.resolve())
    return [
        [arg.replace(prefix, "<VERSION>") for arg in command]
        for command in delivery_plan["commands"]
    ]


class BuildEditBundleTests(unittest.TestCase):
    def test_next_version_dir_increments_without_reusing_gaps_or_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir) / "edit"
            root.mkdir()
            self.assertEqual(next_version_dir(root), root.resolve() / "v001")
            (root / "v001").mkdir()
            (root / "v002").write_text("reserved", encoding="utf-8")
            self.assertEqual(next_version_dir(root), root.resolve() / "v003")

    def test_dry_run_uses_a_new_directory_and_does_not_change_old_versions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "edit"
            old_version = output_root / "v001"
            old_version.mkdir(parents=True)
            sentinel = old_version / "keep.txt"
            sentinel.write_text("original", encoding="utf-8")

            created = build_edit_bundle(FIXTURE, output_root)

            self.assertEqual(created, output_root.resolve() / "v002")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "original")
            self.assertEqual(
                json.loads((created / "bundle_manifest.json").read_text(encoding="utf-8"))[
                    "status"
                ],
                "dry_run_passed",
            )

    def test_dry_run_writes_canon_dual_aspect_handoffs_reports_and_manifest(self):
        expected = {
            "edit_master_plan.json",
            "edit_construction_16x9.md",
            "edit_construction_16x9.csv",
            "edit_construction_9x16.md",
            "edit_construction_9x16.csv",
            "subtitles_16x9.srt",
            "subtitles_9x16.srt",
            "timeline_16x9.otio",
            "timeline_9x16.otio",
            "timeline_16x9.fcpxml",
            "timeline_9x16.fcpxml",
            "ffmpeg_commands.json",
            "adapter_reports.json",
            "ai_editor_plan.json",
            "bundle_manifest.json",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            created = build_edit_bundle(FIXTURE, Path(temp_dir) / "edit")
            present = {
                path.relative_to(created).as_posix()
                for path in created.rglob("*")
                if path.is_file()
            }
            canon = json.loads(
                (created / "edit_master_plan.json").read_text(encoding="utf-8")
            )
            commands = json.loads(
                (created / "ffmpeg_commands.json").read_text(encoding="utf-8")
            )
            reports = json.loads(
                (created / "adapter_reports.json").read_text(encoding="utf-8")
            )
            self.assertTrue(
                (created / "ai_editor_plan.json").is_file(),
                "AI target must emit an independent ai_editor_plan.json",
            )
            ai_plan = json.loads(
                (created / "ai_editor_plan.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(present, expected)
        self.assertEqual(canon, load_plan())
        self.assertEqual({item["timeline_id"] for item in commands["deliveries"]}, {"TL-16", "TL-9"})
        self.assertEqual(reports["ffmpeg"]["status"], "planned")
        self.assertEqual(reports["otio"]["status"], "generated")
        self.assertEqual(reports["fcpxml"]["status"], "generated")
        self.assertEqual(reports["ai_editor"]["artifact"], "ai_editor_plan.json")
        self.assertEqual(ai_plan["artifact_role"], "derived_ai_editor_handoff")
        self.assertEqual(ai_plan["source_canon_artifact"], "edit_master_plan.json")
        self.assertEqual(ai_plan["source_edit_plan_id"], canon["edit_plan_id"])
        self.assertTrue(ai_plan["read_only"])
        self.assertTrue(ai_plan["return_changes_to_canon"])
        for field in (
            "media_bindings",
            "timelines",
            "audio_tracks",
            "text_tracks",
            "look_plan",
            "delivery_specs",
        ):
            with self.subTest(ai_field=field):
                self.assertEqual(ai_plan[field], canon[field])
        self.assertEqual(
            ai_plan["execution"]["step_order"],
            ["probe", "bind", "timelines", "text", "audio", "look", "export", "validate"],
        )
        self.assertEqual(
            ai_plan["execution"]["authorization_refs"]["dry_run_manifest_id"],
            canon["execution"]["dry_run_manifest_id"],
        )
        self.assertEqual(ai_plan["export"]["delivery_specs"], canon["delivery_specs"])
        self.assertEqual(ai_plan["evidence_refs"]["edit"], ["VAL-D16", "VAL-D9"])
        self.assertEqual(ai_plan["evidence_refs"]["probe"], ["A01", "A02"])
        for evidence_kind in ("edit", "cinematic", "tool", "probe", "review"):
            self.assertIn(evidence_kind, ai_plan["evidence_refs"])
        self.assertEqual(manifest["status"], "dry_run_passed")
        self.assertEqual(set(manifest["artifacts"]), present - {"bundle_manifest.json"})

    def test_ai_editor_handoff_is_target_gated_and_stable(self):
        ai_plan_source = load_plan()
        no_ai_source = copy.deepcopy(ai_plan_source)
        no_ai_source["software_targets"] = [
            target
            for target in no_ai_source["software_targets"]
            if target["target"] != "ai_editor"
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            ai_source_path = write_plan(temp_dir, ai_plan_source, "ai-plan.json")
            no_ai_source_path = write_plan(temp_dir, no_ai_source, "no-ai-plan.json")
            first = build_edit_bundle(ai_source_path, Path(temp_dir) / "first")
            second = build_edit_bundle(ai_source_path, Path(temp_dir) / "second")
            without_ai = build_edit_bundle(
                no_ai_source_path, Path(temp_dir) / "without-ai"
            )
            self.assertTrue(
                (first / "ai_editor_plan.json").is_file(),
                "AI target must emit an independent ai_editor_plan.json",
            )
            first_payload = json.loads(
                (first / "ai_editor_plan.json").read_text(encoding="utf-8")
            )
            second_payload = json.loads(
                (second / "ai_editor_plan.json").read_text(encoding="utf-8")
            )
            no_ai_reports = json.loads(
                (without_ai / "adapter_reports.json").read_text(encoding="utf-8")
            )

        self.assertEqual(first_payload, second_payload)
        self.assertFalse((without_ai / "ai_editor_plan.json").exists())
        self.assertNotIn("ai_editor", no_ai_reports)
        self.assertEqual(first.name, "v001")
        self.assertEqual(second.name, "v001")
        self.assertEqual(without_ai.name, "v001")

    def test_cinematic_bundle_emits_quality_reports(self):
        audit_fields = (
            "content_consistency",
            "intent_fidelity",
            "character_identity_integrity",
            "action_reaction_coverage",
            "kinetic_profile_audit",
            "shot_scale_and_composition_variety",
            "transition_fulfillment",
            "audio_presence_and_structure",
            "static_hold_audit",
            "source_motion_review",
            "director_quality",
            "subtext_fidelity",
        )
        source_plan = load_plan(CINEMATIC_FIXTURE)
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "edit"
            previous = output_root / "v001"
            previous.mkdir(parents=True)
            sentinel = previous / "keep.txt"
            sentinel.write_text("previous", encoding="utf-8")

            with mock.patch(
                "build_edit_bundle.validate_edit_plan",
                wraps=validate_edit_plan,
            ) as validator:
                created = build_edit_bundle(CINEMATIC_FIXTURE, output_root)

            expected_reports = {
                "cinematic_quality_report.json",
                "cinematic_quality_report.md",
            }
            self.assertTrue(
                expected_reports.issubset({path.name for path in created.iterdir()})
            )
            report = json.loads(
                (created / "cinematic_quality_report.json").read_text(
                    encoding="utf-8"
                )
            )
            markdown = (created / "cinematic_quality_report.md").read_text(
                encoding="utf-8"
            )
            self.assertTrue((created / "ai_editor_plan.json").is_file())
            ai_plan = json.loads(
                (created / "ai_editor_plan.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )

            self.assertEqual(created, output_root.resolve() / "v002")
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "previous")
            self.assertFalse((previous / "cinematic_quality_report.json").exists())
            self.assertFalse((output_root / "cinematic_quality_report.json").exists())

        cinematic = source_plan["cinematic_validation"]
        self.assertEqual(
            set(report),
            {
                "edit_plan_id",
                "declared_mode",
                "genre",
                "cinematic_ready",
                "ppt_risk_flags",
                *audit_fields,
                "evidence_refs",
            },
        )
        self.assertEqual(report["edit_plan_id"], source_plan["edit_plan_id"])
        for field in (
            "declared_mode",
            "genre",
            "cinematic_ready",
            "ppt_risk_flags",
            *audit_fields,
            "evidence_refs",
        ):
            self.assertEqual(report[field], cinematic[field], field)
        self.assertIn("cinematic_quality_report.json", manifest["artifacts"])
        self.assertIn("cinematic_quality_report.md", manifest["artifacts"])
        self.assertEqual(
            ai_plan["evidence_refs"]["cinematic"],
            ["CONTACT-16", "CONTACT-9", "PROBE-AUDIO-01"],
        )
        self.assertIn("MIX-REVIEW-01", ai_plan["evidence_refs"]["review"])
        self.assertIn("Edit plan: EDIT\\-001", markdown)
        self.assertIn("cinematic", markdown)
        self.assertIn("Genre: action\\_spectacle", markdown)
        self.assertIn("false", markdown)
        self.assertIn("PPT risk flags", markdown)
        for field in audit_fields:
            self.assertIn(field, markdown)
            self.assertIn(cinematic[field]["status"], markdown)
        for evidence_ref in cinematic["evidence_refs"]:
            self.assertIn(evidence_ref.replace("-", "\\-"), markdown)
        self.assertTrue(markdown.endswith("\n"))
        self.assertTrue(
            validator.call_args_list[0].kwargs.get("require_cinematic", False)
        )

    def test_cinematic_ppt_plan_blocks_before_runner(self):
        runner_calls = []
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch(
            "build_edit_bundle.validate_edit_plan",
            wraps=validate_edit_plan,
        ) as validator:
            output_root = Path(temp_dir) / "edit"
            with self.assertRaisesRegex(
                BuildError, "PPT risk flags must be empty before ready"
            ):
                build_edit_bundle(
                    CINEMATIC_PPT_FIXTURE,
                    output_root,
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=lambda *args, **kwargs: runner_calls.append(args),
                )

            successful_versions = [
                path
                for path in output_root.glob("v*")
                if (path / "bundle_manifest.json").exists()
                and json.loads(
                    (path / "bundle_manifest.json").read_text(encoding="utf-8")
                ).get("status")
                == "dry_run_passed"
            ]

        self.assertEqual(runner_calls, [])
        self.assertEqual(successful_versions, [])
        self.assertTrue(
            validator.call_args_list[0].kwargs.get("require_cinematic", False)
        )

    def test_cinematic_execution_preflight_requires_cinematic_before_runner(self):
        runner_calls = []
        validation_calls = []

        def blocking_execution_validator(plan, **kwargs):
            validation_calls.append(kwargs)
            if kwargs.get("for_execution") is True:
                return ["synthetic execution preflight blocker"]
            return []

        with tempfile.TemporaryDirectory() as temp_dir:
            plan = authorize_plan(load_plan(CINEMATIC_FIXTURE))
            plan_path = write_plan(temp_dir, plan)
            output_root = Path(temp_dir) / "edit"
            with mock.patch(
                "build_edit_bundle.validate_edit_plan",
                side_effect=blocking_execution_validator,
            ), self.assertRaisesRegex(BuildError, "synthetic execution preflight blocker"):
                build_edit_bundle(
                    plan_path,
                    output_root,
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=lambda *args, **kwargs: runner_calls.append(args),
                )
            self.assertFalse(output_root.exists())

        self.assertEqual(runner_calls, [])
        self.assertEqual(len(validation_calls), 2)
        self.assertTrue(validation_calls[0].get("require_cinematic", False))
        self.assertTrue(validation_calls[1].get("require_cinematic", False))
        self.assertTrue(validation_calls[1]["for_execution"])

    def test_cinematic_missing_audit_block_fails_before_runner_or_version(self):
        plan = load_plan(CINEMATIC_FIXTURE)
        del plan["cinematic_validation"]["source_motion_review"]
        runner_calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            plan_path = write_plan(temp_dir, plan)
            output_root = Path(temp_dir) / "edit"
            with self.assertRaisesRegex(
                BuildError, "missing field source_motion_review"
            ):
                build_edit_bundle(
                    plan_path,
                    output_root,
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=lambda *args, **kwargs: runner_calls.append(args),
                )
            self.assertFalse(output_root.exists())

        self.assertEqual(runner_calls, [])

    def test_cinematic_report_payload_rejects_non_object_validation(self):
        for value in (None, [], "cinematic"):
            with self.subTest(value=value), self.assertRaisesRegex(
                ValueError, "cinematic_validation is required"
            ):
                cinematic_report_payload({"cinematic_validation": value})

        payload = cinematic_report_payload(load_plan(CINEMATIC_FIXTURE))
        payload["cinematic_ready"] = False
        payload["ppt_risk_flags"] = ["poster_pose"]
        markdown = cinematic_report_markdown(payload)
        self.assertIn("PPT risk flags: 1", markdown)
        self.assertIn("poster\\_pose", markdown)

    def test_cinematic_bundle_escapes_untrusted_markdown_values(self):
        malicious = (
            "trace` *bold* [link](javascript:alert(1))\r\n"
            "- Cinematic ready: false\r\n"
            "## Forged section\r\n"
            "<script>&"
        )
        plan = load_plan(CINEMATIC_FIXTURE)
        plan["cinematic_validation"]["genre"] = malicious
        plan["cinematic_validation"]["evidence_refs"] = [malicious]

        with tempfile.TemporaryDirectory() as temp_dir:
            plan_path = write_plan(temp_dir, plan)
            created = build_edit_bundle(plan_path, Path(temp_dir) / "edit")
            report = json.loads(
                (created / "cinematic_quality_report.json").read_text(
                    encoding="utf-8"
                )
            )
            markdown = (created / "cinematic_quality_report.md").read_text(
                encoding="utf-8"
            )

        self.assertEqual(report["genre"], malicious)
        self.assertEqual(report["evidence_refs"], [malicious])
        self.assertEqual(
            [line for line in markdown.splitlines() if line.startswith("#")],
            [
                "# Cinematic Quality Report",
                "## Audit statuses",
                "## Top-level evidence",
            ],
        )
        self.assertEqual(
            [
                line
                for line in markdown.splitlines()
                if line.startswith("- Cinematic ready:")
            ],
            ["- Cinematic ready: false"],
        )
        self.assertEqual(markdown.count("\n- Cinematic ready: false"), 1)
        self.assertNotIn("\n## Forged section", markdown)
        self.assertNotIn("<script>", markdown)
        self.assertIn("trace\\` \\*bold\\*", markdown)
        self.assertIn("\\[link\\]\\(javascript:alert\\(1\\)\\)", markdown)
        self.assertIn("\\r\\n\\- Cinematic ready: false", markdown)
        self.assertIn("\\r\\n\\#\\# Forged section", markdown)
        self.assertIn("&lt;script&gt;&amp;", markdown)

    def test_cinematic_markdown_escapes_every_dynamic_report_field(self):
        malicious = "DYNAMIC`\r\n## Forged section<script>&"
        payload = cinematic_report_payload(load_plan(CINEMATIC_FIXTURE))
        payload["edit_plan_id"] = malicious
        payload["declared_mode"] = malicious
        payload["genre"] = malicious
        payload["ppt_risk_flags"] = [malicious]
        payload["evidence_refs"] = [malicious]
        for field in (
            "content_consistency",
            "intent_fidelity",
            "character_identity_integrity",
            "action_reaction_coverage",
            "kinetic_profile_audit",
            "shot_scale_and_composition_variety",
            "transition_fulfillment",
            "audio_presence_and_structure",
            "static_hold_audit",
            "source_motion_review",
            "director_quality",
            "subtext_fidelity",
        ):
            payload[field]["status"] = malicious

        markdown = cinematic_report_markdown(payload)

        self.assertEqual(markdown.count("DYNAMIC\\`"), 17)
        self.assertNotIn("\n## Forged section", markdown)
        self.assertNotIn("<script>", markdown)
        self.assertEqual(markdown.count("\\r\\n\\#\\# Forged section"), 17)
        self.assertEqual(markdown.count("&lt;script&gt;&amp;"), 17)
        self.assertTrue(markdown.endswith("\n"))

    def test_cinematic_report_writer_failure_preserves_version_recovery(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "edit"
            previous = output_root / "v001"
            previous.mkdir(parents=True)
            sentinel = previous / "keep.txt"
            sentinel.write_text("previous", encoding="utf-8")

            with mock.patch(
                "build_edit_bundle.cinematic_report_markdown",
                side_effect=OSError("synthetic cinematic report failure"),
            ), self.assertRaisesRegex(BuildError, "synthetic cinematic report failure"):
                build_edit_bundle(CINEMATIC_FIXTURE, output_root)

            failed = output_root / "v002"
            failed_manifest = json.loads(
                (failed / "bundle_manifest.json").read_text(encoding="utf-8")
            )
            retry = build_edit_bundle(CINEMATIC_FIXTURE, output_root)
            retry_has_report = (
                retry / "cinematic_quality_report.json"
            ).is_file()

            self.assertEqual(sentinel.read_text(encoding="utf-8"), "previous")
            self.assertFalse((previous / "cinematic_quality_report.json").exists())
            self.assertFalse((output_root / "cinematic_quality_report.json").exists())

        self.assertEqual(failed_manifest["status"], "blocked")
        self.assertIn(
            "synthetic cinematic report failure",
            failed_manifest["error"]["message"],
        )
        self.assertEqual(retry.name, "v003")
        self.assertTrue(retry_has_report)

    def test_jianying_target_gets_manual_instructions_and_no_private_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            created = build_edit_bundle(JIANYING_FIXTURE, Path(temp_dir) / "edit")
            instruction = created / "jianying_capcut_instructions.md"
            instruction_text = instruction.read_text(encoding="utf-8")
            json_names = [path.name for path in created.rglob("*.json")]
            reports = json.loads(
                (created / "adapter_reports.json").read_text(encoding="utf-8")
            )

        self.assertIn("manual_or_unverified", instruction_text)
        self.assertEqual(
            reports["jianying_capcut"]["status"], "manual_or_unverified"
        )
        self.assertFalse(
            any("jianying" in name.lower() or "capcut" in name.lower() for name in json_names)
        )

    def test_execute_without_authorization_stops_before_runner(self):
        calls = []

        def runner(*args, **kwargs):
            calls.append((args, kwargs))
            raise AssertionError("runner must not be called")

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(BuildError):
                build_edit_bundle(
                    FIXTURE,
                    Path(temp_dir) / "edit",
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=runner,
                )
        self.assertEqual(calls, [])

    def test_execute_without_ffmpeg_raises_exact_blocker_before_rendering(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            plan_path = write_plan(temp_dir, authorized_plan())
            output_root = Path(temp_dir) / "edit"

            with self.assertRaisesRegex(BuildError, "^ffmpeg is unavailable$"):
                build_edit_bundle(
                    plan_path, output_root, execute=True, ffmpeg_path=None
                )

            self.assertEqual(list(output_root.rglob("*.mp4")), [])

    def test_mock_execution_records_success_and_preserves_blocked_logs(self):
        def successful_runner(args, **kwargs):
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "ok", "")

        def failed_runner(args, **kwargs):
            return subprocess.CompletedProcess(args, 9, "", "synthetic failure")

        with tempfile.TemporaryDirectory() as temp_dir:
            success_plan, success_plan_path = write_authorized_plan(
                temp_dir,
                name="success-plan.json",
                version_directory="success/v001",
            )
            success_dir = build_edit_bundle(
                success_plan_path,
                Path(temp_dir) / "success",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=successful_runner,
            )
            success_log = json.loads(
                (success_dir / "execution_log.json").read_text(encoding="utf-8")
            )
            success_manifest = json.loads(
                (success_dir / "bundle_manifest.json").read_text(encoding="utf-8")
            )

            blocked_plan, blocked_plan_path = write_authorized_plan(
                temp_dir,
                name="blocked-plan.json",
                version_directory="blocked/v001",
            )
            blocked_dir = build_edit_bundle(
                blocked_plan_path,
                Path(temp_dir) / "blocked",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=failed_runner,
            )
            blocked_log = json.loads(
                (blocked_dir / "execution_log.json").read_text(encoding="utf-8")
            )
            blocked_manifest = json.loads(
                (blocked_dir / "bundle_manifest.json").read_text(encoding="utf-8")
            )
            blocked_canon_preserved = (blocked_dir / "edit_master_plan.json").is_file()

        self.assertEqual(success_manifest["status"], "rendered")
        self.assertTrue(success_log["commands"])
        self.assertEqual(len(success_log["rendered_outputs"]), 2)
        self.assertTrue(all(item["status"] == "rendered" for item in success_log["rendered_outputs"]))
        self.assertEqual(blocked_manifest["status"], "blocked")
        self.assertEqual(blocked_log["status"], "blocked")
        self.assertEqual(blocked_log["commands"][0]["returncode"], 9)
        self.assertEqual(blocked_log["commands"][0]["stderr"], "synthetic failure")
        self.assertTrue(blocked_canon_preserved)

    def test_execute_validates_preflights_materializes_and_updates_only_copy(self):
        calls = []

        def successful_runner(args, **kwargs):
            self.assertIsInstance(args, list)
            self.assertNotIn("shell", kwargs)
            self.assertEqual(
                set(kwargs), {"cwd", "capture_output", "text", "check"}
            )
            self.assertTrue(kwargs["capture_output"])
            self.assertTrue(kwargs["text"])
            self.assertFalse(kwargs["check"])
            version_dir = Path(kwargs["cwd"]).resolve()
            output = Path(args[-1]).resolve()
            output.relative_to(version_dir)
            if "concat" in args:
                concat_path = Path(args[args.index("-i") + 1])
                self.assertTrue(concat_path.is_file())
                self.assertIn("file '", concat_path.read_text(encoding="utf-8"))
            elif "-i" in args:
                media_input = Path(args[args.index("-i") + 1])
                self.assertTrue(media_input.is_absolute())
                self.assertTrue(media_input.is_file())
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            calls.append((args, kwargs))
            return subprocess.CompletedProcess(args, 0, "ok", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            plan, plan_path = write_authorized_plan(temp_dir)
            source_before = plan_path.read_text(encoding="utf-8")
            with mock.patch(
                "build_edit_bundle.validate_edit_plan",
                wraps=validate_edit_plan,
            ) as validator:
                created = build_edit_bundle(
                    plan_path,
                    Path(temp_dir) / "edit",
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=successful_runner,
                )

            copied = json.loads(
                (created / "edit_master_plan.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

            self.assertEqual(plan_path.read_text(encoding="utf-8"), source_before)
            self.assertEqual(copied["plan_status"], "rendered")
            self.assertEqual(validate_edit_plan(copied), [])
            self.assertTrue(
                all(item["status"] == "rendered" for item in copied["delivery_specs"])
            )
            self.assertTrue(copied["execution"]["executed_commands"])
            self.assertEqual(manifest["status"], "rendered")
            self.assertEqual(
                manifest["rendered_outputs"], log["rendered_outputs"]
            )
            self.assertEqual(log["status"], "rendered")
            self.assertTrue(
                all(item["probe_status"] == "unverified" for item in log["rendered_outputs"])
            )
            for output in log["rendered_outputs"]:
                (created / Path(output["output_ref"]).name).resolve().relative_to(
                    created.resolve()
                )
                self.assertTrue((created / Path(output["output_ref"]).name).is_file())
                self.assertTrue(
                    (created / Path(output["output_ref"]).with_suffix(".srt").name).is_file()
                )

        self.assertTrue(calls)
        execution_calls = [
            call
            for call in validator.call_args_list
            if call.kwargs.get("for_execution") is True
        ]
        self.assertEqual(len(execution_calls), 1)

    def test_execute_blocks_claimed_destination_that_does_not_match_real_output(self):
        calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = authorized_plan()
            plan["delivery_specs"][0]["destination"] = (
                "edit/v001/CLAIMED-D16.mp4"
            )
            materialize_plan_media(temp_dir, plan)
            plan_path = write_plan(temp_dir, plan)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=lambda *args, **kwargs: calls.append(args),
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(calls, [])
        self.assertEqual(log["status"], "blocked")
        self.assertIn("destination and filename", log["blocker"])
        self.assertEqual(log["rendered_outputs"], [])
        self.assertEqual(manifest["rendered_outputs"], [])

    def test_execute_with_no_ready_delivery_is_blocked_without_commands(self):
        calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = authorized_plan()
            for delivery in plan["delivery_specs"]:
                delivery["ready"] = False
            materialize_plan_media(temp_dir, plan)
            plan_path = write_plan(temp_dir, plan)
            source_before = plan_path.read_text(encoding="utf-8")
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=lambda *args, **kwargs: calls.append(args),
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )
            copied = json.loads(
                (created / "edit_master_plan.json").read_text(encoding="utf-8")
            )
            source_after = plan_path.read_text(encoding="utf-8")

        self.assertEqual(calls, [])
        self.assertEqual(log["status"], "blocked")
        self.assertIn("no ready delivery", log["blocker"])
        self.assertEqual(log["rendered_outputs"], [])
        self.assertEqual(manifest["status"], "blocked")
        self.assertEqual(copied["plan_status"], "blocked")
        self.assertTrue(
            all(item["status"] == "authorized" for item in copied["delivery_specs"])
        )
        self.assertEqual(source_after, source_before)

    def test_execute_requires_verified_matching_ffmpeg_tool_evidence(self):
        cases = (
            ([], "verified ffmpeg tool evidence"),
            (
                [
                    {
                        "tool_evidence_id": "AUTH-OTHER",
                        "tool": "totally-not-an-editor",
                        "path": "ffmpeg-test",
                        "status": "verified",
                    }
                ],
                "tool must be ffmpeg",
            ),
        )
        for evidence, expected in cases:
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as temp_dir:
                plan = authorized_plan()
                plan["execution"]["tool_evidence"] = evidence
                materialize_plan_media(temp_dir, plan)
                plan_path = write_plan(temp_dir, plan)
                calls = []
                created = build_edit_bundle(
                    plan_path,
                    Path(temp_dir) / "edit",
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=lambda args, **kwargs: (
                        calls.append(args)
                        or subprocess.CompletedProcess(args, 9, "", "must not run")
                    ),
                )
                log = json.loads(
                    (created / "execution_log.json").read_text(encoding="utf-8")
                )

            self.assertEqual(calls, [])
            self.assertEqual(log["status"], "blocked")
            self.assertIn(expected, log["blocker"])

    def test_final_execution_requires_matching_verified_ffprobe_evidence(self):
        calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = rich_tier_plan("final_master")
            plan, plan_path = write_authorized_plan(temp_dir, plan)
            plan["execution"]["tool_evidence"] = [
                {
                    "tool_evidence_id": "AUTH-FFMPEG",
                    "tool": "ffmpeg",
                    "path": "ffmpeg-test",
                    "status": "verified",
                }
            ]
            plan_path = write_plan(temp_dir, plan, "final-no-probe-evidence.json")
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=lambda args, **kwargs: (
                    calls.append(args)
                    or subprocess.CompletedProcess(args, 9, "", "must not run")
                ),
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(calls, [])
        self.assertEqual(log["status"], "blocked")
        self.assertIn("verified ffprobe tool evidence", log["blocker"])

    def test_ffprobe_evidence_rejects_wrong_tool_identity_even_when_path_matches(self):
        calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            plan = rich_tier_plan("final_master")
            plan, plan_path = write_authorized_plan(temp_dir, plan)
            probe_evidence = next(
                item
                for item in plan["execution"]["tool_evidence"]
                if item["tool"] == "ffprobe"
            )
            probe_evidence["tool"] = "totally-not-a-probe"
            plan_path = write_plan(temp_dir, plan, "wrong-probe-tool.json")
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=lambda args, **kwargs: (
                    calls.append(args)
                    or subprocess.CompletedProcess(args, 9, "", "must not run")
                ),
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(calls, [])
        self.assertEqual(log["status"], "blocked")
        self.assertIn("tool must be ffprobe", log["blocker"])

    def test_tool_only_ffmpeg_evidence_rejects_absolute_and_relative_paths(self):
        for requested in (r"C:\tools\ffmpeg.exe", r".\bin\ffmpeg.exe"):
            with self.subTest(requested=requested), tempfile.TemporaryDirectory() as temp_dir:
                plan = authorized_plan()
                plan["execution"]["tool_evidence"] = [
                    {
                        "tool_evidence_id": "AUTH-FFMPEG",
                        "tool": "ffmpeg",
                        "status": "verified",
                    }
                ]
                materialize_plan_media(temp_dir, plan)
                plan_path = write_plan(temp_dir, plan)
                calls = []
                created = build_edit_bundle(
                    plan_path,
                    Path(temp_dir) / "edit",
                    execute=True,
                    ffmpeg_path=requested,
                    runner=lambda args, **kwargs: (
                        calls.append(args)
                        or subprocess.CompletedProcess(args, 9, "", "must not run")
                    ),
                )
                log = json.loads(
                    (created / "execution_log.json").read_text(encoding="utf-8")
                )

            self.assertEqual(calls, [])
            self.assertEqual(log["status"], "blocked")
            self.assertIn("must bind path/executable", log["blocker"])

    def test_tool_only_ffprobe_evidence_rejects_absolute_and_relative_paths(self):
        for requested in (r"C:\tools\ffprobe.exe", r".\bin\ffprobe.exe"):
            with self.subTest(requested=requested), tempfile.TemporaryDirectory() as temp_dir:
                plan = rich_tier_plan("final_master")
                plan, _plan_path = write_authorized_plan(temp_dir, plan)
                plan["execution"]["tool_evidence"] = [
                    {
                        "tool_evidence_id": "AUTH-FFMPEG",
                        "tool": "ffmpeg",
                        "path": "ffmpeg-test",
                        "status": "verified",
                    },
                    {
                        "tool_evidence_id": "AUTH-FFPROBE",
                        "tool": "ffprobe",
                        "status": "verified",
                    },
                ]
                plan_path = write_plan(temp_dir, plan, "probe-path.json")
                calls = []
                created = build_edit_bundle(
                    plan_path,
                    Path(temp_dir) / "edit",
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    ffprobe_path=requested,
                    runner=lambda args, **kwargs: (
                        calls.append(args)
                        or subprocess.CompletedProcess(args, 9, "", "must not run")
                    ),
                )
                log = json.loads(
                    (created / "execution_log.json").read_text(encoding="utf-8")
                )

            self.assertEqual(calls, [])
            self.assertEqual(log["status"], "blocked")
            self.assertIn("must bind path/executable", log["blocker"])

    def test_tool_only_evidence_accepts_bare_case_insensitive_commands(self):
        def runner(args, **kwargs):
            if args[0].casefold() == "ffprobe.exe":
                filename = Path(args[-1]).name
                width, height = (
                    (1920, 1080) if "16x9" in filename else (1080, 1920)
                )
                payload = {
                    "streams": [
                        {
                            "codec_type": "video",
                            "codec_name": "h264",
                            "width": width,
                            "height": height,
                            "avg_frame_rate": "24/1",
                        },
                        {
                            "codec_type": "audio",
                            "codec_name": "aac",
                            "sample_rate": "48000",
                            "channels": 2,
                        },
                    ],
                    "format": {"duration": "4.0"},
                }
                return subprocess.CompletedProcess(args, 0, json.dumps(payload), "")
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            plan = rich_tier_plan("final_master")
            plan, _plan_path = write_authorized_plan(temp_dir, plan)
            plan["execution"]["tool_evidence"] = [
                {
                    "tool_evidence_id": "AUTH-FFMPEG",
                    "tool": "FFMPEG",
                    "status": "verified",
                },
                {
                    "tool_evidence_id": "AUTH-FFPROBE",
                    "tool": "FFPROBE",
                    "status": "verified",
                },
            ]
            plan_path = write_plan(temp_dir, plan, "bare-tools.json")
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="FFMPEG.EXE",
                ffprobe_path="FFPROBE.EXE",
                runner=runner,
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )

        self.assertEqual(manifest["status"], "rendered")

    def test_execution_validation_happens_before_the_first_runner_command(self):
        event_order = []

        def observing_validator(*args, **kwargs):
            if kwargs.get("for_execution") is True:
                event_order.append("validated_for_execution")
            return validate_edit_plan(*args, **kwargs)

        def successful_runner(args, **kwargs):
            event_order.append("runner")
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch(
            "build_edit_bundle.validate_edit_plan",
            side_effect=observing_validator,
        ):
            _plan, plan_path = write_authorized_plan(temp_dir)
            build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=successful_runner,
            )

        self.assertEqual(event_order[0], "validated_for_execution")

    def test_authorization_is_bound_to_the_actual_new_version_directory(self):
        runner_calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            _plan, plan_path = write_authorized_plan(temp_dir)
            output_root = Path(temp_dir) / "edit"
            (output_root / "v001").mkdir(parents=True)

            with self.assertRaisesRegex(
                BuildError, "authorized version directory does not match"
            ):
                build_edit_bundle(
                    plan_path,
                    output_root,
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=lambda *args, **kwargs: runner_calls.append(args),
                )

            blocked = json.loads(
                (output_root / "v002" / "bundle_manifest.json").read_text(
                    encoding="utf-8"
                )
            )

        self.assertEqual(runner_calls, [])
        self.assertEqual(blocked["status"], "blocked")

    def test_missing_local_media_and_provider_uri_block_before_runner(self):
        cases = []
        missing = authorized_plan()
        cases.append(("missing", missing, "regular file"))
        provider = authorized_plan()
        provider["media_bindings"][0]["source_type"] = "provider_result"
        provider["media_bindings"][0]["path_or_uri"] = "provider://job/A01"
        cases.append(("provider", provider, "must be rebound"))

        for name, plan, expected in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp_dir:
                if name == "provider":
                    materialize_plan_media(temp_dir, plan)
                plan_path = write_plan(temp_dir, plan)
                calls = []
                with self.assertRaisesRegex(BuildError, expected):
                    build_edit_bundle(
                        plan_path,
                        Path(temp_dir) / "edit",
                        execute=True,
                        ffmpeg_path="ffmpeg-test",
                        runner=lambda *args, **kwargs: calls.append(args),
                    )
                self.assertEqual(calls, [])

    def test_runner_failure_stops_and_preserves_intermediates_and_diagnostics(self):
        calls = []

        def failing_second_runner(args, **kwargs):
            calls.append(args)
            if len(calls) == 1:
                output = Path(args[-1])
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"first segment")
                return subprocess.CompletedProcess(args, 0, "first ok", "")
            return subprocess.CompletedProcess(args, 7, "partial", "decode failed")

        with tempfile.TemporaryDirectory() as temp_dir:
            _plan, plan_path = write_authorized_plan(temp_dir)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=failing_second_runner,
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )

            self.assertEqual(len(calls), 2)
            self.assertEqual(log["status"], "blocked")
            self.assertEqual(log["commands"][-1]["stdout"], "partial")
            self.assertEqual(log["commands"][-1]["stderr"], "decode failed")
            self.assertTrue((created / "segments/0001_E16-01.mp4").is_file())
            self.assertTrue((created / "edit_construction_16x9.md").is_file())
            self.assertEqual(manifest["status"], "blocked")

    def test_runner_exception_becomes_first_error_execution_record(self):
        calls = []

        def exploding_runner(args, **kwargs):
            calls.append(args)
            raise RuntimeError("synthetic runner explosion")

        with tempfile.TemporaryDirectory() as temp_dir:
            _plan, plan_path = write_authorized_plan(temp_dir)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=exploding_runner,
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(log["status"], "blocked")
        self.assertEqual(log["commands"][0]["command"], calls[0])
        self.assertEqual(log["commands"][0]["error"], "synthetic runner explosion")
        self.assertEqual(log["commands"][0]["stdout"], "")
        self.assertEqual(log["commands"][0]["stderr"], "synthetic runner explosion")

    def test_malformed_ffprobe_shapes_are_blocked_with_execution_log(self):
        malformed_payloads = (
            {"streams": [None], "format": {"duration": "4.0"}},
            {
                "streams": [
                    {
                        "codec_type": "video",
                        "codec_name": "h264",
                        "width": 1920,
                        "height": 1080,
                        "avg_frame_rate": "24/1",
                    }
                ],
                "format": [],
            },
        )
        for index, malformed in enumerate(malformed_payloads):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as temp_dir:
                plan = rich_tier_plan("final_master")
                plan, plan_path = write_authorized_plan(temp_dir, plan)

                def runner(args, **kwargs):
                    if args[0] == "ffprobe-test":
                        return subprocess.CompletedProcess(
                            args, 0, json.dumps(malformed), ""
                        )
                    output = Path(args[-1])
                    output.parent.mkdir(parents=True, exist_ok=True)
                    output.write_bytes(b"rendered")
                    return subprocess.CompletedProcess(args, 0, "", "")

                created = build_edit_bundle(
                    plan_path,
                    Path(temp_dir) / "edit",
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    ffprobe_path="ffprobe-test",
                    runner=runner,
                )
                log = json.loads(
                    (created / "execution_log.json").read_text(encoding="utf-8")
                )

            self.assertEqual(log["status"], "blocked")
            self.assertIn("invalid", log["blocker"])

    def test_publish_failure_recovers_to_blocked_plan_log_and_manifest(self):
        real_replace = os.replace
        injected = []

        def flaky_replace(source, destination):
            if Path(destination).name == "execution_log.json" and not injected:
                injected.append(Path(destination))
                raise OSError("synthetic atomic log publish failure")
            return real_replace(source, destination)

        def successful_runner(args, **kwargs):
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch(
            "build_edit_bundle.os.replace", side_effect=flaky_replace
        ):
            _plan, plan_path = write_authorized_plan(temp_dir)
            source_before = plan_path.read_text(encoding="utf-8")
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=successful_runner,
            )
            copied = json.loads(
                (created / "edit_master_plan.json").read_text(encoding="utf-8")
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )
            source_after = plan_path.read_text(encoding="utf-8")

        self.assertEqual(len(injected), 1)
        self.assertEqual(source_after, source_before)
        self.assertEqual(copied["plan_status"], "blocked")
        self.assertEqual(log["status"], "blocked")
        self.assertIn("synthetic atomic log publish failure", log["publish_error"])
        self.assertEqual(manifest["status"], "blocked")
        self.assertIn("synthetic atomic log publish failure", manifest["publish_error"])

    def test_persistent_final_manifest_failure_raises_and_preserves_evidence(self):
        real_replace = os.replace
        manifest_replaces = []

        def persistent_manifest_failure(source, destination):
            if Path(destination).name == "bundle_manifest.json":
                manifest_replaces.append(Path(destination))
                if len(manifest_replaces) > 1:
                    raise OSError("synthetic persistent manifest publish failure")
            return real_replace(source, destination)

        def successful_runner(args, **kwargs):
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch(
            "build_edit_bundle.os.replace",
            side_effect=persistent_manifest_failure,
        ):
            _plan, plan_path = write_authorized_plan(temp_dir)
            source_before = plan_path.read_text(encoding="utf-8")
            output_root = Path(temp_dir) / "edit"
            with self.assertRaisesRegex(
                BuildError, "synthetic persistent manifest publish failure"
            ):
                build_edit_bundle(
                    plan_path,
                    output_root,
                    execute=True,
                    ffmpeg_path="ffmpeg-test",
                    runner=successful_runner,
                )
            version_dir = output_root / "v001"
            manifest = json.loads(
                (version_dir / "bundle_manifest.json").read_text(encoding="utf-8")
            )
            copied = json.loads(
                (version_dir / "edit_master_plan.json").read_text(encoding="utf-8")
            )
            log = json.loads(
                (version_dir / "execution_log.json").read_text(encoding="utf-8")
            )
            source_after = plan_path.read_text(encoding="utf-8")

        self.assertGreaterEqual(len(manifest_replaces), 3)
        self.assertEqual(source_after, source_before)
        self.assertEqual(manifest["status"], "publishing")
        self.assertEqual(copied["plan_status"], "blocked")
        self.assertEqual(log["status"], "blocked")
        self.assertIn("synthetic persistent manifest publish failure", log["publish_error"])

    def test_cli_persistent_manifest_failure_is_not_success(self):
        real_replace = os.replace
        manifest_replaces = []

        def persistent_manifest_failure(source, destination):
            if Path(destination).name == "bundle_manifest.json":
                manifest_replaces.append(Path(destination))
                if len(manifest_replaces) > 1:
                    raise OSError("synthetic persistent CLI manifest failure")
            return real_replace(source, destination)

        def successful_runner(args, **kwargs):
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "", "")

        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir:
            _plan, plan_path = write_authorized_plan(temp_dir)
            with mock.patch.dict(
                build_edit_bundle.__kwdefaults__, {"runner": successful_runner}
            ), mock.patch(
                "build_edit_bundle.os.replace",
                side_effect=persistent_manifest_failure,
            ), redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = main(
                    [
                        str(plan_path),
                        "--out",
                        str(Path(temp_dir) / "edit"),
                        "--execute",
                        "--ffmpeg",
                        "ffmpeg-test",
                    ]
                )

        self.assertEqual(exit_code, 1)
        self.assertGreaterEqual(len(manifest_replaces), 3)
        self.assertIn("synthetic persistent CLI manifest failure", stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")

    def test_output_link_to_external_file_is_blocked_after_runner_success(self):
        calls = []

        def linked_output_runner(args, **kwargs):
            calls.append(args)
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            os.link(external, output)
            return subprocess.CompletedProcess(args, 0, "claimed success", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            external = Path(temp_dir) / "outside.mp4"
            external.write_bytes(b"outside")
            _plan, plan_path = write_authorized_plan(temp_dir)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=linked_output_runner,
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(log["status"], "blocked")
        self.assertIn("link", log["blocker"])
        self.assertEqual(log["rendered_outputs"], [])

    def test_input_identity_change_after_first_command_blocks_before_next_spawn(self):
        calls = []

        def replacing_runner(args, **kwargs):
            calls.append(args)
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            if len(calls) == 1:
                source = Path(args[args.index("-i") + 1])
                source.unlink()
                source.write_bytes(b"replacement input with a new identity")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            _plan, plan_path = write_authorized_plan(temp_dir)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                runner=replacing_runner,
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(len(calls), 1)
        self.assertEqual(log["status"], "blocked")
        self.assertIn("input identity changed", log["blocker"])
        self.assertEqual(log["commands"][-1]["returncode"], None)

    def test_final_master_requires_and_validates_ffprobe_json(self):
        probe_calls = []

        def runner(args, **kwargs):
            if args[0] == "ffprobe-test":
                probe_calls.append(args)
                filename = Path(args[-1]).name
                width, height = (
                    (1920, 1080) if "16x9" in filename else (1080, 1920)
                )
                payload = {
                    "streams": [
                        {
                            "codec_type": "video",
                            "codec_name": "h264",
                            "width": width,
                            "height": height,
                            "avg_frame_rate": "24/1",
                        },
                        {
                            "codec_type": "audio",
                            "codec_name": "aac",
                            "sample_rate": "48000",
                            "channels": 2,
                        },
                    ],
                    "format": {"duration": "4.0"},
                }
                return subprocess.CompletedProcess(
                    args, 0, json.dumps(payload), ""
                )
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            final = rich_tier_plan("final_master")
            final, plan_path = write_authorized_plan(temp_dir, final)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=runner,
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )
            copied = json.loads(
                (created / "edit_master_plan.json").read_text(encoding="utf-8")
            )

        self.assertEqual(len(probe_calls), 2)
        self.assertEqual(log["status"], "rendered")
        self.assertTrue(
            all(item["probe_status"] == "passed" for item in log["rendered_outputs"])
        )
        self.assertIn(
            "ffprobe",
            {item["tool"] for item in copied["execution"]["tool_evidence"]},
        )
        self.assertIn(
            "ffprobe-test",
            {
                item.get("path")
                for item in copied["execution"]["tool_evidence"]
            },
        )

    def test_rough_temporary_or_silent_probe_allows_video_only_output(self):
        def runner(args, **kwargs):
            if args[0] == "ffprobe-test":
                filename = Path(args[-1]).name
                width, height = (
                    (1920, 1080) if "16x9" in filename else (1080, 1920)
                )
                payload = {
                    "streams": [
                        {
                            "codec_type": "video",
                            "codec_name": "h264",
                            "width": width,
                            "height": height,
                            "avg_frame_rate": "24/1",
                        }
                    ],
                    "format": {"duration": "4.0"},
                }
                return subprocess.CompletedProcess(args, 0, json.dumps(payload), "")
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"video only")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            _plan, plan_path = write_authorized_plan(temp_dir)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=runner,
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(log["status"], "rendered")
        self.assertTrue(
            all(item["probe_status"] == "passed" for item in log["rendered_outputs"])
        )

    def test_final_probe_without_audio_stream_is_blocked(self):
        def runner(args, **kwargs):
            if args[0] == "ffprobe-test":
                filename = Path(args[-1]).name
                width, height = (
                    (1920, 1080) if "16x9" in filename else (1080, 1920)
                )
                payload = {
                    "streams": [
                        {
                            "codec_type": "video",
                            "codec_name": "h264",
                            "width": width,
                            "height": height,
                            "avg_frame_rate": "24/1",
                        }
                    ],
                    "format": {"duration": "4.0"},
                }
                return subprocess.CompletedProcess(args, 0, json.dumps(payload), "")
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"missing final audio")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            final, plan_path = write_authorized_plan(
                temp_dir, rich_tier_plan("final_master")
            )
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=runner,
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(log["status"], "blocked")
        self.assertIn("missing an audio stream", log["blocker"])

    def test_bad_final_probe_and_missing_fine_probe_are_blocked(self):
        def bad_probe_runner(args, **kwargs):
            if args[0] == "ffprobe-test":
                payload = {
                    "streams": [
                        {
                            "codec_type": "video",
                            "codec_name": "h264",
                            "width": 640,
                            "height": 360,
                            "avg_frame_rate": "24/1",
                        },
                        {
                            "codec_type": "audio",
                            "codec_name": "aac",
                            "sample_rate": "48000",
                            "channels": 2,
                        },
                    ],
                    "format": {"duration": "4.0"},
                }
                return subprocess.CompletedProcess(args, 0, json.dumps(payload), "")
            output = Path(args[-1])
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_bytes(b"rendered")
            return subprocess.CompletedProcess(args, 0, "", "")

        with tempfile.TemporaryDirectory() as temp_dir:
            final, final_path = write_authorized_plan(
                temp_dir,
                rich_tier_plan("final_master"),
                "final.json",
                "final-edit/v001",
            )
            final_dir = build_edit_bundle(
                final_path,
                Path(temp_dir) / "final-edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=bad_probe_runner,
            )
            final_log = json.loads(
                (final_dir / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(final_log["status"], "blocked")
        self.assertIn("resolution", final_log["blocker"])

        with tempfile.TemporaryDirectory() as temp_dir:
            fine, fine_path = write_authorized_plan(
                temp_dir, rich_tier_plan("fine_cut"), "fine.json"
            )
            fine_dir = build_edit_bundle(
                fine_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path=None,
                runner=lambda *args, **kwargs: self.fail(
                    "fine cut must block before FFmpeg without ffprobe"
                ),
            )
            fine_log = json.loads(
                (fine_dir / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(fine_log["status"], "blocked")
        self.assertIn("ffprobe is required", fine_log["blocker"])

    def test_fine_cut_rejects_placeholders_and_unready_deliveries_are_not_run(self):
        fine = rich_tier_plan("fine_cut")
        fine["media_bindings"][0]["source_type"] = "generated_placeholder"
        fine["media_bindings"][0]["file_status"] = "placeholder"
        fine["delivery_specs"][1]["ready"] = False
        calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            fine, plan_path = write_authorized_plan(temp_dir, fine)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=lambda *args, **kwargs: calls.append(args),
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )

        self.assertEqual(calls, [])
        self.assertEqual(log["status"], "blocked")
        self.assertIn("placeholder", log["blocker"])

    def test_unsupported_transition_blocks_without_degraded_render_and_keeps_handoffs(self):
        plan = rich_tier_plan("fine_cut")
        plan["timelines"][0]["video_tracks"][0]["edit_units"][0][
            "transition_out"
        ] = "cross_dissolve"
        calls = []
        with tempfile.TemporaryDirectory() as temp_dir:
            plan, plan_path = write_authorized_plan(temp_dir, plan)
            created = build_edit_bundle(
                plan_path,
                Path(temp_dir) / "edit",
                execute=True,
                ffmpeg_path="ffmpeg-test",
                ffprobe_path="ffprobe-test",
                runner=lambda *args, **kwargs: calls.append(args),
            )
            log = json.loads(
                (created / "execution_log.json").read_text(encoding="utf-8")
            )
            reports = json.loads(
                (created / "adapter_reports.json").read_text(encoding="utf-8")
            )

            self.assertTrue((created / "edit_construction_16x9.md").is_file())
            self.assertTrue((created / "edit_construction_9x16.csv").is_file())

        self.assertEqual(calls, [])
        self.assertEqual(log["status"], "blocked")
        self.assertIn("unsupported transition", log["blocker"])
        self.assertEqual(reports["ffmpeg"]["status"], "blocked")

    def test_cli_wraps_path_resolve_runtime_error_without_traceback(self):
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            Path,
            "resolve",
            side_effect=RuntimeError("synthetic resolve loop"),
        ), redirect_stderr(stderr):
            exit_code = main(
                [str(FIXTURE), "--out", str(Path(temp_dir) / "edit")]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("synthetic resolve loop", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_delivery_tiers_emit_different_commands_and_canonical_requirements(self):
        compiled = {}
        with tempfile.TemporaryDirectory() as temp_dir:
            for role, plan in (
                ("rough_cut", load_plan()),
                ("fine_cut", rich_tier_plan("fine_cut")),
                ("final_master", rich_tier_plan("final_master")),
            ):
                plan_path = write_plan(temp_dir, plan, f"{role}.json")
                created = build_edit_bundle(
                    plan_path, Path(temp_dir) / f"edit-{role}"
                )
                command_plan = json.loads(
                    (created / "ffmpeg_commands.json").read_text(encoding="utf-8")
                )
                selected = command_plan["deliveries"][0]
                compiled[role] = {
                    "commands": normalized_commands(selected, created),
                    "requirements": selected["requirements"],
                }

        self.assertEqual(compiled["rough_cut"]["requirements"]["look_mode"], "none")
        self.assertNotIn("final_mix", json.dumps(compiled["rough_cut"]))
        self.assertTrue(compiled["fine_cut"]["requirements"]["approved_cuts"])
        self.assertTrue(compiled["fine_cut"]["requirements"]["text_cues"])
        self.assertTrue(compiled["fine_cut"]["requirements"]["audio_cues"])
        final_requirements = compiled["final_master"]["requirements"]
        self.assertTrue(final_requirements["look_filters"])
        self.assertEqual(final_requirements["loudness"][0]["target_lufs"], -14)
        self.assertIn("video_codec", final_requirements["encoding"])
        self.assertTrue(final_requirements["probe"]["required"])
        self.assertEqual(
            len(
                {
                    json.dumps(value["commands"], sort_keys=True)
                    for value in compiled.values()
                }
            ),
            3,
        )

    def test_fine_and_final_cannot_use_none_modes_to_masquerade_as_tiers(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for role, expected in (
                ("fine_cut", "fine_cut requires approved cut, text, and audio"),
                (
                    "final_master",
                    "final_master requires approved text, audio, and look",
                ),
            ):
                with self.subTest(role=role):
                    plan = copy.deepcopy(load_plan())
                    for delivery in plan["delivery_specs"]:
                        delivery["version_role"] = role
                        delivery["subtitle_mode"] = "none"
                        delivery["audio_mode"] = "none"
                        delivery["look_mode"] = "none"
                    plan_path = write_plan(temp_dir, plan, f"{role}.json")
                    with self.assertRaisesRegex(BuildError, expected):
                        build_edit_bundle(
                            plan_path, Path(temp_dir) / f"edit-{role}"
                        )

    def test_cli_reports_writer_oserror_as_build_blocker(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with tempfile.TemporaryDirectory() as temp_dir, mock.patch(
            "build_edit_bundle.write_construction_markdown",
            side_effect=OSError("synthetic disk failure"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(
                [str(FIXTURE), "--out", str(Path(temp_dir) / "edit")]
            )

        self.assertEqual(exit_code, 1)
        self.assertIn("synthetic disk failure", stderr.getvalue())
        self.assertNotIn("could not load edit plan", stderr.getvalue())
        self.assertEqual(stdout.getvalue(), "")

    def test_cli_accepts_only_mode_specific_terminal_manifest_status(self):
        cases = (
            (False, "dry_run_passed", 0),
            (True, "rendered", 0),
            (False, "blocked", 1),
            (True, "blocked", 1),
            (False, "rendered", 1),
            (True, "dry_run_passed", 1),
            (False, "publishing", 1),
            (True, "publishing", 1),
            (False, "building", 1),
            (True, "unknown", 1),
            (False, None, 1),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            for index, (execute, status, expected) in enumerate(cases):
                with self.subTest(execute=execute, status=status):
                    version_dir = root / f"v{index:03d}"
                    version_dir.mkdir()
                    manifest = {} if status is None else {"status": status}
                    (version_dir / "bundle_manifest.json").write_text(
                        json.dumps(manifest), encoding="utf-8"
                    )
                    argv = [str(FIXTURE), "--out", str(root / "unused")]
                    if execute:
                        argv.append("--execute")
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    with mock.patch(
                        "build_edit_bundle.build_edit_bundle",
                        return_value=version_dir,
                    ), redirect_stdout(stdout), redirect_stderr(stderr):
                        try:
                            exit_code = main(argv)
                        except Exception as exc:
                            self.fail(f"CLI leaked {type(exc).__name__}: {exc}")
                    self.assertEqual(exit_code, expected)
                    if expected == 0:
                        self.assertIn(f"Bundle status: {status}", stdout.getvalue())

    def test_cli_keeps_missing_and_invalid_source_plan_errors_at_exit_two(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            invalid = Path(temp_dir) / "invalid.json"
            invalid.write_text("{not-json", encoding="utf-8")
            for source in (Path(temp_dir) / "missing.json", invalid):
                with self.subTest(source=source):
                    stdout = io.StringIO()
                    stderr = io.StringIO()
                    with redirect_stdout(stdout), redirect_stderr(stderr):
                        exit_code = main(
                            [
                                str(source),
                                "--out",
                                str(Path(temp_dir) / "edit"),
                            ]
                        )
                    self.assertEqual(exit_code, 2)
                    self.assertIn("could not load edit plan", stderr.getvalue())
                    self.assertEqual(stdout.getvalue(), "")

    def test_writer_failure_preserves_partial_bundle_with_blocked_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_root = Path(temp_dir) / "edit"
            with mock.patch(
                "build_edit_bundle.write_srt",
                side_effect=OSError("synthetic SRT write failure"),
            ):
                with self.assertRaisesRegex(BuildError, "synthetic SRT write failure"):
                    build_edit_bundle(FIXTURE, output_root)

            failed_version = output_root / "v001"
            blocked_manifest = json.loads(
                (failed_version / "bundle_manifest.json").read_text(encoding="utf-8")
            )
            preserved_before_retry = {
                path.relative_to(failed_version).as_posix()
                for path in failed_version.rglob("*")
                if path.is_file()
            }
            next_version = build_edit_bundle(FIXTURE, output_root)

        self.assertEqual(blocked_manifest["status"], "blocked")
        self.assertIn("synthetic SRT write failure", blocked_manifest["error"]["message"])
        self.assertEqual(
            set(blocked_manifest["artifacts"]),
            preserved_before_retry - {"bundle_manifest.json"},
        )
        self.assertIn("edit_master_plan.json", preserved_before_retry)
        self.assertIn("edit_construction_16x9.md", preserved_before_retry)
        self.assertEqual(next_version.name, "v002")

    def test_version_creation_rescans_after_a_bounded_mkdir_race(self):
        real_mkdir = Path.mkdir
        collisions = []

        def racing_mkdir(path, *args, **kwargs):
            if path.name == "v001" and not collisions:
                real_mkdir(path, *args, **kwargs)
                collisions.append(path)
                raise FileExistsError("simulated concurrent v001 allocation")
            return real_mkdir(path, *args, **kwargs)

        with tempfile.TemporaryDirectory() as temp_dir, mock.patch.object(
            Path, "mkdir", new=racing_mkdir
        ):
            output_root = Path(temp_dir) / "edit"
            created = build_edit_bundle(FIXTURE, output_root)

        self.assertEqual(len(collisions), 1)
        self.assertEqual(created.name, "v002")


if __name__ == "__main__":
    unittest.main()
