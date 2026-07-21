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
    package["continuity_bible"]["characters"][0]["identity_profile"] = {
        "identity_profile_id": "IDP-character-01",
        "approval_status": "approved",
        "face_anchors": ["oval face", "small mole above left eyebrow"],
        "body_anchors": ["adult medium build", "consistent shoulder width"],
        "hair_anchors": ["short black hair"],
        "fixed_accessories": ["none"],
        "signature_effect_anchors": ["soft amber pulse"],
        "reference_asset_ids": [
            "REF-character-01-front",
            "REF-character-01-profile",
        ],
        "forbidden_drift": [
            "face change",
            "age change",
            "body proportion change",
            "hair change",
        ],
    }
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
            "state_before": {"story_state": "book open"},
            "state_after": {"story_state": "book closed"},
            "composition_16x9": "Centered medium shot with foreground depth",
            "recomposition_9x16": {
                "strategy": "recompose",
                "composition": "Vertical medium shot with clear lower third",
                "safe_areas": ["lower third clear for subtitles"],
            },
            "platform_capability_needs": ["reference-image-to-video"],
        }
    )
    prompt = package["shot_prompts"][0]
    prompt.update(
        {
            "approval_status": "final",
            "global_lock_block": "Lock character-01, prop-01, and look-01.",
            "direction_variants": {
                "16:9": (
                    "Centered medium shot with foreground depth; "
                    "the lead closes the red book."
                ),
                "9:16": (
                    "Vertical medium shot with clear lower third; "
                    "the lead closes the red book."
                ),
            },
        }
    )
    landscape_job = package["model_job_manifest"][0]
    landscape_job["duration_seconds"] = 30
    landscape_job["aspect"] = "16:9"
    landscape_job["approval_status"] = "approved"
    landscape_job["reference_inputs"].extend(
        [
            "REF-character-01-front",
            "REF-character-01-profile",
        ]
    )
    landscape_job["character_model_bindings"] = [
        {
            "character_id": "character-01",
            "identity_profile_id": "IDP-character-01",
            "model_family": "video-model",
            "model_version": "video-model-v1",
            "identity_binding_method": "multi-reference-subject-binding",
            "reference_input_ids": [
                "REF-character-01-front",
                "REF-character-01-profile",
            ],
            "lock_status": "locked",
        }
    ]
    landscape_job["prompt_source"] = {
        "global_lock_source": (
            "shot_prompts[shot_id=shot-01].global_lock_block"
        ),
        "direction_source": (
            "shot_prompts[shot_id=shot-01].direction_variants[16:9]"
        ),
    }
    portrait_job = copy.deepcopy(landscape_job)
    portrait_job["job_id"] = "job-02"
    portrait_job["aspect"] = "9:16"
    portrait_job["prompt_source"] = {
        "global_lock_source": (
            "shot_prompts[shot_id=shot-01].global_lock_block"
        ),
        "direction_source": (
            "shot_prompts[shot_id=shot-01].direction_variants[9:16]"
        ),
    }
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
            "identity_integrity": {
                "status": "pass",
                "unresolved_conflicts": [],
                "evidence_refs": ["identity-audit-character-01"],
            },
        }
    )
    return package


