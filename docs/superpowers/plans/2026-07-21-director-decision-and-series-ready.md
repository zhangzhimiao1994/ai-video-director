# Director Decision and Series-Ready Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `aibiandao` preserve the user's intended meaning, require real scene direction before shot selection, reject decorative or unmotivated shots, and expose safe single-episode hooks for a future serial-drama controller.

**Architecture:** Add one focused `director_validation.py` module that validates `project_brief.intent_contract`, scene directing plans, per-shot director decisions, prompt traceability, quality gates, and optional series handoffs without changing the ten top-level generation objects. Integrate its hard-gate result into the existing cinematic approval state machine, extend finished-film cinematic validation with intent/director audits, then update stage references and behavioral pressure prompts from the same contract.

**Tech Stack:** Python 3 standard library, `unittest`, JSON fixtures, Markdown Skill/reference contracts, existing `validate_package.py`, `cinematic_validation.py`, and edit-bundle reporting tools.

---

## File Structure

### New files

- `scripts/director_validation.py` — deterministic content-intent, scene-direction, shot-decision, prompt-trace, quality-gate, and series-hook validation.
- `tests/test_director_validation.py` — focused unit tests for the new validator without requiring the full package validator.
- `tests/test_director_mode_docs.py` — contract tests for Skill routing and all directing/series-ready reference documentation.
- `docs/evals/2026-07-21-director-intent-baseline.md` — raw pre-change behavior evidence for semantic drift and low-grade shot choices.
- `docs/evals/2026-07-21-director-intent-green.md` — post-change behavior evidence using the same prompts and rubric.

### Modified files

- `SKILL.md` — route intent locking before creative expansion, place scene direction before storyboarding, add director-quality hard gates and series-ready boundaries.
- `scripts/validate_package.py` — call the focused validator and merge its result into cinematic readiness/approval status.
- `scripts/cinematic_validation.py` — require finished-film `intent_fidelity` and `director_quality` audits and edit-unit intent tracing.
- `scripts/cinematic_report.py` — include both new audit objects in the derived report.
- `references/production-meeting.md` — define `project_brief.intent_contract` and the non-reversible meaning boundary.
- `references/story-directing.md` — define `intent_refs` and `scene_directing_plan` before shot design.
- `references/continuity-storyboard.md` — define per-shot deltas, blocking change, camera necessity, and shot relation.
- `references/cinematic-directing.md` — define the high-level director method matrix, advanced-shot gate, key-scene alternatives, and rejection patterns.
- `references/prompt-compiler.md` — inherit intent/director decisions and prohibit director-name shortcuts or visual replacement of meaning.
- `references/editing-finish.md` — preserve intent through edit units and actual-output review.
- `references/output-contract.md` — document nested fields, hard-gate statuses, and optional series input/output objects.
- `tests/test_validate_package.py` — update the cinematic fixture and add integration/status tests.
- `tests/test_cinematic_validation.py` — add edit-stage intent/director audit tests.
- `tests/test_build_edit_bundle.py` — assert the derived cinematic report carries the new audits.
- `tests/test_editing_finish_docs.py` — keep documented cinematic fields exactly aligned with code.
- `tests/fixtures/editing/cinematic_valid_plan.json` — add valid edit-unit intent refs and passed intent/director audits.
- `tests/fixtures/editing/cinematic_ppt_plan.json` — add trace fields while preserving its deliberate PPT failures.
- `test-prompts.json` — add semantic-drift, director-quality, and series-boundary behavior cases.
- `tests/test_test_prompts.py` — make those cases mandatory and semantically complete.
- `results.tsv` — append the final measured behavior/regression result without rewriting history.

## Task 1: Freeze the New Behavior Failures

**Files:**
- Modify: `test-prompts.json`
- Modify: `tests/test_test_prompts.py`
- Create: `docs/evals/2026-07-21-director-intent-baseline.md`

- [ ] **Step 1: Write failing prompt-catalog tests**

Add to `tests/test_test_prompts.py`:

```python
    def test_catalog_declares_director_intent_contract_cases(self):
        ids = {record["id"] for record in self.prompts}
        self.assertTrue(
            {
                "P13-intent-drift-guarding-cost",
                "P14-director-quality-dialogue",
                "P15-series-controller-boundary",
            }.issubset(ids)
        )

    def test_director_intent_cases_declare_required_semantics(self):
        required = {
            "P13-intent-drift-guarding-cost": (
                "intent_contract",
                "intent_refs",
                "主动承担代价",
                "不得用无关奇观替代",
            ),
            "P14-director-quality-dialogue": (
                "scene_directing_plan",
                "blocking_map",
                "camera_necessity",
                "机械正反打",
            ),
            "P15-series-controller-boundary": (
                "series_project",
                "series_context",
                "series_handoff",
                "不能声称已同步剧集总账",
            ),
        }
        for prompt_id, tokens in required.items():
            expected = self.prompts_by_id[prompt_id]["expected"]
            for token in tokens:
                with self.subTest(prompt_id=prompt_id, token=token):
                    self.assertIn(token, expected)
```

- [ ] **Step 2: Run the catalog tests and verify RED**

Run:

```powershell
python -m unittest tests.test_test_prompts.PromptCatalogContractTests.test_catalog_declares_director_intent_contract_cases tests.test_test_prompts.PromptCatalogContractTests.test_director_intent_cases_declare_required_semantics -v
```

