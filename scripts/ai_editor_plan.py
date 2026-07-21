"""Build the read-only AI-editor handoff derived from ``edit_master_plan``."""

from __future__ import annotations

import copy
from typing import Any

__all__ = ["ai_editor_plan_payload"]


_STEP_ORDER = (
    "probe",
    "bind",
    "timelines",
    "text",
    "audio",
    "look",
    "export",
    "validate",
)


def _unique_strings(values: list[object]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if isinstance(value, str) and value and value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _nested_evidence_refs(value: object) -> list[str]:
    refs: list[object] = []

    def visit(item: object) -> None:
        if isinstance(item, dict):
            for key, child in item.items():
                if key == "evidence_refs" and isinstance(child, list):
                    refs.extend(child)
                else:
                    visit(child)
        elif isinstance(item, list):
            for child in item:
                visit(child)

    visit(value)
    return _unique_strings(refs)


def _tool_evidence_refs(execution: object) -> list[str]:
    if not isinstance(execution, dict):
        return []
    refs: list[object] = []
    evidence = execution.get("tool_evidence")
    if not isinstance(evidence, list):
        return []
    for item in evidence:
        if not isinstance(item, dict):
            continue
        for key in ("tool_evidence_id", "evidence_id", "id", "path", "tool"):
            value = item.get(key)
            if isinstance(value, str) and value:
                refs.append(value)
                break
    return _unique_strings(refs)


def ai_editor_plan_payload(edit_master_plan: dict[str, Any]) -> dict[str, Any]:
    """Return a stable derivative payload without mutating or replacing the Canon."""

    if not isinstance(edit_master_plan, dict):
        raise TypeError("edit_master_plan must be an object")

    execution = edit_master_plan.get("execution")
    if not isinstance(execution, dict):
        execution = {}
    cinematic = edit_master_plan.get("cinematic_validation")
    if not isinstance(cinematic, dict):
        cinematic = {}

    edit_refs: list[object] = []
    for delivery in edit_master_plan.get("delivery_specs", []):
        if isinstance(delivery, dict) and isinstance(delivery.get("validation_refs"), list):
            edit_refs.extend(delivery["validation_refs"])

    probe_refs = [
        binding.get("asset_id")
        for binding in edit_master_plan.get("media_bindings", [])
        if isinstance(binding, dict) and "probe_status" in binding
    ]
    delivery_specs = copy.deepcopy(edit_master_plan.get("delivery_specs", []))

    return {
        "schema_version": 1,
        "artifact_role": "derived_ai_editor_handoff",
        "source_canon_artifact": "edit_master_plan.json",
        "source_edit_plan_id": edit_master_plan.get("edit_plan_id"),
        "read_only": True,
        "return_changes_to_canon": True,
        "media_bindings": copy.deepcopy(edit_master_plan.get("media_bindings", [])),
        "timelines": copy.deepcopy(edit_master_plan.get("timelines", [])),
        "audio_tracks": copy.deepcopy(edit_master_plan.get("audio_tracks", [])),
        "text_tracks": copy.deepcopy(edit_master_plan.get("text_tracks", [])),
        "look_plan": copy.deepcopy(edit_master_plan.get("look_plan", {})),
        "delivery_specs": delivery_specs,
        "export": {"delivery_specs": copy.deepcopy(delivery_specs)},
        "execution": {
            "step_order": list(_STEP_ORDER),
            "steps": [
                {"step_id": step_id, "sequence": sequence, "status": "pending"}
                for sequence, step_id in enumerate(_STEP_ORDER, start=1)
            ],
            "authorization_refs": {
                key: copy.deepcopy(execution.get(key))
                for key in (
                    "operation_authorization",
                    "dry_run_manifest_id",
                    "version_directory",
                    "authorized_manifest_id",
                    "authorized_version_directory",
                )
            },
        },
        "evidence_refs": {
            "edit": _unique_strings(edit_refs),
            "cinematic": _unique_strings(cinematic.get("evidence_refs", [])),
            "tool": _tool_evidence_refs(execution),
            "probe": _unique_strings(probe_refs),
            "review": _nested_evidence_refs(cinematic),
        },
    }
