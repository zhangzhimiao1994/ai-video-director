"""Build versioned, non-overwriting finished-film editing handoff bundles."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path
from typing import Any

from ai_editor_plan import ai_editor_plan_payload
from cinematic_report import cinematic_report_markdown, cinematic_report_payload
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
    try:
        return Path(path.anchor).resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"invalid filesystem root: {exc}") from None


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

    try:
        root = Path(output_root).resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"invalid output root: {exc}") from None
    for _attempt in range(_VERSION_CREATE_ATTEMPTS):
        version_dir = next_version_dir(root)
        try:
            version_dir.resolve().relative_to(root)
        except (OSError, RuntimeError, TypeError, ValueError):
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
    """Atomically replace invocation-owned JSON inside the fresh version directory."""

    _atomic_replace_json(destination, value)


def _atomic_replace_json(destination: Path, value: object) -> None:
    """Atomically publish JSON within an invocation-owned version directory."""

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        newline="",
        prefix=f".{destination.name}.",
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


def _declares_cinematic(plan: object) -> bool:
    if not isinstance(plan, dict):
        return False
    cinematic = plan.get("cinematic_validation")
    return (
        isinstance(cinematic, dict)
        and cinematic.get("declared_mode") == "cinematic"
    )


def _build_handoffs(
    plan: dict[str, Any],
    version_dir: Path,
    ffmpeg_path: str,
    *,
    compile_commands: bool = True,
) -> list[dict[str, Any]]:
    command_deliveries: list[dict[str, Any]] = []
    exchange_blockers: dict[str, list[str]] = {"otio": [], "fcpxml": []}
    try:
        if _declares_cinematic(plan):
            cinematic_report = cinematic_report_payload(plan)
            _write_json_exclusive(
                version_dir / "cinematic_quality_report.json",
                cinematic_report,
            )
            _write_exclusive_bytes(
                version_dir / "cinematic_quality_report.md",
                cinematic_report_markdown(cinematic_report).encode("utf-8"),
            )
        for timeline in plan["timelines"]:
            slug = _timeline_slug(timeline)
            write_construction_markdown(
                plan, timeline, version_dir / f"edit_construction_{slug}.md"
            )
            write_construction_csv(
                plan, timeline, version_dir / f"edit_construction_{slug}.csv"
            )
            write_srt(plan, timeline, version_dir / f"subtitles_{slug}.srt")
            for adapter_name, writer, suffix in (
                ("otio", write_otio, "otio"),
                ("fcpxml", write_fcpxml, "fcpxml"),
            ):
                try:
                    writer(plan, timeline, version_dir / f"timeline_{slug}.{suffix}")
                except AdapterError as exc:
                    if compile_commands:
                        raise
                    exchange_blockers[adapter_name].append(str(exc))

            delivery = _delivery_for_timeline(plan, timeline.get("timeline_id"))
            command_deliveries.append(
                {
                    "delivery_id": delivery.get("delivery_id"),
                    "timeline_id": timeline.get("timeline_id"),
                    "version_role": delivery.get("version_role"),
                    "stages": _tier_stages(delivery.get("version_role")),
                    "requirements": _tier_requirements(plan, timeline, delivery),
                    "commands": (
                        ffmpeg_command_plan(
                            plan,
                            timeline,
                            version_dir,
                            delivery,
                            ffmpeg_path=ffmpeg_path,
                        )
                        if compile_commands
                        else []
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
        for adapter_name, blockers in exchange_blockers.items():
            if blockers:
                reports[adapter_name] = {
                    "status": "blocked",
                    "reason": blockers[0],
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
            _write_json_exclusive(
                version_dir / "ai_editor_plan.json",
                ai_editor_plan_payload(plan),
            )
            reports["ai_editor"] = {
                "status": "strict_json_handoff",
                "artifact": "ai_editor_plan.json",
            }
        _write_json_exclusive(
            version_dir / "ffmpeg_commands.json",
            {"schema_version": 1, "deliveries": command_deliveries},
        )
        _write_json_exclusive(version_dir / "adapter_reports.json", reports)
    except (AdapterError, KeyError, TypeError) as exc:
        raise BuildError(str(exc)) from None
    return command_deliveries


def _resolved_path(value: object, base_dir: Path, label: str) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise BuildError(f"{label} must be a non-empty path")
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = base_dir / candidate
    try:
        return candidate.resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"could not resolve {label}: {exc}") from None


def _path_inside(candidate: Path, roots: list[Path]) -> bool:
    for root in roots:
        try:
            candidate.relative_to(root)
        except ValueError:
            continue
        return True
    return False


def _referenced_media_ids(plan: dict[str, Any]) -> set[str]:
    referenced: set[str] = set()
    audio_cue_ids: set[str] = set()
    for timeline in plan["timelines"]:
        for unit in _active_units(timeline):
            asset_id = unit.get("asset_id")
            if isinstance(asset_id, str):
                referenced.add(asset_id)
            for cue_id in unit.get("audio_cue_ids", []):
                if isinstance(cue_id, str):
                    audio_cue_ids.add(cue_id)
    for track in plan["audio_tracks"]:
        for cue in track.get("cues", []):
            if cue.get("audio_cue_id") in audio_cue_ids:
                asset_id = cue.get("asset_id")
                if isinstance(asset_id, str):
                    referenced.add(asset_id)
    for item in plan["look_plan"].get("ffmpeg_filters", []):
        if isinstance(item, dict) and isinstance(item.get("params"), dict):
            asset_id = item["params"].get("asset_id")
            if isinstance(asset_id, str):
                referenced.add(asset_id)
    return referenced


def _absolute_without_resolving(path: Path, base_dir: Path) -> Path:
    candidate = path if path.is_absolute() else base_dir / path
    return Path(os.path.abspath(candidate))


def _path_is_link_or_junction(path: Path, mode: int) -> bool:
    if stat.S_ISLNK(mode):
        return True
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction is not None and is_junction())


def _reject_link_chain(path: Path, label: str) -> None:
    parts = path.parts
    if not parts:
        raise BuildError(f"{label} is not a filesystem path")
    current = Path(parts[0])
    for part in parts[1:]:
        current /= part
        try:
            metadata = os.lstat(current)
        except FileNotFoundError:
            # Let the leaf check report the stable regular-file contract. A
            # missing component is still safely blocked; it simply cannot be
            # inspected for links any further down the chain.
            return
        except OSError as exc:
            raise BuildError(f"could not inspect {label}: {exc}") from None
        if _path_is_link_or_junction(current, metadata.st_mode):
            raise BuildError(f"{label} must not use a symbolic link or junction")


def _file_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_size,
        metadata.st_mtime_ns,
    )


def _capture_input_guard(
    path_value: object,
    base_dir: Path,
    roots: list[Path],
    label: str,
) -> tuple[Path, dict[str, Any]]:
    if not isinstance(path_value, str) or not path_value.strip():
        raise BuildError(f"{label} must be a non-empty path")
    declared = _absolute_without_resolving(Path(path_value), base_dir)
    _reject_link_chain(declared, label)
    try:
        leaf = os.lstat(declared)
    except FileNotFoundError:
        raise BuildError(f"{label} must exist as a regular file") from None
    except OSError as exc:
        raise BuildError(f"could not inspect {label}: {exc}") from None
    if _path_is_link_or_junction(declared, leaf.st_mode):
        raise BuildError(f"{label} must not be a symbolic link or junction")
    if not stat.S_ISREG(leaf.st_mode):
        raise BuildError(f"{label} must exist as a regular file")
    try:
        canonical = declared.resolve(strict=True)
        metadata = os.stat(canonical, follow_symlinks=False)
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"could not resolve {label}: {exc}") from None
    if not _path_inside(canonical, roots):
        raise BuildError(f"{label} is outside authorized media roots")
    return canonical, {
        "label": label,
        "declared_path": declared,
        "canonical_path": canonical,
        "authorized_roots": tuple(roots),
        "identity": _file_identity(metadata),
    }


def _revalidate_input_guards(input_guards: list[dict[str, Any]]) -> None:
    for guard in input_guards:
        label = guard["label"]
        declared = guard["declared_path"]
        _reject_link_chain(declared, label)
        try:
            leaf = os.lstat(declared)
        except FileNotFoundError:
            raise BuildError(f"{label} must remain a regular file") from None
        except OSError as exc:
            raise BuildError(f"could not inspect {label}: {exc}") from None
        if _path_is_link_or_junction(declared, leaf.st_mode):
            raise BuildError(f"{label} must not be a symbolic link or junction")
        if not stat.S_ISREG(leaf.st_mode):
            raise BuildError(f"{label} must remain a regular file")
        try:
            canonical = declared.resolve(strict=True)
            metadata = os.stat(canonical, follow_symlinks=False)
        except (OSError, RuntimeError, TypeError, ValueError) as exc:
            raise BuildError(f"could not revalidate {label}: {exc}") from None
        if canonical != guard["canonical_path"] or _file_identity(metadata) != guard[
            "identity"
        ]:
            raise BuildError(f"{label} input identity changed after preflight")
        if not _path_inside(canonical, list(guard["authorized_roots"])):
            raise BuildError(f"{label} moved outside authorized media roots")


def _prepare_execution_plan(
    plan: dict[str, Any], plan_path: Path
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Resolve command inputs against the plan without mutating its Canon copy."""

    try:
        base_dir = Path(plan_path).resolve().parent
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"could not resolve edit plan directory: {exc}") from None
    prepared = copy.deepcopy(plan)
    execution = prepared["execution"]
    roots = [
        _resolved_path(value, base_dir, "authorized media root")
        for value in execution["authorized_media_roots"]
    ]
    if not roots:
        raise BuildError("authorized media roots must not be empty")
    execution["authorized_media_roots"] = [str(root) for root in roots]
    referenced = _referenced_media_ids(prepared)
    input_guards: list[dict[str, Any]] = []
    for binding in prepared["media_bindings"]:
        asset_id = binding.get("asset_id")
        source_type = binding.get("source_type")
        active_local = (
            source_type == "local_file" and binding.get("runtime_role") == "active"
        )
        consumed = isinstance(asset_id, str) and asset_id in referenced
        if not (active_local or consumed):
            continue
        if source_type == "provider_result":
            raise BuildError(
                f"provider result asset {asset_id} must be rebound to an authorized local file"
            )
        if source_type not in {"local_file", "post_asset", "generated_placeholder"}:
            raise BuildError(f"asset {asset_id} is not executable local media")
        media_path, guard = _capture_input_guard(
            binding.get("path_or_uri"),
            base_dir,
            roots,
            f"asset {asset_id}",
        )
        input_guards.append(guard)
        binding["path_or_uri"] = str(media_path)
    return prepared, input_guards