def cinematic_chain(shot_count=2):
    package = cinematic_package()
    duration = 30 / shot_count
    base_shot = package["storyboard"][0]
    base_prompt = package["shot_prompts"][0]
    base_jobs = package["model_job_manifest"]
    package["storyboard"] = []
    package["shot_prompts"] = []
    package["model_job_manifest"] = []

    for index in range(1, shot_count + 1):
        shot_id = f"shot-{index:02d}"
        shot = copy.deepcopy(base_shot)
        shot["shot_id"] = shot_id
        shot["sequence"] = index
        shot["duration_seconds"] = duration
        shot["state_dependencies"] = (
            [f"shot-{index - 1:02d}"] if index > 1 else []
        )
        shot["state_before"] = {"story_state": f"phase-{index - 1}"}
        shot["state_after"] = {"story_state": f"phase-{index}"}
        package["storyboard"].append(shot)

        prompt = copy.deepcopy(base_prompt)
        prompt["shot_id"] = shot_id
        package["shot_prompts"].append(prompt)

        for aspect_index, base_job in enumerate(base_jobs, start=1):
            job = copy.deepcopy(base_job)
            job["job_id"] = f"job-{index:02d}-{aspect_index}"
            job["shot_id"] = shot_id
            job["duration_seconds"] = duration
            job["prompt_source"] = {
                "global_lock_source": (
                    f"shot_prompts[shot_id={shot_id}].global_lock_block"
                ),
                "direction_source": (
                    f"shot_prompts[shot_id={shot_id}]."
                    f"direction_variants[{job['aspect']}]"
                ),
            }
            package["model_job_manifest"].append(job)

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

    def test_cinematic_character_requires_approved_identity_profile(self):
        package = cinematic_package()
        package["continuity_bible"]["characters"][0].pop("identity_profile")
        self.assertIn(
            "character character-01: missing cinematic identity_profile",
            validate_package(package),
        )

    def test_cinematic_job_cannot_drift_model_version_for_same_character(self):
        package = cinematic_package()
        package["model_job_manifest"][1]["character_model_bindings"][0][
            "model_version"
        ] = "video-model-v2"
        self.assertIn(
            "character character-01 model lock: model_version drift within video-model",
            validate_package(package),
        )

    def test_cinematic_job_cannot_drift_identity_reference_set(self):
        package = cinematic_package()
        package["model_job_manifest"][1]["character_model_bindings"][0][
            "reference_input_ids"
        ] = ["REF-character-01-front"]
        self.assertIn(
            "character character-01 model lock: reference_input_ids drift within video-model",
            validate_package(package),
        )

    def test_ready_cinematic_package_requires_identity_integrity_pass(self):
        package = cinematic_package()
        package["quality_report"]["checks"]["identity_integrity"][
            "status"
        ] = "fail"
        self.assertIn(
            "quality_report.ready: identity_integrity must pass",
            validate_package(package),
        )

    def test_identity_profile_requires_every_contract_field(self):
        fields = (
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
        for field in fields:
            with self.subTest(field=field):
                package = cinematic_package()
                package["continuity_bible"]["characters"][0][
                    "identity_profile"
                ].pop(field)
                self.assertIn(
                    f"character character-01 identity_profile: missing required field {field}",
                    validate_package(package),
                )

    def test_identity_profile_must_be_an_approved_object(self):
        package = cinematic_package()
        package["continuity_bible"]["characters"][0]["identity_profile"] = []
        self.assertIn(
            "character character-01: identity_profile must be an object",
            validate_package(package),
        )

        package = cinematic_package()
        package["continuity_bible"]["characters"][0]["identity_profile"][
            "approval_status"
        ] = "draft"
        self.assertIn(
            "character character-01 identity_profile: approval_status must be approved",
            validate_package(package),
        )

    def test_identity_profile_lists_are_non_empty_string_lists(self):
        list_fields = (
            "face_anchors",
            "body_anchors",
            "hair_anchors",
            "fixed_accessories",
            "signature_effect_anchors",
            "reference_asset_ids",
            "forbidden_drift",
        )
        for field in list_fields:
            for invalid_value, expected in (
                ([], f"character character-01 identity_profile: {field} must be a non-empty list"),
                ("anchor", f"character character-01 identity_profile: {field} must be a non-empty list"),
                ([None], f"character character-01 identity_profile: {field} item 1 must be a non-empty string"),
            ):
                with self.subTest(field=field, invalid_value=invalid_value):
                    package = cinematic_package()
                    package["continuity_bible"]["characters"][0][
                        "identity_profile"
                    ][field] = invalid_value
                    self.assertIn(expected, validate_package(package))

    def test_identity_profile_ids_must_be_non_empty_and_unique(self):
        package = cinematic_package()
        package["continuity_bible"]["characters"][0]["identity_profile"][
            "identity_profile_id"
        ] = ""
        self.assertIn(
            "character character-01 identity_profile: identity_profile_id must be a non-empty string",
            validate_package(package),
        )

        package = cinematic_package()
        second_character = copy.deepcopy(
            package["continuity_bible"]["characters"][0]
        )
        second_character["character_id"] = "character-02"
        package["continuity_bible"]["characters"].append(second_character)
        self.assertIn(
            "identity_profile IDP-character-01: duplicate identity_profile_id",
            validate_package(package),
        )

    def test_cinematic_job_requires_binding_list_and_object_items(self):
        package = cinematic_package()
        package["model_job_manifest"][0].pop("character_model_bindings")
        self.assertIn(
            "model_job_manifest job-01: missing required field character_model_bindings",
            validate_package(package),
        )

        package = cinematic_package()
        package["model_job_manifest"][0]["character_model_bindings"] = {}
        self.assertIn(
            "model_job_manifest job-01: character_model_bindings must be a list",
            validate_package(package),
        )

        package = cinematic_package()
        package["model_job_manifest"][0]["character_model_bindings"] = [None]
        self.assertIn(
            "model_job_manifest job-01: character_model_bindings item 1 must be an object",
            validate_package(package),
        )

    def test_character_binding_requires_every_contract_field(self):
        fields = (
            "character_id",
            "identity_profile_id",
            "model_family",
            "model_version",
            "identity_binding_method",
            "reference_input_ids",
            "lock_status",
        )
        for field in fields:
            with self.subTest(field=field):
                package = cinematic_package()
                package["model_job_manifest"][0]["character_model_bindings"][0].pop(
                    field
                )
                self.assertIn(
                    f"model_job_manifest job-01 character_model_binding item 1: missing required field {field}",
                    validate_package(package),
                )

    def test_character_binding_values_are_consumable_and_locked(self):
        for field in (
            "character_id",
            "identity_profile_id",
            "model_family",
            "model_version",
            "identity_binding_method",
        ):
            with self.subTest(field=field):
                package = cinematic_package()
                package["model_job_manifest"][0]["character_model_bindings"][0][
                    field
                ] = ""
                self.assertIn(
                    f"model_job_manifest job-01 character_model_binding item 1: {field} must be a non-empty string",
                    validate_package(package),
                )

        package = cinematic_package()
        package["model_job_manifest"][0]["character_model_bindings"][0][
            "lock_status"
        ] = "pending"
        self.assertIn(
            "model_job_manifest job-01 character_model_binding item 1: lock_status must be locked",
            validate_package(package),
        )

    def test_character_binding_reference_ids_are_non_empty_strings(self):
        for invalid_value, expected in (
            ([], "reference_input_ids must be a non-empty list"),
            ({}, "reference_input_ids must be a non-empty list"),
            ([None], "reference_input_ids item 1 must be a non-empty string"),
        ):
            with self.subTest(invalid_value=invalid_value):
                package = cinematic_package()
                package["model_job_manifest"][0]["character_model_bindings"][0][
                    "reference_input_ids"
                ] = invalid_value
                self.assertIn(
                    "model_job_manifest job-01 character_model_binding item 1: "
                    + expected,
                    validate_package(package),
                )

    def test_character_binding_character_and_profile_must_resolve(self):
        package = cinematic_package()
        binding = package["model_job_manifest"][0]["character_model_bindings"][0]
        binding["character_id"] = "character-99"
        self.assertIn(
            "model_job_manifest job-01 character_model_binding item 1: unknown character_id character-99",
            validate_package(package),
        )

        package = cinematic_package()
        binding = package["model_job_manifest"][0]["character_model_bindings"][0]
        binding["identity_profile_id"] = "IDP-character-99"
        self.assertIn(
            "model_job_manifest job-01 character_model_binding item 1: identity_profile_id IDP-character-99 does not resolve to character character-01",
            validate_package(package),
        )

    def test_binding_references_must_come_from_profile_and_job_inputs(self):
        package = cinematic_package()
        binding = package["model_job_manifest"][0]["character_model_bindings"][0]
        binding["reference_input_ids"].append("unapproved-reference")
        package["model_job_manifest"][0]["reference_inputs"].append(
            "unapproved-reference"
        )
        self.assertIn(
            "model_job_manifest job-01 character_model_binding item 1: reference_input_id unapproved-reference must be declared by identity_profile IDP-character-01",
            validate_package(package),
        )

        package = cinematic_package()
        package["model_job_manifest"][0]["reference_inputs"].remove(
            "REF-character-01-profile"
        )
        self.assertIn(
            "model_job_manifest job-01 character_model_binding item 1: reference_input_id REF-character-01-profile must exist in job reference_inputs",
            validate_package(package),
        )

    def test_job_binding_characters_exactly_match_the_shot(self):
        package = cinematic_package()
        package["model_job_manifest"][0]["character_model_bindings"] = []
        self.assertIn(
            "model_job_manifest job-01: character_model_bindings character_ids must exactly match shot shot-01 character_ids; expected [character-01], got []",
            validate_package(package),
        )

        package = cinematic_package()
        package["storyboard"][0]["character_ids"] = []
        for job in package["model_job_manifest"]:
            job["character_model_bindings"] = []
        self.assertEqual(validate_package(package), [])

    def test_character_binding_profile_and_method_cannot_drift(self):
        for field, value in (
            ("identity_profile_id", "IDP-character-other"),
            ("identity_binding_method", "identity-adapter"),
        ):
            with self.subTest(field=field):
                package = cinematic_package()
                package["model_job_manifest"][1]["character_model_bindings"][0][
                    field
                ] = value
                self.assertIn(
                    f"character character-01 model lock: {field} drift within video-model",
                    validate_package(package),
                )

    def test_character_binding_reference_order_is_normalized_for_model_lock(self):
        package = cinematic_package()
        package["model_job_manifest"][1]["character_model_bindings"][0][
            "reference_input_ids"
        ].reverse()
        self.assertEqual(validate_package(package), [])

    def test_approved_job_also_requires_identity_integrity_gate(self):
        package = cinematic_package()
        package["quality_report"]["ready"] = False
        package["shot_prompts"][0]["approval_status"] = "draft"
        package["model_job_manifest"][1]["approval_status"] = "blocked"
        identity = package["quality_report"]["checks"]["identity_integrity"]
        identity["status"] = "fail"
        identity["unresolved_conflicts"] = ["face mismatch"]
        identity["evidence_refs"] = []
        errors = validate_package(package)
        self.assertIn(
            "approved cinematic job: identity_integrity must pass", errors
        )
        self.assertIn(
            "approved cinematic job: identity_integrity unresolved_conflicts must be empty",
            errors,
        )
        self.assertIn(
            "approved cinematic job: identity_integrity evidence_refs must be a non-empty list",
            errors,
        )

    def test_ready_identity_integrity_requires_empty_conflicts_and_evidence(self):
        package = cinematic_package()
        identity = package["quality_report"]["checks"]["identity_integrity"]
        identity["unresolved_conflicts"] = ["hair drift"]
        identity["evidence_refs"] = []
        errors = validate_package(package)
        self.assertIn(
            "quality_report.ready: identity_integrity unresolved_conflicts must be empty",
            errors,
        )
        self.assertIn(
            "quality_report.ready: identity_integrity evidence_refs must be a non-empty list",
            errors,
        )

    def test_identity_contract_malformed_collections_do_not_crash(self):
        cases = (
            ("characters", "not-a-list"),
            ("storyboard", {}),
            ("model_job_manifest", {}),
            ("quality_report", []),
        )
        for field, invalid_value in cases:
            with self.subTest(field=field):
                package = cinematic_package()
                if field == "characters":
                    package["continuity_bible"][field] = invalid_value
                else:
                    package[field] = invalid_value
                errors = validate_package(package)
                self.assertIsInstance(errors, list)

        package = cinematic_package()
        package["quality_report"]["checks"]["identity_integrity"] = []
        self.assertIn(
            "quality_report.checks.identity_integrity: expected object",
            validate_package(package),
        )

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

    def test_legacy_package_without_cinematic_mode_remains_valid(self):
        self.assertEqual(validate_package(valid_package()), [])

    def test_explicit_null_cinematic_mode_is_rejected(self):
        package = valid_package()
        package["project_brief"]["cinematic_mode"] = None
        self.assertEqual(
            validate_package(package),
            ["project_brief.cinematic_mode: expected object"],
        )

    def test_non_object_cinematic_mode_is_rejected(self):
        for invalid_value in ("enabled", []):
            with self.subTest(invalid_value=invalid_value):
                package = valid_package()
                package["project_brief"]["cinematic_mode"] = invalid_value
                self.assertEqual(
                    validate_package(package),
                    ["project_brief.cinematic_mode: expected object"],
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

    def test_cinematic_shot_requires_graph_and_aspect_fields(self):
        fields = (
            "rhythm_role",
            "state_dependencies",
            "state_before",
            "state_after",
            "composition_16x9",
            "recomposition_9x16",
            "platform_capability_needs",
        )
        for field in fields:
            with self.subTest(field=field):
                package = cinematic_package()
                package["storyboard"][0].pop(field)
                self.assertIn(
                    f"shot shot-01: missing required field {field}",
                    validate_package(package),
                )

    def test_cinematic_shot_rejects_self_and_unknown_dependencies(self):
        cases = (
            ("shot-01", "shot shot-01: state_dependency must not reference itself"),
            ("shot-missing", "shot shot-01: unknown state_dependency shot-missing"),
        )
        for dependency, expected_error in cases:
            with self.subTest(dependency=dependency):
                package = cinematic_package()
                package["storyboard"][0]["state_dependencies"] = [dependency]
                self.assertIn(expected_error, validate_package(package))

    def test_cinematic_state_dependencies_reject_forward_edges(self):
        package = cinematic_chain(2)
        package["storyboard"][0]["state_dependencies"] = ["shot-02"]
        package["storyboard"][1]["state_dependencies"] = []
        self.assertIn(
            "shot shot-01: state_dependency shot-02 must reference a lower sequence",
            validate_package(package),
        )

    def test_cinematic_dependency_order_uses_sequence_when_array_is_shuffled(self):
        package = cinematic_chain(2)
        package["storyboard"].reverse()
        self.assertEqual(validate_package(package), [])

    def test_cinematic_dependency_rejects_future_sequence_in_shuffled_array(self):
        package = cinematic_chain(2)
        first, second = package["storyboard"]
        first["state_dependencies"] = ["shot-02"]
        first["state_before"] = copy.deepcopy(second["state_after"])
        second["state_dependencies"] = []
        package["storyboard"] = [second, first]
        self.assertIn(
            "shot shot-01: state_dependency shot-02 must reference a lower sequence",
            validate_package(package),
        )

    def test_cinematic_duplicate_active_sequences_are_rejected(self):
        package = cinematic_chain(2)
        package["storyboard"][1]["sequence"] = 1
        self.assertIn(
            "storyboard: duplicate active sequence 1",
            validate_package(package),
        )

    def test_duplicate_valid_sequences_are_rejected_with_an_invalid_peer(self):
        package = cinematic_chain(3)
        package["storyboard"][1]["sequence"] = 1
        package["storyboard"][2]["sequence"] = "third"
        errors = validate_package(package)
        self.assertIn("storyboard: duplicate active sequence 1", errors)
        self.assertIn("shot shot-03: sequence must be an integer", errors)

    def test_invalid_or_missing_sequence_reports_shape_error_without_crashing(self):
        cases = (
            (
                "invalid",
                "shot shot-01: sequence must be an integer",
            ),
            (
                "missing",
                "shot shot-01: missing required field sequence",
            ),
        )
        for case, expected in cases:
            with self.subTest(case=case):
                package = cinematic_chain(2)
                if case == "invalid":
                    package["storyboard"][0]["sequence"] = "first"
                else:
                    package["storyboard"][0].pop("sequence")
                self.assertIn(expected, validate_package(package))

    def test_cinematic_state_dependencies_reject_two_node_cycles(self):
        package = cinematic_chain(2)
        package["storyboard"][0]["state_dependencies"] = ["shot-02"]
        self.assertIn(
            "storyboard: cinematic state_dependencies must be acyclic",
            validate_package(package),
        )

    def test_cinematic_state_dependencies_reject_longer_cycles(self):
        package = cinematic_chain(3)
        package["storyboard"][0]["state_dependencies"] = ["shot-03"]
        self.assertIn(
            "storyboard: cinematic state_dependencies must be acyclic",
            validate_package(package),
        )

    def test_cinematic_dependency_handoff_must_match_declared_state(self):
        package = cinematic_chain(2)
        package["storyboard"][1]["state_before"] = {
            "story_state": "contradiction"
        }
        self.assertIn(
            "shot shot-02: state_before must include matching state_after "
            "of dependency shot-01",
            validate_package(package),
        )

    def test_cinematic_dependency_handoff_allows_additional_incoming_state(self):
        package = cinematic_chain(2)
        package["storyboard"][1]["state_before"]["weather"] = "rain"
        self.assertEqual(validate_package(package), [])

    def test_cinematic_before_and_after_states_are_non_empty_objects(self):
        for field in ("state_before", "state_after"):
            for invalid_value in (None, "state", [], {}):
                with self.subTest(field=field, invalid_value=invalid_value):
                    package = cinematic_package()
                    package["storyboard"][0][field] = invalid_value
                    self.assertIn(
                        f"shot shot-01: {field} must be a non-empty object",
                        validate_package(package),
                    )

    def test_cinematic_shot_validates_portrait_recomposition(self):
        package = cinematic_package()
        package["storyboard"][0]["recomposition_9x16"] = {
            "strategy": "crop",
            "composition": "",
            "safe_areas": "lower third",
        }
        errors = validate_package(package)
        self.assertIn(
            "shot shot-01: recomposition_9x16.strategy must be recompose or independent_generation",
            errors,
        )
        self.assertIn(
            "shot shot-01: recomposition_9x16.composition "
            "must be a non-empty string",
            errors,
        )
        self.assertIn(
            "shot shot-01: recomposition_9x16.safe_areas must be a list",
            errors,
        )

    def test_cinematic_composition_fields_require_non_empty_strings(self):
        cases = (
            ("composition_16x9", 7),
            ("composition_16x9", {}),
            ("composition_16x9", ""),
            ("portrait", 7),
            ("portrait", {}),
            ("portrait", ""),
        )
        for field, invalid_value in cases:
            with self.subTest(field=field, invalid_value=invalid_value):
                package = cinematic_package()
                if field == "portrait":
                    package["storyboard"][0]["recomposition_9x16"][
                        "composition"
                    ] = invalid_value
                    expected = (
                        "shot shot-01: recomposition_9x16.composition "
                        "must be a non-empty string"
                    )
                else:
                    package["storyboard"][0][field] = invalid_value
                    expected = (
                        "shot shot-01: composition_16x9 must be a non-empty string"
                    )
                self.assertIn(expected, validate_package(package))

    def test_cinematic_safe_areas_require_non_empty_string_items(self):
        package = cinematic_package()
        package["storyboard"][0]["recomposition_9x16"]["safe_areas"] = [
            None
        ]
        self.assertIn(
            "shot shot-01 recomposition_9x16: safe_areas item 1 "
            "must be a non-empty string",
            validate_package(package),
        )

    def test_cinematic_safe_areas_must_not_be_empty(self):
        package = cinematic_package()
        package["storyboard"][0]["recomposition_9x16"]["safe_areas"] = []
        self.assertIn(
            "shot shot-01: recomposition_9x16.safe_areas must not be empty",
            validate_package(package),
        )

    def test_cinematic_prompt_requires_canonical_lock_and_direction_variants(self):
        for field in ("approval_status", "global_lock_block", "direction_variants"):
            with self.subTest(field=field):
                package = cinematic_package()
                package["shot_prompts"][0].pop(field)
                self.assertIn(
                    f"shot_prompt shot-01: missing required field {field}",
                    validate_package(package),
                )

    def test_cinematic_direction_variants_must_be_non_empty_strings(self):
        for aspect in ("16:9", "9:16"):
            for invalid_value in (None, "", {}):
                with self.subTest(aspect=aspect, invalid_value=invalid_value):
                    package = cinematic_package()
                    package["shot_prompts"][0]["direction_variants"][
                        aspect
                    ] = invalid_value
                    self.assertIn(
                        f"shot_prompt shot-01: direction_variants[{aspect}] "
                        "must be a non-empty string",
                        validate_package(package),
                    )

    def test_independent_generation_requires_distinct_direction_variants(self):
        package = cinematic_package()
        shot = package["storyboard"][0]
        shot["recomposition_9x16"]["strategy"] = "independent_generation"
        variants = package["shot_prompts"][0]["direction_variants"]
        variants["9:16"] = variants["16:9"]
        self.assertIn(
            "shot_prompt shot-01: independent_generation requires distinct "
            "16:9 and 9:16 direction variants",
            validate_package(package),
        )

    def test_recompose_requires_distinct_direction_variants(self):
        package = cinematic_package()
        variants = package["shot_prompts"][0]["direction_variants"]
        variants["9:16"] = variants["16:9"]
        shot = package["storyboard"][0]
        shot["recomposition_9x16"]["composition"] = shot[
            "composition_16x9"
        ]
        self.assertIn(
            "shot_prompt shot-01: 16:9 and 9:16 direction variants "
            "must be distinct",
            validate_package(package),
        )

    def test_landscape_direction_contains_composition_16x9(self):
        package = cinematic_package()
        package["shot_prompts"][0]["direction_variants"]["16:9"] = (
            "A generic landscape direction without the declared framing."
        )
        self.assertIn(
            "shot_prompt shot-01: 16:9 direction variant must include "
            "composition_16x9",
            validate_package(package),
        )

    def test_portrait_direction_contains_recomposition(self):
        package = cinematic_package()
        package["shot_prompts"][0]["direction_variants"]["9:16"] = (
            "A copied generic direction without the declared portrait framing."
        )
        self.assertIn(
            "shot_prompt shot-01: 9:16 direction variant must include "
            "recomposition_9x16.composition",
            validate_package(package),
        )

    def test_cinematic_jobs_reference_their_matching_direction_variant(self):
        package = cinematic_package()
        package["model_job_manifest"][1]["prompt_source"][
            "direction_source"
        ] = (
            "shot_prompts[shot_id=shot-01].direction_variants[16:9]"
        )
        self.assertIn(
            "model_job_manifest job-02: prompt_source.direction_source must equal "
            "shot_prompts[shot_id=shot-01].direction_variants[9:16]",
            validate_package(package),
        )

    def test_cinematic_job_aspect_must_be_a_supported_non_empty_string(self):
        cases = (
            ("1:1", "1:1"),
            (1, "1"),
            ({}, "{}"),
        )
        for aspect, source_aspect in cases:
            with self.subTest(aspect=aspect):
                package = cinematic_package()
                job = package["model_job_manifest"][0]
                job["aspect"] = aspect
                job["prompt_source"]["direction_source"] = (
                    "shot_prompts[shot_id=shot-01]."
                    f"direction_variants[{source_aspect}]"
                )
                self.assertIn(
                    "model_job_manifest job-01: aspect must be a non-empty "
                    "string in project_brief.cinematic_mode.delivery_aspects",
                    validate_package(package),
                )

    def test_cinematic_job_direction_source_must_resolve_to_existing_variant(self):
        package = cinematic_package()
        package["shot_prompts"][0]["direction_variants"].pop("9:16")
        self.assertIn(
            "model_job_manifest job-02: prompt_source.direction_source must "
            "resolve to shot_prompt shot-01 direction_variants[9:16]",
            validate_package(package),
        )

    def test_cinematic_job_sources_must_resolve_to_the_bound_shot_prompt(self):
        package = cinematic_package()
        package["shot_prompts"] = []
        errors = validate_package(package)
        self.assertIn(
            "model_job_manifest job-01: prompt_source.global_lock_source must "
            "resolve to shot_prompt shot-01 global_lock_block",
            errors,
        )
        self.assertIn(
            "model_job_manifest job-01: prompt_source.direction_source must "
            "resolve to shot_prompt shot-01 direction_variants[16:9]",
            errors,
        )

    def test_cinematic_wrong_sources_do_not_resolve(self):
        package = cinematic_package()
        source = package["model_job_manifest"][0]["prompt_source"]
        source["global_lock_source"] = (
            "shot_prompts[shot_id=shot-99].global_lock_block"
        )
        source["direction_source"] = (
            "shot_prompts[shot_id=shot-99].direction_variants[16:9]"
        )
        errors = validate_package(package)
        self.assertIn(
            "model_job_manifest job-01: prompt_source.global_lock_source must "
            "resolve to shot_prompt shot-01 global_lock_block",
            errors,
        )
        self.assertIn(
            "model_job_manifest job-01: prompt_source.direction_source must "
            "resolve to shot_prompt shot-01 direction_variants[16:9]",
            errors,
        )

    def test_cinematic_job_requires_canonical_global_lock_source(self):
        package = cinematic_package()
        package["model_job_manifest"][0]["prompt_source"].pop(
            "global_lock_source"
        )
        self.assertIn(
            "model_job_manifest job-01 prompt_source: missing required field "
            "global_lock_source",
            validate_package(package),
        )

    def test_legacy_job_aspect_remains_unrestricted(self):
        package = valid_package()
        package["model_job_manifest"][0]["aspect"] = "1:1"
        self.assertEqual(validate_package(package), [])

    def test_cinematic_manifest_requires_each_delivery_aspect_per_shot(self):
        package = cinematic_package()
        package["model_job_manifest"] = [package["model_job_manifest"][0]]
        self.assertIn(
            "model_job_manifest: shot shot-01 missing cinematic aspect job 9:16",
            validate_package(package),
        )

    def test_cinematic_quality_requires_both_hard_gate_records(self):
        for field in ("narrative_clarity", "continuity_integrity"):
            with self.subTest(field=field):
                package = cinematic_package()
                package["quality_report"]["checks"].pop(field)
                self.assertIn(
                    f"quality_report.checks: missing required field {field}",
                    validate_package(package),
                )

    def test_ready_cinematic_package_rejects_failed_narrative_gate(self):
        package = cinematic_package()
        package["quality_report"]["checks"]["narrative_clarity"][
            "goal"
        ] = "fail"
        self.assertIn(
            "quality_report: ready cannot be true while cinematic hard gates fail",
            validate_package(package),
        )

    def test_ready_cinematic_package_rejects_continuity_conflicts(self):
        package = cinematic_package()
        continuity = package["quality_report"]["checks"][
            "continuity_integrity"
        ]
        continuity["status"] = "fail"
        continuity["unresolved_conflicts"] = ["prop-01 changes hands"]
        self.assertIn(
            "quality_report: ready cannot be true while cinematic hard gates fail",
            validate_package(package),
        )

    def test_unready_cinematic_failed_gate_requires_blocked_compilation(self):
        package = cinematic_package()
        package["quality_report"]["ready"] = False
        package["quality_report"]["checks"]["narrative_clarity"][
            "goal"
        ] = "fail"
        self.assertEqual(
            validate_package(package),
            [
                "shot_prompt shot-01: approval_status must be draft or blocked "
                "while cinematic hard gates fail",
                "model_job_manifest job-01: approval_status must be blocked or "
                "non_executable while cinematic hard gates fail",
                "model_job_manifest job-02: approval_status must be blocked or "
                "non_executable while cinematic hard gates fail",
            ],
        )

    def test_failed_gates_allow_only_draft_or_blocked_artifacts(self):
        package = cinematic_package()
        package["quality_report"]["ready"] = False
        package["quality_report"]["checks"]["narrative_clarity"]["goal"] = (
            "fail"
        )
        package["shot_prompts"][0]["approval_status"] = "blocked"
        for job in package["model_job_manifest"]:
            job["approval_status"] = "non_executable"
        self.assertEqual(validate_package(package), [])

    def test_unready_package_rejects_final_prompt_when_gates_pass(self):
        package = cinematic_package()
        package["quality_report"]["ready"] = False
        for job in package["model_job_manifest"]:
            job["approval_status"] = "blocked"
        self.assertEqual(
            validate_package(package),
            [
                "shot_prompt shot-01: approval_status must be draft or blocked "
                "while quality_report.ready is false",
            ],
        )

    def test_unready_package_rejects_approved_jobs_when_gates_pass(self):
        package = cinematic_package()
        package["quality_report"]["ready"] = False
        package["shot_prompts"][0]["approval_status"] = "draft"
        self.assertEqual(
            validate_package(package),
            [
                "model_job_manifest job-01: approval_status must be blocked or "
                "non_executable while quality_report.ready is false",
                "model_job_manifest job-02: approval_status must be blocked or "
                "non_executable while quality_report.ready is false",
            ],
        )

    def test_ready_package_requires_final_prompts_and_approved_jobs(self):
        package = cinematic_package()
        package["shot_prompts"][0]["approval_status"] = "draft"
        package["model_job_manifest"][0]["approval_status"] = "blocked"
        self.assertEqual(
            validate_package(package),
            [
                "shot_prompt shot-01: approval_status must be final when "
                "quality_report.ready is true",
                "model_job_manifest job-01: approval_status must be approved "
                "when quality_report.ready is true",
            ],
        )


if __name__ == "__main__":
    unittest.main()
