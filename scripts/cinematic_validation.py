"""Validate cinematic creative-readiness evidence for an edit plan."""

from __future__ import annotations


CINEMATIC_FIELDS = (
    "declared_mode",
    "genre",
    "content_consistency",
    "intent_fidelity",
    "character_identity_integrity",
    "action_reaction_coverage",
    "kinetic_profile_audit",
    "shot_scale_and_composition_variety",
    "transition_fulfillment",
    "audio_presence_and_structure",
    "static_hold_audit",
    "source_motion_review",
    "director_quality",
    "subtext_fidelity",
    "ppt_risk_flags",
    "evidence_refs",
    "cinematic_ready",
)

AUDIT_FIELDS = (
    "content_consistency",
    "intent_fidelity",
    "character_identity_integrity",
    "action_reaction_coverage",
    "kinetic_profile_audit",
    "shot_scale_and_composition_variety",
    "transition_fulfillment",
    "audio_presence_and_structure",
    "static_hold_audit",
    "source_motion_review",
    "director_quality",
    "subtext_fidelity",
)

VISUAL_AUDIT_FIELDS = tuple(
    field for field in AUDIT_FIELDS if field != "audio_presence_and_structure"
)

AUDIT_STATUSES = {"passed", "failed", "manual_review_required"}
MOTION_LAYERS = {"subject", "performance", "camera", "environment"}


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _array(value: object, label: str, errors: list[str]) -> list[object] | None:
    if not isinstance(value, list):
        errors.append(f"{label}: must be an array")
        return None
    return value


def _string_list(
    value: object,
    label: str,
    errors: list[str],
    *,
    nonempty: bool,
) -> list[str] | None:
    values = _array(value, label, errors)
    if values is None:
        return None
    if (nonempty and not values) or any(
        not _nonempty_string(item) for item in values
    ):
        qualifier = "non-empty " if nonempty else ""
        errors.append(f"{label}: must be a {qualifier}list of strings")
        return None
    return values  # type: ignore[return-value]


def _audit_object(
    cinematic: dict[str, object], field: str, errors: list[str]
) -> dict[str, object] | None:
    if field not in cinematic:
        return None
    value = cinematic[field]
    label = f"cinematic_validation.{field}"
    if not isinstance(value, dict):
        errors.append(f"{label}: must be an object")
        return None
    return value


def _collect_timeline_coverage(
    plan: dict[str, object],
) -> tuple[
    list[str],
    dict[str, str],
    list[tuple[str, str]],
    dict[str, dict[str, object]],
]:
    """Collect valid active V1 unit IDs and adjacent pairs without shape errors."""
    timelines = plan.get("timelines")
    if not isinstance(timelines, list):
        return [], {}, [], {}

    ordered_unit_ids: list[str] = []
    unit_timelines: dict[str, str] = {}
    adjacent_pairs: list[tuple[str, str]] = []
    units_by_id: dict[str, dict[str, object]] = {}
    for timeline_index, timeline in enumerate(timelines, start=1):
        if not isinstance(timeline, dict):
            continue
        raw_timeline_id = timeline.get("timeline_id")
        timeline_id = (
            raw_timeline_id
            if _nonempty_string(raw_timeline_id)
            else f"item-{timeline_index}"
        )
        video_tracks = timeline.get("video_tracks")
        if not isinstance(video_tracks, list):
            continue
        selected_tracks = [
            track
            for track in video_tracks
            if isinstance(track, dict)
            and track.get("track_id") == "V1"
            and track.get("runtime_role") == "active"
            and track.get("release_role") == "first_release"
        ]
        if not selected_tracks:
            continue
        raw_units = selected_tracks[0].get("edit_units")
        if not isinstance(raw_units, list):
            continue

        sortable_units: list[tuple[int, int, str]] = []
        for unit_index, unit in enumerate(raw_units):
            if not isinstance(unit, dict):
                continue
            unit_id = unit.get("edit_unit_id")
            if not _nonempty_string(unit_id):
                continue
            sequence = unit.get("sequence")
            sort_sequence = (
                sequence
                if isinstance(sequence, int) and not isinstance(sequence, bool)
                else 10**9
            )
            sortable_units.append((sort_sequence, unit_index, unit_id))
        sortable_units.sort(key=lambda entry: (entry[0], entry[1]))
        timeline_unit_ids = [entry[2] for entry in sortable_units]
        for unit_id in timeline_unit_ids:
            if unit_id not in unit_timelines:
                ordered_unit_ids.append(unit_id)
                unit_timelines[unit_id] = timeline_id
                units_by_id[unit_id] = next(
                    unit
                    for unit in raw_units
                    if isinstance(unit, dict)
                    and unit.get("edit_unit_id") == unit_id
                )
        adjacent_pairs.extend(zip(timeline_unit_ids, timeline_unit_ids[1:]))
    return ordered_unit_ids, unit_timelines, adjacent_pairs, units_by_id