def _bind_authorized_version(
    plan: dict[str, Any], plan_path: Path, version_dir: Path
) -> None:
    try:
        base_dir = Path(plan_path).resolve().parent
        actual = Path(version_dir).resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"could not resolve authorized version directory: {exc}") from None
    execution = plan["execution"]
    expected_root = _resolved_path(
        execution.get("output_root"), base_dir, "authorized output root"
    )
    expected_version = _resolved_path(
        execution.get("authorized_version_directory"),
        base_dir,
        "authorized version directory",
    )
    if actual.parent != expected_root or actual != expected_version:
        raise BuildError(
            "authorized version directory does not match the actual new version directory"
        )


def _tier_blocker(
    plan: dict[str, Any], timeline: dict[str, Any], delivery: dict[str, Any]
) -> str | None:
    role = delivery.get("version_role")
    units = _active_units(timeline)
    assets = {item.get("asset_id"): item for item in plan["media_bindings"]}
    if role == "rough_cut":
        return None
    if role not in {"fine_cut", "final_master"}:
        return f"unsupported delivery tier {role}"
    used = [assets.get(unit.get("asset_id")) for unit in units]
    if any(
        binding is None
        or binding.get("source_type") == "generated_placeholder"
        or binding.get("file_status") == "placeholder"
        for binding in used
    ):
        return f"{role} does not permit placeholder media"
    for unit in units:
        if unit.get("approval_status") != "approved":
            return f"{role} requires approved selected takes and cut points"
        if not isinstance(unit.get("reframe"), str) or not unit["reframe"].strip():
            return f"{role} requires reframe instructions"
    try:
        requirements = _tier_requirements(plan, timeline, delivery)
    except BuildError as exc:
        return str(exc)
    if not requirements.get("text_cues") or not requirements.get("audio_cues"):
        return f"{role} requires text and audio instructions"
    if role == "final_master":
        if any(binding.get("rights_status") != "cleared" for binding in used):
            return "final_master requires cleared media rights"
        if plan["look_plan"].get("matching_status") != "passed":
            return "final_master requires passed look matching"
        mounted_text_ids = set(timeline["text_track_refs"])
        if any(
            track.get("safe_area_status") != "passed"
            for track in plan["text_tracks"]
            if track.get("text_track_id") in mounted_text_ids
        ):
            return "final_master requires passed subtitle safe area"
        mounted_audio_ids = set(timeline["audio_track_refs"])
        if any(
            track.get("rights_status") != "cleared"
            for track in plan["audio_tracks"]
            if track.get("audio_track_id") in mounted_audio_ids
        ):
            return "final_master requires cleared final audio rights"
    return None


