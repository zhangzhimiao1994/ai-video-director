# AI Video Director：输出契约

本参考定义最终 Markdown 制作包与 JSON 制作包的唯一字段映射。两种格式必须表达同一组已批准事实；Markdown 供制片、导演和剪辑审阅，JSON 供校验与后续 API 编排。字段名以 `scripts/validate_package.py` 为准，不得在下游改名。

## 顶层顺序

Markdown 标题与 JSON 顶层键必须严格按以下顺序出现：

1. `project_brief`
2. `creative_directions`
3. `selected_treatment`
4. `story_structure`
5. `screenplay`
6. `continuity_bible`
7. `storyboard`
8. `shot_prompts`
9. `model_job_manifest`
10. `quality_report`

不得添加包裹层，也不得用 `brief`、`treatment`、`shot_list`、`prompts` 或 `jobs` 替换这些键。

## 跨对象不变量

- 每个 `storyboard[].shot_id` 恰好对应一个 canonical `shot_prompts` 记录。
- 每个镜头至少对应一个 `model_job_manifest` 记录；需要参考图准备、主生成、扩展或变体时可对应多个 job。
- 每个 job 必须引用已存在的 `shot_id`，且不得引入已批准 storyboard 中不存在的人物、地点、道具、动作、台词、产品事实或结局。
- legacy-only 包的 `prompt_source` 必须指向该镜唯一的 `universal_prompt_en`，模型差异只能进入 `model_variants` 和 job 的正式映射；电影化包使用下方同时绑定共享锁与画幅方向的对象契约。
- `documented_parameters` 必须是对象，只能包含在当前官方一手文档中核实过的请求字段和值；没有可核实字段时使用空对象。
- `requires_manual_configuration` 必须是数组，逐项列出尚未解析的 provider 字段、项目配置或能力选择；没有未决项时使用空数组。
- `runtime_role` 可为 `active` 或 `fallback`，缺省视为 `active`。只有 active 镜头计入目标时长；fallback 仍须有独立 canonical prompt 和至少一个 job。
- `risk_level: "high"` 必须具有非空 `fallback_shot`。该 ID 必须引用一个风险更低、`runtime_role: "fallback"` 的完整镜头，并逐项保持相同 `sequence`、`duration_seconds`、`scene_id`、`story_function`、`beat_change`、`opening_state`、`closing_state`、`character_ids`、`location_id`、`wardrobe_ids`、`prop_ids`、`look_id`。

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

此时 storyboard 每镜必须包含 `rhythm_role`、`state_dependencies`、非空对象 `state_before`/`state_after`、非空字符串 `composition_16x9`、`recomposition_9x16` 和 `platform_capability_needs`。`state_dependencies` 必须按有效数字 `sequence` 形成只指向更小序号镜头的有向无环图；不得用数组位置推断上游，active 镜头序号不得重复。本镜 `state_before` 必须包含每个依赖镜头 `state_after` 的全部字段并保持对应值相同，可额外包含其他已声明依赖交接的状态。`recomposition_9x16.composition` 是非空字符串，`safe_areas` 是非空数组且每项为非空字符串。

每镜仍只有一个 canonical prompt record 和一个共享 `global_lock_block`，但必须在 `direction_variants` 中分别提供非空 `16:9` 与 `9:16` 导演文本。16:9 文本必须包含 `composition_16x9`，9:16 文本必须包含 `recomposition_9x16.composition`，并且两份文本在两种重构策略下都不得相同。每镜必须有 16:9 与 9:16 job 覆盖，每个电影化 job 使用以下 `prompt_source` 对象，同时引用同镜共享锁和与自身画幅匹配的方向：

```json
{
  "global_lock_source": "shot_prompts[shot_id=SH001].global_lock_block",
  "direction_source": "shot_prompts[shot_id=SH001].direction_variants[9:16]"
}
```

`quality_report.checks.narrative_clarity` 必须逐项记录 `protagonist`、`goal`、`obstacle`、`causality`、`ending_change` 的 `pass` 或 `fail`。`quality_report.checks.continuity_integrity` 必须记录 `status` 与 `unresolved_conflicts`。prompt 的 `approval_status` 为 `draft`、`blocked` 或 `final`；job 的 `approval_status` 为 `blocked`、`non_executable` 或 `approved`。任一硬门失败时，`quality_report.ready` 只能是 `false`，prompt 只能为 `draft`/`blocked`，job 只能为 `blocked`/`non_executable`；硬门通过但 `ready: false` 时也保持这组非最终状态。只有 `ready: true` 且两道硬门通过时，prompt 才能为 `final`、job 才能为 `approved`。

