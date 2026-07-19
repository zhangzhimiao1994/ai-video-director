# Finished-Film Editing RED Baseline — 2026-07-19

This baseline records the current skill's read-only responses before the finished-film editing contract is introduced. The fenced excerpts below are copied verbatim from the raw evaluation outputs.

## P8 — Dual-Aspect Finished-Film Delivery

Missing contract: `edit_master_plan`, `media_bindings`, separate 16:9 and 9:16 timelines (双时间线), and a per-edit-unit execution table (施工表).

Source: `E:\code_x\.tmp-aibiandao-editing-red\P8.txt`

```text
当前无法按这项技能直接交付 45 秒成片或可执行剪辑时间线。技能边界明确禁止编辑本地视频、生成或修改成片；它只能设计并交付提示词与 API-ready 任务清单，不能把未实际完成的字幕、混音、调色或 NLE 工程标记为可执行。

## 🔴 CHECKPOINT 1 · Brief Gate · 🛑 STOP

- 已锁定：素材命名为 `shot-01` 至 `shot-06`；目标时长 45 秒；交付 16:9 与 9:16。
- 未解决：素材内容、源时码、可用时长、声音状态及授权尚未形成可审计记录。
- 制作边界：9:16 应独立重构，不能默认机械裁切；精确字幕只能规划为后期合成。
- 当前状态：`blocked`，不能输出虚构的逐秒施工表或声称 `ready: true`。

是否将本次交付改为本技能支持的“非执行性导演制作包、提示词与 API-ready manifest”，而不是实际成片和 NLE 时间线？
```

## P9 — Missing Media and Master Gate

Current safety behavior: the response already places the missing shot in the rough cut as a `NOT FOR MASTER` placeholder and blocks the final master with `ready: false`. It therefore already enforces 占位只允许粗剪、最终母版必须阻断.

Remaining contract gap: the missing media is not located in machine-readable `edit_master_plan`/`media_bindings`; there is no independent `fine_cut` gate; and `ready`/`rendered` are not constrained in normalized delivery/execution state. The safe judgment is therefore not yet a verifiable, executable finished-film contract.

Source: `E:\code_x\.tmp-aibiandao-editing-red\P9.txt`

```text
无法直接交付粗剪视频或最终母版：本技能不执行视频编辑、媒体下载或生成任务。“不要再问”可以省略中间确认，但不能越过该范围边界。

- 粗剪交接：在 sequence 4 保留 `shot-04` 的原定时长，使用占位卡 `SHOT-04 MISSING / OFFLINE PLACEHOLDER / NOT FOR MASTER`，不得改动前后镜头时长。
- 最终母版：`blocked`
- `quality_report.ready: false`
- `continuity_integrity: fail`
- 未解决冲突：`shot-04` 缺失，无法核验其 opening/closing state 与相邻镜头的连续性。
- 粗剪与最终母版媒体文件均未生成；占位卡不能作为最终镜头交付。
```

## P10 — Multi-NLE AI Handoff

Missing contract: one Canon for multi-NLE handoff (唯一 Canon 的多 NLE 交接) plus explicit operation authorization (显式操作授权).

Source: `E:\code_x\.tmp-aibiandao-editing-red\P10.txt`

```text
这个交付要求与当前能力边界冲突：

- 无论是否存在外部工具，当前流程都不直接剪辑、渲染或导出成片。
- 当前输出契约不包含剪映、Premiere、Resolve 的原生工程文件或三端互转包。
- 可交付的是统一的 Markdown/JSON 制作包、逐镜提示词和 `model_job_manifest`，供外部剪辑师或 API 编排使用。
- 没有可验证工具或 provider 时，只能输出 `Generic fallback` 手动配置任务；它不是可直接执行的剪辑工程，不能冒充已可运行。
- 若要实现三端工程和成片导出，必须接入另一个具备后期剪辑、工程转换与渲染能力的已授权工具链。

请选择：A 先按当前能力交付统一、可校验的上游制作包；还是 B 改由具备剪辑执行与三端工程导出能力的工具链完成？
```
