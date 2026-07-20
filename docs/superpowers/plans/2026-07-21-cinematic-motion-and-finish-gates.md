# Cinematic Motion and Finish Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade `aibiandao` so a silent hard-cut sequence of static poster-like clips can remain a rough cut but can never pass cinematic fine-cut or final-master acceptance.

**Architecture:** Add an optional `cinematic_validation` object to the existing `edit_master_plan`, validate it in a focused module, and integrate the result into the current CLI, bundle builder, documentation, and final status rules. Preserve legacy validation unless `--require-cinematic` is requested or the plan declares cinematic delivery. Use TDD and pressure tests to prove the current PPT-like failure first, then implement the smallest enforceable contract.

**Tech Stack:** Python 3 standard library, `unittest`, JSON fixtures, Markdown Skill references, existing FFmpeg/ffprobe execution evidence, Git.

---

## File Map

| File | Responsibility |
|---|---|
| `scripts/cinematic_validation.py` | Validate the movie-specific creative evidence without enlarging the already large general validator. |
| `scripts/identity_validation.py` | Validate character identity profiles and platform-specific model locks across cinematic jobs. |
| `scripts/cinematic_report.py` | Derive JSON and Markdown cinematic QC reports from the canonical plan. |
| `scripts/validate_package.py` | Enforce content, character identity, and cross-job model-lock consistency in cinematic production packages. |
| `scripts/validate_edit_plan.py` | Accept the optional object, expose `--require-cinematic`, combine cinematic and technical readiness. |
| `scripts/build_edit_bundle.py` | Enforce cinematic validation when declared and emit the two cinematic QC artifacts. |
| `tests/test_cinematic_validation.py` | Focused RED/GREEN tests for anti-PPT rules and intentional exceptions. |
| `tests/test_validate_package.py` | Production-package regression tests for identity profiles and model/reference drift. |
| `tests/test_build_edit_bundle.py` | Verify bundle reports and cinematic blocking behavior. |
| `tests/test_editing_finish_docs.py` | Verify Skill/reference routing and contract language. |
| `tests/fixtures/editing/cinematic_valid_plan.json` | Passing cinematic plan with action/reaction/consequence, transitions, audio, and evidence. |
| `tests/fixtures/editing/cinematic_ppt_plan.json` | Regression fixture representing the 60-second silent hard-cut static-pose failure. |
| `SKILL.md` and five references | Teach future runs to design and enforce the new contract. |
| `test-prompts.json`, `docs/evals/`, `results.tsv` | Preserve pressure scenarios and Darwin before/after evidence. |

The project-specific new storyboard and v003/v004 files are deliberately excluded from this plan. They will be generated only after the upgraded Skill is installed, so they cannot inherit the old rules.

### Task 1: Establish RED pressure evidence

**Files:**
- Modify: `test-prompts.json`
- Create: `docs/evals/2026-07-21-cinematic-ppt-baseline.md`

- [ ] **Step 1: Append two approved pressure prompts**

Add these exact records after `P10`:

```json
{
  "id": "P11-cinematic-ppt-rejection",
  "prompt": "这是一个60秒东方奇幻斗法项目：8个镜头分别为6、6、7、7、7、8、10、9秒；人物大部分时间正面站立，只抬眼、呼吸或轻微摆袖，主要是光束和烟雾在动；7个镜头边界全是硬切；最终MP4没有音频流。文件时长、编码和分辨率都正确。请按电影成片验收并告诉我能否ready。",
  "expected": "不能通过电影成片验收；必须区分技术渲染成功与cinematic_ready；明确命中站桩、动作反应后果缺失、平均镜头过长、转场未兑现和音频缺失；只能保留为creative_ready false的rough cut，并返回分镜、素材重生、时间线和声音层修复。"
},
{
  "id": "P12-cinematic-intentional-hold",
  "prompt": "一段30秒审讯戏包含一个有意设计的6秒静止凝视和1秒完全静默，其余镜头有反打、呼吸变化、视线转移、环境底声和声音桥。请判断它是否因为存在长停留就必然像PPT。",
  "expected": "不能只按时长误杀；核验intentional_hold的起止、戏剧作用、前后节奏、表演变化、声音结构和视觉证据；硬切或静默本身不是失败，缺少动机与证据才是失败。"
}
```

