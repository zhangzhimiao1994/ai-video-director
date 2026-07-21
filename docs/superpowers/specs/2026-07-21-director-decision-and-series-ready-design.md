# aibiandao：表达忠实度、导演决策与短剧连续生产预留设计

- 日期：2026-07-21
- 状态：四层设计与书面规格均已获用户确认
- 目标 Skill：`aibiandao`
- 当前实施范围：表达意图锁、导演决策引擎、高级镜头门、短剧接口预留
- 后续独立范围：完整短剧总控、小说/长剧本拆集与自动化执行器

## 1. 问题定义

现有 Skill 已能建立故事因果、角色与模型锁、Shot Graph、运动契约、转场契约、声音计划和反 PPT 成片验收，但仍可能生成两类失败结果：

1. **语义漂移**：镜头在形式上符合故事、运动和连续性字段，却与用户真正想表达的内容无关。`sufficient_draft` 和 `one-pass draft` 可以补齐制作事实，但当前没有独立对象锁定核心表达、禁止暗示和逐镜内容证据，导致“可逆假设”可能膨胀为未经批准的实质创作。
2. **合规但低级的导演处理**：镜头拥有景别、运镜、动作、反应和转场，却仍可能是人物居中站桩、机械正反打、无动机慢推、随机空镜或只靠特效制造变化。现有验证器能检查“有没有”，不能充分检查“为什么此刻必须这样拍”。

用户已确认本轮默认采用通用叙事导演能力，主输出保持可执行，附带导演决策说明；导演层可重构场面调度、镜头覆盖和局部节拍，但不得改变核心剧情、人物动机与结局。

用户后续希望制作可连续展开剧情的 AI 短剧。该能力不能通过延长单条视频实现，必须在单集制作包上方建立剧集级 Canon、资产、状态和伏笔总账。本轮只实现不锁死未来的接口预留，完整短剧总控另立规格实施。

## 2. 已确认决策

1. A「通用叙事导演」是默认导演核心；动作奇观和作者表达作为可选处理，不取代叙事清晰度。
2. 采用双层输出：主分镜直接可生成、可剪辑；导演附录解释视点、调度、镜头必要性、方法依据和关键场景备选处理。
3. 导演方法不以导演姓名或可识别风格直接编译进生成提示词；只提炼可迁移的高层方法。
4. 导演层可以重构场面调度、拆合镜头和局部节拍，但必须保持锁定的核心剧情、人物动机、事件意义和结局。
5. 内容相关性先于电影感。任何与用户表达无关的镜头，即使构图、运动和特效出色，也不能通过。
6. “高级镜头”不等于特殊角度、持续运镜、慢动作、粒子或复杂转场。它必须体现视点、信息、表演、空间、权力或因果判断。
7. 仅对开场、重大反转、高潮、结尾和重复失败的关键镜头生成多个导演处理；普通场景由单一导演决策引擎完成，防止输出膨胀。
8. 短剧能力分两期：本期完成导演核心并预留剧集接口；下一期实现剧集总控、长文本拆集和自动化执行器。

## 3. 目标与非目标

### 3.1 本期目标

- 把用户想表达的内容写成可追踪、不可静默漂移的 `intent_contract`。
- 建立 `用户表达 → 意图条目 → 节拍 → 场景 → 镜头 → 提示词 → 剪辑单元` 的证据链。
- 在拆分镜头前完成视点、信息、表演、场面调度、揭示和剪辑策略。
- 让每个镜头证明其必要性，并拒绝漂亮但无用、无动机或模板化的镜头。
- 把知名导演的高层方法转化为判断问题和拒绝规则，而非名字标签。
- 在不破坏当前单集十对象包的前提下，预留剧集项目引用、状态快照和资产版本接口。
- 通过行为压力测试证明 Skill 不再用视觉奇观替换用户内容。

### 3.2 本期非目标

