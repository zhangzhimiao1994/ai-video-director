# AI Video Director：连续性与三层分镜

本参考把已批准的 `selected_treatment`、`story_structure` 与 `screenplay` 转成顶层 `continuity_bible` 和 `storyboard`。它负责镜头设计与连续性，不改写已批准的故事事实，也不写厂商专用参数。逐镜提示词由 `prompt-compiler.md` 编译。

## 目录

- [阶段边界](#阶段边界)
- [稳定 ID](#稳定-id)
- [连续性圣经](#连续性圣经)
- [逐镜状态](#逐镜状态)
- [三层分镜](#三层分镜)
- [Storyboard 字段契约](#storyboard-字段契约)
- [完整分镜表](#完整分镜表)
- [镜头拆分规则](#镜头拆分规则)
- [连续性规则](#连续性规则)
- [时长与替代镜头](#时长与替代镜头)
- [工作流程](#工作流程)
- [可解析示例](#可解析示例)
- [交接检查](#交接检查)

## 阶段边界

进入本阶段前，确认：

- 标准流程中简报时长与画幅已确认；`one-pass draft` 可使用未批准、可逆且附影响说明的暂定正数时长与暂定画幅，但不得据此进入执行编译；
- 创意方向已选择，或明确标记为 `one-pass draft`；
- 剧本拥有稳定 scene、beat、character、location、cue 与 audio motif ID；
- 未解决的授权、真人、口型、精确文字和模型能力风险已显式记录。

本阶段只新增两个顶层对象：

- `continuity_bible`：跨镜头不能漂移的事实与允许变化；
- `storyboard`：按剪辑顺序排列的镜头记录。

不得在分镜中新增人物关系、产品功能、对白、结局、品牌主张或其他未获批准的故事事实。若镜头需要新事实，退回故事阶段；不要把它偷偷写进提示词。

## 稳定 ID

ID 一经进入下游引用，不因排序、改名或文案润色而变化。

| 对象 | 格式示例 | 规则 |
|---|---|---|
| scene | `S01` | 继承 `screenplay.scenes[].scene_id`。 |
| beat | `B01` | 继承 `story_structure.beats[].beat_id`。 |
| character | `C01` | 一名角色一个 ID；服装变化不新建角色。 |
| location | `L01` | 同一可辨空间一个 ID；无法连续的空间变化新建地点。 |
| wardrobe | `W01` | 一套可见服装状态一个 ID。 |
| prop | `P01` | 需要跟踪状态或接触的道具一个 ID。 |
| look | `LOOK01` | 一套全局视觉规则一个 ID。 |
| audio motif | `AM01` | 一个可复现的声音母题一个 ID。 |
| shot | `SH001` | 每个候选镜头唯一；不得按模型任务重编号。 |

删除对象时保留变更记录，不复用旧 ID。所有引用先建对象再引用，禁止使用“上个角色”“同一地点”等隐式指代代替 ID。

## 连续性圣经

顶层 `continuity_bible` 必须包含 `characters`、`locations`、`wardrobes`、`props`、`looks`、`audio_motifs` 六个数组。每项都使用以下语义字段：

| 字段 | 要求 |
|---|---|
| 稳定 ID | 使用该集合对应的 `character_id`、`location_id`、`wardrobe_id`、`prop_id`、`look_id` 或 `audio_motif_id`。 |
| `canonical_description` | 写可观察、可复现的基准描述。 |
| `fixed_attributes` | 全片不得无因改变的身份、结构、材质、方位、色彩或声音特征。 |
| `allowed_variations` | 仅列故事允许的表情、姿态、磨损、光线或编曲变化。 |
| `forbidden_variations` | 明确最常见的漂移和错误替换。 |
| `reference_assets` | 使用稳定 `reference_id`、文件角色与授权状态；没有就用空数组。 |
| `prompt_anchors` | 提供可直接继承到英文提示词的短锚点；不写厂商语法。 |

### `characters`

补充角色年龄段、体态、脸部可见特征、发型、左右侧辨识点、动作习惯与授权状态。禁止用族群刻板印象代替可见描述。真人参考必须与 `rights_and_consents` 对齐。

电影化角色在 `identity_profile` 中使用验证器契约：`identity_profile_id`、`approval_status`、`face_anchors`、`body_anchors`、`hair_anchors`、`fixed_accessories`、`signature_effect_anchors`、`reference_asset_ids`、`forbidden_drift`。这些锚点分别锁脸、体型、发型、固定配饰、标志特效和已授权参考图；每个列表必须非空。A concept draft may draft identity upstream for reversible planning, but a production cinematic package accepted by `validate_package` requires `approval_status: approved`. An unapproved profile may keep a job binding pending, but that job cannot be `approved`;脸、体型、发型、配饰或标志特效漂移必须阻塞相关镜头、job 与 edit unit。

### `locations`

记录入口、出口、窗、桌、走廊、光源和角色活动区的相对位置。使用简短平面关系，例如“电梯门在北墙，角色面向北，右侧是控制面板”。

### `wardrobes`

记录每件主服装的颜色、剪裁、材质、开合、袖口、鞋履和损伤状态；与 character 分离，便于剧情内换装。

### `props`

记录尺寸、材质、颜色、持有人、左右手、朝向、开合、液位、损伤与是否需要精确文字后期合成。

### `looks`

记录画幅安全区、对比度、黑位、肤色原则、主辅色、颗粒、光源方向与允许的故事性变化。继承 `selected_treatment.visual_reference_attributes` 和 `weather_time_of_day`，不复制被禁止的参考属性。

### `audio_motifs`

记录母题的音色、节奏、空间、触发条件、允许变奏、禁用声音和对应 cue ID。它是连续性锚点，不等于最终混音文件。

## 逐镜状态

在设计镜头前建立 `state_snapshot`，至少记录：

- `screen_direction`：角色或主体在画面中朝左、朝右、靠近或远离；
- `eye_line`：角色看向哪个 ID、画外哪个方向或镜头轴哪一侧；
- `body_position`：站、坐、转身角度、画面区域与相对距离；
- `carried_props`：道具 ID、左右手、握持点、开合与朝向；
- `wardrobe_state`：服装 ID、穿着方式、褶皱、湿度、污损；
- `time`、`weather`、`light_direction`：时段、天气、主光来向和变化原因；
- `damage_or_dirt`：人物、服装、地点、道具的累积状态；
- `opening_state`：该镜第一帧可验证的状态；
- `closing_state`：该镜最后一帧可验证的状态。

相邻镜头必须满足：前镜 `closing_state` 能成为后镜 `opening_state`，或由明确转场解释差异。不要用“保持一致”代替具体状态。

### 电影化 Shot Graph 扩展

仅当 `project_brief.cinematic_mode` 存在时，每个镜头增加：

- `rhythm_role`：`world_building`、`performance`、`reaction`、`insert`、`hero`、`suspense` 或 `transition`。
- `state_dependencies`：本镜状态依赖的上游 `shot_id` 数组；上游按经过类型校验的数字 `sequence` 判断，只允许引用 `sequence` 更小的镜头，不按 storyboard 数组位置判断。不得引用自身、未知或相同/更大序号的镜头，active 镜头不得重复有效序号；所有依赖合起来必须是有向无环图。
- `state_before`、`state_after`：非空对象，分别记录进入本镜前与离开本镜后的可比较 Canon 状态。每条依赖都要求下游 `state_before` 包含上游 `state_after` 的全部字段且对应值相同；缺失或值不同就是依赖交接冲突，必须在编译前修复。下游可以补充来自其他已声明依赖的状态字段。
- `composition_16x9`：非空字符串，记录电影母版构图、人物调度和前中后景关系。
- `recomposition_9x16`：包含 `strategy`、`composition`、`safe_areas`；`strategy` 只能为 `recompose` 或 `independent_generation`，`composition` 必须为非空字符串，`safe_areas` 必须为非空的字符串数组且每项非空。
- `platform_capability_needs`：实现该镜所需的参考图、首帧、尾帧、音频或编辑能力，不在此映射厂商字段。
- `coverage_role`：本镜可承担一个或多个导演覆盖角色，完整枚举只有 `setup`、`anticipation`、`action`、`impact`、`reaction`、`consequence`、`transition`、`aftermath`。关键事件至少让 `action`、`reaction`、`consequence` 能追溯到实际镜头；其他角色按题材和节奏使用，不要求每个事件机械凑齐八类。
- `kinetic_profile`：逐镜声明 `subject_motion`、`performance_change`、`camera_motion`、`environment_motion`、`motion_layers_required`、`intentional_hold`、`hold_reason`、`acceptance_evidence`。前四项分别描述主体路径、表演状态变化、摄影机运动和环境响应；`motion_layers_required` 声明验收所需层，不把粒子或背景运动当成主体/表演证据；`acceptance_evidence` 是未来成片应观察到的证据目标，不是已完成验收的声明。`intentional_hold: true` 时不按固定秒数误杀，但 `hold_reason` 与 `acceptance_evidence` 必须非空。
- `transition_contract`：每个镜头边界只声明 `type`、`visual_precondition`、`incoming_match`、`duration_frames`、`audio_bridge_cue_id`、`story_reason`、`fallback`。`incoming_match` 说明下一镜如何接住画面、动作或状态，`duration_frames` 是目标帧数；hard cut 可为 0 帧，只要动机与前提明确。

The `storyboard declaration layer` states intent and acceptance targets only. It must not claim that an edit or rendered film already fulfilled them. The `editing fulfillment layer` owns `fulfillment_status` and `evidence_refs` after the boundary is implemented and reviewed; these fields are not part of the storyboard `transition_contract`. 若目标 NLE 不支持原转场，剪辑层必须采用已声明 `fallback` 并重新 dry-run，不得把所有边界默认为硬切。由动作、状态或声音动机支持的 hard cut 仍可通过。

两种画幅共享 `story_function`、角色 ID、事件、对白意义、`opening_state`、`closing_state`、`state_before` 和 `state_after`。16:9 导演文本必须包含 `composition_16x9`，9:16 导演文本必须包含 `recomposition_9x16.composition`；无论策略是 `recompose` 还是 `independent_generation`，两份文本都必须不同。9:16 不得写成对 16:9 的机械裁切。完整制作包必须为每个镜头和每个 `delivery_aspects` 值生成可追踪 job。

## 三层分镜

每个 `shot_id` 只代表一个剪辑单元，同时从三层描述同一个镜头。

### 叙事层

回答“为什么必须有这镜”：

- `story_function`：这镜承担 Hook、阻力、证据、转折、回报或 CTA 中哪一项；
- `beat_change`：镜头开始到结束，知识、目标、情绪、关系或物理状态改变什么；
- `opening_state` 与 `closing_state`：让变化可核对；
- 删除测试：删掉后若因果、理解或回报不受影响，删除或合并该镜。

### 视觉层

回答“观众如何看见变化”：

- `visual_description`、`shot_size`、`camera_angle`、`lens_intent`、`composition`；
- 一次有动机的 `camera_movement`，或明确 `locked_off`；
- `subject_action` 与 `performance`；
- character、location、wardrobe、prop、look ID；
- 轴线、视线、画面方向、地理、时段、天气与光线；
- `transitions`、`continuity_in`、`continuity_out`；
- `storyboard_frame_prompt`：描述代表性静帧，不混入时间性运镜指令。

### 生成层

回答“如何稳定生成与替换”：

完整生成层是 `storyboard`、`shot_prompts` 与 `model_job_manifest` 按 `shot_id` 联合后的视图，必须同时覆盖中文导演意图、英文正/负提示词、连续性锚点、参考与首尾帧、声音/口型、duration、aspect、resolution、strategy 和 risk/fallback。aspect 与 resolution 继承已批准简报或进入 `requires_manual_configuration`；不得猜厂商值。

- `generation_strategy`：文生视频、图生视频、首帧、首尾帧、分层合成或后期文字；
- `risk_level`：`low`、`medium` 或 `high`；`risk_triggers` 用结构化对象写具体失败模式、验收检查和切换 fallback 的条件；
- `fallback_shot`：高风险时引用低风险替代镜头 ID；低、中风险可为 `null`；
- 参考资产、首尾帧、声音与口型依赖在后续 `shot_prompts` 中展开；
- 不在本阶段写未核实的厂商参数。

## `storyboard` 字段契约

每个镜头必须包含验证器要求的全部字段：

| 字段 | 要求 |
|---|---|
| `shot_id` | 稳定唯一 ID。 |
| `scene_id` | 引用剧本 scene。 |
| `sequence` | 激活剪辑中的连续整数，从 1 开始；fallback 镜头保留其替换位置序号但不参与连续性计算。 |
| `duration_seconds` | 正有限数；激活镜头合计必须精确等于目标时长。 |
| `story_function` | 唯一主要叙事职责。 |
| `beat_change` | 一个主要状态变化。 |
| `visual_description` | 可观察画面与时间进展。 |
| `shot_size` | 如 ECU、CU、MS、WS，并说明叙事原因。 |
| `camera_angle` | 高度、俯仰与轴线侧。 |
| `lens_intent` | 同时说明空间压缩/透视意图与景深/焦点意图，不猜毫米数。 |
| `composition` | 主体位置、层次、负空间与安全区。 |
| `camera_movement` | 一个运动或 `locked_off`，写起止与动机。 |
| `character_ids` | 只引用 bible；无人为空数组。 |
| `location_id` | 引用 bible。 |
| `wardrobe_ids` | 只引用 bible；不可见为空数组。 |
| `prop_ids` | 只引用 bible；无道具为空数组。 |
| `look_id` | 引用 bible。 |
| `subject_action` | 一个主要动作或重大视觉变化。 |
| `performance` | 具体姿态、节奏、视线、呼吸或反应。 |
| `opening_state` | 第一帧可验证状态。 |
| `closing_state` | 最后一帧可验证状态。 |
| `continuity_in` | 继承自前镜的具体状态与 ID。 |
| `continuity_out` | 交给后镜的具体状态与 ID。 |
| `transitions` | 切、叠化、动作匹配、声音桥等及理由。 |
| `storyboard_frame_prompt` | 英文静帧提示，固定身份、构图与光线。 |
| `generation_strategy` | 参考输入、分层与后期路径；不写未知参数。 |
| `risk_level` | `low`、`medium` 或 `high`。 |
| `risk_triggers` | 数组；每项含 `failure_mode`、`acceptance_check`、`fallback_when`。medium/high 至少一项。 |
| `fallback_shot` | 替代镜头 ID 或 `null`。 |
| `state_snapshot` | 必填对象；包含逐镜状态节定义的全部字段，且 opening/closing 与镜头顶层状态完全一致。 |

可选字段 `audio_motif_ids` 引用 bible；`director_intent_zh` 可用于内部审阅，但最终逐镜中文意图以 `shot_prompts` 为准。`state_snapshot` 是必填连续性证据，不得省略。

每镜还可使用 `runtime_role`，值只能为 `active` 或 `fallback`，缺省为 `active`。只有 `active` 镜头参与 sequence 连续性和目标时长求和；`fallback_shot` 必须引用一个完整、风险更低、`runtime_role: "fallback"` 的镜头记录。fallback 仍须拥有 canonical prompt 和至少一个 job。

## 完整分镜表

Markdown 交付必须至少提供下表列组；JSON 仍以字段契约为准。

| Shot | Duration | Story function | Beat change | Opening state | Action |
|---|---:|---|---|---|---|
| `SH001` | 5 | 建立期待 | 门从关闭到打开 | 门闭合，角色等待 | 角色抬眼，门打开 |

| Shot size/angle | Lens/composition | Camera | Performance | Closing state |
|---|---|---|---|---|
| MS / 平视 | 中性透视，人物右三分之一 | 稳定机位 | 先屏息，提示音后抬眼 | 门开，暖光落到人物左脸 |

| Transition | Continuity | Keyframe prompt | Generation strategy | Risk/fallback |
|---|---|---|---|---|
| 声音先行硬切 | C01、W01、L01、P01、LOOK01 | `Medium shot...` | 首帧锁定角色和空间 | medium / null |

## 镜头拆分规则

硬规则：**one primary action or one major visual change per shot**。辅助动作只能支持主要变化，不能形成第二个独立因果节点。

| 负载 | 必须拆分的信号 | 拆法 |
|---|---|---|
| 同时动作 | 两名主体分别完成会改变剧情的动作。 | 按因果顺序拆为动作与反应，或选一个作为画外结果。 |
| 复杂变形 | 身份、材质、尺度、环境同时变化。 | 每镜只改变一类属性，使用匹配切或中间状态。 |
| 人群 | 多人需要独立身份、路径和同步反应。 | 建立主角镜、群体轮廓镜、局部反应镜；减少可辨个体。 |
| 反射 | 主体与镜像都需精确动作和身份。 | 改用越肩、玻璃模糊反射或分层合成；避免双重表演。 |
| 手与物接触 | 手指、按钮、液体、开合或交接必须精确。 | 用接近、接触、结果三阶段；必要时插入道具特写或实拍。 |
| 长对白 | 一镜中有多句、转折、表演反应或口型近景。 | 按意群与反应点拆镜；可改旁白或画外音。 |
| 多重运镜 | 同时推、绕、升降、变焦或穿越空间。 | 保留一个揭示最关键关系的运动，其余改切镜。 |
| 不可能地理 | 镜头要求穿墙、瞬移或方向关系无法成立。 | 建立空间主镜，再用切镜、遮挡或声音桥完成迁移。 |

若用户坚持一镜到底，不得静默拆分。沿用制片阶段的话术，展示真实一镜、隐藏剪辑、明确拆镜三个选项，并等待选择。

## 连续性规则

### 轴线与视线

- 建立两主体或主体—目标轴线；相邻镜头保持在同一侧。
- 越轴必须用中性正轴镜、可见绕轴运动或明确空间重建。
- 视线高度与方向必须能在反打中相接；画外目标改变时先给可见原因。

### 运动与地理

- 角色出画方向与下一镜入画方向保持运动连续。
- 记录门、窗、桌、道路和控制面板的相对位置。
- 改变地点前提供建立镜、方向标志、声音桥或可读转场。

### 光线、时间与天气

- 主光方向、色温、阴影长度和天气继承 bible。
- 时间跳跃必须由剧本、转场或明确环境证据触发。
- 情绪性调色可以递进，但不能无因改变物理光源。

### 人物、服装与道具

- 每镜引用准确 ID，不用描述近似匹配。
- 跟踪左右手、袖口、纽扣、污损、液位、屏幕内容和道具朝向。
- 精确文字默认后期合成；生成画面只留安全区与跟踪面。

### 声音

- 用 `audio_motif_ids`、cue ID 或声音桥维持空间和节拍连续。
- 口型镜头必须记录说话者、语言、台词区间和可见嘴部程度。
- 关键信息不能只依赖未经验证的生成音频。

## 时长与替代镜头

1. 先按 beat 分配秒数，再按镜头分配；不要先堆镜头再压缩。
2. 每镜 `duration_seconds` 包含入镜、主动作、反应、转场和必要尾帧。
3. 激活剪辑的镜头时长总和必须精确等于 `project_brief.target_duration_seconds`。
4. 修改拆镜、对白或转场后重新求和，禁止用“约”绕过。
5. 每个 `high` 风险镜头必须设计同一 `story_function`、同一 `beat_change` 的低风险替代方案。
6. `fallback_shot` 只保存替代镜头 ID；不要把替代方案写成含糊备注。
7. 最终执行清单用 `runtime_role` 区分激活镜头与备用镜头；备用镜头不得被重复计入成片时长。
8. validator 只累计 `runtime_role: "active"`；fallback 必须保持相同 `story_function`、`beat_change`、关键 opening/closing state，并具有更低 `risk_level`。

以下可解析片段证明 5 秒主镜和同为 5 秒的备用镜头只产生 5 秒激活时长；两个镜头仍分别需要 prompt 与 job：

```json
{
  "storyboard_runtime_example": [
    {"shot_id": "SH010", "runtime_role": "active", "sequence": 1, "duration_seconds": 5, "story_function": "揭示产品选择", "beat_change": "从犹豫到决定", "opening_state": "角色停在关闭的门前", "closing_state": "门打开，角色迈向暖光", "risk_level": "high", "fallback_shot": "SH010F"},
    {"shot_id": "SH010F", "runtime_role": "fallback", "sequence": 1, "duration_seconds": 5, "story_function": "揭示产品选择", "beat_change": "从犹豫到决定", "opening_state": "角色停在关闭的门前", "closing_state": "门打开，角色迈向暖光", "risk_level": "low", "fallback_shot": null}
  ],
  "active_runtime_seconds": 5,
  "prompt_records_required": ["SH010", "SH010F"],
  "minimum_job_records_required": ["SH010", "SH010F"]
}
```

## 工作流程

1. 继承故事阶段全部稳定 ID 和批准状态。
2. 建立六类 continuity bible；逐项写固定、允许、禁止和锚点。
3. 按 scene 与 beat 建立叙事层，先通过删除测试。
4. 为每个 beat 选择最少镜头数，执行单一主动作测试。
5. 写视觉层并建立逐镜 `state_snapshot`。
6. 从前一镜 closing state 推导后一镜 opening state。
7. 写生成策略、风险与同功能 fallback。
8. 计算精确时长并检查 sequence 连续。
9. 通过 Screenplay + Storyboard Gate 后，才交给 prompt compiler。

## 可解析示例

以下是阶段片段，不是最终完整 package；所有数组对象使用真实键名。

```json
{
  "continuity_bible": {
    "characters": [{"character_id": "C01", "canonical_description": "三十岁左右的虚构女性，短黑发，左眉上有小痣", "fixed_attributes": ["短黑发", "左眉上小痣"], "allowed_variations": ["从屏息到轻微微笑"], "forbidden_variations": ["发色改变", "面部年龄漂移"], "reference_assets": [{"reference_id": "REF-C01", "role": "identity", "authorization_status": "project_owned"}], "prompt_anchors": ["fictional East Asian woman in her early thirties, short black hair, small mole above the left eyebrow"]}],
    "locations": [{"location_id": "L01", "canonical_description": "窄小电梯内，北侧双开门，东侧金属控制面板", "fixed_attributes": ["北侧双开门", "东侧控制面板"], "allowed_variations": ["门缝暖光逐步变宽"], "forbidden_variations": ["控制面板换边", "空间尺度跳变"], "reference_assets": [], "prompt_anchors": ["compact brushed-steel elevator, double doors ahead, control panel on camera right"]}],
    "wardrobes": [{"wardrobe_id": "W01", "canonical_description": "深蓝哑光风衣，衣领打开", "fixed_attributes": ["深蓝", "哑光", "衣领打开"], "allowed_variations": ["自然袖褶"], "forbidden_variations": ["亮面", "扣合衣领"], "reference_assets": [], "prompt_anchors": ["matte navy trench coat with open collar"]}],
    "props": [{"prop_id": "P01", "canonical_description": "无品牌琥珀色方形香水瓶，黑色瓶盖", "fixed_attributes": ["方形", "琥珀玻璃", "黑色瓶盖"], "allowed_variations": ["玻璃高光随门光移动"], "forbidden_variations": ["可读品牌文字", "瓶盖消失"], "reference_assets": [{"reference_id": "REF-P01", "role": "product_shape", "authorization_status": "project_owned"}], "prompt_anchors": ["unbranded square amber perfume bottle with a black cap"]}],
    "looks": [{"look_id": "LOOK01", "canonical_description": "冷灰电梯与门外暖金晨光形成克制对比", "fixed_attributes": ["门内冷灰", "门外暖金", "自然肤色"], "allowed_variations": ["暖光从门缝逐步进入"], "forbidden_variations": ["霓虹色", "无来源轮廓光"], "reference_assets": [{"reference_id": "REF01", "role": "palette_only", "authorization_status": "confirmed"}], "prompt_anchors": ["cool gray interior contrasted with restrained warm golden light from the opening doors"]}],
    "audio_motifs": [{"audio_motif_id": "AM01", "canonical_description": "低沉电梯运行声在提示音后停止", "fixed_attributes": ["低频机械底声"], "allowed_variations": ["停止后留半秒近静默"], "forbidden_variations": ["突兀爆炸声"], "reference_assets": [], "prompt_anchors": ["low elevator hum ending after a soft arrival chime"]}]
  },
  "storyboard": [
    {
      "shot_id": "SH001",
      "runtime_role": "active",
      "scene_id": "S01",
      "sequence": 1,
      "duration_seconds": 5,
      "story_function": "以电梯门开启把等待转成产品揭示",
      "beat_change": "从封闭等待到暖光中的选择",
      "visual_description": "角色站在电梯右后方，提示音后抬眼；前方双门打开，暖光照亮她左脸和手中香水瓶",
      "shot_size": "medium shot，保留人物、手中产品与门的空间关系",
      "camera_angle": "胸口高度平视，位于人物—电梯门轴线右侧",
      "lens_intent": "中性透视，避免电梯空间夸张变形",
      "composition": "人物位于右三分之一，香水瓶在下方安全区，门缝位于画面中心",
      "camera_movement": "locked_off；让门和光的变化承担揭示",
      "character_ids": ["C01"],
      "location_id": "L01",
      "wardrobe_ids": ["W01"],
      "prop_ids": ["P01"],
      "look_id": "LOOK01",
      "audio_motif_ids": ["AM01"],
      "subject_action": "提示音后角色抬眼，电梯门一次平稳打开",
      "performance": "开场屏息并看向门缝，提示音后缓慢抬眼，肩部放松但不说话",
      "opening_state": "门完全关闭；角色面向北侧门，右手在腰部握住 P01；冷灰顶光",
      "closing_state": "门完全打开；角色仍在原位，P01 仍在右手；门外暖光落到左脸",
      "continuity_in": "继承 C01、W01、P01 无污损状态；P01 黑色瓶盖闭合",
      "continuity_out": "C01 视线朝门外；P01 仍闭合并在右手；暖光方向由北向南",
      "transitions": "以 AM01 到站提示音先行进入；结尾硬切到门外反打",
      "storyboard_frame_prompt": "Medium shot inside a compact brushed-steel elevator, fictional woman with short black hair in a matte navy trench coat on the right third, holding an unbranded square amber perfume bottle in her right hand, double doors open ahead, restrained warm golden light touches the left side of her face, camera at chest height, neutral perspective, no readable text",
      "generation_strategy": "使用角色、产品和地点参考锁定首帧；门外区域保持低细节；精确品牌文字留给后期",
      "risk_level": "medium",
      "risk_triggers": [{"failure_mode": "开门过程中角色身份、P01 右手握持或门体结构漂移", "acceptance_check": "全镜只有 C01 与一个 P01；P01 始终在右手；门只打开一次且控制面板保持画面右侧", "fallback_when": "任一身份、持手、门体或控制面板连续性检查失败"}],
      "fallback_shot": null,
      "state_snapshot": {"screen_direction": "C01 面向画面左前方的门中心", "eye_line": "看向北侧门缝", "body_position": "电梯右后方，站立", "carried_props": [{"prop_id": "P01", "hand": "right", "state": "cap_closed"}], "wardrobe_state": [{"wardrobe_id": "W01", "state": "clean_open_collar"}], "time": "清晨", "weather": "晴", "light_direction": "门内顶光；门外光由北向南", "damage_or_dirt": "none", "opening_state": "门完全关闭；角色面向北侧门，右手在腰部握住 P01；冷灰顶光", "closing_state": "门完全打开；角色仍在原位，P01 仍在右手；门外暖光落到左脸"}
    }
  ]
}
```

## 交接检查

- 六个 bible 集合均存在，ID 唯一且所有引用可解析；
- 每镜只有一个主要动作或重大视觉变化；
- 每镜叙事职责、变化、开场与收场状态完整；
- 轴线、视线、运动、地理、光线、服装、道具与损伤连续；
- `sequence` 连续，激活镜头时长精确等于目标；
- 每个高风险镜头有同功能低风险替代，且不会重复计入成片；
- storyboard 获批后才进入提示词编译；
- 未引入新故事事实或未经核实的模型参数。
