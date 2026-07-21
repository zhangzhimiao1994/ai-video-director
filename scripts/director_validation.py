"""Validate intent fidelity and director-decision evidence."""

from __future__ import annotations

from typing import Any


INTENT_CONTRACT_FIELDS = (
    "core_message",
    "audience_takeaway",
    "emotional_destination",
    "must_show_claims",
    "must_preserve_events",
    "must_not_imply",
    "metaphor_policy",
    "source_fidelity",
)

SCENE_DIRECTING_FIELDS = (
    "scene_pov",
    "audience_knowledge_before",
    "audience_knowledge_after",
    "dramatic_turn",
    "character_objectives",
    "subtext_and_playable_actions",
    "inner_state_arc",
    "unsaid_thoughts",
    "psychological_externalization",
    "dialogue_subtext_strategy",
    "silence_and_pause_plan",
    "blocking_map",
    "reveal_strategy",
    "camera_rule",
    "coverage_strategy",
    "visual_motif_progression",
    "editorial_consequence",
    "rejected_choices",
    "intent_refs",
)

SHOT_DIRECTING_FIELDS = (
    "intent_refs",
    "dramatic_question",
    "information_delta",
    "emotion_delta",
    "power_delta",
    "spatial_delta",
    "blocking_change",
    "camera_necessity",
    "performance_verb",
    "inner_state_ref",
    "visible_psychological_evidence",
    "subtext_action",
    "emotional_leak",
    "dialogue_or_silence_function",
    "shot_relation",
    "director_rejection_reason",
)

DIRECTOR_DELTA_FIELDS = (
    "information_delta",
    "emotion_delta",
    "power_delta",
    "spatial_delta",
)

_SCENE_LIST_FIELDS = {
    "character_objectives",
    "subtext_and_playable_actions",
    "inner_state_arc",
    "unsaid_thoughts",
    "psychological_externalization",
    "dialogue_subtext_strategy",
    "silence_and_pause_plan",
    "rejected_choices",
    "intent_refs",
}
_OPTIONAL_EMPTY_SCENE_LIST_FIELDS = {"rejected_choices"}
_OPTIONAL_EMPTY_SHOT_FIELDS = {"director_rejection_reason", *DIRECTOR_DELTA_FIELDS}
_QUALITY_GATE_FIELDS = ("intent_fidelity", "director_quality", "inner_life_audit")
_QUALITY_STATUSES = {"pass", "fail"}
SERIES_CONTEXT_FIELDS = (
    "series_project_id",
    "episode_id",
    "series_snapshot_id",
    "asset_registry_version",
    "episode_opening_state_ref",
    "foreshadow_refs",
    "payoff_refs",
)
SERIES_HANDOFF_FIELDS = (
    "episode_closing_state_delta",
    "continuity_evidence_refs",
    "foreshadow_status_changes",
    "payoff_status_changes",
    "commit_eligibility",
    "handoff_status",
)
_SERIES_CONTEXT_STRING_FIELDS = (
    "series_project_id",
    "episode_id",
    "series_snapshot_id",
    "asset_registry_version",
    "episode_opening_state_ref",
)
_SERIES_CONTEXT_LIST_FIELDS = ("foreshadow_refs", "payoff_refs")
_SERIES_HANDOFF_LIST_FIELDS = (
    "continuity_evidence_refs",
    "foreshadow_status_changes",
    "payoff_status_changes",
)


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _string_list(
    value: object,
    label: str,
    errors: list[str],
    *,
    nonempty: bool,
) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label}: must be a list")
        return []
    if nonempty and not value:
        errors.append(f"{label}: must not be empty")
    valid: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value, start=1):
        if not _nonempty_string(item):
            errors.append(f"{label} item {index}: must be a non-empty string")
        elif item in seen:
            errors.append(f"{label}: duplicate value {item}")
        else:
            seen.add(item)
            valid.append(item)
    return valid


def _require_fields(
    value: dict[str, Any], fields: tuple[str, ...], label: str, errors: list[str]
) -> None:
    for field in fields:
        if field not in value:
            errors.append(f"{label}: missing required field {field}")