Expected: FAIL because P13–P15 do not exist.

- [ ] **Step 3: Add the exact prompt records**

Append these records to `test-prompts.json`:

```json
{
  "id": "P13-intent-drift-guarding-cost",
  "prompt": "做一段45秒电影短片，核心只表达：守护不是获胜，而是主动替别人承担代价。不要擅自增加爱情、复仇、天选之子或无关世界观。请给剧本、分镜和提示词。",
  "expected": "先建立intent_contract，锁定‘主动承担代价’、禁止暗示和直接画面证据；beat、scene、active shot和prompt均携带可解析intent_refs；镜头必须展示主动选择、受力代价和被保护者反应；不得用巨龙、城市、粒子或无关奇观替代内容；内容不清时停止而不是自动补剧情。"
},
{
  "id": "P14-director-quality-dialogue",
  "prompt": "两个人在餐桌旁谈判：母亲已经知道儿子在撒谎，但儿子不知道她知道。不要拍成轮流说话的正反打，要有真正的导演处理，并说明每个镜头为什么存在。",
  "expected": "先写scene_directing_plan，明确母亲视点、观众信息差、双方目标、潜台词、可执行表演动作与blocking_map；再选择镜头；每个active shot至少有信息、情绪、权力、空间或因果delta，并写camera_necessity与shot_relation；拒绝机械正反打、随机手眼特写和无动机慢推；主分镜简洁可执行，导演附录解释关键选择。"
},
{
  "id": "P15-series-controller-boundary",
  "prompt": "把这个故事连续做成80集短剧，每集2分钟，人物、服装、伤势、伏笔和模型都不能漂移；现在先生成第1集，并自动把结果同步给后面79集。",
  "expected": "明确完整series_project、长文本拆集与跨集状态提交属于下一期短剧总控；当前单集只可读取project_brief.series_context并输出quality_report.series_handoff候选状态；没有外部series controller、API、授权与证据时不能声称已同步剧集总账；第1集仍须通过intent_contract、scene_directing_plan、人物模型锁和单集成片硬门。"
}
```

- [ ] **Step 4: Capture the pre-change behavior**

Run P13 and P14 against the current Skill in fresh behavior evaluations. Save the raw answers and a table with these binary checks to `docs/evals/2026-07-21-director-intent-baseline.md`:

```markdown
| Check | P13 | P14 |
|---|---:|---:|
| Locks the user's core message before expansion | 0/1 | N/A |
| Every active shot traces to the message | 0/1 | N/A |
| Rejects unrelated spectacle | 0/1 | N/A |
| Blocks scene before choosing camera | N/A | 0/1 |
| Uses playable actions and power changes | N/A | 0/1 |
| Rejects mechanical coverage | N/A | 0/1 |
```

Record verbatim failures without editing the old output into compliance.

- [ ] **Step 5: Re-run the catalog test and commit**

Run:

```powershell
python -m unittest tests.test_test_prompts -v
```

Expected: PASS.

Commit:

```powershell
git add test-prompts.json tests/test_test_prompts.py docs/evals/2026-07-21-director-intent-baseline.md
git commit -m "test: freeze intent drift and director quality failures"
```

## Task 2: Add the Intent and Director Validator

**Files:**
- Create: `scripts/director_validation.py`
- Create: `tests/test_director_validation.py`

- [ ] **Step 1: Write the focused failing tests**

Create `tests/test_director_validation.py` with a local `valid_director_package()` fixture containing:

```python
def valid_director_package():
    return {
        "project_brief": {
            "intent_contract": {
                "core_message": "Protection means choosing to bear the cost.",
                "audience_takeaway": "The choice, not victory, defines protection.",
                "emotional_destination": "awe becomes recognition of cost",
                "must_show_claims": [
                    {
                        "intent_id": "INT-001",
                        "claim": "The lead chooses to absorb the impact.",
                        "required_evidence": "choice, impact, and protected person's reaction",
                        "source_status": "user_locked",
                    }
                ],
                "must_preserve_events": ["EVENT-CHOICE", "EVENT-COST"],
                "must_not_imply": ["the hit is accidental"],
                "metaphor_policy": {
                    "mode": "literal_evidence_first",
                    "rule": "Metaphor supports but never replaces direct evidence.",
                },
                "source_fidelity": {
                    "mode": "concept_mode",
                    "locked_source_refs": [],
                    "allowed_adaptation": "blocking_coverage_and_local_pacing_only",
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
                        "audience_knowledge_before": "the threat is approaching",
                        "audience_knowledge_after": "the lead chose the cost",
                        "dramatic_turn": "the lead steps into the impact",
                        "character_objectives": ["lead protects", "companion escapes"],
                        "subtext_and_playable_actions": ["hide the shaking hand"],
                        "blocking_map": "lead crosses from rear right to block the central path",
                        "reveal_strategy": "show the choice before revealing the wound",
                        "camera_rule": "move only to reveal the protected companion",
                        "coverage_strategy": "choice, impact, reaction, consequence",
                        "visual_motif_progression": "open hand closes around the wound",
                        "editorial_consequence": "the hidden wound motivates the next scene",
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
        "shot_prompts": [
            {"shot_id": "SH001", "intent_refs": ["INT-001"]}
        ],
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
```

Add these tests:

```python
def test_valid_director_package_passes(self):
    errors, blocked = validate_director_package(valid_director_package(), required=True)
    self.assertEqual(errors, [])
    self.assertFalse(blocked)

def test_intent_claim_ids_must_be_unique(self):
    package = valid_director_package()
    package["project_brief"]["intent_contract"]["must_show_claims"].append(
        dict(package["project_brief"]["intent_contract"]["must_show_claims"][0])
    )
    errors, blocked = validate_director_package(package, required=True)
    self.assertIn("project_brief.intent_contract: duplicate intent_id INT-001", errors)
    self.assertTrue(blocked)

def test_every_trace_ref_must_resolve(self):
    package = valid_director_package()
    package["storyboard"][0]["intent_refs"] = ["INT-MISSING"]
    errors, blocked = validate_director_package(package, required=True)
    self.assertIn("shot SH001: unknown intent_ref INT-MISSING", errors)
    self.assertTrue(blocked)

def test_active_shot_requires_at_least_one_observable_delta(self):
    package = valid_director_package()
    for field in ("information_delta", "emotion_delta", "power_delta", "spatial_delta"):
        package["storyboard"][0][field] = ""
    errors, blocked = validate_director_package(package, required=True)
    self.assertIn("shot SH001: at least one director delta must be non-empty", errors)
    self.assertTrue(blocked)

def test_failed_director_gate_blocks_ready(self):
    package = valid_director_package()
    package["quality_report"]["checks"]["director_quality"]["status"] = "fail"
    errors, blocked = validate_director_package(package, required=True)
    self.assertIn("quality_report: ready cannot be true while director hard gates fail", errors)
    self.assertTrue(blocked)
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -m unittest tests.test_director_validation -v
```

Expected: ERROR because `director_validation` does not exist.

- [ ] **Step 3: Implement the minimal focused validator**

Create `scripts/director_validation.py` with these public contracts:

```python
INTENT_CONTRACT_FIELDS = (
    "core_message", "audience_takeaway", "emotional_destination",
    "must_show_claims", "must_preserve_events", "must_not_imply",
    "metaphor_policy", "source_fidelity",
)
SCENE_DIRECTING_FIELDS = (
    "scene_pov", "audience_knowledge_before", "audience_knowledge_after",
    "dramatic_turn", "character_objectives", "subtext_and_playable_actions",
    "blocking_map", "reveal_strategy", "camera_rule", "coverage_strategy",
    "visual_motif_progression", "editorial_consequence", "rejected_choices",
    "intent_refs",
)
SHOT_DIRECTING_FIELDS = (
    "intent_refs", "dramatic_question", "information_delta", "emotion_delta",
    "power_delta", "spatial_delta", "blocking_change", "camera_necessity",
    "performance_verb", "shot_relation", "director_rejection_reason",
)
DIRECTOR_DELTA_FIELDS = (
    "information_delta", "emotion_delta", "power_delta", "spatial_delta",
)

def validate_director_package(
    package: object, *, required: bool
) -> tuple[list[str], bool]:
    """Return deterministic errors and whether director hard gates block."""
```

Implementation rules:

1. Return `([], False)` when `required` is false and neither `intent_contract` nor director fields are declared.
2. Require an object `project_brief.intent_contract` when `required` is true.
3. Require all `INTENT_CONTRACT_FIELDS`; validate non-empty scalar strings, string lists, `must_show_claims` objects, unique non-empty `intent_id`, and non-empty `claim`, `required_evidence`, `source_status`.
4. Collect valid intent IDs once, then validate non-empty, deduplicated, resolving `intent_refs` on every beat object, scene, active shot, and shot prompt.
5. Require every scene's `scene_directing_plan` and every `SCENE_DIRECTING_FIELDS` member. List fields must be non-empty string lists; scalar fields must be non-empty strings; `rejected_choices` may be an empty string list.
6. Require all `SHOT_DIRECTING_FIELDS` on active cinematic shots. `director_rejection_reason` may be empty; the other scalar decision fields follow their documented types. Require at least one non-empty `DIRECTOR_DELTA_FIELDS` value.
7. Require shot prompt `intent_refs` to equal the linked shot's refs as sets and contain no duplicates.
8. Require `quality_report.checks.intent_fidelity` and `director_quality`, each with `status`, `unresolved_conflicts`, and `evidence_refs`. Status must be `pass` or `fail`; ready requires pass, zero conflicts, and non-empty evidence.
9. Deduplicate returned errors while preserving first occurrence order.

Use only local helpers such as:

```python
def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())

def _string_list(value: object, label: str, errors: list[str], *, nonempty: bool) -> list[str]:
    if not isinstance(value, list):
        errors.append(f"{label}: must be a list")
        return []
    if nonempty and not value:
        errors.append(f"{label}: must not be empty")
    valid = []
    seen = set()
    for index, item in enumerate(value, start=1):
        if not _nonempty_string(item):
            errors.append(f"{label} item {index}: must be a non-empty string")
        elif item in seen:
            errors.append(f"{label}: duplicate value {item}")
        else:
            seen.add(item)
            valid.append(item)
    return valid
```