导演摘要、剧本、Canon 与资产圣经、Shot Graph、关键帧、平台包、双画幅方案和质检报告是逻辑交付部分。默认在 Markdown 或十对象 JSON 中表达；只有用户明确要求保存文件时才创建实际目录。

## 1. `project_brief`

Markdown 写“制片简报”；JSON 使用 `project_brief` 对象。至少包含获批状态、正数 `target_duration_seconds`、画幅、平台、目标、期望反应、约束、假设和风险。未经用户批准的事实必须保留草案或假设状态。

## 2. `creative_directions`

Markdown 写“三个创意方向对比”；JSON 使用 `creative_directions` 数组。标准流程恰含三个机制不同的方向，并保留最终选中方向，以便审计选择过程。

## 3. `selected_treatment`

Markdown 写“导演阐述”；JSON 使用 `selected_treatment` 对象。记录选中 `direction_id`、主题或引导问题、表演、画面、剪辑、声音和禁项。不得改名为 `director_treatment`。

## 4. `story_structure`

Markdown 写“故事结构与节拍账本”；JSON 使用 `story_structure` 对象。beat ID、因果、证据和时长必须能映射到 screenplay 与 storyboard。

## 5. `screenplay`

Markdown 写“可审计剧本”；JSON 使用 `screenplay` 对象，并在 `scenes` 中保存稳定 `scene_id`。所有 scene 时长之和必须与目标时长一致。

## 6. `continuity_bible`

Markdown 写“连续性圣经”；JSON 使用 `continuity_bible` 对象，并始终包含 `characters`、`locations`、`wardrobes`、`props`、`looks`、`audio_motifs` 六个数组。每个被 storyboard 引用的 ID 必须在对应数组中存在且唯一。

## 7. `storyboard`

Markdown 写“叙事层、视觉层、生成层三层分镜”；JSON 使用 `storyboard` 数组。每个镜头必须包含验证器定义的全部字段：

`shot_id`、`scene_id`、`sequence`、`duration_seconds`、`story_function`、`beat_change`、`visual_description`、`shot_size`、`camera_angle`、`lens_intent`、`composition`、`camera_movement`、`character_ids`、`location_id`、`wardrobe_ids`、`prop_ids`、`look_id`、`subject_action`、`performance`、`opening_state`、`closing_state`、`continuity_in`、`continuity_out`、`transitions`、`storyboard_frame_prompt`、`generation_strategy`、`risk_level`、`risk_triggers`、`fallback_shot`、`state_snapshot`。

`runtime_role` 与 `audio_motif_ids` 是允许的补充字段。`risk_triggers` 中每项必须包含 `failure_mode`、`acceptance_check`、`fallback_when`；medium/high 风险至少一项。`state_snapshot` 必须包含轴线、视线、位置、道具、服装、时间、天气、光线、污损以及与镜头完全相同的 opening/closing state。不要把旧字段 `sequence_index`、`transition_in`、`transition_out` 混入最终契约。

## 8. `shot_prompts`

Markdown 写“逐镜中文导演意图与英文生成提示”；JSON 使用 `shot_prompts` 数组。每条记录必须包含：

`shot_id`、`director_intent_zh`、`universal_prompt_en`、`negative_prompt_en`、`continuity_anchors`、`reference_requirements`、`audio_guidance`、`model_variants`。

一个 `shot_id` 只能拥有一条 `universal_prompt_en`。不得为每个模型复制并改写一套主提示词。

## 9. `model_job_manifest`

Markdown 写“模型任务清单”；JSON 使用 `model_job_manifest` 数组。每个 job 必须包含：

`job_id`、`shot_id`、`job_purpose`、`model_family`、`generation_mode`、`prompt_source`、`reference_inputs`、`duration_seconds`、`aspect`、`resolution`、`documented_parameters`、`requires_manual_configuration`。

最终键名是 `aspect`，不是 `aspect_ratio`。job 只负责路由与正式参数映射，不负责创作。

## 10. `quality_report`

