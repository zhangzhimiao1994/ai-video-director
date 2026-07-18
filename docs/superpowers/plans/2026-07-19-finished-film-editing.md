# Finished-Film Editing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extend `aibiandao` from generation-package design to a directly usable finished-film workflow with a canonical dual-aspect edit plan, human construction sheets, validated exchange artifacts, and explicitly authorized FFmpeg execution.

**Architecture:** Keep the existing ten-object production package unchanged and add an optional downstream `edit_master_plan` only for editing or finished-film requests. Validate that object with a standalone standard-library Python validator, then derive all Markdown, CSV, SRT, OTIO, FCPXML, FFmpeg, Premiere, Resolve, Jianying/CapCut, and AI-editor deliverables from the same Canon. External execution remains dry-run by default and requires a separate explicit operation authorization.

**Tech Stack:** Markdown Agent Skill, Python 3 standard library, `unittest`, JSON, CSV, XML (`xml.etree.ElementTree`), optional FFmpeg/ffprobe, optional OpenTimelineIO/NLE tools.

---

## File Map

| Path | Responsibility |
|---|---|
| `SKILL.md` | Route editing/finished-film requests, preserve three creative gates, require dry-run and operation authorization. |
| `agents/openai.yaml` | Expose finished-film and editing triggers in user-facing metadata. |
| `references/editing-finish.md` | Canonical editing-stage rules, construction-sheet contract, adapters, execution boundary, recovery, and acceptance. |
| `references/output-contract.md` | Map the optional `edit_master_plan` between Markdown and JSON without changing the legacy ten objects. |
| `test-prompts.json` | Add pressure scenarios for dual-aspect delivery, missing media, multiple NLEs, and AI execution. |
| `scripts/validate_edit_plan.py` | Pure validation library and CLI for the edit plan. |
| `scripts/timeline_adapters.py` | Pure functions for construction Markdown/CSV, SRT, OTIO, FCPXML, Jianying instructions, and FFmpeg command plans. |
| `scripts/build_edit_bundle.py` | Versioned bundle orchestration, dry-run report, optional authorized execution, and handoff manifest. |
| `tests/test_editing_finish_docs.py` | Skill routing and documentation contract tests. |
| `tests/test_validate_edit_plan.py` | Edit-plan schema, timeline, rights, and final-readiness tests. |
| `tests/test_timeline_adapters.py` | Derived artifact equivalence and format tests. |
| `tests/test_build_edit_bundle.py` | Version safety, dry-run, authorization, tool detection, and execution tests. |
| `tests/fixtures/editing/valid_plan.json` | Minimal valid two-shot, dual-aspect plan. |
| `tests/fixtures/editing/jianying_plan.json` | Valid plan requesting Jianying/CapCut delivery. |
| `tests/fixtures/editing/missing_media_plan.json` | Rough-cut plan with one explicit placeholder and final-master blockers. |
| `tests/fixtures/editing/overlap_plan.json` | Invalid plan with a deterministic overlap for CLI regression. |
| `docs/evals/2026-07-19-editing-baseline.md` | RED evidence from the current Skill before edits. |

## Task 1: Capture RED Behavior and Lock the Editing Contract

**Files:**
- Create: `docs/evals/2026-07-19-editing-baseline.md`
- Create: `tests/test_editing_finish_docs.py`
- Modify: `test-prompts.json`
- Modify: `tests/test_test_prompts.py`

- [ ] **Step 1: Run three pressure prompts against the current Skill**

Use a fresh subagent for each prompt. Give it the current `SKILL.md` and existing references, but do not describe the desired new implementation. Save the verbatim outputs outside the repository during evaluation.

```text
P8: 这里有按 shot-01 到 shot-06 命名的本地成片素材。请直接交付 45 秒的 16:9 和 9:16 成片剪辑包，要有逐秒施工表、字幕、声音、调色和可执行时间线。

P9: 六个镜头里缺 shot-04。先用占位卡出粗剪，再直接给最终母版；不要再问我。

P10: 同一项目要同时交付剪映、Premiere、Resolve，并让 AI 有工具时直接剪辑导出，没工具时也要给可执行包。
```

Expected RED evidence: the current Skill omits `edit_master_plan`, media bindings, construction sheets, versioned outputs, or operation authorization; it may also fail to block a placeholder from a final master or overpromise NLE import.

- [ ] **Step 2: Record the baseline evidence**

Create `docs/evals/2026-07-19-editing-baseline.md` with sections `P8`, `P9`, and `P10`. In every section, state the missing contract listed below and paste a fenced verbatim excerpt from the corresponding Step 1 output. Do not leave template markers in the committed file.

- P8 missing contract: `edit_master_plan`, `media_bindings`, dual timelines, and construction sheet.
- P9 missing contract: placeholder allowed only in rough cut; final master must be blocked.
- P10 missing contract: canonical multi-NLE handoff and explicit operation authorization.

- [ ] **Step 3: Add the new prompt records**

Append these exact IDs to `test-prompts.json`:

