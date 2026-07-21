"""Derive stable cinematic quality evidence from a validated edit plan."""

from __future__ import annotations

import html


AUDIT_FIELDS = (
    "content_consistency",
    "character_identity_integrity",
    "action_reaction_coverage",
    "kinetic_profile_audit",
    "shot_scale_and_composition_variety",
    "transition_fulfillment",
    "audio_presence_and_structure",
    "static_hold_audit",
    "source_motion_review",
)

_MARKDOWN_CONTROL_CHARACTERS = frozenset("`*_{}[]()#+-.!|~=^")


def _markdown_text(value: object) -> str:
    """Encode an untrusted scalar as one inert, traceable Markdown line value."""

    text = str(value)
    text = text.replace("\\", "\\\\").replace("\r", "\\r").replace("\n", "\\n")
    text = "".join(
        f"\\{character}"
        if character in _MARKDOWN_CONTROL_CHARACTERS
        else character
        for character in text
    )
    return html.escape(text, quote=True)


def cinematic_report_payload(plan: dict[str, object]) -> dict[str, object]:
    """Return the cinematic validation evidence intended for bundle handoff."""

    cinematic = plan.get("cinematic_validation")
    if not isinstance(cinematic, dict):
        raise ValueError("cinematic_validation is required")
    return {
        "edit_plan_id": plan.get("edit_plan_id"),
        "declared_mode": cinematic.get("declared_mode"),
        "genre": cinematic.get("genre"),
        "cinematic_ready": cinematic.get("cinematic_ready"),
        "ppt_risk_flags": cinematic.get("ppt_risk_flags", []),
        **{field: cinematic.get(field) for field in AUDIT_FIELDS},
        "evidence_refs": cinematic.get("evidence_refs", []),
    }


def cinematic_report_markdown(payload: dict[str, object]) -> str:
    """Render a readable, deterministic Markdown summary of report evidence."""

    ppt_risk_flags = payload["ppt_risk_flags"]
    flag_values = (
        ", ".join(_markdown_text(value) for value in ppt_risk_flags) or "none"
    )
    lines = [
        "# Cinematic Quality Report",
        "",
        f"- Edit plan: {_markdown_text(payload['edit_plan_id'])}",
        f"- Declared mode: {_markdown_text(payload['declared_mode'])}",
        f"- Genre: {_markdown_text(payload['genre'])}",
        "- Cinematic ready: "
        f"{_markdown_text(str(payload['cinematic_ready']).lower())}",
        f"- PPT risk flags: {_markdown_text(len(ppt_risk_flags))} ({flag_values})",
        "",
        "## Audit statuses",
        "",
    ]
    for field in AUDIT_FIELDS:
        audit = payload[field]
        lines.append(f"- `{field}`: {_markdown_text(audit['status'])}")
    lines.extend(["", "## Top-level evidence", ""])
    evidence_refs = payload["evidence_refs"]
    if evidence_refs:
        lines.extend(f"- {_markdown_text(ref)}" for ref in evidence_refs)
    else:
        lines.append("- None declared")
    return "\n".join(lines) + "\n"