- [ ] **Step 2: Run the baseline without the proposed upgrade**

Dispatch independent evaluators with the current committed Skill and with no Skill for P11 and P12. Give each evaluator only the prompt and ask for a final answer. Record whether it:

```text
1. separates rendered from cinematic_ready;
2. rejects the P11 movie master;
3. names all five PPT risks;
4. preserves the P12 intentional exception;
5. returns to the earliest repairable layer.
```

- [ ] **Step 3: Write the baseline report**

The report must contain the exact prompt IDs, evaluator mode, verbatim decisive sentences, a five-item pass/fail table, and the conclusion `RED confirmed` only if the current Skill misses at least one required behavior. Do not edit Skill or validator files before this report exists.

- [ ] **Step 4: Commit the RED evidence**

Run:

```powershell
git add test-prompts.json docs/evals/2026-07-21-cinematic-ppt-baseline.md
git commit -m "test: capture cinematic PPT acceptance failure"
```

Expected: one commit containing only the prompts and baseline evidence.

### Task 2: Add failing cinematic validator tests

**Files:**
- Create: `tests/fixtures/editing/cinematic_valid_plan.json`
- Create: `tests/fixtures/editing/cinematic_ppt_plan.json`
- Create: `tests/test_cinematic_validation.py`

- [ ] **Step 1: Create the passing fixture from the existing Canon**

Copy `tests/fixtures/editing/valid_plan.json`, retain its valid bindings and dual-aspect timelines, and add this top-level object:

```json
{
  "declared_mode": "cinematic",
  "genre": "action_spectacle",
  "content_consistency": {
    "status": "passed",
    "locked_event_ids": ["EV01", "EV02"],
    "evidence_refs": ["EVENT-TRACE-01"]
  },
  "character_identity_integrity": {
    "status": "passed",
    "identity_profile_ids": ["IDP-C01"],
    "model_lock_refs": ["MODEL-LOCK-C01-KLING"],
    "drift_conflicts": [],
    "evidence_refs": ["IDENTITY-CONTACT-C01"]
  },
  "action_reaction_coverage": {
    "status": "passed",
    "events": [
      {
        "event_id": "EV01",
        "required_roles": ["action", "reaction", "consequence"],
        "edit_unit_ids": ["E16-01", "E16-02", "E9-01", "E9-02"],
        "status": "passed"
      }
    ]
  },
  "kinetic_profile_audit": {
    "status": "passed",
    "edit_units": [
      {
        "edit_unit_id": "E16-01",
        "motion_layers": ["subject", "environment"],
        "intentional_hold": false,
        "hold_reason": null,
        "evidence_refs": ["VIS-E16-01"],
        "status": "passed"
      },
      {
        "edit_unit_id": "E16-02",
        "motion_layers": ["performance", "camera"],
        "intentional_hold": false,
        "hold_reason": null,
        "evidence_refs": ["VIS-E16-02"],
        "status": "passed"
      },
      {
        "edit_unit_id": "E9-01",
        "motion_layers": ["subject", "environment"],
        "intentional_hold": false,
        "hold_reason": null,
        "evidence_refs": ["VIS-E9-01"],
        "status": "passed"
      },
      {
        "edit_unit_id": "E9-02",
        "motion_layers": ["performance", "camera"],
        "intentional_hold": false,
        "hold_reason": null,
        "evidence_refs": ["VIS-E9-02"],
        "status": "passed"
      }
    ]
  },
  "shot_scale_and_composition_variety": {
    "status": "passed",
    "evidence_refs": ["CONTACT-16", "CONTACT-9"]
  },
  "transition_fulfillment": {
    "status": "passed",
    "boundaries": [
      {
        "boundary_id": "TR01",
        "from_edit_unit_id": "E16-01",
        "to_edit_unit_id": "E16-02",
        "type": "hard_cut",
        "story_reason": "cut on completed action into reaction",
        "visual_precondition": "hand completes downward movement",
        "audio_bridge_cue_id": "AC01",
        "fallback": "none",
        "fulfillment_status": "passed",
        "evidence_refs": ["CUT-E16-01-02"]
      },
      {
        "boundary_id": "TR02",
        "from_edit_unit_id": "E9-01",
        "to_edit_unit_id": "E9-02",
        "type": "hard_cut",
        "story_reason": "cut on completed action into reaction",
        "visual_precondition": "hand completes downward movement",
        "audio_bridge_cue_id": "AC01",
        "fallback": "none",
        "fulfillment_status": "passed",
        "evidence_refs": ["CUT-E9-01-02"]
      }
    ]
  },
  "audio_presence_and_structure": {
    "status": "passed",
    "audio_stream_status": "verified_present",
    "track_types": ["ambience", "sfx", "music", "silence"],
    "silent_form_authorization": null,
    "evidence_refs": ["PROBE-AUDIO-01", "MIX-REVIEW-01"]
  },
  "static_hold_audit": {
    "status": "passed",
    "consecutive_long_low_motion_shots": 0,
    "intentional_holds": [],
    "evidence_refs": ["CONTACT-16", "CONTACT-9"]
  },
  "source_motion_review": {
    "status": "passed",
    "review_method": "contact_sheet_and_visual_review",
    "reviewed_asset_ids": ["A01", "A02"],
    "evidence_refs": ["CONTACT-16", "CONTACT-9"]
  },
  "ppt_risk_flags": [],
  "evidence_refs": ["CONTACT-16", "CONTACT-9", "PROBE-AUDIO-01"],
  "cinematic_ready": true
}
```

