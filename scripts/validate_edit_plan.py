"""Validate a finished-film ``edit_master_plan`` JSON object."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from cinematic_validation import validate_cinematic_plan


MAX_JSON_INTEGER_DIGITS = 4300
MAX_PLAN_BYTES = 10 * 1024 * 1024

TOP_LEVEL_FIELDS = (
    "edit_plan_id",
    "plan_status",
    "source_package_id",
    "target_duration_seconds",
    "locked_event_ids",
    "media_bindings",
    "timelines",
    "audio_tracks",
    "text_tracks",
    "look_plan",
    "delivery_specs",
    "software_targets",
    "execution",
    "edit_validation",
)

OPTIONAL_TOP_LEVEL_FIELDS = ("cinematic_validation",)

PLAN_STATUSES = {"draft", "dry_run_passed", "authorized", "rendered", "blocked"}
DELIVERY_ROLES = {"rough_cut", "fine_cut", "final_master"}
DELIVERY_STATUSES = PLAN_STATUSES
ASPECTS = {"16:9", "9:16"}
BINDING_SCOPES = {"shot", "edit_unit", "timeline", "project"}
SOURCE_TYPES = {
    "local_file",
    "provider_result",
    "generated_placeholder",
    "post_asset",
}
SUBTITLE_MODES = {"none", "sidecar", "burn_in"}
AUDIO_MODES = {"temporary_or_silent", "final_mix", "none"}
LOOK_MODES = {"none", "approved"}
RENDER_BACKENDS = {
    "ffmpeg",
    "premiere",
    "resolve",
    "jianying_capcut",
    "ai_editor",
    "manual",
}
BACKEND_SOFTWARE_TARGETS = {
    "ffmpeg": "generic",
    "premiere": "premiere",
    "resolve": "resolve",
    "jianying_capcut": "jianying_capcut",
    "ai_editor": "ai_editor",
}
SUCCESS_EVIDENCE_STATUSES = {"passed", "verified", "success", "succeeded"}
EXECUTION_STEP_STATUSES = {"pending", "running", "passed", "failed", "blocked"}

MEDIA_FIELDS = (
    "asset_id",
    "binding_scope",
    "target_id",
    "source_type",
    "path_or_uri",
    "file_status",
    "rights_status",
    "probe_status",
    "selection_reason",
    "acceptance_status",
)

SHOT_MEDIA_FIELDS = (
    "shot_id",
    "take_id",
    "runtime_role",
    "duration_seconds",
    "frame_rate",
    "resolution",
    "audio_channels",
    "source_in_seconds",
    "source_out_seconds",
    "fallback_asset_id",
)

TIMELINE_FIELDS = (
    "timeline_id",
    "aspect_ratio",
    "resolution",
    "frame_rate",
    "duration_seconds",
    "video_tracks",
    "audio_track_refs",
    "text_track_refs",
    "export_refs",
)

EDIT_UNIT_FIELDS = (
    "edit_unit_id",
    "sequence",
    "shot_id",
    "asset_id",
    "timeline_in_seconds",
    "timeline_out_seconds",
    "duration_seconds",
    "source_in_seconds",
    "source_out_seconds",
    "story_function",
    "cut_reason",
    "transition_in",
    "transition_out",
    "speed",
    "freeze_frames",
    "stabilization",
    "reframe",
    "safe_area",
    "scale",
    "position",
    "opening_state",
    "closing_state",
    "continuity_ids",
    "locked_event_ids",
    "audio_cue_ids",
    "text_cue_ids",
    "look_instruction",
    "risk_triggers",
    "approval_status",
)

DELIVERY_FIELDS = (
    "delivery_id",
    "version_role",
    "version_id",
    "timeline_id",
    "status",
    "ready",
    "artifact_refs",
    "validation_refs",
    "change_summary",
    "aspect_ratio",
    "resolution",
    "frame_rate",
    "container",
    "video_codec",
    "audio_codec",
    "codec",
    "bitrate",
    "audio_sample_rate",
    "audio_channels",
    "filename",
    "destination",
    "subtitle_mode",
    "audio_mode",
    "look_mode",
    "render_backend",
)

EXECUTION_FIELDS = (
    "dry_run_status",
    "operation_authorization",
    "output_root",
    "version_policy",
    "dry_run_manifest_id",
    "version_directory",
    "authorized_manifest_id",
    "authorized_version_directory",
    "authorized_media_roots",
    "tool_evidence",
    "executed_commands",
    "rendered_outputs",
)

REVIEW_EVIDENCE_FIELDS = (
    "review_evidence_id",
    "delivery_id",
    "evidence_type",
    "artifact_ref",
    "status",
    "tool_evidence_ref",
)


def parse_bounded_json_int(value: str) -> int:
    """Keep JSON integer parsing deterministic across supported Python versions."""
    if len(value.lstrip("-")) > MAX_JSON_INTEGER_DIGITS:
        raise ValueError(
            f"integer literal exceeds {MAX_JSON_INTEGER_DIGITS} decimal digits"
        )
    return int(value)


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON number {value} is not allowed")


def _is_nonempty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _is_success_status(value: Any) -> bool:
    return isinstance(value, str) and value in SUCCESS_EVIDENCE_STATUSES


def _require_fields(
    value: dict[str, Any], fields: tuple[str, ...], label: str, errors: list[str]
) -> None:
    for field in fields:
        if field not in value:
            errors.append(f"{label}: missing required field {field}")


def _decimal(
    value: Any, *, positive: bool = False, nonnegative: bool = False
) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        converted = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    if not converted.is_finite():
        return None
    if positive and converted <= 0:
        return None
    if nonnegative and converted < 0:
        return None
    return converted


def _positive_number(
    value: Any, label: str, errors: list[str]
) -> Decimal | None:
    converted = _decimal(value, positive=True)
    if converted is None:
        errors.append(f"{label} must be a positive finite number")
    return converted


def _nonnegative_number(
    value: Any, label: str, errors: list[str]
) -> Decimal | None:
    converted = _decimal(value, nonnegative=True)
    if converted is None:
        errors.append(f"{label} must be a non-negative finite number")
    return converted


def _positive_integer(value: Any) -> int | None:
    converted = _decimal(value, positive=True)
    if converted is None or converted != converted.to_integral_value():
        return None
    return int(converted)


def _nonnegative_integer(value: Any) -> int | None:
    converted = _decimal(value, nonnegative=True)
    if converted is None or converted != converted.to_integral_value():
        return None
    return int(converted)


def _validate_id(value: Any, label: str, errors: list[str]) -> str | None:
    if not _is_nonempty_string(value):
        errors.append(f"{label} must be a non-empty string")
        return None
    return value


def _validate_string_list(
    value: Any,
    label: str,
    errors: list[str],
    *,
    nonempty: bool = False,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label}: expected list")
        return []
    if nonempty and not value:
        errors.append(f"{label}: must not be empty")
    valid: list[str] = []
    for index, item in enumerate(value, start=1):
        if not _is_nonempty_string(item):
            errors.append(f"{label} item {index}: must be a non-empty string")
        else:
            valid.append(item)
    return valid


def _validate_enum(
    value: Any,
    allowed: set[str],
    label: str,
    rendered_allowed: str,
    errors: list[str],
) -> None:
    if not isinstance(value, str) or value not in allowed:
        errors.append(f"{label} must be {rendered_allowed}")


def _list_field(plan: dict[str, Any], name: str, errors: list[str]) -> list[Any]:
    value = plan.get(name)
    if not isinstance(value, list):
        if name in plan:
            errors.append(f"{name}: expected list")
        return []
    return value


def _dict_field(plan: dict[str, Any], name: str, errors: list[str]) -> dict[str, Any]:
    value = plan.get(name)
    if not isinstance(value, dict):
        if name in plan:
            errors.append(f"{name}: expected object")
        return {}
    return value


def _lexical_path(
    value: Any, label: str, errors: list[str]
) -> tuple[str, PurePosixPath | PureWindowsPath] | None:
    if not _is_nonempty_string(value):
        errors.append(f"{label} must be a non-empty string")
        return None
    if any(ord(character) < 32 for character in value):
        errors.append(f"{label} must not contain NUL or control characters")
        return None
    windows_path = PureWindowsPath(value)
    if windows_path.drive and not windows_path.is_absolute():
        errors.append(f"{label} must not use a drive-relative path")
        return None
    if windows_path.is_absolute():
        style = "windows"
        parsed: PurePosixPath | PureWindowsPath = windows_path
    elif value.startswith("/"):
        style = "posix"
        parsed = PurePosixPath(value)
    else:
        style = "relative"
        parsed = PurePosixPath(value.replace("\\", "/"))
    if ".." in parsed.parts:
        errors.append(f"{label} must not contain '..' segments")
        return None
    return style, parsed


def _path_is_within(
    candidate: tuple[str, PurePosixPath | PureWindowsPath],
    root: tuple[str, PurePosixPath | PureWindowsPath],
    *,
    strict: bool,
) -> bool:
    candidate_style, candidate_path = candidate
    root_style, root_path = root
    if candidate_style != root_style:
        return False
    if candidate_style == "windows" and (
        candidate_path.drive.lower() != root_path.drive.lower()
    ):
        return False
    try:
        relative = candidate_path.relative_to(root_path)
    except ValueError:
        return False
    return not strict or relative != PurePosixPath(".") and str(relative) != "."


def _is_safe_lut_path(value: Any) -> bool:
    """Apply lexical checks only; render adapters must still escape filtergraphs."""
    if not _is_nonempty_string(value):
        return False
    if any(
        ord(character) < 32
        or ord(character) == 127
        or character in "'\";,[]="
        for character in value
    ):
        return False
    colon_positions = [
        index for index, character in enumerate(value) if character == ":"
    ]
    if colon_positions:
        windows_path = PureWindowsPath(value)
        windows_drive_colon = (
            colon_positions == [1]
            and value[0].isalpha()
            and windows_path.is_absolute()
        )
        if not windows_drive_colon:
            return False
    # Backslashes are path separators here, never general-purpose escapes.
    return True


def _validate_media_bindings(
    items: list[Any], errors: list[str]
) -> dict[str, dict[str, Any]]:
    assets: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"media_bindings item {index}: expected object")
            continue
        raw_asset_id = item.get("asset_id")
        label_id = raw_asset_id if _is_nonempty_string(raw_asset_id) else f"item-{index}"
        label = f"asset {label_id}"
        _require_fields(item, MEDIA_FIELDS, label, errors)
        asset_id = _validate_id(raw_asset_id, f"{label}: asset_id", errors)
        if asset_id is not None:
            if asset_id in assets:
                errors.append(f"media_bindings: duplicate asset_id {asset_id}")
            else:
                assets[asset_id] = item

        source_type = item.get("source_type")
        if not isinstance(source_type, str) or source_type not in SOURCE_TYPES:
            errors.append(
                f"{label}: source_type must be local_file, provider_result, "
                "generated_placeholder, or post_asset"
            )
        binding_scope = item.get("binding_scope")
        if not isinstance(binding_scope, str) or binding_scope not in BINDING_SCOPES:
            errors.append(
                f"{label}: binding_scope must be shot, edit_unit, timeline, or project"
            )
        _validate_id(item.get("target_id"), f"{label}: target_id", errors)
        for field in (
            "path_or_uri",
            "file_status",
            "rights_status",
            "probe_status",
            "selection_reason",
            "acceptance_status",
        ):
            if field in item:
                _validate_id(item.get(field), f"{label}: {field}", errors)

        if source_type == "post_asset":
            if (
                not isinstance(binding_scope, str)
                or binding_scope not in {"edit_unit", "timeline", "project"}
            ):
                errors.append(
                    f"{label}: post_asset binding_scope must be edit_unit, "
                    "timeline, or project"
                )
            continue

        _require_fields(item, SHOT_MEDIA_FIELDS, label, errors)
        shot_id = _validate_id(item.get("shot_id"), f"{label}: shot_id", errors)
        _validate_id(item.get("take_id"), f"{label}: take_id", errors)
        _validate_id(item.get("runtime_role"), f"{label}: runtime_role", errors)
        if binding_scope != "shot":
            errors.append(
                f"{label}: shot-derived media must use binding_scope shot"
            )
        if shot_id is not None and item.get("target_id") != shot_id:
            errors.append(f"{label}: target_id must equal shot_id")

        duration = None
        source_in = None
        source_out = None
        if "duration_seconds" in item:
            duration = _positive_number(
                item.get("duration_seconds"),
                f"{label}: duration_seconds",
                errors,
            )
        if "frame_rate" in item:
            _positive_number(item.get("frame_rate"), f"{label}: frame_rate", errors)
        if "resolution" in item:
            _validate_id(item.get("resolution"), f"{label}: resolution", errors)
        if "audio_channels" in item:
            channels = _nonnegative_integer(item.get("audio_channels"))
            if channels is None:
                errors.append(
                    f"{label}: audio_channels must be a non-negative integer"
                )
        if "source_in_seconds" in item:
            source_in = _nonnegative_number(
                item.get("source_in_seconds"),
                f"{label}: source_in_seconds",
                errors,
            )
        if "source_out_seconds" in item:
            source_out = _positive_number(
                item.get("source_out_seconds"),
                f"{label}: source_out_seconds",
                errors,
            )
        if source_in is not None and source_out is not None:
            if source_out <= source_in:
                errors.append(f"{label}: source range must have positive duration")
            if duration is not None and source_out > duration:
                errors.append(f"{label}: source range exceeds media duration")
    for asset_id, item in assets.items():
        fallback_id = item.get("fallback_asset_id")
        if fallback_id is not None:
            if not _is_nonempty_string(fallback_id):
                errors.append(
                    f"asset {asset_id}: fallback_asset_id must be null or a "
                    "non-empty string"
                )
            elif fallback_id not in assets:
                errors.append(
                    f"asset {asset_id}: unknown fallback_asset_id {fallback_id}"
                )
    return assets


def _validate_edit_unit(
    item: Any,
    item_index: int,
    assets: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[dict[str, Any] | None, dict[str, Decimal | int | None]]:
    numbers: dict[str, Decimal | int | None] = {
        "sequence": None,
        "timeline_in": None,
        "timeline_out": None,
        "duration": None,
        "source_in": None,
        "source_out": None,
        "speed": None,
    }
    if not isinstance(item, dict):
        errors.append(f"edit unit item {item_index}: expected object")
        return None, numbers
    raw_id = item.get("edit_unit_id")
    unit_id = raw_id if _is_nonempty_string(raw_id) else f"item-{item_index}"
    label = f"edit unit {unit_id}"
    _require_fields(item, EDIT_UNIT_FIELDS, label, errors)
    _validate_id(raw_id, f"{label}: edit_unit_id", errors)
    _validate_id(item.get("shot_id"), f"{label}: shot_id", errors)
    asset_id = _validate_id(item.get("asset_id"), f"{label}: asset_id", errors)
    if asset_id is not None and asset_id not in assets:
        errors.append(f"{label}: unknown asset_id {asset_id}")

    if "sequence" in item:
        sequence = _positive_integer(item.get("sequence"))
        numbers["sequence"] = sequence
        if sequence is None:
            errors.append(f"{label}: sequence must be a positive integer")
    numeric_specs = (
        ("timeline_in_seconds", "timeline_in", False),
        ("timeline_out_seconds", "timeline_out", True),
        ("duration_seconds", "duration", True),
        ("source_in_seconds", "source_in", False),
        ("source_out_seconds", "source_out", True),
        ("speed", "speed", True),
    )
    for field, result_name, positive in numeric_specs:
        if field not in item:
            continue
        if positive:
            numbers[result_name] = _positive_number(
                item.get(field), f"{label}: {field}", errors
            )
        else:
            numbers[result_name] = _nonnegative_number(
                item.get(field), f"{label}: {field}", errors
            )
    if "freeze_frames" in item and _nonnegative_integer(
        item.get("freeze_frames")
    ) is None:
        errors.append(f"{label}: freeze_frames must be a non-negative integer")
    if "scale" in item:
        _positive_number(item.get("scale"), f"{label}: scale", errors)
    position = item.get("position")
    if "position" in item:
        if not isinstance(position, dict):
            errors.append(f"{label}: position must be an object")
        else:
            for axis in ("x", "y"):
                if axis not in position or _decimal(position.get(axis)) is None:
                    errors.append(
                        f"{label}: position.{axis} must be a finite number"
                    )

    for field in (
        "story_function",
        "cut_reason",
        "transition_in",
        "transition_out",
        "stabilization",
        "reframe",
        "safe_area",
        "opening_state",
        "closing_state",
        "look_instruction",
        "approval_status",
    ):
        if field in item:
            _validate_id(item.get(field), f"{label}: {field}", errors)
    for field in (
        "continuity_ids",
        "locked_event_ids",
        "audio_cue_ids",
        "text_cue_ids",
    ):
        if field in item:
            _validate_string_list(item.get(field), f"{label}.{field}", errors)
    if "risk_triggers" in item and not isinstance(item.get("risk_triggers"), list):
        errors.append(f"{label}.risk_triggers: expected list")

    timeline_in = numbers["timeline_in"]
    timeline_out = numbers["timeline_out"]
    duration = numbers["duration"]
    source_in = numbers["source_in"]
    source_out = numbers["source_out"]
    speed = numbers["speed"]
    if (
        isinstance(timeline_in, Decimal)
        and isinstance(timeline_out, Decimal)
        and isinstance(duration, Decimal)
        and timeline_out - timeline_in != duration
    ):
        errors.append(f"{label}: timeline range must equal duration_seconds")
    if (
        isinstance(source_in, Decimal)
        and isinstance(source_out, Decimal)
        and isinstance(duration, Decimal)
        and isinstance(speed, Decimal)
        and source_out - source_in != duration * speed
    ):
        errors.append(f"{label}: source range must equal duration times speed")
    if asset_id in assets and isinstance(source_out, Decimal):
        media_duration = _decimal(assets[asset_id].get("duration_seconds"), positive=True)
        if media_duration is not None and source_out > media_duration:
            errors.append(f"{label}: source range exceeds asset {asset_id} duration")
    return item, numbers


def _validate_timelines(
    items: list[Any],
    assets: dict[str, dict[str, Any]],
    target_duration: Decimal | None,
    locked_event_ids: list[str],
    errors: list[str],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, list[dict[str, Any]]],
]:
    timelines: dict[str, dict[str, Any]] = {}
    active_units: dict[str, list[dict[str, Any]]] = {}
    aspect_owner: dict[str, str] = {}
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"timelines item {index}: expected object")
            continue
        raw_id = item.get("timeline_id")
        timeline_id = raw_id if _is_nonempty_string(raw_id) else f"item-{index}"
        label = f"timeline {timeline_id}"
        _require_fields(item, TIMELINE_FIELDS, label, errors)
        valid_id = _validate_id(raw_id, f"{label}: timeline_id", errors)
        if valid_id is not None:
            if valid_id in timelines:
                errors.append(f"timelines: duplicate timeline_id {valid_id}")
            else:
                timelines[valid_id] = item

        aspect = item.get("aspect_ratio")
        if not isinstance(aspect, str) or aspect not in ASPECTS:
            errors.append(f"{label}: aspect_ratio must be 16:9 or 9:16")
        elif aspect in aspect_owner:
            errors.append(f"timelines: duplicate aspect_ratio {aspect}")
        else:
            aspect_owner[aspect] = timeline_id
        if "resolution" in item:
            _validate_id(item.get("resolution"), f"{label}: resolution", errors)
        if "frame_rate" in item:
            _positive_number(item.get("frame_rate"), f"{label}: frame_rate", errors)
        timeline_duration = None
        if "duration_seconds" in item:
            timeline_duration = _positive_number(
                item.get("duration_seconds"), f"{label}: duration_seconds", errors
            )
            if (
                timeline_duration is not None
                and target_duration is not None
                and timeline_duration != target_duration
            ):
                errors.append(
                    f"{label}: duration_seconds must equal target duration"
                )

        video_tracks = item.get("video_tracks")
        if not isinstance(video_tracks, list):
            if "video_tracks" in item:
                errors.append(f"{label}.video_tracks: expected list")
            video_tracks = []
        selected_tracks = [
            track
            for track in video_tracks
            if isinstance(track, dict)
            and track.get("track_id") == "V1"
            and track.get("runtime_role") == "active"
            and track.get("release_role") == "first_release"
        ]
        if len(selected_tracks) != 1:
            errors.append(
                f"{label}: expected exactly one V1 active first_release track"
            )
        track = selected_tracks[0] if selected_tracks else None
        raw_units = track.get("edit_units") if isinstance(track, dict) else []
        if not isinstance(raw_units, list):
            errors.append(f"{label}.V1.edit_units: expected list")
            raw_units = []

        validated: list[
            tuple[dict[str, Any], dict[str, Decimal | int | None], int]
        ] = []
        unit_ids: set[str] = set()
        for unit_index, raw_unit in enumerate(raw_units, start=1):
            unit, numbers = _validate_edit_unit(
                raw_unit, unit_index, assets, errors
            )
            if unit is None:
                continue
            unit_id = unit.get("edit_unit_id")
            if _is_nonempty_string(unit_id):
                if unit_id in unit_ids:
                    errors.append(f"{label}: duplicate edit_unit_id {unit_id}")
                unit_ids.add(unit_id)
            sequence_value = numbers["sequence"]
            sort_sequence = sequence_value if isinstance(sequence_value, int) else 10**9
            validated.append((unit, numbers, sort_sequence))
        validated.sort(key=lambda entry: (entry[2], raw_units.index(entry[0])))
        sequences = [entry[1]["sequence"] for entry in validated]
        if sequences != list(range(1, len(validated) + 1)):
            errors.append(f"{label}: V1 sequence must be contiguous from 1")

        flattened_events: list[str] = []
        previous_out = Decimal(0)
        previous_closing: Any = None
        final_out: Decimal | None = None
        ordered_units: list[dict[str, Any]] = []
        for unit, numbers, _ in validated:
            ordered_units.append(unit)
            unit_id = unit.get("edit_unit_id")
            unit_label = unit_id if _is_nonempty_string(unit_id) else "unknown"
            timeline_in = numbers["timeline_in"]
            timeline_out = numbers["timeline_out"]
            if isinstance(timeline_in, Decimal):
                if timeline_in > previous_out:
                    errors.append(f"{label}: gap before {unit_label}")
                elif timeline_in < previous_out:
                    errors.append(f"{label}: overlap before {unit_label}")
            if isinstance(timeline_out, Decimal):
                previous_out = timeline_out
                final_out = timeline_out
            opening = unit.get("opening_state")
            if previous_closing is not None and opening != previous_closing:
                errors.append(f"{label}: continuity state mismatch before {unit_label}")
            previous_closing = unit.get("closing_state")
            unit_events = unit.get("locked_event_ids")
            if isinstance(unit_events, list):
                flattened_events.extend(
                    event for event in unit_events if _is_nonempty_string(event)
                )
        if flattened_events != locked_event_ids:
            errors.append(f"{label}: locked events are missing or reordered")
        if (
            final_out is not None
            and target_duration is not None
            and final_out != target_duration
        ):
            errors.append(f"{label}: final out must equal target duration")
        active_units[timeline_id] = ordered_units

        for ref_field in ("audio_track_refs", "text_track_refs", "export_refs"):
            if ref_field in item:
                _validate_string_list(
                    item.get(ref_field), f"{label}.{ref_field}", errors
                )

    if set(aspect_owner) != ASPECTS:
        errors.append("timelines: aspect ratios must equal 16:9 and 9:16")

    landscape_id = aspect_owner.get("16:9")
    portrait_id = aspect_owner.get("9:16")
    if landscape_id in active_units and portrait_id in active_units:
        landscape_units = active_units[landscape_id]
        portrait_units = active_units[portrait_id]
        if len(landscape_units) == len(portrait_units) and landscape_units:
            same_composition = all(
                (
                    left.get("reframe"),
                    left.get("scale"),
                    left.get("position"),
                )
                == (
                    right.get("reframe"),
                    right.get("scale"),
                    right.get("position"),
                )
                for left, right in zip(landscape_units, portrait_units)
            )
            if same_composition:
                errors.append(
                    "timelines: 9:16 composition must be independently authored"
                )
    return timelines, active_units


def _validate_audio_tracks(
    items: list[Any],
    assets: dict[str, dict[str, Any]],
    errors: list[str],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, str],
]:
    tracks: dict[str, dict[str, Any]] = {}
    cues: dict[str, dict[str, Any]] = {}
    cue_owners: dict[str, str] = {}
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"audio_tracks item {index}: expected object")
            continue
        raw_id = item.get("audio_track_id")
        track_id = raw_id if _is_nonempty_string(raw_id) else f"item-{index}"
        label = f"audio track {track_id}"
        _require_fields(
            item,
            (
                "audio_track_id",
                "track_type",
                "cues",
                "rights_status",
                "target_lufs",
                "true_peak_db",
            ),
            label,
            errors,
        )
        valid_id = _validate_id(raw_id, f"{label}: audio_track_id", errors)
        if valid_id is not None:
            if valid_id in tracks:
                errors.append(f"audio_tracks: duplicate audio_track_id {valid_id}")
            else:
                tracks[valid_id] = item
        for field in ("track_type", "rights_status"):
            if field in item:
                _validate_id(item.get(field), f"{label}: {field}", errors)
        for field in ("target_lufs", "true_peak_db"):
            if field in item and _decimal(item.get(field)) is None:
                errors.append(f"{label}: {field} must be a finite number")
        raw_cues = item.get("cues")
        if not isinstance(raw_cues, list):
            if "cues" in item:
                errors.append(f"{label}.cues: expected list")
            continue
        for cue_index, cue in enumerate(raw_cues, start=1):
            if not isinstance(cue, dict):
                errors.append(f"{label}.cues item {cue_index}: expected object")
                continue
            raw_cue_id = cue.get("audio_cue_id")
            cue_id = (
                raw_cue_id
                if _is_nonempty_string(raw_cue_id)
                else f"item-{cue_index}"
            )
            cue_label = f"audio cue {cue_id}"
            _require_fields(
                cue,
                (
                    "audio_cue_id",
                    "asset_id",
                    "timeline_in_seconds",
                    "timeline_out_seconds",
                ),
                cue_label,
                errors,
            )
            valid_cue_id = _validate_id(
                raw_cue_id, f"{cue_label}: audio_cue_id", errors
            )
            if valid_cue_id is not None:
                if valid_cue_id in cues:
                    errors.append(f"audio_tracks: duplicate audio_cue_id {valid_cue_id}")
                else:
                    cues[valid_cue_id] = cue
                    if valid_id is not None:
                        cue_owners[valid_cue_id] = valid_id
            cue_asset_id = _validate_id(
                cue.get("asset_id"), f"{cue_label}: asset_id", errors
            )
            if cue_asset_id is not None and cue_asset_id not in assets:
                errors.append(
                    f"{cue_label}: unknown asset_id {cue_asset_id}"
                )
            cue_in = None
            cue_out = None
            if "timeline_in_seconds" in cue:
                cue_in = _nonnegative_number(
                    cue.get("timeline_in_seconds"),
                    f"{cue_label}: timeline_in_seconds",
                    errors,
                )
            if "timeline_out_seconds" in cue:
                cue_out = _positive_number(
                    cue.get("timeline_out_seconds"),
                    f"{cue_label}: timeline_out_seconds",
                    errors,
                )
            if cue_in is not None and cue_out is not None and cue_out <= cue_in:
                errors.append(f"{cue_label}: timeline range must have positive duration")
    return tracks, cues, cue_owners


def _validate_text_tracks(
    items: list[Any], assets: dict[str, dict[str, Any]], errors: list[str]
) -> tuple[
    dict[str, dict[str, Any]],
    dict[str, dict[str, Any]],
    dict[str, str],
]:
    tracks: dict[str, dict[str, Any]] = {}
    cues: dict[str, dict[str, Any]] = {}
    cue_owners: dict[str, str] = {}
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"text_tracks item {index}: expected object")
            continue
        raw_id = item.get("text_track_id")
        track_id = raw_id if _is_nonempty_string(raw_id) else f"item-{index}"
        label = f"text track {track_id}"
        _require_fields(
            item,
            ("text_track_id", "language", "cues", "safe_area_status"),
            label,
            errors,
        )
        valid_id = _validate_id(raw_id, f"{label}: text_track_id", errors)
        if valid_id is not None:
            if valid_id in tracks:
                errors.append(f"text_tracks: duplicate text_track_id {valid_id}")
            else:
                tracks[valid_id] = item
        for field in ("language", "safe_area_status"):
            if field in item:
                _validate_id(item.get(field), f"{label}: {field}", errors)
        raw_cues = item.get("cues")
        if not isinstance(raw_cues, list):
            if "cues" in item:
                errors.append(f"{label}.cues: expected list")
            continue
        for cue_index, cue in enumerate(raw_cues, start=1):
            if not isinstance(cue, dict):
                errors.append(f"{label}.cues item {cue_index}: expected object")
                continue
            cue_id = cue.get("text_cue_id")
            cue_label = cue_id if _is_nonempty_string(cue_id) else f"item-{cue_index}"
            valid_cue_id = _validate_id(
                cue_id, f"text cue {cue_label}: text_cue_id", errors
            )
            if valid_cue_id is not None:
                if valid_cue_id in cues:
                    errors.append(f"text_tracks: duplicate text_cue_id {valid_cue_id}")
                else:
                    cues[valid_cue_id] = cue
                    if valid_id is not None:
                        cue_owners[valid_cue_id] = valid_id
            if "asset_id" in cue:
                cue_asset_id = _validate_id(
                    cue.get("asset_id"), f"text cue {cue_label}: asset_id", errors
                )
                if cue_asset_id is not None and cue_asset_id not in assets:
                    errors.append(
                        f"text cue {cue_label}: unknown asset_id {cue_asset_id}"
                    )
    return tracks, cues, cue_owners


def _validate_deliveries(
    items: list[Any],
    timelines: dict[str, dict[str, Any]],
    errors: list[str],
) -> dict[str, dict[str, Any]]:
    deliveries: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            errors.append(f"delivery_specs item {index}: expected object")
            continue
        raw_id = item.get("delivery_id")
        delivery_id = raw_id if _is_nonempty_string(raw_id) else f"item-{index}"
        label = f"delivery {delivery_id}"
        _require_fields(item, DELIVERY_FIELDS, label, errors)
        valid_id = _validate_id(raw_id, f"{label}: delivery_id", errors)
        if valid_id is not None:
            if valid_id in deliveries:
                errors.append(f"delivery_specs: duplicate delivery_id {valid_id}")
            else:
                deliveries[valid_id] = item
        for field in (
            "version_id",
            "timeline_id",
            "change_summary",
            "aspect_ratio",
            "resolution",
            "container",
            "video_codec",
            "audio_codec",
            "codec",
            "bitrate",
            "filename",
            "destination",
        ):
            if field in item:
                _validate_id(item.get(field), f"{label}: {field}", errors)
        _validate_enum(
            item.get("version_role"),
            DELIVERY_ROLES,
            f"{label}: version_role",
            "rough_cut, fine_cut, or final_master",
            errors,
        )
        _validate_enum(
            item.get("status"),
            DELIVERY_STATUSES,
            f"{label}: status",
            "draft, dry_run_passed, authorized, rendered, or blocked",
            errors,
        )
        if "ready" in item and not isinstance(item.get("ready"), bool):
            errors.append(f"{label}: ready must be a boolean")
        for field in ("artifact_refs", "validation_refs"):
            if field in item:
                _validate_string_list(
                    item.get(field),
                    f"{label}.{field}",
                    errors,
                    nonempty=field == "validation_refs",
                )
        for field in ("frame_rate", "audio_sample_rate", "audio_channels"):
            if field in item:
                _positive_number(item.get(field), f"{label}: {field}", errors)
        _validate_enum(
            item.get("subtitle_mode"),
            SUBTITLE_MODES,
            f"{label}: subtitle_mode",
            "none, sidecar, or burn_in",
            errors,
        )
        _validate_enum(
            item.get("audio_mode"),
            AUDIO_MODES,
            f"{label}: audio_mode",
            "temporary_or_silent, final_mix, or none",
            errors,
        )
        _validate_enum(
            item.get("look_mode"),
            LOOK_MODES,
            f"{label}: look_mode",
            "none or approved",
            errors,
        )
        _validate_enum(
            item.get("render_backend"),
            RENDER_BACKENDS,
            f"{label}: render_backend",
            "ffmpeg, premiere, resolve, jianying_capcut, ai_editor, or manual",
            errors,
        )

        timeline_id = item.get("timeline_id")
        if _is_nonempty_string(timeline_id):
            bound_timeline = timelines.get(timeline_id)
            if bound_timeline is None:
                errors.append(f"{label}: unknown timeline_id {timeline_id}")
            else:
                if item.get("aspect_ratio") != bound_timeline.get("aspect_ratio"):
                    errors.append(f"{label}: aspect_ratio must match timeline")
                if item.get("resolution") != bound_timeline.get("resolution"):
                    errors.append(f"{label}: resolution must match timeline")
                delivery_rate = _decimal(item.get("frame_rate"), positive=True)
                timeline_rate = _decimal(
                    bound_timeline.get("frame_rate"), positive=True
                )
                if (
                    delivery_rate is not None
                    and timeline_rate is not None
                    and delivery_rate != timeline_rate
                ):
                    errors.append(f"{label}: frame_rate must match timeline")
    return deliveries


def _validate_look_plan(look_plan: dict[str, Any], errors: list[str]) -> None:
    _require_fields(
        look_plan,
        (
            "input_color_space",
            "output_color_space",
            "matching_status",
            "instructions",
            "ffmpeg_filters",
        ),
        "look_plan",
        errors,
    )
    for field in ("input_color_space", "output_color_space", "matching_status"):
        if field in look_plan:
            _validate_id(look_plan.get(field), f"look_plan: {field}", errors)
    if "instructions" in look_plan:
        _validate_string_list(
            look_plan.get("instructions"),
            "look_plan.instructions",
            errors,
            nonempty=True,
        )
    if "ffmpeg_filters" in look_plan and not isinstance(
        look_plan.get("ffmpeg_filters"), list
    ):
        errors.append("look_plan.ffmpeg_filters: expected list")


def _collect_referenced_asset_ids(
    assets: dict[str, dict[str, Any]],
    timelines: dict[str, dict[str, Any]],
    active_units: dict[str, list[dict[str, Any]]],
    audio_tracks: dict[str, dict[str, Any]],
    audio_cues: dict[str, dict[str, Any]],
    text_tracks: dict[str, dict[str, Any]],
    text_cues: dict[str, dict[str, Any]],
    look_plan: dict[str, Any],
) -> set[str]:
    referenced: set[str] = {
        asset_id
        for asset_id, binding in assets.items()
        if binding.get("source_type") == "local_file"
        and binding.get("runtime_role") == "active"
    }

    def add_asset_id(value: Any) -> None:
        if _is_nonempty_string(value) and value in assets:
            referenced.add(value)

    for timeline_id, timeline_units in active_units.items():
        for unit in timeline_units:
            add_asset_id(unit.get("asset_id"))
            audio_cue_ids = unit.get("audio_cue_ids")
            if isinstance(audio_cue_ids, list):
                for cue_id in audio_cue_ids:
                    cue = audio_cues.get(cue_id) if _is_nonempty_string(cue_id) else None
                    if cue is not None:
                        add_asset_id(cue.get("asset_id"))
            text_cue_ids = unit.get("text_cue_ids")
            if isinstance(text_cue_ids, list):
                for cue_id in text_cue_ids:
                    cue = text_cues.get(cue_id) if _is_nonempty_string(cue_id) else None
                    if cue is not None:
                        add_asset_id(cue.get("asset_id"))

        timeline = timelines.get(timeline_id, {})
        audio_refs = timeline.get("audio_track_refs")
        if isinstance(audio_refs, list):
            for track_id in audio_refs:
                track = (
                    audio_tracks.get(track_id)
                    if _is_nonempty_string(track_id)
                    else None
                )
                raw_cues = track.get("cues") if track is not None else None
                if isinstance(raw_cues, list):
                    for cue in raw_cues:
                        if isinstance(cue, dict):
                            add_asset_id(cue.get("asset_id"))
        text_refs = timeline.get("text_track_refs")
        if isinstance(text_refs, list):
            for track_id in text_refs:
                track = (
                    text_tracks.get(track_id)
                    if _is_nonempty_string(track_id)
                    else None
                )
                raw_cues = track.get("cues") if track is not None else None
                if isinstance(raw_cues, list):
                    for cue in raw_cues:
                        if isinstance(cue, dict):
                            add_asset_id(cue.get("asset_id"))

    filters = look_plan.get("ffmpeg_filters")
    if isinstance(filters, list):
        for filter_item in filters:
            params = filter_item.get("params") if isinstance(filter_item, dict) else None
            if isinstance(params, dict):
                add_asset_id(params.get("asset_id"))

    pending = list(referenced)
    while pending:
        asset_id = pending.pop()
        fallback_id = assets[asset_id].get("fallback_asset_id")
        if (
            _is_nonempty_string(fallback_id)
            and fallback_id in assets
            and fallback_id not in referenced
        ):
            referenced.add(fallback_id)
            pending.append(fallback_id)
    return referenced


def _validate_execution_paths(
    execution: dict[str, Any],
    assets: dict[str, dict[str, Any]],
    referenced_asset_ids: set[str],
    errors: list[str],
) -> None:
    output_root = _lexical_path(
        execution.get("output_root"), "execution: output_root", errors
    )
    version_directory = _lexical_path(
        execution.get("version_directory"),
        "execution: version_directory",
        errors,
    )
    if output_root is not None:
        style, path = output_root
        is_filesystem_root = (
            style == "posix" and path == PurePosixPath("/")
        ) or (
            style == "windows" and str(path) == path.anchor
        ) or (
            style == "relative" and str(path) == "."
        )
        if is_filesystem_root:
            errors.append("execution: output_root must not be a filesystem root")
    if (
        output_root is not None
        and version_directory is not None
        and not _path_is_within(version_directory, output_root, strict=True)
    ):
        errors.append(
            "execution: version_directory must be a strict child of output_root"
        )

    raw_roots = execution.get("authorized_media_roots")
    valid_roots: list[tuple[str, PurePosixPath | PureWindowsPath]] = []
    if isinstance(raw_roots, list):
        if not raw_roots:
            errors.append("execution.authorized_media_roots: must not be empty")
        for index, raw_root in enumerate(raw_roots, start=1):
            label = f"execution.authorized_media_roots item {index}:"
            if not _is_nonempty_string(raw_root):
                errors.append(f"{label} must be a non-empty string")
                continue
            parsed_root = _lexical_path(raw_root, label, errors)
            if parsed_root is not None:
                valid_roots.append(parsed_root)

    for asset_id, binding in assets.items():
        source_type = binding.get("source_type")
        path_bearing = isinstance(source_type, str) and source_type in {
            "local_file",
            "post_asset",
        } and (
            asset_id in referenced_asset_ids
            or (
                source_type == "local_file"
                and binding.get("runtime_role") == "active"
            )
        )
        if not path_bearing:
            continue
        parsed_path = _lexical_path(
            binding.get("path_or_uri"), f"asset {asset_id}: path_or_uri", errors
        )
        if parsed_path is not None and not any(
            _path_is_within(parsed_path, root, strict=False)
            for root in valid_roots
        ):
            errors.append(
                f"asset {asset_id}: path_or_uri is outside authorized_media_roots"
            )


def _validate_review_evidence(
    execution: dict[str, Any],
    delivery_ids: set[str],
    errors: list[str],
) -> None:
    raw_review_evidence = execution.get("review_evidence")
    if raw_review_evidence is None:
        return
    if not isinstance(raw_review_evidence, list):
        errors.append("execution.review_evidence: expected list")
        return

    raw_tools = execution.get("tool_evidence")
    verified_tool_ids = {
        evidence.get("tool_evidence_id")
        for evidence in raw_tools
        if isinstance(evidence, dict)
        and _is_nonempty_string(evidence.get("tool_evidence_id"))
        and evidence.get("status") == "verified"
    } if isinstance(raw_tools, list) else set()
    seen_review_ids: set[str] = set()
    for index, evidence in enumerate(raw_review_evidence, start=1):
        if not isinstance(evidence, dict):
            errors.append(
                f"execution.review_evidence item {index}: expected object"
            )
            continue
        raw_id = evidence.get("review_evidence_id")
        evidence_id = (
            raw_id if _is_nonempty_string(raw_id) else f"item-{index}"
        )
        label = f"execution.review_evidence {evidence_id}"
        _require_fields(evidence, REVIEW_EVIDENCE_FIELDS, label, errors)
        for field in sorted(set(evidence) - set(REVIEW_EVIDENCE_FIELDS)):
            errors.append(f"{label}: unexpected field {field}")

        valid_id = _validate_id(
            raw_id, f"{label}: review_evidence_id", errors
        )
        if valid_id is not None and valid_id in seen_review_ids:
            errors.append(
                "execution.review_evidence: duplicate review_evidence_id "
                f"{valid_id}"
            )
        elif valid_id is not None:
            seen_review_ids.add(valid_id)

        delivery_id = evidence.get("delivery_id")
        if not _is_nonempty_string(delivery_id):
            errors.append(f"{label}: delivery_id must be a non-empty string")
        elif delivery_id not in delivery_ids:
            errors.append(f"{label}: unknown delivery_id {delivery_id}")
        evidence_type = evidence.get("evidence_type")
        if not isinstance(evidence_type, str) or evidence_type not in {
            "frame_change",
            "contact_sheet",
        }:
            errors.append(
                f"{label}: evidence_type must be frame_change or contact_sheet"
            )
        if not _is_nonempty_string(evidence.get("artifact_ref")):
            errors.append(f"{label}: artifact_ref must be a non-empty string")
        if evidence.get("status") != "passed":
            errors.append(f"{label}: status must be passed")
        tool_ref = evidence.get("tool_evidence_ref")
        if not _is_nonempty_string(tool_ref):
            errors.append(
                f"{label}: tool_evidence_ref must be a non-empty string"
            )
        elif isinstance(tool_ref, str) and tool_ref not in verified_tool_ids:
            errors.append(
                f"{label}: tool_evidence_ref {tool_ref} does not resolve to "
                "verified evidence"
            )


def _validate_execution(
    execution: dict[str, Any],
    deliveries: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
    referenced_asset_ids: set[str],
    for_execution: bool,
    errors: list[str],
) -> tuple[set[str], bool]:
    delivery_ids = set(deliveries)
    _require_fields(execution, EXECUTION_FIELDS, "execution", errors)
    _validate_review_evidence(execution, delivery_ids, errors)
    for field in (
        "dry_run_status",
        "operation_authorization",
        "output_root",
        "version_policy",
        "dry_run_manifest_id",
        "version_directory",
    ):
        if field in execution:
            _validate_id(execution.get(field), f"execution: {field}", errors)
    for field in (
        "authorized_media_roots",
        "tool_evidence",
        "executed_commands",
        "review_evidence",
        "rendered_outputs",
    ):
        if field in execution and not isinstance(execution.get(field), list):
            errors.append(f"execution.{field}: expected list")
    rendered_outputs = execution.get("rendered_outputs")
    if isinstance(rendered_outputs, list):
        for index, output in enumerate(rendered_outputs, start=1):
            if not isinstance(output, dict):
                errors.append(
                    f"execution.rendered_outputs item {index}: expected object"
                )
                continue
            output_id = output.get("delivery_id")
            if _is_nonempty_string(output_id) and output_id not in delivery_ids:
                errors.append(
                    f"execution.rendered_outputs: unknown delivery_id {output_id}"
                )
            elif not _is_nonempty_string(output_id):
                errors.append(
                    f"execution.rendered_outputs item {index}: delivery_id must "
                    "be a non-empty string"
                )

    pending_delivery_ids: set[str] = set()
    has_blocking_step = False
    raw_steps = execution.get("steps")
    if raw_steps is not None and not isinstance(raw_steps, list):
        errors.append("execution.steps: expected list")
    elif isinstance(raw_steps, list):
        seen_step_ids: set[str] = set()
        for index, step in enumerate(raw_steps, start=1):
            if not isinstance(step, dict):
                errors.append(f"execution.steps item {index}: expected object")
                continue
            raw_step_id = step.get("step_id")
            step_id = (
                raw_step_id
                if _is_nonempty_string(raw_step_id)
                else f"item-{index}"
            )
            label = f"execution step {step_id}"
            _require_fields(
                step, ("step_id", "delivery_id", "status"), label, errors
            )
            valid_step_id = _validate_id(
                raw_step_id, f"{label}: step_id", errors
            )
            duplicate = (
                valid_step_id in seen_step_ids
                if valid_step_id is not None
                else False
            )
            if duplicate:
                errors.append(
                    f"execution.steps: duplicate step_id {valid_step_id}"
                )
            elif valid_step_id is not None:
                seen_step_ids.add(valid_step_id)
            delivery_id = _validate_id(
                step.get("delivery_id"), f"{label}: delivery_id", errors
            )
            delivery_valid = delivery_id in delivery_ids if delivery_id else False
            if delivery_id is not None and not delivery_valid:
                errors.append(f"{label}: unknown delivery_id {delivery_id}")
            status = step.get("status")
            status_valid = (
                _is_nonempty_string(status)
                and status in EXECUTION_STEP_STATUSES
            )
            if not status_valid:
                errors.append(
                    f"{label}: status must be pending, running, passed, failed, "
                    "or blocked"
                )
            if (
                valid_step_id is not None
                and not duplicate
                and delivery_valid
                and status_valid
                and status in {"pending", "running"}
            ):
                pending_delivery_ids.add(delivery_id)
            if (
                valid_step_id is not None
                and not duplicate
                and delivery_valid
                and status_valid
                and status in {"failed", "blocked"}
            ):
                has_blocking_step = True

    _validate_execution_paths(execution, assets, referenced_asset_ids, errors)

    if not for_execution:
        return pending_delivery_ids, has_blocking_step
    if execution.get("dry_run_status") != "passed":
        errors.append("execution: dry-run status must be passed")
    if execution.get("operation_authorization") != "approved":
        errors.append("execution: operation authorization is required")
    if execution.get("version_policy") != "create_new":
        errors.append("execution: version_policy must be create_new")
    dry_manifest = execution.get("dry_run_manifest_id")
    authorized_manifest = execution.get("authorized_manifest_id")
    version_directory = execution.get("version_directory")
    authorized_directory = execution.get("authorized_version_directory")
    if not _is_nonempty_string(authorized_manifest):
        errors.append("execution: authorized_manifest_id is required")
    elif _is_nonempty_string(dry_manifest) and authorized_manifest != dry_manifest:
        errors.append("execution: authorization does not match dry-run manifest")
    if not _is_nonempty_string(authorized_directory):
        errors.append("execution: authorized_version_directory is required")
    elif (
        _is_nonempty_string(version_directory)
        and authorized_directory != version_directory
    ):
        errors.append("execution: authorization does not match version directory")

    locked_directory = _lexical_path(
        authorized_directory,
        "execution: authorized_version_directory",
        errors,
    )
    for delivery_id, delivery in deliveries.items():
        selected_for_execution = (
            delivery.get("ready") is True
            or delivery.get("status") == "authorized"
            or delivery_id in pending_delivery_ids
        )
        if not selected_for_execution:
            continue
        destination = _lexical_path(
            delivery.get("destination"),
            f"delivery {delivery_id}: destination",
            errors,
        )
        if (
            locked_directory is None
            or destination is None
            or not _path_is_within(destination, locked_directory, strict=True)
        ):
            errors.append(
                f"delivery {delivery_id}: destination must be a strict child of "
                "authorized_version_directory"
            )
    return pending_delivery_ids, has_blocking_step


def _validate_edit_validation(
    validation: dict[str, Any], delivery_ids: set[str], errors: list[str]
) -> None:
    _require_fields(
        validation,
        ("ready", "checks", "blocking_errors", "per_delivery_results"),
        "edit_validation",
        errors,
    )
    if "ready" in validation and not isinstance(validation.get("ready"), bool):
        errors.append("edit_validation: ready must be a boolean")
    for field in ("checks", "blocking_errors", "per_delivery_results"):
        if field in validation and not isinstance(validation.get(field), list):
            errors.append(f"edit_validation.{field}: expected list")
    results = validation.get("per_delivery_results")
    if isinstance(results, list):
        for index, result in enumerate(results, start=1):
            if not isinstance(result, dict):
                errors.append(
                    f"edit_validation.per_delivery_results item {index}: "
                    "expected object"
                )
                continue
            delivery_id = result.get("delivery_id")
            if _is_nonempty_string(delivery_id) and delivery_id not in delivery_ids:
                errors.append(
                    "edit_validation.per_delivery_results: unknown delivery_id "
                    f"{delivery_id}"
                )
            elif not _is_nonempty_string(delivery_id):
                errors.append(
                    f"edit_validation.per_delivery_results item {index}: "
                    "delivery_id must be a non-empty string"
                )


def _validate_binding_targets(
    assets: dict[str, dict[str, Any]],
    timelines: dict[str, dict[str, Any]],
    active_units: dict[str, list[dict[str, Any]]],
    source_package_id: Any,
    errors: list[str],
) -> None:
    edit_unit_ids = {
        unit.get("edit_unit_id")
        for timeline_units in active_units.values()
        for unit in timeline_units
        if _is_nonempty_string(unit.get("edit_unit_id"))
    }
    for asset_id, binding in assets.items():
        scope = binding.get("binding_scope")
        target_id = binding.get("target_id")
        if not _is_nonempty_string(target_id):
            continue
        if scope == "edit_unit" and target_id not in edit_unit_ids:
            errors.append(f"asset {asset_id}: unknown edit_unit target_id {target_id}")
        elif scope == "timeline" and target_id not in timelines:
            errors.append(f"asset {asset_id}: unknown timeline target_id {target_id}")
        elif scope == "project" and target_id != source_package_id:
            errors.append(
                f"asset {asset_id}: project target_id must equal source_package_id"
            )

    for timeline_units in active_units.values():
        for unit in timeline_units:
            unit_id = unit.get("edit_unit_id")
            asset_id = unit.get("asset_id")
            binding = assets.get(asset_id) if isinstance(asset_id, str) else None
            if binding is None or binding.get("binding_scope") != "shot":
                continue
            binding_shot_id = binding.get("shot_id")
            if unit.get("shot_id") != binding_shot_id:
                errors.append(
                    f"edit unit {unit_id}: shot_id must match asset {asset_id} "
                    f"binding shot_id {binding_shot_id}"
                )


def _validate_asset_use_context(
    assets: dict[str, dict[str, Any]],
    asset_id: Any,
    timeline_id: str,
    unit: dict[str, Any],
    source_package_id: Any,
    usage_label: str,
    errors: list[str],
) -> None:
    binding = assets.get(asset_id) if _is_nonempty_string(asset_id) else None
    if binding is None:
        return
    scope = binding.get("binding_scope")
    expected_targets = {
        "edit_unit": unit.get("edit_unit_id"),
        "timeline": timeline_id,
        "project": source_package_id,
        "shot": unit.get("shot_id"),
    }
    if scope not in expected_targets:
        return
    target_id = binding.get("target_id")
    expected_target = expected_targets[scope]
    if target_id != expected_target:
        errors.append(
            f"{usage_label}: asset {asset_id} binding_scope {scope} target_id "
            f"{target_id} does not match current {scope} {expected_target}"
        )


def _validate_track_cue_asset_context(
    assets: dict[str, dict[str, Any]],
    cue: dict[str, Any],
    cue_kind: str,
    track_id: str,
    timeline_id: str,
    timeline_units: list[dict[str, Any]],
    source_package_id: Any,
    errors: list[str],
) -> None:
    cue_id_field = f"{cue_kind}_cue_id"
    cue_id = cue.get(cue_id_field)
    asset_id = cue.get("asset_id")
    binding = assets.get(asset_id) if _is_nonempty_string(asset_id) else None
    if binding is None:
        return
    label = f"timeline {timeline_id} {cue_kind} track {track_id} cue {cue_id}"
    scope = binding.get("binding_scope")
    target_id = binding.get("target_id")
    if scope in {"timeline", "project"}:
        expected_target = (
            timeline_id if scope == "timeline" else source_package_id
        )
        if target_id != expected_target:
            errors.append(
                f"{label}: asset {asset_id} binding_scope {scope} target_id "
                f"{target_id} does not match current {scope} {expected_target}"
            )
        return
    if scope not in {"edit_unit", "shot"}:
        return
    cue_refs_field = f"{cue_kind}_cue_ids"
    explicit_owners = [
        unit
        for unit in timeline_units
        if isinstance(unit.get(cue_refs_field), list)
        and cue_id in unit.get(cue_refs_field)
    ]
    if scope == "edit_unit":
        unique_target_owner = (
            len(explicit_owners) == 1
            and explicit_owners[0].get("edit_unit_id") == target_id
        )
        if not unique_target_owner:
            errors.append(
                f"{label}: edit_unit-scoped asset {asset_id} must be explicitly "
                f"referenced by its unique target unit {target_id}"
            )
    elif scope == "shot":
        unique_target_owner = (
            len(explicit_owners) == 1
            and explicit_owners[0].get("shot_id") == target_id
        )
        if not unique_target_owner:
            errors.append(
                f"{label}: shot-scoped asset {asset_id} must be explicitly "
                f"referenced by one unit with target shot {target_id}"
            )


def _validate_render_evidence(
    execution: dict[str, Any],
    validation: dict[str, Any],
    deliveries: dict[str, dict[str, Any]],
    *,
    plan_is_rendered: bool,
    errors: list[str],
) -> set[str]:
    valid_tools: dict[str, dict[str, Any]] = {}
    seen_tool_ids: set[str] = set()
    raw_tools = execution.get("tool_evidence")
    if isinstance(raw_tools, list):
        for index, evidence in enumerate(raw_tools, start=1):
            if not isinstance(evidence, dict):
                errors.append(f"execution.tool_evidence item {index}: expected object")
                continue
            raw_id = evidence.get("tool_evidence_id")
            evidence_id = raw_id if _is_nonempty_string(raw_id) else f"item-{index}"
            label = f"execution.tool_evidence {evidence_id}"
            valid_id = _validate_id(raw_id, f"{label}: tool_evidence_id", errors)
            duplicate = valid_id in seen_tool_ids if valid_id is not None else False
            if duplicate:
                errors.append(
                    f"execution.tool_evidence: duplicate tool_evidence_id {valid_id}"
                )
            elif valid_id is not None:
                seen_tool_ids.add(valid_id)
            tool_valid = _is_nonempty_string(evidence.get("tool"))
            if not tool_valid:
                errors.append(f"{label}: tool must be a non-empty string")
            status_valid = evidence.get("status") in ("verified", "passed")
            if not status_valid:
                errors.append(f"{label}: status must be verified or passed")
            if valid_id is not None and not duplicate and tool_valid and status_valid:
                valid_tools[valid_id] = evidence

    valid_probes: dict[str, dict[str, Any]] = {}
    seen_probe_ids: set[str] = set()
    raw_probes = execution.get("probe_evidence")
    if raw_probes is not None and not isinstance(raw_probes, list):
        errors.append("execution.probe_evidence: expected list")
        raw_probes = []
    if isinstance(raw_probes, list):
        for index, evidence in enumerate(raw_probes, start=1):
            if not isinstance(evidence, dict):
                errors.append(f"execution.probe_evidence item {index}: expected object")
                continue
            raw_id = evidence.get("probe_evidence_id")
            evidence_id = raw_id if _is_nonempty_string(raw_id) else f"item-{index}"
            label = f"execution.probe_evidence {evidence_id}"
            valid_id = _validate_id(raw_id, f"{label}: probe_evidence_id", errors)
            duplicate = valid_id in seen_probe_ids if valid_id is not None else False
            if duplicate:
                errors.append(
                    f"execution.probe_evidence: duplicate probe_evidence_id {valid_id}"
                )
            elif valid_id is not None:
                seen_probe_ids.add(valid_id)
            delivery_id = evidence.get("delivery_id")
            delivery_valid = _is_nonempty_string(delivery_id)
            if not delivery_valid:
                errors.append(f"{label}: delivery_id must be a non-empty string")
            elif delivery_id not in deliveries:
                errors.append(f"{label}: unknown delivery_id {delivery_id}")
                delivery_valid = False
            output_valid = _is_nonempty_string(evidence.get("output_ref"))
            if not output_valid:
                errors.append(f"{label}: output_ref must be a non-empty string")
            status_valid = evidence.get("status") == "passed"
            if not status_valid:
                errors.append(f"{label}: status must be passed")
            if (
                valid_id is not None
                and not duplicate
                and delivery_valid
                and output_valid
                and status_valid
            ):
                valid_probes[valid_id] = evidence

    valid_outputs: dict[str, dict[str, Any]] = {}
    seen_output_deliveries: set[str] = set()
    raw_outputs = execution.get("rendered_outputs")
    if isinstance(raw_outputs, list):
        for index, output in enumerate(raw_outputs, start=1):
            if not isinstance(output, dict):
                continue
            delivery_id = output.get("delivery_id")
            if not _is_nonempty_string(delivery_id) or delivery_id not in deliveries:
                continue
            duplicate = delivery_id in seen_output_deliveries
            if duplicate:
                errors.append(
                    f"execution.rendered_outputs: duplicate delivery_id {delivery_id}"
                )
            else:
                seen_output_deliveries.add(delivery_id)
            output_ref = output.get("output_ref")
            if not _is_nonempty_string(output_ref):
                output_ref = output.get("path")
            output_valid = _is_nonempty_string(output_ref)
            if not output_valid and plan_is_rendered:
                errors.append(
                    f"plan_status rendered: delivery {delivery_id} rendered output "
                    "requires output_ref or path"
                )
            output_path = (
                _lexical_path(
                    output_ref,
                    f"execution.rendered_outputs {delivery_id}: output",
                    errors,
                )
                if output_valid
                else None
            )
            destination_path = _lexical_path(
                deliveries[delivery_id].get("destination"),
                f"delivery {delivery_id}: destination",
                errors,
            )
            output_matches_destination = (
                output_path is not None
                and destination_path is not None
                and _path_is_within(
                    output_path, destination_path, strict=False
                )
            )
            if output_valid and not output_matches_destination:
                errors.append(
                    f"execution.rendered_outputs {delivery_id}: output must "
                    "match or be within delivery destination"
                )
            status_valid = output.get("status") == "rendered"
            if not status_valid:
                errors.append(
                    f"execution.rendered_outputs {delivery_id}: status must be rendered"
                )
            tool_ref = output.get("tool_evidence_ref")
            tool_valid = _is_nonempty_string(tool_ref) and tool_ref in valid_tools
            if not _is_nonempty_string(tool_ref) and plan_is_rendered:
                errors.append(
                    f"plan_status rendered: delivery {delivery_id} rendered output "
                    "requires tool_evidence_ref"
                )
            elif _is_nonempty_string(tool_ref) and not tool_valid:
                errors.append(
                    f"execution.rendered_outputs {delivery_id}: tool_evidence_ref "
                    f"{tool_ref} does not resolve to verified evidence"
                )
            tool_status_valid = _is_success_status(output.get("tool_status"))
            if not tool_status_valid:
                errors.append(
                    f"execution.rendered_outputs {delivery_id}: tool_status "
                    "must be a successful status"
                )
            probe_ref = output.get("probe_evidence_ref")
            probe = valid_probes.get(probe_ref) if _is_nonempty_string(probe_ref) else None
            probe_valid = (
                probe is not None
                and probe.get("delivery_id") == delivery_id
                and probe.get("output_ref") == output_ref
            )
            if not _is_nonempty_string(probe_ref) and plan_is_rendered:
                errors.append(
                    f"plan_status rendered: delivery {delivery_id} rendered output "
                    "requires probe_evidence_ref"
                )
            elif _is_nonempty_string(probe_ref) and not probe_valid:
                errors.append(
                    f"execution.rendered_outputs {delivery_id}: probe_evidence_ref "
                    f"{probe_ref} does not match delivery and output"
                )
            probe_status_valid = _is_success_status(output.get("probe_status")) or (
                output.get("probe_status") == "unverified"
                and deliveries[delivery_id].get("version_role") == "rough_cut"
            )
            if not probe_status_valid:
                errors.append(
                    f"execution.rendered_outputs {delivery_id}: probe_status "
                    "must be a successful status"
                )
            if (
                not duplicate
                and output_valid
                and output_matches_destination
                and status_valid
                and tool_valid
                and tool_status_valid
                and probe_valid
                and probe_status_valid
            ):
                valid_outputs[delivery_id] = output

    valid_results: set[str] = set()
    seen_result_deliveries: set[str] = set()
    raw_results = validation.get("per_delivery_results")
    if isinstance(raw_results, list):
        for result in raw_results:
            if not isinstance(result, dict):
                continue
            delivery_id = result.get("delivery_id")
            if not _is_nonempty_string(delivery_id) or delivery_id not in deliveries:
                continue
            if delivery_id in seen_result_deliveries:
                errors.append(
                    "edit_validation.per_delivery_results: duplicate delivery_id "
                    f"{delivery_id}"
                )
                valid_results.discard(delivery_id)
                continue
            seen_result_deliveries.add(delivery_id)
            delivery = deliveries[delivery_id]
            needs_result = (
                delivery.get("status") == "rendered"
                or delivery.get("ready") is True
            )
            status_valid = result.get("status") == "passed"
            validation_valid = result.get("validation_status") == "passed"
            if needs_result and (not status_valid or not validation_valid):
                if plan_is_rendered:
                    errors.append(
                        f"plan_status rendered: delivery {delivery_id} "
                        "per-delivery validation status must be passed"
                    )
            if status_valid and validation_valid:
                valid_results.add(delivery_id)

    if plan_is_rendered and not valid_tools:
        errors.append(
            "plan_status rendered: execution.tool_evidence must contain "
            "verified successful evidence"
        )
    return set(valid_outputs) & valid_results


def _validate_current_authorization(
    execution: dict[str, Any], plan_status: str, errors: list[str]
) -> None:
    label = f"plan_status {plan_status}"
    if execution.get("dry_run_status") != "passed":
        errors.append(f"{label}: dry-run status must be passed")
    if execution.get("operation_authorization") != "approved":
        errors.append(f"{label}: operation authorization must be approved")
    if execution.get("version_policy") != "create_new":
        errors.append(f"{label}: version_policy must be create_new")
    if execution.get("authorized_manifest_id") != execution.get(
        "dry_run_manifest_id"
    ):
        errors.append(f"{label}: authorization does not match dry-run manifest")
    if execution.get("authorized_version_directory") != execution.get(
        "version_directory"
    ):
        errors.append(f"{label}: authorization does not match version directory")


def _validate_cross_references(
    timelines: dict[str, dict[str, Any]],
    active_units: dict[str, list[dict[str, Any]]],
    deliveries: dict[str, dict[str, Any]],
    assets: dict[str, dict[str, Any]],
    source_package_id: Any,
    audio_tracks: dict[str, dict[str, Any]],
    audio_cues: dict[str, dict[str, Any]],
    audio_cue_tracks: dict[str, str],
    text_tracks: dict[str, dict[str, Any]],
    text_cues: dict[str, dict[str, Any]],
    text_cue_tracks: dict[str, str],
    errors: list[str],
) -> None:
    for timeline_id, timeline in timelines.items():
        audio_refs = timeline.get("audio_track_refs")
        if not isinstance(audio_refs, list):
            audio_refs = []
        seen_audio_refs: set[str] = set()
        for audio_ref in audio_refs:
            if _is_nonempty_string(audio_ref) and audio_ref in seen_audio_refs:
                errors.append(
                    f"timeline {timeline_id}: duplicate audio_track_id "
                    f"{audio_ref} in audio_track_refs"
                )
            elif _is_nonempty_string(audio_ref):
                seen_audio_refs.add(audio_ref)
            if _is_nonempty_string(audio_ref) and audio_ref not in audio_tracks:
                errors.append(
                    f"timeline {timeline_id}: unknown audio_track_id {audio_ref}"
                )
        checked_audio_tracks: set[str] = set()
        for audio_ref in audio_refs:
            if (
                not _is_nonempty_string(audio_ref)
                or audio_ref in checked_audio_tracks
                or audio_ref not in audio_tracks
            ):
                continue
            checked_audio_tracks.add(audio_ref)
            raw_cues = audio_tracks[audio_ref].get("cues")
            if isinstance(raw_cues, list):
                for cue in raw_cues:
                    if isinstance(cue, dict):
                        _validate_track_cue_asset_context(
                            assets,
                            cue,
                            "audio",
                            audio_ref,
                            timeline_id,
                            active_units.get(timeline_id, []),
                            source_package_id,
                            errors,
                        )
        text_refs = timeline.get("text_track_refs")
        if not isinstance(text_refs, list):
            text_refs = []
        seen_text_refs: set[str] = set()
        for text_ref in text_refs:
            if _is_nonempty_string(text_ref) and text_ref in seen_text_refs:
                errors.append(
                    f"timeline {timeline_id}: duplicate text_track_id "
                    f"{text_ref} in text_track_refs"
                )
            elif _is_nonempty_string(text_ref):
                seen_text_refs.add(text_ref)
            if _is_nonempty_string(text_ref) and text_ref not in text_tracks:
                errors.append(
                    f"timeline {timeline_id}: unknown text_track_id {text_ref}"
                )
        checked_text_tracks: set[str] = set()
        for text_ref in text_refs:
            if (
                not _is_nonempty_string(text_ref)
                or text_ref in checked_text_tracks
                or text_ref not in text_tracks
            ):
                continue
            checked_text_tracks.add(text_ref)
            raw_cues = text_tracks[text_ref].get("cues")
            if isinstance(raw_cues, list):
                for cue in raw_cues:
                    if isinstance(cue, dict) and "asset_id" in cue:
                        _validate_track_cue_asset_context(
                            assets,
                            cue,
                            "text",
                            text_ref,
                            timeline_id,
                            active_units.get(timeline_id, []),
                            source_package_id,
                            errors,
                        )
        export_refs = timeline.get("export_refs")
        if not isinstance(export_refs, list):
            export_refs = []
        seen_delivery_refs: set[str] = set()
        for delivery_ref in export_refs:
            if not _is_nonempty_string(delivery_ref):
                continue
            if delivery_ref in seen_delivery_refs:
                errors.append(
                    f"timeline {timeline_id}: duplicate delivery_id "
                    f"{delivery_ref} in export_refs"
                )
            else:
                seen_delivery_refs.add(delivery_ref)
            bound_delivery = deliveries.get(delivery_ref)
            if bound_delivery is None:
                errors.append(
                    f"timeline {timeline_id}: unknown delivery_id {delivery_ref} "
                    "in export_refs"
                )
            else:
                bound_timeline_id = bound_delivery.get("timeline_id")
                if bound_timeline_id != timeline_id:
                    errors.append(
                        f"timeline {timeline_id}: delivery {delivery_ref} is "
                        f"bound to timeline {bound_timeline_id}"
                    )
        for unit in active_units.get(timeline_id, []):
            unit_id = unit.get("edit_unit_id")
            _validate_asset_use_context(
                assets,
                unit.get("asset_id"),
                timeline_id,
                unit,
                source_package_id,
                f"edit unit {unit_id}",
                errors,
            )
            unit_audio_refs = unit.get("audio_cue_ids")
            if not isinstance(unit_audio_refs, list):
                unit_audio_refs = []
            for audio_cue_id in unit_audio_refs:
                if _is_nonempty_string(audio_cue_id) and audio_cue_id not in audio_cues:
                    errors.append(
                        f"edit unit {unit_id}: unknown audio_cue_id {audio_cue_id}"
                    )
                elif _is_nonempty_string(audio_cue_id):
                    owner = audio_cue_tracks.get(audio_cue_id)
                    if owner is not None and owner not in seen_audio_refs:
                        errors.append(
                            f"edit unit {unit_id}: audio_cue_id {audio_cue_id} "
                            f"belongs to unreferenced audio track {owner}"
                        )
                    cue = audio_cues.get(audio_cue_id)
                    if cue is not None:
                        _validate_asset_use_context(
                            assets,
                            cue.get("asset_id"),
                            timeline_id,
                            unit,
                            source_package_id,
                            f"edit unit {unit_id} audio cue {audio_cue_id}",
                            errors,
                        )
            unit_text_refs = unit.get("text_cue_ids")
            if not isinstance(unit_text_refs, list):
                unit_text_refs = []
            for text_cue_id in unit_text_refs:
                if (
                    _is_nonempty_string(text_cue_id)
                    and text_cue_id not in text_cue_tracks
                ):
                    errors.append(
                        f"edit unit {unit_id}: unknown text_cue_id {text_cue_id}"
                    )
                elif _is_nonempty_string(text_cue_id):
                    owner = text_cue_tracks.get(text_cue_id)
                    if owner is not None and owner not in seen_text_refs:
                        errors.append(
                            f"edit unit {unit_id}: text_cue_id {text_cue_id} "
                            f"belongs to unreferenced text track {owner}"
                        )
                    cue = text_cues.get(text_cue_id)
                    if cue is not None and "asset_id" in cue:
                        _validate_asset_use_context(
                            assets,
                            cue.get("asset_id"),
                            timeline_id,
                            unit,
                            source_package_id,
                            f"edit unit {unit_id} text cue {text_cue_id}",
                            errors,
                        )
    for delivery_id, delivery in deliveries.items():
        timeline_id = delivery.get("timeline_id")
        bound_timeline = (
            timelines.get(timeline_id)
            if isinstance(timeline_id, str)
            else None
        )
        export_refs = (
            bound_timeline.get("export_refs")
            if bound_timeline is not None
            else None
        )
        if bound_timeline is not None and (
            not isinstance(export_refs, list)
            or export_refs.count(delivery_id) == 0
        ):
            errors.append(
                f"delivery {delivery_id}: timeline export_refs do not reference delivery"
            )


def _validate_ffmpeg_filter_plan(
    look_plan: dict[str, Any],
    assets: dict[str, dict[str, Any]],
    errors: list[str],
) -> bool:
    filters = look_plan.get("ffmpeg_filters")
    if not isinstance(filters, list):
        return True
    blocked = False
    for index, filter_item in enumerate(filters, start=1):
        if isinstance(filter_item, str):
            errors.append(
                "look_plan.ffmpeg_filters: raw filter strings are not allowed"
            )
            blocked = True
            continue
        if not isinstance(filter_item, dict):
            errors.append(
                f"look_plan.ffmpeg_filters: item {index} must be an object"
            )
            blocked = True
            continue
        keys = set(filter_item)
        if keys == {"name", "params"}:
            name = filter_item["name"]
        elif keys == {"filter", "params"}:
            name = filter_item["filter"]
        else:
            errors.append(
                f"look_plan.ffmpeg_filters: item {index} must have exact shape "
                "{name, params} or {filter, params}"
            )
            blocked = True
            continue
        if not isinstance(name, str) or name not in {"eq", "curves", "lut3d"}:
            errors.append(
                f"look_plan.ffmpeg_filters: unsupported filter {name}"
            )
            blocked = True
        params = filter_item.get("params")
        if not isinstance(params, dict):
            errors.append(
                f"look_plan.ffmpeg_filters: filter {name} params must be an object"
            )
            blocked = True
            continue
        if name == "eq":
            ranges = {
                "brightness": (Decimal("-1"), Decimal("1")),
                "contrast": (Decimal("0"), Decimal("2")),
                "saturation": (Decimal("0"), Decimal("3")),
                "gamma": (Decimal("0.1"), Decimal("10")),
                "gamma_r": (Decimal("0.1"), Decimal("10")),
                "gamma_g": (Decimal("0.1"), Decimal("10")),
                "gamma_b": (Decimal("0.1"), Decimal("10")),
            }
            for key, value in params.items():
                if key not in ranges:
                    errors.append(
                        f"look_plan.ffmpeg_filters: filter eq has unsupported param {key}"
                    )
                    blocked = True
                    continue
                decimal_value = _decimal(value)
                if decimal_value is None:
                    errors.append(
                        f"look_plan.ffmpeg_filters: filter eq param {key} "
                        "must be a finite number"
                    )
                    blocked = True
                    continue
                minimum, maximum = ranges[key]
                if not minimum <= decimal_value <= maximum:
                    errors.append(
                        f"look_plan.ffmpeg_filters: filter eq param {key} must "
                        f"be between {minimum} and {maximum}"
                    )
                    blocked = True
        elif name == "curves":
            for key in params:
                if key != "preset":
                    errors.append(
                        "look_plan.ffmpeg_filters: filter curves has unsupported "
                        f"param {key}"
                    )
                    blocked = True
            safe_presets = {
                "none",
                "color_negative",
                "cross_process",
                "darker",
                "increase_contrast",
                "lighter",
                "linear_contrast",
                "medium_contrast",
                "strong_contrast",
                "vintage",
            }
            preset = params.get("preset")
            if not isinstance(preset, str) or preset not in safe_presets:
                errors.append(
                    "look_plan.ffmpeg_filters: filter curves preset must be a "
                    "safe named preset"
                )
                blocked = True
        elif name == "lut3d":
            for key in params:
                if key != "asset_id":
                    errors.append(
                        "look_plan.ffmpeg_filters: filter lut3d has unsupported "
                        f"param {key}"
                    )
                    blocked = True
            asset_id = params.get("asset_id")
            safe_asset_id = _is_nonempty_string(asset_id) and all(
                character.isalnum() or character in "._-"
                for character in asset_id
            )
            if _is_nonempty_string(asset_id) and not safe_asset_id:
                errors.append(
                    "look_plan.ffmpeg_filters: filter lut3d asset_id contains "
                    "unsafe characters"
                )
                blocked = True
            binding = assets.get(asset_id) if safe_asset_id else None
            if safe_asset_id and binding is None:
                errors.append(
                    f"look_plan.ffmpeg_filters: filter lut3d unknown asset_id {asset_id}"
                )
                blocked = True
            elif binding is not None:
                authorized = (
                    binding.get("source_type") in ("local_file", "post_asset")
                    and binding.get("rights_status") == "cleared"
                    and binding.get("file_status") == "online"
                    and binding.get("probe_status") == "verified"
                )
                if not authorized:
                    errors.append(
                        f"look_plan.ffmpeg_filters: filter lut3d asset {asset_id} "
                        "must be cleared, online, and verified local/post media"
                    )
                    blocked = True
                path = binding.get("path_or_uri")
                path_safe = _is_safe_lut_path(path)
                if not path_safe or not path.lower().endswith(".cube"):
                    errors.append(
                        f"look_plan.ffmpeg_filters: filter lut3d asset {asset_id} "
                        "must use a safe .cube path"
                    )
                    blocked = True
    return blocked


def _validate_final_requirements(
    *,
    require_final: bool,
    assets: dict[str, dict[str, Any]],
    active_units: dict[str, list[dict[str, Any]]],
    audio_tracks: dict[str, dict[str, Any]],
    audio_cues: dict[str, dict[str, Any]],
    text_tracks: dict[str, dict[str, Any]],
    look_plan: dict[str, Any],
    deliveries: dict[str, dict[str, Any]],
    software_targets: dict[str, dict[str, Any]],
    evidenced_delivery_ids: set[str],
    errors: list[str],
) -> None:
    if not require_final:
        return

    shared_blocker = False
    placeholder_assets = {
        asset_id
        for asset_id, binding in assets.items()
        if binding.get("source_type") == "generated_placeholder"
        or binding.get("file_status") == "placeholder"
    }
    for asset_id, binding in assets.items():
        if asset_id in placeholder_assets:
            shared_blocker = True
        if (
            binding.get("file_status") != "online"
            or binding.get("probe_status") != "verified"
        ):
            errors.append(
                f"asset {asset_id}: final delivery requires online verified media"
            )
            shared_blocker = True
        if binding.get("rights_status") != "cleared":
            errors.append(f"asset {asset_id}: final delivery requires cleared rights")
            shared_blocker = True
    for track_id, track in audio_tracks.items():
        if track.get("rights_status") != "cleared":
            errors.append(
                f"audio track {track_id}: final delivery requires cleared rights"
            )
            shared_blocker = True
    for track_id, track in text_tracks.items():
        if track.get("safe_area_status") != "passed":
            errors.append(
                f"text track {track_id}: safe area must pass for final delivery"
            )
            shared_blocker = True
    if look_plan.get("matching_status") != "passed":
        errors.append("look_plan: matching must pass for final delivery")
        shared_blocker = True

    final_deliveries = [
        (delivery_id, delivery)
        for delivery_id, delivery in deliveries.items()
        if delivery.get("version_role") == "final_master"
    ]
    if not final_deliveries and placeholder_assets:
        errors.append("final validation: placeholder media is not allowed")

    for delivery_id, delivery in final_deliveries:
        delivery_blocked = shared_blocker
        if delivery.get("ready") is True and (
            delivery.get("status") != "rendered"
            or delivery_id not in evidenced_delivery_ids
        ):
            errors.append(
                f"final master {delivery_id}: ready requires rendered status "
                "and complete evidence"
            )
            delivery_blocked = True
        timeline_id = delivery.get("timeline_id")
        timeline_units = (
            active_units.get(timeline_id, [])
            if isinstance(timeline_id, str)
            else []
        )
        used_asset_ids = {
            unit.get("asset_id")
            for unit in timeline_units
            if _is_nonempty_string(unit.get("asset_id"))
        }
        if used_asset_ids & placeholder_assets:
            errors.append(
                f"final master {delivery_id}: placeholder media is not allowed"
            )
            delivery_blocked = True

        backend = delivery.get("render_backend")
        backend_valid = _is_nonempty_string(backend) and backend in RENDER_BACKENDS
        if not backend_valid:
            delivery_blocked = True
        elif backend == "manual":
            errors.append(
                f"final master {delivery_id}: render backend manual is not executable"
            )
            delivery_blocked = True
        elif delivery.get("ready") is True:
            required_target = BACKEND_SOFTWARE_TARGETS.get(backend)
            target = software_targets.get(required_target)
            if target is None:
                errors.append(
                    f"final master {delivery_id}: missing software target "
                    f"{required_target}"
                )
                delivery_blocked = True
            else:
                target_status = target.get("status")
                target_status_valid = (
                    _is_nonempty_string(target_status)
                    and target_status in {"supported", "verified"}
                )
                if not target_status_valid:
                    errors.append(
                        f"final master {delivery_id}: software target "
                        f"{required_target} must be supported or verified"
                    )
                    delivery_blocked = True
        if backend_valid and backend == "ffmpeg":
            for unit in timeline_units:
                unit_id = unit.get("edit_unit_id")
                for field in ("transition_in", "transition_out"):
                    transition = unit.get(field)
                    if (
                        not isinstance(transition, str)
                        or transition not in {"hard_cut", "end"}
                    ):
                        errors.append(
                            f"final master {delivery_id}: ffmpeg does not support "
                            f"transition {transition} in {unit_id}"
                        )
                        delivery_blocked = True
                effects = unit.get("effects", [])
                if not isinstance(effects, list):
                    errors.append(
                        f"final master {delivery_id}: effects in {unit_id} must be a list"
                    )
                    delivery_blocked = True
                else:
                    for effect in effects:
                        effect_name = (
                            effect.get("type") if isinstance(effect, dict) else effect
                        )
                        errors.append(
                            f"final master {delivery_id}: ffmpeg does not support "
                            f"effect {effect_name} in {unit_id}"
                        )
                        delivery_blocked = True

            subtitle_mode = delivery.get("subtitle_mode")
            if not (
                _is_nonempty_string(subtitle_mode)
                and subtitle_mode in {"none", "burn_in"}
            ):
                errors.append(
                    f"final master {delivery_id}: ffmpeg subtitle configuration "
                    "is unsupported"
                )
                delivery_blocked = True
            audio_mode = delivery.get("audio_mode")
            if not (
                _is_nonempty_string(audio_mode)
                and audio_mode in {"none", "final_mix"}
            ):
                errors.append(
                    f"final master {delivery_id}: ffmpeg audio configuration is unsupported"
                )
                delivery_blocked = True
            if delivery.get("look_mode") == "approved":
                filters = look_plan.get("ffmpeg_filters")
                if not isinstance(filters, list) or not filters:
                    errors.append(
                        f"final master {delivery_id}: ffmpeg look configuration "
                        "is unsupported"
                    )
                    delivery_blocked = True
                if _validate_ffmpeg_filter_plan(look_plan, assets, errors):
                    delivery_blocked = True

            if delivery.get("audio_mode") == "final_mix":
                for cue_id, cue in audio_cues.items():
                    asset_id = cue.get("asset_id")
                    binding = (
                        assets.get(asset_id)
                        if isinstance(asset_id, str)
                        else None
                    )
                    authorized = (
                        binding is not None
                        and binding.get("source_type") == "post_asset"
                        and isinstance(binding.get("binding_scope"), str)
                        and binding.get("binding_scope") in {
                            "edit_unit",
                            "timeline",
                            "project",
                        }
                        and binding.get("file_status") == "online"
                        and binding.get("probe_status") == "verified"
                        and binding.get("rights_status") == "cleared"
                    )
                    if not authorized:
                        errors.append(
                            f"final master {delivery_id}: audio cue {cue_id} "
                            f"asset_id {asset_id} is not an authorized local/post binding"
                        )
                        delivery_blocked = True

        if delivery.get("ready") is True and delivery_blocked:
            errors.append(
                f"final master {delivery_id}: ready cannot be true while final "
                "blockers remain"
            )


def validate_edit_plan(
    plan: object,
    *,
    require_final: bool = False,
    for_execution: bool = False,
    require_cinematic: bool = False,
) -> list[str]:
    """Return deterministic validation errors for an edit master plan."""
    errors: list[str] = []
    if not isinstance(plan, dict):
        return ["edit plan: expected object"]

    _require_fields(plan, TOP_LEVEL_FIELDS, "edit plan", errors)
    allowed_top_level_fields = TOP_LEVEL_FIELDS + OPTIONAL_TOP_LEVEL_FIELDS
    for field in sorted(set(plan) - set(allowed_top_level_fields)):
        errors.append(f"edit plan: unknown top-level field {field}")
    if "edit_plan_id" in plan:
        _validate_id(plan.get("edit_plan_id"), "edit_plan_id", errors)
    if "source_package_id" in plan:
        _validate_id(plan.get("source_package_id"), "source_package_id", errors)
    if "plan_status" in plan:
        _validate_enum(
            plan.get("plan_status"),
            PLAN_STATUSES,
            "plan_status",
            "draft, dry_run_passed, authorized, rendered, or blocked",
            errors,
        )
    target_duration = None
    if "target_duration_seconds" in plan:
        target_duration = _positive_number(
            plan.get("target_duration_seconds"),
            "target_duration_seconds",
            errors,
        )

    locked_event_ids = (
        _validate_string_list(
            plan.get("locked_event_ids"),
            "locked_event_ids",
            errors,
            nonempty=True,
        )
        if "locked_event_ids" in plan
        else []
    )
    if len(locked_event_ids) != len(set(locked_event_ids)):
        errors.append("locked_event_ids: duplicate IDs are not allowed")

    media_items = _list_field(plan, "media_bindings", errors)
    timeline_items = _list_field(plan, "timelines", errors)
    audio_items = _list_field(plan, "audio_tracks", errors)
    text_items = _list_field(plan, "text_tracks", errors)
    delivery_items = _list_field(plan, "delivery_specs", errors)
    software_items = _list_field(plan, "software_targets", errors)
    look_plan = _dict_field(plan, "look_plan", errors)
    execution = _dict_field(plan, "execution", errors)
    edit_validation = _dict_field(plan, "edit_validation", errors)

    assets = _validate_media_bindings(media_items, errors)
    timelines, active_units = _validate_timelines(
        timeline_items, assets, target_duration, locked_event_ids, errors
    )
    audio_tracks, audio_cues, audio_cue_tracks = _validate_audio_tracks(
        audio_items, assets, errors
    )
    text_tracks, text_cues, text_cue_tracks = _validate_text_tracks(
        text_items, assets, errors
    )
    _validate_look_plan(look_plan, errors)
    deliveries = _validate_deliveries(delivery_items, timelines, errors)
    ffmpeg_may_consume_look_plan = any(
        delivery.get("render_backend") == "ffmpeg"
        and (
            delivery.get("look_mode") == "approved"
            or (for_execution and delivery.get("ready") is True)
        )
        for delivery in deliveries.values()
    )
    if ffmpeg_may_consume_look_plan:
        _validate_ffmpeg_filter_plan(look_plan, assets, errors)
    _validate_binding_targets(
        assets,
        timelines,
        active_units,
        plan.get("source_package_id"),
        errors,
    )

    software_targets: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(software_items, start=1):
        if not isinstance(item, dict):
            errors.append(f"software_targets item {index}: expected object")
            continue
        _require_fields(item, ("target", "status"), "software target", errors)
        target = _validate_id(
            item.get("target"), f"software target item {index}: target", errors
        )
        _validate_id(
            item.get("status"), f"software target item {index}: status", errors
        )
        if target is not None:
            if target in software_targets:
                errors.append(f"software_targets: duplicate target {target}")
            else:
                software_targets[target] = item
        if target == "jianying_capcut" and (
            not isinstance(item.get("status"), str)
            or item.get("status")
            not in {
                "manual_or_unverified",
                "blocked",
                "supported",
                "verified",
            }
        ):
            errors.append(
                "software target jianying_capcut: status must be "
                "manual_or_unverified, blocked, supported, or verified"
            )

    _validate_cross_references(
        timelines,
        active_units,
        deliveries,
        assets,
        plan.get("source_package_id"),
        audio_tracks,
        audio_cues,
        audio_cue_tracks,
        text_tracks,
        text_cues,
        text_cue_tracks,
        errors,
    )
    referenced_asset_ids = _collect_referenced_asset_ids(
        assets,
        timelines,
        active_units,
        audio_tracks,
        audio_cues,
        text_tracks,
        text_cues,
        look_plan,
    )
    (
        pending_execution_delivery_ids,
        has_blocking_execution_step,
    ) = _validate_execution(
        execution,
        deliveries,
        assets,
        referenced_asset_ids,
        for_execution,
        errors,
    )
    _validate_edit_validation(edit_validation, set(deliveries), errors)

    cinematic = plan.get("cinematic_validation")
    cinematic_required = require_cinematic or (
        isinstance(cinematic, dict)
        and cinematic.get("declared_mode") == "cinematic"
    )
    cinematic_errors = validate_cinematic_plan(
        plan, required=cinematic_required
    )
    errors.extend(cinematic_errors)
    cinematic_blocked = bool(cinematic_errors)
    if cinematic_blocked:
        if plan.get("plan_status") == "rendered":
            errors.append(
                "plan_status rendered: cinematic blockers require aggregate "
                "status blocked"
            )
        if edit_validation.get("ready") is True:
            errors.append(
                "edit_validation.ready: cannot be true while cinematic "
                "blockers remain"
            )
        for delivery_id, delivery in deliveries.items():
            if delivery.get("ready") is True:
                errors.append(
                    f"delivery {delivery_id}: ready cannot be true while "
                    "cinematic blockers remain"
                )

    plan_status = plan.get("plan_status")
    evidenced_delivery_ids = _validate_render_evidence(
        execution,
        edit_validation,
        deliveries,
        plan_is_rendered=plan_status == "rendered",
        errors=errors,
    )

    blocking_errors = edit_validation.get("blocking_errors")
    has_blocker = (
        isinstance(blocking_errors, list)
        and bool(blocking_errors)
    ) or cinematic_blocked or has_blocking_execution_step or any(
        delivery.get("status") == "blocked"
        for delivery in deliveries.values()
    ) or any(
        binding.get("file_status") == "offline"
        or binding.get("rights_status") == "blocked"
        for binding in assets.values()
    )
    if has_blocker and _is_nonempty_string(plan_status) and plan_status != "blocked":
        errors.append(
            f"plan_status {plan_status}: blockers require aggregate status blocked"
        )

    if plan_status == "rendered":
        _validate_current_authorization(execution, "rendered", errors)
        all_rendered = bool(deliveries) and all(
            delivery.get("status") == "rendered" and delivery.get("ready") is True
            for delivery in deliveries.values()
        )
        if not all_rendered:
            errors.append(
                "plan_status rendered: plan cannot be rendered before every "
                "requested delivery is rendered and ready"
            )
        if evidenced_delivery_ids != set(deliveries):
            errors.append(
                "plan_status rendered: every requested delivery requires a "
                "complete output, tool, probe, and validation evidence chain"
            )
        if edit_validation.get("ready") is not True:
            errors.append("plan_status rendered: edit_validation.ready must be true")
    elif plan_status == "authorized":
        _validate_current_authorization(execution, "authorized", errors)
        if not pending_execution_delivery_ids:
            errors.append(
                "plan_status authorized: at least one requested delivery requires "
                "a pending or running execution step"
            )
    elif plan_status == "dry_run_passed":
        if execution.get("dry_run_status") != "passed":
            errors.append("plan_status dry_run_passed: dry-run status must be passed")
        if execution.get("operation_authorization") == "approved":
            errors.append(
                "plan_status dry_run_passed: approved authorization requires "
                "authorized aggregate status"
            )
        if any(
            delivery.get("status") != "dry_run_passed"
            for delivery in deliveries.values()
        ):
            errors.append(
                "plan_status dry_run_passed: every requested delivery must be "
                "dry_run_passed"
            )
    elif plan_status == "blocked":
        if not has_blocker:
            errors.append(
                "plan_status blocked: no blocking requested delivery or shared dependency"
            )

    _validate_final_requirements(
        require_final=require_final,
        assets=assets,
        active_units=active_units,
        audio_tracks=audio_tracks,
        audio_cues=audio_cues,
        text_tracks=text_tracks,
        look_plan=look_plan,
        deliveries=deliveries,
        software_targets=software_targets,
        evidenced_delivery_ids=evidenced_delivery_ids,
        errors=errors,
    )
    return list(dict.fromkeys(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a finished-film edit master plan JSON file."
    )
    parser.add_argument("plan", type=Path, help="Path to the edit plan JSON file")
    parser.add_argument(
        "--require-final",
        action="store_true",
        help="Apply final-master media, rights, text, look, and render gates.",
    )
    parser.add_argument(
        "--for-execution",
        action="store_true",
        help="Require authorization bound to the dry-run manifest and directory.",
    )
    parser.add_argument(
        "--require-cinematic",
        action="store_true",
        help="Apply motion, coverage, transition, audio, and anti-PPT gates.",
    )
    args = parser.parse_args(argv)

    try:
        plan_size = args.plan.stat().st_size
        if plan_size > MAX_PLAN_BYTES:
            print(
                f"ERROR: plan exceeds maximum size of 10 MiB: {args.plan}",
                file=sys.stderr,
            )
            return 2
        with args.plan.open("r", encoding="utf-8") as plan_file:
            plan = json.load(
                plan_file,
                parse_int=parse_bounded_json_int,
                parse_constant=_reject_json_constant,
            )
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: could not read {args.plan}: {exc}", file=sys.stderr)
        return 2
    except (ValueError, RecursionError, MemoryError) as exc:
        detail = str(exc) or type(exc).__name__
        print(f"ERROR: invalid JSON: {detail}", file=sys.stderr)
        return 2

    errors = validate_edit_plan(
        plan,
        require_final=args.require_final,
        for_execution=args.for_execution,
        require_cinematic=args.require_cinematic,
    )
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1

    print("Edit plan is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