def _replace_command_plans(
    plan: dict[str, Any],
    plan_path: Path,
    version_dir: Path,
    command_deliveries: list[dict[str, Any]],
    ffmpeg_path: str,
) -> None:
    try:
        plan_base_dir = Path(plan_path).resolve().parent
        resolved_version = version_dir.resolve()
    except (OSError, RuntimeError, TypeError, ValueError) as exc:
        raise BuildError(f"could not resolve delivery output paths: {exc}") from None
    timelines = {item.get("timeline_id"): item for item in plan["timelines"]}
    deliveries = {item.get("delivery_id"): item for item in plan["delivery_specs"]}
    for compiled in command_deliveries:
        delivery = deliveries[compiled["delivery_id"]]
        if delivery.get("ready") is not True:
            compiled["commands"] = []
            compiled["execution_status"] = "not_ready"
            continue
        try:
            declared_output = _resolved_path(
                delivery.get("destination"),
                plan_base_dir,
                f"delivery {delivery.get('delivery_id')} destination",
            )
            filename_output = _resolved_path(
                delivery.get("filename"),
                resolved_version,
                f"delivery {delivery.get('delivery_id')} filename",
            )
            declared_output.relative_to(resolved_version)
        except (BuildError, ValueError) as exc:
            compiled["commands"] = []
            compiled["blocker"] = str(exc)
            compiled["execution_status"] = "blocked"
            continue
        if declared_output != filename_output:
            compiled["commands"] = []
            compiled["blocker"] = (
                f"delivery {delivery.get('delivery_id')} destination and filename "
                "do not identify the same actual output"
            )
            compiled["execution_status"] = "blocked"
            continue
        compiled["expected_output_path"] = str(declared_output)
        compiled["expected_output_ref"] = delivery["destination"]
        timeline = timelines[compiled["timeline_id"]]
        blocker = _tier_blocker(plan, timeline, delivery)
        if blocker is not None:
            compiled["commands"] = []
            compiled["blocker"] = blocker
            compiled["execution_status"] = "blocked"
            continue
        try:
            compiled["commands"] = ffmpeg_command_plan(
                plan,
                timeline,
                version_dir,
                delivery,
                ffmpeg_path=ffmpeg_path,
            )
            if Path(compiled["commands"][-1][-1]).resolve() != declared_output:
                compiled["commands"] = []
                compiled["blocker"] = (
                    f"delivery {delivery.get('delivery_id')} command output does "
                    "not match its canonical expected output"
                )
                compiled["execution_status"] = "blocked"
        except AdapterError as exc:
            compiled["commands"] = []
            compiled["blocker"] = str(exc)
            compiled["execution_status"] = "blocked"