Markdown 写“质量与未决项报告”；JSON 使用 `quality_report` 对象。至少报告故事因果、时长、ID、连续性、提示词一一对应、job 覆盖、fallback、官方字段核实和未决手动配置。`ready` 只能表示制作包通过当前校验，不代表 API 凭据、配额或平台审核已经完成。

## 五秒香水电梯示例：Markdown

### `project_brief`

标题为 “Five-Second Perfume Lift”，`brief_status: approved`。这是 5 秒、9:16、面向竖屏社交视频的虚构香水广告：用电梯里一次可见变化揭示无品牌香水，让观众感到克制的自信并注意到瓶子。约束是生成画面中不得出现可读品牌文字且无对白；无临时假设。当前风险仅为 provider project、authentication、storage 与 output resolution 尚未配置。

### `creative_directions`

| ID | Logline | 结构 | 标志画面 | 难度 |
|---|---|---|---|---|
| `D1` | 门开启，把等待变成克制的产品揭示 | single reveal | 暖光落到她右手的瓶子 | medium |
| `D2` | 楼层显示倒计时，收束为安静持瓶 | countdown and payoff | 最后一盏楼层灯在瓶子上方熄灭 | low |
| `D3` | 反射先揭示琥珀色瓶子，再揭示主人 | reflection reveal | 琥珀玻璃先在拉丝金属反射中出现 | high |

选择 `D1`。

### `selected_treatment`

`treatment_status: approved`，选择 `D1`。主题是“自信来自克制的显露，而非展示”；戏剧问题是“门打开时，什么发生了变化？”人物从屏息变为缓慢抬眼和肩部放松。视觉语言是冷灰电梯与前方克制暖光相接、稳定构图。声音只有 `CUE01`：sfx 轨，在门开始开启时触发揭示，无口型依赖，后期制作。

### `story_structure`

| Beat | 功能 | 变化 | 时长 |
|---|---|---|---:|
| `B01` | 产品揭示 | 从封闭等待到暖光中的选择 | 5 秒 |

结构为 `single reveal`，目标时长 5 秒。开场是门关闭、女人右手握着带盖瓶子等待；`CUE01` 导致门开始开启，暖光继而显露人物和瓶子，视觉证据是暖光落到她左脸与右手瓶子；关联 `AM01`。回报是“不做销售动作也让瓶子被注意”，结尾是门已开、瓶子仍带盖并留在右手。

### `screenplay`

`screenplay_status: approved`，目标 5 秒。唯一场景 `S01` 的目标是通过到站揭示产品，悬念是“她在等着揭示什么？”开场为门闭、视线向下、右手腰间持带盖瓶；`CUE01` 后她只抬眼一次，门打开，暖光落到左脸与琥珀色瓶。情绪从屏息期待变为克制自信；无对白或旁白。结尾为门开、视线向外、瓶子仍在右手；时长 5 秒，关联 `B01`、`CUE01`、`AM01`，前后均无其他场景因果链接。

### `continuity_bible`

- `C01`：短黑发、左眉上小痣的虚构成年女性。固定短黑发与痣；只允许视线上抬、肩部放松；禁止换脸和头发变长；无参考资产；提示锚点为 `fictional adult woman, short black hair, small mole above the left eyebrow`。
- `L01`：窄小拉丝金属电梯，双门在前，控制面板在画面右侧。固定门与面板方位；只允许门开启；禁止面板换边或门数变化；无参考资产；提示锚点为 `compact brushed-steel lift, double doors ahead, control panel on camera right`。
- `W01`：深蓝哑光开领风衣。只允许自然袖褶；禁止亮面材质或衣领闭合；无参考资产；提示锚点为 `matte navy trench coat with open collar`。
- `P01`：无品牌琥珀色方瓶、黑色瓶盖、右手持握。只允许暖高光在玻璃上移动；禁止可读标签、缺盖或换到左手；无参考资产；提示锚点为 `unbranded square amber perfume bottle with a black cap`。
- `LOOK01`：冷灰电梯内部与从前方进入的克制暖金光，自然肤色。只允许门开时暖光增强；禁止霓虹配色或光线反向；无参考资产；提示锚点为 `cool gray interior, restrained warm golden light entering from ahead`。
- `AM01`：低沉机械电梯底声在一次柔和到站提示音后停止。只允许提示音后短暂近静默；禁止对白或警报；无参考资产；提示锚点为 `low lift hum ending after a soft arrival cue`。

