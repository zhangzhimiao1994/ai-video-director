# Cinematic Director Mode Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a platform-neutral 30–60 second cinematic directing mode that accepts a story idea or screenplay, defaults to narrative-first rhythm A, produces 16:9 and 9:16 plans, and blocks final readiness when story clarity or continuity fails.

**Architecture:** Keep the existing ten-object package as the canonical contract and opt into the new behavior with `project_brief.cinematic_mode`. A focused cinematic reference defines routing and directing behavior; existing story, continuity, prompt, adapter, and output references own their stage-specific extensions. The validator applies cinematic-only schema, shot-graph, dual-aspect, and quality-gate checks without changing legacy package requirements.

**Tech Stack:** Markdown Skill references, Python 3 standard library, `unittest`, JSON fixtures, Git.

---

## Scope and file map

The approved specification is `docs/superpowers/specs/2026-07-18-cinematic-director-mode-design.md`.

This is one coherent subsystem: the cinematic mode is routed by the Skill, represented in the existing package, compiled by existing stages, and enforced by one validator. It does not require a separate runtime service or API client.

### Files to create

- `references/cinematic-directing.md` — single source of truth for cinematic-mode activation, input modes, A/B/C rhythms, hard gates, dual-aspect behavior, and logical deliverables.
- `tests/test_cinematic_mode_docs.py` — static contract tests ensuring the Skill and references retain the approved behavior.
- `tests/test_test_prompts.py` — validates the prompt catalog and the new cinematic regression cases.

### Files to modify

- `SKILL.md` — route cinematic requests to the new reference while preserving the three existing checkpoints.
- `references/story-directing.md` — define concept/screenplay routing and the adaptive six-beat map.
- `references/continuity-storyboard.md` — define cinematic shot fields, state dependencies, and independent 9:16 recomposition.
- `references/prompt-compiler.md` — define three-layer cinematic compilation and the anti-overload rule.
- `references/model-adapters.md` — formalize capability records and add verified HappyHorse guidance while keeping unverified Kling/Seedance fields manual.
- `references/output-contract.md` — document the optional cinematic JSON extension and logical artifact layout.
- `scripts/validate_package.py` — add conditional cinematic-mode validation without changing legacy validation.
- `tests/test_validate_package.py` — add cinematic fixtures and validator regressions.
- `test-prompts.json` — add concept, screenplay, reserved-novel, and hard-gate behavior probes.

### Files intentionally unchanged

- `references/production-meeting.md` — existing brief questions already cover duration, aspect, platform, sources, rights, and resources.
- `agents/openai.yaml` — the Skill identity and tool declaration do not change.
- `results.tsv` — update only after a separate scored Darwin evaluation, not during implementation.

---

### Task 1: Route cinematic requests through a focused reference

**Files:**
- Create: `references/cinematic-directing.md`
- Create: `tests/test_cinematic_mode_docs.py`
- Modify: `SKILL.md:12-44`
- Modify: `SKILL.md:86-97`

- [ ] **Step 1: Write the failing routing and reference tests**

Create `tests/test_cinematic_mode_docs.py` with this content:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CinematicModeDocsTests(unittest.TestCase):
    def read(self, relative_path):
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_routes_cinematic_mode(self):
        skill = self.read("SKILL.md")
        self.assertIn("## Cinematic Mode Router", skill)
        self.assertIn("references/cinematic-directing.md", skill)
        self.assertIn("rhythm preset A", skill)

    def test_cinematic_reference_contains_approved_contract(self):
        reference = self.read("references/cinematic-directing.md")
        required_tokens = (
            "concept_mode",
            "screenplay_mode",
            "novel_mode_reserved",
            "narrative_clarity",
            "continuity_integrity",
            "16:9",
            "9:16",
            "A narrative-first cinematic",
            "B spectacle-heavy",
            "C performance-first",
            "key_shot_review",
            "local_repair",
        )
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, reference)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests and verify the intended failure**

Run:

```powershell
python -m unittest discover -s tests -p "test_cinematic_mode_docs.py" -v
```

Expected: 2 tests run and fail because `SKILL.md` has no cinematic router and `references/cinematic-directing.md` does not exist.

- [ ] **Step 3: Add the cinematic router to `SKILL.md`**

Insert after `## Operating Mode` and its existing paragraphs:

```markdown
## Cinematic Mode Router

Activate cinematic mode when the user asks for a 30–60 second cinematic clip, trailer, film-like adaptation, or a multi-platform package centered on story clarity and character continuity. Read `references/cinematic-directing.md` before entering the normal stage references.

Accept `concept_mode` for an idea or premise and `screenplay_mode` for a complete or partial screenplay. `novel_mode_reserved` is not a shipped input mode: for a long novel, explain the current boundary and request one self-contained excerpt or screenplay segment.

Use rhythm preset A by default. B and C require an explicit user choice. Cinematic mode produces a 16:9 master plan and a separately recomposed 9:16 plan. It does not bypass the existing Brief, Direction, or Screenplay + Storyboard checkpoints, and it never authorizes an API call.
```

In `## Required Workflow`, add this sentence immediately before the numbered list:

```markdown
When cinematic mode is active, first read `references/cinematic-directing.md`; then use the same staged workflow below and materialize the cinematic extensions in the existing ten objects.
```

Add this row to the `## Reference Router` table immediately before Package delivery:

```markdown
| Cinematic mode overlay | `references/cinematic-directing.md` plus the active stage reference | Optional cinematic fields inside the existing ten objects | Story clarity or continuity hard gate does not pass |
```