def _update_ffmpeg_adapter_report(
    version_dir: Path, command_deliveries: list[dict[str, Any]]
) -> None:
    blockers = [
        item["blocker"] for item in command_deliveries if item.get("blocker")
    ]
    if not blockers:
        return
    report_path = version_dir / "adapter_reports.json"
    try:
        reports = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise BuildError(f"could not update adapter reports: {exc}") from None
    reports["ffmpeg"] = {"status": "blocked", "reason": blockers[0]}
    _replace_owned_json(report_path, reports)


def _write_exclusive_bytes(destination: Path, content: bytes) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination.open("xb") as output:
            output.write(content)
    except FileExistsError:
        raise BuildError(f"artifact already exists: {destination}") from None


def _materialize_delivery_inputs(
    version_dir: Path,
    commands: list[list[str]],
    delivery: dict[str, Any],
    timeline: dict[str, Any],
) -> None:
    concat_index = next(
        (
            index
            for index, args in enumerate(commands)
            if "-f" in args
            and args[args.index("-f") + 1] == "concat"
        ),
        None,
    )
    if concat_index is None:
        raise BuildError("FFmpeg command plan is missing concat assembly")
    segment_paths = [Path(args[-1]).resolve() for args in commands[:concat_index]]
    for segment in segment_paths:
        try:
            segment.relative_to(version_dir.resolve())
        except (OSError, RuntimeError, ValueError):
            raise BuildError("FFmpeg segment output escapes version directory") from None
        segment.parent.mkdir(parents=True, exist_ok=True)
    concat_command = commands[concat_index]
    concat_path = Path(concat_command[concat_command.index("-i") + 1]).resolve()
    try:
        concat_path.relative_to(version_dir.resolve())
    except (OSError, RuntimeError, ValueError):
        raise BuildError("FFmpeg concat input escapes version directory") from None
    lines = ["file '" + str(path).replace("'", "'\\''") + "'" for path in segment_paths]
    _write_exclusive_bytes(concat_path, ("\n".join(lines) + "\n").encode("utf-8"))

    if delivery.get("subtitle_mode") == "sidecar":
        slug = _timeline_slug(timeline)
        source = version_dir / f"subtitles_{slug}.srt"
        final_output = Path(commands[-1][-1])
        sidecar = final_output.with_suffix(".srt")
        if source.resolve() != sidecar.resolve():
            _write_exclusive_bytes(sidecar, source.read_bytes())


def _expected_command_output(args: list[str], version_dir: Path) -> Path:
    if not isinstance(args, list) or not args:
        raise BuildError("runner command must be a non-empty argument list")
    try:
        output = Path(args[-1]).resolve()
        output.relative_to(version_dir.resolve())
    except (OSError, RuntimeError, TypeError, ValueError):
        raise BuildError("all command outputs must remain inside version_dir") from None
    return output


def _verify_completed_output(expected_output: Path, version_dir: Path) -> None:
    try:
        metadata = os.lstat(expected_output)
    except OSError as exc:
        raise BuildError(f"expected output is missing: {expected_output}: {exc}") from None
    if _path_is_link_or_junction(expected_output, metadata.st_mode):
        raise BuildError(f"expected output must not be a symbolic link or junction: {expected_output}")
    if not stat.S_ISREG(metadata.st_mode):
        raise BuildError(f"expected output is not a regular file: {expected_output}")
    if metadata.st_nlink != 1:
        raise BuildError(f"expected output must not be a hard link: {expected_output}")
    try:
        actual = expected_output.resolve(strict=True)
        actual.relative_to(version_dir.resolve(strict=True))
    except (OSError, RuntimeError, TypeError, ValueError):
        raise BuildError("completed output escapes version_dir") from None
    if actual != expected_output:
        raise BuildError("completed output does not match its canonical expected file")


