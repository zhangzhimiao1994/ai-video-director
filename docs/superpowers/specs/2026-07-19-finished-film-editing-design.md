# aibiandao：AI 成片剪辑与多软件交付设计

日期：2026-07-19  
状态：已完成交互设计确认，等待书面规格审核  
目标技能：`aibiandao`

## 1. 背景与目标

`aibiandao` 当前可以交付制片简报、剧本、三层分镜、连续性方案、逐镜提示词和模型任务清单，也会描述剪辑节奏与声音计划。但它没有把生成素材组装为成片所需的素材绑定、逐剪辑点时间线、字幕、混音、调色、软件适配、渲染和验收规则完整物化。

本次扩展要让用户在要求“剪辑”“成片”“直接可用”或“AI 自动剪辑”时，获得两类互相一致的交付：

1. 剪辑师可直接照表操作的逐秒施工方案；
2. 软件或 AI 可读取、验证、转换并在获得操作授权后执行的机器交付。

目标软件包括剪映专业版 / CapCut、Adobe Premiere Pro 和 DaVinci Resolve。实际自动剪辑采用混合模式：FFmpeg / OpenTimelineIO 兼容时间线提供稳定兜底；检测到可靠的软件适配或自动化能力时，才创建或操作对应工程。

## 2. 已批准的产品决策

- 默认同时交付人类剪辑施工表和机器可读时间线。
- 本地素材目录与可灵、Seedance、HappyHorse 等平台生成结果均可作为素材来源。
- 缺失镜头允许用占位卡完成粗剪，但不得进入最终母版。
- 交付分为粗剪、精剪、最终母版和可继续编辑的工程 / 时间线。
- 16:9 与 9:16 使用两条独立时间线；共享故事事实和素材身份，不使用机械居中裁切替代竖版重构。
- FFmpeg / OTIO 是无界面稳定路径；剪映、Premiere、Resolve 是派生适配器。
- 有工具时可以实际组装和导出；没有工具时必须交付完整 AI-ready 剪辑包，不得假装已经渲染。
- 未经官方验证的私有工程格式不得伪造为“可导入”。

## 3. 范围边界

### 3.1 包含

- 素材扫描、探测、命名、绑定和缺失项审计；
- 逐镜素材入点 / 出点、时间线入点 / 出点、剪辑理由和版本记录；
- 硬切、叠化、匹配剪辑、声音桥、隐藏剪辑等转场指令；
- 变速、定格、防抖、缩放、重构和画幅安全区；
- 对白、旁白、环境声、音效、音乐、静默和 lip-sync 分轨；
- 字幕、标题、CTA、法律文字的文字、时间码、样式意图和位置；
- 基础曝光、白平衡、镜间匹配、风格调色与验收目标；
- 16:9 与 9:16 独立时间线；
- 粗剪、精剪、母版、字幕、交换时间线和软件施工包；
- dry-run、操作授权、实际渲染、失败回退和结果验证；
- Premiere、Resolve、剪映和未来 AI 剪辑器的适配交付。

### 3.2 不包含

- 在用户未授权时运行视频 API、剪辑软件、FFmpeg 或导出任务；
- 覆盖原始素材、已有工程或既有母版；
- 逆向工程或伪造剪映 / CapCut 私有草稿格式；
- 在缺少软件、编码器、字体、插件或官方格式证据时声称交付可直接导入；
- 把粗剪占位卡、离线媒体、未授权音乐或未解决版权素材包装为最终母版；
- 自动发布到抖音、TikTok、YouTube 或其他平台。

## 4. 架构

现有十对象生成制作包保持兼容。只有用户要求剪辑、成片、完整交付或 AI 自动剪辑时，才进入成片装配层并增加 `edit_master_plan`。旧的只写剧本、分镜、提示词或任务清单用法不创建该对象。

```text
project_brief / screenplay / storyboard
                    ↓
       shot_prompts / model_job_manifest
                    ↓
 本地素材 + 平台生成结果 + 授权音频 / 字幕资产
                    ↓
       素材探测、shot_id 绑定、占位审计
                    ↓
             edit_master_plan
          ↙           ↓            ↘
   人类施工表      通用执行包      软件适配器
                  FFmpeg / OTIO    Premiere / Resolve / 剪映
                    ↓
       粗剪 → 精剪 → 最终双画幅母版
```

`edit_master_plan` 是唯一可信剪辑源。Markdown 施工表、JSON、CSV、SRT、FFmpeg 脚本、OTIO、FCPXML 和软件说明都由它派生，不允许各自维护不同的镜头顺序、时长或故事事实。