### `storyboard`

叙事层：`SH001`，`runtime_role: active`，对应 `S01`，序号 1，时长 5 秒。故事功能是借门开启揭示香水，beat 变化是“封闭等待变成克制暖光揭示”。人物在右三分之一等待；提示音后只抬眼一次，同时门开启，暖光落到脸与瓶。人物的唯一主动作是抬眼；门开启是环境事件。表演从屏息低头到缓慢抬眼、肩部放松，无对白。

视觉层：胸口高度平视中景，镜头需同时读清脸、右手、瓶与门；机位位于人物—门轴线右侧，中性透视、中等景深。人物在右三分之一、门缝居中、瓶在下方安全区；`camera_movement: locked_off`。引用 `C01`、`L01`、`W01`、`P01`、`LOOK01`、`AM01`。开场为门全闭、C01 在右三分之一、P01 带盖置于右手腰间、冷灰顶光；结尾为门全开、人物位置不变、P01 仍带盖在右手、暖光落到左脸和瓶。入镜连续性固定五类 ID 与右手带盖状态，出镜固定向门外视线、右手瓶与前方暖光；入转场是持续底声上的硬切，出转场在门全开后切走。

生成层：storyboard frame 为“拉丝金属窄电梯内中景，短黑发虚构成年女性穿深蓝哑光风衣站右三分之一，右手持无品牌带黑盖琥珀色方瓶，双门在前打开，克制暖金光落到左脸，胸口高度平视、中性透视、无可读文字”。采用文生视频、固定机位和一次开门动作，精确标签后期合成。风险 `medium`；失败模式是开门时瓶子换手、复制或丢盖；验收是首尾始终只有一个带盖 P01 留在 C01 右手；连续两次失败即返回 storyboard review，申请批准低风险插镜。当前 `fallback_shot: null`，因为未批准任何替代镜头。

状态快照：C01 从画面右侧面向中央门，视线从下方门缝抬到正前；身体始终在右三分之一。P01 状态为 `right/cap_closed`，W01 状态为 `clean_open_collar`；时间 `morning`、天气 `clear`、无污损；门内冷顶光，门开后暖光从前方进入。快照的 opening/closing state 与本镜头首尾状态逐字一致。

### `shot_prompts`

**`shot_id`**：`SH001`

**`director_intent_zh`**：用电梯门一次开启，把封闭等待转成克制的产品揭示。观众先看见人物抬眼，再看见暖光中的右手香水瓶；机位全程固定。

**`universal_prompt_en`**

```text
A fictional adult woman with short black hair and a small mole above her left eyebrow wears a matte navy trench coat with an open collar and holds one unbranded square amber perfume bottle with a black cap at her waist in her right hand, inside a compact brushed-steel lift with double doors ahead and the control panel on camera right. After one soft arrival cue, she slowly raises her eyes as the double doors open once; her held breath releases and her shoulders relax without speech. Medium shot from chest height, eye level, neutral perspective, the woman on the right third, the door seam centered, and the bottle inside the lower safe area. Locked-off camera. Cool gray top light inside is joined by restrained warm golden light entering from ahead. The shot starts with the doors fully closed, her gaze lowered, and the capped bottle at her waist in her right hand; it ends with the doors fully open, her gaze outward, and warm light reaching her left cheek and the same capped bottle. Maintain the same face, hair, navy coat, right-hand bottle grip, door layout, control-panel side, clear morning, and light direction. Keep all exact label text for post-production.
```

**`negative_prompt_en`**

```text
Anatomy: extra fingers, fused hands, distorted face. Duplication: duplicate woman, duplicate bottle. Identity drift: changed face, changed hair length, coat color shift. Unwanted text: readable label, random subtitles, watermark. Unwanted camera behavior: shake, orbit, zoom, focus pumping. Continuity breaks: bottle in left hand, missing cap, reversed doors, control panel changing sides, warm light reversing direction.
```

**`continuity_anchors`**：character `C01`；wardrobe `W01`；P01 在右手且瓶盖闭合；location `L01`；look `LOOK01`；audio motif `AM01`；首尾状态分别引用 `storyboard.SH001.opening_state` 与 `storyboard.SH001.closing_state`。

**`reference_requirements`**：空数组；本示例使用文生视频，身份、产品与地点均由 bible 锚点约束。