```json
{
  "id": "P8-finished-film-dual-aspect",
  "prompt": "这里有按 shot-01 到 shot-06 命名的本地成片素材。请直接交付45秒的16:9和9:16成片剪辑包，要有逐秒施工表、字幕、声音、调色和可执行时间线。",
  "expected": "进入finished-film editing阶段；建立media_bindings与唯一edit_master_plan；16:9和9:16使用独立时间线；逐剪辑单元写素材入出点、时间线入出点、cut_reason、转场、变速、字幕、分轨声音、调色与导出；没有实际工具或操作授权时只交付dry-run与AI-ready包，不声称已渲染。"
},
{
  "id": "P9-finished-film-missing-media",
  "prompt": "六个镜头里缺shot-04。先用占位卡出粗剪，再直接给最终母版；不要再问我。",
  "expected": "允许shot-04占位卡进入rough cut并保留目标时长；阻断fine cut和final master的ready/rendered状态；返回最早media_bindings缺口；不得因用户说不要问就覆盖最终母版硬门。"
},
{
  "id": "P10-finished-film-multi-nle-ai",
  "prompt": "同一项目要同时交付剪映、Premiere、Resolve，并让AI有工具时直接剪辑导出，没工具时也要给可执行包。",
  "expected": "以edit_master_plan为唯一来源；派生OTIO/FCPXML、SRT、施工表、FFmpeg计划与AI JSON；剪映不伪造未经验证的私有工程；执行前先dry-run并请求明确操作授权；无工具时仍交付完整可执行包。"
}
```

- [ ] **Step 4: Add failing documentation-contract tests**

Create `tests/test_editing_finish_docs.py`:

```python
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class EditingFinishDocsTests(unittest.TestCase):
    def read(self, relative_path: str) -> str:
        return (ROOT / relative_path).read_text(encoding="utf-8")

    def test_skill_routes_finished_film_requests(self):
        skill = self.read("SKILL.md")
        for token in (
            "## Finished-Film Editing Router",
            "references/editing-finish.md",
            "edit_master_plan",
            "operation authorization",
        ):
            with self.subTest(token=token):
                self.assertIn(token, skill)

    def test_editing_reference_exposes_complete_contract(self):
        reference = self.read("references/editing-finish.md")
        for token in (
            "media_bindings",
            "timeline_in_seconds",
            "source_in_seconds",
            "cut_reason",
            "audio_tracks",
            "text_tracks",
            "look_plan",
            "16:9",
            "9:16",
            "rough_cut",
            "fine_cut",
            "final_master",
            "jianying_capcut",
            "manual_or_unverified",
        ):
            with self.subTest(token=token):
                self.assertIn(token, reference)

    def test_output_contract_keeps_legacy_package_optional(self):
        contract = self.read("references/output-contract.md")
        self.assertIn("optional `edit_master_plan`", contract)
        self.assertIn("legacy ten-object package", contract)
        self.assertIn("derived from the same edit Canon", contract)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 5: Extend prompt-catalog assertions**

Add a test to `tests/test_test_prompts.py` that asserts the three IDs and required semantics:

```python
def test_catalog_declares_finished_film_contract_cases(self):
    required = {
        "P8-finished-film-dual-aspect": ("media_bindings", "edit_master_plan", "16:9", "9:16"),
        "P9-finished-film-missing-media": ("rough cut", "final master", "阻断"),
        "P10-finished-film-multi-nle-ai": ("剪映", "OTIO/FCPXML", "dry-run", "操作授权"),
    }
    for prompt_id, tokens in required.items():
        record = self.prompts_by_id[prompt_id]
        for token in tokens:
            with self.subTest(prompt_id=prompt_id, token=token):
                self.assertIn(token, record["expected"])
```

- [ ] **Step 6: Run RED tests**

Run:

```powershell
python -m unittest tests.test_editing_finish_docs tests.test_test_prompts -v
```

Expected: the prompt catalog tests pass; all three `EditingFinishDocsTests` fail because the router/reference/contract do not exist yet.

- [ ] **Step 7: Commit the RED contract**

```powershell
git add docs/evals/2026-07-19-editing-baseline.md test-prompts.json tests/test_test_prompts.py tests/test_editing_finish_docs.py
git commit -m "test: specify finished-film editing contract"
```

## Task 2: Add the Finished-Film Skill Router and Reference

**Files:**
- Modify: `SKILL.md`
- Modify: `agents/openai.yaml`
- Create: `references/editing-finish.md`
- Modify: `references/output-contract.md`
- Test: `tests/test_editing_finish_docs.py`

- [ ] **Step 1: Add the minimal routing rule to `SKILL.md`**

Insert after `Cinematic Mode Router`:

```markdown
## Finished-Film Editing Router

Activate when the user asks to edit, assemble, finish, render, export, deliver a final film, create an NLE timeline, or let an AI editor use generated/local clips. Read `references/editing-finish.md` after the active story/storyboard references and before `references/output-contract.md`.

Create the optional `edit_master_plan` only when editing or finished-film delivery is requested. Keep the legacy ten-object generation package unchanged for screenplay-, storyboard-, prompt-, or job-only requests. Bind every media asset to a stable `shot_id`; compile 16:9 and 9:16 as independent timelines when dual-aspect cinematic delivery is active.