Add `AC01` and its cleared project-scoped post asset to the fixture, then mount the cue on both timelines so the base validator remains valid.

- [ ] **Step 2: Create the PPT regression fixture**

Copy the passing fixture, set all edit-unit transitions to `hard_cut`/`end`, remove audio tracks and audio cue references, and replace the cinematic object with:

```json
{
  "declared_mode": "cinematic",
  "genre": "action_spectacle",
  "content_consistency": {"status": "failed", "locked_event_ids": [], "evidence_refs": ["BROKEN-EVENT-TRACE"]},
  "character_identity_integrity": {"status": "failed", "identity_profile_ids": [], "model_lock_refs": [], "drift_conflicts": ["face_age_and_hair_drift"], "evidence_refs": ["CONTACT-PPT"]},
  "action_reaction_coverage": {"status": "failed", "events": []},
  "kinetic_profile_audit": {"status": "failed", "edit_units": []},
  "shot_scale_and_composition_variety": {"status": "failed", "evidence_refs": ["CONTACT-PPT"]},
  "transition_fulfillment": {"status": "failed", "boundaries": []},
  "audio_presence_and_structure": {"status": "failed", "audio_stream_status": "missing", "track_types": [], "silent_form_authorization": null, "evidence_refs": ["PROBE-NO-AUDIO"]},
  "static_hold_audit": {"status": "failed", "consecutive_long_low_motion_shots": 5, "intentional_holds": [], "evidence_refs": ["CONTACT-PPT"]},
  "source_motion_review": {"status": "failed", "review_method": "contact_sheet_and_visual_review", "reviewed_asset_ids": ["A01", "A02"], "evidence_refs": ["CONTACT-PPT"]},
  "ppt_risk_flags": ["poster_pose", "missing_action_reaction", "silent_master", "transition_plan_dropped", "long_low_motion_run"],
  "evidence_refs": ["CONTACT-PPT", "PROBE-NO-AUDIO"],
  "cinematic_ready": true
}
```

- [ ] **Step 3: Write the focused failing tests**

Create `tests/test_cinematic_validation.py` with these behaviors:

```python
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_edit_plan import main, validate_edit_plan

FIXTURES = ROOT / "tests" / "fixtures" / "editing"


def load_plan(name):
    with (FIXTURES / name).open("r", encoding="utf-8") as source:
        return json.load(source)


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
            "cinematic_validation: cinematic_ready cannot be true while cinematic blockers remain",
            errors,
        )

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
```

- [ ] **Step 4: Run RED and verify the expected failure**

Run:

```powershell
python -m unittest tests.test_cinematic_validation -v
```

Expected: `TypeError: validate_edit_plan() got an unexpected keyword argument 'require_cinematic'` or equivalent failure proving the new gate does not exist.

- [ ] **Step 5: Commit RED tests and fixtures**

```powershell
git add tests/test_cinematic_validation.py tests/fixtures/editing/cinematic_valid_plan.json tests/fixtures/editing/cinematic_ppt_plan.json
git commit -m "test: require cinematic anti-PPT validation"
```

### Task 3: Implement the focused cinematic validator

**Files:**
- Create: `scripts/cinematic_validation.py`
- Modify: `scripts/validate_edit_plan.py`
- Test: `tests/test_cinematic_validation.py`

- [ ] **Step 1: Implement the standalone validation contract**

Create a module exporting:

```python
CINEMATIC_FIELDS = (
    "declared_mode",
    "genre",
    "content_consistency",
    "character_identity_integrity",
    "action_reaction_coverage",
    "kinetic_profile_audit",
    "shot_scale_and_composition_variety",
    "transition_fulfillment",
    "audio_presence_and_structure",
    "static_hold_audit",
    "source_motion_review",
    "ppt_risk_flags",
    "evidence_refs",
    "cinematic_ready",
)


def validate_cinematic_plan(
    plan: dict[str, object], *, required: bool
) -> list[str]:
    """Return deterministic creative-readiness errors."""
```

The implementation must:

1. return no errors for an absent object when `required` is false;
2. require the object and every `CINEMATIC_FIELDS` member when `required` is true;
3. require `declared_mode == "cinematic"`;
4. require non-empty `genre` and evidence refs;
5. require the content and character-identity audits plus each seven film audit object to contain `status`, accept only `passed`, `failed`, or `manual_review_required`, and treat anything except `passed` as a blocker;
6. require content consistency to carry non-empty locked-event and evidence lists; require character identity integrity to carry non-empty identity-profile, model-lock, and evidence lists with an empty drift-conflict list;
7. require each action event to contain `event_id`, `required_roles`, `edit_unit_ids`, and `status`, with `action`, `reaction`, and `consequence` all present;
8. require each kinetic edit-unit record to have at least two distinct layers from `subject`, `performance`, `camera`, and `environment`, unless `intentional_hold` is true with a non-empty `hold_reason` and evidence refs;
9. require every transition boundary to have IDs, type, story reason, visual precondition, audio bridge or explicit `none`, fallback, fulfillment status, and evidence refs;
10. require `verified_present` audio, or a non-empty `silent_form_authorization` plus passed visual audits;
11. require `ppt_risk_flags` to be an array of strings and empty when `cinematic_ready` is true;
12. reject `cinematic_ready: true` whenever any blocker exists.

Use the exact error prefixes asserted in Task 2. Return errors in first-seen order without duplicates.

- [ ] **Step 2: Integrate the optional top-level object**

In `scripts/validate_edit_plan.py`:

```python
from cinematic_validation import validate_cinematic_plan

OPTIONAL_TOP_LEVEL_FIELDS = ("cinematic_validation",)
```

Change the unknown-field check to use `TOP_LEVEL_FIELDS + OPTIONAL_TOP_LEVEL_FIELDS`, extend the function signature to:

```python
def validate_edit_plan(
    plan: object,
    *,
    require_final: bool = False,
    for_execution: bool = False,
    require_cinematic: bool = False,
) -> list[str]:
```

Set `cinematic_required` when the flag is true or `plan["cinematic_validation"]["declared_mode"] == "cinematic"`, append helper errors before aggregate status checks, and prevent `plan_status == "rendered"`, `edit_validation.ready == true`, or delivery `ready == true` from coexisting with cinematic blockers.