- 不实现长篇小说的章节理解、自动拆集或整季成片。
- 不实现小云雀或任何第三方产品的私有工作流复制。
- 不因用户要求“像某导演”而输出可识别的在世导演风格模仿提示词。
- 不用单一数值分数自动断言艺术质量；主观导演判断必须有可解释证据。
- 不执行视频生成 API、批量调度、素材云存储、自动发布或未经授权的外部剪辑。
- 不用更多字段掩盖缺少真实内容、表演或导演判断的问题。

## 4. 总体架构

本期电影化链路调整为：

`用户材料 → 表达意图锁 → 故事因果 → 场景导演计划 → 场面调度 → 高级镜头选择 → 连续性/身份锁 → 提示词 → 素材 → 剪辑 → 内容与电影化双重验收`

本轮不创建与现有 Canon 竞争的第十一个单集顶层对象：

- `intent_contract` 位于 `project_brief` 内；
- `scene_directing_plan` 位于 `screenplay.scenes[]` 内；
- 逐镜导演决策字段位于现有 `storyboard[]` 记录内；
- 导演附录由上述 Canon 派生，不成为新的事实源；
- 剧集输入引用统一位于 `project_brief.series_context`，本集候选状态增量统一位于 `quality_report.series_handoff`；不在本轮实现剧集总账写入。

## 5. 第一层：表达意图锁

### 5.1 `project_brief.intent_contract`

电影化、剧情改编、完整剧本和未来剧集模式必须在创意方向或故事扩写之前建立：

```json
{
  "intent_contract": {
    "core_message": "守护不是获胜，而是主动承担代价",
    "audience_takeaway": "观众应理解主角的选择改变了他人与自己的处境",
    "emotional_destination": "从敬畏英雄力量转为理解其代价",
    "must_show_claims": [
      {
        "intent_id": "INT-001",
        "claim": "主角主动替他人承担伤害",
        "required_evidence": "可见选择、受力结果和被保护者的反应",
        "source_status": "user_locked"
      }
    ],
    "must_preserve_events": ["EVENT-CHOICE", "EVENT-COST", "EVENT-SURVIVAL"],
    "must_not_imply": ["主角因意外被击中", "主角毫无代价地获胜"],
    "metaphor_policy": {
      "mode": "literal_evidence_first",
      "rule": "隐喻只能强化已有内容证据，不能代替事件、选择或后果"
    },
    "source_fidelity": {
      "mode": "concept_mode",
      "locked_source_refs": [],
      "allowed_adaptation": "blocking_coverage_and_local_pacing_only"
    }
  }
}
```

`source_fidelity.mode` 只允许 `concept_mode` 或 `screenplay_mode`。`must_show_claims[].source_status` 只允许 `user_locked`、`source_locked` 或 `draft_recommendation`；无论来源状态如何，实质剧情缺口都不能由 `one-pass draft` 静默升级为用户事实。

### 5.2 假设边界

`one-pass draft` 仍可补齐画幅安全区、暂定时长、非关键环境细节等生产信息，但下列内容不得作为可逆假设自动补齐：

- 核心观点、人物动机、关系、能力与立场；
- 事件的主动或被动性质；
- 关键选择、代价、胜负和结局；
- 会改变观众理解的象征或隐喻；
- 用户明确要求呈现或禁止呈现的内容。

这些字段缺失或存在多种实质解释时，必须进入 `missing_material`，不能由推荐方向静默决定。

### 5.3 内容追踪

每个 beat、scene、active shot、canonical prompt 和 edit unit 必须携带非空 `intent_refs`。每个引用必须解析到 `must_show_claims[].intent_id`，并在相应阶段记录可见或可听证据。

内容追踪至少回答：

- 该对象服务哪项用户表达；
- 它提供什么新增证据；
- 删除后会损失什么理解、情绪、权力变化或因果；
- 它是否引入未批准的暗示；
- 下游是否保持同一语义。

若 active shot 无可解析意图引用，或只能以“增强氛围、电影感、震撼”解释其存在，直接判为装饰性镜头并退回。

