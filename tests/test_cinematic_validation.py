import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures" / "editing"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_edit_plan import validate_edit_plan


def load_plan(name):
    with (FIXTURES / name).open("r", encoding="utf-8") as source:
        return json.load(source)


def edit_units(plan, timeline_index=0):
    return plan["timelines"][timeline_index]["video_tracks"][0][
        "edit_units"
    ]


class CinematicValidationTests(unittest.TestCase):
    def test_legacy_plan_remains_valid_without_cinematic_gate(self):
        self.assertEqual(validate_edit_plan(load_plan("valid_plan.json")), [])

    def test_require_cinematic_needs_canonical_object(self):
        errors = validate_edit_plan(
            load_plan("valid_plan.json"), require_cinematic=True
        )

        self.assertIn(
            "cinematic_validation: required for cinematic delivery", errors
        )

    def test_ppt_fixture_captures_the_reported_failure_geometry(self):
        plan = load_plan("cinematic_ppt_plan.json")
        units = edit_units(plan)
        cinematic = plan["cinematic_validation"]

        self.assertEqual(len(units), 8)
        self.assertEqual(
            sum(unit["duration_seconds"] for unit in units) / len(units),
            7.5,
        )
        self.assertEqual(
            [unit["transition_out"] for unit in units[:-1]],
            ["hard_cut"] * 7,
        )
        self.assertEqual(len(cinematic["transition_fulfillment"]["boundaries"]), 7)
        self.assertTrue(
            all(
                boundary["type"] == "hard_cut"
                for boundary in cinematic["transition_fulfillment"][
                    "boundaries"
                ]
            )
        )
        self.assertEqual(plan["audio_tracks"], [])
        self.assertTrue(
            all(not timeline["audio_track_refs"] for timeline in plan["timelines"])
        )
        self.assertTrue(
            all(
                audit["motion_layers"] == ["environment"]
                for audit in cinematic["kinetic_profile_audit"]["edit_units"]
            )
        )
        self.assertEqual(cinematic["content_consistency"]["status"], "passed")
        self.assertEqual(
            cinematic["character_identity_integrity"]["status"], "passed"
        )
        self.assertTrue(cinematic["cinematic_ready"])

    def test_static_silent_hard_cut_plan_cannot_claim_cinematic_ready(self):
        errors = validate_edit_plan(
            load_plan("cinematic_ppt_plan.json"), require_cinematic=True
        )

        self.assertIn(
            "cinematic_validation: PPT risk flags must be empty before ready",
            errors,
        )
        self.assertIn(
            "cinematic_validation: missing audio requires silent-form authorization",
            errors,
        )
        self.assertIn(
            "cinematic_validation: cinematic_ready cannot be true while "
            "cinematic blockers remain",
            errors,
        )
        for dimension in (
            "action_reaction_coverage",
            "kinetic_profile_audit",
            "shot_scale_and_composition_variety",
            "transition_fulfillment",
            "audio_presence_and_structure",
            "static_hold_audit",
            "source_motion_review",
        ):
            with self.subTest(dimension=dimension):
                self.assertTrue(
                    any(dimension in error for error in errors),
                    f"missing cinematic failure dimension: {dimension}",
                )

    def test_valid_fixture_documents_an_evidenced_intentional_hold(self):
        cinematic = load_plan("cinematic_valid_plan.json")[
            "cinematic_validation"
        ]
        holds = [
            unit
            for unit in cinematic["kinetic_profile_audit"]["edit_units"]
            if unit["intentional_hold"]
        ]

        self.assertEqual(len(holds), 1)
        self.assertTrue(holds[0]["hold_reason"])
        self.assertTrue(holds[0]["evidence_refs"])
        self.assertEqual(cinematic["ppt_risk_flags"], [])
        self.assertTrue(cinematic["cinematic_ready"])

    def test_complete_cinematic_evidence_passes(self):
        self.assertEqual(
            validate_edit_plan(
                load_plan("cinematic_valid_plan.json"),
                require_cinematic=True,
            ),
            [],
        )


if __name__ == "__main__":
    unittest.main()