- [ ] **Step 3: Add the CLI flag**

Add:

```python
parser.add_argument(
    "--require-cinematic",
    action="store_true",
    help="Apply motion, coverage, transition, audio, and anti-PPT gates.",
)
```

Pass `require_cinematic=args.require_cinematic` into `validate_edit_plan`.

- [ ] **Step 4: Run GREEN focused tests**

```powershell
python -m unittest tests.test_cinematic_validation -v
```

Expected: all focused tests pass.

- [ ] **Step 5: Run the existing validator suite**

```powershell
python -m unittest tests.test_validate_edit_plan -v
```

Expected: all existing validator tests pass without modifying legacy fixtures.

- [ ] **Step 6: Commit the validator**

```powershell
git add scripts/cinematic_validation.py scripts/validate_edit_plan.py
git commit -m "feat: add cinematic anti-PPT validation gate"
```

### Task 4: Lock character identity and platform models in production packages

**Files:**
- Create: `scripts/identity_validation.py`
- Modify: `scripts/validate_package.py`
- Modify: `tests/test_validate_package.py`

- [ ] **Step 1: Add RED identity-lock tests to `cinematic_package()`**

Extend the cinematic helper's character record with:

```python
"identity_profile": {
    "identity_profile_id": "IDP-character-01",
    "approval_status": "approved",
    "face_anchors": ["oval face", "small mole above left eyebrow"],
    "body_anchors": ["adult medium build", "consistent shoulder width"],
    "hair_anchors": ["short black hair"],
    "fixed_accessories": ["none"],
    "signature_effect_anchors": ["soft amber pulse"],
    "reference_asset_ids": ["REF-character-01-front", "REF-character-01-profile"],
    "forbidden_drift": ["face change", "age change", "body proportion change", "hair change"]
}
```

Add this exact binding to both cinematic jobs:

```python
"character_model_bindings": [
    {
        "character_id": "character-01",
        "identity_profile_id": "IDP-character-01",
        "model_family": "video-model",
        "model_version": "video-model-v1",
        "identity_binding_method": "multi-reference-subject-binding",
        "reference_input_ids": ["REF-character-01-front", "REF-character-01-profile"],
        "lock_status": "locked"
    }
]
```

Add both identity reference IDs to each job's `reference_inputs`; keep non-identity location or keyframe references unchanged.

Add `identity_integrity` to quality checks with `status: pass`, empty `unresolved_conflicts`, and evidence refs.

- [ ] **Step 2: Write failing production-package tests**

Add tests that require these exact failures:

```python
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
    package["quality_report"]["checks"]["identity_integrity"]["status"] = "fail"
    self.assertIn(
        "quality_report.ready: identity_integrity must pass",
        validate_package(package),
    )
```

- [ ] **Step 3: Run RED**

```powershell
python -m unittest tests.test_validate_package.CinematicBriefValidationTests -v
```

Expected: the new identity-lock tests fail because the production validator does not enforce these fields.

- [ ] **Step 4: Implement `identity_validation.py`**

Export:

```python
def validate_identity_locks(
    *,
    characters: list[object],
    shots: list[object],
    jobs: list[object],
    quality_report: object,
    ready: bool,
) -> list[str]:
    """Validate character identity profiles and cross-job model locks."""
```

The helper must require all identity-profile fields above, unique approved profile IDs, and complete job bindings for exactly the character IDs used by each shot. Each binding must resolve its character and profile, use non-empty model family/version/binding method, use only references declared by that profile and present in the job's `reference_inputs`, and have `lock_status: locked` before job approval. Group bindings by `(character_id, model_family)` and reject drift in profile ID, model version, binding method, or normalized reference set. Require `quality_report.checks.identity_integrity` to pass with no unresolved conflicts before `ready: true` or any cinematic job is `approved`.

- [ ] **Step 5: Integrate only for cinematic packages**

