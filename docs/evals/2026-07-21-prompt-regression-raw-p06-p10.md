# P06–P10 blind behavior regression raw output

Evaluator input was limited to P06–P10, committed `SKILL.md`, and Skill-routed references. The evaluator was forbidden to read expected results, tests, reports, `results.tsv`, or git history. The following is its complete output.

## P06 raw output

当前不支持把三十万字长篇直接进行全书级“自动拆季并生成第 1 集”；长篇小说模式尚未作为可交付输入模式开放。直接处理会迫使我擅自决定第一季边界、删改主线和集尾钩子。

请指定一个能够独立成集的小说片段或剧本段落，至少包含主角、动机、阻碍、关键行动和结局变化：你希望先处理哪一段？

## P07 raw output

当前不能直接编译 Seedance 提示词。你锁定的两镜存在尚未获得剧情解释的身份与道具连续性冲突，“震撼”不能替代连续性证据。

```yaml
return_to:
  - story/action
  - continuity_bible
  - storyboard
narrative_clarity:
  status: fail
  unresolved_conflicts:
    - 白发少年为何变成红发成年女人尚无可见原因、过程或结果
continuity_integrity:
  status: fail
  unresolved_conflicts:
    - 主角年龄段、性别呈现、发色跨镜漂移
    - 戒指从左手变到右手，且没有交接动作或转场解释
prompt_approval_status: blocked
job_approval_status: non_executable
provider_schema_status: manual_only_until_official_request_schema_is_readable
documented_parameters: {}
requires_manual_configuration:
  - official_schema_access
  - product_or_model_id
  - endpoint
  - authentication
  - generation_mode
  - prompt_field
  - reference_inputs
  - first_last_frame_support
  - audio_support
  - duration
  - aspect
  - resolution
  - all_request_parameters
```

可选修复路径：

- 把变化确认为剧情事件：补充一个可观察的触发、变身过程或转场，以及变身后戒指换手的明确动作；两镜仍可保留现有外观。
- 把变化认定为生成漂移：统一主角的年龄段、性别呈现和发色，并固定戒指持手。

请选择：保留为有因果证据的剧情变身，还是修正为同一人物、同一持手的连续镜头？

## P08 raw output

可以制作，但当前还不能声称已经交付成片或可执行时间线：素材只描述为本地存在，尚未给出可探测路径，因而六个 `shot_id` 的文件状态、时长、帧率、分辨率、音轨、授权和合法入出点都未核实。

```yaml
plan_status: draft
target_duration_seconds: 45
media_bindings: missing_material
requested_timelines:
  - aspect_ratio: "16:9"
    strategy: independent_timeline
  - aspect_ratio: "9:16"
    strategy: independent_recomposition
rendered: false
ready: false
```

素材绑定通过后，交付包将由同一个 `edit_master_plan` 派生，包含：

- 16:9 与 9:16 两条独立 45 秒时间线，不以机械居中裁切代替竖屏重构；
- 每个 edit unit 的时间线入点、出点、时长、源素材入出点、剪切理由、转场、速度、定格、稳定、重构、缩放和位置；
- 逐秒施工表及 Markdown/CSV 版本；
- 字幕表与逐画幅 SRT，含准确文本、时间码、字体回退、安全区和可读性检查；
- 对白、环境、音效、音乐及静默的声音表，含来源、授权、路由、淡入淡出和目标电平；
- 输入/输出色彩空间、曝光、白平衡、镜头匹配、风格意图与验收目标；
- 媒体清单、重链接表、导出矩阵、质量报告和 FFmpeg 命令计划；
- 新建版本目录中的非执行干跑包、完整 manifest、阻塞项和工具状态。

实际剪辑、媒体写入、渲染和导出必须等干跑通过后，再由你对显示出的 manifest 与确切版本目录给出操作授权。

请提供包含 `shot-01` 到 `shot-06` 的本地素材目录绝对路径。

## P09 raw output

可以先做带 `shot-04` 占位卡的粗剪，但不能把含占位卡的版本直接交付为最终母版。

```yaml
rough_cut:
  placeholder:
    shot_id: shot-04
    label: "MISSING: shot-04"
    missing_reason: source_media_absent
    duration: inherit_locked_shot_duration
  allowed: true
  creative_ready: false
  unresolved_items:
    - shot-04 正式素材缺失

final_master:
  status: blocked
  ready: false
  blocker:
    object: media_bindings[shot-04]
    reason: 最终母版禁止占位卡、离线媒体或未验证替代素材
```

粗剪与最终母版必须是两个独立版本。粗剪会保留占位卡和缺失报告；最终母版必须绑定正式 `shot-04`，或绑定一个经批准、保持相同故事功能、事件、时长及首尾状态的替代素材。不能复制、重命名粗剪来冒充最终母版，也不能靠拉长其他镜头隐藏缺失事件。

请选择：补交正式 `shot-04`，还是批准一个保持同一事件与边界状态的替代素材？

## P10 raw output

可以统一交付，但三套软件必须消费同一个剪辑 Canon，不能各自维护一套镜头顺序、字幕时间或调色数据。

| 目标 | 有可验证工具时 | 没有工具或支持未核实时 |
|---|---|---|
| 剪映 / CapCut | 干跑通过并获得绑定 manifest 与确切版本目录的操作授权后，才可自动操作；记录软件版本、步骤和结果 | 交付逐步施工表、排序重命名媒体、SRT、轨道映射、效果参数、字体/LUT/音频依赖；私有工程文件标记 `manual_or_unverified` |
| Premiere Pro | 仅在当前导入格式与自动化能力有证据时生成并验证 XML/OTIO，授权后方可导入、剪辑和导出 | 交付轨道映射、代理策略、重链接、字幕、插件依赖、调色与导出设置；适配器标记 `manual_or_unverified` |
| DaVinci Resolve | 仅在当前 FCPXML/OTIO 或自动化路径验证通过后，授权执行导入、调色、Fairlight 和导出 | 交付轨道与重链接映射、色彩空间、节点说明、Fairlight 路由、字幕和导出设置；不支持项明确阻塞或标记 `manual_or_unverified` |

通用可执行包包含：

- `edit_master_plan.json`
- 每个画幅的施工表 Markdown/CSV
- SRT 与字幕安全区规范
- 音频 cue、总线和目标电平表
- 调色/色彩管理表
- 媒体清单与重链接映射
- FFmpeg 干跑报告及命令计划
- 软件适配报告
- 导出矩阵、验收清单和质量报告
- 包含确切输入、输出、命令、阻塞项、预期产物及版本目录的 dry-run manifest

即使检测到可用 AI 或 NLE 工具，也不会立即写工程、改媒体或导出。必须先探测输入、验证 Canon、生成新版本目录的干跑清单，再由你针对该 manifest 和确切目录明确授权；任何输入、命令、软件目标或目录变化都要重新干跑和授权。

请提供这个项目的素材/工程根目录绝对路径。