## 6. 第二层：导演决策引擎

### 6.1 名导方法的使用边界

方法库只储存可迁移的导演问题，不储存“模仿某导演”的生成指令：

| 方法维度 | 可迁移问题 | 主要研究来源 |
|---|---|---|
| 观众注意与心理细节 | 此刻观众必须看见哪个细节？谁知道得更多？ | Alfred Hitchcock 的第一人称方法文章 |
| 视点与动作地理 | 观众从谁的经验进入？动作空间是否可追踪？ | Steven Spielberg 的 DGA 访谈 |
| 表演与人物行为 | 演员正在做什么，而非“表现什么情绪”？ | Martin Scorsese、Christopher Nolan 的 DGA 访谈 |
| 精确预演 | 分镜是否真正代表要拍的因果和调度？ | Bong Joon Ho 的 DGA 问答 |
| 取舍与克制 | 镜头是否只是漂亮、混乱或比角色反应更夸张？ | Donald Richie 记录的 Akira Kurosawa 工作案例 |
| 场面调度 | 人物位置、路径和空间关系是否先于 shot list 成立？ | DGA blocking/staging 导演培训资料 |

用户可在导演附录查看方法依据，但 `storyboard_frame_prompt`、`universal_prompt_en` 和 provider prompt 不使用导演姓名作为风格捷径。

### 6.2 `screenplay.scenes[].scene_directing_plan`

每场戏在拆分镜头前必须记录：

- `scene_pov`：视点拥有者、允许知道的信息和何时可脱离；
- `audience_knowledge_before` / `audience_knowledge_after`；
- `dramatic_turn`：本场唯一主要转折及触发原因；
- `character_objectives`：逐角色目标、阻力和策略；
- `subtext_and_playable_actions`：潜台词及演员可执行动词；
- `blocking_map`：人物起止位置、距离、遮挡、进退、出入口和空间权力变化；
- `reveal_strategy`：展示、隐藏、延迟和反转顺序；
- `camera_rule`：摄影机允许移动的条件和禁止的无动机运动；
- `coverage_strategy`：主镜、反应、插入、主观或空间重建的必要性；
- `visual_motif_progression`：已有母题在本场如何改变；
- `editorial_consequence`：本场结尾如何触发或限制下一场；
- `rejected_choices`：被淘汰的俗套或错误方案及原因；
- `intent_refs`：本场服务的表达意图。

场面调度先于镜头选择。无法说明人物为什么处于当前位置、为什么移动或为什么保持距离时，不得仅靠景别和运镜继续分镜。

### 6.3 逐镜导演决策

电影化 active shot 在现有字段上增加：

- `intent_refs`；
- `dramatic_question`：本镜让观众等待或确认什么；
- `information_delta`；
- `emotion_delta`；
- `power_delta`；
- `spatial_delta`；
- `blocking_change`；
- `camera_necessity`：机位、景别、镜头高度、焦点和运动为何必要；
- `performance_verb`：演员可执行的主要行为；
- `shot_relation`：本镜如何提问、回答、延迟、打断或反转相邻镜头；
- `director_rejection_reason`：当镜头被替换或退回时记录原因。

每镜不要求所有 delta 都改变，但至少有一项非空、可观察并与 `beat_change` 一致。仅更换背景、角度、粒子或特效不构成有效 delta。

## 7. 第三层：高级镜头门

### 7.1 高级镜头的通过标准

镜头必须同时满足：

1. 与用户表达存在可解析关联；
2. 来自已建立的场面调度和视点；
3. 产生至少一种信息、情绪、权力、空间或因果增量；
4. 机位、景别、镜头运动和切点具有可解释动机；
5. 表演使用可执行行为、视线、呼吸、节奏或身体路径；
6. 与相邻镜头形成可读关系，而非孤立海报；
7. 不以风格、特效或转场替代内容和人物行为；
8. 能说明删除该镜会造成的具体损失。