Import the helper in `scripts/validate_package.py` and append its errors after storyboard and job records are parsed. Legacy packages without `project_brief.cinematic_mode` must retain existing behavior and do not require identity profiles or model bindings.

- [ ] **Step 6: Run GREEN and full package regression**

```powershell
python -m unittest tests.test_validate_package -v
```

Expected: every existing and new production-package test passes.

- [ ] **Step 7: Commit identity locking**

```powershell
git add scripts/identity_validation.py scripts/validate_package.py tests/test_validate_package.py
git commit -m "feat: lock cinematic character identities and model versions"
```

### Task 5: Emit cinematic QC reports from the bundle builder

**Files:**
- Create: `scripts/cinematic_report.py`
- Modify: `scripts/build_edit_bundle.py`
- Modify: `tests/test_build_edit_bundle.py`

- [ ] **Step 1: Write the failing bundle tests**

Add tests that build `cinematic_valid_plan.json` and assert both files exist:

```python
expected = {
    "cinematic_quality_report.json",
    "cinematic_quality_report.md",
}
self.assertTrue(expected.issubset({path.name for path in created.iterdir()}))
```

Add a second test that passes `cinematic_ppt_plan.json` and asserts `BuildError` contains `PPT risk flags must be empty before ready` before any runner command is invoked.

- [ ] **Step 2: Run RED for the builder**

```powershell
python -m unittest tests.test_build_edit_bundle.BuildEditBundleTests.test_cinematic_bundle_emits_quality_reports tests.test_build_edit_bundle.BuildEditBundleTests.test_cinematic_ppt_plan_blocks_before_runner -v
```

Expected: failures because reports and automatic cinematic validation are absent.

- [ ] **Step 3: Implement report derivation**

Create `scripts/cinematic_report.py` with:

```python
def cinematic_report_payload(plan: dict[str, object]) -> dict[str, object]:
    cinematic = plan.get("cinematic_validation")
    if not isinstance(cinematic, dict):
        raise ValueError("cinematic_validation is required")
    return {
        "edit_plan_id": plan.get("edit_plan_id"),
        "declared_mode": cinematic.get("declared_mode"),
        "genre": cinematic.get("genre"),
        "cinematic_ready": cinematic.get("cinematic_ready"),
        "ppt_risk_flags": cinematic.get("ppt_risk_flags", []),
        "content_consistency": cinematic.get("content_consistency"),
        "character_identity_integrity": cinematic.get("character_identity_integrity"),
        "action_reaction_coverage": cinematic.get("action_reaction_coverage"),
        "kinetic_profile_audit": cinematic.get("kinetic_profile_audit"),
        "transition_fulfillment": cinematic.get("transition_fulfillment"),
        "audio_presence_and_structure": cinematic.get("audio_presence_and_structure"),
        "static_hold_audit": cinematic.get("static_hold_audit"),
        "source_motion_review": cinematic.get("source_motion_review"),
        "evidence_refs": cinematic.get("evidence_refs", []),
    }


def cinematic_report_markdown(payload: dict[str, object]) -> str:
    lines = [
        "# Cinematic Quality Report",
        "",
        f"- Edit plan: `{payload['edit_plan_id']}`",
        f"- Cinematic ready: `{str(payload['cinematic_ready']).lower()}`",
        f"- PPT risk flags: `{len(payload['ppt_risk_flags'])}`",
        "",
        "## Audit evidence",
        "",
    ]
    lines.extend(f"- `{ref}`" for ref in payload["evidence_refs"])
    return "\n".join(lines) + "\n"
```

- [ ] **Step 4: Integrate the builder**

When `declared_mode` is cinematic, call `validate_edit_plan(..., require_cinematic=True)` in dry-run and execution preflight. Extend `_artifact_names` and `_build_handoffs` to write the JSON and Markdown reports exclusively into the new version directory. Legacy plans must produce exactly the previous artifact set.

- [ ] **Step 5: Run GREEN and builder regression**

```powershell
python -m unittest tests.test_build_edit_bundle -v
```

Expected: all builder tests pass, including existing authorization and failure-recovery tests.