## 5. `edit_master_plan` 数据契约

顶层至少包含：

| 字段 | 约束 |
|---|---|
| `edit_plan_id` | 非空稳定 ID。 |
| `plan_status` | `draft`、`dry_run_passed`、`authorized`、`rendered` 或 `blocked`。 |
| `source_package_id` | 指向生成制作包或其稳定项目 ID。 |
| `media_bindings` | 素材与 `shot_id`、take、fallback、音频和文字资产的绑定。 |
| `timelines` | 恰好包含请求的时间线；电影化双画幅完整交付必须包含 `16:9` 与 `9:16`。 |
| `audio_tracks` | 对白、旁白、环境声、音效、音乐、静默和 lip-sync 分轨。 |
| `text_tracks` | 字幕、标题、CTA、法律文字及其时间码、安全区和语言。 |
| `look_plan` | 镜间匹配、曝光、白平衡、色彩空间、风格意图和验收条件。 |
| `delivery_specs` | 粗剪、精剪、母版、工程和平台导出要求。 |
| `software_targets` | `generic`、`premiere`、`resolve`、`jianying_capcut`、`ai_editor` 的请求与支持状态。 |
| `execution` | dry-run、授权、输出目录、覆盖策略、工具证据与执行结果。 |
| `edit_validation` | 时长、空洞、重叠、离线媒体、占位卡、字幕、音频、色彩、版权和导出审计。 |

### 5.1 素材绑定

每条 `media_binding` 至少包含：

- `asset_id`、`shot_id`、`take_id`、`runtime_role`；
- `source_type`: `local_file`、`provider_result`、`generated_placeholder` 或 `post_asset`；
- `path_or_uri`、`file_status`、`rights_status`；
- `probe_status`、`duration_seconds`、`frame_rate`、`resolution`、`audio_channels`；
- `source_in_seconds`、`source_out_seconds`；
- `selection_reason`、`acceptance_status`、`fallback_asset_id`。

本地素材优先通过文件名中的稳定 `shot_id` / `take_id` 匹配；平台结果通过 job 到 shot 的既有引用匹配。模糊匹配只能成为建议，不能自动设为最终绑定。

### 5.2 独立时间线

每条时间线包含 `timeline_id`、`aspect_ratio`、`resolution`、`frame_rate`、`duration_seconds`、`video_tracks`、`audio_track_refs`、`text_track_refs` 与 `export_refs`。

每个剪辑单元至少包含：

- `edit_unit_id`、`sequence`、`shot_id`、`asset_id`；
- `timeline_in_seconds`、`timeline_out_seconds`、`duration_seconds`；
- `source_in_seconds`、`source_out_seconds`；
- `story_function`、`cut_reason`；
- `transition_in`、`transition_out`；
- `speed`、`freeze_frames`、`stabilization`；
- `reframe`、`safe_area`、`scale`、`position`；
- `opening_state`、`closing_state`、`continuity_ids`；
- `audio_cue_ids`、`text_cue_ids`；
- `look_instruction`、`risk_triggers`、`approval_status`。

16:9 与 9:16 可以使用不同的切点、节奏、镜头选择和空间重构，但不得改变锁定事件、对白含义、因果顺序、人物身份或结局。

## 6. 人类可执行剪辑施工表

施工表每行对应一个 `edit_unit_id`，按时间线顺序输出：

1. 时间线入点、出点和最终时长；
2. 素材文件、`shot_id`、take、fallback 与素材内部入点 / 出点；
3. 当前剪辑动作和叙事理由；
4. 转场类型、持续时间、画面条件和声音桥；
5. 变速、定格、防抖、重构、缩放与位置；
6. 对白、环境声、音效、音乐和目标电平；
7. 字幕、标题、CTA、法律文字及时间码和位置；
8. 曝光、白平衡、镜间色彩匹配和风格目标；
9. 16:9 / 9:16 的专属构图指令；
10. 风险、缺失素材、接受检查和回退路径。

施工表之后必须附上轨道布局、素材目录、字幕表、声音 cue 表、调色表、导出表和最终验收表。不得只写“这里快切”“加电影感音乐”“统一调色”等不可执行形容词。

## 7. 机器交付与软件适配

### 7.1 通用交付

- `edit_master_plan.json`
- `edit_construction_16x9.md` / `.csv`
- `edit_construction_9x16.md` / `.csv`
- `timeline_16x9.otio`
- `timeline_9x16.otio`
- `subtitles_16x9.srt`
- `subtitles_9x16.srt`
- FFmpeg dry-run 报告和可执行脚本
- 素材重命名、目录结构和重链接清单
- `edit_quality_report.md` / `.json`

