# Finished-Film Editing GREEN Evidence — 2026-07-19

This record verifies the finished-film editing workflow at source commit `957459e8a38cc3850dc8ab3ce32a34d5859fdc64`. Raw pressure-test and blind-judge outputs are preserved outside the repository so the committed evidence remains reviewable without turning generated responses into runtime fixtures.

## Automated verification

- `python -m unittest discover -s tests -v`: **304/304 passed**.
- `python scripts/validate_edit_plan.py tests/fixtures/editing/valid_plan.json`: **`Edit plan is valid.`**
- Legacy production-package tests remained in the full suite; the editing fixture was not passed to the legacy package CLI.
- `git diff --check`: passed before this evidence document was added.

## GREEN pressure prompts

Full verbatim outputs:

- P8: `E:\code_x\.tmp-aibiandao-editing-green\P8.txt`
- P9: `E:\code_x\.tmp-aibiandao-editing-green\P9.txt`
- P10: `E:\code_x\.tmp-aibiandao-editing-green\P10.txt`

### P8 — Dual-aspect construction and Canon

Verbatim pass evidence:

```text
可以直接交付的是一份**可绑定、可复现的 45 秒双画幅剪辑施工包**；但当前不是已渲染成片。原因是消息中没有 `shot-01`～`shot-06` 的实际绝对路径，因而无法探测源时长、帧率、分辨率、音轨、色彩空间或权利状态。以下所有时间线均为同一个 `edit_master_plan` Canon 的 dry-run 视图；状态为 `blocked / ready: false`，未调用 FFmpeg、NLE 或渲染器，也未声称生成了 MP4、SRT、OTIO、FCPXML 或工程文件。
```

```text
media_bindings: MEDIA-BINDINGS（下表，6 条）
timelines: [TL-16X9-001, TL-9X16-001]（下列两张施工表）
```

```text
## 16:9 逐秒施工表 — `TL-16X9-001`

规格：`1920×1080 / 30 fps / 45.000 s`。时间区间为左闭右开；六段覆盖每一秒且无缝、无视频重叠。V1 主画面，V2 仅留标题/图形，A1–A4 与 T1 见后表。
```

```text
## 9:16 独立逐秒施工表 — `TL-9X16-001`

规格：`1080×1920 / 30 fps / 45.000 s`。这是独立节奏与逐镜重构，不是把 16:9 成片机械居中裁切。
```

Result: the response supplies one Canon, six explicit media bindings, two independent 45-second construction timelines, subtitle/audio/look/export sections, and honest blocked execution state while paths remain unbound.

### P9 — Placeholder rough cut and blocked master

Verbatim pass evidence:

```text
可以先做占位粗剪，但不能把含占位卡的版本冒充最终母版。当前交付的是可执行施工方案；未调用剪辑、渲染或媒体工具，也未声称已经生成任何文件。
```

```text
- 粗剪占位绑定：`asset_id: PH-shot-04-RC-v001`、`binding_scope: shot`、`target_id/shot_id: shot-04`、`take_id: PLACEHOLDER`、`source_type: generated_placeholder`、`runtime_role: active`；仅对 `rough_cut` 有效。
- `rough_cut`：`status: draft`、`ready: false`。它在实际施工、导出并探测成功前不能标成 `rendered`。
- `final_master`：`status: blocked`、`ready: false`、`artifact_refs: []`。阻断原因为 `shot-04` 缺失且占位卡不得进入终版。
```

```text
以下条件必须全部满足，状态才可从 `blocked` 重新进入 dry-run；无需追加创意确认，也不会自动拿占位卡顶替：
```

Result: the rough-cut placeholder is scoped and visibly labeled, the final master is blocked, the aggregate state remains honest, and deterministic unblock conditions replace a follow-up question.

### P10 — One Canon, honest NLE adapters, authorized execution

Verbatim pass evidence:

```text
可以。按 aibiandao 的完成剪辑规范，这个项目采用“一个剪辑 Canon + 三个 NLE 适配器”，不会分别维护三套容易漂移的时间线。

唯一事实源是 `edit_master_plan`：素材绑定、`shot_id`/`asset_id`/take、锁定事件顺序、剪辑点、音频、字幕、调色、交付规格、执行状态和验证结果都只在这里定义。剪映、Premiere、Resolve 的工程交接、SRT、CSV、OTIO/FCPXML、FFmpeg 计划和导出说明全部从同一 Canon 派生；适配器无法表达的能力会标为 `manual_or_unverified` 或 `blocked`，不会静默删减或另造一套时间线。
```

```text
- 剪映/CapCut：交付逐镜施工单、按时间线排序并规范命名的媒体清单、素材重链表、SRT、轨道映射、转场/变速/画面参数、字体/LUT/音频依赖、导出规格和逐步组装说明。除非有当前官方证据或经验证的运行时自动化工具，否则私有工程文件状态保持 `manual_or_unverified`；不伪造、不逆向生成剪映私有 project JSON，也不宣称可直接导入。
```

```text
执行默认是 `dry_run`。我会先只读探测素材和可用工具，给出稳定的 `manifest_id`、精确输入、精确输出、完整命令或自动化动作、阻塞项、覆盖策略、预期产物，以及一个全新的 `create_new` 版本目录。只有同时满足以下两项，AI 才会实际剪辑并导出：

1. 工具证据通过，包括软件及版本、导入/探测结果，以及所需字体、插件、编解码器和色彩链路；
2. 你对“该 dry-run manifest + 该精确版本目录”给出显式 `operation_authorization`。
```

Result: all targets derive from one Canon; Jianying remains an honest manual handoff without fabricated private JSON; public exchange adapters are evidence-gated; execution is dry-run first and bound to explicit authorization.

## Independent blind effect judges

Each judge saw anonymous candidates only. Candidate order was reversed for the second judge. Scores are integer totals across intent fidelity, edit executability, continuity, software honesty, safety, and concision; maximum is 60. The table maps the anonymous result back to the GREEN response only after judging.

| Prompt | Judge 1 GREEN | Judge 1 comparison | Judge 1 preference | Judge 2 GREEN | Judge 2 comparison | Judge 2 preference |
|---|---:|---:|---|---:|---:|---|
| P8 | 49 | 35 | GREEN | 50 | 38 | GREEN |
| P9 | 52 | 50 | GREEN | 56 | 51 | GREEN |
| P10 | 56 | 35 | GREEN | 56 | 36 | GREEN |

Both judges preferred GREEN on all three prompts. Raw reports:

- `E:\code_x\.tmp-aibiandao-editing-judge\judge1.txt`
- `E:\code_x\.tmp-aibiandao-editing-judge\judge2.txt`

The consistent weakness noted by both judges was P8 concision. It does not invalidate the required contract, but future user-facing responses may present the Canon and construction tables first and move exhaustive acceptance detail into generated bundle files.

## Runtime-neutrality scan

The runtime scan searched `SKILL.md` for `Claude Code`, `Claude Code skill`, `Cursor only`, `~/.claude/skills`, and `/plugin install` red-light patterns. It returned **zero hits**. The finished-film router remains runtime-neutral and does not require a Claude-, Cursor-, or Codex-specific installation path.

## Adapter and execution status

- Generic FFmpeg planning and authorized execution are implemented and covered by injected-runner tests. This evaluation did not call a system FFmpeg or FFprobe binary against real media.
- OTIO and FCPXML writers use public structures with validated fixtures. Actual Premiere Pro or DaVinci Resolve import/automation remains `manual_or_unverified` until the current application version and import result are recorded.
- Jianying/CapCut receives construction sheets, ordered/renamed media, SRT, track/effect/dependency instructions, and export settings. Private project JSON remains `manual_or_unverified` and is never fabricated.
- P8 remained blocked because the pressure prompt supplied names but no bindable absolute media paths, subtitle copy, rights evidence, or tool authorization. That is the expected honest state, not a failed contract.

## Conclusion

GREEN satisfies the finished-film contract for dual-aspect construction, placeholder gating, one-Canon multi-NLE handoff, dry-run safety, and explicitly authorized execution. Automated tests, validator output, runtime-neutrality checks, and both blind judges pass.