- [ ] **Step 4: Run focused tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_director_validation -v
```

Expected: PASS.

- [ ] **Step 5: Commit the validator**

```powershell
git add scripts/director_validation.py tests/test_director_validation.py
git commit -m "feat: validate intent and director decisions"
```

## Task 3: Integrate Director Hard Gates into Production Packages

**Files:**
- Modify: `scripts/validate_package.py:1-15, 825-1528`
- Modify: `tests/test_validate_package.py:1-330, 1633-end`

- [ ] **Step 1: Write failing integration tests**

Update `cinematic_package()` so its project brief, beat, scene, shot, prompt, and quality report contain the valid fields from `valid_director_package()` in Task 2. Then add:

```python
def test_cinematic_package_requires_intent_contract(self):
    package = cinematic_package()
    del package["project_brief"]["intent_contract"]
    self.assertIn(
        "project_brief.intent_contract: required for director delivery",
        validate_package(package),
    )

def test_cinematic_scene_requires_directing_plan_before_storyboard(self):
    package = cinematic_package()
    del package["screenplay"]["scenes"][0]["scene_directing_plan"]
    self.assertIn(
        "scene scene-01: scene_directing_plan is required",
        validate_package(package),
    )

def test_director_gate_blocks_final_prompt_and_approved_job(self):
    package = cinematic_package()
    package["quality_report"]["ready"] = False
    package["quality_report"]["checks"]["intent_fidelity"]["status"] = "fail"
    errors = validate_package(package)
    self.assertIn(
        "shot_prompt shot-01: approval_status must be draft or blocked while cinematic hard gates fail",
        errors,
    )
    self.assertIn(
        "model_job_manifest job-01: approval_status must be blocked or non_executable while cinematic hard gates fail",
        errors,
    )

def test_legacy_non_cinematic_package_does_not_require_director_fields(self):
    self.assertEqual(validate_package(valid_package()), [])
```

- [ ] **Step 2: Run the integration tests and verify RED**

Run:

```powershell
python -m unittest tests.test_validate_package.ValidatePackageTests.test_cinematic_package_requires_intent_contract tests.test_validate_package.ValidatePackageTests.test_cinematic_scene_requires_directing_plan_before_storyboard tests.test_validate_package.ValidatePackageTests.test_director_gate_blocks_final_prompt_and_approved_job tests.test_validate_package.ValidatePackageTests.test_legacy_non_cinematic_package_does_not_require_director_fields -v
```

Expected: FAIL because `validate_package` does not call the new validator.

- [ ] **Step 3: Integrate without duplicating validation logic**

At the top of `scripts/validate_package.py` add:

```python
from director_validation import validate_director_package
```

Before quality status compilation, call:

```python
director_errors, director_gate_failed = validate_director_package(
    package,
    required=cinematic_mode is not None,
)
errors.extend(director_errors)
```

Change the cinematic quality block to combine gates:

```python
cinematic_gate_failed = _validate_cinematic_quality(quality_report, errors)
gate_failed = cinematic_gate_failed or director_gate_failed
_validate_cinematic_compilation_statuses(
    quality_report.get("ready") is True,
    gate_failed,
    cinematic_prompt_statuses,
    cinematic_job_statuses,
    errors,
)
```

Initialize `director_gate_failed = False` before quality processing so malformed/non-object quality reports remain deterministic.

- [ ] **Step 4: Run package regression tests**

Run:

```powershell
python -m unittest tests.test_validate_package -v
```

Expected: PASS, including the legacy package test.

- [ ] **Step 5: Commit package integration**

```powershell
git add scripts/validate_package.py tests/test_validate_package.py
git commit -m "feat: enforce director gates in cinematic packages"
```

## Task 4: Add Safe Series-Ready Hooks

**Files:**
- Modify: `scripts/director_validation.py`
- Modify: `tests/test_director_validation.py`
- Modify: `tests/test_validate_package.py`

- [ ] **Step 1: Write failing series-hook tests**

Add focused tests:

```python
def test_series_context_requires_exact_read_snapshot_fields(self):
    package = valid_director_package()
    package["project_brief"]["series_context"] = {
        "series_project_id": "SERIES-01",
        "episode_id": "EP-001",
    }
    errors, blocked = validate_director_package(package, required=True)
    self.assertIn(
        "project_brief.series_context: missing required field series_snapshot_id",
        errors,
    )
    self.assertTrue(blocked)

def test_series_handoff_cannot_claim_commit(self):
    package = valid_director_package()
    package["project_brief"]["series_context"] = valid_series_context()
    package["quality_report"]["series_handoff"] = valid_series_handoff()
    package["quality_report"]["series_handoff"]["handoff_status"] = "committed"
    errors, blocked = validate_director_package(package, required=True)
    self.assertIn(
        "quality_report.series_handoff.handoff_status: must be draft or unresolved",
        errors,
    )
    self.assertTrue(blocked)

def test_series_handoff_requires_series_context(self):
    package = valid_director_package()
    package["quality_report"]["series_handoff"] = valid_series_handoff()
    errors, blocked = validate_director_package(package, required=True)
    self.assertIn(
        "quality_report.series_handoff: requires project_brief.series_context",
        errors,
    )
    self.assertTrue(blocked)
```

The valid helper values are:

```python
def valid_series_context():
    return {
        "series_project_id": "SERIES-01",
        "episode_id": "EP-001",
        "series_snapshot_id": "SNAP-000",
        "asset_registry_version": "ASSET-V1",
        "episode_opening_state_ref": "SNAP-000.opening",
        "foreshadow_refs": ["FS-001"],
        "payoff_refs": ["PO-001"],
    }

