import copy
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from validate_package import main, validate_package


def valid_package():
    return {
        "project_brief": {
            "title": "Five Second Story",
            "target_duration_seconds": 5,
        },
        "creative_directions": [{"direction_id": "direction-01"}],
        "selected_treatment": {"direction_id": "direction-01"},
        "story_structure": {"beats": ["setup", "payoff"]},
        "screenplay": {"scenes": [{"scene_id": "scene-01"}]},
        "continuity_bible": {
            "characters": [
                {"character_id": "character-01", "description": "Lead"}
            ],
            "locations": [
                {"location_id": "location-01", "description": "Studio"}
            ],
            "wardrobes": [
                {"wardrobe_id": "wardrobe-01", "description": "Blue coat"}
            ],
            "props": [{"prop_id": "prop-01", "description": "Red book"}],
            "looks": [{"look_id": "look-01", "description": "Warm dusk"}],
            "audio_motifs": [
                {"audio_motif_id": "audio-01", "description": "Soft pulse"}
            ],
        },
        "storyboard": [
            {
                "shot_id": "shot-01",
                "scene_id": "scene-01",
                "sequence": 1,
                "duration_seconds": 5,
                "story_function": "Resolve the central beat",
                "beat_change": "Uncertainty becomes confidence",
                "visual_description": "The lead closes a red book and smiles.",
                "shot_size": "medium",
                "camera_angle": "eye-level",
                "lens_intent": "natural perspective",
                "composition": "centered subject",
                "camera_movement": "slow push-in",
                "character_ids": ["character-01"],
                "location_id": "location-01",
                "wardrobe_ids": ["wardrobe-01"],
                "prop_ids": ["prop-01"],
                "look_id": "look-01",
                "subject_action": "Closes the book",
                "performance": "Small, relieved smile",
                "opening_state": "Book open; subject looking down",
                "closing_state": "Book closed; subject looking forward",
                "continuity_in": "Blue coat and red book established",
                "continuity_out": "Book remains closed in both hands",
                "transitions": {"in": "cut", "out": "cut"},
                "storyboard_frame_prompt": "A centered medium shot in warm dusk light",
                "generation_strategy": "image-to-video",
                "risk_level": "medium",
                "risk_triggers": [
                    {
                        "failure_mode": "Book or hands drift",
                        "acceptance_check": "One red book remains in both hands",
                        "fallback_when": "Book or hand continuity is broken",
                    }
                ],
                "fallback_shot": None,
                "state_snapshot": {
                    "screen_direction": "Subject faces camera",
                    "eye_line": "Looks from book to camera",
                    "body_position": "Centered and seated",
                    "carried_props": ["prop-01 in both hands"],
                    "wardrobe_state": ["wardrobe-01 clean"],
                    "time": "dusk",
                    "weather": "interior, not applicable",
                    "light_direction": "camera left to right",
                    "damage_or_dirt": "none",
                    "opening_state": "Book open; subject looking down",
                    "closing_state": "Book closed; subject looking forward",
                },
            }
        ],
        "shot_prompts": [
            {
                "shot_id": "shot-01",
                "director_intent_zh": "角色合上书本并露出释然的微笑。",
                "universal_prompt_en": "The lead closes a red book and smiles.",
                "negative_prompt_en": "No extra fingers, no text artifacts.",
                "continuity_anchors": ["character-01", "look-01"],
                "reference_requirements": ["character-01", "location-01"],
                "audio_guidance": "A soft pulse resolves at the end.",
                "model_variants": [
                    {
                        "model_family": "default",
                        "prompt_adaptation": "Natural cinematic motion.",
                    }
                ],
            }
        ],
        "model_job_manifest": [
            {
                "job_id": "job-01",
                "shot_id": "shot-01",
                "job_purpose": "Generate the final shot",
                "model_family": "video-model",
                "generation_mode": "image-to-video",
                "prompt_source": "shot_prompts[shot_id=shot-01].universal_prompt_en",
                "reference_inputs": ["character-01", "location-01"],
                "duration_seconds": 5,
                "aspect": "16:9",
                "resolution": "1920x1080",
                "documented_parameters": {"seed": 42},
                "requires_manual_configuration": [],
            }
        ],
        "quality_report": {
            "ready": True,
            "status": "valid",
            "checks": {"fallback_audit": "not_required_no_high_risk_shots"},
            "unresolved_provider_fields": [],
        },
    }