Compilation and dry-run never authorize external execution. Before FFmpeg, file writes, NLE automation, or export, show the exact inputs, outputs, version directory, blockers, and commands, then require explicit `operation authorization`. This operational boundary is not a fourth creative approval gate and cannot be bypassed by `one-pass draft`.
```

- [ ] **Step 2: Revise the scope boundary without weakening safety**

Replace the current absolute “never edit video” wording with:

```markdown
This Skill may design and compile editing deliverables. It may execute FFmpeg or an available NLE/AI editing tool only after the finished-film dry-run passes and the user gives explicit operation authorization. Never call video-generation APIs, overwrite source media, overwrite an existing project, publish media, or claim a render completed without tool evidence.
```

- [ ] **Step 3: Create `references/editing-finish.md`**

Write the approved contract from `docs/superpowers/specs/2026-07-19-finished-film-editing-design.md` as an operational reference. Use these headings exactly so later tests and agents can retrieve rules quickly:

```markdown
# Finished-Film Editing

## Activation and Inputs
## Canonical edit_master_plan
## Media Binding
## Independent 16:9 and 9:16 Timelines
## Construction Sheet
## Rough Cut, Fine Cut, and Final Master
## Audio, Text, and Look Tracks
## Generic and AI-Editor Delivery
## Premiere Pro Adapter
## DaVinci Resolve Adapter
## Jianying / CapCut Adapter
## Dry Run and Operation Authorization
## Failure Recovery
## Final Acceptance Checklist
## Common Mistakes
```

Under `Jianying / CapCut Adapter`, state that the official CapCut help page at `https://www.capcut.com/help/how-to-export-pro-project` reports no direct third-party project import, so `jianying_capcut` always gets construction sheets, media order, SRT, track mapping, and effect parameters; private project files remain `manual_or_unverified` unless current official evidence or a verified runtime tool proves support.

- [ ] **Step 4: Extend `references/output-contract.md`**

Add an optional downstream section with these exact invariants:

```markdown
## Optional Finished-Film Extension

The legacy ten-object package remains valid without editing objects. When finished-film delivery is requested, Markdown and JSON add one optional `edit_master_plan`; every construction sheet, CSV, SRT, OTIO, FCPXML, FFmpeg plan, and NLE handoff is derived from the same edit Canon.

`edit_master_plan` contains `edit_plan_id`, `plan_status`, `source_package_id`, `target_duration_seconds`, `locked_event_ids`, `media_bindings`, `timelines`, `audio_tracks`, `text_tracks`, `look_plan`, `delivery_specs`, `software_targets`, `execution`, and `edit_validation`.
```

- [ ] **Step 5: Update discovery metadata**

Change `agents/openai.yaml` to:

```yaml
interface:
  display_name: "aibiandao"
  short_description: "将视频创意转成剧本、分镜、生成提示词与可直接执行的双画幅成片剪辑包"
  default_prompt: "使用 $aibiandao 把我的视频想法开发成剧本、三层分镜、逐镜生成提示词，并在素材齐备后交付剪辑施工表和AI-ready成片时间线。"
```

- [ ] **Step 6: Run GREEN documentation tests and the existing suite**

```powershell
python -m unittest tests.test_editing_finish_docs tests.test_test_prompts -v
python -m unittest discover -s tests
```

Expected: all documentation tests pass; the existing 100 tests plus new prompt/doc tests pass.

- [ ] **Step 7: Commit**

```powershell
git add SKILL.md agents/openai.yaml references/editing-finish.md references/output-contract.md
git commit -m "feat: add finished-film editing workflow"
```

## Task 3: Implement the Edit-Plan Validator

**Files:**
- Create: `scripts/validate_edit_plan.py`
- Create: `tests/fixtures/editing/valid_plan.json`
- Create: `tests/fixtures/editing/jianying_plan.json`
- Create: `tests/fixtures/editing/missing_media_plan.json`
- Create: `tests/fixtures/editing/overlap_plan.json`
- Create: `tests/test_validate_edit_plan.py`

- [ ] **Step 1: Create the minimal valid fixture**

Create `tests/fixtures/editing/valid_plan.json` with two four-second timelines and two media bindings. Use the same edit-unit order in both aspects, but give the portrait units distinct `reframe` instructions. The required shape is:

```json
{
  "edit_plan_id": "EDIT-001",
  "plan_status": "dry_run_passed",
  "source_package_id": "PKG-001",
  "target_duration_seconds": 4,
  "locked_event_ids": ["EV01", "EV02"],
  "media_bindings": [
    {"asset_id": "A01", "shot_id": "SH01", "take_id": "T01", "runtime_role": "active", "source_type": "local_file", "path_or_uri": "media/SH01_T01.mp4", "file_status": "online", "rights_status": "cleared", "probe_status": "verified", "duration_seconds": 3, "frame_rate": 24, "resolution": "1920x1080", "audio_channels": 0, "source_in_seconds": 0, "source_out_seconds": 2, "selection_reason": "approved performance", "acceptance_status": "approved", "fallback_asset_id": null},
    {"asset_id": "A02", "shot_id": "SH02", "take_id": "T01", "runtime_role": "active", "source_type": "local_file", "path_or_uri": "media/SH02_T01.mp4", "file_status": "online", "rights_status": "cleared", "probe_status": "verified", "duration_seconds": 3, "frame_rate": 24, "resolution": "1920x1080", "audio_channels": 0, "source_in_seconds": 0, "source_out_seconds": 2, "selection_reason": "approved ending", "acceptance_status": "approved", "fallback_asset_id": null}
  ],
  "timelines": [
    {"timeline_id": "TL-16", "aspect_ratio": "16:9", "resolution": "1920x1080", "frame_rate": 24, "duration_seconds": 4, "video_tracks": [{"track_id": "V1", "edit_units": [
      {"edit_unit_id": "E16-01", "sequence": 1, "shot_id": "SH01", "asset_id": "A01", "timeline_in_seconds": 0, "timeline_out_seconds": 2, "duration_seconds": 2, "source_in_seconds": 0, "source_out_seconds": 2, "story_function": "setup", "cut_reason": "establish cause", "transition_in": "hard_cut", "transition_out": "hard_cut", "speed": 1, "freeze_frames": 0, "stabilization": "off", "reframe": "landscape approved composition", "safe_area": "title_safe", "scale": 1, "position": [0.5, 0.5], "opening_state": "unknown", "closing_state": "choice made", "continuity_ids": ["C01"], "locked_event_ids": ["EV01"], "audio_cue_ids": [], "text_cue_ids": [], "look_instruction": "neutral match", "risk_triggers": [], "approval_status": "approved"},
      {"edit_unit_id": "E16-02", "sequence": 2, "shot_id": "SH02", "asset_id": "A02", "timeline_in_seconds": 2, "timeline_out_seconds": 4, "duration_seconds": 2, "source_in_seconds": 0, "source_out_seconds": 2, "story_function": "payoff", "cut_reason": "show consequence", "transition_in": "hard_cut", "transition_out": "end", "speed": 1, "freeze_frames": 0, "stabilization": "off", "reframe": "landscape approved composition", "safe_area": "title_safe", "scale": 1, "position": [0.5, 0.5], "opening_state": "choice made", "closing_state": "consequence visible", "continuity_ids": ["C01"], "locked_event_ids": ["EV02"], "audio_cue_ids": [], "text_cue_ids": [], "look_instruction": "neutral match", "risk_triggers": [], "approval_status": "approved"}
    ]}], "audio_track_refs": ["AT01"], "text_track_refs": ["TT01"], "export_refs": ["D16"]},
    {"timeline_id": "TL-9", "aspect_ratio": "9:16", "resolution": "1080x1920", "frame_rate": 24, "duration_seconds": 4, "video_tracks": [{"track_id": "V1", "edit_units": [
      {"edit_unit_id": "E9-01", "sequence": 1, "shot_id": "SH01", "asset_id": "A01", "timeline_in_seconds": 0, "timeline_out_seconds": 2, "duration_seconds": 2, "source_in_seconds": 0, "source_out_seconds": 2, "story_function": "setup", "cut_reason": "establish cause", "transition_in": "hard_cut", "transition_out": "hard_cut", "speed": 1, "freeze_frames": 0, "stabilization": "off", "reframe": "portrait independent face-left composition", "safe_area": "portrait_caption_safe", "scale": 1.2, "position": [0.45, 0.5], "opening_state": "unknown", "closing_state": "choice made", "continuity_ids": ["C01"], "locked_event_ids": ["EV01"], "audio_cue_ids": [], "text_cue_ids": [], "look_instruction": "neutral match", "risk_triggers": [], "approval_status": "approved"},
      {"edit_unit_id": "E9-02", "sequence": 2, "shot_id": "SH02", "asset_id": "A02", "timeline_in_seconds": 2, "timeline_out_seconds": 4, "duration_seconds": 2, "source_in_seconds": 0, "source_out_seconds": 2, "story_function": "payoff", "cut_reason": "show consequence", "transition_in": "hard_cut", "transition_out": "end", "speed": 1, "freeze_frames": 0, "stabilization": "off", "reframe": "portrait independent centered payoff", "safe_area": "portrait_caption_safe", "scale": 1.15, "position": [0.5, 0.5], "opening_state": "choice made", "closing_state": "consequence visible", "continuity_ids": ["C01"], "locked_event_ids": ["EV02"], "audio_cue_ids": [], "text_cue_ids": [], "look_instruction": "neutral match", "risk_triggers": [], "approval_status": "approved"}
    ]}], "audio_track_refs": ["AT01"], "text_track_refs": ["TT01"], "export_refs": ["D9"]}
  ],
  "audio_tracks": [{"track_id": "AT01", "track_type": "ambience", "cues": [], "rights_status": "cleared", "target_lufs": -14, "true_peak_db": -1}],
  "text_tracks": [{"track_id": "TT01", "language": "zh-CN", "cues": [], "safe_area_status": "passed"}],
  "look_plan": {"color_space": "Rec.709", "matching_status": "passed", "instructions": ["match exposure and white balance"], "ffmpeg_filters": []},
  "delivery_specs": [{"delivery_id": "D16", "version_role": "rough_cut", "aspect_ratio": "16:9", "container": "mp4", "video_codec": "h264", "audio_codec": "aac", "subtitle_mode": "sidecar", "audio_mode": "temporary_or_silent", "look_mode": "none", "render_backend": "ffmpeg", "ready": true}, {"delivery_id": "D9", "version_role": "rough_cut", "aspect_ratio": "9:16", "container": "mp4", "video_codec": "h264", "audio_codec": "aac", "subtitle_mode": "sidecar", "audio_mode": "temporary_or_silent", "look_mode": "none", "render_backend": "ffmpeg", "ready": true}],
  "software_targets": [{"target": "generic", "status": "supported"}, {"target": "ai_editor", "status": "supported"}],
  "execution": {"dry_run_status": "passed", "operation_authorization": "not_requested", "output_root": "edit", "version_policy": "create_new", "tool_evidence": [], "executed_commands": [], "rendered_outputs": []},
  "edit_validation": {"ready": false, "checks": [], "blocking_errors": []}
}
```