- [ ] **Step 4: Create the focused cinematic reference**

Create `references/cinematic-directing.md` with the following complete structure and rules:

```markdown
# AI Video Director：通用电影化模式

本参考是现有十对象制作包上的可选导演层。它不创建第十一个顶层对象，不调用 API，也不改变三个批准门。

## Activation

适用于 30–60 秒电影级片段或预告。启用后，在 `project_brief.cinematic_mode` 中显式记录输入模式、节奏预设、双画幅和视觉预设。

## Input modes

- `concept_mode`：用户提供一句故事、主题、人物或冲突；先补全可审计因果，再进入三个创意方向。
- `screenplay_mode`：用户提供完整或部分剧本；保留核心事实、人物动机和因果，压缩为目标时长。
- `novel_mode_reserved`：仅为未来扩展保留。首版遇到长篇小说时说明边界，请用户选择一个自包含片段或提供剧本，不宣称已经完成章节拆解。

## Hard gates

- `narrative_clarity`：必须明确主角、目标、阻碍、因果和结尾变化。
- `continuity_integrity`：不得存在未解决的角色 ID、服装、道具、人物状态、空间方向或镜头依赖冲突。

任一硬门失败时，`quality_report.ready` 必须为 `false`。镜头震撼度是建议项，不得覆盖硬门。

## Rhythm presets

- `A narrative-first cinematic`：默认。远景建立尺度，近景、双人、反应和插入镜头讲清关系，只保留 1–2 个英雄镜头。
- `B spectacle-heavy`：增加大全景、动态构图、复杂特效和运镜；参考资产不足时降级为 A。
- `C performance-first`：增加近景、特写、双人覆盖、停顿和微表情，减少复杂场景切换。

切换 A/B/C 不得改变剧情事实、角色 ID、事件顺序或结局。

## Shot design

30–60 秒通常使用 7–12 个 active 镜头，但以因果和可生成性为准。每镜只保留一个主要动作、一个主要运镜、一个情绪转折和一个视觉关注点。镜头必须声明叙事功能、边界状态、状态依赖和平台能力需求。

`style_preset` 是可切换数据，不是暗黑西幻硬编码。它可以表达东方玄幻、科幻、末世、写实或用户定义视觉规则，但不能改变已锁定剧情事实。

## Dual aspect

- 16:9 是电影母版，使用横向调度、前中后景和环境尺度。
- 9:16 是独立重构，重新安排人物、视线、字幕安全区和纵向景深。
- 无法安全重构时使用 `independent_generation`，不得伪装成机械裁切。

两种画幅共享同一故事、Canon 事实和状态，只改变构图、调度与平台编译。

## Prompt order

电影化提示词保持三层语义：`global_lock_block`、`shot_direction_block`、`platform_compile_block`。平台层只做格式和已核实能力映射，不得新增剧情事实。

## key_shot_review

只对世界建立、剧情反转、英雄镜头、双画幅困难镜头或重复连续性失败镜头启用额外评审。编剧、导演、摄影和连续性监督只能给出局部修改，不得重写已锁定故事。普通镜头不运行反复评审。

## local_repair

- 剧情不清时返回 Beat Map，不靠新增旁白掩盖。
- 连续性失败时冻结剧情和无关镜头，只修复问题镜头及其依赖。
- 关键资产不足时先交付角色、服装、道具和场景参考图提示词。
- 平台能力不足时按 `reference_video → multi_reference_images → first_last_frames → first_frame → text_only → manual_job` 降级，并说明一致性影响。
- API 执行不在 Skill 范围内；任务失败处理只能写入交接建议。

## Logical delivery

默认以 Markdown 分节交付导演摘要、剧本、Canon 与资产圣经、Shot Graph、关键帧提示词、平台提示词包、双画幅方案和质检报告。只有用户明确要求保存文件时，才把这些逻辑部分写成目录。
```

- [ ] **Step 5: Run the routing tests and the legacy suite**

Run:

```powershell
python -m unittest discover -s tests -p "test_cinematic_mode_docs.py" -v
python -m unittest discover -s tests -v
```

Expected: the new file reports 2 passing tests; the full suite reports 45 passing tests.

- [ ] **Step 6: Commit the routing slice**

```powershell
git add SKILL.md references/cinematic-directing.md tests/test_cinematic_mode_docs.py
git commit -m "feat: route cinematic director mode"
```

---

### Task 2: Validate the cinematic brief contract without affecting legacy packages

**Files:**
- Modify: `scripts/validate_package.py:24-133`
- Modify: `scripts/validate_package.py:276-292`
- Modify: `scripts/validate_package.py:525-540`
- Modify: `tests/test_validate_package.py:17-135`
- Modify: `tests/test_validate_package.py:735-774`

- [ ] **Step 1: Add a valid cinematic fixture and four failing tests**

Insert this helper after `valid_package()` in `tests/test_validate_package.py`:

```python
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
```

Insert this class before the module's `if __name__ == "__main__":` block:

```python
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
```

- [ ] **Step 2: Run the validator tests and verify the cinematic fixture fails**

Run:

```powershell
python -m unittest discover -s tests -p "test_validate_package.py" -v
```

Expected: 47 tests run; the valid opt-in fixture may still pass because legacy validation ignores its extra fields, while the three constraint methods fail because cinematic brief validation does not exist.

- [ ] **Step 3: Add the cinematic brief constants and helper**

Add below `QUALITY_REPORT_REQUIRED_FIELDS` in `scripts/validate_package.py`:

```python
CINEMATIC_MODE_REQUIRED_FIELDS = (
    "input_mode",
    "rhythm_preset",
    "delivery_aspects",
    "style_preset",
)

CINEMATIC_INPUT_MODES = {"concept_mode", "screenplay_mode"}
CINEMATIC_RHYTHM_PRESETS = {"A", "B", "C"}
CINEMATIC_DELIVERY_ASPECTS = {"16:9", "9:16"}
```

Add after `_require_fields()`:

```python
def _validate_cinematic_mode(
    project_brief: Any, errors: list[str]
) -> dict[str, Any] | None:
    if not isinstance(project_brief, dict):
        return None
    mode = project_brief.get("cinematic_mode")
    if mode is None:
        return None
    if not isinstance(mode, dict):
        errors.append("project_brief.cinematic_mode: expected object")
        return None

    _require_fields(
        mode,
        CINEMATIC_MODE_REQUIRED_FIELDS,
        "project_brief.cinematic_mode",
        errors,
    )

    if mode.get("input_mode") not in CINEMATIC_INPUT_MODES:
        errors.append(
            "project_brief.cinematic_mode: input_mode must be concept_mode or screenplay_mode"
        )
    if mode.get("rhythm_preset") not in CINEMATIC_RHYTHM_PRESETS:
        errors.append(
            "project_brief.cinematic_mode: rhythm_preset must be A, B, or C"
        )
    aspects = mode.get("delivery_aspects")
    if (
        not isinstance(aspects, list)
        or len(aspects) != 2
        or any(not isinstance(aspect, str) for aspect in aspects)
        or set(aspects) != CINEMATIC_DELIVERY_ASPECTS
    ):
        errors.append(
            "project_brief.cinematic_mode: delivery_aspects must contain exactly 16:9 and 9:16"
        )
    style_preset = mode.get("style_preset")
    if not isinstance(style_preset, str) or not style_preset.strip():
        errors.append(
            "project_brief.cinematic_mode: style_preset must not be empty"
        )

    duration = _positive_decimal(project_brief.get("target_duration_seconds"))
    if duration is not None and not (Decimal(30) <= duration <= Decimal(60)):
        errors.append(
            "project_brief: cinematic target_duration_seconds must be between 30 and 60"
        )
    return mode
```

- [ ] **Step 4: Activate conditional validation inside `validate_package()`**

Immediately after `known_scene_ids = _scene_ids(...)`, add:

```python
    project_brief = package.get("project_brief")
    cinematic_mode = _validate_cinematic_mode(project_brief, errors)
```

At the existing target-duration block, remove only the duplicate assignment `project_brief = package.get("project_brief")`; keep the existing `if isinstance(project_brief, dict):` validation unchanged. `cinematic_mode` remains `None` for every legacy package.

- [ ] **Step 5: Run targeted and full regression tests**

Run:

```powershell
python -m unittest discover -s tests -p "test_validate_package.py" -v
python -m unittest discover -s tests -v
```

Expected: the validator file reports 47 passing tests; the full suite reports 49 passing tests.

- [ ] **Step 6: Commit the brief contract**

```powershell
git add scripts/validate_package.py tests/test_validate_package.py
git commit -m "feat: validate cinematic mode brief"
```

---

### Task 3: Validate Shot Graph fields and dual-aspect job coverage

**Files:**
- Modify: `scripts/validate_package.py:39-90`
- Modify: `scripts/validate_package.py:304-524`
- Modify: `scripts/validate_package.py:648-756`
- Modify: `tests/test_validate_package.py` before the module runner

- [ ] **Step 1: Add four failing Shot Graph tests**

Append these methods to `CinematicBriefValidationTests`:

```python
    def test_cinematic_shot_requires_graph_and_aspect_fields(self):
        fields = (
            "rhythm_role",
            "state_dependencies",
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
            "shot shot-01: recomposition_9x16.composition must not be empty",
            errors,
        )
        self.assertIn(
            "shot shot-01: recomposition_9x16.safe_areas must be a list",
            errors,
        )

    def test_cinematic_manifest_requires_each_delivery_aspect_per_shot(self):
        package = cinematic_package()
        package["model_job_manifest"] = [package["model_job_manifest"][0]]
        self.assertIn(
            "model_job_manifest: shot shot-01 missing cinematic aspect job 9:16",
            validate_package(package),
        )
```

- [ ] **Step 2: Run the validator tests and verify four failures**

Run:

```powershell
python -m unittest discover -s tests -p "test_validate_package.py" -v
```

Expected: 51 tests run; the four new methods fail because cinematic shot fields and aspect coverage are not validated.

- [ ] **Step 3: Add cinematic shot constants and a local validator**

Add near the other required-field constants:

```python
CINEMATIC_SHOT_REQUIRED_FIELDS = (
    "rhythm_role",
    "state_dependencies",
    "composition_16x9",
    "recomposition_9x16",
    "platform_capability_needs",
)

CINEMATIC_RHYTHM_ROLES = {
    "world_building",
    "performance",
    "reaction",
    "insert",
    "hero",
    "suspense",
    "transition",
}

PORTRAIT_RECOMPOSITION_STRATEGIES = {
    "recompose",
    "independent_generation",
}
```

Add after `_validate_cinematic_mode()`:

```python
def _validate_cinematic_shot(
    shot_id: str, shot: dict[str, Any], errors: list[str]
) -> list[str]:
    _require_fields(
        shot,
        CINEMATIC_SHOT_REQUIRED_FIELDS,
        f"shot {shot_id}",
        errors,
    )

    if shot.get("rhythm_role") not in CINEMATIC_RHYTHM_ROLES:
        errors.append(
            f"shot {shot_id}: rhythm_role must be a documented cinematic role"
        )
    if not _is_nonempty(shot.get("composition_16x9")):
        errors.append(f"shot {shot_id}: composition_16x9 must not be empty")

    dependencies = shot.get("state_dependencies")
    if not isinstance(dependencies, list):
        errors.append(f"shot {shot_id}: state_dependencies must be a list")
        dependencies = []
    else:
        _validate_nonempty_string_list(
            f"shot {shot_id}",
            dependencies,
            "state_dependencies",
            errors,
        )
        dependencies = [
            dependency
            for dependency in dependencies
            if isinstance(dependency, str) and dependency.strip()
        ]

    needs = shot.get("platform_capability_needs")
    if not isinstance(needs, list):
        errors.append(
            f"shot {shot_id}: platform_capability_needs must be a list"
        )
    else:
        _validate_nonempty_string_list(
            f"shot {shot_id}",
            needs,
            "platform_capability_needs",
            errors,
        )

    portrait = shot.get("recomposition_9x16")
    if not isinstance(portrait, dict):
        errors.append(f"shot {shot_id}: recomposition_9x16 must be an object")
    else:
        _require_fields(
            portrait,
            ("strategy", "composition", "safe_areas"),
            f"shot {shot_id} recomposition_9x16",
            errors,
        )
        if portrait.get("strategy") not in PORTRAIT_RECOMPOSITION_STRATEGIES:
            errors.append(
                f"shot {shot_id}: recomposition_9x16.strategy must be recompose or independent_generation"
            )
        if not _is_nonempty(portrait.get("composition")):
            errors.append(
                f"shot {shot_id}: recomposition_9x16.composition must not be empty"
            )
        if not isinstance(portrait.get("safe_areas"), list):
            errors.append(
                f"shot {shot_id}: recomposition_9x16.safe_areas must be a list"
            )

    return dependencies
```

- [ ] **Step 4: Integrate state-dependency validation into the storyboard loop**

Before the storyboard loop, initialize:

```python
    cinematic_dependencies: dict[str, list[str]] = {}
```

Inside the loop, after a valid `shot_id` is added to `shot_by_id`, add:

```python
            if cinematic_mode is not None:
                cinematic_dependencies[raw_shot_id] = _validate_cinematic_shot(
                    raw_shot_id, shot, errors
                )
```

After the loop and before sequence validation, add:

```python
    for shot_id, dependencies in cinematic_dependencies.items():
        for dependency in dependencies:
            if dependency == shot_id:
                errors.append(
                    f"shot {shot_id}: state_dependency must not reference itself"
                )
            elif dependency not in known_shot_ids:
                errors.append(
                    f"shot {shot_id}: unknown state_dependency {dependency}"
                )
```

- [ ] **Step 5: Enforce job coverage for both requested aspects**

Before the job loop, initialize:

```python
    job_aspects_by_shot: dict[str, set[str]] = {}
```

Inside the valid `job_shot_id` branch, after incrementing `job_counts`, add:

```python
                job_aspect = job.get("aspect")
                if isinstance(job_aspect, str) and job_aspect.strip():
                    job_aspects_by_shot.setdefault(job_shot_id, set()).add(
                        job_aspect
                    )
```

After the existing job-count coverage loop, add:

```python
    if cinematic_mode is not None:
        required_aspects = {
            aspect
            for aspect in cinematic_mode.get("delivery_aspects", [])
            if isinstance(aspect, str)
        }
        for shot_id in sorted(known_shot_ids):
            missing_aspects = required_aspects - job_aspects_by_shot.get(
                shot_id, set()
            )
            for aspect in sorted(missing_aspects):
                errors.append(
                    f"model_job_manifest: shot {shot_id} "
                    f"missing cinematic aspect job {aspect}"
                )
```

- [ ] **Step 6: Run targeted and full tests**

Run:

```powershell
python -m unittest discover -s tests -p "test_validate_package.py" -v
python -m unittest discover -s tests -v
```

Expected: the validator file reports 51 passing tests; the full suite reports 53 passing tests.

- [ ] **Step 7: Commit the Shot Graph slice**

```powershell
git add scripts/validate_package.py tests/test_validate_package.py
git commit -m "feat: validate cinematic shot graph"
```

---

### Task 4: Enforce narrative and continuity hard gates

**Files:**
- Modify: `scripts/validate_package.py:118-133`
- Modify: `scripts/validate_package.py:758-802`
- Modify: `tests/test_validate_package.py` before the module runner

- [ ] **Step 1: Add four failing quality-gate tests**

Append to `CinematicBriefValidationTests`:

```python
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

    def test_unready_cinematic_draft_may_report_a_failed_gate(self):
        package = cinematic_package()
        package["quality_report"]["ready"] = False
        package["quality_report"]["checks"]["narrative_clarity"][
            "goal"
        ] = "fail"
        self.assertNotIn(
            "quality_report: ready cannot be true while cinematic hard gates fail",
            validate_package(package),
        )
```

- [ ] **Step 2: Run the validator tests and verify the new failures**

Run:

```powershell
python -m unittest discover -s tests -p "test_validate_package.py" -v
```

Expected: 55 tests run; the three tests that require cinematic gate enforcement fail, while the unready-draft test may already pass because legacy validation does not forbid a false readiness value.

- [ ] **Step 3: Add hard-gate field definitions and validation**

Add near the cinematic constants:

```python
CINEMATIC_NARRATIVE_FIELDS = (
    "protagonist",
    "goal",
    "obstacle",
    "causality",
    "ending_change",
)
```

Add this helper before `validate_package()`:

```python
def _validate_cinematic_quality(
    quality_report: dict[str, Any], errors: list[str]
) -> None:
    checks = quality_report.get("checks")
    if not isinstance(checks, dict):
        return
    _require_fields(
        checks,
        ("narrative_clarity", "continuity_integrity"),
        "quality_report.checks",
        errors,
    )

    gate_failed = False
    narrative = checks.get("narrative_clarity")
    if not isinstance(narrative, dict):
        if "narrative_clarity" in checks:
            errors.append(
                "quality_report.checks.narrative_clarity: expected object"
            )
        gate_failed = True
    else:
        _require_fields(
            narrative,
            CINEMATIC_NARRATIVE_FIELDS,
            "quality_report.checks.narrative_clarity",
            errors,
        )
        for field in CINEMATIC_NARRATIVE_FIELDS:
            value = narrative.get(field)
            if value not in ("pass", "fail"):
                errors.append(
                    "quality_report.checks.narrative_clarity."
                    f"{field} must be pass or fail"
                )
                gate_failed = True
            elif value == "fail":
                gate_failed = True

    continuity = checks.get("continuity_integrity")
    if not isinstance(continuity, dict):
        if "continuity_integrity" in checks:
            errors.append(
                "quality_report.checks.continuity_integrity: expected object"
            )
        gate_failed = True
    else:
        _require_fields(
            continuity,
            ("status", "unresolved_conflicts"),
            "quality_report.checks.continuity_integrity",
            errors,
        )
        status = continuity.get("status")
        if status not in ("pass", "fail"):
            errors.append(
                "quality_report.checks.continuity_integrity.status "
                "must be pass or fail"
            )
            gate_failed = True
        elif status == "fail":
            gate_failed = True
        conflicts = continuity.get("unresolved_conflicts")
        if not isinstance(conflicts, list):
            errors.append(
                "quality_report.checks.continuity_integrity."
                "unresolved_conflicts must be a list"
            )
            gate_failed = True
        else:
            _validate_nonempty_string_list(
                "quality_report.checks.continuity_integrity",
                conflicts,
                "unresolved_conflicts",
                errors,
            )
            if conflicts:
                gate_failed = True

    if quality_report.get("ready") is True and gate_failed:
        errors.append(
            "quality_report: ready cannot be true while cinematic hard gates fail"
        )
```

- [ ] **Step 4: Invoke hard-gate validation conditionally**

At the end of the existing `quality_report` object branch, after unresolved-provider validation, add:

```python
        if cinematic_mode is not None:
            _validate_cinematic_quality(quality_report, errors)
```

- [ ] **Step 5: Run targeted and full tests**

Run:

```powershell
python -m unittest discover -s tests -p "test_validate_package.py" -v
python -m unittest discover -s tests -v
```

Expected: the validator file reports 55 passing tests; the full suite reports 57 passing tests.

- [ ] **Step 6: Commit the quality gates**

```powershell
git add scripts/validate_package.py tests/test_validate_package.py
git commit -m "feat: enforce cinematic quality gates"
```

---

### Task 5: Integrate the approved directing behavior into stage references

**Files:**
- Modify: `tests/test_cinematic_mode_docs.py`
- Modify: `references/story-directing.md:21-48`
- Modify: `references/continuity-storyboard.md:93-145`
- Modify: `references/prompt-compiler.md:40-99`
- Modify: `references/output-contract.md:22-84`

- [ ] **Step 1: Add a failing stage-reference contract test**

Add this method to `CinematicModeDocsTests`:

```python
    def test_stage_references_expose_the_cinematic_contract(self):
        expected_tokens = {
            "references/story-directing.md": (
                "cinematic_six_beats",
                "concept_mode",
                "screenplay_mode",
            ),
            "references/continuity-storyboard.md": (
                "rhythm_role",
                "state_dependencies",
                "composition_16x9",
                "recomposition_9x16",
                "platform_capability_needs",
            ),
            "references/prompt-compiler.md": (
                "global_lock_block",
                "shot_direction_block",
                "platform_compile_block",
            ),
            "references/output-contract.md": (
                "project_brief.cinematic_mode",
                "narrative_clarity",
                "continuity_integrity",
            ),
        }
        for path, tokens in expected_tokens.items():
            content = self.read(path)
            for token in tokens:
                with self.subTest(path=path, token=token):
                    self.assertIn(token, content)
```

- [ ] **Step 2: Run the doc tests and verify the new method fails**

Run:

```powershell
python -m unittest discover -s tests -p "test_cinematic_mode_docs.py" -v
```

Expected: 3 tests run; the stage-reference method fails on the missing machine-readable field names.

- [ ] **Step 3: Add input routing and the six-beat map to `story-directing.md`**

Insert after `## 输入与职责`:

```markdown
### 电影化输入路由

当 `project_brief.cinematic_mode` 存在时，先记录输入模式：

- `concept_mode`：从用户事实生成可逆草案，不把补全内容写成用户事实。
- `screenplay_mode`：锁定原剧本的核心事件、动机和因果，只压缩节奏、场面与对白。
- 长篇小说不是首版可用模式；请求用户选择一个自包含片段或提供剧本。

电影化故事结构使用 `cinematic_six_beats`：`hook`、`goal`、`escalation`、`reversal`、`climax_choice`、`aftertaste`。每个 beat 都必须声明进入状态、可见变化、原因、结果和时长。六段可合并但不能让目标、阻碍、因果或结尾变化消失。
```

