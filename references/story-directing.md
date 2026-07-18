# AI Video Director：故事导演参考

本参考负责把已批准的简报与创意方向转成导演阐述、故事结构和可审计剧本。只设计故事、表演、画面与声音意图；本阶段不制作 storyboard，也不编译任何模型专用参数。最终完整包以 `output-contract` 为唯一契约；本文 JSON 是三个故事阶段顶层对象的完整最小实例，不替代完整包契约。

## 目录

- [输入与职责](#输入与职责)
- [结构选择器](#结构选择器)
- [导演阐述字段](#导演阐述字段)
- [故事结构契约](#故事结构契约)
- [剧本契约](#剧本契约)
- [因果与节拍测试](#因果与节拍测试)
- [时长设计](#时长设计)
- [声音计划](#声音计划)
- [短视频信息结构](#短视频信息结构)
- [审阅流程](#审阅流程)
- [常见失败](#常见失败)
- [下一阶段交接](#下一阶段交接)
- [快速参考](#快速参考)

## 输入与职责

开始前要求以下输入已经存在：

- 标准流程中 `project_brief.brief_status` 为 `approved` 或 `locked`；`one-pass draft` 已明确启用时可为 `draft`，但全部缺口必须进入可逆假设与风险记录；
- 标准流程中 `target_duration_seconds` 已确认；`one-pass draft` 可使用简报中未批准、可逆且附影响说明的暂定正数值；
- 创意方向 `direction_id` 已由用户选择，或 `one-pass draft` 已明确启用并附可逆假设；
- 关键人物、场地、授权、音频与模型限制已经记录；
- 一镜到底等实质冲突已有用户选择。

若输入存在实质冲突，退回制片会议处理，不在故事阶段静默改动简报。若只有不影响故事的细节缺口，沿用简报中的可逆假设并保持标记。

本阶段只输出三个顶层对象：`selected_treatment`、`story_structure`、`screenplay`，不增加交接包装层。把“观众为什么继续看”“每场改变了什么”“如何用画面和声音证明”写清楚。

### 电影化输入路由

当 `project_brief.cinematic_mode` 存在时，先记录输入模式：

- `concept_mode`：从用户事实生成可逆草案，不把补全内容写成用户事实。
- `screenplay_mode`：锁定原剧本的核心事件、动机和因果，只压缩节奏、场景与对白。
- 长篇小说不是首版可用模式；请求用户选择一个自包含片段或提供剧本。

电影化故事结构使用 `cinematic_six_beats`：`hook`、`goal`、`escalation`、`reversal`、`climax_choice`、`aftertaste`。每个 beat 必须声明进入状态、可见变化、原因、结果和时长。六段可合并，但不得让目标、阻碍、因果或结尾变化消失。

## 结构选择器

根据题材目标选择结构，不要把同一种营销模板套给所有视频。

| 类型 | 推荐结构 | 节拍密度 | 常见失败 |
|---|---|---|---|
| 剧情短片 | 现状与欲望 → 阻力 → 选择 → 后果 → 新状态；也可使用悬念揭示，但必须保持角色因果。 | 约每 8–20 秒一个主要变化；短于 60 秒时减少角色和支线。 | 只展示氛围，没有选择与后果；转折来自巧合；结尾状态与开头相同。 |
| 广告 | Hook → 痛点或欲望 → 产品机制 → 证据 → 回报 → CTA。 | 约每 2–6 秒一个信息或情绪变化；一个镜头只承担一个主张。 | 先讲品牌背景才给价值；功能罗列无证据；CTA 与核心承诺不一致。 |
| 知识或口播 | Hook → Context → Main points → Proof/example → Payoff → CTA 或收束。 | 约每 4–10 秒一个可复述要点；复杂概念给例证停留。 | 信息点过多、缺少例子、旁白速度超限、画面只做装饰。 |
| 概念片 | 建立视觉规则 → 变奏 → 升级 → 破例或反转 → 标志性收束。 | 约每 5–12 秒一次视觉规则变化；每次变化都推进主题。 | 只有随机漂亮镜头；母题不发展；结尾只是停止而非完成。 |
| 音乐驱动 | 依据乐段建立 motif → 重复与变奏 → build → drop 或高潮 → 尾奏回响。 | 以拍点、乐句和段落为单位；视觉切换服从音乐结构但保留叙事可读性。 | 每拍都切导致疲劳；画面与音乐情绪相反却无意图；高潮没有视觉升级。 |

若作品跨类型，指定一个主结构和一个辅结构。例如“剧情短片为主、广告回报为辅”；不要把两套完整结构并排塞进同一时长。

## 导演阐述字段

顶层 `selected_treatment` 包含 `treatment_status`、`direction_id`、主题或引导问题、表演、视觉、剪辑、分轨声音、禁项与 `sound_plan`。`treatment_status` 只能为 `draft` 或 `approved`；每项写可执行选择及其叙事理由，禁止只堆氛围形容词。

| 字段 | 导演要求 |
|---|---|
| `theme` | 写作品检验的观点，不写泛泛主题词。例如写“效率若牺牲理解便失去价值”，而非只写“科技”。 |
| `dramatic_question`、`guiding_question` 或 `thematic_tension` | 剧情片写观众等待回答的戏剧问题；概念片或音乐片可改用引导问题或主题张力，并在结尾完成、反转或有意悬置，不为非剧情作品硬造剧情问题。三者至少存在一项。 |
| `pov` | 指定谁拥有信息、谁被限制，以及镜头何时允许脱离其视角。 |
| `performance` | 指定表演强度、节奏、潜台词、视线与身体行为；把情绪落到可演动作。 |
| `visual_reference_attributes` | 使用数组引用已批准的 `reference_id`；每项明确 `borrow_attributes` 与 `prohibited_copy_or_imitation`，只锁定可使用的媒介、配色、构图、材质等属性，不把参考来源或在世艺术家的可识别风格当作可复制目标。 |
| `weather_time_of_day` | 明确 `weather`、`time_of_day` 与跨场连续性规则；变化必须由故事节拍触发，不能在相邻场景无理由漂移。 |
| `palette` | 指定主色、强调色、饱和度变化及其节拍用途。 |
| `lighting` | 指定光源逻辑、对比度、时间变化和人物可读性。 |
| `texture` | 指定材质、空气感、颗粒或表面细节，以及这些质感服务的主题。 |
| `composition` | 指定主体位置、层次、留白、画幅安全区和权力关系。 |
| `lens` | 指定视角倾向、景深和空间压缩目的；不必在此写模型语法或厂商参数。 |
| `camera_movement` | 每种移动都写动机、起点与终点；没有叙事动机时使用稳定机位。 |
| `edit_rhythm` | 指定何时快切、何时延长、转场依据和尾帧停留。 |
| `dialogue` | 指定谁说、说话目的、潜台词、可删信息和口型要求。 |
| `narration` | 指定叙述者、可信度、语速、信息职责，以及不能重复画面之处。 |
| `ambience` | 指定空间底声、时间感和连续性线索。 |
| `sfx` | 指定动作证据、转折提示和主观声音；不要用音效替代画面因果。 |
| `music` | 指定进入、退出、结构、情绪变化与授权条件；不要只写“史诗感音乐”。 |
| `silence` | 指定静默出现的节拍、持续时间和戏剧作用。 |
| `prohibited_choices` | 列出会破坏品牌、故事、授权或可读性的明确禁项。 |
| `sound_plan` | 作为 `selected_treatment` 的子数组记录逐项 cue；每项至少包含 `cue_id`、`track`、`timing_or_trigger`、`story_function`、`lip_sync_dependency`、`source_status`。 |

`selected_treatment.treatment_status` 在共同审批前保持 `draft`，可以在 Direction Gate 后交给剧本与分镜共同迭代；只有用户通过 **Screenplay + Storyboard Gate** 时才更新为 `approved`。`one-pass draft` 全程保持 `draft`，但允许继续组装完整草案；不得根据代理自评自动批准。

## 故事结构契约

先用顶层 `story_structure` 确认节拍职责，再写场景细节。至少记录 `structure_type`、`target_duration_seconds`、`opening_state`、`beats`、`payoff`、`closing_state`；每个 beat 使用真实 JSON 键 `beat_id`、`function`、`change`、`cause`、`effect`、`visual_evidence`、`duration_seconds`，并用 `cue_ids` 或 `audio_motif_id` 引用声音计划。

要求：

1. `opening_state` 与 `closing_state` 必须形成可陈述差异。
2. 每个 beat 只承担一个 `change`；辅助信息不得抢走主要变化。
3. `cause` 必须来自前一动作、选择、信息或已建立条件；不要用未经铺垫的巧合推进。
4. `effect` 必须触发下一 beat，或完成结局回报。
5. `visual_evidence` 必须是观众可看见或可听见的证据，不写“观众感到震撼”这类结果词。
6. 所有 beat 的 `duration_seconds` 之和必须精确等于确认时长；`one-pass draft` 则精确等于暂定时长，并包含转场与尾帧停留。

## 剧本契约

顶层 `screenplay` 必须包含 `screenplay_status`、`target_duration_seconds` 与 `scenes` 数组；每个 scene 含全部必填字段，并显式记录因果和声音引用。可复制的真实 JSON 见“下一阶段交接”。

字段约束：

- `scene_id`：使用稳定唯一 ID，供分镜和声音计划引用。
- `objective`：写本场要让角色或观众获得什么，不写摄影任务。
- `conflict_or_question`：写阻碍、信息差或本场必须回答的问题。
- `action`：按可见因果顺序写动作，避免文学性心理描写。
- `dialogue_or_narration`：只保留推动目标、冲突、证据或转折的语言；没有语言时使用 `null`。
- `emotional_change`：写“从 X 到 Y，并由 Z 触发”，不得只写单一情绪标签。
- `visual_evidence`：列出证明变化的表情、动作、物件状态、空间关系或可读图形。
- `opening_state` 与 `closing_state`：使用可比较状态，明确本场改变了什么。
- `duration_seconds`：包含动作、语言、呼吸和本场内部停留。
- `causal_link_from_previous`：说明上一场的哪个结果造成本场；首场可为 `null`。
- `causal_link_to_next`：说明本场的哪个结果触发下一场；末场可为 `null`，但必须完成 payoff。
- `beat_ids`：引用 `story_structure.beats`，不创建无法追溯的场景。
- `cue_ids` 或 `audio_motif_id`：引用 `selected_treatment.sound_plan`，供后续分镜继承，不在本阶段展开逐镜设计。

所有 scene 的 `duration_seconds` 之和必须精确等于 `target_duration_seconds`。共同审批前 `screenplay_status` 保持 `draft`，可交给分镜阶段迭代；只有用户通过 **Screenplay + Storyboard Gate** 后才更新为 `approved`。`one-pass draft` 不因向后交接而自动获批。

## 因果与节拍测试

对每个场景和每个 beat 执行以下测试：

1. **状态变化测试**：它必须改变知识、情绪、关系、目标或物理状态中的至少一项。
2. **删除测试**：删除后若不影响后续理解、选择、因果或 payoff，删除该场或合并其必要信息。
3. **单一变化测试**：每个 beat 只承担一个主要变化；若同时承担两个独立转折，拆成两个 beat 并重新分配时长。
4. **因果测试**：用“因为前一结果，所以发生本场；因为本场结果，所以下一场发生”朗读。若只能用“然后”，补足因果或删场。
5. **证据测试**：观众必须能从画面、对白或声音识别变化；导演解释不能成为唯一证据。
6. **动机测试**：角色行动来自目标、压力或新信息；摄影机移动来自揭示、跟随、主观变化或空间重构。
7. **回报测试**：结尾回答 `dramatic_question`，或完成 `guiding_question`、`thematic_tension`，并兑现 Hook、承诺或视觉母题；有意悬置也要让观众知道悬置的意义。

建立简短审计表，便于复核：

| Beat | 主要变化 | 原因 | 可见或可听证据 | 触发的后果 | 秒数 |
|---|---|---|---|---|---|
| `B01` | 从机械执行到意识到重复 | 第十次打开同一模板 | 同名文件与纸张堆叠 | 使用者开始寻找替代流程 | 5 |

若两行的主要变化、证据和后果实质相同，视为重复 beat，合并或重写。

## 时长设计

标准流程只在 `target_duration_seconds` 已确认后进行精确分配；`one-pass draft` 使用已记录为未批准、可逆并附影响说明的暂定正数值，同样精确分配，但不得据此进入执行编译。

1. 先给结构 beat 分秒，再细分到 scene；不要先写满对白再硬压时间。
2. 单独预留开场识别、场间转场、动作反应和尾帧停留。尾帧若承载品牌、结论或 CTA，给足可读时间。
3. 旁白按自然中文口播约 **3.5–4.5 字/秒**估算；标点不计入字数，数字、英文与单位按实际读音估算。该范围只用于初排，不是验收标准。
4. 最终必须朗读完整对白与旁白并计时；记录实际耗时，加上停顿、呼吸和表演反应后再调整。
5. 对关键信息留出理解时间。快速字幕、数字、图表和产品机制不能只按发音时间计时。
6. 每次改词、删场或改转场后，重新计算 scene 与 beat 时长。
7. 最终满足：`sum(scene.duration_seconds) = sum(beat.duration_seconds) = target_duration_seconds`，不得使用约数绕过。

可使用以下时长账本：

| 项目 | 秒数 | 验证方式 |
|---|---:|---|
| 开场与 Hook | 5 | 首次观看能识别重复劳动的问题 |
| 主体 scenes | 20 | 动作计时与朗读计时均已记录 |
| 转场 | 0 | 已计入所属 scene 的时长 |
| 尾帧停留 | 5 | 空桌、人物与夕光的回报可读 |
| 合计 | 30 | 与 `target_duration_seconds` 精确相等 |

## 声音计划

把声音拆成独立轨道规划，不写成一个笼统的“音频”段落。计划必须位于 `selected_treatment.sound_plan`；每个 cue 至少使用真实 JSON 键 `cue_id`、`track`、`timing_or_trigger`、`story_function`、`lip_sync_dependency`、`source_status`。需要补充内容、制作方法或验收条件时使用明确键，不另建平行声音对象。

- **Production dialogue**：记录现场或画内对白、说话者、表演目的与干净收音要求。
- **Narration**：记录叙述者、文本、语速、停顿和它补充而非重复的画面信息。
- **Ambience**：建立空间与时间连续性，场景切换时说明底声如何过渡。
- **SFX**：给动作、材质与转折提供证据；标出必须同步的瞬间。
- **Music**：按结构段落标进入、升级、抽离与结束；记录版权或生成来源。
- **Silence**：把静默作为有时长的 cue，说明它制造的注意力、压力或回报。
- **Lip-sync**：记录可见嘴部的台词、语言、近景程度和所用流程的可靠性；能力不足时回到制片冲突处理。

`track` 使用 `production_dialogue`、`narration`、`ambience`、`sfx`、`music`、`silence` 或 `lip_sync`。scene、beat 和后续 storyboard 必须用 `cue_ids` 或 `audio_motif_id` 引用这些 cue，不能仅写“配音乐”或“加音效”。

不得把理解故事所必需的唯一信息放在所选模型不支持生成或可靠同步的音频里。为关键信息提供画面证据、后期旁白、字幕或其他已验证通道。

当画面需要品牌名、数字、界面、字幕或法律文案时，优先计划后期合成精确屏幕文字。生成画面只负责留出构图安全区和跟踪条件，不依赖模型直接拼写。

## 短视频信息结构

对营销、产品说明、知识口播和需要明确行动的短视频，可使用：

`Hook → Context → Main points → Proof/example → Payoff → CTA`

执行要求：

- Hook 提出具体问题、反差或承诺，不用无关惊吓骗取停留；
- Context 只补理解 Main points 所需的信息；
- Main points 控制数量，每项承担一个主张；
- Proof/example 用可验证事实、演示、对比或案例支持主张；
- Payoff 回答开场承诺，让信息形成闭环；
- CTA 与目标一致，并放在 payoff 之后或自然融入回报。

该结构只用于营销、知识、产品说明等合适题材。不要强塞剧情片、音乐驱动片或纯概念片；剧情片优先角色选择与后果，音乐片优先乐段和视觉母题。若 CTA 破坏叙事，可以用片尾卡、描述区或品牌尾帧承载，而不让角色突然口播。

## 审阅流程

按以下顺序审阅，前一层不通过时不要用镜头美化掩盖：

1. 检查主题，以及 `dramatic_question`、`guiding_question` 或 `thematic_tension` 中适用于当前题材的一项，是否与已选方向一致。
2. 检查 opening state、beats、payoff、closing state 是否形成因果变化。
3. 对每场执行状态变化、删除、单一变化、因果与证据测试。
4. 朗读对白与旁白，并完成精确时长账本。
5. 检查表演、构图、镜头运动、剪辑与声音是否各有叙事动机。
6. 检查禁项、授权、口型、精确文字和模型能力限制是否被遵守。
7. 审阅并输出顶层 `selected_treatment`、`story_structure`、`screenplay`；标准流程在 Direction Gate 后、`one-pass draft` 在标清全部假设后，把 draft 对象交给 `continuity-storyboard` 共同迭代。

本阶段不制作或批准 storyboard。后续阶段完成 storyboard 后，由 `screenplay` 与 storyboard 共同通过 **Screenplay + Storyboard Gate**，再进入执行编译。

## 常见失败

| 失败 | 识别方式 | 修正 |
|---|---|---|
| 画面漂亮但没有因果 | 场景之间只能说“然后”，删除任一镜头也不影响结局。 | 补写 cause/effect 与状态变化；无法补足时删场。 |
| 重复 beat | 连续节拍改变同一状态，证据和后果也相同。 | 合并节拍，或让后一个节拍升级、反转、证明前一个变化。 |
| 泛化氛围词 | 使用“电影感、梦幻、高级、震撼”却没有色彩、光线、表演或构图行为。 | 把每个词改写为可观察选择和叙事目的。 |
| 无动机运镜 | 推拉摇移不揭示信息、不跟随行动，也不改变空间关系。 | 写明移动的起点、终点和揭示；无动机时使用稳定机位。 |
| 对白超过时长 | 按字数估算已接近上限，朗读加停顿后明显超时。 | 先删重复信息，再改为画面证据；重新朗读和计时。 |
| 结尾没有 payoff | 结尾未回答戏剧问题、未兑现 Hook，或 closing state 没有变化。 | 让最终动作、证据或画面母题完成承诺，并预留停留。 |
| CTA 破坏叙事 | 角色突然停止行动直接卖货，语气与世界观断裂。 | 把 CTA 融入角色结果，或移至片尾卡、品牌尾帧、描述区。 |
| 关键信息只存在于不可靠音频 | 静音观看或音频生成失败时，故事无法理解。 | 增加画面证据、后期旁白或精确字幕。 |
| 精确文字交给生成画面 | 品牌名、数字或法律文案出现错字。 | 预留安全区和跟踪条件，使用后期合成。 |
| 故事阶段提前制作分镜或编译参数 | 职责边界混乱，故事决定被逐镜细节或厂商语法锁死。 | 本阶段只交付三个可审阅的顶层故事对象；分镜阶段完成 storyboard 后共同批准，获批结果再交执行编译。 |

## 下一阶段交接

在标准流程通过 Direction Gate，或用户明确要求 `one-pass draft` 后，把三个对象直接作为顶层字段交给 `continuity-storyboard`，不增加包装层。草案交接不等于批准，也不得触发真实 API 执行。以下是已通过共同审批时的完整、可复制且可解析最小故事阶段 JSON；最终完整包仍以 `output-contract` 为唯一契约。

```json
{
  "selected_treatment": {
    "treatment_status": "approved",
    "direction_id": "D1",
    "theme": "自动化的价值不是更快忙碌，而是归还可支配时间",
    "dramatic_question": "重复劳动被拿走后，使用者会把时间还给什么？",
    "pov": "始终贴近使用者，只在结果揭示时切到客观俯视",
    "performance": "开场动作机械且呼吸短促，完成后肩颈放松并停看窗外一秒",
    "visual_reference_attributes": [{"reference_id": "REF01", "borrow_attributes": ["产品配色"], "prohibited_copy_or_imitation": ["第三方标识", "在世艺术家的可识别风格"]}],
    "weather_time_of_day": {"weather": "晴朗，窗外无降水或云量突变", "time_of_day": "工作日傍晚", "continuity_rule": "S01 至 S03 保持同一傍晚，暖夕光只随故事回报逐步进入人物区域"},
    "palette": "冷灰工作区逐步让位于暖橙夕光",
    "lighting": "屏幕冷光作为压力来源，结尾由窗侧暖光恢复面部层次",
    "texture": "纸张堆叠与干净桌面的触感差异承担状态变化",
    "composition": "开场以文件挤压人物，结尾扩大人物前方留白",
    "lens": "中性视角保持流程可读，结果揭示使用轻微广角展示空桌",
    "camera_movement": "只在任务完成时缓慢后移，揭示被释放的空间",
    "edit_rhythm": "前十二秒短促重复，中段随流程压缩，最后五秒保持完整停留",
    "dialogue": "不使用画内对白，避免口型依赖",
    "narration": "三句画外音只提出问题、解释机制并完成回报，不复述画面",
    "ambience": "办公室空调与键盘底声贯穿，完成瞬间减少键盘密度",
    "sfx": "点击、纸张摩擦与完成提示音提供动作证据",
    "music": "使用已授权的轻节奏器乐，结尾从循环进入开放和弦",
    "silence": "完成提示后留出一秒近静默，让状态变化落地",
    "prohibited_choices": ["不显示无法核验的效率百分比", "不让角色突然对镜口播 CTA"],
    "sound_plan": [
      {"cue_id": "CUE01", "track": "ambience", "timing_or_trigger": "00:00-00:25 持续，任务完成后降低键盘密度", "story_function": "维持办公室连续性并衬托压力解除", "lip_sync_dependency": "none", "source_status": "original_recording_confirmed", "audio_motif_id": "AM01"},
      {"cue_id": "CUE02", "track": "narration", "timing_or_trigger": "00:02、00:12、00:25 三次进入", "story_function": "提出问题、说明机制、完成主题回报", "lip_sync_dependency": "voice_over_no_visible_mouth", "source_status": "original_voice_confirmed"},
      {"cue_id": "CUE03", "track": "sfx", "timing_or_trigger": "B04 自动化任务完成时", "story_function": "提供流程完成的可听证据", "lip_sync_dependency": "none", "source_status": "licensed_library_confirmed"},
      {"cue_id": "CUE04", "track": "music", "timing_or_trigger": "00:00-00:30，B04 后由循环转开放和弦", "story_function": "把重复压力转为释放", "lip_sync_dependency": "none", "source_status": "licensed_library_confirmed", "audio_motif_id": "AM01"},
      {"cue_id": "CUE05", "track": "silence", "timing_or_trigger": "CUE03 后持续 1 秒", "story_function": "为结果揭示和呼吸反应留空间", "lip_sync_dependency": "none", "source_status": "designed_in_edit"}
    ]
  },
  "story_structure": {
    "structure_type": "角色选择与后果为主，广告回报为辅",
    "target_duration_seconds": 30,
    "opening_state": "使用者被重复日报占满桌面和注意力",
    "beats": [
      {"beat_id": "B01", "function": "Hook", "change": "从机械执行到意识到重复", "cause": "第十次打开同一模板", "effect": "使用者开始寻找替代流程", "visual_evidence": "同名文件与纸张堆叠", "duration_seconds": 5, "cue_ids": ["CUE01", "CUE02"], "audio_motif_id": "AM01"},
      {"beat_id": "B02", "function": "建立阻力", "change": "从怀疑到决定试用自动化", "cause": "重复步骤再次出错", "effect": "使用者启动自动化流程", "visual_evidence": "错误标记出现后手指移向启动键", "duration_seconds": 7, "cue_ids": ["CUE01", "CUE02"]},
      {"beat_id": "B03", "function": "机制与证据", "change": "从等待到看见步骤被压缩", "cause": "自动化流程启动", "effect": "日报在一次操作后完成", "visual_evidence": "多张纸依次消失且完成文件出现", "duration_seconds": 8, "cue_ids": ["CUE01", "CUE04"], "audio_motif_id": "AM01"},
      {"beat_id": "B04", "function": "结果揭示", "change": "从紧绷到确认任务结束", "cause": "完成文件通过校验", "effect": "使用者停止重复动作", "visual_evidence": "完成标记亮起且双手离开键盘", "duration_seconds": 5, "cue_ids": ["CUE03", "CUE05"]},
      {"beat_id": "B05", "function": "Payoff", "change": "从被工作占据到拥有可支配时间", "cause": "重复任务已完成", "effect": "主题在暖光与留白中闭合", "visual_evidence": "空桌、放松肩颈和窗外夕光同框", "duration_seconds": 5, "cue_ids": ["CUE02", "CUE04"], "audio_motif_id": "AM01"}
    ],
    "payoff": "使用者把省下的时间用于停下来观察窗外，而非承接更多重复任务",
    "closing_state": "桌面清空，使用者恢复注意力与选择权"
  },
  "screenplay": {
    "screenplay_status": "approved",
    "target_duration_seconds": 30,
    "scenes": [
      {"scene_id": "S01", "objective": "让观众识别重复劳动及其代价", "conflict_or_question": "同一份日报为什么要手工重做", "action": "使用者打开第十个同名文件，发现错误后停手并启动自动化", "dialogue_or_narration": "同一份日报，为什么每天都要重做？", "emotional_change": "从麻木到不满，由重复错误触发", "visual_evidence": "同名文件、红色错误标记和转向启动键的手", "opening_state": "机械重复且未质疑流程", "closing_state": "决定尝试替代流程", "duration_seconds": 12, "causal_link_from_previous": null, "causal_link_to_next": "启动自动化使流程结果成为下一场待验证的问题", "beat_ids": ["B01", "B02"], "cue_ids": ["CUE01", "CUE02"], "audio_motif_id": "AM01"},
      {"scene_id": "S02", "objective": "用可见流程证明自动化完成任务", "conflict_or_question": "新流程能否可靠完成日报", "action": "步骤依次完成，完成文件通过校验，使用者双手离开键盘", "dialogue_or_narration": "把重复步骤交给流程，一次完成。", "emotional_change": "从怀疑到确认，由完成校验触发", "visual_evidence": "步骤收束为完成文件，校验标记亮起", "opening_state": "流程结果未知", "closing_state": "任务已完成且有证据", "duration_seconds": 13, "causal_link_from_previous": "S01 启动的自动化流程进入结果验证", "causal_link_to_next": "完成校验释放出可支配时间并触发主题回报", "beat_ids": ["B03", "B04"], "cue_ids": ["CUE01", "CUE03", "CUE04", "CUE05"], "audio_motif_id": "AM01"},
      {"scene_id": "S03", "objective": "完成被归还时间的主题回报", "conflict_or_question": "省下的时间最终属于谁", "action": "使用者靠回椅背，转头看向窗外，空桌与夕光保持五秒", "dialogue_or_narration": "更快的意义，是把时间还给你。", "emotional_change": "从确认完成到释然，由可支配时间出现触发", "visual_evidence": "放松肩颈、空桌留白与窗外暖光", "opening_state": "任务结束但价值尚未落地", "closing_state": "时间与选择权回到使用者", "duration_seconds": 5, "causal_link_from_previous": "S02 的完成校验让使用者停止重复劳动", "causal_link_to_next": null, "beat_ids": ["B05"], "cue_ids": ["CUE02", "CUE04"], "audio_motif_id": "AM01"}
    ]
  }
}
```

交给分镜前，标准流程至少已有明确 direction；`one-pass draft` 则必须保留 `draft` 状态与全部可逆假设。无论状态如何，scene 与 beat 都须精确合计 30 秒，所有 cue 引用可解析。只有通过最终共同审批后，`selected_treatment.treatment_status` 与 `screenplay.screenplay_status` 才为 `approved` 并允许进入执行编译。

禁止在这三个顶层对象中提前编译厂商专用提示词、镜头 API 参数、随机种子、采样参数、运动强度数值或队列配置。`continuity-storyboard` 不得反向改写已批准故事决定；共同批准门通过后，再交执行层编译。

## 快速参考

| 问题 | 检查 | 通过标准 |
|---|---|---|
| 这个结构适合题材吗 | 对照结构选择器 | 主结构与目标一致，辅结构不争夺时长 |
| 每场有作用吗 | 状态变化与删除测试 | 每场改变至少一种状态，删除会破坏因果或回报 |
| 节拍可审计吗 | 检查 ID、cause、effect、evidence、seconds | 每项完整且可追溯到 scene |
| 时长可靠吗 | 朗读、动作计时、转场与尾帧账本 | scene 与 beat 总和都精确等于目标 |
| 声音可执行吗 | 检查七类轨道和 cue | 关键信息有可靠通道，口型风险已处理 |
| 结尾完成了吗 | 对照 Hook、戏剧问题或主题张力和 closing state | 承诺被兑现、反转或有意悬置 |
| 可以交给分镜阶段吗 | 检查 direction、草案状态、时长与引用 | direction 已明确，三个顶层对象可审阅，时长与引用有效，无 storyboard 或模型专用参数；`approved` 只作为进入执行编译的前提 |