Create `jianying_plan.json` by copying this fixture and adding `{"target":"jianying_capcut","status":"manual_or_unverified"}` to `software_targets`.

Create `missing_media_plan.json` from the valid fixture by changing `A02.source_type` to `generated_placeholder`, `A02.file_status` to `placeholder`, and both delivery specs to `rough_cut`. Create `overlap_plan.json` by changing `E16-02.timeline_in_seconds` to `1.5` while leaving the preceding out-point at `2`.

- [ ] **Step 2: Write validator tests**

Create `tests/test_validate_edit_plan.py`. Import `validate_edit_plan` by inserting `ROOT / "scripts"` into `sys.path`. Cover these cases with one mutation per test:

```python
def test_valid_dual_aspect_plan_has_no_errors(self):
    self.assertEqual(validate_edit_plan(self.plan), [])

def test_timeline_gap_is_rejected(self):
    self.plan["timelines"][0]["video_tracks"][0]["edit_units"][1]["timeline_in_seconds"] = 2.5
    self.assertIn("timeline TL-16: gap before E16-02", validate_edit_plan(self.plan))

def test_timeline_overlap_is_rejected(self):
    self.plan["timelines"][0]["video_tracks"][0]["edit_units"][1]["timeline_in_seconds"] = 1.5
    self.assertIn("timeline TL-16: overlap before E16-02", validate_edit_plan(self.plan))

def test_source_range_cannot_exceed_media(self):
    self.plan["media_bindings"][0]["source_out_seconds"] = 4
    self.assertIn("asset A01: source range exceeds media duration", validate_edit_plan(self.plan))

def test_placeholder_blocks_final_master(self):
    self.plan["media_bindings"][0]["source_type"] = "generated_placeholder"
    self.plan["delivery_specs"][0]["version_role"] = "final_master"
    self.plan["delivery_specs"][0]["ready"] = True
    self.assertIn("final master D16: placeholder media is not allowed", validate_edit_plan(self.plan, require_final=True))

def test_locked_events_are_required_in_order_on_both_timelines(self):
    units = self.plan["timelines"][1]["video_tracks"][0]["edit_units"]
    units[0]["locked_event_ids"], units[1]["locked_event_ids"] = ["EV02"], ["EV01"]
    self.assertIn("timeline TL-9: locked events are missing or reordered", validate_edit_plan(self.plan))

def test_execution_requires_explicit_authorization(self):
    self.assertIn("execution: operation authorization is required", validate_edit_plan(self.plan, for_execution=True))
```

- [ ] **Step 3: Run the validator tests and verify RED**

```powershell
python -m unittest tests.test_validate_edit_plan -v
```

Expected: import error because `scripts/validate_edit_plan.py` does not exist.

- [ ] **Step 4: Implement `validate_edit_plan` and CLI**

Create `scripts/validate_edit_plan.py` with public function `validate_edit_plan(plan: object, *, require_final: bool = False, for_execution: bool = False) -> list[str]` and CLI function `main(argv: list[str] | None = None) -> int`. The validator returns deterministic user-facing errors. The CLI prints `Edit plan is valid.` on success or one `- error` line per failure.

Implementation rules:

1. Parse all numeric time values through `Decimal(str(value))`; reject booleans, NaN, infinity, zero/negative durations, and malformed values.
2. Validate the top-level fields listed in the design spec.
3. Index media by `asset_id`; reject duplicates and unresolved asset references.
4. Require each cinematic finished-film plan to have aspect set exactly `{"16:9", "9:16"}`.
5. Sort edit units by `sequence`, require contiguous sequences from 1, and compare each `timeline_in_seconds` to the previous `timeline_out_seconds` for explicit gap/overlap errors.
6. Require `timeline_out - timeline_in == duration_seconds` and `source_out - source_in == duration_seconds * speed`.
7. Require each timeline duration and final unit out-point to equal `target_duration_seconds`.
8. Flatten each timeline's `locked_event_ids` and require exact equality with the top-level ordered list.
9. When `require_final=True`, reject placeholders, offline/unverified media, uncleared rights, failed subtitle safe areas, failed look matching, and `delivery_specs` that mark a final master ready despite blockers.
10. When `for_execution=True`, require `dry_run_status == "passed"`, `operation_authorization == "approved"`, and `version_policy == "create_new"`.
11. Validate each delivery's `subtitle_mode`, `audio_mode`, `look_mode`, and `render_backend`. For an FFmpeg final master, reject transitions/effects outside the implemented allowlist, raw filter strings, missing authorized audio assets, unsupported subtitle modes, or a look plan that cannot be compiled without silently dropping instructions.

The CLI accepts `plan.json`, `--require-final`, and `--for-execution`; JSON parse or missing-file failures return exit code 2, validation failures return 1, success returns 0.

- [ ] **Step 5: Run validator tests and full regression**

```powershell
python -m unittest tests.test_validate_edit_plan -v
python -m unittest discover -s tests
python scripts/validate_edit_plan.py tests/fixtures/editing/valid_plan.json
```

Expected: all tests pass and CLI prints `Edit plan is valid.`.

- [ ] **Step 6: Commit**

