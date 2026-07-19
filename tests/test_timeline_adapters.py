import copy
import csv
import io
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from decimal import Decimal
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURE = ROOT / "tests" / "fixtures" / "editing" / "valid_plan.json"
sys.path.insert(0, str(SCRIPTS_DIR))

from timeline_adapters import (
    AdapterError,
    construction_rows,
    ffmpeg_command_plan,
    srt_timestamp,
    write_construction_csv,
    write_construction_markdown,
    write_fcpxml,
    write_jianying_instructions,
    write_otio,
    write_srt,
)


def load_plan():
    with FIXTURE.open("r", encoding="utf-8") as plan_file:
        return json.load(plan_file)


def timeline(plan, timeline_id="TL-16"):
    return next(
        item for item in plan["timelines"] if item["timeline_id"] == timeline_id
    )


def delivery(plan, delivery_id="D16"):
    return next(
        item
        for item in plan["delivery_specs"]
        if item["delivery_id"] == delivery_id
    )


def units(plan, timeline_id="TL-16"):
    return timeline(plan, timeline_id)["video_tracks"][0]["edit_units"]


def add_text_cues(plan):
    plan["text_tracks"][0]["cues"] = [
        {
            "text_cue_id": "TC02",
            "text": "第二句",
            "timeline_in_seconds": 2,
            "timeline_out_seconds": 4,
        },
        {
            "text_cue_id": "TC01",
            "text": "第一句",
            "timeline_in_seconds": 0,
            "timeline_out_seconds": 2,
        },
    ]
    units(plan)[0]["text_cue_ids"] = ["TC01"]
    units(plan)[1]["text_cue_ids"] = ["TC02"]