### 7.2 默认拒绝模式

- 人物居中正面站立，只有背景、光束、烟雾或粒子运动；
- 没有揭示、跟随、压迫、释放或空间重构目的的慢推、环绕、升降或手持；
- 为凑景别随机插入眼睛、手、天空、建筑或无人机空镜；
- 机械正反打中人物距离、权力、情绪和策略均不变化；
- 只写“愤怒、悲伤、震惊”，没有演员可执行行为；
- 关键英雄镜头没有被前序行动、反应与后果挣得；
- 多个镜头只重复同一气氛、姿态、信息或视觉母题；
- 镜头构图漂亮，但与 `intent_contract`、dramatic turn 或相邻镜头无关；
- 依赖导演附录解释才能理解画面含义。

有意静止、长镜头、硬切、极简构图和沉默仍可通过，但必须具有明确注意力变化、戏剧压力、表演过程和边界证据。

### 7.3 双层输出

主分镜只展示制作必需字段和简洁导演指令。导演附录派生展示：

- 本场视点与信息策略；
- 调度图的文字说明；
- 每个关键镜头的必要性；
- 使用的高层导演方法；
- 被淘汰方案及原因；
- 开场、反转、高潮和结尾的备选处理。

附录不能修改 Canon；若附录与主分镜冲突，以 Canon 为准并使交付失败。

## 8. 第四层：短剧连续生产预留

### 8.1 分期边界

本期只为单集包增加两个可选嵌套对象，不新增顶层对象。

`project_brief.series_context` 保存只读输入快照：

- `series_project_id`；
- `episode_id`；
- `series_snapshot_id`；
- `asset_registry_version`；
- `episode_opening_state_ref`；
- `foreshadow_refs`；
- `payoff_refs`。

`quality_report.series_handoff` 保存本集候选输出：

- `episode_closing_state_delta`；
- `continuity_evidence_refs`；
- `foreshadow_status_changes`；
- `payoff_status_changes`；
- `commit_eligibility`，本期固定为 `external_series_controller_required`；
- `handoff_status`，未接入下一期总控时只能为 `draft` 或 `unresolved`。

这些字段存在时必须可追踪，但本期不创建、修改或提交外部剧集总账。未知或未批准的剧集引用保持 `draft`/`unresolved`，不能伪造已同步状态；即使单集通过验收，`series_handoff` 也只是一份待外部剧集总控审阅的候选变更。

### 8.2 下一期 `series_project`

完整短剧总控将作为单集包的父级 manifest，至少包含：

- `series_bible`：世界规则、主题、人物关系和终局；
- `season_arc`：整季冲突、角色弧光、阶段升级和终点；
- `director_language_bible`：镜头语法、表演尺度、色彩、声音母题和禁项；
- `asset_registry`：人物定妆、服装、道具、场景、声音、模型和参考资产版本；
- `continuity_ledger`：伤势、位置、持有物、秘密、关系和知识状态；
- `foreshadow_payoff_ledger`：伏笔建立、发展、回收和状态；
- `episode_index`：每集进入状态、目标、阻碍、反转、高潮、钩子和退出状态。

单集采用事务式状态提交：草稿、生成失败和未验收成片不能修改剧集总账；只有通过内容、连续性、人物和电影化验收的版本才能把 `episode_closing_state_delta` 提交为下一集的 opening snapshot。早期集数变更必须列出受影响的后续集、镜头、提示词、素材和剪辑单元。

### 8.3 自动化执行器边界

达到一站式生成还需要独立执行器，负责：

- 调用经核验的平台 API；
- 素材、任务、版本和失败重试；
- 按角色模型锁和资产注册表绑定输入；
- 调用剪辑适配器或 AI editor；
- 运行探测、接触表和成片审阅；
- 经授权后提交剧集状态。

Skill 负责导演决策与 Canon，执行器负责有证据的外部动作。没有真实工具、API、授权和输出证据时，只能交付执行计划，不能声称已生成或已同步。

