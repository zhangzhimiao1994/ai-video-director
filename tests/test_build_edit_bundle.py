import copy
import io
import json
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
sys.path.insert(0, str(SCRIPTS_DIR))

from build_edit_bundle import BuildError, build_edit_bundle, main, next_version_dir


def load_plan(path=FIXTURE):
    with Path(path).open("r", encoding="utf-8") as source:
        return json.load(source)


def write_plan(directory, plan, name="plan.json"):
    path = Path(directory) / name
    path.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return path


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
    return plan


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
            manifest = json.loads(
                (created / "bundle_manifest.json").read_text(encoding="utf-8")
            )

        self.assertTrue(expected.issubset(present), expected - present)
        self.assertEqual(canon, load_plan())
        self.assertEqual({item["timeline_id"] for item in commands["deliveries"]}, {"TL-16", "TL-9"})
        self.assertEqual(reports["ffmpeg"]["status"], "planned")
        self.assertEqual(reports["otio"]["status"], "generated")
        self.assertEqual(reports["fcpxml"]["status"], "generated")
        self.assertEqual(manifest["status"], "dry_run_passed")
        self.assertEqual(set(manifest["artifacts"]), present - {"bundle_manifest.json"})

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
            plan_path = write_plan(temp_dir, authorized_plan())
            success_dir = build_edit_bundle(
                plan_path,
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

            blocked_dir = build_edit_bundle(
                plan_path,
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