def _run_command(
    args: list[str],
    version_dir: Path,
    delivery_id: str,
    runner: Callable[..., subprocess.CompletedProcess],
    input_guards: list[dict[str, Any]],
) -> tuple[subprocess.CompletedProcess | None, dict[str, Any]]:
    try:
        _revalidate_input_guards(input_guards)
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
            "command": args,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "error": None,
        }
        return completed, record
    except Exception as exc:
        detail = str(exc) or type(exc).__name__
        return None, {
            "delivery_id": delivery_id,
            "args": args,
            "command": args,
            "returncode": None,
            "stdout": "",
            "stderr": detail,
            "error": detail,
        }


def _probe_blocker(
    payload: object, delivery: dict[str, Any], timeline: dict[str, Any]
) -> str | None:
    if not isinstance(payload, dict) or not isinstance(payload.get("streams"), list):
        return "ffprobe returned invalid JSON structure"
    if any(not isinstance(item, dict) for item in payload["streams"]):
        return "ffprobe returned invalid stream metadata"
    format_metadata = payload.get("format")
    if not isinstance(format_metadata, dict):
        return "ffprobe returned invalid format metadata"
    video = next(
        (item for item in payload["streams"] if item.get("codec_type") == "video"),
        None,
    )
    audio = next(
        (item for item in payload["streams"] if item.get("codec_type") == "audio"),
        None,
    )
    if not isinstance(video, dict):
        return "ffprobe output is missing a video stream"
    try:
        width_text, height_text = str(delivery["resolution"]).lower().split("x", 1)
        expected_width, expected_height = int(width_text), int(height_text)
        if (video.get("width"), video.get("height")) != (
            expected_width,
            expected_height,
        ):
            return "ffprobe resolution does not match delivery specification"
        actual_rate = Fraction(str(video.get("avg_frame_rate", "0")))
        expected_rate = Fraction(str(delivery["frame_rate"]))
        if actual_rate != expected_rate:
            return "ffprobe frame rate does not match delivery specification"
        raw_duration = format_metadata.get("duration")
        if raw_duration is None:
            raw_duration = video.get("duration")
        actual_duration = Decimal(str(raw_duration))
        expected_duration = Decimal(str(timeline["duration_seconds"]))
        tolerance = Decimal(expected_rate.denominator) / Decimal(
            expected_rate.numerator
        )
        if abs(actual_duration - expected_duration) > tolerance:
            return "ffprobe duration exceeds one-frame tolerance"
    except (InvalidOperation, ValueError, ZeroDivisionError, TypeError, KeyError):
        return "ffprobe returned invalid numeric metadata"
    if video.get("codec_name") != delivery.get("video_codec"):
        return "ffprobe video codec does not match delivery specification"
    audio_required = (
        delivery.get("version_role") in {"fine_cut", "final_master"}
        or delivery.get("audio_mode") == "final_mix"
    )
    if not isinstance(audio, dict):
        return "ffprobe output is missing an audio stream" if audio_required else None
    if audio.get("codec_name") != delivery.get("audio_codec"):
        return "ffprobe audio codec does not match delivery specification"
    try:
        sample_rate = int(audio.get("sample_rate"))
        channels = int(audio.get("channels"))
    except (TypeError, ValueError):
        return "ffprobe returned invalid audio metadata"
    if sample_rate != delivery.get("audio_sample_rate"):
        return "ffprobe sample rate does not match delivery specification"
    if channels != delivery.get("audio_channels"):
        return "ffprobe channels do not match delivery specification"
    return None


def _tool_evidence_blocker(
    plan: dict[str, Any], requested_tool: str, tool_name: str
) -> str | None:
    normalized_requested = os.path.normcase(os.path.normpath(requested_tool.strip()))
    verified = [
        item
        for item in plan["execution"].get("tool_evidence", [])
        if isinstance(item, dict) and item.get("status") == "verified"
    ]
    typed = [
        item
        for item in verified
        if isinstance(item.get("tool"), str)
        and os.path.normcase(item["tool"].strip()) == os.path.normcase(tool_name)
    ]
    if not typed:
        wrong_identity_matches_path = any(
            isinstance(item.get(field), str)
            and os.path.normcase(os.path.normpath(item[field].strip()))
            == normalized_requested
            for item in verified
            for field in ("path", "executable")
        )
        if wrong_identity_matches_path:
            return f"verified {tool_name} tool evidence tool must be {tool_name}"
        return f"verified {tool_name} tool evidence is required"

    requested_text = requested_tool.strip()
    standard_tool_only = (
        "/" not in requested_text
        and "\\" not in requested_text
        and not Path(requested_text).drive
        and requested_text.casefold() in {
            tool_name.casefold(),
            f"{tool_name}.exe".casefold(),
        }
    )
    saw_bound_path = False
    for item in typed:
        bound_values = [
            item.get(field)
            for field in ("path", "executable")
            if isinstance(item.get(field), str) and item.get(field).strip()
        ]
        if bound_values:
            saw_bound_path = True
            if any(
                os.path.normcase(os.path.normpath(value.strip()))
                == normalized_requested
                for value in bound_values
            ):
                return None
        elif standard_tool_only:
            return None
    if saw_bound_path:
        return (
            f"verified {tool_name} tool evidence does not match {requested_tool}"
        )
    return (
        f"verified {tool_name} tool evidence must bind path/executable to "
        f"{requested_tool}"
    )


