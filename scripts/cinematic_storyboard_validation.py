"""Validate cinematic directing declarations on active storyboard shots."""

from __future__ import annotations

from typing import Any


COVERAGE_ROLES = (
    "setup",
    "anticipation",
    "action",
    "impact",
    "reaction",
    "consequence",
    "transition",
    "aftermath",
)

KINETIC_PROFILE_FIELDS = (
    "subject_motion",
    "performance_change",
    "camera_motion",
    "environment_motion",
    "motion_layers_required",
    "intentional_hold",
    "hold_reason",
    "acceptance_evidence",
)

MOTION_DESCRIPTION_FIELDS = (
    "subject_motion",
    "performance_change",
    "camera_motion",
    "environment_motion",
)

TRANSITION_CONTRACT_FIELDS = (
    "type",
    "visual_precondition",
    "incoming_match",
    "duration_frames",
    "audio_bridge_cue_id",
    "story_reason",
    "fallback",
)


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _shot_label(shot: dict[str, Any], index: int) -> str:
    shot_id = shot.get("shot_id")
    return shot_id if _nonempty_string(shot_id) else f"item-{index}"


def _validate_acceptance_evidence(
    value: object, label: str, errors: list[str]
) -> bool:
    if not _nonempty_string(value):
        errors.append(f"{label}: must be a non-empty string")
        return False
    return True


def _validate_kinetic_profile(
    shot_id: str, value: object, errors: list[str]
) -> None:
    label = f"shot {shot_id} kinetic_profile"
    if not isinstance(value, dict):
        errors.append(f"shot {shot_id}: kinetic_profile must be an object")
        return

    for field in KINETIC_PROFILE_FIELDS:
        if field not in value:
            errors.append(f"{label}: missing required field {field}")

    for field in MOTION_DESCRIPTION_FIELDS:
        motion = value.get(field)
        if not isinstance(motion, str):
            errors.append(f"{label}.{field}: must be a string")

    required_layers = value.get("motion_layers_required")
    intentional_hold = value.get("intentional_hold")
    if not isinstance(intentional_hold, bool):
        errors.append(f"{label}.intentional_hold: must be a boolean")
    if (
        not isinstance(required_layers, int)
        or isinstance(required_layers, bool)
        or required_layers < 0
    ):
        errors.append(
            f"{label}.motion_layers_required: must be a non-negative integer"
        )
        required_layers = None

    evidence_ok = _validate_acceptance_evidence(
        value.get("acceptance_evidence"),
        f"{label}.acceptance_evidence",
        errors,
    )
    described_layers = sum(
        _nonempty_string(value.get(field)) for field in MOTION_DESCRIPTION_FIELDS
    )

    if intentional_hold is True:
        if required_layers not in (0, 1):
            errors.append(
                f"{label}.motion_layers_required: intentional hold allows only 0 or 1"
            )
        if not _nonempty_string(value.get("hold_reason")):
            errors.append(f"{label}: intentional hold requires hold_reason")
        if not evidence_ok:
            errors.append(
                f"{label}: intentional hold requires non-empty acceptance_evidence"
            )
        return

    if required_layers is not None and required_layers < 2:
        errors.append(
            f"{label}.motion_layers_required: non-hold requires at least 2"
        )
    if required_layers is not None and described_layers < required_layers:
        errors.append(
            f"{label}: non-hold requires at least motion_layers_required "
            "non-empty motion descriptions"
        )


def _validate_transition_contract(
    shot_id: str, value: object, errors: list[str]
) -> None:
    label = f"shot {shot_id} transition_contract"
    if not isinstance(value, dict):
        errors.append(f"shot {shot_id}: transition_contract must be an object")
        return

    for field in TRANSITION_CONTRACT_FIELDS:
        if field not in value:
            errors.append(f"{label}: missing required field {field}")

    for field in (
        "type",
        "visual_precondition",
        "incoming_match",
        "audio_bridge_cue_id",
        "story_reason",
        "fallback",
    ):
        if field in value and not _nonempty_string(value.get(field)):
            errors.append(f"{label}.{field}: must be a non-empty string")

    duration_frames = value.get("duration_frames")
    if "duration_frames" in value and (
        not isinstance(duration_frames, int)
        or isinstance(duration_frames, bool)
        or duration_frames < 0
    ):
        errors.append(
            f"{label}.duration_frames: must be a non-negative integer"
        )

    for editing_field in ("fulfillment_status", "evidence_refs"):
        if editing_field in value:
            errors.append(
                f"{label}: {editing_field} belongs to editing fulfillment, "
                "not storyboard intent"
            )


def validate_cinematic_storyboard(storyboard: object) -> list[str]:
    """Return deterministic errors for active cinematic storyboard shots."""
    if not isinstance(storyboard, list):
        return ["storyboard: expected list"]

    active_shots: list[tuple[int, int, str, dict[str, Any]]] = []
    for index, shot in enumerate(storyboard, start=1):
        if not isinstance(shot, dict) or shot.get("runtime_role", "active") != "active":
            continue
        shot_id = _shot_label(shot, index)
        sequence = shot.get("sequence")
        sort_sequence = (
            sequence
            if isinstance(sequence, int) and not isinstance(sequence, bool)
            else 10**9
        )
        active_shots.append((sort_sequence, index, shot_id, shot))
    active_shots.sort(key=lambda entry: (entry[0], entry[1]))

    errors: list[str] = []
    for position, (_, _, shot_id, shot) in enumerate(active_shots):
        if shot.get("coverage_role") not in COVERAGE_ROLES:
            errors.append(
                f"shot {shot_id}: coverage_role must be setup, anticipation, "
                "action, impact, reaction, consequence, transition, or aftermath"
            )
        _validate_kinetic_profile(shot_id, shot.get("kinetic_profile"), errors)

        has_next = position < len(active_shots) - 1
        transition = shot.get("transition_contract")
        if has_next and transition is None:
            next_id = active_shots[position + 1][2]
            errors.append(
                f"shot {shot_id}: transition_contract is required before "
                f"adjacent shot {next_id}"
            )
        elif transition is not None:
            _validate_transition_contract(shot_id, transition, errors)

    return list(dict.fromkeys(errors))
