import copy
import sys
import unittest
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from director_validation import validate_director_package


def valid_director_package():
    return {
        "project_brief": {
            "intent_contract": {
                "core_message": "Protection means choosing to bear the cost.",
                "audience_takeaway": (
                    "The choice, not victory, defines protection."
                ),
                "emotional_destination": "awe becomes recognition of cost",
                "must_show_claims": [
                    {
                        "intent_id": "INT-001",
                        "claim": "The lead chooses to absorb the impact.",
                        "required_evidence": (
                            "choice, impact, and protected person's reaction"
                        ),
                        "source_status": "user_locked",
                    }
                ],
                "must_preserve_events": ["EVENT-CHOICE", "EVENT-COST"],
                "must_not_imply": ["the hit is accidental"],
                "metaphor_policy": {
                    "mode": "literal_evidence_first",
                    "rule": (
                        "Metaphor supports but never replaces direct evidence."
                    ),
                },
                "source_fidelity": {
                    "mode": "concept_mode",
                    "locked_source_refs": [],
                    "allowed_adaptation": (
                        "blocking_coverage_and_local_pacing_only"
                    ),
                },
            }
        },
        "story_structure": {
            "beats": [{"beat_id": "B01", "intent_refs": ["INT-001"]}]
        },
        "screenplay": {
            "scenes": [
                {
                    "scene_id": "S01",
                    "intent_refs": ["INT-001"],
                    "scene_directing_plan": {
                        "scene_pov": "the protecting lead",
                        "audience_knowledge_before": (
                            "the threat is approaching"
                        ),
                        "audience_knowledge_after": (
                            "the lead chose the cost"
                        ),
                        "dramatic_turn": "the lead steps into the impact",
                        "character_objectives": [
                            "lead protects",
                            "companion escapes",
                        ],
                        "subtext_and_playable_actions": [
                            "hide the shaking hand"
                        ],
                        "blocking_map": (
                            "lead crosses from rear right to block the "
                            "central path"
                        ),
                        "reveal_strategy": (
                            "show the choice before revealing the wound"
                        ),
                        "camera_rule": (
                            "move only to reveal the protected companion"
                        ),
                        "coverage_strategy": (
                            "choice, impact, reaction, consequence"
                        ),
                        "visual_motif_progression": (
                            "open hand closes around the wound"
                        ),
                        "editorial_consequence": (
                            "the hidden wound motivates the next scene"
                        ),
                        "rejected_choices": ["unrelated dragon skyline"],
                        "intent_refs": ["INT-001"],
                    },
                }
            ]
        },
        "storyboard": [
            {
                "shot_id": "SH001",
                "runtime_role": "active",
                "intent_refs": ["INT-001"],
                "dramatic_question": "Will the lead choose the cost?",
                "information_delta": "the choice becomes visible",
                "emotion_delta": "resolve becomes pain",
                "power_delta": "",
                "spatial_delta": "the lead takes the exposed position",
                "blocking_change": "crosses into the threat path",
                "camera_necessity": "lateral move reveals who is protected",
                "performance_verb": "intercept",
                "shot_relation": "answers the prior threat setup",
                "director_rejection_reason": "",
            }
        ],
        "shot_prompts": [{"shot_id": "SH001", "intent_refs": ["INT-001"]}],
        "quality_report": {
            "ready": True,
            "checks": {
                "intent_fidelity": {
                    "status": "pass",
                    "unresolved_conflicts": [],
                    "evidence_refs": ["TRACE-INT-001"],
                },
                "director_quality": {
                    "status": "pass",
                    "unresolved_conflicts": [],
                    "evidence_refs": ["DIRECTOR-REVIEW-S01"],
                },
            },
        },
    }


def valid_series_context():
    return {
        "series_project_id": "series-divine-game",
        "episode_id": "EP-003",
        "series_snapshot_id": "snapshot-EP-002-lock",
        "asset_registry_version": "assets-v007",
        "episode_opening_state_ref": "episode_state.EP-002.closing",
        "foreshadow_refs": ["FS-shadow-oath"],
        "payoff_refs": ["PO-cost-reveal"],
    }