def _mark_copied_plan(
    plan: dict[str, Any], execution_log: dict[str, Any]
) -> None:
    outputs_by_id = {
        item["delivery_id"]: item for item in execution_log["rendered_outputs"]
    }
    blocked = execution_log["status"] == "blocked"
    blocker = execution_log.get("blocker")
    for delivery in plan["delivery_specs"]:
        delivery_id = delivery["delivery_id"]
        if delivery_id in outputs_by_id:
            delivery["status"] = "rendered"
        elif blocked and delivery.get("ready") is True:
            delivery["status"] = "blocked"
    plan["execution"]["executed_commands"] = execution_log["commands"]
    tool_evidence = []
    probe_evidence = []
    canonical_outputs = []
    for output in execution_log["rendered_outputs"]:
        delivery_id = output["delivery_id"]
        tool_id = f"TOOL-{delivery_id}"
        probe_id = f"PROBE-{delivery_id}"
        tool_evidence.append(
            {
                "tool_evidence_id": tool_id,
                "tool": "ffmpeg",
                "path": output["ffmpeg_tool"],
                "status": "verified",
            }
        )
        if output.get("ffprobe_tool"):
            probe_tool_id = f"TOOL-FFPROBE-{delivery_id}"
            tool_evidence.append(
                {
                    "tool_evidence_id": probe_tool_id,
                    "tool": "ffprobe",
                    "path": output["ffprobe_tool"],
                    "status": "verified",
                }
            )
        probe_evidence.append(
            {
                "probe_evidence_id": probe_id,
                "delivery_id": delivery_id,
                "output_ref": output["output_ref"],
                "status": "passed",
                "probe_status": output["probe_status"],
                "tool_evidence_ref": (
                    probe_tool_id if output.get("ffprobe_tool") else tool_id
                ),
            }
        )
        canonical_outputs.append(
            {
                **output,
                "tool_evidence_ref": tool_id,
                "probe_evidence_ref": probe_id,
            }
        )
    plan["execution"]["tool_evidence"] = tool_evidence
    plan["execution"]["probe_evidence"] = probe_evidence
    plan["execution"]["rendered_outputs"] = canonical_outputs
    for step in plan["execution"].get("steps", []):
        if step.get("delivery_id") in outputs_by_id:
            step["status"] = "passed"
        elif blocked:
            step["status"] = "blocked"
    if blocked:
        plan["plan_status"] = "blocked"
        plan["edit_validation"]["ready"] = False
        plan["edit_validation"]["blocking_errors"] = [blocker or "execution blocked"]
    elif all(
        delivery.get("ready") is True and delivery.get("status") == "rendered"
        for delivery in plan["delivery_specs"]
    ):
        plan["plan_status"] = "rendered"
        plan["edit_validation"]["ready"] = True
        plan["edit_validation"]["blocking_errors"] = []
    for result in plan["edit_validation"]["per_delivery_results"]:
        delivery_id = result.get("delivery_id")
        if delivery_id in outputs_by_id:
            result["status"] = "passed"
            result["validation_status"] = "passed"
        elif blocked:
            result["status"] = "blocked"
            result["validation_status"] = "blocked"