def valid_series_handoff():
    return {
        "episode_closing_state_delta": {"C01.injury": "left-hand tremor"},
        "continuity_evidence_refs": ["EVID-EP001-C01"],
        "foreshadow_status_changes": ["FS-001:advanced"],
        "payoff_status_changes": [],
        "commit_eligibility": "external_series_controller_required",
        "handoff_status": "draft",
    }
```

- [ ] **Step 2: Run the series-hook tests and verify RED**

Run:

```powershell
python -m unittest tests.test_director_validation -v
```

Expected: FAIL because series objects are not validated.

- [ ] **Step 3: Implement optional nested validation**

Add constants:

```python
SERIES_CONTEXT_FIELDS = (
    "series_project_id", "episode_id", "series_snapshot_id",
    "asset_registry_version", "episode_opening_state_ref",
    "foreshadow_refs", "payoff_refs",
)
SERIES_HANDOFF_FIELDS = (
    "episode_closing_state_delta", "continuity_evidence_refs",
    "foreshadow_status_changes", "payoff_status_changes",
    "commit_eligibility", "handoff_status",
)
```

Validation rules:

- `series_context` and `series_handoff` are optional and never required for ordinary single-episode work.
- When present, each must be an object with all documented fields.
- IDs and snapshot/version refs must be non-empty strings.
- foreshadow/payoff/evidence/status-change fields must be deduplicated string lists; empty payoff change lists are valid.
- `episode_closing_state_delta` must be a non-empty object.
- `commit_eligibility` must equal `external_series_controller_required`.
- `handoff_status` must be `draft` or `unresolved`.
- A handoff without input context is a hard-gate failure.

- [ ] **Step 4: Run focused and package tests**

Run:

```powershell
python -m unittest tests.test_director_validation tests.test_validate_package -v
```

Expected: PASS.

- [ ] **Step 5: Commit the series-ready hooks**

```powershell
git add scripts/director_validation.py tests/test_director_validation.py tests/test_validate_package.py
git commit -m "feat: validate series-ready episode handoffs"
```

## Task 5: Carry Intent and Director Evidence into Finished-Film Validation

**Files:**
- Modify: `scripts/cinematic_validation.py`
- Modify: `scripts/cinematic_report.py`
- Modify: `tests/test_cinematic_validation.py`
- Modify: `tests/test_build_edit_bundle.py`
- Modify: `tests/fixtures/editing/cinematic_valid_plan.json`
- Modify: `tests/fixtures/editing/cinematic_ppt_plan.json`

- [ ] **Step 1: Write failing edit-stage tests**

In `tests/test_cinematic_validation.py`, add:

```python
def test_cinematic_edit_requires_intent_and_director_audits(self):
    for field in ("intent_fidelity", "director_quality"):
        with self.subTest(field=field):
            plan = load_plan("cinematic_valid_plan.json")
            del plan["cinematic_validation"][field]
            self.assert_deterministic_errors(
                plan,
                (f"cinematic_validation: missing field {field}",),
            )

def test_every_actual_edit_unit_requires_resolving_intent_refs(self):
    plan = load_plan("cinematic_valid_plan.json")
    del edit_units(plan)[0]["intent_refs"]
    self.assert_deterministic_errors(
        plan,
        (f"cinematic edit unit {edit_units(plan)[0]['edit_unit_id']}.intent_refs: must be an array",),
    )

def test_failed_intent_audit_blocks_cinematic_ready(self):
    plan = load_plan("cinematic_valid_plan.json")
    plan["cinematic_validation"]["intent_fidelity"]["status"] = "failed"
    self.assert_deterministic_errors(
        plan,
        ("cinematic_validation.intent_fidelity: status failed blocks cinematic readiness",),
    )

def test_director_quality_rejects_unresolved_pattern_flags(self):
    plan = load_plan("cinematic_valid_plan.json")
    plan["cinematic_validation"]["director_quality"]["rejected_pattern_flags"] = ["mechanical_shot_reverse_shot"]
    self.assert_deterministic_errors(
        plan,
        ("cinematic_validation.director_quality.rejected_pattern_flags: must be empty",),
    )
```

Add a report assertion in `tests/test_build_edit_bundle.py`:

```python
self.assertIn("intent_fidelity", report)
self.assertIn("director_quality", report)
```

- [ ] **Step 2: Run targeted tests and verify RED**

Run:

```powershell
python -m unittest tests.test_cinematic_validation tests.test_build_edit_bundle -v
```

Expected: FAIL because the audits and edit-unit refs are not required or reported.

- [ ] **Step 3: Extend the edit validation contract**

In `scripts/cinematic_validation.py`:

```python
CINEMATIC_FIELDS = (
    "declared_mode", "genre", "content_consistency", "intent_fidelity",
    "director_quality", "character_identity_integrity",
    "action_reaction_coverage", "kinetic_profile_audit",
    "shot_scale_and_composition_variety", "transition_fulfillment",
    "audio_presence_and_structure", "static_hold_audit",
    "source_motion_review", "ppt_risk_flags", "evidence_refs",
    "cinematic_ready",
)