- [ ] **Step 4: Add Shot Graph and dual-aspect fields to `continuity-storyboard.md`**

Insert after `## 逐镜状态`:

```markdown
### 电影化 Shot Graph 扩展

仅当 `project_brief.cinematic_mode` 存在时，每个镜头增加：

- `rhythm_role`：`world_building`、`performance`、`reaction`、`insert`、`hero`、`suspense` 或 `transition`。
- `state_dependencies`：本镜状态依赖的上游 `shot_id` 数组；不得引用自身或不存在的镜头。
- `composition_16x9`：电影母版构图、人物调度和前中后景关系。
- `recomposition_9x16`：包含 `strategy`、`composition`、`safe_areas`。`strategy` 只能是 `recompose` 或 `independent_generation`。
- `platform_capability_needs`：为实现该镜头所需的参考图、首帧、尾帧、音频或编辑能力，不在此处映射厂商字段。

两种画幅共享 `story_function`、角色 ID、事件、对白意义、`opening_state` 和 `closing_state`。9:16 不得写成对 16:9 的机械裁切。完整制作包必须为每个镜头和每个 `delivery_aspects` 值生成可追溯 job。
```

- [ ] **Step 5: Add three-layer cinematic compilation to `prompt-compiler.md`**

Insert after `## 规范语义顺序`:

```markdown
### 电影化三层编译

启用电影化模式时，仍只保留一个 canonical prompt record，但按以下三层组织语义：

1. `global_lock_block`：角色、服装、道具、场景、时代、材质、色彩和禁止项。
2. `shot_direction_block`：单一主动作、表演、构图、一个主要运镜、光线、时间进程、声音和边界状态。
3. `platform_compile_block`：把前两层映射成所选平台已核实的格式、参考输入和参数；不得新增故事事实。

反奇怪感检查要求每镜只有一个主要动作、一个主要运镜、一个主要情绪转折和一个视觉关注点。发现两个独立动作、相互冲突的运镜或无法同时验收的特效时，返回分镜阶段拆分或选择 fallback，而不是继续堆形容词。
```

- [ ] **Step 6: Document the optional JSON extension in `output-contract.md`**

Insert after `## 跨对象不变量`:

````markdown
### 可选电影化扩展

旧制作包无需增加字段。启用时，`project_brief.cinematic_mode` 使用：

```json
{
  "input_mode": "concept_mode",
  "rhythm_preset": "A",
  "delivery_aspects": ["16:9", "9:16"],
  "style_preset": "dark-fantasy"
}
```

此时 storyboard 每镜必须包含 `rhythm_role`、`state_dependencies`、`composition_16x9`、`recomposition_9x16` 和 `platform_capability_needs`。每镜必须有 16:9 与 9:16 job 覆盖。

`quality_report.checks.narrative_clarity` 必须逐项记录 `protagonist`、`goal`、`obstacle`、`causality`、`ending_change` 的 `pass` 或 `fail`。`quality_report.checks.continuity_integrity` 必须记录 `status` 与 `unresolved_conflicts`。任一硬门失败时，`quality_report.ready` 只能是 `false`。

导演摘要、剧本、Canon 与资产圣经、Shot Graph、关键帧、平台包、双画幅方案和质检报告是逻辑交付部分。默认在 Markdown 或十对象 JSON 中表达；只有用户明确要求保存文件时才创建实际目录。
````

- [ ] **Step 7: Run documentation and full regression tests**

Run:

```powershell
python -m unittest discover -s tests -p "test_cinematic_mode_docs.py" -v
python -m unittest discover -s tests -v
```

Expected: the docs file reports 3 passing tests; the full suite reports 58 passing tests.

- [ ] **Step 8: Commit the stage contracts**

```powershell
git add references/story-directing.md references/continuity-storyboard.md references/prompt-compiler.md references/output-contract.md tests/test_cinematic_mode_docs.py
git commit -m "docs: define cinematic production contract"
```

---

### Task 6: Add a verified HappyHorse adapter and preserve manual degradation

**Files:**
- Modify: `tests/test_cinematic_mode_docs.py`
- Modify: `references/model-adapters.md:20-38`
- Modify: `references/model-adapters.md:290-392`

- [ ] **Step 1: Add a failing adapter contract test**

Add this method to `CinematicModeDocsTests`:

```python
    def test_happyhorse_adapter_is_verified_and_mode_specific(self):
        adapters = self.read("references/model-adapters.md")
        required_tokens = (
            "## HappyHorse on Alibaba Cloud Model Studio",
            "happyhorse-1.1-t2v",
            "happyhorse-1.1-i2v",
            "happyhorse-1.1-r2v",
            "create_task_then_poll",
            "result_url_valid_for_24_hours",
            "i2v_request_schema",
            "r2v_request_schema",
        )
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, adapters)
```

- [ ] **Step 2: Run the docs tests and verify the HappyHorse failure**

Run:

```powershell
python -m unittest discover -s tests -p "test_cinematic_mode_docs.py" -v
```

Expected: 4 tests run; only the HappyHorse method fails.

- [ ] **Step 3: Extend the adapter record vocabulary**

After the existing required adapter fields in `## Adapter 记录字段`, add:

```markdown
电影化模式还要记录异步与留存语义：

- `async_job_model`：同步、创建后轮询或未核实。
- `result_expiry`：官方明确的结果有效期；未明确时写 `unsupported_or_unverified`。

这两个字段只描述任务交接，不授权 Skill 提交、轮询或下载任务。
```

