"""Validate cinematic character identity profiles and platform model locks."""

from __future__ import annotations

from typing import Any


IDENTITY_PROFILE_REQUIRED_FIELDS = (
    "identity_profile_id",
    "approval_status",
    "face_anchors",
    "body_anchors",
    "hair_anchors",
    "fixed_accessories",
    "signature_effect_anchors",
    "reference_asset_ids",
    "forbidden_drift",
)

IDENTITY_PROFILE_LIST_FIELDS = (
    "face_anchors",
    "body_anchors",
    "hair_anchors",
    "fixed_accessories",
    "signature_effect_anchors",
    "reference_asset_ids",
    "forbidden_drift",
)

CHARACTER_MODEL_BINDING_REQUIRED_FIELDS = (
    "character_id",
    "identity_profile_id",
    "model_family",
    "model_version",
    "identity_binding_method",
    "reference_input_ids",
    "lock_status",
)

CHARACTER_MODEL_BINDING_STRING_FIELDS = (
    "character_id",
    "identity_profile_id",
    "model_family",
    "model_version",
    "identity_binding_method",
)

IDENTITY_LOCK_STATUSES = {"pending", "locked"}


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _required_fields(
    value: dict[str, Any], fields: tuple[str, ...], owner: str, errors: list[str]
) -> None:
    for field in fields:
        if field not in value:
            errors.append(f"{owner}: missing required field {field}")


def _nonempty_string_list(
    value: object, owner: str, field: str, errors: list[str]
) -> list[str] | None:
    if not isinstance(value, list) or not value:
        errors.append(f"{owner}: {field} must be a non-empty list")
        return None
    normalized: list[str] = []
    for index, item in enumerate(value, start=1):
        if not _nonempty_string(item):
            errors.append(
                f"{owner}: {field} item {index} must be a non-empty string"
            )
        else:
            normalized.append(item.strip())
    return normalized


def _display_ids(values: set[str]) -> str:
    return "[" + ", ".join(sorted(values)) + "]"


def _validate_identity_integrity(
    quality_report: object,
    *,
    required_by: str | None,
    errors: list[str],
) -> None:
    if not isinstance(quality_report, dict):
        return
    checks = quality_report.get("checks")
    if not isinstance(checks, dict):
        return
    if "identity_integrity" not in checks:
        if required_by is not None:
            errors.append(
                "quality_report.checks: missing required field identity_integrity"
            )
        return

    integrity = checks.get("identity_integrity")
    if not isinstance(integrity, dict):
        errors.append("quality_report.checks.identity_integrity: expected object")
        return

    owner = "quality_report.checks.identity_integrity"
    _required_fields(
        integrity,
        ("status", "unresolved_conflicts", "evidence_refs"),
        owner,
        errors,
    )

    status = integrity.get("status")
    if status not in ("pass", "fail"):
        errors.append(f"{owner}.status must be pass or fail")

    conflicts = integrity.get("unresolved_conflicts")
    conflicts_valid = isinstance(conflicts, list)
    if not conflicts_valid:
        errors.append(f"{owner}.unresolved_conflicts must be a list")
    else:
        for index, conflict in enumerate(conflicts, start=1):
            if not _nonempty_string(conflict):
                errors.append(
                    f"{owner}: unresolved_conflicts item {index} "
                    "must be a non-empty string"
                )

    evidence = integrity.get("evidence_refs")
    evidence_valid = isinstance(evidence, list)
    if not evidence_valid:
        errors.append(f"{owner}.evidence_refs must be a list")
    else:
        for index, reference in enumerate(evidence, start=1):
            if not _nonempty_string(reference):
                errors.append(
                    f"{owner}: evidence_refs item {index} "
                    "must be a non-empty string"
                )

    if required_by is None:
        return
    if status != "pass":
        errors.append(f"{required_by}: identity_integrity must pass")
    if not conflicts_valid or bool(conflicts):
        errors.append(
            f"{required_by}: identity_integrity unresolved_conflicts must be empty"
        )
    if (
        not evidence_valid
        or not evidence
        or any(not _nonempty_string(reference) for reference in evidence)
    ):
        errors.append(
            f"{required_by}: identity_integrity evidence_refs must be a non-empty list"
        )


