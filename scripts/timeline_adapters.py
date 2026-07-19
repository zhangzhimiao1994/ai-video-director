"""Derive human, subtitle, exchange, and FFmpeg handoffs from an edit plan."""

from __future__ import annotations

import csv
import io
import json
import math
import re
import xml.etree.ElementTree as ET
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any
from urllib.parse import quote


class AdapterError(ValueError):
    """Raised when a Canon value cannot be represented without a downgrade."""


CONSTRUCTION_FIELDS = (
    "edit_unit_id",
    "sequence",
    "shot_id",
    "asset_id",
    "asset_path",
    "take_id",
    "fallback_asset_id",
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
)

EQ_RANGES = {
    "brightness": (Decimal("-1"), Decimal("1")),
    "contrast": (Decimal("0"), Decimal("2")),
    "saturation": (Decimal("0"), Decimal("3")),
    "gamma": (Decimal("0.1"), Decimal("10")),
    "gamma_r": (Decimal("0.1"), Decimal("10")),
    "gamma_g": (Decimal("0.1"), Decimal("10")),
    "gamma_b": (Decimal("0.1"), Decimal("10")),
}

CURVES_PRESETS = {
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

SAFE_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise AdapterError(f"{label} must be an object")
    return value


def _list(value: object, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise AdapterError(f"{label} must be a list")
    return value


def _nonempty_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdapterError(f"{label} must be a non-empty string")
    return value


def _decimal(value: object, label: str, *, nonnegative: bool = False) -> Decimal:
    if isinstance(value, bool) or value is None:
        raise AdapterError(f"{label} must be a finite number")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise AdapterError(f"{label} must be a finite number") from None
    if not result.is_finite() or (nonnegative and result < 0):
        raise AdapterError(f"{label} must be a finite non-negative number")
    return result


def _fraction(value: object, label: str, *, positive: bool = False) -> Fraction:
    if isinstance(value, bool) or value is None:
        raise AdapterError(f"{label} must be a finite number")
    try:
        if isinstance(value, Fraction):
            result = value
        elif isinstance(value, Decimal):
            if not value.is_finite():
                raise ValueError
            result = Fraction(value)
        else:
            decimal_value = Decimal(str(value))
            if not decimal_value.is_finite():
                raise ValueError
            result = Fraction(decimal_value)
    except (InvalidOperation, TypeError, ValueError, ZeroDivisionError):
        raise AdapterError(f"{label} must be a finite number") from None
    if positive and result <= 0:
        raise AdapterError(f"{label} must be positive")
    return result


def _number_text(value: object, label: str) -> str:
    decimal_value = _decimal(value, label)
    normalized = decimal_value.normalize()
    if normalized == normalized.to_integral():
        return str(normalized.quantize(Decimal("1")))
    return format(normalized, "f")


def _assets(plan: dict[str, Any]) -> dict[str, dict[str, Any]]:
    assets: dict[str, dict[str, Any]] = {}
    for index, raw_binding in enumerate(
        _list(plan.get("media_bindings"), "plan.media_bindings"), start=1
    ):
        binding = _object(raw_binding, f"media binding {index}")
        asset_id = _nonempty_string(binding.get("asset_id"), f"media binding {index}.asset_id")
        if asset_id in assets:
            raise AdapterError(f"duplicate asset_id {asset_id}")
        assets[asset_id] = binding
    return assets


def _video_units(timeline: dict[str, Any]) -> list[dict[str, Any]]:
    tracks = _list(timeline.get("video_tracks"), "timeline.video_tracks")
    v1: dict[str, Any] | None = None
    for index, raw_track in enumerate(tracks, start=1):
        track = _object(raw_track, f"video track {index}")
        track_id = track.get("track_id")
        raw_units = track.get("edit_units")
        track_units = _list(raw_units, f"video track {track_id or index}.edit_units")
        selected_v1 = (
            track_id == "V1"
            and track.get("runtime_role") == "active"
            and track.get("release_role") == "first_release"
        )
        if selected_v1:
            if v1 is not None:
                raise AdapterError(
                    "timeline must contain exactly one active first_release V1 video track"
                )
            v1 = track
        elif track.get("runtime_role") == "active" and track_units:
            raise AdapterError("multi-layer video requires manual_or_unverified handling")
    if v1 is None:
        raise AdapterError(
            "timeline must contain exactly one active first_release V1 video track"
        )
    units: list[dict[str, Any]] = []
    for index, raw_unit in enumerate(
        _list(v1.get("edit_units"), "video track V1.edit_units"), start=1
    ):
        units.append(_object(raw_unit, f"edit unit {index}"))
    return units


def _timeline_id(timeline: dict[str, Any]) -> str:
    return _nonempty_string(timeline.get("timeline_id"), "timeline.timeline_id")


def _aspect_slug(
    timeline: dict[str, Any], delivery: dict[str, Any] | None = None
) -> str:
    aspect = _nonempty_string(timeline.get("aspect_ratio"), "timeline.aspect_ratio")
    if delivery is not None:
        delivery_aspect = _nonempty_string(
            delivery.get("aspect_ratio"), "delivery.aspect_ratio"
        )
        if delivery_aspect != aspect:
            raise AdapterError("delivery aspect_ratio does not match timeline")
    if re.fullmatch(r"[1-9][0-9]*:[1-9][0-9]*", aspect) is None:
        raise AdapterError("aspect_ratio must use WIDTH:HEIGHT")
    return aspect.replace(":", "x")


def construction_rows(plan: dict, timeline: dict) -> list[dict]:
    """Return one canonical construction row per V1 edit unit."""

    plan_object = _object(plan, "plan")
    timeline_object = _object(timeline, "timeline")
    assets = _assets(plan_object)
    rows: list[dict[str, Any]] = []
    for index, unit in enumerate(_video_units(timeline_object), start=1):
        asset_id = _nonempty_string(unit.get("asset_id"), f"edit unit {index}.asset_id")
        binding = assets.get(asset_id)
        if binding is None:
            raise AdapterError(f"edit unit {index} references unknown asset_id {asset_id}")
        path = _nonempty_string(
            binding.get("path_or_uri"), f"asset {asset_id}.path_or_uri"
        )
        row = {field: unit.get(field) for field in CONSTRUCTION_FIELDS}
        row["asset_path"] = path
        row["take_id"] = binding.get("take_id")
        row["fallback_asset_id"] = binding.get("fallback_asset_id")
        rows.append(row)
    return rows


def _exclusive_text(destination: Path, content: str) -> Path:
    try:
        destination_path = Path(destination)
    except (TypeError, ValueError):
        raise AdapterError("destination must be a filesystem path") from None
    if destination_path.exists():
        raise AdapterError(f"destination already exists: {destination_path}")
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with destination_path.open("x", encoding="utf-8", newline="") as output:
            output.write(content)
    except FileExistsError:
        raise AdapterError(f"destination already exists: {destination_path}") from None
    return destination_path


def _cell(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _markdown_cell(value: object) -> str:
    return _cell(value).replace("|", "\\|").replace("\r", " ").replace("\n", "<br>")


def _markdown_table(fields: tuple[str, ...], rows: list[dict[str, Any]]) -> str:
    header = "| " + " | ".join(fields) + " |"
    separator = "| " + " | ".join("---" for _ in fields) + " |"
    body = [
        "| " + " | ".join(_markdown_cell(row.get(field)) for field in fields) + " |"
        for row in rows
    ]
    return "\n".join((header, separator, *body))


def _construction_appendices(
    plan: dict[str, Any], timeline: dict[str, Any]
) -> str:
    timeline_id = _timeline_id(timeline)
    assets = _assets(plan)

    track_rows: list[dict[str, Any]] = []
    for raw_track in _list(timeline.get("video_tracks"), "timeline.video_tracks"):
        track = _object(raw_track, "video track")
        edit_units = _list(track.get("edit_units"), "video track.edit_units")
        track_rows.append(
            {
                "kind": "video",
                "track_id": track.get("track_id"),
                "runtime_role": track.get("runtime_role"),
                "release_role": track.get("release_role"),
                "item_count": len(edit_units),
            }
        )
    for track_id in _list(timeline.get("audio_track_refs"), "timeline.audio_track_refs"):
        track_rows.append(
            {"kind": "audio", "track_id": track_id, "item_count": "mounted"}
        )
    for track_id in _list(timeline.get("text_track_refs"), "timeline.text_track_refs"):
        track_rows.append(
            {"kind": "text", "track_id": track_id, "item_count": "mounted"}
        )

    media_rows = [
        {
            "asset_id": asset_id,
            "path_or_uri": binding.get("path_or_uri"),
            "binding_scope": binding.get("binding_scope"),
            "target_id": binding.get("target_id"),
            "take_id": binding.get("take_id"),
            "fallback_asset_id": binding.get("fallback_asset_id"),
            "file_status": binding.get("file_status"),
            "rights_status": binding.get("rights_status"),
            "probe_status": binding.get("probe_status"),
        }
        for asset_id, binding in assets.items()
    ]

    subtitle_rows = [
        {
            "text_cue_id": cue.get("text_cue_id"),
            "timeline_in_seconds": cue.get("timeline_in_seconds"),
            "timeline_out_seconds": cue.get("timeline_out_seconds"),
            "text": cue.get("text"),
        }
        for cue in _mounted_text_cues(plan, timeline)
    ]

    audio_tracks: dict[str, dict[str, Any]] = {}
    for raw_track in _list(plan.get("audio_tracks"), "plan.audio_tracks"):
        track = _object(raw_track, "audio track")
        track_id = _nonempty_string(track.get("audio_track_id"), "audio_track_id")
        audio_tracks[track_id] = track
    audio_rows = []
    for track_id in _list(timeline.get("audio_track_refs"), "timeline.audio_track_refs"):
        if track_id not in audio_tracks:
            raise AdapterError(f"timeline references unknown audio track {track_id}")
        track = audio_tracks[track_id]
        for raw_cue in _list(track.get("cues"), f"audio track {track_id}.cues"):
            cue = _object(raw_cue, f"audio cue on {track_id}")
            audio_rows.append(
                {
                    "audio_track_id": track_id,
                    "audio_cue_id": cue.get("audio_cue_id"),
                    "asset_id": cue.get("asset_id"),
                    "timeline_in_seconds": cue.get("timeline_in_seconds"),
                    "timeline_out_seconds": cue.get("timeline_out_seconds"),
                    "gain_db": cue.get("gain_db"),
                    "target_lufs": track.get("target_lufs"),
                    "true_peak_db": track.get("true_peak_db"),
                }
            )

    look_plan = _object(plan.get("look_plan"), "plan.look_plan")
    look_rows = [
        {
            "input_color_space": look_plan.get("input_color_space"),
            "output_color_space": look_plan.get("output_color_space"),
            "matching_status": look_plan.get("matching_status"),
            "instructions": look_plan.get("instructions"),
            "ffmpeg_filters": look_plan.get("ffmpeg_filters"),
        }
    ]
    export_rows = []
    for raw_delivery in _list(plan.get("delivery_specs"), "plan.delivery_specs"):
        delivery = _object(raw_delivery, "delivery spec")
        if delivery.get("timeline_id") == timeline_id:
            export_rows.append(
                {
                    field: delivery.get(field)
                    for field in (
                        "delivery_id",
                        "version_role",
                        "resolution",
                        "frame_rate",
                        "codec",
                        "bitrate",
                        "filename",
                        "subtitle_mode",
                        "audio_mode",
                        "look_mode",
                    )
                }
            )

    checklist = [
        f"- [{'x' if unit.get('approval_status') == 'approved' else ' '}] "
        f"{unit.get('edit_unit_id')}: approval={unit.get('approval_status')}, "
        f"safe_area={unit.get('safe_area')}, risks={_cell(unit.get('risk_triggers'))}"
        for unit in _video_units(timeline)
    ]
    checklist.extend(
        f"- [{'x' if binding.get('file_status') == 'online' and binding.get('rights_status') == 'cleared' and binding.get('probe_status') == 'verified' else ' '}] "
        f"{asset_id}: file={binding.get('file_status')}, rights={binding.get('rights_status')}, "
        f"probe={binding.get('probe_status')}"
        for asset_id, binding in assets.items()
    )

    return "\n\n".join(
        (
            "## Track Layout\n\n"
            + _markdown_table(
                ("kind", "track_id", "runtime_role", "release_role", "item_count"),
                track_rows,
            ),
            "## Media Inventory and Relink Map\n\n"
            + _markdown_table(
                (
                    "asset_id",
                    "path_or_uri",
                    "binding_scope",
                    "target_id",
                    "take_id",
                    "fallback_asset_id",
                    "file_status",
                    "rights_status",
                    "probe_status",
                ),
                media_rows,
            ),
            "## Subtitle Table\n\n"
            + _markdown_table(
                (
                    "text_cue_id",
                    "timeline_in_seconds",
                    "timeline_out_seconds",
                    "text",
                ),
                subtitle_rows,
            ),
            "## Audio Cue Sheet\n\n"
            + _markdown_table(
                (
                    "audio_track_id",
                    "audio_cue_id",
                    "asset_id",
                    "timeline_in_seconds",
                    "timeline_out_seconds",
                    "gain_db",
                    "target_lufs",
                    "true_peak_db",
                ),
                audio_rows,
            ),
            "## Look / Color Sheet\n\n"
            + _markdown_table(
                (
                    "input_color_space",
                    "output_color_space",
                    "matching_status",
                    "instructions",
                    "ffmpeg_filters",
                ),
                look_rows,
            ),
            "## Export Matrix\n\n"
            + _markdown_table(
                (
                    "delivery_id",
                    "version_role",
                    "resolution",
                    "frame_rate",
                    "codec",
                    "bitrate",
                    "filename",
                    "subtitle_mode",
                    "audio_mode",
                    "look_mode",
                ),
                export_rows,
            ),
            "## Acceptance Checklist\n\n" + "\n".join(checklist),
        )
    )


def write_construction_markdown(plan, timeline, destination: Path) -> Path:
    plan_object = _object(plan, "plan")
    rows = construction_rows(plan_object, timeline)
    timeline_object = _object(timeline, "timeline")
    title = f"# Construction Sheet: {_timeline_id(timeline_object)}"
    content = "\n\n".join(
        (
            title,
            _markdown_table(CONSTRUCTION_FIELDS, rows),
            _construction_appendices(plan_object, timeline_object),
        )
    )
    return _exclusive_text(destination, content + "\n")


def write_construction_csv(plan, timeline, destination: Path) -> Path:
    rows = construction_rows(plan, timeline)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CONSTRUCTION_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({field: _cell(row[field]) for field in CONSTRUCTION_FIELDS})
    return _exclusive_text(destination, buffer.getvalue())


def srt_timestamp(seconds: object) -> str:
    """Format a non-negative Decimal-compatible value as an SRT timestamp."""

    value = _decimal(seconds, "seconds", nonnegative=True)
    milliseconds = int((value * 1000).quantize(Decimal("1")))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    whole_seconds, millis = divmod(remainder, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole_seconds:02d},{millis:03d}"


def _mounted_text_cues(plan: dict[str, Any], timeline: dict[str, Any]) -> list[dict[str, Any]]:
    track_refs = _list(timeline.get("text_track_refs"), "timeline.text_track_refs")
    ref_ids = {
        _nonempty_string(value, "timeline text track reference") for value in track_refs
    }
    tracks: dict[str, dict[str, Any]] = {}
    for index, raw_track in enumerate(_list(plan.get("text_tracks"), "plan.text_tracks"), start=1):
        track = _object(raw_track, f"text track {index}")
        track_id = _nonempty_string(track.get("text_track_id"), f"text track {index}.text_track_id")
        tracks[track_id] = track
    unknown = ref_ids.difference(tracks)
    if unknown:
        raise AdapterError(f"timeline references unknown text track {sorted(unknown)[0]}")
    cues: list[dict[str, Any]] = []
    for track_id in track_refs:
        track = tracks[track_id]
        for index, raw_cue in enumerate(_list(track.get("cues"), f"text track {track_id}.cues"), start=1):
            cue = _object(raw_cue, f"text cue {index} on {track_id}")
            _nonempty_string(cue.get("text_cue_id"), f"text cue {index}.text_cue_id")
            _nonempty_string(cue.get("text"), f"text cue {index}.text")
            cue_in = _decimal(cue.get("timeline_in_seconds"), "text cue timeline_in", nonnegative=True)
            cue_out = _decimal(cue.get("timeline_out_seconds"), "text cue timeline_out", nonnegative=True)
            if cue_out <= cue_in:
                raise AdapterError("text cue timeline_out must be after timeline_in")
            cues.append(cue)
    return sorted(
        cues,
        key=lambda cue: (
            _decimal(cue["timeline_in_seconds"], "text cue timeline_in"),
            _decimal(cue["timeline_out_seconds"], "text cue timeline_out"),
            cue["text_cue_id"],
        ),
    )


def write_srt(plan, timeline, destination: Path) -> Path:
    plan_object = _object(plan, "plan")
    timeline_object = _object(timeline, "timeline")
    blocks = []
    for number, cue in enumerate(_mounted_text_cues(plan_object, timeline_object), start=1):
        blocks.append(
            f"{number}\n"
            f"{srt_timestamp(cue['timeline_in_seconds'])} --> "
            f"{srt_timestamp(cue['timeline_out_seconds'])}\n"
            f"{cue['text']}"
        )
    content = "\n\n".join(blocks) + ("\n" if blocks else "")
    return _exclusive_text(destination, content)


def _frame_rate(timeline: dict[str, Any]) -> Fraction:
    return _fraction(timeline.get("frame_rate"), "timeline.frame_rate", positive=True)


def _frame_count(value: object, rate: Fraction, label: str) -> int:
    frames = _fraction(value, label) * rate
    if frames.denominator != 1:
        raise AdapterError(f"{label} is not on a frame boundary")
    return frames.numerator


def _json_rate(rate: Fraction) -> int | float:
    return rate.numerator if rate.denominator == 1 else float(rate)


def _rational_time(frames: int, rate: Fraction) -> dict[str, Any]:
    return {
        "OTIO_SCHEMA": "RationalTime.1",
        "value": frames,
        "rate": _json_rate(rate),
    }


def _validated_unit_frames(
    units: list[dict[str, Any]], rate: Fraction
) -> list[dict[str, int]]:
    result = []
    fields = (
        "timeline_in_seconds",
        "timeline_out_seconds",
        "duration_seconds",
        "source_in_seconds",
        "source_out_seconds",
    )
    for index, unit in enumerate(units, start=1):
        unit_id = unit.get("edit_unit_id", index)
        converted = {
            field: _frame_count(unit.get(field), rate, f"edit unit {unit_id}.{field}")
            for field in fields
        }
        if converted["timeline_out_seconds"] - converted["timeline_in_seconds"] != converted["duration_seconds"]:
            raise AdapterError(f"edit unit {unit_id} timeline duration is inconsistent")
        if converted["source_out_seconds"] <= converted["source_in_seconds"]:
            raise AdapterError(f"edit unit {unit_id} source range is invalid")
        if converted["source_out_seconds"] - converted["source_in_seconds"] != converted["duration_seconds"]:
            raise AdapterError(f"edit unit {unit_id} source duration is inconsistent")
        result.append(converted)
    return result


def _media_uri(path_value: object) -> str:
    value = _nonempty_string(path_value, "media path")
    windows_path = PureWindowsPath(value)
    if windows_path.is_absolute():
        rendered = windows_path.as_posix()
        return "file:///" + quote(rendered, safe="/:")
    posix_path = PurePosixPath(value)
    if posix_path.is_absolute():
        return "file://" + quote(posix_path.as_posix(), safe="/")
    return Path(value).resolve().as_uri()


def write_otio(plan, timeline, destination: Path) -> Path:
    plan_object = _object(plan, "plan")
    timeline_object = _object(timeline, "timeline")
    timeline_id = _timeline_id(timeline_object)
    assets = _assets(plan_object)
    units = _video_units(timeline_object)
    _validate_first_release_units(units)
    rate = _frame_rate(timeline_object)
    _frame_count(
        timeline_object.get("duration_seconds"), rate, "timeline.duration_seconds"
    )
    frame_ranges = _validated_unit_frames(units, rate)
    children = []
    for index, (unit, frames) in enumerate(zip(units, frame_ranges), start=1):
        asset_id = _nonempty_string(unit.get("asset_id"), f"edit unit {index}.asset_id")
        binding = assets.get(asset_id)
        if binding is None:
            raise AdapterError(f"edit unit {index} references unknown asset_id {asset_id}")
        children.append(
            {
                "OTIO_SCHEMA": "Clip.2",
                "name": _nonempty_string(unit.get("edit_unit_id"), f"edit unit {index}.edit_unit_id"),
                "media_reference": {
                    "OTIO_SCHEMA": "ExternalReference.1",
                    "target_url": _media_uri(binding.get("path_or_uri")),
                },
                "source_range": {
                    "OTIO_SCHEMA": "TimeRange.1",
                    "start_time": _rational_time(frames["source_in_seconds"], rate),
                    "duration": _rational_time(frames["duration_seconds"], rate),
                },
                "metadata": {
                    "edit_unit_id": unit["edit_unit_id"],
                    "timeline_in_frames": frames["timeline_in_seconds"],
                    "timeline_out_frames": frames["timeline_out_seconds"],
                },
            }
        )
    document = {
        "OTIO_SCHEMA": "Timeline.1",
        "name": timeline_id,
        "global_start_time": _rational_time(0, rate),
        "tracks": {
            "OTIO_SCHEMA": "Stack.1",
            "name": f"{timeline_id} tracks",
            "children": [
                {
                    "OTIO_SCHEMA": "Track.1",
                    "name": "V1",
                    "kind": "Video",
                    "children": children,
                }
            ],
        },
    }
    content = json.dumps(document, ensure_ascii=False, indent=2) + "\n"
    return _exclusive_text(destination, content)


def _fcpx_time_from_frames(frames: int, rate: Fraction) -> str:
    seconds = Fraction(frames, 1) / rate
    if seconds.denominator == 1:
        return f"{seconds.numerator}s"
    return f"{seconds.numerator}/{seconds.denominator}s"


def _resolution(timeline: dict[str, Any]) -> tuple[int, int]:
    value = _nonempty_string(timeline.get("resolution"), "timeline.resolution")
    match = re.fullmatch(r"([1-9][0-9]*)x([1-9][0-9]*)", value)
    if match is None:
        raise AdapterError("timeline.resolution must be WIDTHxHEIGHT")
    return int(match.group(1)), int(match.group(2))


def write_fcpxml(plan, timeline, destination: Path) -> Path:
    plan_object = _object(plan, "plan")
    timeline_object = _object(timeline, "timeline")
    timeline_id = _timeline_id(timeline_object)
    assets = _assets(plan_object)
    units = _video_units(timeline_object)
    _validate_first_release_units(units)
    rate = _frame_rate(timeline_object)
    frame_ranges = _validated_unit_frames(units, rate)
    width, height = _resolution(timeline_object)
    duration_frames = _frame_count(
        timeline_object.get("duration_seconds"), rate, "timeline.duration_seconds"
    )

    root = ET.Element("fcpxml", {"version": "1.10"})
    resources = ET.SubElement(root, "resources")
    ET.SubElement(
        resources,
        "format",
        {
            "id": "r1",
            "name": f"FFVideoFormat{width}x{height}",
            "frameDuration": _fcpx_time_from_frames(1, rate),
            "width": str(width),
            "height": str(height),
        },
    )
    resource_ids: dict[str, str] = {}
    for asset_id, binding in assets.items():
        resource_id = f"r{len(resource_ids) + 2}"
        resource_ids[asset_id] = resource_id
        attributes = {
            "id": resource_id,
            "name": asset_id,
            "src": _media_uri(binding.get("path_or_uri")),
        }
        if binding.get("duration_seconds") is not None:
            asset_duration = _frame_count(
                binding.get("duration_seconds"),
                rate,
                f"asset {asset_id}.duration_seconds",
            )
            attributes.update(
                {
                    "start": "0s",
                    "duration": _fcpx_time_from_frames(asset_duration, rate),
                }
            )
        if binding.get("source_type") == "post_asset":
            attributes["hasAudio"] = "1"
        else:
            attributes.update({"hasVideo": "1", "format": "r1"})
            if isinstance(binding.get("audio_channels"), int) and binding["audio_channels"] > 0:
                attributes["hasAudio"] = "1"
        ET.SubElement(resources, "asset", attributes)

    library = ET.SubElement(root, "library")
    event = ET.SubElement(library, "event", {"name": "Finished Film Handoff"})
    project = ET.SubElement(event, "project", {"name": timeline_id})
    sequence = ET.SubElement(
        project,
        "sequence",
        {
            "format": "r1",
            "duration": _fcpx_time_from_frames(duration_frames, rate),
            "tcStart": "0s",
            "tcFormat": "NDF",
        },
    )
    spine = ET.SubElement(sequence, "spine")
    for unit, frames in zip(units, frame_ranges):
        asset_id = unit["asset_id"]
        ET.SubElement(
            spine,
            "asset-clip",
            {
                "name": str(unit.get("edit_unit_id", asset_id)),
                "ref": resource_ids[asset_id],
                "offset": _fcpx_time_from_frames(frames["timeline_in_seconds"], rate),
                "start": _fcpx_time_from_frames(frames["source_in_seconds"], rate),
                "duration": _fcpx_time_from_frames(frames["duration_seconds"], rate),
            },
        )
    ET.indent(root, space="  ")
    content = ET.tostring(root, encoding="unicode", xml_declaration=False)
    return _exclusive_text(destination, '<?xml version="1.0" encoding="UTF-8"?>\n' + content + "\n")


def write_jianying_instructions(plan, destination: Path) -> Path:
    plan_object = _object(plan, "plan")
    assets = _assets(plan_object)
    raw_timelines = _list(plan_object.get("timelines"), "plan.timelines")
    timelines = [_object(value, f"timeline {index}") for index, value in enumerate(raw_timelines, 1)]
    ordered_asset_ids: list[str] = []
    timeline_sections: list[str] = []
    for selected in timelines:
        timeline_id = _timeline_id(selected)
        aspect = _nonempty_string(selected.get("aspect_ratio"), f"timeline {timeline_id}.aspect_ratio")
        aspect_slug = _aspect_slug(selected)
        construction_filename = f"edit_construction_{aspect_slug}.csv"
        subtitle_filename = f"subtitles_{aspect_slug}.srt"
        rows = construction_rows(plan_object, selected)
        lines = [
            f"### {timeline_id} ({aspect})",
            "",
            f"Import construction CSV `{construction_filename}` and SRT "
            f"`{subtitle_filename}`, then apply this track mapping and effect "
            "parameters in order:",
            "",
        ]
        for row in rows:
            asset_id = row["asset_id"]
            if asset_id not in ordered_asset_ids:
                ordered_asset_ids.append(asset_id)
            lines.append(
                f"- {row['sequence']}. {row['edit_unit_id']} -> V1, media {asset_id}, "
                f"{row['timeline_in_seconds']}-{row['timeline_out_seconds']}s; "
                f"scale={row['scale']}, position={_cell(row['position'])}, "
                f"reframe={row['reframe']}, stabilization={row['stabilization']}."
            )
        timeline_sections.append("\n".join(lines))
    for asset_id, binding in assets.items():
        if (
            binding.get("source_type") == "post_asset"
            and asset_id not in ordered_asset_ids
        ):
            ordered_asset_ids.append(asset_id)
    media_lines = []
    for index, asset_id in enumerate(ordered_asset_ids, start=1):
        binding = assets.get(asset_id)
        if binding is None:
            raise AdapterError(f"ordered media references unknown asset_id {asset_id}")
        path = _nonempty_string(
            binding.get("path_or_uri"), f"asset {asset_id}.path_or_uri"
        )
        safe_asset_id = re.sub(r"[^A-Za-z0-9._-]", "_", asset_id).strip(".")
        suffix = PureWindowsPath(path.split("?", 1)[0]).suffix.lower()
        if re.fullmatch(r"\.[a-z0-9]{1,10}", suffix) is None:
            suffix = ""
        rename_target = f"{index:03d}_{safe_asset_id or 'asset'}{suffix}"
        media_lines.append(
            f"{index}. {asset_id}: {path} -> {rename_target}"
        )
    version_policy = _object(plan_object.get("execution"), "plan.execution").get("version_policy")
    content = (
        "# Jianying / CapCut Assembly Instructions\n\n"
        "Status: manual_or_unverified. Use official application import and manual assembly only.\n\n"
        f"Version policy: {version_policy}; always create_new and preserve source media.\n\n"
        "## Ordered media\n\n"
        + "\n".join(media_lines)
        + "\n\n## Timeline assembly\n\n"
        + "\n\n".join(timeline_sections)
        + "\n\nDo not fabricate or reverse engineer a private project file. Save a new project through the official application UI.\n"
    )
    return _exclusive_text(destination, content)


def _delivery_for_timeline(
    plan: dict[str, Any], timeline_id: str, supplied: dict | None
) -> dict[str, Any]:
    if supplied is not None:
        selected = _object(supplied, "delivery_spec")
        if selected.get("timeline_id") != timeline_id:
            raise AdapterError("delivery_spec.timeline_id does not match timeline")
        return selected
    matches = []
    for index, raw_delivery in enumerate(
        _list(plan.get("delivery_specs"), "plan.delivery_specs"), start=1
    ):
        item = _object(raw_delivery, f"delivery spec {index}")
        if item.get("timeline_id") == timeline_id:
            matches.append(item)
    if len(matches) != 1:
        raise AdapterError(f"expected exactly one delivery spec for timeline {timeline_id}")
    return matches[0]


def _lexical_path(value: object, label: str):
    text = _nonempty_string(value, label)
    if any(ord(character) < 32 or ord(character) == 127 for character in text):
        raise AdapterError(f"{label} contains control characters")
    windows = PureWindowsPath(text)
    if windows.drive and not windows.is_absolute():
        raise AdapterError(f"{label} is drive-relative")
    if windows.is_absolute():
        style, parsed = "windows", windows
    elif text.startswith("/"):
        style, parsed = "posix", PurePosixPath(text)
    else:
        style, parsed = "relative", PurePosixPath(text.replace("\\", "/"))
    if ".." in parsed.parts:
        raise AdapterError(f"{label} contains an unsafe '..' segment")
    return style, parsed


def _path_within(candidate, root) -> bool:
    candidate_style, candidate_path = candidate
    root_style, root_path = root
    if candidate_style != root_style:
        return False
    if candidate_style == "windows" and candidate_path.drive.lower() != root_path.drive.lower():
        return False
    try:
        candidate_path.relative_to(root_path)
    except ValueError:
        return False
    return True


def _safe_generated_output(version_dir: Path, relative: str) -> Path:
    relative_path = Path(relative)
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise AdapterError("all FFmpeg outputs must remain inside version_dir")
    version = version_dir.resolve()
    candidate = (version / relative_path).resolve()
    try:
        candidate.relative_to(version)
    except ValueError:
        raise AdapterError("all FFmpeg outputs must remain inside version_dir") from None
    return candidate


def _validate_version_dir(version_dir: Path) -> Path:
    try:
        resolved = Path(version_dir).resolve()
    except (TypeError, ValueError, OSError):
        raise AdapterError("version_dir must be a filesystem path") from None
    if str(resolved) == resolved.anchor:
        raise AdapterError("version_dir must not be a filesystem root")
    return resolved


def _validate_first_release_units(units: list[dict[str, Any]]) -> None:
    for index, unit in enumerate(units, start=1):
        unit_id = unit.get("edit_unit_id", index)
        for field in ("transition_in", "transition_out"):
            transition = unit.get(field)
            if not isinstance(transition, str) or transition not in {"hard_cut", "end"}:
                raise AdapterError(
                    f"unsupported transition {transition} in edit unit {unit_id}"
                )
        effects = unit.get("effects", [])
        if not isinstance(effects, list) or effects:
            raise AdapterError(f"unsupported effect in edit unit {unit_id}")
        speed = _decimal(unit.get("speed"), f"edit unit {unit_id}.speed")
        freeze = _decimal(unit.get("freeze_frames"), f"edit unit {unit_id}.freeze_frames")
        if speed != 1:
            raise AdapterError(f"unsupported speed effect in edit unit {unit_id}")
        if freeze != 0:
            raise AdapterError(f"unsupported freeze effect in edit unit {unit_id}")
        if unit.get("stabilization") != "none":
            raise AdapterError(f"unsupported stabilization effect in edit unit {unit_id}")


def _authorized_media(binding: dict[str, Any]) -> bool:
    source_type = binding.get("source_type")
    return (
        isinstance(source_type, str)
        and source_type in {"local_file", "post_asset"}
        and binding.get("file_status") == "online"
        and binding.get("rights_status") == "cleared"
        and binding.get("probe_status") == "verified"
    )


def _escape_filter_path(value: str, label: str) -> str:
    if any(
        ord(character) < 32
        or ord(character) == 127
        or character in "'\";,[]="
        for character in value
    ):
        raise AdapterError(f"{label} is unsafe")
    colon_positions = [index for index, character in enumerate(value) if character == ":"]
    windows_drive = (
        colon_positions == [1]
        and value[0].isalpha()
        and PureWindowsPath(value).is_absolute()
    )
    if colon_positions and not windows_drive:
        raise AdapterError(f"{label} is unsafe")
    _lexical_path(value, label)
    escaped = value.replace("\\", "\\\\").replace(":", "\\:")
    return "'" + escaped + "'"


def compile_subtitle_artifacts(
    plan,
    timeline,
    version_dir: Path,
    delivery_spec: dict | None = None,
) -> dict:
    """Compile subtitle artifacts and picture-filter intent without writing files."""

    plan_object = _object(plan, "plan")
    timeline_object = _object(timeline, "timeline")
    timeline_id = _timeline_id(timeline_object)
    version = _validate_version_dir(version_dir)
    selected_delivery = _delivery_for_timeline(
        plan_object, timeline_id, delivery_spec
    )
    mode = selected_delivery.get("subtitle_mode")
    if not isinstance(mode, str) or mode not in {"none", "sidecar", "burn_in"}:
        raise AdapterError(f"unsupported subtitle_mode {mode}")
    if mode == "none":
        return {
            "mode": "none",
            "srt_path": None,
            "manifest": [],
            "video_filter": None,
        }
    aspect_slug = _aspect_slug(timeline_object, selected_delivery)
    srt_path = _safe_generated_output(version, f"subtitles_{aspect_slug}.srt")
    artifact_type = (
        "subtitle_sidecar" if mode == "sidecar" else "subtitle_burn_source"
    )
    return {
        "mode": mode,
        "srt_path": str(srt_path),
        "manifest": [
            {
                "artifact_type": artifact_type,
                "timeline_id": timeline_id,
                "path": str(srt_path),
            }
        ],
        "video_filter": (
            None
            if mode == "sidecar"
            else "subtitles=filename="
            + _escape_filter_path(str(srt_path), "subtitle path")
        ),
    }


def _compile_look_filters(
    plan: dict[str, Any], assets: dict[str, dict[str, Any]], mode: object
) -> list[str]:
    if mode == "none":
        return []
    if mode != "approved":
        raise AdapterError(f"unsupported look_mode {mode}")
    look_plan = _object(plan.get("look_plan"), "plan.look_plan")
    raw_filters = _list(look_plan.get("ffmpeg_filters"), "look filters")
    if not raw_filters:
        raise AdapterError("look filters must not be empty for approved look_mode")
    compiled: list[str] = []
    for index, raw_filter in enumerate(raw_filters, start=1):
        if not isinstance(raw_filter, dict):
            raise AdapterError(f"look filter {index} must be an object, not a raw string")
        keys = set(raw_filter)
        if keys == {"name", "params"}:
            name = raw_filter["name"]
        elif keys == {"filter", "params"}:
            name = raw_filter["filter"]
        else:
            raise AdapterError(
                f"look filter {index} must have exact shape {{name, params}} or {{filter, params}}"
            )
        if not isinstance(name, str) or name not in {"eq", "curves", "lut3d"}:
            raise AdapterError(f"look filter {index} uses unsupported filter {name}")
        params = raw_filter.get("params")
        if not isinstance(params, dict):
            raise AdapterError(f"look filter {index} params must be an object")
        if name == "eq":
            values = []
            for key, value in params.items():
                if key not in EQ_RANGES:
                    raise AdapterError(f"look filter eq has unsupported param {key}")
                converted = _decimal(value, f"look filter eq param {key}")
                minimum, maximum = EQ_RANGES[key]
                if not minimum <= converted <= maximum:
                    raise AdapterError(f"look filter eq param {key} is out of range")
                values.append(f"{key}={_number_text(converted, key)}")
            compiled.append("eq=" + ":".join(values))
        elif name == "curves":
            preset = params.get("preset")
            if (
                set(params) != {"preset"}
                or not isinstance(preset, str)
                or preset not in CURVES_PRESETS
            ):
                raise AdapterError("look filter curves preset is unsafe")
            compiled.append(f"curves=preset={params['preset']}")
        else:
            if set(params) != {"asset_id"}:
                raise AdapterError("look filter lut3d must use only asset_id")
            asset_id = params.get("asset_id")
            if not isinstance(asset_id, str) or SAFE_ID.fullmatch(asset_id) is None:
                raise AdapterError("look filter lut3d asset_id is unsafe")
            binding = assets.get(asset_id)
            if binding is None:
                raise AdapterError(f"look filter lut3d references unknown asset_id {asset_id}")
            if not _authorized_media(binding):
                raise AdapterError(f"look filter lut3d asset {asset_id} is not authorized")
            path = _nonempty_string(binding.get("path_or_uri"), f"look filter lut3d asset {asset_id} path")
            if not path.lower().endswith(".cube"):
                raise AdapterError("look filter lut3d must use a .cube asset")
            candidate = _lexical_path(path, "look filter lut3d path")
            execution = _object(plan.get("execution"), "plan.execution")
            roots = _list(execution.get("authorized_media_roots"), "authorized_media_roots")
            parsed_roots = [_lexical_path(root, "authorized media root") for root in roots]
            if not any(_path_within(candidate, root) for root in parsed_roots):
                raise AdapterError("look filter lut3d asset is outside authorized media roots")
            compiled.append(f"lut3d=file={_escape_filter_path(path, 'look filter lut3d path')}")
    return compiled


def _mounted_audio_cues(
    plan: dict[str, Any], timeline: dict[str, Any], units: list[dict[str, Any]], assets: dict[str, dict[str, Any]]
) -> list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]:
    refs = _list(timeline.get("audio_track_refs"), "timeline.audio_track_refs")
    ref_ids = {_nonempty_string(value, "audio track reference") for value in refs}
    referenced_cue_ids: set[str] = set()
    for unit in units:
        for cue_id in _list(unit.get("audio_cue_ids"), "edit unit.audio_cue_ids"):
            referenced_cue_ids.add(_nonempty_string(cue_id, "audio cue reference"))
    tracks: dict[str, dict[str, Any]] = {}
    for index, raw_track in enumerate(_list(plan.get("audio_tracks"), "plan.audio_tracks"), start=1):
        track = _object(raw_track, f"audio track {index}")
        track_id = _nonempty_string(track.get("audio_track_id"), f"audio track {index}.audio_track_id")
        tracks[track_id] = track
    unknown_tracks = ref_ids.difference(tracks)
    if unknown_tracks:
        raise AdapterError(f"timeline references unknown audio track {sorted(unknown_tracks)[0]}")
    cues_by_id: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
    for track_id in refs:
        track = tracks[track_id]
        for index, raw_cue in enumerate(_list(track.get("cues"), f"audio track {track_id}.cues"), start=1):
            cue = _object(raw_cue, f"audio cue {index} on {track_id}")
            cue_id = _nonempty_string(cue.get("audio_cue_id"), f"audio cue {index}.audio_cue_id")
            if cue_id in cues_by_id:
                raise AdapterError(f"duplicate mounted audio cue {cue_id}")
            cues_by_id[cue_id] = (cue, track)
    unknown_cues = referenced_cue_ids.difference(cues_by_id)
    if unknown_cues:
        raise AdapterError(f"unknown audio cue {sorted(unknown_cues)[0]}")
    compiled = []
    for cue_id in sorted(
        cues_by_id,
        key=lambda value: (
            _decimal(
                cues_by_id[value][0].get("timeline_in_seconds"),
                "audio cue timeline_in",
            ),
            value,
        ),
    ):
        cue, track = cues_by_id[cue_id]
        asset_id = cue.get("asset_id")
        binding = assets.get(asset_id) if isinstance(asset_id, str) else None
        if binding is None:
            raise AdapterError(f"audio asset {asset_id} is unknown")
        if binding.get("source_type") != "post_asset" or not _authorized_media(binding):
            raise AdapterError(f"audio asset {asset_id} is not authorized")
        scope = binding.get("binding_scope")
        target_id = binding.get("target_id")
        if scope == "project":
            if target_id != plan.get("source_package_id"):
                raise AdapterError(
                    f"audio asset {asset_id} scope target does not match project"
                )
        elif scope == "timeline":
            if target_id != timeline.get("timeline_id"):
                raise AdapterError(
                    f"audio asset {asset_id} scope target does not match timeline"
                )
        elif scope == "edit_unit":
            owners = [
                unit
                for unit in units
                if cue_id
                in _list(unit.get("audio_cue_ids"), "edit unit.audio_cue_ids")
            ]
            if (
                len(owners) != 1
                or owners[0].get("edit_unit_id") != target_id
            ):
                raise AdapterError(
                    f"audio asset {asset_id} scope requires its unique target edit unit"
                )
        else:
            raise AdapterError(
                f"audio asset {asset_id} scope must be edit_unit, timeline, or project"
            )
        compiled.append((cue, track, binding))
    return compiled


def _audio_filter_graph(
    cues: list[tuple[dict[str, Any], dict[str, Any], dict[str, Any]]]
) -> str:
    if not cues:
        raise AdapterError("final_mix requires at least one mounted local audio cue")
    chains = []
    labels = []
    for index, (cue, _track, _binding) in enumerate(cues):
        cue_in = _decimal(cue.get("timeline_in_seconds"), "audio cue timeline_in", nonnegative=True)
        cue_out = _decimal(cue.get("timeline_out_seconds"), "audio cue timeline_out", nonnegative=True)
        if cue_out <= cue_in:
            raise AdapterError("audio cue timeline_out must be after timeline_in")
        duration = cue_out - cue_in
        delay = int((cue_in * 1000).quantize(Decimal("1")))
        gain = _decimal(cue.get("gain_db", 0), "audio cue gain_db")
        label = f"a{index}"
        labels.append(f"[{label}]")
        chains.append(
            f"[{index + 1}:a]atrim=start=0:end={_number_text(duration, 'audio duration')},"
            f"asetpts=PTS-STARTPTS,adelay={delay}|{delay},"
            f"volume={_number_text(gain, 'audio gain')}dB[{label}]"
        )
    target_lufs = _decimal(cues[0][1].get("target_lufs", -14), "audio target_lufs")
    true_peak = _decimal(cues[0][1].get("true_peak_db", -1), "audio true_peak_db")
    chains.append(
        "".join(labels)
        + f"amix=inputs={len(labels)}:normalize=0,"
        + f"loudnorm=I={_number_text(target_lufs, 'target_lufs')}:"
        + f"TP={_number_text(true_peak, 'true_peak_db')}:LRA=11[aout]"
    )
    return ";".join(chains)


def ffmpeg_command_plan(
    plan,
    timeline,
    version_dir: Path,
    delivery_spec: dict | None = None,
    ffmpeg_path: str = "ffmpeg",
) -> list[list[str]]:
    """Compile, but never execute or materialize, an FFmpeg argv plan."""

    plan_object = _object(plan, "plan")
    timeline_object = _object(timeline, "timeline")
    executable = _nonempty_string(ffmpeg_path, "ffmpeg_path")
    version = _validate_version_dir(version_dir)
    timeline_id = _timeline_id(timeline_object)
    selected_delivery = _delivery_for_timeline(plan_object, timeline_id, delivery_spec)
    if selected_delivery.get("resolution") != timeline_object.get("resolution"):
        raise AdapterError("delivery resolution does not match timeline")
    if _fraction(selected_delivery.get("frame_rate"), "delivery.frame_rate", positive=True) != _frame_rate(timeline_object):
        raise AdapterError("delivery frame_rate does not match timeline")
    width, height = _resolution(timeline_object)
    rate = _frame_rate(timeline_object)
    rate_text = _number_text(Decimal(rate.numerator) / Decimal(rate.denominator), "frame rate")
    units = _video_units(timeline_object)
    _validate_first_release_units(units)
    assets = _assets(plan_object)

    subtitle_plan = compile_subtitle_artifacts(
        plan_object, timeline_object, version, selected_delivery
    )
    audio_mode = selected_delivery.get("audio_mode")
    if not isinstance(audio_mode, str) or audio_mode not in {"temporary_or_silent", "final_mix", "none"}:
        raise AdapterError(f"unsupported audio_mode {audio_mode}")
    version_role = selected_delivery.get("version_role")
    if (
        isinstance(version_role, str)
        and version_role in {"fine_cut", "final_master"}
        and audio_mode == "temporary_or_silent"
    ):
        raise AdapterError("fine_cut/final_master cannot silently drop planned audio")
    look_filters = _compile_look_filters(plan_object, assets, selected_delivery.get("look_mode"))
    output_name = _nonempty_string(selected_delivery.get("filename"), "delivery.filename")
    final_output = _safe_generated_output(version, output_name)
    commands: list[list[str]] = []
    for index, unit in enumerate(units, start=1):
        unit_id = _nonempty_string(unit.get("edit_unit_id"), f"edit unit {index}.edit_unit_id")
        if SAFE_ID.fullmatch(unit_id) is None:
            raise AdapterError(f"edit unit id {unit_id} is unsafe for an output path")
        asset_id = _nonempty_string(unit.get("asset_id"), f"edit unit {unit_id}.asset_id")
        binding = assets.get(asset_id)
        if binding is None:
            raise AdapterError(f"edit unit {unit_id} references unknown asset_id {asset_id}")
        if not _authorized_media(binding):
            raise AdapterError(f"video asset {asset_id} is not authorized")
        asset_path = _nonempty_string(binding.get("path_or_uri"), f"asset {asset_id}.path_or_uri")
        segment = _safe_generated_output(version, f"segments/{index:04d}_{unit_id}.mp4")
        picture_filter = (
            f"scale={width}:{height}:force_original_aspect_ratio=increase,"
            f"crop={width}:{height},fps={rate_text},format=yuv420p"
        )
        commands.append(
            [
                executable,
                "-y",
                "-ss",
                _number_text(unit.get("source_in_seconds"), f"edit unit {unit_id}.source_in_seconds"),
                "-t",
                _number_text(unit.get("duration_seconds"), f"edit unit {unit_id}.duration_seconds"),
                "-i",
                asset_path,
                "-an",
                "-vf",
                picture_filter,
                "-c:v",
                "libx264",
                str(segment),
            ]
        )

    audio_cues = (
        _mounted_audio_cues(plan_object, timeline_object, units, assets)
        if audio_mode == "final_mix"
        else []
    )
    needs_postprocess = bool(
        look_filters or subtitle_plan["video_filter"] or audio_cues
    )
    concat_output = (
        _safe_generated_output(version, f"picture_{timeline_id}.mp4")
        if needs_postprocess
        else final_output
    )
    concat_list = _safe_generated_output(version, f"concat_{timeline_id}.txt")
    commands.append(
        [
            executable,
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat_list),
            "-c",
            "copy",
            str(concat_output),
        ]
    )
    if needs_postprocess:
        final_command = [executable, "-y", "-i", str(concat_output)]
        for _cue, _track, binding in audio_cues:
            final_command.extend(["-i", str(binding["path_or_uri"])])
        video_filters = list(look_filters)
        if subtitle_plan["video_filter"] is not None:
            video_filters.append(subtitle_plan["video_filter"])
        if video_filters:
            final_command.extend(["-vf", ",".join(video_filters)])
        if audio_cues:
            final_command.extend(
                [
                    "-filter_complex",
                    _audio_filter_graph(audio_cues),
                    "-map",
                    "0:v:0",
                    "-map",
                    "[aout]",
                    "-c:a",
                    "aac",
                ]
            )
        else:
            final_command.append("-an")
        final_command.extend(["-c:v", "libx264", str(final_output)])
        commands.append(final_command)
    return commands