AUDIT_FIELDS = (
    "content_consistency", "intent_fidelity", "director_quality",
    "character_identity_integrity", "action_reaction_coverage",
    "kinetic_profile_audit", "shot_scale_and_composition_variety",
    "transition_fulfillment", "audio_presence_and_structure",
    "static_hold_audit", "source_motion_review",
)
```

Add `_validate_intent_fidelity`, `_validate_director_quality`, and `_validate_edit_unit_intent_refs`:

```python
def _validate_intent_fidelity(audit, real_unit_ids, errors):
    intent_ids = _string_list(
        audit.get("intent_ids"),
        "cinematic_validation.intent_fidelity.intent_ids",
        errors,
        nonempty=True,
    ) or []
    mappings = _array(
        audit.get("edit_unit_mappings"),
        "cinematic_validation.intent_fidelity.edit_unit_mappings",
        errors,
    ) or []
    known_intents = set(intent_ids)
    mapped_intents = set()
    for index, mapping in enumerate(mappings, start=1):
        label = f"cinematic_validation.intent_fidelity.edit_unit_mappings item {index}"
        if not isinstance(mapping, dict):
            errors.append(f"{label}: must be an object")
            continue
        intent_id = mapping.get("intent_id")
        if not _nonempty_string(intent_id) or intent_id not in known_intents:
            errors.append(f"{label}.intent_id: must resolve to intent_ids")
        else:
            mapped_intents.add(intent_id)
        unit_ids = _string_list(
            mapping.get("edit_unit_ids"),
            f"{label}.edit_unit_ids",
            errors,
            nonempty=True,
        ) or []
        for unit_id in unit_ids:
            if unit_id not in real_unit_ids:
                errors.append(f"{label}.edit_unit_ids: unknown edit_unit_id {unit_id}")
        _string_list(
            mapping.get("evidence_refs"),
            f"{label}.evidence_refs",
            errors,
            nonempty=True,
        )
    missing = known_intents - mapped_intents
    for intent_id in sorted(missing):
        errors.append(
            "cinematic_validation.intent_fidelity.edit_unit_mappings: "
            f"missing intent_id {intent_id}"
        )

def _validate_director_quality(audit, real_unit_ids, errors):
    reviewed = _string_list(
        audit.get("reviewed_edit_unit_ids"),
        "cinematic_validation.director_quality.reviewed_edit_unit_ids",
        errors,
        nonempty=True,
    ) or []
    if set(reviewed) != set(real_unit_ids):
        errors.append(
            "cinematic_validation.director_quality.reviewed_edit_unit_ids: "
            "must cover every actual edit unit exactly"
        )
    _string_list(
        audit.get("evidence_refs"),
        "cinematic_validation.director_quality.evidence_refs",
        errors,
        nonempty=True,
    )
    flags = _string_list(
        audit.get("rejected_pattern_flags"),
        "cinematic_validation.director_quality.rejected_pattern_flags",
        errors,
        nonempty=False,
    )
    if flags:
        errors.append(
            "cinematic_validation.director_quality.rejected_pattern_flags: "
            "must be empty"
        )
```

Call both after `_validate_audit_status`. Add `_collect_actual_edit_units(plan)` using the same V1/active/first-release selection as `_collect_timeline_coverage`, returning `{edit_unit_id: edit_unit}`. Validate every returned unit with:

```python
def _validate_edit_unit_intent_refs(actual_units, valid_intent_ids, errors):
    for unit_id, unit in actual_units.items():
        refs = _string_list(
            unit.get("intent_refs"),
            f"cinematic edit unit {unit_id}.intent_refs",
            errors,
            nonempty=True,
        ) or []
        for intent_id in refs:
            if intent_id not in valid_intent_ids:
                errors.append(
                    f"cinematic edit unit {unit_id}: unknown intent_ref {intent_id}"
                )