def _object(value: object, label: str, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        errors.append(f"{label}: must be an object")
        return None
    return value


def _project_brief(package: dict[str, Any]) -> dict[str, Any]:
    value = package.get("project_brief")
    return value if isinstance(value, dict) else {}


def _has_director_fields(package: object) -> bool:
    if not isinstance(package, dict):
        return False
    brief = _project_brief(package)
    if "intent_contract" in brief or "series_context" in brief:
        return True
    screenplay = package.get("screenplay")
    scenes = screenplay.get("scenes") if isinstance(screenplay, dict) else None
    if isinstance(scenes, list) and any(
        isinstance(scene, dict) and "scene_directing_plan" in scene
        for scene in scenes
    ):
        return True
    storyboard = package.get("storyboard")
    if isinstance(storyboard, list) and any(
        isinstance(shot, dict)
        and any(field in shot for field in SHOT_DIRECTING_FIELDS)
        for shot in storyboard
    ):
        return True
    quality = package.get("quality_report")
    checks = quality.get("checks") if isinstance(quality, dict) else None
    if isinstance(checks, dict) and any(
        field in checks for field in _QUALITY_GATE_FIELDS
    ):
        return True
    return isinstance(quality, dict) and "series_handoff" in quality


def _validate_series_context(
    brief: dict[str, Any], errors: list[str]
) -> bool:
    context = brief.get("series_context")
    if context is None:
        return False
    context_object = _object(context, "project_brief.series_context", errors)
    if context_object is None:
        return False

    _require_fields(
        context_object,
        SERIES_CONTEXT_FIELDS,
        "project_brief.series_context",
        errors,
    )
    for field in _SERIES_CONTEXT_STRING_FIELDS:
        if field in context_object and not _nonempty_string(context_object.get(field)):
            errors.append(
                f"project_brief.series_context.{field}: must be a non-empty string"
            )
    for field in _SERIES_CONTEXT_LIST_FIELDS:
        if field in context_object:
            _string_list(
                context_object.get(field),
                f"project_brief.series_context.{field}",
                errors,
                nonempty=False,
            )
    return True


def _validate_series_handoff(
    package: dict[str, Any], has_series_context: bool, errors: list[str]
) -> None:
    quality = package.get("quality_report")
    if not isinstance(quality, dict) or "series_handoff" not in quality:
        return
    if not has_series_context:
        errors.append(
            "quality_report.series_handoff: requires project_brief.series_context"
        )

    handoff = quality.get("series_handoff")
    handoff_object = _object(
        handoff, "quality_report.series_handoff", errors
    )
    if handoff_object is None:
        return

    _require_fields(
        handoff_object,
        SERIES_HANDOFF_FIELDS,
        "quality_report.series_handoff",
        errors,
    )
    state_delta = handoff_object.get("episode_closing_state_delta")
    if "episode_closing_state_delta" in handoff_object:
        if not isinstance(state_delta, dict):
            errors.append(
                "quality_report.series_handoff.episode_closing_state_delta: "
                "must be an object"
            )
        elif not state_delta:
            errors.append(
                "quality_report.series_handoff.episode_closing_state_delta: "
                "must not be empty"
            )

    for field in _SERIES_HANDOFF_LIST_FIELDS:
        if field in handoff_object:
            _string_list(
                handoff_object.get(field),
                f"quality_report.series_handoff.{field}",
                errors,
                nonempty=False,
            )

    if (
        "commit_eligibility" in handoff_object
        and handoff_object.get("commit_eligibility")
        != "external_series_controller_required"
    ):
        errors.append(
            "quality_report.series_handoff.commit_eligibility: must be "
            "external_series_controller_required"
        )
    if "handoff_status" in handoff_object and handoff_object.get(
        "handoff_status"
    ) not in ("draft", "unresolved"):
        errors.append(
            "quality_report.series_handoff.handoff_status: must be draft or "
            "unresolved"
        )


def _validate_intent_contract(
    brief: dict[str, Any], errors: list[str]
) -> set[str]:
    intent = brief.get("intent_contract")
    if not isinstance(intent, dict):
        errors.append("project_brief.intent_contract: required for director delivery")
        return set()

    _require_fields(
        intent, INTENT_CONTRACT_FIELDS, "project_brief.intent_contract", errors
    )
    for field in (
        "core_message",
        "audience_takeaway",
        "emotional_destination",
    ):
        if field in intent and not _nonempty_string(intent.get(field)):
            errors.append(f"project_brief.intent_contract.{field}: must not be empty")

    intent_ids: set[str] = set()
    claims = intent.get("must_show_claims")
    if not isinstance(claims, list):
        errors.append("project_brief.intent_contract.must_show_claims: must be a list")
    elif not claims:
        errors.append("project_brief.intent_contract.must_show_claims: must not be empty")
    else:
        for index, claim in enumerate(claims, start=1):
            label = f"project_brief.intent_contract.must_show_claims item {index}"
            if not isinstance(claim, dict):
                errors.append(f"{label}: must be an object")
                continue
            for field in (
                "intent_id",
                "claim",
                "required_evidence",
                "source_status",
            ):
                if field not in claim:
                    errors.append(f"{label}: missing required field {field}")
                elif not _nonempty_string(claim.get(field)):
                    errors.append(f"{label}.{field}: must be a non-empty string")
            intent_id = claim.get("intent_id")
            if _nonempty_string(intent_id):
                if intent_id in intent_ids:
                    errors.append(
                        f"project_brief.intent_contract: duplicate intent_id {intent_id}"
                    )
                else:
                    intent_ids.add(intent_id)

    for field in ("must_preserve_events", "must_not_imply"):
        if field in intent:
            _string_list(
                intent.get(field),
                f"project_brief.intent_contract.{field}",
                errors,
                nonempty=True,
            )

    metaphor = intent.get("metaphor_policy")
    if "metaphor_policy" in intent:
        metaphor_object = _object(
            metaphor, "project_brief.intent_contract.metaphor_policy", errors
        )
        if metaphor_object is not None:
            for nested in ("mode", "rule"):
                if not _nonempty_string(metaphor_object.get(nested)):
                    errors.append(
                        "project_brief.intent_contract.metaphor_policy."
                        f"{nested}: must be a non-empty string"
                    )

    fidelity = intent.get("source_fidelity")
    if "source_fidelity" in intent:
        fidelity_object = _object(
            fidelity, "project_brief.intent_contract.source_fidelity", errors
        )
        if fidelity_object is not None:
            for nested in ("mode", "allowed_adaptation"):
                if not _nonempty_string(fidelity_object.get(nested)):
                    errors.append(
                        "project_brief.intent_contract.source_fidelity."
                        f"{nested}: must be a non-empty string"
                    )
            _string_list(
                fidelity_object.get("locked_source_refs"),
                "project_brief.intent_contract.source_fidelity.locked_source_refs",
                errors,
                nonempty=False,
            )

    return intent_ids


def _validate_intent_refs(
    value: object,
    label: str,
    known_intent_ids: set[str],
    errors: list[str],
) -> list[str]:
    refs = _string_list(value, f"{label}.intent_refs", errors, nonempty=True)
    for intent_id in refs:
        if intent_id not in known_intent_ids:
            errors.append(f"{label}: unknown intent_ref {intent_id}")
    return refs


def _validate_beat_refs(
    package: dict[str, Any], known_intent_ids: set[str], errors: list[str]
) -> None:
    story = package.get("story_structure")
    beats = story.get("beats") if isinstance(story, dict) else []
    if not isinstance(beats, list):
        errors.append("story_structure.beats: must be a list")
        return
    for index, beat in enumerate(beats, start=1):
        if not isinstance(beat, dict):
            continue
        beat_id = beat.get("beat_id")
        label = f"beat {beat_id}" if _nonempty_string(beat_id) else f"beat item {index}"
        _validate_intent_refs(beat.get("intent_refs"), label, known_intent_ids, errors)


def _validate_scene_refs_and_plans(
    package: dict[str, Any], known_intent_ids: set[str], errors: list[str]
) -> None:
    screenplay = package.get("screenplay")
    scenes = screenplay.get("scenes") if isinstance(screenplay, dict) else None
    if not isinstance(scenes, list):
        errors.append("screenplay.scenes: must be a list")
        return
    for index, scene in enumerate(scenes, start=1):
        if not isinstance(scene, dict):
            errors.append(f"screenplay.scenes item {index}: must be an object")
            continue
        scene_id = scene.get("scene_id")
        label = f"scene {scene_id}" if _nonempty_string(scene_id) else f"scene item {index}"
        _validate_intent_refs(scene.get("intent_refs"), label, known_intent_ids, errors)
        plan = scene.get("scene_directing_plan")
        if not isinstance(plan, dict):
            errors.append(f"{label}: scene_directing_plan is required")
            continue
        _require_fields(plan, SCENE_DIRECTING_FIELDS, f"{label}.scene_directing_plan", errors)
        for field in SCENE_DIRECTING_FIELDS:
            if field not in plan:
                continue
            field_label = f"{label}.scene_directing_plan.{field}"
            if field in _SCENE_LIST_FIELDS:
                refs = _string_list(
                    plan.get(field),
                    field_label,
                    errors,
                    nonempty=field not in _OPTIONAL_EMPTY_SCENE_LIST_FIELDS,
                )
                if field == "intent_refs":
                    for intent_id in refs:
                        if intent_id not in known_intent_ids:
                            errors.append(f"{field_label}: unknown intent_ref {intent_id}")
            elif not _nonempty_string(plan.get(field)):
                errors.append(f"{field_label}: must be a non-empty string")


def _validate_active_shot_refs(
    package: dict[str, Any], known_intent_ids: set[str], errors: list[str]
) -> dict[str, list[str]]:
    storyboard = package.get("storyboard")
    shot_refs: dict[str, list[str]] = {}
    if not isinstance(storyboard, list):
        errors.append("storyboard: must be a list")
        return shot_refs
    for index, shot in enumerate(storyboard, start=1):
        if not isinstance(shot, dict):
            errors.append(f"storyboard item {index}: must be an object")
            continue
        shot_id = shot.get("shot_id")
        label = f"shot {shot_id}" if _nonempty_string(shot_id) else f"shot item {index}"
        runtime_role = shot.get("runtime_role", "active")
        if runtime_role != "active":
            continue
        _require_fields(shot, SHOT_DIRECTING_FIELDS, label, errors)
        for field in SHOT_DIRECTING_FIELDS:
            if field not in shot:
                continue
            if field == "intent_refs":
                continue
            if field in _OPTIONAL_EMPTY_SHOT_FIELDS:
                if not isinstance(shot.get(field), str):
                    errors.append(f"{label}.{field}: must be a string")
            elif not _nonempty_string(shot.get(field)):
                errors.append(f"{label}.{field}: must be a non-empty string")
        if not any(_nonempty_string(shot.get(field)) for field in DIRECTOR_DELTA_FIELDS):
            errors.append(f"{label}: at least one director delta must be non-empty")
        refs = _validate_intent_refs(
            shot.get("intent_refs"), label, known_intent_ids, errors
        )
        if _nonempty_string(shot_id):
            shot_refs[shot_id] = refs
    return shot_refs


def _validate_prompt_refs(
    package: dict[str, Any],
    known_intent_ids: set[str],
    shot_refs: dict[str, list[str]],
    errors: list[str],
) -> None:
    prompts = package.get("shot_prompts")
    if not isinstance(prompts, list):
        errors.append("shot_prompts: must be a list")
        return
    for index, prompt in enumerate(prompts, start=1):
        if not isinstance(prompt, dict):
            errors.append(f"shot_prompts item {index}: must be an object")
            continue
        shot_id = prompt.get("shot_id")
        label = (
            f"shot_prompt {shot_id}"
            if _nonempty_string(shot_id)
            else f"shot_prompt item {index}"
        )
        refs = _validate_intent_refs(
            prompt.get("intent_refs"), label, known_intent_ids, errors
        )
        if _nonempty_string(shot_id) and shot_id in shot_refs:
            if set(refs) != set(shot_refs[shot_id]):
                errors.append(
                    f"{label}: intent_refs must match shot {shot_id} intent_refs"
                )


def _validate_quality_gates(
    package: dict[str, Any], errors: list[str]
) -> bool:
    quality = package.get("quality_report")
    if not isinstance(quality, dict):
        errors.append("quality_report: must be an object")
        return True
    checks = quality.get("checks")
    if not isinstance(checks, dict):
        errors.append("quality_report.checks: must be an object")
        return True

    gate_failed = False
    for field in _QUALITY_GATE_FIELDS:
        label = f"quality_report.checks.{field}"
        audit = checks.get(field)
        if not isinstance(audit, dict):
            errors.append(f"{label}: must be an object")
            gate_failed = True
            continue
        _require_fields(audit, ("status", "unresolved_conflicts", "evidence_refs"), label, errors)
        status = audit.get("status")
        if status not in _QUALITY_STATUSES:
            errors.append(f"{label}.status: must be pass or fail")
            gate_failed = True
        elif status == "fail":
            gate_failed = True
        conflicts = _string_list(
            audit.get("unresolved_conflicts"),
            f"{label}.unresolved_conflicts",
            errors,
            nonempty=False,
        )
        if conflicts:
            gate_failed = True
        evidence = _string_list(
            audit.get("evidence_refs"),
            f"{label}.evidence_refs",
            errors,
            nonempty=True,
        )
        if not evidence:
            gate_failed = True

    if quality.get("ready") is True and gate_failed:
        errors.append(
            "quality_report: ready cannot be true while director hard gates fail"
        )
    return gate_failed


def validate_director_package(
    package: object, *, required: bool
) -> tuple[list[str], bool]:
    """Return deterministic errors and whether director hard gates block."""

    if not required and not _has_director_fields(package):
        return [], False
    errors: list[str] = []
    if not isinstance(package, dict):
        return ["package: must be an object"], True

    brief = _project_brief(package)
    has_series_context = _validate_series_context(brief, errors)
    intent_ids = _validate_intent_contract(brief, errors)
    _validate_beat_refs(package, intent_ids, errors)
    _validate_scene_refs_and_plans(package, intent_ids, errors)
    shot_refs = _validate_active_shot_refs(package, intent_ids, errors)
    _validate_prompt_refs(package, intent_ids, shot_refs, errors)
    _validate_series_handoff(package, has_series_context, errors)
    gate_failed = _validate_quality_gates(package, errors)
    deduped_errors = list(dict.fromkeys(errors))
    return deduped_errors, gate_failed or bool(deduped_errors)