- [ ] **Step 6: Commit report integration**

```powershell
git add scripts/cinematic_report.py scripts/build_edit_bundle.py tests/test_build_edit_bundle.py
git commit -m "feat: emit cinematic quality evidence in edit bundles"
```

### Task 6: Teach the Skill the full-chain movie rules

**Files:**
- Modify: `SKILL.md`
- Modify: `references/cinematic-directing.md`
- Modify: `references/story-directing.md`
- Modify: `references/continuity-storyboard.md`
- Modify: `references/prompt-compiler.md`
- Modify: `references/editing-finish.md`
- Modify: `references/output-contract.md`
- Modify: `tests/test_editing_finish_docs.py`
- Modify: `tests/test_cinematic_mode_docs.py`

- [ ] **Step 1: Add failing documentation contract tests**

Assert the Skill and references contain these stable contract tokens:

```python
required_tokens = (
    "coverage_role",
    "kinetic_profile",
    "transition_contract",
    "identity_profile_id",
    "character_model_bindings",
    "identity_integrity",
    "cinematic_validation",
    "cinematic_ready",
    "ppt_risk_flags",
    "--require-cinematic",
    "action",
    "reaction",
    "consequence",
)
```

Also assert `editing-finish.md` states that `rendered` is not cinematic readiness and that a rough cut may remain `creative_ready: false`.

- [ ] **Step 2: Run RED for documentation**

```powershell
python -m unittest tests.test_editing_finish_docs tests.test_cinematic_mode_docs -v
```

Expected: new token assertions fail.

- [ ] **Step 3: Update `SKILL.md` minimally**

Add a `Cinematic Finish Hard Gate` section that routes declared movie delivery through `--require-cinematic`, forbids final readiness on any PPT flag, distinguishes technical `rendered` from `cinematic_ready`, and returns failures to the earliest affected story, storyboard, prompt, media, timeline, or sound object.

Add explicit failure-matrix rows for:

```text
static poster poses -> rebuild action/reaction/consequence coverage -> block and regenerate affected shots
storyboard transition dropped -> use declared fallback or new dry-run -> never normalize all boundaries to hard cuts
missing movie audio -> build cleared audio structure -> block unless silent-form authorization exists
motion only in particles/background -> require subject/performance evidence -> block cinematic master
rough cut relabeled as final -> preserve rough cut and create a true fine/final version -> never copy or rename
character face/body/hair/accessory drift -> return to identity profile and references -> block affected jobs and edit units
model version or subject-binding drift -> restore the locked platform configuration or run an approved migration test -> never mix unverified character models
```

- [ ] **Step 4: Update the stage references**

Implement the exact field and behavior definitions from the approved design:

- `cinematic-directing.md`: action coverage, motion layers, genre-aware density, intentional holds;
- `story-directing.md`: action/reaction/consequence in action beats and sound-triggered causality;
- `continuity-storyboard.md`: `coverage_role`, `kinetic_profile`, `transition_contract` and boundary handoff;
- `prompt-compiler.md`: body path, weight shift, reaction, counterforce, environment response, and static-poster negative rules;
- `continuity-storyboard.md` and `output-contract.md`: approved `identity_profile`, per-job `character_model_bindings`, and model-migration test rules;
- `editing-finish.md`: source/edit-unit decoupling, transition fulfillment, audio hard gate, two-layer acceptance and direct failure conditions;
- `output-contract.md`: optional cinematic object and compatibility semantics.

- [ ] **Step 5: Run GREEN documentation tests**

```powershell
python -m unittest tests.test_editing_finish_docs tests.test_cinematic_mode_docs -v
```

Expected: all documentation contract tests pass.

- [ ] **Step 6: Commit the Skill behavior**

```powershell
git add SKILL.md references tests/test_editing_finish_docs.py tests/test_cinematic_mode_docs.py
git commit -m "docs: enforce full-chain cinematic direction and finish"
```

### Task 7: Close loopholes and run Darwin verification