```

Update `scripts/cinematic_report.py` to import or mirror the expanded audit order and include the two objects in both JSON and Markdown rendering.

Update both fixtures:

- add `intent_refs` to every first-release V1 edit unit;
- add passed `intent_fidelity` with `intent_ids`, complete `edit_unit_mappings`, and evidence refs;
- add passed `director_quality` with exact reviewed edit-unit coverage, empty `rejected_pattern_flags`, and evidence refs;
- preserve `cinematic_ppt_plan.json`'s existing deliberate motion, sound, transition, and PPT failures.

- [ ] **Step 4: Run edit-stage regression tests**

Run:

```powershell
python -m unittest tests.test_cinematic_validation tests.test_validate_edit_plan tests.test_build_edit_bundle -v
```

Expected: PASS.

- [ ] **Step 5: Commit finished-film intent validation**

```powershell
git add scripts/cinematic_validation.py scripts/cinematic_report.py tests/test_cinematic_validation.py tests/test_build_edit_bundle.py tests/fixtures/editing/cinematic_valid_plan.json tests/fixtures/editing/cinematic_ppt_plan.json
git commit -m "feat: verify intent and director quality in final edits"
```

## Task 6: Update the Upstream Skill and Director References

**Files:**
- Create: `tests/test_director_mode_docs.py`
- Modify: `SKILL.md`
- Modify: `references/production-meeting.md`
- Modify: `references/story-directing.md`
- Modify: `references/continuity-storyboard.md`
- Modify: `references/cinematic-directing.md`

- [ ] **Step 1: Write failing documentation contract tests**

Create `tests/test_director_mode_docs.py` with assertions that:

```python
EXPECTED = {
    "SKILL.md": (
        "intent_contract", "scene_directing_plan", "intent fidelity",
        "director quality", "series_context", "series_handoff",
    ),
    "references/production-meeting.md": (
        "project_brief.intent_contract", "must_show_claims",
        "must_not_imply", "literal_evidence_first",
    ),
    "references/story-directing.md": (
        "scene_directing_plan", "blocking_map", "dramatic_turn",
        "subtext_and_playable_actions", "intent_refs",
    ),
    "references/continuity-storyboard.md": (
        "information_delta", "emotion_delta", "power_delta",
        "spatial_delta", "camera_necessity", "shot_relation",
    ),
    "references/cinematic-directing.md": (
        "director decision engine", "pretty but useless",
        "mechanical shot/reverse-shot", "key scene alternatives",
    ),
}
```

Also assert the `SKILL.md` order:

```python
self.assertLess(skill.index("intent_contract"), skill.index("exactly three directions"))
self.assertLess(skill.index("scene_directing_plan"), skill.index("three-layer storyboard"))
```

Assert the method reference prohibits name shortcuts:

```python
self.assertIn("director names are not provider prompt shortcuts", cinematic)
self.assertIn("high-level transferable methods", cinematic)
```

- [ ] **Step 2: Run documentation tests and verify RED**

Run:

```powershell
python -m unittest tests.test_director_mode_docs -v
```

Expected: FAIL because the new contract is absent.

- [ ] **Step 3: Update routing and stage contracts**

Make these exact semantic changes:

1. `SKILL.md` Input Sufficiency Router: core message, motivation, relationship, choice, cost, victory/defeat, ending, and meaning-changing metaphor are not reversible assumptions.
2. `SKILL.md` Cinematic Router: build `intent_contract` before the three directions; all directions inherit it.
3. `SKILL.md` Required Workflow: `intent_contract → story → scene_directing_plan → storyboard → prompt`.
4. `SKILL.md` hard gates: add intent fidelity and director quality beside narrative, continuity, identity, motion, transition, and sound.
5. `SKILL.md` recovery matrix: semantic drift returns to intent contract; no dramatic turn returns to story; no playable action/blocking returns to scene plan; unmotivated camera returns to storyboard.
6. `production-meeting.md`: add the exact nested schema from the design and a source-status distinction among `user_locked`, `source_locked`, and `draft_recommendation`.
7. `story-directing.md`: require `intent_refs` on beats/scenes and all `scene_directing_plan` fields before storyboard handoff.
8. `continuity-storyboard.md`: require per-shot decision fields and at least one observable delta; preserve justified stillness.
9. `cinematic-directing.md`: add the method matrix, high-level-only usage boundary, advanced-shot pass/reject rules, and at most two inactive alternatives for key scenes.

Keep the main Skill concise: detailed field definitions belong in the stage references, while `SKILL.md` owns routing, hard gates, stops, and recovery.

- [ ] **Step 4: Run documentation and existing cinematic-mode tests**

Run:

```powershell
python -m unittest tests.test_director_mode_docs tests.test_cinematic_mode_docs -v
```

Expected: PASS.

- [ ] **Step 5: Commit upstream documentation**

```powershell
git add SKILL.md references/production-meeting.md references/story-directing.md references/continuity-storyboard.md references/cinematic-directing.md tests/test_director_mode_docs.py
git commit -m "docs: require intent-first scene direction"
```

## Task 7: Update Prompt, Edit, and Output Contracts

**Files:**
- Modify: `references/prompt-compiler.md`
- Modify: `references/editing-finish.md`
- Modify: `references/output-contract.md`
- Modify: `tests/test_director_mode_docs.py`
- Modify: `tests/test_editing_finish_docs.py`

- [ ] **Step 1: Add failing downstream contract assertions**

Extend `tests/test_director_mode_docs.py`:

```python
def test_downstream_contract_preserves_intent_without_name_shortcuts(self):
    prompt = self.read("references/prompt-compiler.md")
    editing = self.read("references/editing-finish.md")
    output = self.read("references/output-contract.md")
    for token in ("intent_refs", "camera_necessity", "performance_verb", "director names"):
        self.assertIn(token, prompt)
    for token in ("intent_fidelity", "director_quality", "edit-unit intent_refs"):
        self.assertIn(token, editing)
    for token in (
        "project_brief.series_context",
        "quality_report.series_handoff",
        "external_series_controller_required",
        "intent_fidelity",
        "director_quality",
    ):
        self.assertIn(token, output)