def cinematic_package():
    package = valid_package()
    package["project_brief"]["target_duration_seconds"] = 30
    package["project_brief"]["cinematic_mode"] = {
        "input_mode": "concept_mode",
        "rhythm_preset": "A",
        "delivery_aspects": ["16:9", "9:16"],
        "style_preset": "dark-fantasy",
    }
    shot = package["storyboard"][0]
    shot["duration_seconds"] = 30
    shot.update(
        {
            "rhythm_role": "performance",
            "state_dependencies": [],
            "composition_16x9": "Centered medium shot with foreground depth",
            "recomposition_9x16": {
                "strategy": "recompose",
                "composition": "Vertical medium shot with clear lower third",
                "safe_areas": ["lower third clear for subtitles"],
            },
            "platform_capability_needs": ["reference-image-to-video"],
        }
    )
    landscape_job = package["model_job_manifest"][0]
    landscape_job["duration_seconds"] = 30
    landscape_job["aspect"] = "16:9"
    portrait_job = copy.deepcopy(landscape_job)
    portrait_job["job_id"] = "job-02"
    portrait_job["aspect"] = "9:16"
    package["model_job_manifest"].append(portrait_job)
    package["quality_report"]["checks"].update(
        {
            "narrative_clarity": {
                "protagonist": "pass",
                "goal": "pass",
                "obstacle": "pass",
                "causality": "pass",
                "ending_change": "pass",
            },
            "continuity_integrity": {
                "status": "pass",
                "unresolved_conflicts": [],
            },
        }
    )
    return package


def run_cli(path):
    stdout = io.StringIO()
    stderr = io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        exit_code = main([str(path)])
    return exit_code, stdout.getvalue(), stderr.getvalue()