**`audio_guidance`**：无对白、旁白、音乐或口型；低沉电梯底声；门开始打开时一次柔和提示音；门完全打开后短暂近静默；音频走后期制作。

**`model_variants`**：仅一项 `veo-2.0-generate-001`；`universal_prompt_en` 原样映射为 instance prompt；不使用 reference mapping；精确项目分辨率未核实；`project_id`、`authentication`、`storageUri`、`resolution` 进入 `requires_manual_configuration`。

### `model_job_manifest`

`JOB-SH001-01` 为 `SH001` 生成不改变已批准镜头的 active final clip。模型为 `veo-2.0-generate-001`，模式 text-to-video，`prompt_source` 精确引用 `shot_prompts[shot_id=SH001].universal_prompt_en`，`reference_inputs` 为空，时长 5 秒、画幅 9:16，`resolution: unresolved`。已核实并写入的请求字段只有 `durationSeconds: 5`、`aspectRatio: 9:16`、`sampleCount: 1`；`project_id`、`authentication`、`storageUri`、`resolution` 必须手动配置。

### `quality_report`

`ready: true`，状态为 `valid_package_pending_provider_configuration`：制作包本身已通过校验，但 provider 配置未完成。故事因果、连续性 ID、一镜一主动作、一镜一个 canonical prompt、每镜至少一个 job、job 不增加事实、官方参数审计均通过，active runtime 为 5 秒。fallback 审计结果为 `not_required_no_high_risk_shots`。未决字段为 `project_id`、`authentication`、`storageUri`、`resolution`。

## 五秒香水电梯示例：完整 JSON

以下对象可以原样复制到 UTF-8 JSON 文件，并由 `scripts/validate_package.py` 校验。