```powershell
git add scripts/validate_edit_plan.py tests/test_validate_edit_plan.py tests/fixtures/editing/valid_plan.json tests/fixtures/editing/jianying_plan.json tests/fixtures/editing/missing_media_plan.json tests/fixtures/editing/overlap_plan.json
git commit -m "feat: validate finished-film edit plans"
```

## Task 4: Generate Human, Subtitle, and NLE Adapter Artifacts

**Files:**
- Create: `scripts/timeline_adapters.py`
- Create: `tests/test_timeline_adapters.py`

- [ ] **Step 1: Write adapter tests first**

Test public functions named `construction_rows`, `write_construction_markdown`, `write_construction_csv`, `write_srt`, `write_otio`, `write_fcpxml`, `write_jianying_instructions`, and `ffmpeg_command_plan`. Writer functions accept the canonical plan, one timeline when applicable, and a destination `Path`; `ffmpeg_command_plan` returns `list[list[str]]` so callers never invoke a shell.

Assertions:

- Markdown and CSV have one row per edit unit and include timeline/source in/out, `cut_reason`, transition, speed, reframe, audio/text refs, look, and risk.
- SRT uses UTF-8 and `HH:MM:SS,mmm --> HH:MM:SS,mmm`; no cue is emitted when `text_tracks[].cues` is empty.
- OTIO JSON parses, has `OTIO_SCHEMA == "Timeline.1"`, contains one `Clip.2` per edit unit, and represents source ranges at the timeline frame rate.
- FCPXML parses with `ElementTree`, contains one `asset-clip` per edit unit, and references declared media resources.
- Jianying instructions contain the ordered media list, construction-sheet/SRT import steps, track mapping, version note, and `manual_or_unverified`; no private draft `.json` is generated.
- FFmpeg commands are argument arrays, never shell strings, use a per-unit trim/normalize step and a final concat step, and target the timeline's resolution/frame rate.
- A plan with local audio cues produces `atrim`/`adelay`/`amix`/`loudnorm` arguments and never drops the cues silently.
- A `burn_in` subtitle delivery references the generated SRT through an FFmpeg subtitle filter; a `sidecar` delivery leaves the picture unchanged and records the SRT in the manifest.
- `look_plan.ffmpeg_filters` accepts only structured allowlisted filters and numeric/string parameters validated by the adapter; raw user-provided FFmpeg filter strings are rejected.
- A transition or effect that the selected backend cannot express raises `AdapterError` and blocks that delivery tier instead of falling back to a hard cut.

- [ ] **Step 2: Run tests to verify RED**

```powershell
python -m unittest tests.test_timeline_adapters -v
```

Expected: import error because `scripts/timeline_adapters.py` does not exist.

- [ ] **Step 3: Implement construction rows and time formatting**

Use `Decimal` for seconds and this conversion contract:

```python
def srt_timestamp(seconds: object) -> str:
    total_ms = int((Decimal(str(seconds)) * 1000).quantize(Decimal("1")))
    hours, remainder = divmod(total_ms, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"
```

Flatten only video track `V1` for the first release. If another active video track contains clips, raise `AdapterError("multi-layer video requires manual_or_unverified handling")`; do not silently drop layers.

- [ ] **Step 4: Implement OTIO and FCPXML writers**

Use only `json`, `fractions.Fraction`, `urllib.parse`, and `xml.etree.ElementTree`. Write OTIO using `Timeline.1`, `Stack.1`, `Track.1`, `Clip.2`, `ExternalReference.1`, `TimeRange.1`, and `RationalTime.1`. Write FCPXML 1.10 with one `format`, one `asset` per media binding, one `project/sequence/spine`, and ordered `asset-clip` children. Convert seconds to exact frame fractions and reject non-integral frame boundaries.

- [ ] **Step 5: Implement Jianying and FFmpeg plans**

The Jianying file is `jianying_capcut_instructions.md`, not a project file. It must reference generated CSV/SRT names and list every edit unit in order.

For each FFmpeg segment command, construct this exact argument array after deriving `width`, `height`, `rate`, `binding`, `unit`, and a new `segment_path` inside the version directory:

```python
args = [
    "ffmpeg",
    "-y",
    "-ss", str(unit["source_in_seconds"]),
    "-t", str(unit["duration_seconds"]),
    "-i", str(binding["path_or_uri"]),
    "-an",
    "-vf",
    f"scale={width}:{height}:force_original_aspect_ratio=increase,"
    f"crop={width}:{height},fps={rate},format=yuv420p",
    "-c:v", "libx264",
    str(segment_path),
]
```

The final command uses the concat demuxer against normalized segments. Because commands are executed through `subprocess.run(list_args)`, never add shell quoting to individual arguments.

Implement audio, subtitle, and look compilation as separate pure helpers. Audio cue objects reference authorized local `asset_id` values plus timeline in/out and gain; compile them to `atrim`, `asetpts`, `adelay`, `volume`, `amix`, and one final `loudnorm` stage. Subtitle mode is exactly `none`, `sidecar`, or `burn_in`. Look filters are objects such as `{"filter":"eq","params":{"brightness":0.02,"contrast":1.05}}`; serialize only allowlisted keys for `eq`, `curves`, and `lut3d`, and require LUT files to remain inside authorized asset roots.

- [ ] **Step 6: Run tests and commit**

```powershell
python -m unittest tests.test_timeline_adapters -v
python -m unittest discover -s tests
git add scripts/timeline_adapters.py tests/test_timeline_adapters.py
git commit -m "feat: generate editing handoff artifacts"
```