def add_audio_cue(plan, *, authorized=True):
    plan["media_bindings"].append(
        {
            "asset_id": "AUD01",
            "binding_scope": "project",
            "target_id": "PKG-001",
            "source_type": "post_asset",
            "path_or_uri": "media/music.wav",
            "file_status": "online" if authorized else "offline",
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
    units(plan)[0]["audio_cue_ids"] = ["AC01"]


def prepare_delivery(plan, **updates):
    selected = delivery(plan)
    selected.update(
        {
            "version_role": "final_master",
            "subtitle_mode": "none",
            "audio_mode": "none",
            "look_mode": "none",
            **updates,
        }
    )
    return selected


def parse_fcpx_time(value):
    if not value.endswith("s"):
        raise AssertionError(f"not an FCPXML time: {value}")
    return Fraction(value[:-1])


class TimelineAdapterTests(unittest.TestCase):
    def test_construction_rows_are_stable_complete_and_canonical(self):
        plan = load_plan()
        selected = timeline(plan)

        rows = construction_rows(plan, selected)

        self.assertEqual([row["edit_unit_id"] for row in rows], ["E16-01", "E16-02"])
        expected_fields = {
            "edit_unit_id",
            "sequence",
            "shot_id",
            "asset_id",
            "asset_path",
            "timeline_in_seconds",
            "timeline_out_seconds",
            "duration_seconds",
            "source_in_seconds",
            "source_out_seconds",
            "cut_reason",
            "transition_in",
            "transition_out",
            "speed",
            "freeze_frames",
            "stabilization",
            "reframe",
            "scale",
            "position",
            "audio_cue_ids",
            "text_cue_ids",
            "look_instruction",
            "risk_triggers",
            "approval_status",
        }
        self.assertTrue(expected_fields.issubset(rows[0]))
        self.assertEqual(rows[0]["asset_path"], "media/SH01_T01.mp4")
        self.assertEqual(rows[1]["position"], {"x": 0.55, "y": 0.5})

    def test_construction_rows_reject_missing_asset_reference(self):
        plan = load_plan()
        units(plan)[0]["asset_id"] = "MISSING"

        with self.assertRaisesRegex(AdapterError, "unknown asset_id MISSING"):
            construction_rows(plan, timeline(plan))

    def test_construction_writers_match_rows_and_preserve_utf8(self):
        plan = load_plan()
        units(plan)[0]["cut_reason"] = "中文切点"
        rows = construction_rows(plan, timeline(plan))
        with tempfile.TemporaryDirectory() as temp_dir:
            markdown_path = Path(temp_dir) / "nested" / "construction.md"
            csv_path = Path(temp_dir) / "nested" / "construction.csv"

            self.assertEqual(
                write_construction_markdown(plan, timeline(plan), markdown_path),
                markdown_path,
            )
            self.assertEqual(
                write_construction_csv(plan, timeline(plan), csv_path), csv_path
            )
            markdown = markdown_path.read_text(encoding="utf-8")
            parsed_csv = list(
                csv.DictReader(io.StringIO(csv_path.read_text(encoding="utf-8")))
            )

        self.assertIn("# Construction Sheet: TL-16", markdown)
        self.assertIn("edit_unit_id", markdown)
        self.assertIn("中文切点", markdown)
        self.assertEqual(markdown.count("\n| E16-"), len(rows))
        self.assertEqual(len(parsed_csv), len(rows))
        self.assertEqual(set(parsed_csv[0]), set(rows[0]))
        self.assertEqual(parsed_csv[0]["cut_reason"], "中文切点")

    def test_all_writers_refuse_to_overwrite_destination(self):
        plan = load_plan()
        writer_calls = (
            lambda path: write_construction_markdown(plan, timeline(plan), path),
            lambda path: write_construction_csv(plan, timeline(plan), path),
            lambda path: write_srt(plan, timeline(plan), path),
            lambda path: write_otio(plan, timeline(plan), path),
            lambda path: write_fcpxml(plan, timeline(plan), path),
            lambda path: write_jianying_instructions(plan, path),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            for index, writer in enumerate(writer_calls):
                destination = Path(temp_dir) / f"existing-{index}"
                destination.write_text("keep", encoding="utf-8")
                with self.subTest(index=index):
                    with self.assertRaisesRegex(AdapterError, "already exists"):
                        writer(destination)
                    self.assertEqual(destination.read_text(encoding="utf-8"), "keep")

    def test_srt_timestamp_uses_decimal_millisecond_time(self):
        self.assertEqual(srt_timestamp(Decimal("0")), "00:00:00,000")
        self.assertEqual(srt_timestamp(Decimal("3661.234")), "01:01:01,234")
        self.assertEqual(srt_timestamp(Decimal("0.001")), "00:00:00,001")
        with self.assertRaises(AdapterError):
            srt_timestamp({})

    def test_srt_is_empty_for_no_cues_and_sorts_only_mounted_track_cues(self):
        plan = load_plan()
        with tempfile.TemporaryDirectory() as temp_dir:
            empty_path = Path(temp_dir) / "empty.srt"
            write_srt(plan, timeline(plan), empty_path)
            self.assertEqual(empty_path.read_bytes(), b"")

            add_text_cues(plan)
            populated_path = Path(temp_dir) / "subtitles.srt"
            write_srt(plan, timeline(plan), populated_path)
            content = populated_path.read_text(encoding="utf-8")

            timeline(plan, "TL-9")["text_track_refs"] = []
            isolated_path = Path(temp_dir) / "isolated.srt"
            write_srt(plan, timeline(plan, "TL-9"), isolated_path)
            isolated_content = isolated_path.read_bytes()

        self.assertEqual(
            content,
            "1\n00:00:00,000 --> 00:00:02,000\n第一句\n\n"
            "2\n00:00:02,000 --> 00:00:04,000\n第二句\n",
        )
        self.assertEqual(isolated_content, b"")

    def test_otio_has_public_schema_and_frame_exact_clip_ranges(self):
        plan = load_plan()
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "timeline.otio"
            write_otio(plan, timeline(plan), destination)
            document = json.loads(destination.read_text(encoding="utf-8"))

        self.assertEqual(document["OTIO_SCHEMA"], "Timeline.1")
        stack = document["tracks"]
        self.assertEqual(stack["OTIO_SCHEMA"], "Stack.1")
        track = stack["children"][0]
        self.assertEqual(track["OTIO_SCHEMA"], "Track.1")
        self.assertEqual(track["kind"], "Video")
        self.assertEqual(len(track["children"]), 2)
        first = track["children"][0]
        self.assertEqual(first["OTIO_SCHEMA"], "Clip.2")
        self.assertEqual(first["media_reference"]["OTIO_SCHEMA"], "ExternalReference.1")
        source_range = first["source_range"]
        self.assertEqual(source_range["OTIO_SCHEMA"], "TimeRange.1")
        self.assertEqual(
            source_range["start_time"],
            {"OTIO_SCHEMA": "RationalTime.1", "value": 0, "rate": 24},
        )
        self.assertEqual(
            source_range["duration"],
            {"OTIO_SCHEMA": "RationalTime.1", "value": 48, "rate": 24},
        )

    def test_fcpxml_has_resources_spine_and_frame_exact_clips(self):
        plan = load_plan()
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "timeline.fcpxml"
            write_fcpxml(plan, timeline(plan), destination)
            root = ET.parse(destination).getroot()

        self.assertEqual(root.tag, "fcpxml")
        self.assertEqual(root.attrib["version"], "1.10")
        self.assertEqual(len(root.findall("./resources/format")), 1)
        assets = root.findall("./resources/asset")
        self.assertEqual(len(assets), 2)
        asset_ids = {item.attrib["id"] for item in assets}
        sequence = root.find("./library/event/project/sequence")
        self.assertIsNotNone(sequence)
        clips = sequence.findall("./spine/asset-clip")
        self.assertEqual(len(clips), 2)
        self.assertTrue(all(clip.attrib["ref"] in asset_ids for clip in clips))
        self.assertEqual(parse_fcpx_time(clips[0].attrib["start"]), Fraction(0))
        self.assertEqual(parse_fcpx_time(clips[0].attrib["duration"]), Fraction(2))
        self.assertEqual(parse_fcpx_time(clips[1].attrib["offset"]), Fraction(2))

    def test_exchange_writers_reject_non_frame_boundaries_and_accept_24fps_frame(self):
        for writer, suffix in ((write_otio, ".otio"), (write_fcpxml, ".fcpxml")):
            with self.subTest(writer=writer.__name__):
                plan = load_plan()
                unit = units(plan)[0]
                unit["source_in_seconds"] = 0.01
                unit["source_out_seconds"] = 2.01
                with tempfile.TemporaryDirectory() as temp_dir:
                    with self.assertRaisesRegex(AdapterError, "frame boundary"):
                        writer(plan, timeline(plan), Path(temp_dir) / f"bad{suffix}")

                plan = load_plan()
                unit = units(plan)[0]
                unit["source_in_seconds"] = Fraction(1, 24)
                unit["source_out_seconds"] = Fraction(49, 24)
                with tempfile.TemporaryDirectory() as temp_dir:
                    result = writer(
                        plan, timeline(plan), Path(temp_dir) / f"good{suffix}"
                    )
                    self.assertTrue(result.exists())

    def test_nonempty_extra_video_layer_blocks_flattening_but_empty_layer_is_allowed(self):
        flatteners = (
            lambda plan, selected, path: construction_rows(plan, selected),
            lambda plan, selected, path: write_otio(plan, selected, path / "x.otio"),
            lambda plan, selected, path: write_fcpxml(plan, selected, path / "x.fcpxml"),
            lambda plan, selected, path: ffmpeg_command_plan(plan, selected, path),
        )
        for flattener in flatteners:
            with self.subTest(flattener=flattener):
                plan = load_plan()
                selected = timeline(plan)
                selected["video_tracks"].append(
                    {"track_id": "V2", "edit_units": [copy.deepcopy(units(plan)[0])]}
                )
                with tempfile.TemporaryDirectory() as temp_dir:
                    with self.assertRaisesRegex(
                        AdapterError,
                        "^multi-layer video requires manual_or_unverified handling$",
                    ):
                        flattener(plan, selected, Path(temp_dir) / "version")

                plan = load_plan()
                selected = timeline(plan)
                selected["video_tracks"].append({"track_id": "V2", "edit_units": []})
                with tempfile.TemporaryDirectory() as temp_dir:
                    flattener(plan, selected, Path(temp_dir) / "version")

    def test_jianying_handoff_is_ordered_manual_and_never_private_project_json(self):
        plan = load_plan()
        with tempfile.TemporaryDirectory() as temp_dir:
            destination = Path(temp_dir) / "jianying_capcut_instructions.md"
            result = write_jianying_instructions(plan, destination)
            content = destination.read_text(encoding="utf-8")

        self.assertEqual(result.name, "jianying_capcut_instructions.md")
        for required in (
            "manual_or_unverified",
            "create_new",
            "16:9",
            "9:16",
            "construction CSV",
            "SRT",
            "track mapping",
            "effect parameters",
            "A01",
            "A02",
        ):
            self.assertIn(required, content)
        self.assertLess(content.index("E16-01"), content.index("E16-02"))
        self.assertLess(content.index("E9-01"), content.index("E9-02"))
        self.assertNotIn(".json", content.lower())

    def test_ffmpeg_returns_segment_and_concat_argument_arrays_inside_version(self):
        plan = load_plan()
        selected = timeline(plan)
        with tempfile.TemporaryDirectory() as temp_dir:
            version_dir = Path(temp_dir) / "v001"
            commands = ffmpeg_command_plan(plan, selected, version_dir)

        self.assertEqual(len(commands), 3)
        self.assertTrue(all(isinstance(command, list) for command in commands))
        self.assertTrue(
            all(isinstance(argument, str) for command in commands for argument in command)
        )
        first = commands[0]
        for argument in (
            "-ss",
            "-t",
            "-i",
            "-an",
            "-vf",
            "-c:v",
            "libx264",
        ):
            self.assertIn(argument, first)
        picture_filter = first[first.index("-vf") + 1]
        self.assertIn("scale=1920:1080", picture_filter)
        self.assertIn("crop=1920:1080", picture_filter)
        self.assertIn("fps=24", picture_filter)
        self.assertIn("format=yuv420p", picture_filter)
        self.assertEqual(commands[-1][commands[-1].index("-f") + 1], "concat")
        resolved_version = version_dir.resolve()
        for command in commands:
            output = Path(command[-1]).resolve()
            self.assertEqual(output, resolved_version / output.relative_to(resolved_version))

    def test_ffmpeg_rejects_unsupported_transitions_and_effects_without_downgrade(self):
        cases = (
            ("transition_out", "cross_dissolve"),
            ("effects", [{"type": "glow", "amount": 1}]),
        )
        for field, value in cases:
            with self.subTest(field=field):
                plan = load_plan()
                units(plan)[0][field] = value
                with tempfile.TemporaryDirectory() as temp_dir:
                    with self.assertRaisesRegex(AdapterError, "unsupported"):
                        ffmpeg_command_plan(plan, timeline(plan), Path(temp_dir) / "v001")

    def test_exchange_writers_reject_unsupported_transitions_without_downgrade(self):
        for writer, suffix in ((write_otio, ".otio"), (write_fcpxml, ".fcpxml")):
            with self.subTest(writer=writer.__name__):
                plan = load_plan()
                units(plan)[0]["transition_out"] = "cross_dissolve"
                with tempfile.TemporaryDirectory() as temp_dir:
                    with self.assertRaisesRegex(AdapterError, "unsupported transition"):
                        writer(plan, timeline(plan), Path(temp_dir) / f"bad{suffix}")

    def test_ffmpeg_final_mix_keeps_authorized_audio_and_compiles_required_stages(self):
        plan = load_plan()
        add_audio_cue(plan)
        prepare_delivery(plan, audio_mode="final_mix")
        with tempfile.TemporaryDirectory() as temp_dir:
            commands = ffmpeg_command_plan(plan, timeline(plan), Path(temp_dir) / "v001")

        final = commands[-1]
        graph = final[final.index("-filter_complex") + 1]
        for stage in ("atrim", "asetpts", "adelay", "volume", "amix", "loudnorm"):
            self.assertIn(stage, graph)
        self.assertIn("media/music.wav", final)
        self.assertNotIn("-an", final)

    def test_ffmpeg_rejects_unknown_or_unauthorized_audio_assets(self):
        for mode in ("missing", "unauthorized"):
            with self.subTest(mode=mode):
                plan = load_plan()
                add_audio_cue(plan, authorized=mode != "unauthorized")
                if mode == "missing":
                    plan["audio_tracks"][0]["cues"][0]["asset_id"] = "UNKNOWN"
                prepare_delivery(plan, audio_mode="final_mix")
                with tempfile.TemporaryDirectory() as temp_dir:
                    with self.assertRaisesRegex(AdapterError, "audio asset"):
                        ffmpeg_command_plan(
                            plan, timeline(plan), Path(temp_dir) / "v001"
                        )

    def test_ffmpeg_subtitle_modes_are_exact(self):
        modes = {
            "burn_in": True,
            "sidecar": False,
            "none": False,
        }
        for mode, burned in modes.items():
            with self.subTest(mode=mode):
                plan = load_plan()
                prepare_delivery(plan, subtitle_mode=mode)
                with tempfile.TemporaryDirectory() as temp_dir:
                    version_dir = Path(temp_dir) / "v001"
                    commands = ffmpeg_command_plan(plan, timeline(plan), version_dir)
                all_filters = [
                    command[command.index("-vf") + 1]
                    for command in commands
                    if "-vf" in command
                ]
                self.assertEqual(
                    any(
                        "subtitles=" in value and "subtitles_TL-16.srt" in value
                        for value in all_filters
                    ),
                    burned,
                )

        plan = load_plan()
        prepare_delivery(plan, subtitle_mode="auto")
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(AdapterError, "unsupported subtitle_mode"):
                ffmpeg_command_plan(plan, timeline(plan), Path(temp_dir) / "v001")

    def test_ffmpeg_look_filters_are_allowlisted_and_one_safe_filter_argument(self):
        cases = (
            ([{"name": "eq", "params": {"contrast": 1.1, "brightness": -0.1}}], "eq="),
            ([{"filter": "curves", "params": {"preset": "vintage"}}], "curves=preset=vintage"),
        )
        for filters, expected in cases:
            with self.subTest(filters=filters):
                plan = load_plan()
                prepare_delivery(plan, look_mode="approved")
                plan["look_plan"]["ffmpeg_filters"] = filters
                with tempfile.TemporaryDirectory() as temp_dir:
                    commands = ffmpeg_command_plan(
                        plan, timeline(plan), Path(temp_dir) / "v001"
                    )
                final = commands[-1]
                self.assertEqual(final.count("-vf"), 1)
                self.assertIn(expected, final[final.index("-vf") + 1])

    def test_ffmpeg_lut_uses_authorized_cube_paths_without_splitting_argv(self):
        paths_and_roots = (
            (r"C:\media\look.cube", r"C:\media"),
            ("/media/look.cube", "/media"),
        )
        for lut_path, root in paths_and_roots:
            with self.subTest(lut_path=lut_path):
                plan = load_plan()
                prepare_delivery(plan, look_mode="approved")
                plan["execution"]["authorized_media_roots"] = [root]
                plan["media_bindings"].append(
                    {
                        "asset_id": "LUT01",
                        "binding_scope": "project",
                        "target_id": "PKG-001",
                        "source_type": "post_asset",
                        "path_or_uri": lut_path,
                        "file_status": "online",
                        "rights_status": "cleared",
                        "probe_status": "verified",
                        "selection_reason": "approved LUT",
                        "acceptance_status": "approved",
                    }
                )
                plan["look_plan"]["ffmpeg_filters"] = [
                    {"name": "lut3d", "params": {"asset_id": "LUT01"}}
                ]
                with tempfile.TemporaryDirectory() as temp_dir:
                    commands = ffmpeg_command_plan(
                        plan, timeline(plan), Path(temp_dir) / "v001"
                    )
                final = commands[-1]
                filter_value = final[final.index("-vf") + 1]
                self.assertIn("lut3d=", filter_value)
                self.assertEqual(final.count(filter_value), 1)

    def test_ffmpeg_rejects_malformed_or_unsafe_look_filters(self):
        bad_filters = (
            "eq=contrast=1.1",
            {"name": "unsharp", "params": {}},
            {"name": "eq", "filter": "eq", "params": {}},
            {"name": "eq", "params": {"contrast": "1;movie=x"}},
            {"name": "curves", "params": {"preset": "0/0 1/1"}},
            {"name": "lut3d", "params": {"file": "bad.cube"}},
        )
        for bad_filter in bad_filters:
            with self.subTest(bad_filter=bad_filter):
                plan = load_plan()
                prepare_delivery(plan, look_mode="approved")
                plan["look_plan"]["ffmpeg_filters"] = [bad_filter]
                with tempfile.TemporaryDirectory() as temp_dir:
                    with self.assertRaisesRegex(AdapterError, "look filter"):
                        ffmpeg_command_plan(
                            plan, timeline(plan), Path(temp_dir) / "v001"
                        )

    def test_ffmpeg_rejects_unsafe_lut_and_output_paths_and_filesystem_root(self):
        plan = load_plan()
        delivery(plan)["filename"] = "../escape.mp4"
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(AdapterError, "inside version_dir"):
                ffmpeg_command_plan(plan, timeline(plan), Path(temp_dir) / "v001")

        plan = load_plan()
        prepare_delivery(plan, look_mode="approved")
        plan["media_bindings"].append(
            {
                "asset_id": "LUT01",
                "binding_scope": "project",
                "target_id": "PKG-001",
                "source_type": "post_asset",
                "path_or_uri": "media/../evil.cube",
                "file_status": "online",
                "rights_status": "cleared",
                "probe_status": "verified",
            }
        )
        plan["look_plan"]["ffmpeg_filters"] = [
            {"name": "lut3d", "params": {"asset_id": "LUT01"}}
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaisesRegex(AdapterError, "look filter"):
                ffmpeg_command_plan(plan, timeline(plan), Path(temp_dir) / "v001")

        root_path = Path(Path.cwd().anchor)
        with self.assertRaisesRegex(AdapterError, "filesystem root"):
            ffmpeg_command_plan(load_plan(), timeline(load_plan()), root_path)

    def test_bad_shapes_raise_adapter_error_not_builtin_type_errors(self):
        with self.assertRaises(AdapterError):
            construction_rows([], {})
        with self.assertRaises(AdapterError):
            ffmpeg_command_plan({}, {}, Path("version"))

    def test_unhashable_ffmpeg_values_raise_adapter_error(self):
        mutations = (
            lambda plan: units(plan)[0].__setitem__("transition_out", {}),
            lambda plan: delivery(plan).__setitem__("subtitle_mode", {}),
            lambda plan: delivery(plan).__setitem__("audio_mode", {}),
            lambda plan: plan["look_plan"].__setitem__(
                "ffmpeg_filters", [{"name": {}, "params": {}}]
            ),
            lambda plan: plan["media_bindings"][0].__setitem__("source_type", {}),
        )
        for mutate in mutations:
            with self.subTest(mutate=mutate):
                plan = load_plan()
                if "look_plan" in mutate.__code__.co_consts:
                    prepare_delivery(plan, look_mode="approved")
                mutate(plan)
                with tempfile.TemporaryDirectory() as temp_dir:
                    with self.assertRaises(AdapterError):
                        ffmpeg_command_plan(
                            plan, timeline(plan), Path(temp_dir) / "v001"
                        )

        with self.assertRaises(AdapterError):
            ffmpeg_command_plan(
                load_plan(), timeline(load_plan()), Path("version"), ffmpeg_path={}
            )


if __name__ == "__main__":
    unittest.main()