def _execute_authorized(
    plan: dict[str, Any],
    version_dir: Path,
    command_deliveries: list[dict[str, Any]],
    ffmpeg_path: str,
    ffprobe_path: str | None,
    runner: Callable[..., subprocess.CompletedProcess],
    input_guards: list[dict[str, Any]],
) -> tuple[str, dict[str, Any]]:
    execution_log: dict[str, Any] = {
        "status": "running",
        "commands": [],
        "rendered_outputs": [],
    }
    delivery_specs = {
        item["delivery_id"]: item for item in plan["delivery_specs"]
    }
    timelines = {item["timeline_id"]: item for item in plan["timelines"]}
    selected = [
        item
        for item in command_deliveries
        if delivery_specs[item["delivery_id"]].get("ready") is True
    ]
    blocker = "no ready delivery was selected for execution" if not selected else None
    if blocker is None:
        blocker = next(
            (item.get("blocker") for item in selected if item.get("blocker")),
            None,
        )
    if blocker is None:
        blocker = _tool_evidence_blocker(plan, ffmpeg_path, "ffmpeg")
    if blocker is None and any(
        delivery_specs[item["delivery_id"]].get("version_role")
        in {"fine_cut", "final_master"}
        for item in selected
    ) and (ffprobe_path is None or not str(ffprobe_path).strip()):
        blocker = "ffprobe is required for fine_cut and final_master execution"
    if (
        blocker is None
        and ffprobe_path is not None
        and str(ffprobe_path).strip()
    ):
        blocker = _tool_evidence_blocker(
            plan, str(ffprobe_path), "ffprobe"
        )
    if blocker is not None:
        execution_log["status"] = "blocked"
        execution_log["blocker"] = blocker
        _mark_copied_plan(plan, execution_log)
        return "blocked", execution_log

    for compiled in selected:
        delivery_id = compiled["delivery_id"]
        delivery = delivery_specs[delivery_id]
        timeline = timelines[compiled["timeline_id"]]
        commands = compiled["commands"]
        _materialize_delivery_inputs(version_dir, commands, delivery, timeline)
        delivery_blocker = None
        for args in commands:
            expected_output = _expected_command_output(args, version_dir)
            completed, record = _run_command(
                args, version_dir, delivery_id, runner, input_guards
            )
            execution_log["commands"].append(record)
            if completed is None or completed.returncode != 0:
                delivery_blocker = (
                    record["stderr"] or f"command failed with {record['returncode']}"
                )
                break
            try:
                _verify_completed_output(expected_output, version_dir)
            except BuildError as exc:
                detail = str(exc)
                record["stderr"] = (
                    (record["stderr"] + "\n").lstrip("\n") + detail
                )
                record["error"] = detail
                delivery_blocker = detail
                break
        if delivery_blocker is not None:
            execution_log["status"] = "blocked"
            execution_log["blocker"] = delivery_blocker
            break

        final_output = Path(compiled["expected_output_path"])
        probe_status = "unverified"
        if ffprobe_path is not None and str(ffprobe_path).strip():
            probe_args = [
                str(ffprobe_path),
                "-v",
                "error",
                "-show_streams",
                "-show_format",
                "-of",
                "json",
                str(final_output),
            ]
            completed, record = _run_command(
                probe_args, version_dir, delivery_id, runner, input_guards
            )
            record["tool"] = "ffprobe"
            execution_log["commands"].append(record)
            if completed is None or completed.returncode != 0:
                delivery_blocker = record["stderr"] or "ffprobe command failed"
            else:
                try:
                    probe_payload = json.loads(completed.stdout)
                except (TypeError, ValueError, RecursionError):
                    delivery_blocker = "ffprobe returned invalid JSON"
                else:
                    delivery_blocker = _probe_blocker(
                        probe_payload, delivery, timeline
                    )
            if delivery_blocker is not None:
                execution_log["status"] = "blocked"
                execution_log["blocker"] = delivery_blocker
                break
            probe_status = "passed"
        execution_log["rendered_outputs"].append(
            {
                "delivery_id": delivery_id,
                "output_ref": compiled["expected_output_ref"],
                "actual_output_path": str(final_output),
                "ffmpeg_tool": ffmpeg_path,
                "ffprobe_tool": (
                    str(ffprobe_path)
                    if ffprobe_path is not None and str(ffprobe_path).strip()
                    else None
                ),
                "status": "rendered",
                "tool_status": "passed",
                "probe_status": probe_status,
            }
        )

    if execution_log["status"] == "running":
        execution_log["status"] = "rendered"
    _mark_copied_plan(plan, execution_log)
    return execution_log["status"], execution_log


def _read_terminal_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        detail = str(exc) or type(exc).__name__
        raise BuildError(f"could not confirm {label} terminal state: {detail}") from None
    if not isinstance(value, dict):
        raise BuildError(f"could not confirm {label} terminal state: expected object")
    return value


def _confirm_execution_terminal_state(version_dir: Path, expected: str) -> None:
    if expected not in {"rendered", "blocked"}:
        raise BuildError(f"invalid execution terminal status: {expected}")
    manifest = _read_terminal_json(
        version_dir / "bundle_manifest.json", "bundle manifest"
    )
    execution_log = _read_terminal_json(
        version_dir / "execution_log.json", "execution log"
    )
    copied_plan = _read_terminal_json(
        version_dir / "edit_master_plan.json", "copied plan"
    )
    observed = (
        manifest.get("status"),
        execution_log.get("status"),
        copied_plan.get("plan_status"),
    )
    required = (expected, expected, expected)
    if observed != required:
        raise BuildError(
            "could not confirm consistent execution terminal state: "
            f"expected {required}, observed {observed}"
        )