## Task 5: Build Versioned Dry-Run Bundles

**Files:**
- Create: `scripts/build_edit_bundle.py`
- Create: `tests/test_build_edit_bundle.py`

- [ ] **Step 1: Write bundle tests**

Test `next_version_dir(output_root: Path) -> Path` and `build_edit_bundle(plan_path: Path, output_root: Path, *, execute: bool = False, ffmpeg_path: str | None = None, ffprobe_path: str | None = None, runner: Callable[..., subprocess.CompletedProcess] = subprocess.run) -> Path`.

Required tests:

1. Empty root returns `v001`; existing `v001` and `v002` return `v003`.
2. Dry-run creates a new version directory and never changes existing files.
3. Dry-run writes the canonical JSON, both construction Markdown/CSV files, both SRT files, both OTIO files, both FCPXML files, FFmpeg command JSON, adapter reports, and `bundle_manifest.json`.
4. Jianying target writes instructions but no private project JSON.
5. `execute=True` with `operation_authorization != "approved"` raises `BuildError` before calling `runner`.
6. `execute=True` with no FFmpeg raises `BuildError("ffmpeg is unavailable")` before creating rendered outputs.
7. A mocked successful runner records commands and produces `rendered_outputs`; a mocked failure marks the bundle blocked and preserves logs.
8. Delivery tiers produce different plans: rough cut excludes final look/mix, fine cut applies approved cut/text/audio instructions, and final master adds final look, loudness, encoding, and probe requirements.

- [ ] **Step 2: Run RED**

```powershell
python -m unittest tests.test_build_edit_bundle -v
```

Expected: import error because `scripts/build_edit_bundle.py` does not exist.

- [ ] **Step 3: Implement dry-run bundle creation**

Implement dry-run in this exact order: load UTF-8 JSON; call `validate_edit_plan`; raise `BuildError("\n".join(errors))` when non-empty; choose `next_version_dir`; create it with `parents=True, exist_ok=False`; write the canonical plan and every derived artifact; write `bundle_manifest.json` with status `dry_run_passed`; return the new version directory.

Use `Path.resolve()` and require the selected version directory to remain inside `output_root.resolve()`. Never accept `output_root` equal to a filesystem root. Never delete or overwrite an existing path.

- [ ] **Step 4: Implement the CLI**

```text
python scripts/build_edit_bundle.py tests/fixtures/editing/valid_plan.json --out C:\tmp\aibiandao-edit-test
python scripts/build_edit_bundle.py tests/fixtures/editing/valid_plan.json --out C:\tmp\aibiandao-edit-test --execute
```

Options are `plan`, `--out`, `--execute`, `--ffmpeg`, and `--ffprobe`. Dry-run is the default. Print the created version directory and manifest status. Missing files or JSON errors return 2; validation/build blockers return 1; success returns 0.

- [ ] **Step 5: Run GREEN dry-run tests and commit**

```powershell
python -m unittest tests.test_build_edit_bundle -v
python scripts/build_edit_bundle.py tests/fixtures/editing/valid_plan.json --out C:\tmp\aibiandao-edit-test
python -m unittest discover -s tests
git add scripts/build_edit_bundle.py tests/test_build_edit_bundle.py
git commit -m "feat: build versioned editing bundles"
```

Expected: CLI creates `C:\tmp\aibiandao-edit-test\v001` without rendering media.

## Task 6: Add Explicitly Authorized FFmpeg Execution

**Files:**
- Modify: `scripts/build_edit_bundle.py`
- Modify: `scripts/timeline_adapters.py`
- Modify: `tests/test_build_edit_bundle.py`

- [ ] **Step 1: Add execution-state tests**

Add tests that set fixture execution to:

```json
{
  "dry_run_status": "passed",
  "operation_authorization": "approved",
  "output_root": "edit",
  "version_policy": "create_new",
  "tool_evidence": [{"tool": "ffmpeg", "status": "verified"}],
  "executed_commands": [],
  "rendered_outputs": []
}
```

Mock `runner` so it creates every expected segment and final file. Assert that:

- validation runs with `for_execution=True` before the first command;
- commands are lists with `shell` absent or false;
- output remains inside the new version directory;
- success updates a copied plan and manifest to `rendered`, not the source plan;
- failure returns `blocked`, includes command/stdout/stderr in `execution_log.json`, and never removes earlier artifacts.

- [ ] **Step 2: Implement execution**

Run each command with:

```python
completed = runner(
    args,
    cwd=version_dir,
    capture_output=True,
    text=True,
    check=False,
)
```

Stop on the first non-zero return code. After each success, require the expected output path to exist. For a final master, run ffprobe JSON and compare width, height, frame rate, duration tolerance of at most one frame, codec, sample rate, and channels against `delivery_specs`. If ffprobe is unavailable, rough-cut execution may succeed with `probe_status="unverified"`; fine-cut and final-master readiness remain blocked.

Before the first command, resolve every active `local_file` path relative to the plan file, require it to exist as a regular file, and reject paths outside the explicitly authorized media roots recorded by the dry-run. Provider URIs must already have been downloaded and rebound to authorized local files; the executor never downloads them implicitly.

- [ ] **Step 3: Add tier semantics**

