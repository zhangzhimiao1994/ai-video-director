import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "editing" / "valid_plan.json"
JIANYING_FIXTURE = (
    ROOT / "tests" / "fixtures" / "editing" / "jianying_plan.json"
)
sys.path.insert(0, str(SCRIPTS_DIR))

from build_edit_bundle import BuildError, build_edit_bundle, next_version_dir


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

    def test_delivery_tiers_emit_materially_different_plans(self):
        stages = {}
        with tempfile.TemporaryDirectory() as temp_dir:
            for role in ("rough_cut", "fine_cut", "final_master"):
                plan = copy.deepcopy(load_plan())
                for delivery in plan["delivery_specs"]:
                    delivery["version_role"] = role
                    delivery["audio_mode"] = "none"
                    delivery["look_mode"] = "none"
                plan_path = write_plan(temp_dir, plan, f"{role}.json")
                created = build_edit_bundle(
                    plan_path, Path(temp_dir) / f"edit-{role}"
                )
                command_plan = json.loads(
                    (created / "ffmpeg_commands.json").read_text(encoding="utf-8")
                )
                stages[role] = command_plan["deliveries"][0]["stages"]

        self.assertNotIn("final_look", stages["rough_cut"])
        self.assertNotIn("loudness", stages["rough_cut"])
        for stage in ("approved_cut_points", "text_instructions", "audio_instructions"):
            self.assertIn(stage, stages["fine_cut"])
        for stage in ("final_look", "loudness", "encoding", "probe_requirements"):
            self.assertIn(stage, stages["final_master"])
        self.assertEqual(len({tuple(value) for value in stages.values()}), 3)


if __name__ == "__main__":
    unittest.main()