## 9. 数据流与状态

### 9.1 单集数据流

1. 从用户输入提取用户事实与 `intent_contract`。
2. Brief Gate 确认实质表达缺口；生产细节可保留可逆假设。
3. 三个创意方向都必须映射同一 intent claims，不能以不同方向为由改变核心表达。
4. 故事阶段为 beat 和 scene 写 `intent_refs`。
5. 场景导演计划先建立视点、表演和调度，再交给 storyboard。
6. storyboard 为每镜写 delta、camera necessity 和 shot relation。
7. prompt compiler 继承 intent、动作、调度和身份锚点；平台层不得增加新事实。
8. edit plan 继承同一 intent refs，并证明切点和镜头关系没有破坏表达。
9. 成片验收同时检查 intent fidelity 与 cinematic readiness；任一失败都不能交付电影母版。

### 9.2 关键场景多方案

只有满足 key-shot 条件的场景可生成最多两个局部导演备选。备选必须保持相同 intent refs、核心事件、人物动机、边界状态和时长槽，只允许改变调度、视点、覆盖和节奏处理。用户未选择时，备选不进入 active runtime。

## 10. 失败回退

失败必须返回最早责任层：

| 失败 | 返回位置 | 禁止的伪修复 |
|---|---|---|
| 与用户核心表达无关或新增错误暗示 | `project_brief.intent_contract` | 增加旁白解释无关画面 |
| 剧情没有转折、选择或后果 | `story_structure` / `screenplay` | 用运镜和音乐制造虚假高潮 |
| 人物没有可执行行为或空间关系 | `scene_directing_plan` | 直接写景别和情绪形容词 |
| 调度、机位或镜头关系俗套 | `storyboard` | 随机插入特写、空镜或环绕 |
| 提示词弱化主体行为或引入新事实 | canonical prompt | 在平台字段中补剧情 |
| 生成素材动作、身份或空间失败 | prompt/media regeneration | 用粒子、速度坡度和转场遮盖 |
| 剪辑破坏信息、反应或内容证据 | edit timeline | 只补最终效果或更名版本 |
| 跨集状态冲突 | future `series_project` ledger | 在下一集重新随机设定人物 |

## 11. 验证与测试设计

### 11.1 两级验收

**结构硬门**由确定性验证器检查字段、引用、状态、禁止项和证据链。**导演审片**使用可解释量表检查观众是否无需附录即可理解内容，镜头是否源于人物与戏剧，表演和空间是否可读，以及是否存在漂亮但无用的镜头。主观量表不能覆盖结构硬门。

### 11.2 RED 行为案例

在修改 Skill 前固定以下失败：

1. 用户表达“守护是承担代价”，输出却用巨龙、城市和粒子奇观替代主动选择与受伤后果。
2. 完整剧本在 `one-pass draft` 中被新增人物关系、能力或结局暗示。
3. 对白场景只生成对称正反打，人物距离、策略、权力和情绪均无变化。
4. 动作场景连续使用正面站姿、慢推和背景特效，空间地理与作用力不可读。
5. 为“高级感”随机增加眼睛、手、天空、建筑和无人机空镜。
6. 每个镜头字段齐全，但至少一个 active shot 无 intent refs 或无任何有效 delta。

### 11.3 GREEN 行为案例

1. 同一“守护”输入使用主动挡击、受力、隐藏伤势和被保护者继续前进形成直接证据。
2. 完整剧本只重构调度、覆盖和局部节拍，锁定事件、动机与结局不变。
3. 对白戏通过距离、遮挡、视线、打断和可执行动作改变权力，不强迫持续运镜。
4. 动作戏建立地理、行动、反应和后果，镜头关系可追踪。
5. 有意静止镜头因注意力转移、表演过程和声音压力通过，而非被固定时长误杀。
6. 主分镜与导演附录来自同一 Canon，附录不新增事实。

### 11.4 回归与压力测试