- [ ] **Step 4: Add the HappyHorse section before `## Generic fallback`**

Insert this section after Seedance:

```markdown
## HappyHorse on Alibaba Cloud Model Studio

**official_docs**

- https://www.alibabacloud.com/help/en/model-studio/video-generate-edit-model
- https://www.alibabacloud.com/help/en/model-studio/happyhorse-text-to-video-api-reference

**verified_at**：2026-07-18

**verified_models**

- `happyhorse-1.1-t2v`
- `happyhorse-1.1-i2v`
- `happyhorse-1.1-r2v`

**supported_generation_modes**

- text-to-video：`happyhorse-1.1-t2v`
- first-frame image-to-video：`happyhorse-1.1-i2v`
- reference-image-to-video：`happyhorse-1.1-r2v`

**prompt_language**

- text-to-video 官方字段 `input.prompt` 支持任意语言。

**reference_inputs**

- `t2v` 不需要图像参考。
- `i2v` 与 `r2v` 的模型和用途已由官方模型表核实，但本次没有从独立 API 正文逐字段读取输入 schema；job 中保留 Canon 资产引用，并把 `i2v_request_schema` 或 `r2v_request_schema` 放入手动配置。

**first_last_frame_support**

- `unsupported_or_unverified`；不得把其他阿里云视频模型的首尾帧能力写成 HappyHorse 能力。

**audio_support**

- 官方模型表将 HappyHorse 1.1 的 t2v、i2v、r2v 标记为音画输出。自定义音频输入方式未在所选 HappyHorse 正文中核实。

**documented_durations**

- 3–15 秒。

**documented_aspect_ratios_or_sizes**

- t2v 比例：`16:9`、`9:16`、`1:1`、`4:3`、`3:4`、`4:5`、`5:4`、`9:21`、`21:9`。
- 分辨率：`720P`、`1080P`。
- i2v 与 r2v 的比例控制方式需按各自请求 schema 再核实。

**documented_parameters**

- t2v：`model`、`input.prompt`、`parameters.resolution`、`parameters.ratio`、`parameters.duration`、`parameters.watermark`、`parameters.seed`。
- 异步请求头：`X-DashScope-Async: enable`。
- 状态流转：`PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED`、`CANCELED`、`UNKNOWN`。

**async_job_model**：`create_task_then_poll`。

**result_expiry**：`result_url_valid_for_24_hours`；任务 ID 查询有效期同为 24 小时，应提示用户的编排程序及时归档。

**unsupported_or_unverified**

- i2v 和 r2v 的精确 endpoint、输入字段与参考数量。
- 自定义音频、首尾帧、相机控制和编辑字段。
- 用户账户对应的区域、workspace domain、配额和价格。

**requires_manual_configuration**

- `workspace_id`
- `region_endpoint`
- `authentication`
- `input_asset_urls`
- `i2v_request_schema`
- `r2v_request_schema`
- `result_persistence`

**adaptation_notes**

- 有稳定角色参考资产时，优先建议 r2v；只有首帧时建议 i2v；素材未完成时保留 t2v 或 generic/manual job。
- 只有 t2v 正文中逐字段核实的字段可以进入可执行 `documented_parameters`。i2v/r2v job 在独立 schema 核实前保持 manual-only。
- Skill 只交付任务清单，不提交、轮询或下载真实任务。
```

- [ ] **Step 5: Keep Kling and Seedance degradation explicit**

In the existing Kling and Seedance `adaptation_notes`, ensure each section contains this exact status sentence:

```markdown
**cinematic_adapter_status**：`manual_only_until_official_request_schema_is_readable`。
```

Do not add model IDs, endpoint fields, durations, ratios, reference limits, or audio features to those sections unless they are readable in the official request schema during implementation.

- [ ] **Step 6: Run documentation and full regression tests**

Run:

```powershell
python -m unittest discover -s tests -p "test_cinematic_mode_docs.py" -v
python -m unittest discover -s tests -v
```

Expected: the docs file reports 4 passing tests; the full suite reports 59 passing tests.

- [ ] **Step 7: Commit the adapter slice**

```powershell
git add references/model-adapters.md tests/test_cinematic_mode_docs.py
git commit -m "feat: add HappyHorse adapter guidance"
```

---

### Task 7: Add cinematic behavioral prompt regressions

**Files:**
- Create: `tests/test_test_prompts.py`
- Modify: `test-prompts.json`

- [ ] **Step 1: Add a failing prompt-catalog test**

Create `tests/test_test_prompts.py`:

```python
import json
import unittest
from pathlib import Path


CATALOG = Path(__file__).resolve().parents[1] / "test-prompts.json"


class TestPromptCatalogTests(unittest.TestCase):
    def setUp(self):
        self.prompts = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_prompt_ids_are_unique_and_records_are_complete(self):
        ids = [record["id"] for record in self.prompts]
        self.assertEqual(len(ids), len(set(ids)))
        for record in self.prompts:
            with self.subTest(prompt_id=record["id"]):
                self.assertIsInstance(record["prompt"], str)
                self.assertTrue(record["prompt"].strip())
                self.assertIsInstance(record["expected"], str)
                self.assertTrue(record["expected"].strip())

    def test_cinematic_regression_prompts_are_present(self):
        ids = {record["id"] for record in self.prompts}
        self.assertTrue(
            {
                "P4-cinematic-concept-dual-aspect",
                "P5-cinematic-screenplay-adaptation",
                "P6-cinematic-novel-reserved",
                "P7-cinematic-hard-gates",
            }.issubset(ids)
        )


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the prompt-catalog tests and verify one failure**

Run:

```powershell
python -m unittest discover -s tests -p "test_test_prompts.py" -v
```

Expected: 2 tests run; record structure passes and the required cinematic ID test fails.

- [ ] **Step 3: Add four complete prompt records**

Append these objects to the JSON array in `test-prompts.json`, adding a comma after the existing P3 object:

```json
{
  "id": "P4-cinematic-concept-dual-aspect",
  "prompt": "使用通用电影化模式，把这个灵感做成45秒预告：一个失去名字的守门人发现，每次放行亡魂都会忘掉自己的一段记忆。默认叙事优先电影化，输出16:9母版和9:16重构，并适配可灵、Seedance和HappyHorse。",
  "expected": "识别concept_mode与45秒范围；默认rhythm preset A；先锁定主角、目标、阻碍、因果和结尾变化；建立角色、服装、道具、场景与状态ID；每镜包含Shot Graph依赖和双画幅构图；可灵与Seedance无法读取官方请求schema时保持manual-only，HappyHorse只使用已核实字段；剧情与连续性不过关时ready为false。"
},
{
  "id": "P5-cinematic-screenplay-adaptation",
  "prompt": "我有一份完整剧本，请改成60秒电影级片段。不能改变妹妹主动留下、哥哥独自逃生这个结局；可以压缩对白。需要A为默认节奏，同时给出B和C如何调整镜头资源，但不要改剧情。",
  "expected": "识别screenplay_mode；把结局、动机和因果写入锁定事实；压缩场面和对白而不反转人物选择；A/B/C只改变景别、表演、奇观与运镜资源，事件顺序和结局不变；生成双画幅方案与可审计硬门检查。"
},
{
  "id": "P6-cinematic-novel-reserved",
  "prompt": "这是我的三十万字小说全文，请直接自动拆成第一季并先生成第1集。",
  "expected": "不宣称首版已支持长篇小说或整季拆解；说明novel_mode_reserved边界；只问一个实质问题，请用户选择一个自包含章节/剧情段落或提供剧本；不提前编造人物关系、集数与剧情。"
},
{
  "id": "P7-cinematic-hard-gates",
  "prompt": "先别管为什么，主角第一镜是白发少年，第二镜变成红发成年女人，戒指也从左手跑到右手；只要镜头足够震撼就直接给Seedance提示词。",
  "expected": "明确拒绝用震撼度覆盖角色与剧情硬门；指出身份、年龄、发色和道具状态冲突；返回最早受影响的Canon或分镜阶段，只问一个决定问题；在narrative_clarity与continuity_integrity通过前不生成最终平台提示词，Seedance字段不猜测。"
}
```

- [ ] **Step 4: Validate JSON and run all prompt tests**

Run:

```powershell
python -m json.tool test-prompts.json | Out-Null
python -m unittest discover -s tests -p "test_test_prompts.py" -v
```

Expected: JSON parsing succeeds and both prompt-catalog tests pass.

- [ ] **Step 5: Run the full suite**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: 61 tests pass.

- [ ] **Step 6: Commit the behavioral regressions**

```powershell
git add test-prompts.json tests/test_test_prompts.py
git commit -m "test: add cinematic director prompts"
```

---

### Task 8: Verify the implementation against the approved specification

**Files:**
- Inspect: `docs/superpowers/specs/2026-07-18-cinematic-director-mode-design.md`
- Inspect: all files changed by Tasks 1–7

- [ ] **Step 1: Verify JSON, Python tests, and whitespace**

Run:

```powershell
python -m json.tool test-prompts.json | Out-Null
python -m unittest discover -s tests -v
git diff --check
```

Expected: JSON parsing succeeds, 61 tests pass, and `git diff --check` prints nothing.

- [ ] **Step 2: Check the approved product invariants directly**

Run:

```powershell
rg -n "concept_mode|screenplay_mode|novel_mode_reserved|rhythm preset A|16:9|9:16|narrative_clarity|continuity_integrity" SKILL.md references scripts tests test-prompts.json
rg -n "happyhorse-1.1-t2v|happyhorse-1.1-i2v|happyhorse-1.1-r2v|manual_only_until_official_request_schema_is_readable" references/model-adapters.md tests/test_cinematic_mode_docs.py
```

Expected: every approved mode, hard gate, aspect, HappyHorse model, and manual degradation marker appears in both its owning reference and its regression test.

- [ ] **Step 3: Confirm legacy behavior remains opt-in and no execution code was added**

Inspect `scripts/validate_package.py` and confirm:

- packages without `project_brief.cinematic_mode` follow the original validation path;
- no HTTP client, SDK, subprocess-based provider invocation, polling loop, download code, or credential handling was introduced;
- `quality_report.ready` means package readiness only;
- `results.tsv` is unchanged.

- [ ] **Step 4: Confirm commit and worktree state**

Run:

```powershell
git status --short --branch
git log --oneline -9
```

Expected: the worktree is clean, `main` contains the seven implementation commits, and the two approved design commits remain in history.

- [ ] **Step 5: Prepare the handoff summary**

Report:

- cinematic mode is opt-in and defaults to A;
- concept and screenplay inputs are implemented, while novel input is explicitly reserved;
- dual-aspect and Shot Graph invariants are validator-backed;
- story clarity and continuity are hard readiness gates;
- HappyHorse is verified at the documented level, while Kling and Seedance remain manual where request schemas are unreadable;
- 61 tests pass and no API call was executed.