def valid_series_handoff():
    return {
        "episode_closing_state_delta": {
            "lead_wound_visibility": "hidden from companion",
            "antagonist_knowledge": "suspects the oath can be broken",
        },
        "continuity_evidence_refs": ["SH001.closing_state"],
        "foreshadow_status_changes": ["FS-shadow-oath: escalated"],
        "payoff_status_changes": [],
        "commit_eligibility": "external_series_controller_required",
        "handoff_status": "draft",
    }


class DirectorValidationTests(unittest.TestCase):
    def test_valid_director_package_passes(self):
        errors, blocked = validate_director_package(
            valid_director_package(), required=True
        )
        self.assertEqual(errors, [])
        self.assertFalse(blocked)

    def test_non_required_legacy_package_without_director_fields_passes(self):
        errors, blocked = validate_director_package(
            {"project_brief": {}, "quality_report": {"ready": True}},
            required=False,
        )
        self.assertEqual(errors, [])
        self.assertFalse(blocked)

    def test_intent_claim_ids_must_be_unique(self):
        package = valid_director_package()
        package["project_brief"]["intent_contract"]["must_show_claims"].append(
            copy.deepcopy(
                package["project_brief"]["intent_contract"][
                    "must_show_claims"
                ][0]
            )
        )
        errors, blocked = validate_director_package(package, required=True)
        self.assertIn(
            "project_brief.intent_contract: duplicate intent_id INT-001",
            errors,
        )
        self.assertTrue(blocked)

    def test_every_trace_ref_must_resolve(self):
        package = valid_director_package()
        package["storyboard"][0]["intent_refs"] = ["INT-MISSING"]
        errors, blocked = validate_director_package(package, required=True)
        self.assertIn("shot SH001: unknown intent_ref INT-MISSING", errors)
        self.assertTrue(blocked)

    def test_active_shot_requires_at_least_one_observable_delta(self):
        package = valid_director_package()
        for field in (
            "information_delta",
            "emotion_delta",
            "power_delta",
            "spatial_delta",
        ):
            package["storyboard"][0][field] = ""
        errors, blocked = validate_director_package(package, required=True)
        self.assertIn(
            "shot SH001: at least one director delta must be non-empty",
            errors,
        )
        self.assertTrue(blocked)

    def test_failed_director_gate_blocks_ready(self):
        package = valid_director_package()
        package["quality_report"]["checks"]["director_quality"][
            "status"
        ] = "fail"
        errors, blocked = validate_director_package(package, required=True)
        self.assertIn(
            "quality_report: ready cannot be true while director hard gates fail",
            errors,
        )
        self.assertTrue(blocked)

    def test_series_context_requires_exact_read_snapshot_fields(self):
        package = valid_director_package()
        package["project_brief"]["series_context"] = valid_series_context()
        del package["project_brief"]["series_context"]["series_snapshot_id"]
        errors, blocked = validate_director_package(package, required=True)
        self.assertIn(
            "project_brief.series_context: missing required field "
            "series_snapshot_id",
            errors,
        )
        self.assertTrue(blocked)

    def test_series_handoff_cannot_claim_commit(self):
        package = valid_director_package()
        package["project_brief"]["series_context"] = valid_series_context()
        package["quality_report"]["series_handoff"] = valid_series_handoff()
        package["quality_report"]["series_handoff"][
            "handoff_status"
        ] = "committed"
        errors, blocked = validate_director_package(package, required=True)
        self.assertIn(
            "quality_report.series_handoff.handoff_status: must be draft or "
            "unresolved",
            errors,
        )
        self.assertTrue(blocked)

    def test_series_handoff_requires_series_context(self):
        package = valid_director_package()
        package["quality_report"]["series_handoff"] = valid_series_handoff()
        errors, blocked = validate_director_package(package, required=True)
        self.assertIn(
            "quality_report.series_handoff: requires "
            "project_brief.series_context",
            errors,
        )
        self.assertTrue(blocked)


if __name__ == "__main__":
    unittest.main()
