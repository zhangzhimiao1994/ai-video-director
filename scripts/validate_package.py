"""Validate an AI video production package."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from decimal import Decimal
from pathlib import Path
from typing import Any


MAX_JSON_INTEGER_DIGITS = 4300


def parse_bounded_json_int(value: str) -> int:
    """Keep JSON integer parsing deterministic across supported Python versions."""
    if len(value.lstrip("-")) > MAX_JSON_INTEGER_DIGITS:
        raise ValueError(
            f"integer literal exceeds {MAX_JSON_INTEGER_DIGITS} decimal digits"
        )
    return int(value)


TOP_LEVEL_FIELDS = (
    "project_brief",
    "creative_directions",
    "selected_treatment",
    "story_structure",
    "screenplay",
    "continuity_bible",
    "storyboard",
    "shot_prompts",
    "model_job_manifest",
    "quality_report",
)

SHOT_REQUIRED_FIELDS = (
    "shot_id",
    "scene_id",
    "sequence",
    "duration_seconds",
    "story_function",
    "beat_change",
    "visual_description",
    "shot_size",
    "camera_angle",
    "lens_intent",
    "composition",
    "camera_movement",
    "character_ids",
    "location_id",
    "wardrobe_ids",
    "prop_ids",
    "look_id",
    "subject_action",
    "performance",
    "opening_state",
    "closing_state",
    "continuity_in",
    "continuity_out",
    "transitions",
    "storyboard_frame_prompt",
    "generation_strategy",
    "risk_level",
    "risk_triggers",
    "fallback_shot",
    "state_snapshot",
)

STATE_SNAPSHOT_REQUIRED_FIELDS = (
    "screen_direction",
    "eye_line",
    "body_position",
    "carried_props",
    "wardrobe_state",
    "time",
    "weather",
    "light_direction",
    "damage_or_dirt",
    "opening_state",
    "closing_state",
)

RISK_TRIGGER_REQUIRED_FIELDS = (
    "failure_mode",
    "acceptance_check",
    "fallback_when",
)

PROMPT_REQUIRED_FIELDS = (
    "shot_id",
    "director_intent_zh",
    "universal_prompt_en",
    "negative_prompt_en",
    "continuity_anchors",
    "reference_requirements",
    "audio_guidance",
    "model_variants",
)

JOB_REQUIRED_FIELDS = (
    "job_id",
    "shot_id",
    "job_purpose",
    "model_family",
    "generation_mode",
    "prompt_source",
    "reference_inputs",
    "duration_seconds",
    "aspect",
    "resolution",
    "documented_parameters",
    "requires_manual_configuration",
)

QUALITY_REPORT_REQUIRED_FIELDS = (
    "ready",
    "status",
    "checks",
    "unresolved_provider_fields",
)

CINEMATIC_MODE_REQUIRED_FIELDS = (
    "input_mode",
    "rhythm_preset",
    "delivery_aspects",
    "style_preset",
)

CINEMATIC_SHOT_REQUIRED_FIELDS = (
    "rhythm_role",
    "state_dependencies",
    "state_before",
    "state_after",
    "composition_16x9",
    "recomposition_9x16",
    "platform_capability_needs",
)

CINEMATIC_NARRATIVE_FIELDS = (
    "protagonist",
    "goal",
    "obstacle",
    "causality",
    "ending_change",
)

CINEMATIC_INPUT_MODES = {"concept_mode", "screenplay_mode"}
CINEMATIC_RHYTHM_PRESETS = {"A", "B", "C"}
CINEMATIC_DELIVERY_ASPECTS = {"16:9", "9:16"}
CINEMATIC_RHYTHM_ROLES = {
    "world_building",
    "performance",
    "reaction",
    "insert",
    "hero",
    "suspense",
    "transition",
}

PORTRAIT_RECOMPOSITION_STRATEGIES = {
    "recompose",
    "independent_generation",
}

CINEMATIC_PROMPT_REQUIRED_FIELDS = (
    "approval_status",
    "global_lock_block",
    "direction_variants",
)

CINEMATIC_PROMPT_APPROVAL_STATUSES = {"draft", "blocked", "final"}
CINEMATIC_JOB_APPROVAL_STATUSES = {
    "blocked",
    "non_executable",
    "approved",
}

BIBLE_ID_FIELDS = {
    "characters": "character_id",
    "locations": "location_id",
    "wardrobes": "wardrobe_id",
    "props": "prop_id",
    "looks": "look_id",
    "audio_motifs": "audio_motif_id",
}


def _positive_decimal(value: Any) -> Decimal | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        decimal_value = Decimal(value)
    elif isinstance(value, float):
        decimal_value = Decimal(str(value))
    else:
        return None
    if not decimal_value.is_finite() or decimal_value <= 0:
        return None
    return decimal_value


def _format_seconds(value: Decimal) -> str:
    formatted = format(value, "f")
    return formatted if "." in formatted else f"{formatted}.0"


def _is_nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


def _require_fields(
    value: dict[str, Any], fields: tuple[str, ...], label: str, errors: list[str]
) -> None:
    for field in fields:
        if field not in value:
            errors.append(f"{label}: missing required field {field}")


def _validate_cinematic_mode(
    project_brief: Any, errors: list[str]
) -> dict[str, Any] | None:
    if not isinstance(project_brief, dict):
        return None
    if "cinematic_mode" not in project_brief:
        return None
    mode = project_brief.get("cinematic_mode")
    if not isinstance(mode, dict):
        errors.append("project_brief.cinematic_mode: expected object")
        return None

    _require_fields(
        mode,
        CINEMATIC_MODE_REQUIRED_FIELDS,
        "project_brief.cinematic_mode",
        errors,
    )

    if mode.get("input_mode") not in CINEMATIC_INPUT_MODES:
        errors.append(
            "project_brief.cinematic_mode: input_mode must be concept_mode or screenplay_mode"
        )
    if mode.get("rhythm_preset") not in CINEMATIC_RHYTHM_PRESETS:
        errors.append(
            "project_brief.cinematic_mode: rhythm_preset must be A, B, or C"
        )
    aspects = mode.get("delivery_aspects")
    if (
        not isinstance(aspects, list)
        or len(aspects) != 2
        or any(not isinstance(aspect, str) for aspect in aspects)
        or set(aspects) != CINEMATIC_DELIVERY_ASPECTS
    ):
        errors.append(
            "project_brief.cinematic_mode: delivery_aspects must contain exactly 16:9 and 9:16"
        )
    style_preset = mode.get("style_preset")
    if not isinstance(style_preset, str) or not style_preset.strip():
        errors.append("project_brief.cinematic_mode: style_preset must not be empty")

    duration = _positive_decimal(project_brief.get("target_duration_seconds"))
    if duration is not None and not (Decimal(30) <= duration <= Decimal(60)):
        errors.append(
            "project_brief: cinematic target_duration_seconds must be between 30 and 60"
        )
    return mode


def _validate_cinematic_shot(
    shot_id: str, shot: dict[str, Any], errors: list[str]
) -> list[str]:
    _require_fields(
        shot,
        CINEMATIC_SHOT_REQUIRED_FIELDS,
        f"shot {shot_id}",
        errors,
    )

    if shot.get("rhythm_role") not in CINEMATIC_RHYTHM_ROLES:
        errors.append(
            f"shot {shot_id}: rhythm_role must be a documented cinematic role"
        )
    composition_16x9 = shot.get("composition_16x9")
    if (
        not isinstance(composition_16x9, str)
        or not composition_16x9.strip()
    ):
        errors.append(
            f"shot {shot_id}: composition_16x9 must be a non-empty string"
        )

    for state_field in ("state_before", "state_after"):
        state_value = shot.get(state_field)
        if not isinstance(state_value, dict) or not state_value:
            errors.append(
                f"shot {shot_id}: {state_field} must be a non-empty object"
            )

    dependencies = shot.get("state_dependencies")
    if not isinstance(dependencies, list):
        errors.append(f"shot {shot_id}: state_dependencies must be a list")
        dependencies = []
    else:
        _validate_nonempty_string_list(
            f"shot {shot_id}",
            dependencies,
            "state_dependencies",
            errors,
        )
        dependencies = [
            dependency
            for dependency in dependencies
            if isinstance(dependency, str) and dependency.strip()
        ]

    needs = shot.get("platform_capability_needs")
    if not isinstance(needs, list):
        errors.append(f"shot {shot_id}: platform_capability_needs must be a list")
    else:
        _validate_nonempty_string_list(
            f"shot {shot_id}",
            needs,
            "platform_capability_needs",
            errors,
        )

    portrait = shot.get("recomposition_9x16")
    if not isinstance(portrait, dict):
        errors.append(f"shot {shot_id}: recomposition_9x16 must be an object")
    else:
        _require_fields(
            portrait,
            ("strategy", "composition", "safe_areas"),
            f"shot {shot_id} recomposition_9x16",
            errors,
        )
        if portrait.get("strategy") not in PORTRAIT_RECOMPOSITION_STRATEGIES:
            errors.append(
                f"shot {shot_id}: recomposition_9x16.strategy must be recompose or independent_generation"
            )
        composition = portrait.get("composition")
        if not isinstance(composition, str) or not composition.strip():
            errors.append(
                f"shot {shot_id}: recomposition_9x16.composition "
                "must be a non-empty string"
            )
        safe_areas = portrait.get("safe_areas")
        if not isinstance(safe_areas, list):
            errors.append(
                f"shot {shot_id}: recomposition_9x16.safe_areas must be a list"
            )
        else:
            if not safe_areas:
                errors.append(
                    f"shot {shot_id}: recomposition_9x16.safe_areas "
                    "must not be empty"
                )
            _validate_nonempty_string_list(
                f"shot {shot_id} recomposition_9x16",
                safe_areas,
                "safe_areas",
                errors,
            )

    return dependencies


def _validate_cinematic_prompt(
    shot_id: str,
    prompt: dict[str, Any],
    shot: dict[str, Any] | None,
    errors: list[str],
) -> str | None:
    label = f"shot_prompt {shot_id}"
    _require_fields(prompt, CINEMATIC_PROMPT_REQUIRED_FIELDS, label, errors)

    approval_status = prompt.get("approval_status")
    if approval_status not in CINEMATIC_PROMPT_APPROVAL_STATUSES:
        errors.append(
            f"{label}: approval_status must be draft, blocked, or final"
        )

    global_lock = prompt.get("global_lock_block")
    if not isinstance(global_lock, str) or not global_lock.strip():
        errors.append(f"{label}: global_lock_block must be a non-empty string")

    variants = prompt.get("direction_variants")
    if not isinstance(variants, dict):
        errors.append(f"{label}: direction_variants must be an object")
        return approval_status if isinstance(approval_status, str) else None

    _require_fields(
        variants,
        ("16:9", "9:16"),
        f"{label} direction_variants",
        errors,
    )
    valid_variants: dict[str, str] = {}
    for aspect in ("16:9", "9:16"):
        direction = variants.get(aspect)
        if not isinstance(direction, str) or not direction.strip():
            errors.append(
                f"{label}: direction_variants[{aspect}] "
                "must be a non-empty string"
            )
        else:
            valid_variants[aspect] = direction.strip()

    if isinstance(shot, dict):
        landscape_composition = shot.get("composition_16x9")
        landscape_direction = valid_variants.get("16:9")
        if (
            isinstance(landscape_composition, str)
            and landscape_composition.strip()
            and landscape_direction is not None
            and landscape_composition.strip() not in landscape_direction
        ):
            errors.append(
                f"{label}: 16:9 direction variant must include composition_16x9"
            )
        portrait = shot.get("recomposition_9x16")
        if isinstance(portrait, dict):
            portrait_composition = portrait.get("composition")
            portrait_direction = valid_variants.get("9:16")
            if (
                isinstance(portrait_composition, str)
                and portrait_composition.strip()
                and portrait_direction is not None
                and portrait_composition.strip() not in portrait_direction
            ):
                errors.append(
                    f"{label}: 9:16 direction variant must include "
                    "recomposition_9x16.composition"
                )
            if valid_variants.get("16:9") == valid_variants.get("9:16"):
                if portrait.get("strategy") == "independent_generation":
                    errors.append(
                        f"{label}: independent_generation requires distinct "
                        "16:9 and 9:16 direction variants"
                    )
                else:
                    errors.append(
                        f"{label}: 16:9 and 9:16 direction variants "
                        "must be distinct"
                    )

    return approval_status if isinstance(approval_status, str) else None


def _cinematic_dependencies_have_cycle(
    dependencies_by_shot: dict[str, list[str]],
) -> bool:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(shot_id: str) -> bool:
        if shot_id in visiting:
            return True
        if shot_id in visited:
            return False
        visiting.add(shot_id)
        for dependency in dependencies_by_shot.get(shot_id, []):
            if dependency == shot_id or dependency not in dependencies_by_shot:
                continue
            if visit(dependency):
                return True
        visiting.remove(shot_id)
        visited.add(shot_id)
        return False

    return any(visit(shot_id) for shot_id in dependencies_by_shot)


def _validate_cinematic_job_prompt_source(
    job_id: str,
    shot_id: str,
    aspect: Any,
    prompt_source: Any,
    errors: list[str],
) -> None:
    label = f"model_job_manifest {job_id} prompt_source"
    if not isinstance(prompt_source, dict):
        errors.append(
            f"model_job_manifest {job_id}: prompt_source must be an object "
            "for cinematic jobs"
        )
        return

    _require_fields(
        prompt_source,
        ("global_lock_source", "direction_source"),
        label,
        errors,
    )
    expected_lock_source = (
        f"shot_prompts[shot_id={shot_id}].global_lock_block"
    )
    if prompt_source.get("global_lock_source") != expected_lock_source:
        errors.append(
            f"model_job_manifest {job_id}: "
            f"prompt_source.global_lock_source must equal {expected_lock_source}"
        )
    expected_direction_source = (
        f"shot_prompts[shot_id={shot_id}].direction_variants[{aspect}]"
    )
    if prompt_source.get("direction_source") != expected_direction_source:
        errors.append(
            f"model_job_manifest {job_id}: "
            "prompt_source.direction_source must equal "
            f"{expected_direction_source}"
        )


def _validate_bible(
    bible: Any, errors: list[str]
) -> dict[str, set[str]]:
    identifiers = {section: set() for section in BIBLE_ID_FIELDS}
    if not isinstance(bible, dict):
        errors.append("continuity_bible: expected object")
        return identifiers

    for section, id_field in BIBLE_ID_FIELDS.items():
        entries = bible.get(section)
        if not isinstance(entries, list):
            errors.append(f"continuity_bible.{section}: expected list")
            continue

        for index, entry in enumerate(entries, start=1):
            if not isinstance(entry, dict):
                errors.append(
                    f"continuity_bible.{section} item {index}: expected object"
                )
                continue
            identifier = entry.get(id_field)
            if not isinstance(identifier, str) or not identifier.strip():
                errors.append(
                    f"continuity_bible.{section} item {index}: missing {id_field}"
                )
                continue
            if identifier in identifiers[section]:
                errors.append(
                    f"continuity_bible.{section}: duplicate {id_field} {identifier}"
                )
            else:
                identifiers[section].add(identifier)

    return identifiers


def _scene_ids(screenplay: Any) -> set[str]:
    if not isinstance(screenplay, dict):
        return set()
    scenes = screenplay.get("scenes")
    if not isinstance(scenes, list):
        return set()
    return {
        scene["scene_id"]
        for scene in scenes
        if isinstance(scene, dict)
        and isinstance(scene.get("scene_id"), str)
        and scene["scene_id"].strip()
    }


def _validate_reference_list(
    shot_id: str,
    shot: dict[str, Any],
    field: str,
    id_name: str,
    known_ids: set[str],
    errors: list[str],
) -> None:
    if field not in shot:
        return
    references = shot[field]
    if not isinstance(references, list):
        errors.append(f"shot {shot_id}: {field} must be a list")
        return
    for index, reference in enumerate(references, start=1):
        if not isinstance(reference, str) or not reference.strip():
            errors.append(
                f"shot {shot_id}: {field} item {index} "
                "must be a non-empty string"
            )
        elif reference not in known_ids:
            errors.append(f"shot {shot_id}: unknown {id_name} {reference}")


def _validate_nonempty_string_list(
    owner: str,
    value: Any,
    field: str,
    errors: list[str],
) -> None:
    if not isinstance(value, list):
        errors.append(f"{owner}: {field} must be a list")
        return
    for index, item in enumerate(value, start=1):
        if not isinstance(item, str) or not item.strip():
            errors.append(
                f"{owner}: {field} item {index} must be a non-empty string"
            )


def _validate_cinematic_quality(
    quality_report: dict[str, Any], errors: list[str]
) -> bool:
    checks = quality_report.get("checks")
    if not isinstance(checks, dict):
        return True
    _require_fields(
        checks,
        ("narrative_clarity", "continuity_integrity"),
        "quality_report.checks",
        errors,
    )

    gate_failed = False
    narrative = checks.get("narrative_clarity")
    if not isinstance(narrative, dict):
        if "narrative_clarity" in checks:
            errors.append("quality_report.checks.narrative_clarity: expected object")
        gate_failed = True
    else:
        _require_fields(
            narrative,
            CINEMATIC_NARRATIVE_FIELDS,
            "quality_report.checks.narrative_clarity",
            errors,
        )
        for field in CINEMATIC_NARRATIVE_FIELDS:
            value = narrative.get(field)
            if value not in ("pass", "fail"):
                errors.append(
                    "quality_report.checks.narrative_clarity."
                    f"{field} must be pass or fail"
                )
                gate_failed = True
            elif value == "fail":
                gate_failed = True

    continuity = checks.get("continuity_integrity")
    if not isinstance(continuity, dict):
        if "continuity_integrity" in checks:
            errors.append(
                "quality_report.checks.continuity_integrity: expected object"
            )
        gate_failed = True
    else:
        _require_fields(
            continuity,
            ("status", "unresolved_conflicts"),
            "quality_report.checks.continuity_integrity",
            errors,
        )
        status = continuity.get("status")
        if status not in ("pass", "fail"):
            errors.append(
                "quality_report.checks.continuity_integrity.status "
                "must be pass or fail"
            )
            gate_failed = True
        elif status == "fail":
            gate_failed = True
        conflicts = continuity.get("unresolved_conflicts")
        if not isinstance(conflicts, list):
            errors.append(
                "quality_report.checks.continuity_integrity."
                "unresolved_conflicts must be a list"
            )
            gate_failed = True
        else:
            _validate_nonempty_string_list(
                "quality_report.checks.continuity_integrity",
                conflicts,
                "unresolved_conflicts",
                errors,
            )
            if conflicts:
                gate_failed = True

    if quality_report.get("ready") is True and gate_failed:
        errors.append(
            "quality_report: ready cannot be true while cinematic hard gates fail"
        )
    return gate_failed


def _validate_cinematic_compilation_statuses(
    ready: bool,
    gate_failed: bool,
    prompt_statuses: list[tuple[str, str | None]],
    job_statuses: list[tuple[str, str | None]],
    errors: list[str],
) -> None:
    if ready and not gate_failed:
        for label, status in prompt_statuses:
            if status in CINEMATIC_PROMPT_APPROVAL_STATUSES and status != "final":
                errors.append(
                    f"{label}: approval_status must be final when "
                    "quality_report.ready is true"
                )
        for label, status in job_statuses:
            if status in CINEMATIC_JOB_APPROVAL_STATUSES and status != "approved":
                errors.append(
                    f"{label}: approval_status must be approved when "
                    "quality_report.ready is true"
                )
        return

    if gate_failed:
        for label, status in prompt_statuses:
            if status in CINEMATIC_PROMPT_APPROVAL_STATUSES and status not in {
                "draft",
                "blocked",
            }:
                errors.append(
                    f"{label}: approval_status must be draft or blocked "
                    "while cinematic hard gates fail"
                )
        for label, status in job_statuses:
            if status in CINEMATIC_JOB_APPROVAL_STATUSES and status not in {
                "blocked",
                "non_executable",
            }:
                errors.append(
                    f"{label}: approval_status must be blocked or "
                    "non_executable while cinematic hard gates fail"
                )
        return

    if not ready:
        for label, status in prompt_statuses:
            if status in CINEMATIC_PROMPT_APPROVAL_STATUSES and status not in {
                "draft",
                "blocked",
            }:
                errors.append(
                    f"{label}: approval_status must be draft or blocked "
                    "while quality_report.ready is false"
                )
        for label, status in job_statuses:
            if status in CINEMATIC_JOB_APPROVAL_STATUSES and status not in {
                "blocked",
                "non_executable",
            }:
                errors.append(
                    f"{label}: approval_status must be blocked or "
                    "non_executable while quality_report.ready is false"
                )


def _validate_reference(
    shot_id: str,
    shot: dict[str, Any],
    field: str,
    id_name: str,
    known_ids: set[str],
    errors: list[str],
) -> None:
    if field not in shot:
        return
    reference = shot[field]
    if not isinstance(reference, str) or not reference.strip():
        errors.append(f"shot {shot_id}: {field} must be a non-empty string")
    elif reference not in known_ids:
        errors.append(f"shot {shot_id}: unknown {id_name} {reference}")


def validate_package(package: Any) -> list[str]:
    """Return all validation errors found in *package*."""

    errors: list[str] = []
    if not isinstance(package, dict):
        return ["package: expected object"]

    for field in TOP_LEVEL_FIELDS:
        if field not in package:
            errors.append(f"package: missing top-level field {field}")

    bible_ids = _validate_bible(package.get("continuity_bible"), errors)
    known_scene_ids = _scene_ids(package.get("screenplay"))
    project_brief = package.get("project_brief")
    cinematic_mode = _validate_cinematic_mode(project_brief, errors)

    storyboard = package.get("storyboard")
    if not isinstance(storyboard, list):
        errors.append("storyboard: expected list")
        storyboard = []

    known_shot_ids: set[str] = set()
    shots: list[tuple[str, dict[str, Any]]] = []
    shot_by_id: dict[str, dict[str, Any]] = {}
    runtime_roles: dict[str, str] = {}
    cinematic_dependencies: dict[str, list[str]] = {}
    cinematic_sequences: dict[str, int] = {}
    sequences: list[int] = []
    durations: list[Decimal] = []
    active_shot_count = 0
    has_invalid_shot_id = False

    for index, shot in enumerate(storyboard, start=1):
        if not isinstance(shot, dict):
            errors.append(f"storyboard item {index}: expected object")
            continue

        raw_shot_id = shot.get("shot_id")
        shot_id = (
            raw_shot_id
            if isinstance(raw_shot_id, str) and raw_shot_id.strip()
            else f"item-{index}"
        )
        _require_fields(shot, SHOT_REQUIRED_FIELDS, f"shot {shot_id}", errors)

        if isinstance(raw_shot_id, str) and raw_shot_id.strip():
            if raw_shot_id in known_shot_ids:
                errors.append(f"storyboard: duplicate shot_id {raw_shot_id}")
            else:
                known_shot_ids.add(raw_shot_id)
            shots.append((raw_shot_id, shot))
            shot_by_id[raw_shot_id] = shot
            if cinematic_mode is not None:
                cinematic_dependencies[raw_shot_id] = _validate_cinematic_shot(
                    raw_shot_id, shot, errors
                )
        else:
            errors.append("storyboard: shot_id must be a non-empty string")
            has_invalid_shot_id = True

        runtime_role = shot.get("runtime_role", "active")
        if runtime_role not in ("active", "fallback"):
            errors.append(
                f"shot {shot_id}: runtime_role must be active or fallback"
            )
            runtime_role = "active"
        if isinstance(raw_shot_id, str) and raw_shot_id.strip():
            runtime_roles[raw_shot_id] = runtime_role
        if runtime_role == "active":
            active_shot_count += 1

        sequence = shot.get("sequence")
        if isinstance(sequence, int) and not isinstance(sequence, bool):
            if runtime_role == "active":
                sequences.append(sequence)
            if (
                cinematic_mode is not None
                and isinstance(raw_shot_id, str)
                and raw_shot_id.strip()
            ):
                cinematic_sequences[raw_shot_id] = sequence
        elif "sequence" in shot:
            errors.append(f"shot {shot_id}: sequence must be an integer")

        if "duration_seconds" in shot:
            duration = _positive_decimal(shot["duration_seconds"])
            if duration is None:
                errors.append(
                    f"shot {shot_id}: duration_seconds must be a "
                    "positive finite number"
                )
            else:
                if runtime_role == "active":
                    durations.append(duration)

        for state_field in (
            "opening_state",
            "closing_state",
            "continuity_in",
            "continuity_out",
        ):
            if state_field in shot and not _is_nonempty(shot[state_field]):
                errors.append(f"shot {shot_id}: {state_field} must not be empty")

        risk_level = shot.get("risk_level")
        if not isinstance(risk_level, str) or risk_level not in (
            "low",
            "medium",
            "high",
        ):
            errors.append(
                f"shot {shot_id}: risk_level must be low, medium, or high"
            )

        risk_triggers = shot.get("risk_triggers")
        if "risk_triggers" in shot:
            if not isinstance(risk_triggers, list):
                errors.append(f"shot {shot_id}: risk_triggers must be a list")
            else:
                if risk_level in ("medium", "high") and not risk_triggers:
                    errors.append(
                        f"shot {shot_id}: medium or high risk requires risk_triggers"
                    )
                for trigger_index, trigger in enumerate(risk_triggers, start=1):
                    if not isinstance(trigger, dict):
                        errors.append(
                            f"shot {shot_id}: risk_triggers item "
                            f"{trigger_index} must be an object"
                        )
                        continue
                    trigger_label = (
                        f"shot {shot_id} risk_triggers item {trigger_index}"
                    )
                    _require_fields(
                        trigger,
                        RISK_TRIGGER_REQUIRED_FIELDS,
                        trigger_label,
                        errors,
                    )
                    for trigger_field in RISK_TRIGGER_REQUIRED_FIELDS:
                        if trigger_field in trigger and not _is_nonempty(
                            trigger[trigger_field]
                        ):
                            errors.append(
                                f"{trigger_label}: {trigger_field} must not be empty"
                            )

        state_snapshot = shot.get("state_snapshot")
        if "state_snapshot" in shot:
            if not isinstance(state_snapshot, dict):
                errors.append(f"shot {shot_id}: state_snapshot must be an object")
            else:
                snapshot_label = f"shot {shot_id} state_snapshot"
                _require_fields(
                    state_snapshot,
                    STATE_SNAPSHOT_REQUIRED_FIELDS,
                    snapshot_label,
                    errors,
                )
                for list_field in ("carried_props", "wardrobe_state"):
                    if list_field in state_snapshot and not isinstance(
                        state_snapshot[list_field], list
                    ):
                        errors.append(
                            f"{snapshot_label}: {list_field} must be a list"
                        )
                for snapshot_field in STATE_SNAPSHOT_REQUIRED_FIELDS:
                    if snapshot_field in ("carried_props", "wardrobe_state"):
                        continue
                    if snapshot_field in state_snapshot and not _is_nonempty(
                        state_snapshot[snapshot_field]
                    ):
                        errors.append(
                            f"{snapshot_label}: {snapshot_field} must not be empty"
                        )
                for boundary_field in ("opening_state", "closing_state"):
                    if (
                        boundary_field in state_snapshot
                        and boundary_field in shot
                        and state_snapshot[boundary_field] != shot[boundary_field]
                    ):
                        errors.append(
                            f"shot {shot_id}: state_snapshot {boundary_field} "
                            f"must match shot {boundary_field}"
                        )

        fallback_shot = shot.get("fallback_shot")
        if risk_level == "high" and fallback_shot is None:
            errors.append(f"shot {shot_id}: high-risk shot requires fallback_shot")
        if fallback_shot is not None and (
            not isinstance(fallback_shot, str) or not fallback_shot.strip()
        ):
            errors.append(
                f"shot {shot_id}: fallback_shot must be a non-empty string"
            )

        _validate_reference(
            shot_id,
            shot,
            "scene_id",
            "scene_id",
            known_scene_ids,
            errors,
        )

        _validate_reference_list(
            shot_id,
            shot,
            "character_ids",
            "character_id",
            bible_ids["characters"],
            errors,
        )
        _validate_reference(
            shot_id,
            shot,
            "location_id",
            "location_id",
            bible_ids["locations"],
            errors,
        )
        _validate_reference_list(
            shot_id,
            shot,
            "wardrobe_ids",
            "wardrobe_id",
            bible_ids["wardrobes"],
            errors,
        )
        _validate_reference_list(
            shot_id,
            shot,
            "prop_ids",
            "prop_id",
            bible_ids["props"],
            errors,
        )
        _validate_reference(
            shot_id,
            shot,
            "look_id",
            "look_id",
            bible_ids["looks"],
            errors,
        )
        _validate_reference_list(
            shot_id,
            shot,
            "audio_motif_ids",
            "audio_motif_id",
            bible_ids["audio_motifs"],
            errors,
        )

    for shot_id, dependencies in cinematic_dependencies.items():
        for dependency in dependencies:
            if dependency == shot_id:
                errors.append(
                    f"shot {shot_id}: state_dependency must not reference itself"
                )
            elif dependency not in known_shot_ids:
                errors.append(
                    f"shot {shot_id}: unknown state_dependency {dependency}"
                )
            else:
                dependency_sequence = cinematic_sequences.get(dependency)
                shot_sequence = cinematic_sequences.get(shot_id)
                if (
                    dependency_sequence is not None
                    and shot_sequence is not None
                    and dependency_sequence >= shot_sequence
                ):
                    errors.append(
                        f"shot {shot_id}: state_dependency {dependency} "
                        "must reference a lower sequence"
                    )
                source_state = shot_by_id[dependency].get("state_after")
                incoming_state = shot_by_id[shot_id].get("state_before")
                if (
                    isinstance(source_state, dict)
                    and source_state
                    and isinstance(incoming_state, dict)
                    and incoming_state
                    and any(
                        incoming_state.get(field) != value
                        for field, value in source_state.items()
                    )
                ):
                    errors.append(
                        f"shot {shot_id}: state_before must include matching "
                        f"state_after of dependency {dependency}"
                    )

    if _cinematic_dependencies_have_cycle(cinematic_dependencies):
        errors.append(
            "storyboard: cinematic state_dependencies must be acyclic"
        )

    for sequence, count in sorted(Counter(sequences).items()):
        if count > 1:
            errors.append(
                f"storyboard: duplicate active sequence {sequence}"
            )
    if len(sequences) == active_shot_count:
        expected_sequences = list(range(1, active_shot_count + 1))
        if sorted(sequences) != expected_sequences:
            errors.append(
                "storyboard: sequence must be continuous from 1; "
                f"got {sorted(sequences)}"
            )

    target_duration = None
    if isinstance(project_brief, dict):
        target_duration = _positive_decimal(
            project_brief.get("target_duration_seconds")
        )
        if target_duration is None:
            errors.append(
                "project_brief: target_duration_seconds must be a "
                "positive finite number"
            )
    if target_duration is not None and len(durations) == active_shot_count:
        actual_duration = sum(durations, Decimal(0))
        if target_duration != actual_duration:
            errors.append(
                f"runtime: expected {_format_seconds(target_duration)} seconds, "
                f"got {_format_seconds(actual_duration)}"
            )

    for shot_id, shot in shots:
        fallback_shot = shot.get("fallback_shot")
        if (
            isinstance(fallback_shot, str)
            and fallback_shot.strip()
            and fallback_shot not in known_shot_ids
        ):
            errors.append(f"shot {shot_id}: unknown fallback_shot {fallback_shot}")
            continue
        if isinstance(fallback_shot, str) and fallback_shot.strip():
            fallback = shot_by_id[fallback_shot]
            if runtime_roles.get(fallback_shot) != "fallback":
                errors.append(
                    f"shot {shot_id}: fallback_shot {fallback_shot} "
                    "must have runtime_role fallback"
                )
            for field in (
                "sequence",
                "duration_seconds",
                "scene_id",
                "story_function",
                "beat_change",
                "opening_state",
                "closing_state",
                "character_ids",
                "location_id",
                "wardrobe_ids",
                "prop_ids",
                "look_id",
            ):
                if fallback.get(field) != shot.get(field):
                    errors.append(
                        f"shot {shot_id}: fallback_shot {fallback_shot} "
                        f"must preserve {field}"
                    )
            risk_rank = {"low": 0, "medium": 1, "high": 2}
            source_value = shot.get("risk_level")
            fallback_value = fallback.get("risk_level")
            source_risk = (
                risk_rank.get(source_value)
                if isinstance(source_value, str)
                else None
            )
            fallback_risk = (
                risk_rank.get(fallback_value)
                if isinstance(fallback_value, str)
                else None
            )
            if (
                source_risk is None
                or fallback_risk is None
                or fallback_risk >= source_risk
            ):
                errors.append(
                    f"shot {shot_id}: fallback_shot {fallback_shot} "
                    "must have a lower risk_level"
                )

    shot_prompts = package.get("shot_prompts")
    if not isinstance(shot_prompts, list):
        errors.append("shot_prompts: expected list")
        shot_prompts = []

    prompt_counts: Counter[str] = Counter()
    cinematic_prompt_statuses: list[tuple[str, str | None]] = []
    for index, prompt in enumerate(shot_prompts, start=1):
        if not isinstance(prompt, dict):
            errors.append(f"shot_prompts item {index}: expected object")
            continue
        prompt_shot_id = prompt.get("shot_id")
        label = (
            prompt_shot_id
            if isinstance(prompt_shot_id, str) and prompt_shot_id.strip()
            else f"item-{index}"
        )
        _require_fields(prompt, PROMPT_REQUIRED_FIELDS, f"shot_prompt {label}", errors)
        if isinstance(prompt_shot_id, str) and prompt_shot_id.strip():
            prompt_counts[prompt_shot_id] += 1
            if (
                prompt_shot_id not in known_shot_ids
                and not has_invalid_shot_id
            ):
                errors.append(
                    f"shot_prompt {prompt_shot_id}: unknown shot_id {prompt_shot_id}"
                )
            if cinematic_mode is not None:
                cinematic_prompt_statuses.append(
                    (
                        f"shot_prompt {prompt_shot_id}",
                        _validate_cinematic_prompt(
                            prompt_shot_id,
                            prompt,
                            shot_by_id.get(prompt_shot_id),
                            errors,
                        ),
                    )
                )
        else:
            errors.append("shot_prompt: shot_id must be a non-empty string")
        if "universal_prompt_en" in prompt and not _is_nonempty(
            prompt["universal_prompt_en"]
        ):
            errors.append(
                f"shot_prompt {label}: universal_prompt_en must not be empty"
            )
        model_variants = prompt.get("model_variants")
        if "model_variants" in prompt:
            if not isinstance(model_variants, list):
                errors.append(
                    f"shot_prompt {label}: model_variants must be a list"
                )
            else:
                for variant_index, variant in enumerate(model_variants, start=1):
                    if not isinstance(variant, dict):
                        errors.append(
                            f"shot_prompt {label}: model_variants item "
                            f"{variant_index} must be an object"
                        )

    for shot_id in sorted(known_shot_ids):
        count = prompt_counts[shot_id]
        if count != 1:
            errors.append(
                f"shot_prompts: expected exactly one prompt for {shot_id}, got {count}"
            )

    jobs = package.get("model_job_manifest")
    if not isinstance(jobs, list):
        errors.append("model_job_manifest: expected list")
        jobs = []

    known_job_ids: set[str] = set()
    job_counts: Counter[str] = Counter()
    job_aspects_by_shot: dict[str, set[str]] = {}
    cinematic_job_statuses: list[tuple[str, str | None]] = []
    for index, job in enumerate(jobs, start=1):
        if not isinstance(job, dict):
            errors.append(f"model_job_manifest item {index}: expected object")
            continue
        raw_job_id = job.get("job_id")
        job_id = (
            raw_job_id
            if isinstance(raw_job_id, str) and raw_job_id.strip()
            else f"item-{index}"
        )
        _require_fields(
            job, JOB_REQUIRED_FIELDS, f"model_job_manifest {job_id}", errors
        )
        if cinematic_mode is not None:
            if "approval_status" not in job:
                errors.append(
                    f"model_job_manifest {job_id}: missing required field "
                    "approval_status"
                )
            approval_status = job.get("approval_status")
            if approval_status not in CINEMATIC_JOB_APPROVAL_STATUSES:
                errors.append(
                    f"model_job_manifest {job_id}: approval_status must be "
                    "blocked, non_executable, or approved"
                )
            cinematic_job_statuses.append(
                (
                    f"model_job_manifest {job_id}",
                    approval_status if isinstance(approval_status, str) else None,
                )
            )
        if isinstance(raw_job_id, str) and raw_job_id.strip():
            if raw_job_id in known_job_ids:
                errors.append(
                    f"model_job_manifest: duplicate job_id {raw_job_id}"
                )
            else:
                known_job_ids.add(raw_job_id)
        else:
            errors.append("model_job_manifest: job_id must be a non-empty string")

        job_duration = None
        if "duration_seconds" in job:
            job_duration = _positive_decimal(job["duration_seconds"])
            if job_duration is None:
                errors.append(
                    f"model_job_manifest {job_id}: duration_seconds must be a "
                    "positive finite number"
                )

        job_shot_id = job.get("shot_id")
        if isinstance(job_shot_id, str) and job_shot_id.strip():
            if job_shot_id not in known_shot_ids:
                if not has_invalid_shot_id:
                    errors.append(
                        f"model_job_manifest {job_id}: unknown shot_id {job_shot_id}"
                    )
            else:
                job_counts[job_shot_id] += 1
                job_aspect = job.get("aspect")
                if isinstance(job_aspect, str) and job_aspect.strip():
                    job_aspects_by_shot.setdefault(job_shot_id, set()).add(
                        job_aspect
                    )
                shot_duration = _positive_decimal(
                    shot_by_id[job_shot_id].get("duration_seconds")
                )
                if (
                    job_duration is not None
                    and shot_duration is not None
                    and job_duration != shot_duration
                ):
                    errors.append(
                        f"model_job_manifest {job_id}: duration_seconds "
                        f"must match shot {job_shot_id}"
                    )
            if cinematic_mode is not None:
                _validate_cinematic_job_prompt_source(
                    job_id,
                    job_shot_id,
                    job.get("aspect"),
                    job.get("prompt_source"),
                    errors,
                )
            else:
                expected_prompt_source = (
                    f"shot_prompts[shot_id={job_shot_id}].universal_prompt_en"
                )
                if job.get("prompt_source") != expected_prompt_source:
                    errors.append(
                        f"model_job_manifest {job_id}: prompt_source must equal "
                        f"{expected_prompt_source}"
                    )
        else:
            errors.append(
                f"model_job_manifest {job_id}: "
                "shot_id must be a non-empty string"
            )

        if "reference_inputs" in job:
            _validate_nonempty_string_list(
                f"model_job_manifest {job_id}",
                job["reference_inputs"],
                "reference_inputs",
                errors,
            )
        if "documented_parameters" in job and not isinstance(
            job["documented_parameters"], dict
        ):
            errors.append(
                f"model_job_manifest {job_id}: "
                "documented_parameters must be an object"
            )
        if "requires_manual_configuration" in job:
            _validate_nonempty_string_list(
                f"model_job_manifest {job_id}",
                job["requires_manual_configuration"],
                "requires_manual_configuration",
                errors,
            )

    for shot_id in sorted(known_shot_ids):
        if job_counts[shot_id] == 0:
            errors.append(
                f"model_job_manifest: expected at least one job for {shot_id}, got 0"
            )

    if cinematic_mode is not None:
        required_aspects = {
            aspect
            for aspect in cinematic_mode.get("delivery_aspects", [])
            if isinstance(aspect, str)
        }
        for shot_id in sorted(known_shot_ids):
            missing_aspects = required_aspects - job_aspects_by_shot.get(
                shot_id, set()
            )
            for aspect in sorted(missing_aspects):
                errors.append(
                    f"model_job_manifest: shot {shot_id} "
                    f"missing cinematic aspect job {aspect}"
                )

    quality_report = package.get("quality_report")
    if not isinstance(quality_report, dict):
        errors.append("quality_report: expected object")
    else:
        _require_fields(
            quality_report,
            QUALITY_REPORT_REQUIRED_FIELDS,
            "quality_report",
            errors,
        )
        if "ready" in quality_report and not isinstance(
            quality_report["ready"], bool
        ):
            errors.append("quality_report: ready must be a boolean")
        if "status" in quality_report and (
            not isinstance(quality_report["status"], str)
            or not quality_report["status"].strip()
        ):
            errors.append("quality_report: status must be a non-empty string")
        checks = quality_report.get("checks")
        if "checks" in quality_report:
            if not isinstance(checks, dict):
                errors.append("quality_report: checks must be an object")
            elif "fallback_audit" not in checks:
                errors.append(
                    "quality_report: checks must include fallback_audit"
                )
            elif (
                not isinstance(checks["fallback_audit"], str)
                or not checks["fallback_audit"].strip()
            ):
                errors.append(
                    "quality_report: checks.fallback_audit must be a "
                    "non-empty string"
                )
        if "unresolved_provider_fields" in quality_report:
            _validate_nonempty_string_list(
                "quality_report",
                quality_report["unresolved_provider_fields"],
                "unresolved_provider_fields",
                errors,
            )
        if cinematic_mode is not None:
            gate_failed = _validate_cinematic_quality(quality_report, errors)
            _validate_cinematic_compilation_statuses(
                quality_report.get("ready") is True,
                gate_failed,
                cinematic_prompt_statuses,
                cinematic_job_statuses,
                errors,
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate an AI video production package JSON file."
    )
    parser.add_argument("package", type=Path, help="Path to the package JSON file")
    args = parser.parse_args(argv)

    try:
        with args.package.open("r", encoding="utf-8") as package_file:
            package = json.load(package_file, parse_int=parse_bounded_json_int)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: could not read {args.package}: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2

    errors = validate_package(package)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("Production package is valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
