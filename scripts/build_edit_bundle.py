"""Build versioned, non-overwriting finished-film editing handoff bundles."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

from timeline_adapters import (
    AdapterError,
    ffmpeg_command_plan,
    write_construction_csv,
    write_construction_markdown,
    write_fcpxml,
    write_jianying_instructions,
    write_otio,
    write_srt,
)
from validate_edit_plan import validate_edit_plan


class BuildError(ValueError):
    """Raised when a safe editing bundle cannot be built or executed."""


class _PlanInputError(ValueError):
    """Internal distinction for CLI usage errors while loading the source plan."""


_VERSION_NAME = re.compile(r"^v([0-9]{3,})$")
_VERSION_CREATE_ATTEMPTS = 16


def _filesystem_root(path: Path) -> Path:
    return Path(path.anchor).resolve()


def next_version_dir(output_root: Path) -> Path:
    """Return the next monotonically increasing ``vNNN`` path without creating it."""

    try:
        root = Path(output_root).resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"invalid output root: {exc}") from None
    if not root.anchor or root == _filesystem_root(root):
        raise BuildError("output_root must not be a filesystem root")
    if root.exists() and not root.is_dir():
        raise BuildError("output_root must be a directory")

    highest = 0
    if root.exists():
        try:
            entries = tuple(root.iterdir())
        except OSError as exc:
            raise BuildError(f"could not inspect output_root: {exc}") from None
        for entry in entries:
            match = _VERSION_NAME.fullmatch(entry.name)
            if match is not None:
                highest = max(highest, int(match.group(1)))
    return root / f"v{highest + 1:03d}"


def _create_version_dir(output_root: Path) -> Path:
    """Atomically reserve a fresh version path with finite race recovery."""

    root = Path(output_root).resolve()
    for _attempt in range(_VERSION_CREATE_ATTEMPTS):
        version_dir = next_version_dir(root)
        try:
            version_dir.resolve().relative_to(root)
        except ValueError:
            raise BuildError("version directory escapes output_root") from None
        try:
            version_dir.mkdir(parents=True, exist_ok=False)
        except FileExistsError:
            continue
        except OSError as exc:
            raise BuildError(f"could not create version directory: {exc}") from None
        return version_dir
    raise BuildError(
        "could not allocate a version directory after "
        f"{_VERSION_CREATE_ATTEMPTS} concurrent conflicts"
    )


def _write_json_exclusive(destination: Path, value: object) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("x", encoding="utf-8", newline="") as output:
            json.dump(value, output, ensure_ascii=False, indent=2, sort_keys=True)
            output.write("\n")
    except FileExistsError:
        raise BuildError(f"artifact already exists: {destination}") from None
    return destination


def _replace_owned_json(destination: Path, value: object) -> None:
    """Replace a file created by this invocation inside its fresh version directory."""

    destination.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _atomic_replace_json(destination: Path, value: object) -> None:
    """Atomically publish JSON within an invocation-owned version directory."""

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=".bundle_manifest.",
        suffix=".tmp",
        dir=destination.parent,
        delete=False,
    ) as output:
        temporary_name = output.name
        json.dump(value, output, ensure_ascii=False, indent=2, sort_keys=True)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    # A failed replace leaves this diagnostic temp file in the new version;
    # it never removes a prior manifest or another partial artifact.
    os.replace(temporary_name, destination)


def _timeline_slug(timeline: dict[str, Any]) -> str:
    aspect = timeline.get("aspect_ratio")
    if not isinstance(aspect, str) or re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", aspect) is None:
        raise BuildError("timeline aspect_ratio must use WIDTH:HEIGHT")
    return aspect.replace(":", "x")


def _delivery_for_timeline(
    plan: dict[str, Any], timeline_id: object
) -> dict[str, Any]:
    matches = [
        delivery
        for delivery in plan["delivery_specs"]
        if delivery.get("timeline_id") == timeline_id
    ]
    if len(matches) != 1:
        raise BuildError(
            f"timeline {timeline_id} must have exactly one delivery specification"
        )
    return matches[0]


def _tier_stages(version_role: object) -> list[str]:
    common = ["assembly"]
    fine = [
        "selected_takes",
        "approved_cut_points",
        "transitions",
        "reframe",
        "text_instructions",
        "audio_instructions",
    ]
    final = ["final_look", "loudness", "encoding", "probe_requirements"]
    if version_role == "rough_cut":
        return common
    if version_role == "fine_cut":
        return common + fine
    if version_role == "final_master":
        return common + fine + final
    raise BuildError(f"unsupported delivery tier {version_role}")


def _active_units(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    matches = [
        track
        for track in timeline["video_tracks"]
        if track.get("track_id") == "V1"
        and track.get("runtime_role") == "active"
        and track.get("release_role") == "first_release"
    ]
    if len(matches) != 1:
        raise BuildError("tier plan requires one active first_release V1 track")
    return matches[0]["edit_units"]


def _mounted_cues(
    plan: dict[str, Any], timeline: dict[str, Any], *, kind: str
) -> list[dict[str, Any]]:
    if kind == "text":
        ref_field, tracks_field, id_field, cues_field = (
            "text_track_refs",
            "text_tracks",
            "text_track_id",
            "cues",
        )
    elif kind == "audio":
        ref_field, tracks_field, id_field, cues_field = (
            "audio_track_refs",
            "audio_tracks",
            "audio_track_id",
            "cues",
        )
    else:  # pragma: no cover - private caller uses a closed set.
        raise BuildError(f"unsupported cue kind {kind}")
    mounted_ids = set(timeline[ref_field])
    cues = []
    for track in plan[tracks_field]:
        if track.get(id_field) in mounted_ids:
            cues.extend(track[cues_field])
    return cues


def _approved_cut_requirements(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    requirements = []
    for unit in _active_units(timeline):
        if unit.get("approval_status") != "approved":
            raise BuildError("fine_cut requires every cut and reframe to be approved")
        requirements.append(
            {
                field: unit.get(field)
                for field in (
                    "edit_unit_id",
                    "asset_id",
                    "timeline_in_seconds",
                    "timeline_out_seconds",
                    "source_in_seconds",
                    "source_out_seconds",
                    "transition_in",
                    "transition_out",
                    "reframe",
                    "scale",
                    "position",
                    "approval_status",
                )
            }
        )
    return requirements


def _tier_requirements(
    plan: dict[str, Any],
    timeline: dict[str, Any],
    delivery: dict[str, Any],
) -> dict[str, Any]:
    """Compile enforceable tier inputs, not cosmetic tier labels."""

    role = delivery.get("version_role")
    audio_mode = delivery.get("audio_mode")
    look_mode = delivery.get("look_mode")
    subtitle_mode = delivery.get("subtitle_mode")
    if role == "rough_cut":
        if audio_mode not in {"temporary_or_silent", "none"} or look_mode != "none":
            raise BuildError("rough_cut excludes final look and final mix")
        return {
            "tier": role,
            "timeline_id": timeline.get("timeline_id"),
            "edit_unit_ids": [
                unit.get("edit_unit_id") for unit in _active_units(timeline)
            ],
            "subtitle_mode": subtitle_mode,
            "audio_mode": audio_mode,
            "look_mode": look_mode,
            "probe": {"required": False},
        }

    if role not in {"fine_cut", "final_master"}:
        raise BuildError(f"unsupported delivery tier {role}")

    text_cues = _mounted_cues(plan, timeline, kind="text")
    audio_cues = _mounted_cues(plan, timeline, kind="audio")
    has_text = subtitle_mode in {"sidecar", "burn_in"} and bool(text_cues)
    has_audio = audio_mode == "final_mix" and bool(audio_cues)
    has_final_look = (
        look_mode == "approved"
        and isinstance(plan["look_plan"].get("ffmpeg_filters"), list)
        and bool(plan["look_plan"]["ffmpeg_filters"])
    )
    if role == "fine_cut" and (not has_text or not has_audio or look_mode != "none"):
        raise BuildError(
            "fine_cut requires approved cut, text, and audio instructions; "
            "final look remains excluded"
        )
    if role == "final_master" and (
        not has_text or not has_audio or not has_final_look
    ):
        raise BuildError(
            "final_master requires approved text, audio, and look instructions"
        )

    requirements: dict[str, Any] = {
        "tier": role,
        "timeline_id": timeline.get("timeline_id"),
        "approved_cuts": _approved_cut_requirements(timeline),
        "subtitle_mode": subtitle_mode,
        "text_cues": [
            {
                field: cue.get(field)
                for field in (
                    "text_cue_id",
                    "timeline_in_seconds",
                    "timeline_out_seconds",
                    "text",
                )
            }
            for cue in text_cues
        ],
        "audio_mode": audio_mode,
        "audio_cues": [
            {
                field: cue.get(field)
                for field in (
                    "audio_cue_id",
                    "asset_id",
                    "timeline_in_seconds",
                    "timeline_out_seconds",
                    "gain_db",
                )
            }
            for cue in audio_cues
        ],
        "look_mode": look_mode,
        "probe": {"required": False},
    }
    if role == "final_master":
        mounted_audio_ids = set(timeline["audio_track_refs"])
        requirements.update(
            {
                "look_filters": plan["look_plan"]["ffmpeg_filters"],
                "loudness": [
                    {
                        "audio_track_id": track.get("audio_track_id"),
                        "target_lufs": track.get("target_lufs"),
                        "true_peak_db": track.get("true_peak_db"),
                    }
                    for track in plan["audio_tracks"]
                    if track.get("audio_track_id") in mounted_audio_ids
                ],
                "encoding": {
                    field: delivery.get(field)
                    for field in (
                        "container",
                        "video_codec",
                        "audio_codec",
                        "bitrate",
                        "audio_sample_rate",
                        "audio_channels",
                    )
                },
                "probe": {
                    "required": True,
                    "expected": {
                        "resolution": delivery.get("resolution"),
                        "frame_rate": delivery.get("frame_rate"),
                        "duration_seconds": timeline.get("duration_seconds"),
                        "video_codec": delivery.get("video_codec"),
                        "audio_codec": delivery.get("audio_codec"),
                        "audio_sample_rate": delivery.get("audio_sample_rate"),
                        "audio_channels": delivery.get("audio_channels"),
                    },
                },
            }
        )
    return requirements


def _artifact_names(version_dir: Path) -> list[str]:
    return sorted(
        path.relative_to(version_dir).as_posix()
        for path in version_dir.rglob("*")
        if path.is_file() and path.name != "bundle_manifest.json"
    )


def _manifest(plan: dict[str, Any], version_dir: Path, status: str) -> dict[str, Any]:
    execution = plan.get("execution")
    manifest_id = execution.get("dry_run_manifest_id") if isinstance(execution, dict) else None
    return {
        "manifest_id": manifest_id,
        "edit_plan_id": plan.get("edit_plan_id"),
        "status": status,
        "version_directory": str(version_dir),
        "artifacts": _artifact_names(version_dir),
    }


def _record_blocked_manifest(
    plan: dict[str, Any], version_dir: Path, error: BuildError
) -> None:
    manifest = _manifest(plan, version_dir, "blocked")
    manifest["error"] = {
        "type": type(error).__name__,
        "message": str(error),
    }
    _atomic_replace_json(version_dir / "bundle_manifest.json", manifest)


def _build_handoffs(
    plan: dict[str, Any], version_dir: Path, ffmpeg_path: str
) -> list[dict[str, Any]]:
    command_deliveries: list[dict[str, Any]] = []
    try:
        for timeline in plan["timelines"]:
            slug = _timeline_slug(timeline)
            write_construction_markdown(
                plan, timeline, version_dir / f"edit_construction_{slug}.md"
            )
            write_construction_csv(
                plan, timeline, version_dir / f"edit_construction_{slug}.csv"
            )
            write_srt(plan, timeline, version_dir / f"subtitles_{slug}.srt")
            write_otio(plan, timeline, version_dir / f"timeline_{slug}.otio")
            write_fcpxml(plan, timeline, version_dir / f"timeline_{slug}.fcpxml")

            delivery = _delivery_for_timeline(plan, timeline.get("timeline_id"))
            command_deliveries.append(
                {
                    "delivery_id": delivery.get("delivery_id"),
                    "timeline_id": timeline.get("timeline_id"),
                    "version_role": delivery.get("version_role"),
                    "stages": _tier_stages(delivery.get("version_role")),
                    "requirements": _tier_requirements(plan, timeline, delivery),
                    "commands": ffmpeg_command_plan(
                        plan,
                        timeline,
                        version_dir,
                        delivery,
                        ffmpeg_path=ffmpeg_path,
                    ),
                }
            )

        targets = {
            item.get("target")
            for item in plan["software_targets"]
            if isinstance(item, dict)
        }
        reports: dict[str, dict[str, str]] = {
            "ffmpeg": {
                "status": "planned",
                "artifact": "ffmpeg_commands.json",
            },
            "otio": {"status": "generated", "format": "public_schema"},
            "fcpxml": {"status": "generated", "format": "FCPXML 1.10"},
        }
        if "jianying_capcut" in targets:
            write_jianying_instructions(
                plan, version_dir / "jianying_capcut_instructions.md"
            )
            reports["jianying_capcut"] = {
                "status": "manual_or_unverified",
                "artifact": "jianying_capcut_instructions.md",
            }
        if "ai_editor" in targets:
            reports["ai_editor"] = {
                "status": "strict_json_handoff",
                "artifact": "edit_master_plan.json",
            }
        _write_json_exclusive(
            version_dir / "ffmpeg_commands.json",
            {"schema_version": 1, "deliveries": command_deliveries},
        )
        _write_json_exclusive(version_dir / "adapter_reports.json", reports)
    except (AdapterError, KeyError, TypeError) as exc:
        raise BuildError(str(exc)) from None
    return command_deliveries


def _execute_minimal(
    version_dir: Path,
    command_deliveries: list[dict[str, Any]],
    runner: Callable[..., subprocess.CompletedProcess],
) -> str:
    """Run a planned command list and record state; Task 6 adds full media/probe gates."""

    execution_log: dict[str, Any] = {
        "status": "running",
        "commands": [],
        "rendered_outputs": [],
    }
    blocked = False
    for delivery in command_deliveries:
        delivery_id = delivery["delivery_id"]
        commands = delivery["commands"]
        for args in commands:
            try:
                completed = runner(
                    args,
                    cwd=version_dir,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                record = {
                    "delivery_id": delivery_id,
                    "args": args,
                    "returncode": completed.returncode,
                    "stdout": completed.stdout,
                    "stderr": completed.stderr,
                }
            except OSError as exc:
                record = {
                    "delivery_id": delivery_id,
                    "args": args,
                    "returncode": None,
                    "stdout": "",
                    "stderr": str(exc),
                }
            execution_log["commands"].append(record)
            expected_output = Path(args[-1])
            if record["returncode"] != 0 or not expected_output.is_file():
                if record["returncode"] == 0:
                    record["stderr"] = (
                        (record["stderr"] + "\n").lstrip("\n")
                        + f"expected output is missing: {expected_output}"
                    )
                blocked = True
                break
        if blocked:
            break
        final_output = Path(commands[-1][-1])
        execution_log["rendered_outputs"].append(
            {
                "delivery_id": delivery_id,
                "output_ref": final_output.relative_to(version_dir).as_posix(),
                "status": "rendered",
            }
        )

    execution_log["status"] = "blocked" if blocked else "rendered"
    _write_json_exclusive(version_dir / "execution_log.json", execution_log)
    return execution_log["status"]


def _load_plan(plan_path: Path) -> object:
    source_path = Path(plan_path)
    try:
        with source_path.open("r", encoding="utf-8") as source:
            return json.load(source)
    except (OSError, UnicodeError, ValueError, RecursionError, MemoryError) as exc:
        detail = str(exc) or type(exc).__name__
        raise _PlanInputError(detail) from None


def _build_loaded_bundle(
    plan: object,
    output_root: Path,
    *,
    execute: bool = False,
    ffmpeg_path: str | None = None,
    ffprobe_path: str | None = None,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> Path:
    del ffprobe_path  # Reserved for Task 6 probe verification.
    errors = validate_edit_plan(plan)
    if errors:
        raise BuildError("\n".join(errors))
    if not isinstance(plan, dict):  # Kept explicit for type narrowing and callers.
        raise BuildError("edit plan: expected object")
    execution = plan.get("execution")
    if execute and (
        not isinstance(execution, dict)
        or execution.get("operation_authorization") != "approved"
    ):
        raise BuildError("operation authorization is required")

    version_dir = _create_version_dir(Path(output_root))
    try:
        _write_json_exclusive(version_dir / "edit_master_plan.json", plan)
        command_deliveries = _build_handoffs(
            plan, version_dir, ffmpeg_path or "ffmpeg"
        )
        manifest_path = version_dir / "bundle_manifest.json"
        manifest = _manifest(plan, version_dir, "dry_run_passed")
        _write_json_exclusive(manifest_path, manifest)

        if not execute:
            return version_dir
        if ffmpeg_path is None or not str(ffmpeg_path).strip():
            raise BuildError("ffmpeg is unavailable")

        status = _execute_minimal(version_dir, command_deliveries, runner)
        manifest["status"] = status
        manifest["artifacts"] = _artifact_names(version_dir)
        _replace_owned_json(manifest_path, manifest)
        return version_dir
    except Exception as exc:
        build_error = (
            exc
            if isinstance(exc, BuildError)
            else BuildError(f"could not build bundle: {exc}")
        )
        try:
            _record_blocked_manifest(plan, version_dir, build_error)
        except Exception as manifest_exc:
            raise BuildError(
                f"{build_error}\n"
                "Additionally, the blocked bundle manifest could not be written: "
                f"{manifest_exc}"
            ) from None
        raise build_error from None


def build_edit_bundle(
    plan_path: Path,
    output_root: Path,
    *,
    execute: bool = False,
    ffmpeg_path: str | None = None,
    ffprobe_path: str | None = None,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> Path:
    """Validate a Canon plan and create a fresh dry-run (or authorized) bundle."""

    plan = _load_plan(plan_path)
    try:
        return _build_loaded_bundle(
            plan,
            output_root,
            execute=execute,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
    except BuildError:
        raise
    except (OSError, UnicodeError) as exc:
        raise BuildError(f"could not build bundle: {exc}") from None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build a versioned finished-film editing handoff bundle."
    )
    parser.add_argument("plan", type=Path, help="UTF-8 edit_master_plan JSON")
    parser.add_argument("--out", type=Path, required=True, help="Bundle output root")
    parser.add_argument("--execute", action="store_true", help="Run an authorized FFmpeg plan")
    parser.add_argument("--ffmpeg", help="Explicit FFmpeg executable path")
    parser.add_argument("--ffprobe", help="Explicit ffprobe executable path")
    args = parser.parse_args(argv)

    try:
        version_dir = build_edit_bundle(
            args.plan,
            args.out,
            execute=args.execute,
            ffmpeg_path=args.ffmpeg,
            ffprobe_path=args.ffprobe,
        )
    except _PlanInputError as exc:
        print(f"ERROR: could not load edit plan: {exc}", file=sys.stderr)
        return 2
    except BuildError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        manifest = json.loads(
            (version_dir / "bundle_manifest.json").read_text(encoding="utf-8")
        )
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"ERROR: could not inspect bundle manifest: {exc}", file=sys.stderr)
        return 1
    print(version_dir)
    print(f"Bundle status: {manifest['status']}")
    return 0 if manifest["status"] != "blocked" else 1


if __name__ == "__main__":
    raise SystemExit(main())