粗剪只负责故事顺序、基础切点、占位卡和临时声音；精剪使用已选择 take，完成正式切点、转场、双画幅重构、字幕和分轨声音，但允许调色或混音仍是待审状态；最终母版必须移除所有占位卡和离线媒体，并通过最终调色、混音、版权与导出验收。三个版本不得只是同一时间线换文件名。

OTIO / FCPXML 只有在生成器实现了对应公开结构并通过 fixture 测试时才输出为可导入交换文件。否则保留严格 `edit_master_plan.json`、施工表和 `manual_or_unverified` 适配报告，不生成扩展名正确但内容不可用的伪文件。

### 7.2 Premiere Pro

输出经验证的 XML / OTIO 交换文件、视频 / 音频轨道布局、代理媒体策略、字体 / LUT / 插件依赖和重链接说明。无法验证当前版本导入能力时，交付标记为 `manual_or_unverified`，不得声称已导入。

### 7.3 DaVinci Resolve

输出经验证的 FCPXML / OTIO、轨道映射、色彩空间与调色节点说明、Fairlight 音轨映射和重链接说明。实际导入或渲染必须记录 Resolve 版本和验证结果。

### 7.4 剪映专业版 / CapCut

始终输出逐秒施工表、素材排序与重命名、SRT、轨道映射、效果参数、字体 / LUT / 音频依赖和逐步操作清单。只有官方格式证据或当前环境中已验证的自动化能力存在时，才生成或操作工程。

CapCut 官方帮助中心当前说明不支持直接导入第三方剪辑工程，因此首版不得把未经验证的私有草稿 JSON 包装为正式适配器。参考：<https://www.capcut.com/help/how-to-export-pro-project>。

### 7.5 AI 剪辑器

使用严格 JSON 读取 `edit_master_plan`，按依赖顺序执行素材探测、绑定、时间线构建、字幕、声音、调色、导出和验收。每一步记录 `pending`、`running`、`passed`、`failed` 或 `blocked`；失败必须返回最早可修复对象，不得只改最终渲染结果掩盖上游冲突。

首版不在仓库脚本中硬编码剪映、Premiere 或 Resolve 的界面点击流程。若运行时已经提供经验证的软件控制工具，Skill 可在操作授权后调用该工具；否则只生成软件适配包。界面自动化实现留给独立适配层，避免软件版本、语言和布局变化破坏通用剪辑核心。

## 8. 执行状态机与操作授权

现有 Brief、Direction、Screenplay + Storyboard 三道创意审批门保持不变。成片执行使用独立的操作授权，不增加第四道创意审批门。

1. **Compile**：生成 `edit_master_plan`，不运行外部工具。
2. **Dry run**：探测素材和工具，验证绑定、时间线、输出路径和依赖。
3. **Operation authorization**：展示将读取的目录、将创建的文件、版本目录、工具命令、版权阻断和预计输出；只有用户明确授权“执行剪辑”才进入下一步。
4. **Assemble**：创建新版本目录并生成粗剪、精剪、母版或软件交换文件。
5. **Verify**：运行时长、媒体、字幕、音频、色彩、编码和锁定事件验收。
6. **Handoff**：返回实际生成文件、工程、日志、失败项和可恢复步骤。

`one-pass draft` 只能绕过三道创意对话边界，不能授权文件写入、软件操作或渲染。

## 9. 安全与失败恢复

- 原始素材和已有工程只读；每次写入新的版本目录，如 `edit/v003/`。
- 输出目录已存在时必须递增版本或请求用户选择，不得覆盖。
- 缺失镜头使用带 `shot_id`、缺失原因和目标时长的占位卡；占位卡允许粗剪，阻断最终母版。
- 素材损坏、时长不足或帧率不兼容时优先回到 `media_bindings`，不得静默拉伸或截断锁定事件。
- NLE 适配失败时回退到 FFmpeg 成片、OTIO、SRT 和施工表；通用交付不得依赖专用软件成功。
- 软件版本、界面语言、插件或自动化选择器不匹配时停止 UI 自动化，不猜按钮位置。
- 字幕字体缺失时使用明确批准的 fallback 字体并记录替换；法律文字不得自动改写。
- 未授权音乐、声音克隆、真人素材或品牌资产阻断最终母版。
- 未真实完成渲染时，状态只能是 `dry_run_passed`、`authorized` 或 `blocked`，不得写 `rendered`。

## 10. 最终验收