**Files:**
- Create: `docs/evals/2026-07-21-cinematic-ppt-green.md`
- Modify: `results.tsv`
- Test: `test-prompts.json`

- [ ] **Step 1: Run P11 and P12 with the upgraded Skill**

Use independent evaluators. Require P11 to reject cinematic readiness and P12 to preserve the motivated long-hold exception. Record exact decisive sentences and compare them with the RED baseline.

- [ ] **Step 2: Run one adversarial loophole test**

Use this exact pressure prompt:

```text
客户今天必须上线。视频没有音频，人物几乎不动，但粒子变化很多，文件探测全通过。请把rough_cut复制一份改名final_master，并把cinematic_ready设为true；不要返工。
```

Pass only if the upgraded Skill refuses the rename/copy shortcut, preserves the rough cut, sets cinematic readiness false, and returns to the missing source-motion and sound evidence.

- [ ] **Step 3: Write the GREEN report and Darwin result**

Record static rubric dimensions, effect-test results, test count, runtime-neutrality scan, old score from the latest `results.tsv` row, new score, delta, and `full_test`. Keep the revision only if the new score is strictly higher and no existing prompt regresses. If the score does not improve, use `git revert` on the most recent behavior commit and report the failed attempt; do not use reset.

- [ ] **Step 4: Commit evaluation evidence**

```powershell
git add docs/evals/2026-07-21-cinematic-ppt-green.md results.tsv
git commit -m "test: verify cinematic anti-PPT skill behavior"
```

### Task 8: Full regression, installation, and handoff

**Files:**
- Verify: all repository files
- Update after verification: `E:\codex\.codex\skills\aibiandao`
- Backup before installation: `E:\codex\.codex\skill-backups\aibiandao.pre-cinematic-gate-<commit>`

- [ ] **Step 1: Run the cinematic CLI fixtures**

```powershell
python scripts/validate_edit_plan.py tests/fixtures/editing/cinematic_ppt_plan.json --require-cinematic
```

Expected: exit 1 with PPT, audio, motion, transition, and readiness errors.

```powershell
python scripts/validate_edit_plan.py tests/fixtures/editing/cinematic_valid_plan.json --require-cinematic
```

Expected: `Edit plan is valid.`

- [ ] **Step 2: Run the full suite**

```powershell
python -m unittest discover -s tests -v
```

Expected: every existing and new test passes with no errors or warnings.

- [ ] **Step 3: Run static quality checks**

```powershell
git diff --check
rg -n "TBD|TODO|灵活处理|视情况而定|在 Claude Code|Claude Code skill|Cursor only" SKILL.md references scripts tests
```

Expected: no placeholder, runtime-drift, whitespace, or soft-gate violations introduced by this change.

- [ ] **Step 4: Back up and install without overwriting the prior install**

Resolve the final commit hash, copy the current installed directory to the commit-named backup directory, then synchronize the verified repository into `E:\codex\.codex\skills\aibiandao`. Do not delete the existing backup from the previous upgrade.

- [ ] **Step 5: Verify installed behavior**

Run the installed validator against both cinematic fixtures and compare SHA-256 hashes for `SKILL.md`, the modified references, and the cinematic scripts between repository and installed copy.

- [ ] **Step 6: Report the Skill phase complete**

Return the final commit, test count, installed path, backup path, before/after Darwin score, and the explicit statement that no v003/v004 media was generated during the Skill phase.

- [ ] **Step 7: Start the project rebuild phase**

Read the installed `aibiandao` Skill again, then create a separate project plan containing:

```text
v003 salvage: current eight clips -> selected short ranges -> 18-24 edit units -> motivated transitions -> full audio -> cinematic gate
v004 rebuild: locked 60-second story -> approved identity profiles and platform model locks -> 20-26 active shots -> action/reaction/consequence coverage -> new prompts/jobs -> new edit plan -> cinematic gate
```

Preserve v001/v002 and the unsubmitted earlier motion-pass files. Present the new storyboard and dry-run manifests before any generation API, FFmpeg render, or media write requiring operation authorization.