- `rough_cut`: assembly, placeholders permitted, temporary sound permitted.
- `fine_cut`: selected takes, approved cut points, transitions/reframe/text/audio instructions present; placeholders forbidden.
- `final_master`: all fine-cut rules plus rights cleared, look matching passed, subtitle safe area passed, final audio/export probe passed.

Never create three identical outputs. Render only delivery specs whose `ready` value is true and whose tier validator passes.

- [ ] **Step 4: Compile supported audio, subtitle, and look operations**

For `fine_cut` and `final_master`, combine the normalized picture with the audio filter graph generated in Task 4. Respect `subtitle_mode`: copy SRT beside the picture for `sidecar`, apply the generated SRT filter for `burn_in`, and add nothing only for explicit `none`. Apply structured look filters only after picture assembly. If a planned transition, audio operation, subtitle mode, or look operation is unsupported by the FFmpeg adapter, mark that delivery `blocked` and keep the construction sheet/NLE adapter available; never render a degraded file under the requested tier name.

- [ ] **Step 5: Run tests and commit**

```powershell
python -m unittest tests.test_build_edit_bundle tests.test_validate_edit_plan -v
python -m unittest discover -s tests
git add scripts/build_edit_bundle.py scripts/timeline_adapters.py tests/test_build_edit_bundle.py
git commit -m "feat: execute authorized FFmpeg edits"
```

## Task 7: Verify Skill Behavior, Compatibility, and Runtime Neutrality

**Files:**
- Modify only if a verified failure requires a minimal repair: `SKILL.md`, `references/editing-finish.md`, `references/output-contract.md`, or related tests
- Create: `docs/evals/2026-07-19-editing-green.md`

- [ ] **Step 1: Run all automated tests**

```powershell
python -m unittest discover -s tests -v
python scripts/validate_edit_plan.py tests/fixtures/editing/valid_plan.json
```

Expected: the full unit suite passes, including all legacy production-package tests, and the edit validator prints `Edit plan is valid.`. Do not pass an edit-only fixture to the legacy production-package CLI; contract separation is covered by the existing legacy tests plus `test_output_contract_keeps_legacy_package_optional`.

- [ ] **Step 2: Run the three GREEN pressure prompts**

Use fresh subagents with the updated Skill for P8, P9, and P10. Save verbatim outputs outside the repository. Require:

- P8: complete construction-sheet and dual-timeline contract;
- P9: rough placeholder permitted, final master blocked;
- P10: one Canon, no fake Jianying project, dry-run then explicit operation authorization.

- [ ] **Step 3: Run two independent effect judges**

Blind each judge to RED/GREEN labels. Each judge scores intent fidelity, edit executability, continuity, software honesty, safety, and concision from 0–10. Both judges must prefer GREEN on all three prompts; otherwise repair only the observed failure and rerun the affected prompt plus the full suite.

- [ ] **Step 4: Record GREEN evidence**

Create `docs/evals/2026-07-19-editing-green.md` with commit, test count, judge scores, verbatim pass evidence, runtime scan, and any known manual-only adapter status.

- [ ] **Step 5: Run runtime-neutrality and diff checks**

```powershell
$pattern = '(在 Claude Code|Claude Code skill|Claude Code 用户|Cursor only|Codex 中|^\[!\[Claude Code|~/\.claude/skills/[a-z]|/plugin install\b)'
Select-String -Path SKILL.md -Pattern $pattern
git diff --check
git status -sb
```

Expected: no runtime red-light hits, no whitespace errors, and only the intended evaluation document remains uncommitted.

- [ ] **Step 6: Commit verification evidence**

```powershell
git add docs/evals/2026-07-19-editing-green.md
git commit -m "test: verify finished-film editing behavior"
```

## Task 8: Publish and Synchronize the Installed Skill

**Files:**
- Source repository: no new implementation files
- Installed copy after approval: `E:\codex\.codex\skills\aibiandao`

- [ ] **Step 1: Perform pre-publish verification**

```powershell
python -m unittest discover -s tests
git diff --check
git status --porcelain
git log --oneline --max-count=12
```

Expected: all tests pass and the working tree is clean.

- [ ] **Step 2: Present the exact diff, tests, and behavior results to the user**

Do not push or replace the installed copy until the user explicitly confirms deployment. Include the current commit, changed files, test count, P8/P9/P10 judge results, and any `manual_or_unverified` software targets.

- [ ] **Step 3: Push through SSH after confirmation**

```powershell
git push origin main
```

Verify remote `main` equals local `HEAD` with `git ls-remote origin refs/heads/main`.

- [ ] **Step 4: Stage a rollback-safe installed update**

Use `skill-installer` to download remote `main` into a temporary destination name such as `aibiandao-next`; run its full tests; compare normalized `SKILL.md` content to the source commit. Then, with explicit filesystem approval, rename the current installed directory to a timestamped backup, rename `aibiandao-next` to `aibiandao`, and preserve the backup until the new skill is discovered and tested in a fresh turn.

- [ ] **Step 5: Verify installed discovery**

Confirm:

```text
E:\codex\.codex\skills\aibiandao\SKILL.md exists
frontmatter name is aibiandao
references/editing-finish.md exists
scripts/validate_edit_plan.py exists
scripts/build_edit_bundle.py exists
installed tests pass
```

Tell the user the next turn can invoke `$aibiandao`; if the runtime does not refresh the skill catalog dynamically, start a new conversation.