def _publish_execution_state(
    plan: dict[str, Any],
    execution_log: dict[str, Any],
    version_dir: Path,
    manifest: dict[str, Any],
) -> str:
    """Publish one recoverable execution state using atomic per-file replacement."""

    manifest_path = version_dir / "bundle_manifest.json"
    log_path = version_dir / "execution_log.json"
    plan_path = version_dir / "edit_master_plan.json"
    final_status = execution_log["status"]
    publishing_manifest = {
        **manifest,
        "status": "publishing",
        "rendered_outputs": execution_log["rendered_outputs"],
        "artifacts": _artifact_names(version_dir),
    }
    try:
        _atomic_replace_json(manifest_path, publishing_manifest)
        _atomic_replace_json(log_path, execution_log)
        _atomic_replace_json(plan_path, plan)
        final_manifest = {
            **publishing_manifest,
            "status": final_status,
            "artifacts": _artifact_names(version_dir),
        }
        _atomic_replace_json(manifest_path, final_manifest)
        _confirm_execution_terminal_state(version_dir, final_status)
        return final_status
    except Exception as exc:
        detail = str(exc) or type(exc).__name__
        publish_error = f"execution state publish failed: {detail}"
        execution_log["status"] = "blocked"
        execution_log["blocker"] = publish_error
        execution_log["publish_error"] = detail
        _mark_copied_plan(plan, execution_log)
        blocked_manifest = {
            **manifest,
            "status": "blocked",
            "rendered_outputs": execution_log["rendered_outputs"],
            "publish_error": detail,
        }
        for destination, value in (
            (plan_path, plan),
            (log_path, execution_log),
        ):
            try:
                _atomic_replace_json(destination, value)
            except Exception:
                pass
        blocked_manifest["artifacts"] = _artifact_names(version_dir)
        try:
            _atomic_replace_json(manifest_path, blocked_manifest)
        except Exception:
            pass
        try:
            _confirm_execution_terminal_state(version_dir, "blocked")
        except BuildError as terminal_exc:
            raise BuildError(
                f"{publish_error}; terminal state could not be confirmed: "
                f"{terminal_exc}"
            ) from None
        return "blocked"


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
    plan_path: Path | None = None,
    execute: bool = False,
    ffmpeg_path: str | None = None,
    ffprobe_path: str | None = None,
    runner: Callable[..., subprocess.CompletedProcess] = subprocess.run,
) -> Path:
    require_cinematic = _declares_cinematic(plan)
    errors = validate_edit_plan(plan, require_cinematic=require_cinematic)
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
    if execute:
        execution_errors = validate_edit_plan(
            plan,
            for_execution=True,
            require_cinematic=require_cinematic,
        )
        if execution_errors:
            raise BuildError("\n".join(execution_errors))
        if plan_path is None:
            raise BuildError("plan_path is required for authorized execution")

    version_dir = _create_version_dir(Path(output_root))
    try:
        _write_json_exclusive(version_dir / "edit_master_plan.json", plan)
        command_deliveries = _build_handoffs(
            plan,
            version_dir,
            ffmpeg_path or "ffmpeg",
            compile_commands=not execute,
        )
        manifest_path = version_dir / "bundle_manifest.json"
        manifest = _manifest(plan, version_dir, "dry_run_passed")
        _write_json_exclusive(manifest_path, manifest)

        if not execute:
            return version_dir
        if ffmpeg_path is None or not str(ffmpeg_path).strip():
            raise BuildError("ffmpeg is unavailable")

        _bind_authorized_version(plan, plan_path, version_dir)
        execution_plan, input_guards = _prepare_execution_plan(plan, plan_path)
        _replace_command_plans(
            execution_plan,
            plan_path,
            version_dir,
            command_deliveries,
            str(ffmpeg_path),
        )
        _update_ffmpeg_adapter_report(version_dir, command_deliveries)
        _replace_owned_json(
            version_dir / "ffmpeg_commands.json",
            {"schema_version": 1, "deliveries": command_deliveries},
        )
        status, execution_log = _execute_authorized(
            plan,
            version_dir,
            command_deliveries,
            str(ffmpeg_path),
            ffprobe_path,
            runner,
            input_guards,
        )
        status = _publish_execution_state(
            plan, execution_log, version_dir, manifest
        )
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
            plan_path=Path(plan_path),
            execute=execute,
            ffmpeg_path=ffmpeg_path,
            ffprobe_path=ffprobe_path,
            runner=runner,
        )
    except BuildError:
        raise
    except (OSError, RuntimeError, TypeError, ValueError, UnicodeError) as exc:
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
    status = manifest.get("status") if isinstance(manifest, dict) else None
    expected_status = "rendered" if args.execute else "dry_run_passed"
    if status != expected_status:
        print(
            f"ERROR: unexpected bundle status for this mode: {status!r}; "
            f"expected {expected_status!r}",
            file=sys.stderr,
        )
        return 1
    print(version_dir)
    print(f"Bundle status: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