def validate_identity_locks(
    *,
    characters: list[object],
    shots: list[object],
    jobs: list[object],
    quality_report: object,
    ready: bool,
) -> list[str]:
    """Validate character identity profiles and cross-job model locks."""

    errors: list[str] = []
    profiles_by_character: dict[str, tuple[str, set[str]]] = {}
    seen_profile_ids: set[str] = set()

    for index, character in enumerate(characters, start=1):
        if not isinstance(character, dict):
            continue
        raw_character_id = character.get("character_id")
        character_id = (
            raw_character_id.strip()
            if _nonempty_string(raw_character_id)
            else f"item-{index}"
        )
        character_owner = f"character {character_id}"
        if "identity_profile" not in character:
            errors.append(
                f"{character_owner}: missing cinematic identity_profile"
            )
            continue
        profile = character.get("identity_profile")
        if not isinstance(profile, dict):
            errors.append(f"{character_owner}: identity_profile must be an object")
            continue

        owner = f"{character_owner} identity_profile"
        _required_fields(profile, IDENTITY_PROFILE_REQUIRED_FIELDS, owner, errors)
        raw_profile_id = profile.get("identity_profile_id")
        profile_id = (
            raw_profile_id.strip() if _nonempty_string(raw_profile_id) else None
        )
        if profile_id is None:
            errors.append(
                f"{owner}: identity_profile_id must be a non-empty string"
            )
        elif profile_id in seen_profile_ids:
            errors.append(
                f"identity_profile {profile_id}: duplicate identity_profile_id"
            )
        else:
            seen_profile_ids.add(profile_id)

        if profile.get("approval_status") != "approved":
            errors.append(f"{owner}: approval_status must be approved")

        normalized_lists: dict[str, list[str] | None] = {}
        for field in IDENTITY_PROFILE_LIST_FIELDS:
            normalized_lists[field] = _nonempty_string_list(
                profile.get(field), owner, field, errors
            )

        if (
            _nonempty_string(raw_character_id)
            and profile_id is not None
            and normalized_lists["reference_asset_ids"] is not None
        ):
            profiles_by_character[raw_character_id.strip()] = (
                profile_id,
                set(normalized_lists["reference_asset_ids"] or []),
            )

    shots_by_id: dict[str, dict[str, Any]] = {}
    for shot in shots:
        if isinstance(shot, dict) and _nonempty_string(shot.get("shot_id")):
            shots_by_id[shot["shot_id"].strip()] = shot

    lock_baselines: dict[tuple[str, str], dict[str, object]] = {}
    any_approved_job = False
    for job_index, job in enumerate(jobs, start=1):
        if not isinstance(job, dict):
            continue
        raw_job_id = job.get("job_id")
        job_id = (
            raw_job_id.strip()
            if _nonempty_string(raw_job_id)
            else f"item-{job_index}"
        )
        job_owner = f"model_job_manifest {job_id}"
        if job.get("approval_status") == "approved":
            any_approved_job = True

        if "character_model_bindings" not in job:
            errors.append(
                f"{job_owner}: missing required field character_model_bindings"
            )
            bindings: list[object] = []
        else:
            raw_bindings = job.get("character_model_bindings")
            if not isinstance(raw_bindings, list):
                errors.append(
                    f"{job_owner}: character_model_bindings must be a list"
                )
                bindings = []
            else:
                bindings = raw_bindings

        raw_job_reference_inputs = job.get("reference_inputs")
        job_reference_inputs = {
            value.strip()
            for value in (
                raw_job_reference_inputs
                if isinstance(raw_job_reference_inputs, list)
                else []
            )
            if _nonempty_string(value)
        }
        bound_character_ids: list[str] = []

        for binding_index, binding in enumerate(bindings, start=1):
            if not isinstance(binding, dict):
                errors.append(
                    f"{job_owner}: character_model_bindings item "
                    f"{binding_index} must be an object"
                )
                continue
            owner = (
                f"{job_owner} character_model_binding item {binding_index}"
            )
            _required_fields(
                binding,
                CHARACTER_MODEL_BINDING_REQUIRED_FIELDS,
                owner,
                errors,
            )
            normalized_strings: dict[str, str | None] = {}
            for field in CHARACTER_MODEL_BINDING_STRING_FIELDS:
                value = binding.get(field)
                if not _nonempty_string(value):
                    errors.append(f"{owner}: {field} must be a non-empty string")
                    normalized_strings[field] = None
                else:
                    normalized_strings[field] = value.strip()

            lock_status = binding.get("lock_status")
            if (
                not isinstance(lock_status, str)
                or lock_status not in IDENTITY_LOCK_STATUSES
            ):
                errors.append(
                    f"{owner}: lock_status must be pending or locked"
                )
            elif (
                job.get("approval_status") == "approved"
                and lock_status != "locked"
            ):
                errors.append(
                    f"{owner}: lock_status must be locked"
                )

            reference_ids = _nonempty_string_list(
                binding.get("reference_input_ids"),
                owner,
                "reference_input_ids",
                errors,
            )
            character_id = normalized_strings["character_id"]
            profile_id = normalized_strings["identity_profile_id"]
            model_family = normalized_strings["model_family"]
            if character_id is not None:
                if character_id in bound_character_ids:
                    errors.append(
                        f"{job_owner}: duplicate character_model_binding "
                        f"character_id {character_id}"
                    )
                bound_character_ids.append(character_id)

            profile_record = (
                profiles_by_character.get(character_id)
                if character_id is not None
                else None
            )
            if character_id is not None and profile_record is None:
                errors.append(f"{owner}: unknown character_id {character_id}")
            elif profile_record is not None and profile_id != profile_record[0]:
                errors.append(
                    f"{owner}: identity_profile_id {profile_id or ''} "
                    f"does not resolve to character {character_id}"
                )

            job_model_family = job.get("model_family")
            if (
                model_family is not None
                and _nonempty_string(job_model_family)
                and model_family != job_model_family.strip()
            ):
                errors.append(
                    f"{owner}: model_family must match job model_family "
                    f"{job_model_family.strip()}"
                )

            if reference_ids is not None:
                declared_profile_refs = (
                    profile_record[1] if profile_record else set()
                )
                for reference_id in reference_ids:
                    if (
                        profile_record is not None
                        and reference_id not in declared_profile_refs
                    ):
                        errors.append(
                            f"{owner}: reference_input_id {reference_id} must be "
                            f"declared by identity_profile {profile_record[0]}"
                        )
                    if reference_id not in job_reference_inputs:
                        errors.append(
                            f"{owner}: reference_input_id {reference_id} must exist "
                            "in job reference_inputs"
                        )

            if character_id is not None and model_family is not None:
                lock_values: dict[str, object] = {
                    "identity_profile_id": profile_id,
                    "model_version": normalized_strings["model_version"],
                    "identity_binding_method": normalized_strings[
                        "identity_binding_method"
                    ],
                    "reference_input_ids": tuple(sorted(set(reference_ids or []))),
                }
                lock_key = (character_id, model_family)
                baseline = lock_baselines.setdefault(lock_key, lock_values)
                if baseline is not lock_values:
                    for field in (
                        "identity_profile_id",
                        "model_version",
                        "identity_binding_method",
                        "reference_input_ids",
                    ):
                        if baseline[field] != lock_values[field]:
                            errors.append(
                                f"character {character_id} model lock: {field} "
                                f"drift within {model_family}"
                            )

        shot_id = job.get("shot_id")
        shot = (
            shots_by_id.get(shot_id.strip())
            if _nonempty_string(shot_id)
            else None
        )
        if shot is not None:
            raw_character_ids = shot.get("character_ids")
            expected_character_ids = {
                value.strip()
                for value in (
                    raw_character_ids if isinstance(raw_character_ids, list) else []
                )
                if _nonempty_string(value)
            }
            actual_character_ids = set(bound_character_ids)
            if (
                actual_character_ids != expected_character_ids
                or len(bound_character_ids) != len(actual_character_ids)
            ):
                errors.append(
                    f"{job_owner}: character_model_bindings character_ids must "
                    f"exactly match shot {shot_id.strip()} character_ids; expected "
                    f"{_display_ids(expected_character_ids)}, got "
                    f"{_display_ids(actual_character_ids)}"
                )

    required_by = (
        "quality_report.ready"
        if ready
        else "approved cinematic job" if any_approved_job else None
    )
    _validate_identity_integrity(
        quality_report, required_by=required_by, errors=errors
    )
    return errors