最终母版只有同时满足以下条件才可标记 `ready`：

- 所有用户锁定事件按顺序映射到两条时间线；
- 16:9 与 9:16 的 active duration 分别精确等于目标；
- 无时间线空洞、非法重叠、离线媒体、损坏素材或占位卡；
- 素材入点 / 出点合法，任何变速和转场都计入时长；
- 字幕内容、时间码、编码、可读性和安全区通过；
- 对白、旁白、音乐、环境声、音效和静默均有轨道、来源与验收；
- 响度和峰值满足明确交付规格，不以“听起来正常”代替数值或工具证据；
- 人物、道具、轴线、运动方向、光线和镜间状态连续；
- 色彩空间、分辨率、帧率、编码、码率、音频采样率和声道正确；
- 粗剪、精剪、母版、交换文件、施工表和验证报告都有版本记录；
- 实际输出文件存在且探测结果与声明一致。

## 11. 文件与实现组件

计划新增或修改：

- `SKILL.md`：增加成片请求路由、操作授权、交付与禁止项；
- `references/editing-finish.md`：成片剪辑的完整规范；
- `references/output-contract.md`：增加可选 `edit_master_plan` 映射；
- `scripts/validate_edit_plan.py`：验证剪辑计划；
- `scripts/build_edit_bundle.py`：默认 dry-run，生成施工表、CSV、SRT、FFmpeg 脚本、OTIO / FCPXML 和适配说明；只有显式 `--execute` 且工具证据通过时才渲染；
- `tests/test_editing_finish_docs.py`：路由和文档契约测试；
- `tests/test_validate_edit_plan.py`：验证器单元测试；
- `tests/test_build_edit_bundle.py`：派生产物与 dry-run / execute 边界测试；
- `tests/fixtures/editing/`：完整双画幅、缺失素材、非法重叠、剪映交付等固定样例；
- `test-prompts.json`：增加成片剪辑、缺失素材和多软件 / AI 执行压力场景。

实现不得为首版强制引入第三方 Python 包。FFmpeg / ffprobe、OTIO 库和 NLE 软件均为可选能力；缺失时仍须生成可审阅、可执行的文本 / JSON / 脚本交付。

## 12. 测试策略

### 12.1 RED 基线

修改 Skill 前，用当前版本执行至少三个场景并记录失败：

1. 完整剧本和生成镜头已给出，要求直接交付双画幅成片剪辑包；
2. 本地素材缺一个 `shot_id`，要求先粗剪再出母版；
3. 同时要求剪映、Premiere、Resolve 与 AI 自动剪辑。

预期基线失败包括：只交付提示词 / job、没有素材绑定、没有逐剪辑点时间线、没有操作授权、缺失镜头未阻断最终母版、伪造或过度承诺软件工程格式。

### 12.2 GREEN 文档与行为

- 成片请求必须读取 `references/editing-finish.md`；
- 输出包含人类施工表和 `edit_master_plan`；
- 双画幅时间线独立且锁定事实一致；
- 剪映适配不伪造私有工程；
- 外部执行必须经过 dry-run 和明确操作授权；
- 没有工具时交付 AI-ready 包，不声称已渲染。

### 12.3 验证器与构建器

- 旧十对象生成包测试继续通过；
- 完整双画幅 fixture 通过剪辑验证；
- 空洞、重叠、非法素材边界、时长不等、离线媒体、占位卡母版、字幕越界和未授权音频分别失败；
- dry-run 不启动 FFmpeg 或软件；
- 未传 `--execute` 不创建视频母版；
- 工具缺失时仍生成施工表、JSON、SRT 和执行脚本；
- 派生的 Markdown / CSV / SRT / 时间线与同一 Canon 一致。

### 12.4 端到端

从固定的测试素材或合成色卡生成 16:9 与 9:16 粗剪包。FFmpeg 存在时渲染短测试母版并用 ffprobe 验证；FFmpeg 不存在时验证脚本和阻断状态。任何端到端测试不得依赖网络、付费 API 或专用 NLE 安装。

## 13. 成功标准

- 用户拿到的施工表无需回看 Skill 文档即可逐步剪出成片；
- AI 只读取 `edit_master_plan` 就能确定素材、轨道、切点、效果、导出和验收顺序；
- 两条画幅时间线均可独立渲染且保持锁定剧情；
- 专用软件失败时仍有通用成片与交换文件路径；
- 旧的剧本、分镜、提示词和任务清单用法无行为回归；
- Skill、验证器、构建器和已安装版本通过全部回归测试后才发布。