- `one-pass draft` 不能把实质剧情决定归为可逆假设；
- 三个创意方向保持同一 intent contract；
- A/B/C 节奏切换、画幅重构和平台切换不改变核心表达；
- 非电影化普通任务不被新增电影导演字段误伤；
- 现有角色、模型、连续性、反 PPT、剪辑和授权测试全部继续通过；
- 单集可选剧集引用缺省时保持向后兼容；
- 存在剧集引用时，未解析 snapshot 或 asset version 不能进入 approved execution；
- 使用脱敏行为提示进行前后盲测，导演升级版必须减少无关镜头、模板运镜和人物站桩。

## 12. 验收标准

本期实现只有满足以下条件才能发布：

1. 用户核心表达被写成明确 intent contract，且所有 active shots、prompts 和 edit units 可追踪。
2. `one-pass draft` 不再有权静默决定核心观点、人物动机、关系、关键选择、代价和结局。
3. 每场先完成视点、信息、表演和调度，再生成 shot list。
4. 每镜至少产生一个可观察 delta，并能说明删除造成的具体损失。
5. 漂亮但无关、无动机运镜、机械正反打、随机插入和背景特效替代表演均被拒绝。
6. 主分镜可直接执行，导演附录可解释但不修改 Canon。
7. 内容忠实度失败时，即使技术探测和电影化运动检查通过，也不能成为电影母版。
8. 角色身份、模型锁、剧情事件、空间状态和转场/声音硬门继续有效。
9. 本期只预留剧集引用，不宣称已实现长篇拆集、整季生成或状态提交。
10. 全量测试与新增行为压力测试通过，并保留旧版本。

## 13. 预计文件影响

本期预计修改：

- `SKILL.md`：表达意图路由、导演决策顺序、内容忠实度硬门和失败回退；
- `references/production-meeting.md`：`intent_contract` 与实质假设边界；
- `references/story-directing.md`：scene directing plan、视点、潜台词和表演动作；
- `references/continuity-storyboard.md`：逐镜 intent refs、delta、blocking change、camera necessity 和 shot relation；
- `references/cinematic-directing.md`：名导方法矩阵、高级镜头门和关键场景备选；
- `references/prompt-compiler.md`：意图继承、主体行为优先和导演姓名禁用边界；
- `references/editing-finish.md`：edit-unit intent trace 与内容忠实度成片检查；
- `references/output-contract.md`：新增嵌套字段与可选剧集引用；
- `scripts/validate_package.py`、`scripts/validate_edit_plan.py`：结构硬门与跨阶段引用；
- `test-prompts.json`、`tests/`、`results.tsv`：语义漂移、低级镜头和回归行为证据。

下一期短剧总控将使用独立设计规格和实施计划，不在本轮隐式加入。

## 14. 研究来源

- [Alfred Hitchcock: My Own Methods（BFI / Sight and Sound）](https://www.bfi.org.uk/sight-and-sound/features/alfred-hitchcock-my-own-methods)
- [Steven Spielberg DGA Interview](https://www.dga.org/craft/dgaq/issues/0604-winter-2006/dga-interview-steven-spielberg)
- [Martin Scorsese DGA Interview](https://www.dga.org/craft/dgaq/issues/0704-winter-2007-2008/dga-interview-martin-scorsese)
- [Christopher Nolan DGA Interview](https://www.dga.org/craft/dgaq/issues/1202-spring-2012/dga-interview-christopher-nolan)
- [Bong Joon Ho DGA Q&A](https://www.dga.org/Events/2025/May2025/Mickey17_QnA_0325)
- [Akira Kurosawa working-method account: Throne of Blood（Criterion）](https://www.criterion.com/current/posts/938-throne-of-blood)
- [DGA: Blocking, Staging and Setting a Tone of Leadership](https://www.dga.org/Events/2021/October2021/DDI_TheShoot-BlockingStaging_0821)
- [小云雀官方页面](https://xyq.jianying.com/)