class ValidatePackageTests(unittest.TestCase):
    def test_valid_package_has_no_errors(self):
        self.assertEqual(validate_package(valid_package()), [])

    def test_duplicate_shot_id_is_rejected(self):
        package = valid_package()
        package["storyboard"].append(copy.deepcopy(package["storyboard"][0]))

        self.assertIn(
            "storyboard: duplicate shot_id shot-01", validate_package(package)
        )

    def test_runtime_must_match_target(self):
        package = valid_package()
        package["project_brief"]["target_duration_seconds"] = 6

        self.assertIn(
            "runtime: expected 6.0 seconds, got 5.0", validate_package(package)
        )

    def test_unknown_character_reference_is_rejected(self):
        package = valid_package()
        package["storyboard"][0]["character_ids"] = ["character-missing"]

        self.assertIn(
            "shot shot-01: unknown character_id character-missing",
            validate_package(package),
        )

    def test_every_shot_requires_exactly_one_prompt(self):
        package = valid_package()
        package["shot_prompts"] = []

        self.assertIn(
            "shot_prompts: expected exactly one prompt for shot-01, got 0",
            validate_package(package),
        )

    def test_job_with_unknown_shot_is_rejected(self):
        package = valid_package()
        package["model_job_manifest"][0]["shot_id"] = "shot-missing"

        self.assertIn(
            "model_job_manifest job-01: unknown shot_id shot-missing",
            validate_package(package),
        )

    def test_high_risk_shot_requires_fallback(self):
        package = valid_package()
        package["storyboard"][0]["risk_level"] = "high"

        self.assertIn(
            "shot shot-01: high-risk shot requires fallback_shot",
            validate_package(package),
        )

    def test_fallback_candidate_is_excluded_from_active_runtime(self):
        package = valid_package()
        primary = package["storyboard"][0]
        primary["runtime_role"] = "active"
        primary["risk_level"] = "high"
        primary["fallback_shot"] = "shot-01-fallback"

        fallback = copy.deepcopy(primary)
        fallback["shot_id"] = "shot-01-fallback"
        fallback["runtime_role"] = "fallback"
        fallback["risk_level"] = "low"
        fallback["fallback_shot"] = None
        fallback["generation_strategy"] = "locked-off image-to-video"
        package["storyboard"].append(fallback)

        fallback_prompt = copy.deepcopy(package["shot_prompts"][0])
        fallback_prompt["shot_id"] = "shot-01-fallback"
        package["shot_prompts"].append(fallback_prompt)

        fallback_job = copy.deepcopy(package["model_job_manifest"][0])
        fallback_job["job_id"] = "job-01-fallback"
        fallback_job["shot_id"] = "shot-01-fallback"
        fallback_job["prompt_source"] = (
            "shot_prompts[shot_id=shot-01-fallback].universal_prompt_en"
        )
        package["model_job_manifest"].append(fallback_job)

        self.assertEqual(validate_package(package), [])

    def test_runtime_role_must_be_active_or_fallback(self):
        package = valid_package()
        package["storyboard"][0]["runtime_role"] = "alternate"

        self.assertEqual(
            validate_package(package),
            ["shot shot-01: runtime_role must be active or fallback"],
        )

    def test_risk_level_must_be_a_supported_string_without_crashing(self):
        for invalid_value in ([], {}, True, "extreme"):
            with self.subTest(invalid_value=invalid_value):
                package = valid_package()
                package["storyboard"][0]["risk_level"] = invalid_value
                self.assertIn(
                    "shot shot-01: risk_level must be low, medium, or high",
                    validate_package(package),
                )

    def test_medium_or_high_risk_requires_structured_risk_triggers(self):
        package = valid_package()
        package["storyboard"][0]["risk_triggers"] = []
        self.assertIn(
            "shot shot-01: medium or high risk requires risk_triggers",
            validate_package(package),
        )

        package = valid_package()
        package["storyboard"][0]["risk_triggers"] = ["identity drift"]
        self.assertIn(
            "shot shot-01: risk_triggers item 1 must be an object",
            validate_package(package),
        )

    def test_state_snapshot_is_required_and_must_match_boundary_states(self):
        package = valid_package()
        package["storyboard"][0].pop("state_snapshot")
        self.assertIn(
            "shot shot-01: missing required field state_snapshot",
            validate_package(package),
        )

        package = valid_package()
        package["storyboard"][0]["state_snapshot"]["closing_state"] = "Drifted"
        self.assertIn(
            "shot shot-01: state_snapshot closing_state must match shot closing_state",
            validate_package(package),
        )

    def test_model_variants_must_be_an_array_of_objects(self):
        package = valid_package()
        package["shot_prompts"][0]["model_variants"] = {"default": "variant"}
        self.assertIn(
            "shot_prompt shot-01: model_variants must be a list",
            validate_package(package),
        )

        package = valid_package()
        package["shot_prompts"][0]["model_variants"] = ["variant"]
        self.assertIn(
            "shot_prompt shot-01: model_variants item 1 must be an object",
            validate_package(package),
        )

    def test_job_duration_must_match_storyboard_shot_duration(self):
        package = valid_package()
        package["model_job_manifest"][0]["duration_seconds"] = 1
        self.assertIn(
            "model_job_manifest job-01: duration_seconds must match shot shot-01",
            validate_package(package),
        )

    def test_job_prompt_source_must_reference_canonical_shot_prompt(self):
        package = valid_package()
        package["model_job_manifest"][0]["prompt_source"] = "not-a-real-prompt"
        self.assertIn(
            "model_job_manifest job-01: prompt_source must equal "
            "shot_prompts[shot_id=shot-01].universal_prompt_en",
            validate_package(package),
        )

    def test_job_structured_fields_have_consumable_types(self):
        cases = (
            ("reference_inputs", False, "must be a list"),
            ("documented_parameters", "guessed", "must be an object"),
            ("requires_manual_configuration", False, "must be a list"),
        )
        for field, invalid_value, message in cases:
            with self.subTest(field=field):
                package = valid_package()
                package["model_job_manifest"][0][field] = invalid_value
                self.assertIn(
                    f"model_job_manifest job-01: {field} {message}",
                    validate_package(package),
                )

    def test_job_string_lists_reject_non_string_items(self):
        for field in ("reference_inputs", "requires_manual_configuration"):
            with self.subTest(field=field):
                package = valid_package()
                package["model_job_manifest"][0][field] = [False]
                self.assertIn(
                    f"model_job_manifest job-01: {field} item 1 "
                    "must be a non-empty string",
                    validate_package(package),
                )

    def test_quality_report_requires_ready_fallback_and_unresolved_audits(self):
        package = valid_package()
        package["quality_report"] = {"status": "valid"}
        errors = validate_package(package)
        for field in ("ready", "checks", "unresolved_provider_fields"):
            self.assertIn(
                f"quality_report: missing required field {field}", errors
            )

        package = valid_package()
        package["quality_report"]["ready"] = "yes"
        package["quality_report"]["checks"] = {}
        package["quality_report"]["unresolved_provider_fields"] = False
        errors = validate_package(package)
        self.assertIn("quality_report: ready must be a boolean", errors)
        self.assertIn("quality_report: checks must include fallback_audit", errors)
        self.assertIn(
            "quality_report: unresolved_provider_fields must be a list", errors
        )

    def test_quality_report_scalar_and_list_items_have_consumable_types(self):
        package = valid_package()
        package["quality_report"]["status"] = {"state": "valid"}
        package["quality_report"]["checks"]["fallback_audit"] = None
        package["quality_report"]["unresolved_provider_fields"] = [False]

        errors = validate_package(package)

        self.assertIn(
            "quality_report: status must be a non-empty string", errors
        )
        self.assertIn(
            "quality_report: checks.fallback_audit must be a non-empty string",
            errors,
        )
        self.assertIn(
            "quality_report: unresolved_provider_fields item 1 "
            "must be a non-empty string",
            errors,
        )

    def test_fallback_candidate_must_be_marked_fallback(self):
        package = valid_package()
        primary = package["storyboard"][0]
        primary["risk_level"] = "high"
        primary["fallback_shot"] = "shot-02"
        fallback = copy.deepcopy(primary)
        fallback["shot_id"] = "shot-02"
        fallback["risk_level"] = "low"
        fallback["fallback_shot"] = None
        package["storyboard"].append(fallback)

        self.assertIn(
            "shot shot-01: fallback_shot shot-02 must have runtime_role fallback",
            validate_package(package),
        )

    def test_fallback_candidate_must_preserve_story_contract_and_lower_risk(self):
        package = valid_package()
        primary = package["storyboard"][0]
        primary["runtime_role"] = "active"
        primary["risk_level"] = "medium"
        primary["fallback_shot"] = "shot-02"
        fallback = copy.deepcopy(primary)
        fallback["shot_id"] = "shot-02"
        fallback["runtime_role"] = "fallback"
        fallback["risk_level"] = "medium"
        fallback["fallback_shot"] = None
        fallback["beat_change"] = "A different story change"
        package["storyboard"].append(fallback)

        errors = validate_package(package)
        self.assertIn(
            "shot shot-01: fallback_shot shot-02 must preserve beat_change",
            errors,
        )
        self.assertIn(
            "shot shot-01: fallback_shot shot-02 must have a lower risk_level",
            errors,
        )

    def test_fallback_candidate_must_preserve_slot_and_continuity_references(self):
        compatible_fields = (
            "sequence",
            "duration_seconds",
            "scene_id",
            "character_ids",
            "location_id",
            "wardrobe_ids",
            "prop_ids",
            "look_id",
        )
        for field in compatible_fields:
            with self.subTest(field=field):
                package = valid_package()
                primary = package["storyboard"][0]
                primary["runtime_role"] = "active"
                primary["risk_level"] = "high"
                primary["fallback_shot"] = "shot-02"
                fallback = copy.deepcopy(primary)
                fallback["shot_id"] = "shot-02"
                fallback["runtime_role"] = "fallback"
                fallback["risk_level"] = "low"
                fallback["fallback_shot"] = None
                fallback[field] = (
                    99
                    if field in ("sequence", "duration_seconds")
                    else ([] if field.endswith("_ids") else "different")
                )
                package["storyboard"].append(fallback)

                self.assertIn(
                    f"shot shot-01: fallback_shot shot-02 must preserve {field}",
                    validate_package(package),
                )

    def test_prompt_with_unknown_shot_is_rejected(self):
        package = valid_package()
        package["shot_prompts"][0]["shot_id"] = "shot-missing"

        self.assertIn(
            "shot_prompt shot-missing: unknown shot_id shot-missing",
            validate_package(package),
        )

    def test_duplicate_job_id_is_rejected(self):
        package = valid_package()
        package["model_job_manifest"].append(
            copy.deepcopy(package["model_job_manifest"][0])
        )

        self.assertIn(
            "model_job_manifest: duplicate job_id job-01", validate_package(package)
        )

    def test_duplicate_continuity_character_id_is_rejected(self):
        package = valid_package()
        package["continuity_bible"]["characters"].append(
            copy.deepcopy(package["continuity_bible"]["characters"][0])
        )

        self.assertIn(
            "continuity_bible.characters: duplicate character_id character-01",
            validate_package(package),
        )

    def test_opening_state_must_not_be_empty(self):
        package = valid_package()
        package["storyboard"][0]["opening_state"] = ""

        self.assertIn(
            "shot shot-01: opening_state must not be empty", validate_package(package)
        )

    def test_unknown_scene_reference_is_rejected(self):
        package = valid_package()
        package["storyboard"][0]["scene_id"] = "scene-missing"

        self.assertEqual(
            validate_package(package),
            ["shot shot-01: unknown scene_id scene-missing"],
        )

    def test_shot_id_must_be_a_non_empty_string(self):
        for invalid_shot_id in ("", 123):
            with self.subTest(shot_id=invalid_shot_id):
                package = valid_package()
                package["storyboard"][0]["shot_id"] = invalid_shot_id

                self.assertEqual(
                    validate_package(package),
                    ["storyboard: shot_id must be a non-empty string"],
                )

    def test_prompt_shot_id_must_be_a_non_empty_string(self):
        for invalid_shot_id in ("", 123):
            with self.subTest(shot_id=invalid_shot_id):
                package = valid_package()
                extra_prompt = copy.deepcopy(package["shot_prompts"][0])
                extra_prompt["shot_id"] = invalid_shot_id
                package["shot_prompts"].append(extra_prompt)

                self.assertEqual(
                    validate_package(package),
                    ["shot_prompt: shot_id must be a non-empty string"],
                )

    def test_job_id_must_be_a_non_empty_string(self):
        for invalid_job_id in ("", 123):
            with self.subTest(job_id=invalid_job_id):
                package = valid_package()
                package["model_job_manifest"][0]["job_id"] = invalid_job_id

                self.assertEqual(
                    validate_package(package),
                    ["model_job_manifest: job_id must be a non-empty string"],
                )

    def test_scene_reference_is_rejected_when_screenplay_has_no_valid_scenes(self):
        for empty_screenplay in ([], {"scenes": []}):
            with self.subTest(screenplay=empty_screenplay):
                package = valid_package()
                package["screenplay"] = empty_screenplay

                self.assertEqual(
                    validate_package(package),
                    ["shot shot-01: unknown scene_id scene-01"],
                )

    def test_job_shot_id_must_be_a_non_empty_string(self):
        for invalid_shot_id in ("", 123):
            with self.subTest(shot_id=invalid_shot_id):
                package = valid_package()
                extra_job = copy.deepcopy(package["model_job_manifest"][0])
                extra_job["job_id"] = "job-02"
                extra_job["shot_id"] = invalid_shot_id
                package["model_job_manifest"].append(extra_job)

                self.assertEqual(
                    validate_package(package),
                    [
                        "model_job_manifest job-02: "
                        "shot_id must be a non-empty string"
                    ],
                )

    def test_scalar_shot_references_must_be_non_empty_strings(self):
        for field in ("scene_id", "location_id", "look_id"):
            for invalid_value in (None, "", " ", 123, [], {}):
                with self.subTest(field=field, value=invalid_value):
                    package = valid_package()
                    package["storyboard"][0][field] = invalid_value

                    self.assertEqual(
                        validate_package(package),
                        [f"shot shot-01: {field} must be a non-empty string"],
                    )

    def test_fallback_shot_must_be_a_valid_non_empty_string_when_provided(self):
        for invalid_value in ("", " ", 123, [], ["shot-01"], {}):
            with self.subTest(value=invalid_value):
                package = valid_package()
                package["storyboard"][0]["fallback_shot"] = invalid_value

                self.assertEqual(
                    validate_package(package),
                    ["shot shot-01: fallback_shot must be a non-empty string"],
                )

        package = valid_package()
        package["storyboard"][0]["fallback_shot"] = "shot-missing"
        self.assertEqual(
            validate_package(package),
            ["shot shot-01: unknown fallback_shot shot-missing"],
        )

    def test_reference_fields_must_be_lists_when_present(self):
        for field in (
            "character_ids",
            "wardrobe_ids",
            "prop_ids",
            "audio_motif_ids",
        ):
            for invalid_value in (None, "reference-01", 123, {}):
                with self.subTest(field=field, value=invalid_value):
                    package = valid_package()
                    package["storyboard"][0][field] = invalid_value

                    self.assertEqual(
                        validate_package(package),
                        [f"shot shot-01: {field} must be a list"],
                    )

    def test_reference_list_items_must_be_non_empty_strings(self):
        for field in (
            "character_ids",
            "wardrobe_ids",
            "prop_ids",
            "audio_motif_ids",
        ):
            for invalid_value in ("", " ", 123, [], {}):
                with self.subTest(field=field, value=invalid_value):
                    package = valid_package()
                    package["storyboard"][0][field] = [invalid_value]

                    self.assertEqual(
                        validate_package(package),
                        [
                            f"shot shot-01: {field} item 1 "
                            "must be a non-empty string"
                        ],
                    )

    def test_durations_must_be_positive_finite_json_numbers(self):
        invalid_values = (
            True,
            0,
            -1,
            float("nan"),
            float("inf"),
            float("-inf"),
            "5",
        )
        for invalid_value in invalid_values:
            with self.subTest(field="target_duration_seconds", value=invalid_value):
                package = valid_package()
                package["project_brief"]["target_duration_seconds"] = invalid_value
                self.assertEqual(
                    validate_package(package),
                    [
                        "project_brief: target_duration_seconds must be a "
                        "positive finite number"
                    ],
                )

            with self.subTest(field="shot.duration_seconds", value=invalid_value):
                package = valid_package()
                package["storyboard"][0]["duration_seconds"] = invalid_value
                self.assertEqual(
                    validate_package(package),
                    [
                        "shot shot-01: duration_seconds must be a "
                        "positive finite number"
                    ],
                )

            with self.subTest(field="job.duration_seconds", value=invalid_value):
                package = valid_package()
                package["model_job_manifest"][0]["duration_seconds"] = invalid_value
                self.assertEqual(
                    validate_package(package),
                    [
                        "model_job_manifest job-01: duration_seconds must be a "
                        "positive finite number"
                    ],
                )

    def test_decimal_duration_sum_is_exact(self):
        package = valid_package()
        package["project_brief"]["target_duration_seconds"] = 0.3
        package["storyboard"][0]["duration_seconds"] = 0.1
        package["model_job_manifest"][0]["duration_seconds"] = 0.1

        second_shot = copy.deepcopy(package["storyboard"][0])
        second_shot["shot_id"] = "shot-02"
        second_shot["sequence"] = 2
        second_shot["duration_seconds"] = 0.2
        package["storyboard"].append(second_shot)

        second_prompt = copy.deepcopy(package["shot_prompts"][0])
        second_prompt["shot_id"] = "shot-02"
        package["shot_prompts"].append(second_prompt)

        second_job = copy.deepcopy(package["model_job_manifest"][0])
        second_job["job_id"] = "job-02"
        second_job["shot_id"] = "shot-02"
        second_job["prompt_source"] = (
            "shot_prompts[shot_id=shot-02].universal_prompt_en"
        )
        second_job["duration_seconds"] = 0.2
        package["model_job_manifest"].append(second_job)

        self.assertEqual(validate_package(package), [])

    def test_very_large_integer_duration_does_not_overflow(self):
        package = valid_package()
        package["project_brief"]["target_duration_seconds"] = 10**4000

        errors = validate_package(package)

        self.assertEqual(len(errors), 1)
        self.assertTrue(errors[0].startswith("runtime: expected "))
        self.assertTrue(errors[0].endswith(" seconds, got 5.0"))

    def test_cli_accepts_valid_utf8_package(self):
        package = valid_package()
        package["project_brief"]["title"] = "\u4e94\u79d2\u6545\u4e8b"
        with tempfile.TemporaryDirectory() as temp_dir:
            package_path = Path(temp_dir) / "valid-package.json"
            package_path.write_text(
                json.dumps(package, ensure_ascii=False), encoding="utf-8"
            )

            exit_code, stdout, stderr = run_cli(package_path)

        self.assertEqual(exit_code, 0)
        self.assertEqual(stdout, "Production package is valid.\n")
        self.assertEqual(stderr, "")

    def test_cli_returns_one_for_validation_errors(self):
        package = valid_package()
        package["project_brief"]["target_duration_seconds"] = 6
        with tempfile.TemporaryDirectory() as temp_dir:
            package_path = Path(temp_dir) / "invalid-package.json"
            package_path.write_text(json.dumps(package), encoding="utf-8")

            exit_code, stdout, stderr = run_cli(package_path)

        self.assertEqual(exit_code, 1)
        self.assertIn("ERROR: runtime: expected 6.0 seconds, got 5.0", stdout)
        self.assertEqual(stderr, "")

    def test_cli_returns_two_for_missing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.json"

            exit_code, stdout, stderr = run_cli(missing_path)

        self.assertEqual(exit_code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("ERROR: could not read", stderr)
        self.assertNotIn("Traceback", stderr)

    def test_cli_returns_two_for_json_parse_value_errors(self):
        invalid_documents = {
            "invalid.json": "{",
            "too-long-integer.json": '{"value": ' + "1" * 5000 + "}",
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            for filename, document in invalid_documents.items():
                with self.subTest(filename=filename):
                    package_path = Path(temp_dir) / filename
                    package_path.write_text(document, encoding="utf-8")

                    exit_code, stdout, stderr = run_cli(package_path)

                    self.assertEqual(exit_code, 2)
                    self.assertEqual(stdout, "")
                    self.assertIn("ERROR: invalid JSON", stderr)
                    self.assertNotIn("Traceback", stderr)


class CinematicBriefValidationTests(unittest.TestCase):
    def test_valid_cinematic_package_has_no_errors(self):
        self.assertEqual(validate_package(cinematic_package()), [])

    def test_cinematic_mode_requires_all_brief_fields(self):
        for field in (
            "input_mode",
            "rhythm_preset",
            "delivery_aspects",
            "style_preset",
        ):
            with self.subTest(field=field):
                package = cinematic_package()
                package["project_brief"]["cinematic_mode"].pop(field)
                self.assertIn(
                    f"project_brief.cinematic_mode: missing required field {field}",
                    validate_package(package),
                )

    def test_cinematic_mode_rejects_invalid_input_rhythm_and_duration(self):
        cases = (
            (
                "input_mode",
                "novel",
                "project_brief.cinematic_mode: input_mode must be concept_mode or screenplay_mode",
            ),
            (
                "rhythm_preset",
                "D",
                "project_brief.cinematic_mode: rhythm_preset must be A, B, or C",
            ),
        )
        for field, value, expected_error in cases:
            with self.subTest(field=field):
                package = cinematic_package()
                package["project_brief"]["cinematic_mode"][field] = value
                self.assertIn(expected_error, validate_package(package))

        for duration in (29, 61):
            with self.subTest(duration=duration):
                package = cinematic_package()
                package["project_brief"]["target_duration_seconds"] = duration
                self.assertIn(
                    "project_brief: cinematic target_duration_seconds must be between 30 and 60",
                    validate_package(package),
                )

    def test_cinematic_mode_requires_exact_dual_aspects(self):
        for aspects in (["16:9"], ["9:16"], ["16:9", "16:9"]):
            with self.subTest(aspects=aspects):
                package = cinematic_package()
                package["project_brief"]["cinematic_mode"]["delivery_aspects"] = aspects
                self.assertIn(
                    "project_brief.cinematic_mode: delivery_aspects must contain exactly 16:9 and 9:16",
                    validate_package(package),
                )


if __name__ == "__main__":
    unittest.main()