```json
{
  "project_brief": {
    "title": "Five-Second Perfume Lift",
    "brief_status": "approved",
    "target_duration_seconds": 5,
    "aspect_ratio": "9:16",
    "platform": "vertical social video",
    "objective": "Reveal an unbranded perfume through one visible change in the lift.",
    "desired_response": "The viewer reads restrained confidence and notices the bottle.",
    "constraints": ["No readable brand text in generated pixels", "No dialogue"],
    "assumptions": [],
    "risks": ["Provider project, authentication, storage, and output resolution are not configured"]
  },
  "creative_directions": [
    {
      "direction_id": "D1",
      "logline": "The opening lift doors turn waiting into a restrained product reveal.",
      "story_structure": "single reveal",
      "signature_image": "Warm light reaches the bottle in her right hand",
      "difficulty": "medium"
    },
    {
      "direction_id": "D2",
      "logline": "A floor indicator countdown resolves in a quiet product hold.",
      "story_structure": "countdown and payoff",
      "signature_image": "The final indicator goes dark above the bottle",
      "difficulty": "low"
    },
    {
      "direction_id": "D3",
      "logline": "A reflection reveals the amber bottle before it reveals its owner.",
      "story_structure": "reflection reveal",
      "signature_image": "Amber glass appears first in brushed metal reflection",
      "difficulty": "high"
    }
  ],
  "selected_treatment": {
    "treatment_status": "approved",
    "direction_id": "D1",
    "theme": "Confidence is revealed through restraint, not display.",
    "dramatic_question": "What changes when the doors open?",
    "performance": "Held breath becomes a slow upward glance and relaxed shoulders.",
    "visual_language": "Cool gray lift interior joined by restrained warm light; stable framing.",
    "sound_plan": [
      {
        "cue_id": "CUE01",
        "track": "sfx",
        "timing_or_trigger": "The lift doors begin opening",
        "story_function": "Trigger the reveal",
        "lip_sync_dependency": "none",
        "source_status": "post-production"
      }
    ]
  },
  "story_structure": {
    "structure_type": "single reveal",
    "target_duration_seconds": 5,
    "opening_state": "The lift doors are closed and the woman waits with the capped bottle in her right hand.",
    "beats": [
      {
        "beat_id": "B01",
        "function": "reveal",
        "change": "Closed waiting becomes a warm product reveal.",
        "cause": "The arrival cue starts the doors opening.",
        "effect": "Warm light reveals the poised woman and bottle.",
        "visual_evidence": "The doors open and warm light reaches her left cheek and right-hand bottle.",
        "duration_seconds": 5,
        "cue_ids": ["CUE01"],
        "audio_motif_id": "AM01"
      }
    ],
    "payoff": "The bottle is noticed without a sales gesture.",
    "closing_state": "The doors are open; the bottle remains capped in her right hand under warm light."
  },
  "screenplay": {
    "screenplay_status": "approved",
    "target_duration_seconds": 5,
    "scenes": [
      {
        "scene_id": "S01",
        "objective": "Reveal the product through the lift arrival.",
        "conflict_or_question": "What is she waiting to reveal?",
        "action": "After the arrival cue, she raises her eyes once as the doors open.",
        "dialogue_or_narration": null,
        "emotional_change": "Held anticipation becomes restrained confidence when the doors open.",
        "visual_evidence": "Warm light reaches her face and the amber bottle.",
        "opening_state": "Doors closed; gaze lowered; capped bottle at waist in right hand.",
        "closing_state": "Doors open; gaze outward; capped bottle still in right hand.",
        "duration_seconds": 5,
        "causal_link_from_previous": null,
        "causal_link_to_next": null,
        "beat_ids": ["B01"],
        "cue_ids": ["CUE01"],
        "audio_motif_id": "AM01"
      }
    ]
  },
  "continuity_bible": {
    "characters": [
      {
        "character_id": "C01",
        "canonical_description": "Fictional adult woman with short black hair and a small mole above her left eyebrow.",
        "fixed_attributes": ["short black hair", "small mole above left eyebrow"],
        "allowed_variations": ["gaze rises", "shoulders relax"],
        "forbidden_variations": ["face change", "hair length change"],
        "reference_assets": [],
        "prompt_anchors": ["fictional adult woman, short black hair, small mole above the left eyebrow"]
      }
    ],
    "locations": [
      {
        "location_id": "L01",
        "canonical_description": "Compact brushed-steel lift with double doors ahead and a control panel on camera right.",
        "fixed_attributes": ["double doors ahead", "control panel on camera right"],
        "allowed_variations": ["doors open"],
        "forbidden_variations": ["panel changes side", "door count changes"],
        "reference_assets": [],
        "prompt_anchors": ["compact brushed-steel lift, double doors ahead, control panel on camera right"]
      }
    ],
    "wardrobes": [
      {
        "wardrobe_id": "W01",
        "canonical_description": "Matte navy trench coat with open collar.",
        "fixed_attributes": ["matte navy", "open collar"],
        "allowed_variations": ["natural sleeve folds"],
        "forbidden_variations": ["glossy fabric", "closed collar"],
        "reference_assets": [],
        "prompt_anchors": ["matte navy trench coat with open collar"]
      }
    ],
    "props": [
      {
        "prop_id": "P01",
        "canonical_description": "Unbranded square amber perfume bottle with a black cap.",
        "fixed_attributes": ["square amber glass", "black cap", "right-hand hold"],
        "allowed_variations": ["warm highlight moves across glass"],
        "forbidden_variations": ["readable label", "missing cap", "left-hand hold"],
        "reference_assets": [],
        "prompt_anchors": ["unbranded square amber perfume bottle with a black cap"]
      }
    ],
    "looks": [
      {
        "look_id": "LOOK01",
        "canonical_description": "Cool gray lift interior joined by restrained warm golden light from ahead.",
        "fixed_attributes": ["cool gray interior", "natural skin tone", "warm light from ahead"],
        "allowed_variations": ["warm light grows as doors open"],
        "forbidden_variations": ["neon palette", "light reverses direction"],
        "reference_assets": [],
        "prompt_anchors": ["cool gray interior, restrained warm golden light entering from ahead"]
      }
    ],
    "audio_motifs": [
      {
        "audio_motif_id": "AM01",
        "canonical_description": "Low lift hum ends after one soft arrival cue.",
        "fixed_attributes": ["low mechanical hum", "one soft arrival cue"],
        "allowed_variations": ["brief near-silence after the cue"],
        "forbidden_variations": ["dialogue", "alarm"],
        "reference_assets": [],
        "prompt_anchors": ["low lift hum ending after a soft arrival cue"]
      }
    ]
  },
  "storyboard": [
    {
      "shot_id": "SH001",
      "runtime_role": "active",
      "scene_id": "S01",
      "sequence": 1,
      "duration_seconds": 5,
      "story_function": "Reveal the perfume through the opening lift doors.",
      "beat_change": "Closed waiting becomes a restrained warm reveal.",
      "visual_description": "The woman waits on the right third; after the arrival cue she raises her eyes once while the doors open and warm light reaches her face and bottle.",
      "shot_size": "medium shot showing face, right hand, bottle, and doors",
      "camera_angle": "chest-height eye level from the right side of the woman-door axis",
      "lens_intent": "neutral perspective with readable lift geography and moderate depth of field",
      "composition": "woman on right third, door seam centered, bottle inside lower safe area",
      "camera_movement": "locked_off; the opening doors and light perform the reveal",
      "character_ids": ["C01"],
      "location_id": "L01",
      "wardrobe_ids": ["W01"],
      "prop_ids": ["P01"],
      "look_id": "LOOK01",
      "audio_motif_ids": ["AM01"],
      "subject_action": "She raises her eyes once as the double doors open.",
      "performance": "Begin with held breath and lowered gaze; raise the eyes slowly and relax the shoulders without speaking.",
      "opening_state": "Doors fully closed; C01 on right third; P01 capped at waist in her right hand; cool gray top light.",
      "closing_state": "Doors fully open; C01 remains on right third; P01 capped in her right hand; warm light reaches her left cheek and bottle.",
      "continuity_in": "C01, W01, P01, L01, and LOOK01 begin clean and established; P01 is capped in the right hand.",
      "continuity_out": "C01 looks through the open doors; P01 remains capped in the right hand; warm light continues from ahead.",
      "transitions": {
        "in": "hard cut under continuous lift hum",
        "out": "cut after the doors reach fully open"
      },
      "storyboard_frame_prompt": "Medium shot inside a compact brushed-steel lift, fictional adult woman with short black hair in a matte navy trench coat on the right third, holding one unbranded square amber perfume bottle with black cap in her right hand, double doors open ahead, restrained warm golden light on her left cheek, chest-height eye-level camera, neutral perspective, no readable text.",
      "generation_strategy": "text-to-video; keep exact label text for post-production; use one locked camera and one door-opening action",
      "risk_level": "medium",
      "risk_triggers": [
        {
          "failure_mode": "The bottle changes hands, duplicates, or loses its cap while the doors open.",
          "acceptance_check": "Exactly one capped P01 remains in C01's right hand from first to last frame.",
          "fallback_when": "Return to storyboard review and request approval for a lower-risk insert if two consecutive generations fail this check."
        }
      ],
      "fallback_shot": null,
      "state_snapshot": {
        "screen_direction": "C01 faces from camera right toward the centered doors",
        "eye_line": "from lowered door seam to straight ahead",
        "body_position": "standing on the right third",
        "carried_props": [{"prop_id": "P01", "hand": "right", "state": "cap_closed"}],
        "wardrobe_state": [{"wardrobe_id": "W01", "state": "clean_open_collar"}],
        "time": "morning",
        "weather": "clear",
        "light_direction": "cool top light inside; warm light from ahead after doors open",
        "damage_or_dirt": "none",
        "opening_state": "Doors fully closed; C01 on right third; P01 capped at waist in her right hand; cool gray top light.",
        "closing_state": "Doors fully open; C01 remains on right third; P01 capped in her right hand; warm light reaches her left cheek and bottle."
      }
    }
  ],
  "shot_prompts": [
    {
      "shot_id": "SH001",
      "director_intent_zh": "用电梯门一次开启，把封闭等待转成克制的产品揭示。观众先看见人物抬眼，再看见暖光中的右手香水瓶；机位全程固定。",
      "universal_prompt_en": "A fictional adult woman with short black hair and a small mole above her left eyebrow wears a matte navy trench coat with an open collar and holds one unbranded square amber perfume bottle with a black cap at her waist in her right hand, inside a compact brushed-steel lift with double doors ahead and the control panel on camera right. After one soft arrival cue, she slowly raises her eyes as the double doors open once; her held breath releases and her shoulders relax without speech. Medium shot from chest height, eye level, neutral perspective, the woman on the right third, the door seam centered, and the bottle inside the lower safe area. Locked-off camera. Cool gray top light inside is joined by restrained warm golden light entering from ahead. The shot starts with the doors fully closed, her gaze lowered, and the capped bottle at her waist in her right hand; it ends with the doors fully open, her gaze outward, and warm light reaching her left cheek and the same capped bottle. Maintain the same face, hair, navy coat, right-hand bottle grip, door layout, control-panel side, clear morning, and light direction. Keep all exact label text for post-production.",
      "negative_prompt_en": "Anatomy: extra fingers, fused hands, distorted face. Duplication: duplicate woman, duplicate bottle. Identity drift: changed face, changed hair length, coat color shift. Unwanted text: readable label, random subtitles, watermark. Unwanted camera behavior: shake, orbit, zoom, focus pumping. Continuity breaks: bottle in left hand, missing cap, reversed doors, control panel changing sides, warm light reversing direction.",
      "continuity_anchors": {
        "character_ids": ["C01"],
        "wardrobe_ids": ["W01"],
        "prop_states": [{"prop_id": "P01", "hand": "right", "state": "cap_closed"}],
        "location_id": "L01",
        "look_id": "LOOK01",
        "audio_motif_ids": ["AM01"],
        "opening_state_source": "storyboard.SH001.opening_state",
        "closing_state_handoff": "storyboard.SH001.closing_state"
      },
      "reference_requirements": [],
      "audio_guidance": {
        "production_dialogue": null,
        "narration": null,
        "ambience": "low lift hum",
        "sfx": "one soft arrival cue as doors begin opening",
        "music": null,
        "silence": "brief near-silence after doors open",
        "lip_sync": "none",
        "delivery_path": "post-production"
      },
      "model_variants": [
        {
          "model_family": "veo-2.0-generate-001",
          "prompt_adaptation": "Use universal_prompt_en unchanged as the instance prompt.",
          "supported_reference_mapping": [],
          "unsupported_or_unverified": ["exact output resolution for this project"],
          "requires_manual_configuration": ["project_id", "authentication", "storageUri", "resolution"]
        }
      ]
    }
  ],
  "model_job_manifest": [
    {
      "job_id": "JOB-SH001-01",
      "shot_id": "SH001",
      "job_purpose": "Generate the active final clip without changing the approved shot.",
      "model_family": "veo-2.0-generate-001",
      "generation_mode": "text-to-video",
      "prompt_source": "shot_prompts[shot_id=SH001].universal_prompt_en",
      "reference_inputs": [],
      "duration_seconds": 5,
      "aspect": "9:16",
      "resolution": "unresolved",
      "documented_parameters": {
        "durationSeconds": 5,
        "aspectRatio": "9:16",
        "sampleCount": 1
      },
      "requires_manual_configuration": ["project_id", "authentication", "storageUri", "resolution"]
    }
  ],
  "quality_report": {
    "ready": true,
    "status": "valid_package_pending_provider_configuration",
    "checks": {
      "story_causality": "pass",
      "active_runtime_seconds": 5,
      "continuity_ids": "pass",
      "one_primary_action_per_shot": "pass",
      "one_canonical_prompt_per_shot": "pass",
      "at_least_one_job_per_shot": "pass",
      "job_adds_no_story_facts": "pass",
      "official_parameter_audit": "pass",
      "fallback_audit": "not_required_no_high_risk_shots"
    },
    "unresolved_provider_fields": ["project_id", "authentication", "storageUri", "resolution"]
  }
}
```

## 交付与校验

1. 先核对 Markdown 与 JSON 的十个顶层部分是否一一对应。
2. 将完整 JSON 保存为 UTF-8 文件。
3. 运行 `python scripts/validate_package.py <package.json>`。
4. 若结构校验通过，再人工核对故事因果、视觉连续性、官方字段来源、授权和 provider 手动配置。
5. 只有校验与人工审阅都通过，才把 job 交给外部 API 编排；本 Skill 自身不调用 API。

## Optional Finished-Film Extension

The legacy ten-object package remains valid without editing objects. When finished-film delivery is requested, Markdown and JSON add one optional `edit_master_plan`; every construction sheet, CSV, SRT, OTIO, FCPXML, FFmpeg plan, and NLE handoff is derived from the same edit Canon.

`edit_master_plan` contains `edit_plan_id`, `plan_status`, `source_package_id`, `target_duration_seconds`, `locked_event_ids`, `media_bindings`, `timelines`, `audio_tracks`, `text_tracks`, `look_plan`, `delivery_specs`, `software_targets`, `execution`, and `edit_validation`.