```

Change `tests/test_editing_finish_docs.py` so its exact `CINEMATIC_FIELDS` comparison expects the imported expanded tuple; do not duplicate a stale 14-field count.

- [ ] **Step 2: Run downstream docs tests and verify RED**

Run:

```powershell
python -m unittest tests.test_director_mode_docs tests.test_editing_finish_docs -v
```

Expected: FAIL until all three references align with code.

- [ ] **Step 3: Update downstream references**

Apply these exact contract changes:

- `prompt-compiler.md`: copy shot `intent_refs` unchanged; compile `performance_verb`, `blocking_change`, and `camera_necessity` into observable directions; reject any prompt that weakens the required evidence; state that director names are not prompt shortcuts.
- `editing-finish.md`: require edit-unit `intent_refs`; add `intent_fidelity` and `director_quality` actual-output audits; make a semantically wrong but technically rendered file non-cinematic.
- `output-contract.md`: document all new nested fields, the two quality checks, the two edit audits, and the exact series hook locations. State that `series_handoff` never means committed without an external controller.
- Update the complete JSON example so it remains parseable and reflects the new required cinematic fields.

- [ ] **Step 4: Run all document contract tests**

Run:

```powershell
python -m unittest tests.test_director_mode_docs tests.test_cinematic_mode_docs tests.test_editing_finish_docs -v
```

Expected: PASS.

- [ ] **Step 5: Commit downstream contracts**

```powershell
git add references/prompt-compiler.md references/editing-finish.md references/output-contract.md tests/test_director_mode_docs.py tests/test_editing_finish_docs.py
git commit -m "docs: preserve director intent through delivery"
```

## Task 8: Run Behavior Pressure Tests and Repair the Skill

**Files:**
- Create: `docs/evals/2026-07-21-director-intent-green.md`
- Modify if required by observed failures: `SKILL.md`, stage references, `test-prompts.json`

- [ ] **Step 1: Run P13–P15 with the upgraded Skill**

Use the repository's established `darwin-skill` evaluation procedure and the exact prompts in `test-prompts.json` in fresh evaluations. Capture complete raw answers before scoring. Do not repair the answers manually, and compare the candidate against the frozen baseline rather than scoring the candidate in isolation.

- [ ] **Step 2: Score against explicit behavior checks**

Use this rubric in `docs/evals/2026-07-21-director-intent-green.md`:

```markdown
| Check | P13 | P14 | P15 |
|---|---:|---:|---:|
| Intent is locked before creative expansion | 0/1 | N/A | 0/1 |
| Required evidence appears in every active shot | 0/1 | N/A | N/A |
| Unrelated spectacle is rejected | 0/1 | N/A | N/A |
| Scene blocking precedes camera choice | N/A | 0/1 | N/A |
| Camera and coverage have dramatic reasons | N/A | 0/1 | N/A |
| Mechanical inserts/coverage are rejected | N/A | 0/1 | N/A |
| Series boundary is stated truthfully | N/A | N/A | 0/1 |
| No false state sync or execution claim | N/A | N/A | 0/1 |
```

Required result: every applicable check is `1`; P13 and P14 must contain fewer decorative shots than baseline; P15 must not claim a committed series state.

- [ ] **Step 3: Perform targeted TDD repair if any check fails**

For each failed check:

1. Add the smallest missing behavioral assertion to `tests/test_director_mode_docs.py` or `tests/test_test_prompts.py`.
2. Run the targeted test and observe RED.
3. Change only the responsible router/reference section.
4. Run the same prompt fresh; do not reuse the failed output.
5. Record both failed and repaired raw evidence.

- [ ] **Step 4: Run all prompt/document tests**

Run:

```powershell
python -m unittest tests.test_test_prompts tests.test_director_mode_docs tests.test_cinematic_mode_docs tests.test_editing_finish_docs -v
```

Expected: PASS.

- [ ] **Step 5: Commit green behavior evidence**

```powershell
git add docs/evals/2026-07-21-director-intent-green.md SKILL.md references/production-meeting.md references/story-directing.md references/continuity-storyboard.md references/cinematic-directing.md references/prompt-compiler.md references/editing-finish.md references/output-contract.md test-prompts.json tests/test_director_mode_docs.py tests/test_test_prompts.py
git commit -m "test: verify intent fidelity and director judgment"
```

## Task 9: Full Regression, Score Record, and Release Readiness

**Files:**
- Modify: `results.tsv`
- Modify only if verification exposes a defect: files owned by the failing task

- [ ] **Step 1: Run the complete unit suite**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests PASS; record the exact count instead of assuming the previous 428.

- [ ] **Step 2: Run package and edit-plan smoke validation**

Run:

```powershell
python scripts/validate_edit_plan.py tests/fixtures/editing/cinematic_valid_plan.json --require-cinematic
```

Expected: `Edit plan is valid.`

Run:

```powershell
python scripts/validate_edit_plan.py tests/fixtures/editing/cinematic_ppt_plan.json --require-cinematic
```

Expected: non-zero exit with the pre-existing PPT/motion/transition/audio blockers; absence of intent/director fields must not be the reason because the fixture now declares them.

- [ ] **Step 3: Verify repository consistency**

Run:

```powershell
git diff --check
```

Expected: no output.

Run:

```powershell
git status --short
```

Expected: only the intended `results.tsv` update before the final commit.

- [ ] **Step 4: Append the measured result**

Append one tab-separated row to `results.tsv` with the actual timestamp, commit under test, old score, new score, status, dimension, and evidence. The note must include:

```text
P13-P15=all_applicable_checks_pass; unit_tests=<actual_pass_count>; intent_trace=pass; director_gate=pass; series_boundary=pass; old_versions_preserved=1
```

Do not modify or delete prior rows.

- [ ] **Step 5: Commit release evidence**

```powershell
git add results.tsv
git commit -m "test: record director decision regression result"
```

After this task, use `superpowers:verification-before-completion`, then the repository's branch-finishing workflow. Installation into the active Codex skill directory, merge, and SSH push remain separate release actions and must occur only after verification and any required authorization.