def _validate_audit_status(
    audit: dict[str, object], label: str, errors: list[str]
) -> None:
    if "status" not in audit:
        errors.append(f"{label}: missing field status")
        return
    status = audit.get("status")
    if not isinstance(status, str) or status not in AUDIT_STATUSES:
        errors.append(
            f"{label}.status: must be passed, failed, or manual_review_required"
        )
    elif status != "passed":
        errors.append(
            f"{label}: status {status} blocks cinematic readiness"
        )


def _validate_content(
    audit: dict[str, object], errors: list[str]
) -> None:
    label = "cinematic_validation.content_consistency"
    _string_list(
        audit.get("locked_event_ids"),
        f"{label}.locked_event_ids",
        errors,
        nonempty=True,
    )
    _string_list(
        audit.get("evidence_refs"),
        f"{label}.evidence_refs",
        errors,
        nonempty=True,
    )


def _validate_intent_fidelity(
    audit: dict[str, object],
    real_unit_ids: list[str],
    units_by_id: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    label = "cinematic_validation.intent_fidelity"
    intent_ids = _string_list(
        audit.get("intent_ids"),
        f"{label}.intent_ids",
        errors,
        nonempty=True,
    )
    known_intent_ids = set(intent_ids or ())
    seen_intents: set[str] = set()
    if intent_ids is not None:
        for intent_id in intent_ids:
            if intent_id in seen_intents:
                errors.append(f"{label}.intent_ids: duplicate intent_id {intent_id}")
            seen_intents.add(intent_id)

    for unit_id in real_unit_ids:
        unit = units_by_id.get(unit_id, {})
        if "intent_refs" not in unit:
            errors.append(
                f"edit unit {unit_id}.intent_refs: must be a non-empty "
                "list of strings"
            )
            continue
        refs = _string_list(
            unit.get("intent_refs"),
            f"edit unit {unit_id}.intent_refs",
            errors,
            nonempty=True,
        )
        if refs is None:
            continue
        seen_refs: set[str] = set()
        for intent_id in refs:
            if intent_id in seen_refs:
                errors.append(
                    f"edit unit {unit_id}.intent_refs: duplicate intent_id "
                    f"{intent_id}"
                )
            elif intent_id not in known_intent_ids:
                errors.append(
                    f"edit unit {unit_id}.intent_refs: unknown intent_id {intent_id}"
                )
            seen_refs.add(intent_id)

    mappings = _array(
        audit.get("edit_unit_mappings"),
        f"{label}.edit_unit_mappings",
        errors,
    )
    if mappings is None:
        return
    if not mappings:
        errors.append(f"{label}.edit_unit_mappings: must not be empty")
    mapped_intents: set[str] = set()
    mapped_units: set[str] = set()
    real_unit_id_set = set(real_unit_ids)
    for index, mapping in enumerate(mappings, start=1):
        item_label = f"{label}.edit_unit_mappings item {index}"
        if not isinstance(mapping, dict):
            errors.append(f"{item_label}: must be an object")
            continue
        for field in ("intent_id", "edit_unit_ids", "evidence_refs"):
            if field not in mapping:
                errors.append(f"{item_label}: missing field {field}")
        intent_id = mapping.get("intent_id")
        if "intent_id" in mapping:
            if not _nonempty_string(intent_id):
                errors.append(f"{item_label}.intent_id: must be a non-empty string")
            elif isinstance(intent_id, str):
                if intent_id not in known_intent_ids:
                    errors.append(f"{item_label}.intent_id: unknown intent_id {intent_id}")
                else:
                    mapped_intents.add(intent_id)
        edit_unit_ids = _string_list(
            mapping.get("edit_unit_ids"),
            f"{item_label}.edit_unit_ids",
            errors,
            nonempty=True,
        )
        if edit_unit_ids is not None:
            seen_units: set[str] = set()
            for unit_id in edit_unit_ids:
                if unit_id in seen_units:
                    errors.append(
                        f"{item_label}.edit_unit_ids: duplicate edit_unit_id "
                        f"{unit_id}"
                    )
                elif unit_id not in real_unit_id_set:
                    errors.append(
                        f"{item_label}.edit_unit_ids: unknown edit_unit_id "
                        f"{unit_id}"
                    )
                else:
                    mapped_units.add(unit_id)
                seen_units.add(unit_id)
        _string_list(
            mapping.get("evidence_refs"),
            f"{item_label}.evidence_refs",
            errors,
            nonempty=True,
        )
    for intent_id in sorted(known_intent_ids):
        if intent_id not in mapped_intents:
            errors.append(f"{label}.edit_unit_mappings: missing intent_id {intent_id}")
    for unit_id in real_unit_ids:
        if unit_id not in mapped_units:
            errors.append(f"{label}.edit_unit_mappings: missing edit_unit_id {unit_id}")
    _string_list(
        audit.get("evidence_refs"),
        f"{label}.evidence_refs",
        errors,
        nonempty=True,
    )


def _validate_identity(
    audit: dict[str, object], errors: list[str]
) -> None:
    label = "cinematic_validation.character_identity_integrity"
    for field in ("identity_profile_ids", "model_lock_refs", "evidence_refs"):
        _string_list(
            audit.get(field),
            f"{label}.{field}",
            errors,
            nonempty=True,
        )
    drift_conflicts = _string_list(
        audit.get("drift_conflicts"),
        f"{label}.drift_conflicts",
        errors,
        nonempty=False,
    )
    if drift_conflicts:
        errors.append(f"{label}.drift_conflicts: must be empty")


def _validate_action_events(
    audit: dict[str, object], real_unit_ids: set[str], errors: list[str]
) -> None:
    label = "cinematic_validation.action_reaction_coverage.events"
    events = _array(audit.get("events"), label, errors)
    if events is None:
        return
    if not events:
        errors.append(f"{label}: must not be empty")
    required_fields = ("event_id", "required_roles", "edit_unit_ids", "status")
    for index, event in enumerate(events, start=1):
        item_label = f"{label} item {index}"
        if not isinstance(event, dict):
            errors.append(f"{item_label}: must be an object")
            continue
        for field in required_fields:
            if field not in event:
                errors.append(f"{item_label}: missing field {field}")
        roles = _string_list(
            event.get("required_roles"),
            f"{item_label}.required_roles",
            errors,
            nonempty=True,
        )
        if roles is not None and not {
            "action",
            "reaction",
            "consequence",
        }.issubset(roles):
            errors.append(
                f"{item_label}.required_roles: must include action, reaction, "
                "and consequence"
            )
        edit_unit_ids = _string_list(
            event.get("edit_unit_ids"),
            f"{item_label}.edit_unit_ids",
            errors,
            nonempty=True,
        )
        if edit_unit_ids is not None:
            seen_unit_ids: set[str] = set()
            for unit_id in edit_unit_ids:
                if unit_id in seen_unit_ids:
                    errors.append(
                        f"{item_label}.edit_unit_ids: duplicate edit_unit_id "
                        f"{unit_id}"
                    )
                elif unit_id not in real_unit_ids:
                    errors.append(
                        f"{item_label}.edit_unit_ids: unknown edit_unit_id "
                        f"{unit_id}"
                    )
                seen_unit_ids.add(unit_id)


def _validate_kinetic_records(
    audit: dict[str, object], real_unit_ids: list[str], errors: list[str]
) -> None:
    label = "cinematic_validation.kinetic_profile_audit.edit_units"
    records = _array(audit.get("edit_units"), label, errors)
    if records is None:
        return
    if not records:
        errors.append(f"{label}: must not be empty")
    real_unit_id_set = set(real_unit_ids)
    seen_unit_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        item_label = f"{label} item {index}"
        if not isinstance(record, dict):
            errors.append(f"{item_label}: must be an object")
            continue
        if "edit_unit_id" not in record:
            errors.append(f"{item_label}: missing field edit_unit_id")
        unit_id = record.get("edit_unit_id")
        if "edit_unit_id" in record and not _nonempty_string(unit_id):
            errors.append(
                f"{item_label}.edit_unit_id: must be a non-empty string"
            )
        elif isinstance(unit_id, str):
            if unit_id in seen_unit_ids:
                errors.append(
                    f"{item_label}.edit_unit_id: duplicate edit_unit_id {unit_id}"
                )
            elif unit_id not in real_unit_id_set:
                errors.append(
                    f"{item_label}.edit_unit_id: unknown edit_unit_id {unit_id}"
                )
            seen_unit_ids.add(unit_id)
        layers = _string_list(
            record.get("motion_layers"),
            f"{item_label}.motion_layers",
            errors,
            nonempty=False,
        )
        evidence = _string_list(
            record.get("evidence_refs"),
            f"{item_label}.evidence_refs",
            errors,
            nonempty=True,
        )
        if record.get("intentional_hold") is True:
            if not _nonempty_string(record.get("hold_reason")) or not evidence:
                errors.append(
                    f"{item_label}.intentional_hold: hold_reason and "
                    "evidence_refs are required"
                )
            continue
        valid_layers = set(layers or ()) & MOTION_LAYERS
        if layers is not None and len(valid_layers) < 2:
            errors.append(
                f"{item_label}.motion_layers: requires at least two distinct "
                "valid motion layers unless intentional_hold is evidenced"
            )
    for unit_id in real_unit_ids:
        if unit_id not in seen_unit_ids:
            errors.append(f"{label}: missing edit_unit_id {unit_id}")


def _validate_transition_boundaries(
    audit: dict[str, object],
    unit_timelines: dict[str, str],
    real_pairs: list[tuple[str, str]],
    errors: list[str],
) -> None:
    label = "cinematic_validation.transition_fulfillment.boundaries"
    boundaries = _array(audit.get("boundaries"), label, errors)
    if boundaries is None:
        return
    if real_pairs and not boundaries:
        errors.append(
            f"{label}: must not be empty when timelines have adjacent edit units"
        )
    real_pair_set = set(real_pairs)
    seen_boundary_ids: set[str] = set()
    seen_pairs: set[tuple[str, str]] = set()
    required_fields = (
        "boundary_id",
        "from_edit_unit_id",
        "to_edit_unit_id",
        "type",
        "story_reason",
        "visual_precondition",
        "incoming_match",
        "duration_frames",
        "audio_bridge_cue_id",
        "fallback",
        "fulfillment_status",
        "evidence_refs",
    )
    for index, boundary in enumerate(boundaries, start=1):
        item_label = f"{label} item {index}"
        if not isinstance(boundary, dict):
            errors.append(f"{item_label}: must be an object")
            continue
        for field in required_fields:
            if field not in boundary:
                errors.append(f"{item_label}: missing field {field}")
        for field in (
            "boundary_id",
            "from_edit_unit_id",
            "to_edit_unit_id",
            "type",
            "story_reason",
            "visual_precondition",
            "incoming_match",
            "fallback",
        ):
            if field in boundary and not _nonempty_string(boundary.get(field)):
                errors.append(
                    f"{item_label}.{field}: must be a non-empty string"
                )
        duration_frames = boundary.get("duration_frames")
        if "duration_frames" in boundary and (
            not isinstance(duration_frames, int)
            or isinstance(duration_frames, bool)
            or duration_frames < 0
        ):
            errors.append(
                f"{item_label}.duration_frames: must be a non-negative integer"
            )
        boundary_id = boundary.get("boundary_id")
        if _nonempty_string(boundary_id):
            if boundary_id in seen_boundary_ids:
                errors.append(
                    f"{item_label}.boundary_id: duplicate boundary_id "
                    f"{boundary_id}"
                )
            seen_boundary_ids.add(boundary_id)
        from_id = boundary.get("from_edit_unit_id")
        to_id = boundary.get("to_edit_unit_id")
        from_known = _nonempty_string(from_id) and from_id in unit_timelines
        to_known = _nonempty_string(to_id) and to_id in unit_timelines
        if _nonempty_string(from_id) and not from_known:
            errors.append(
                f"{item_label}.from_edit_unit_id: unknown edit_unit_id {from_id}"
            )
        if _nonempty_string(to_id) and not to_known:
            errors.append(
                f"{item_label}.to_edit_unit_id: unknown edit_unit_id {to_id}"
            )
        if from_known and to_known:
            pair = (from_id, to_id)
            if unit_timelines[from_id] != unit_timelines[to_id]:
                errors.append(f"{item_label}: {from_id} -> {to_id} crosses timelines")
            elif pair not in real_pair_set:
                errors.append(
                    f"{item_label}: {from_id} -> {to_id} is not an actual "
                    "adjacent pair"
                )
            elif pair in seen_pairs:
                errors.append(
                    f"{item_label}: duplicate adjacent pair {from_id} -> {to_id}"
                )
            else:
                seen_pairs.add(pair)
        bridge = boundary.get("audio_bridge_cue_id")
        if "audio_bridge_cue_id" in boundary and not _nonempty_string(bridge):
            errors.append(
                f"{item_label}.audio_bridge_cue_id: must identify a cue or "
                "explicit none"
            )
        if (
            "fulfillment_status" in boundary
            and boundary.get("fulfillment_status") != "passed"
        ):
            errors.append(
                f"{item_label}.fulfillment_status: must be passed"
            )
        _string_list(
            boundary.get("evidence_refs"),
            f"{item_label}.evidence_refs",
            errors,
            nonempty=True,
        )
    for from_id, to_id in real_pairs:
        if (from_id, to_id) not in seen_pairs:
            errors.append(
                f"{label}: missing adjacent pair {from_id} -> {to_id}"
            )


def _validate_audio(
    audit: dict[str, object],
    audits: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    label = "cinematic_validation.audio_presence_and_structure"
    _string_list(
        audit.get("track_types"),
        f"{label}.track_types",
        errors,
        nonempty=False,
    )
    _string_list(
        audit.get("evidence_refs"),
        f"{label}.evidence_refs",
        errors,
        nonempty=True,
    )
    if audit.get("audio_stream_status") == "verified_present":
        return
    if not _nonempty_string(audit.get("silent_form_authorization")):
        errors.append(
            "cinematic_validation: missing audio requires silent-form authorization"
        )
        return
    if any(
        audits.get(field, {}).get("status") != "passed"
        for field in VISUAL_AUDIT_FIELDS
    ):
        errors.append(
            f"{label}: silent-form authorization requires passed visual audits"
        )


def _requested_delivery_ids(plan: dict[str, object]) -> list[str]:
    deliveries = plan.get("delivery_specs")
    if not isinstance(deliveries, list):
        return []
    return [
        delivery_id
        for delivery in deliveries
        if isinstance(delivery, dict)
        and _nonempty_string(delivery_id := delivery.get("delivery_id"))
    ]


def _valid_review_evidence(
    plan: dict[str, object], requested_ids: set[str]
) -> dict[str, dict[str, object]]:
    execution = plan.get("execution")
    if not isinstance(execution, dict):
        return {}
    raw_tools = execution.get("tool_evidence")
    verified_tools = {
        item.get("tool_evidence_id")
        for item in raw_tools
        if isinstance(item, dict)
        and _nonempty_string(item.get("tool_evidence_id"))
        and item.get("status") == "verified"
    } if isinstance(raw_tools, list) else set()
    raw_evidence = execution.get("review_evidence")
    if not isinstance(raw_evidence, list):
        return {}

    required_fields = {
        "review_evidence_id",
        "delivery_id",
        "evidence_type",
        "artifact_ref",
        "status",
        "tool_evidence_ref",
    }
    valid: dict[str, dict[str, object]] = {}
    duplicates: set[str] = set()
    for item in raw_evidence:
        if not isinstance(item, dict) or set(item) != required_fields:
            continue
        evidence_id = item.get("review_evidence_id")
        delivery_id = item.get("delivery_id")
        evidence_type = item.get("evidence_type")
        tool_ref = item.get("tool_evidence_ref")
        if (
            not _nonempty_string(evidence_id)
            or not _nonempty_string(delivery_id)
            or delivery_id not in requested_ids
            or not isinstance(evidence_type, str)
            or evidence_type not in {
                "frame_change",
                "contact_sheet",
            }
            or not _nonempty_string(item.get("artifact_ref"))
            or item.get("status") != "passed"
            or not _nonempty_string(tool_ref)
            or tool_ref not in verified_tools
        ):
            continue
        if evidence_id in valid:
            duplicates.add(evidence_id)
            valid.pop(evidence_id, None)
        elif evidence_id not in duplicates:
            valid[evidence_id] = item
    return valid


def _validate_typed_review_refs(
    source: dict[str, object],
    field: str,
    evidence_type: str,
    requested_ids: set[str],
    review_evidence: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    label = f"cinematic_validation.source_motion_review.{field}"
    refs = _string_list(
        source.get(field), label, errors, nonempty=True
    )
    if refs is None:
        return
    seen_refs: set[str] = set()
    delivery_counts: dict[str, int] = {}
    for evidence_id in refs:
        if evidence_id in seen_refs:
            errors.append(
                f"{label}: duplicate review_evidence_id {evidence_id}"
            )
            continue
        seen_refs.add(evidence_id)
        evidence = review_evidence.get(evidence_id)
        if evidence is None:
            errors.append(
                f"{label}: unknown review_evidence_id {evidence_id}"
            )
            continue
        if evidence.get("evidence_type") != evidence_type:
            errors.append(
                f"{label}: review evidence {evidence_id} must have "
                f"evidence_type {evidence_type}"
            )
            continue
        delivery_id = evidence.get("delivery_id")
        if isinstance(delivery_id, str):
            delivery_counts[delivery_id] = delivery_counts.get(delivery_id, 0) + 1
    if set(delivery_counts) != requested_ids:
        errors.append(
            f"{label}: referenced delivery IDs must match requested delivery "
            "IDs exactly"
        )
    for delivery_id in sorted(requested_ids):
        if delivery_counts.get(delivery_id, 0) > 1:
            errors.append(
                f"{label}: delivery_id {delivery_id} must be referenced "
                "exactly once"
            )


def _validate_actual_output_review(
    source: dict[str, object], plan: dict[str, object], errors: list[str]
) -> None:
    label = "cinematic_validation.source_motion_review"
    if source.get("actual_output_review_status") != "passed":
        errors.append(f"{label}.actual_output_review_status: must be passed")
    reviewed_ids = _string_list(
        source.get("reviewed_delivery_ids"),
        f"{label}.reviewed_delivery_ids",
        errors,
        nonempty=True,
    )
    requested_ids = _requested_delivery_ids(plan)
    if reviewed_ids is not None and (
        len(reviewed_ids) != len(requested_ids)
        or set(reviewed_ids) != set(requested_ids)
    ):
        errors.append(
            f"{label}.reviewed_delivery_ids: must match requested delivery "
            "IDs exactly"
        )
    requested_id_set = set(requested_ids)
    review_evidence = _valid_review_evidence(plan, requested_id_set)
    _validate_typed_review_refs(
        source,
        "frame_change_evidence_refs",
        "frame_change",
        requested_id_set,
        review_evidence,
        errors,
    )
    _validate_typed_review_refs(
        source,
        "contact_sheet_evidence_refs",
        "contact_sheet",
        requested_id_set,
        review_evidence,
        errors,
    )


def _validate_director_quality(
    audit: dict[str, object], real_unit_ids: list[str], errors: list[str]
) -> None:
    label = "cinematic_validation.director_quality"
    reviewed_ids = _string_list(
        audit.get("reviewed_edit_unit_ids"),
        f"{label}.reviewed_edit_unit_ids",
        errors,
        nonempty=True,
    )
    real_unit_id_set = set(real_unit_ids)
    reviewed_id_set: set[str] = set()
    if reviewed_ids is not None:
        for unit_id in reviewed_ids:
            if unit_id in reviewed_id_set:
                errors.append(
                    f"{label}.reviewed_edit_unit_ids: duplicate edit_unit_id "
                    f"{unit_id}"
                )
            elif unit_id not in real_unit_id_set:
                errors.append(
                    f"{label}.reviewed_edit_unit_ids: unknown edit_unit_id {unit_id}"
                )
            reviewed_id_set.add(unit_id)
        for unit_id in real_unit_ids:
            if unit_id not in reviewed_id_set:
                errors.append(
                    f"{label}.reviewed_edit_unit_ids: missing edit_unit_id {unit_id}"
                )

    rejected_flags = _string_list(
        audit.get("rejected_pattern_flags"),
        f"{label}.rejected_pattern_flags",
        errors,
        nonempty=False,
    )
    if rejected_flags:
        errors.append(f"{label}.rejected_pattern_flags: must be empty")
    _string_list(
        audit.get("evidence_refs"),
        f"{label}.evidence_refs",
        errors,
        nonempty=True,
    )


def _validate_subtext_fidelity(
    audit: dict[str, object], real_unit_ids: list[str], errors: list[str]
) -> None:
    label = "cinematic_validation.subtext_fidelity"
    reviewed_ids = _string_list(
        audit.get("reviewed_edit_unit_ids"),
        f"{label}.reviewed_edit_unit_ids",
        errors,
        nonempty=True,
    )
    real_unit_id_set = set(real_unit_ids)
    reviewed_id_set: set[str] = set()
    if reviewed_ids is not None:
        for unit_id in reviewed_ids:
            if unit_id in reviewed_id_set:
                errors.append(
                    f"{label}.reviewed_edit_unit_ids: duplicate edit_unit_id "
                    f"{unit_id}"
                )
            elif unit_id not in real_unit_id_set:
                errors.append(
                    f"{label}.reviewed_edit_unit_ids: unknown edit_unit_id "
                    f"{unit_id}"
                )
            reviewed_id_set.add(unit_id)
        for unit_id in real_unit_ids:
            if unit_id not in reviewed_id_set:
                errors.append(
                    f"{label}.reviewed_edit_unit_ids: missing edit_unit_id "
                    f"{unit_id}"
                )

    _string_list(
        audit.get("inner_life_refs"),
        f"{label}.inner_life_refs",
        errors,
        nonempty=True,
    )
    _string_list(
        audit.get("evidence_refs"),
        f"{label}.evidence_refs",
        errors,
        nonempty=True,
    )
    conflicts = _string_list(
        audit.get("unresolved_conflicts"),
        f"{label}.unresolved_conflicts",
        errors,
        nonempty=False,
    )
    if conflicts:
        errors.append(f"{label}.unresolved_conflicts: must be empty")


def _validate_ready_execution_claim(
    plan: dict[str, object], errors: list[str]
) -> None:
    if plan.get("plan_status") != "rendered":
        errors.append(
            "cinematic_validation.cinematic_ready: requires plan_status rendered"
        )
    deliveries = plan.get("delivery_specs")
    if not isinstance(deliveries, list) or not deliveries or any(
        not isinstance(delivery, dict)
        or delivery.get("status") != "rendered"
        or delivery.get("ready") is not True
        for delivery in deliveries
    ):
        errors.append(
            "cinematic_validation.cinematic_ready: every requested delivery "
            "must be rendered and ready"
        )
    edit_validation = plan.get("edit_validation")
    if (
        not isinstance(edit_validation, dict)
        or edit_validation.get("ready") is not True
    ):
        errors.append(
            "cinematic_validation.cinematic_ready: requires edit_validation.ready true"
        )
    execution = plan.get("execution")
    for field in ("tool_evidence", "probe_evidence", "rendered_outputs"):
        evidence = execution.get(field) if isinstance(execution, dict) else None
        if not isinstance(evidence, list) or not evidence:
            errors.append(
                f"cinematic_validation.cinematic_ready: requires non-empty "
                f"execution.{field}"
            )


def _validate_supporting_audit_arrays(
    audits: dict[str, dict[str, object]],
    plan: dict[str, object],
    cinematic_ready: bool,
    errors: list[str],
) -> None:
    static = audits.get("static_hold_audit")
    if static is not None:
        _array(
            static.get("intentional_holds"),
            "cinematic_validation.static_hold_audit.intentional_holds",
            errors,
        )
        _string_list(
            static.get("evidence_refs"),
            "cinematic_validation.static_hold_audit.evidence_refs",
            errors,
            nonempty=True,
        )
    source = audits.get("source_motion_review")
    if source is not None:
        _string_list(
            source.get("reviewed_asset_ids"),
            "cinematic_validation.source_motion_review.reviewed_asset_ids",
            errors,
            nonempty=True,
        )
        if cinematic_ready:
            _validate_actual_output_review(source, plan, errors)
        _string_list(
            source.get("evidence_refs"),
            "cinematic_validation.source_motion_review.evidence_refs",
            errors,
            nonempty=True,
        )


def validate_cinematic_plan(
    plan: dict[str, object], *, required: bool
) -> list[str]:
    """Return deterministic creative-readiness errors."""
    errors: list[str] = []
    cinematic = plan.get("cinematic_validation")
    if cinematic is None and "cinematic_validation" not in plan:
        if required:
            return ["cinematic_validation: required for cinematic delivery"]
        return []
    if not isinstance(cinematic, dict):
        return ["cinematic_validation: must be an object"]

    (
        real_unit_ids,
        unit_timelines,
        real_pairs,
        units_by_id,
    ) = _collect_timeline_coverage(plan)

    for field in CINEMATIC_FIELDS:
        if field not in cinematic:
            errors.append(f"cinematic_validation: missing field {field}")

    if cinematic.get("declared_mode") != "cinematic":
        errors.append("cinematic_validation.declared_mode: must be cinematic")
    if not _nonempty_string(cinematic.get("genre")):
        errors.append("cinematic_validation.genre: must be a non-empty string")

    audits: dict[str, dict[str, object]] = {}
    for field in AUDIT_FIELDS:
        audit = _audit_object(cinematic, field, errors)
        if audit is not None:
            audits[field] = audit
            _validate_audit_status(
                audit, f"cinematic_validation.{field}", errors
            )

    content = audits.get("content_consistency")
    if content is not None:
        _validate_content(content, errors)
    intent = audits.get("intent_fidelity")
    if intent is not None:
        _validate_intent_fidelity(intent, real_unit_ids, units_by_id, errors)
    identity = audits.get("character_identity_integrity")
    if identity is not None:
        _validate_identity(identity, errors)
    action = audits.get("action_reaction_coverage")
    if action is not None:
        _validate_action_events(action, set(real_unit_ids), errors)
    kinetic = audits.get("kinetic_profile_audit")
    if kinetic is not None:
        _validate_kinetic_records(kinetic, real_unit_ids, errors)
    transition = audits.get("transition_fulfillment")
    if transition is not None:
        _validate_transition_boundaries(
            transition, unit_timelines, real_pairs, errors
        )
    audio = audits.get("audio_presence_and_structure")
    if audio is not None:
        _validate_audio(audio, audits, errors)
    director = audits.get("director_quality")
    if director is not None:
        _validate_director_quality(director, real_unit_ids, errors)
    subtext = audits.get("subtext_fidelity")
    if subtext is not None:
        _validate_subtext_fidelity(subtext, real_unit_ids, errors)
    cinematic_ready = cinematic.get("cinematic_ready") is True
    _validate_supporting_audit_arrays(
        audits, plan, cinematic_ready, errors
    )

    ppt_flags = _string_list(
        cinematic.get("ppt_risk_flags"),
        "cinematic_validation.ppt_risk_flags",
        errors,
        nonempty=False,
    )
    if cinematic.get("cinematic_ready") is True and ppt_flags:
        errors.append(
            "cinematic_validation: PPT risk flags must be empty before ready"
        )
    _string_list(
        cinematic.get("evidence_refs"),
        "cinematic_validation.evidence_refs",
        errors,
        nonempty=True,
    )
    if "cinematic_ready" in cinematic and not isinstance(
        cinematic.get("cinematic_ready"), bool
    ):
        errors.append("cinematic_validation.cinematic_ready: must be a boolean")

    if cinematic_ready:
        _validate_ready_execution_claim(plan, errors)

    if cinematic_ready and errors:
        errors.append(
            "cinematic_validation: cinematic_ready cannot be true while "
            "cinematic blockers remain"
        )
    return list(dict.fromkeys(errors))
