# AI Video Director：制片会议参考

本参考只负责把用户意图转成可批准、可执行的顶层 `project_brief` 与 `creative_directions`。先完成制片判断，再把已批准结果交给故事导演；不要在本阶段写完整剧本、逐镜分镜或模型参数。最终完整包以 `output-contract` 为唯一契约；本参考中的 JSON 仅展示顶层片段。

## 目录

- [会议原则](#会议原则)
- [信息采集顺序](#信息采集顺序)
- [实质性提问规则](#实质性提问规则)
- [未限定时长的处理](#未限定时长的处理)
- [`project_brief` 字段契约](#project_brief-字段契约)
- [简短确认摘要](#简短确认摘要)
- [三个创意方向](#三个创意方向)
- [批准门](#批准门)
- [约束冲突处理](#约束冲突处理)
- [常见错误](#常见错误)
- [快速参考](#快速参考)

## 会议原则

1. 像专业制片会议一样推进：先确定结果，再讨论形式。
2. 一次只问一个会实质改变结果的问题；收到回答后再决定是否需要下一问。
3. 复述已知事实，不让用户重复提供已经明确的信息。
4. 区分“用户事实”“制片建议”“可逆假设”，不得把推测写成已确认事实。
5. 暴露成本、版权、真人、模型能力与交付风险，不用漂亮描述掩盖生产约束。
6. 在方向获批前保持方案轻量；方向未选定时禁止写完整剧本。

## 信息采集顺序

按以下顺序检查信息。只问当前最先出现且具有实质性的缺口，不要把清单一次性抛给用户。

1. **目标与期望观众反应**：明确视频要完成什么任务，以及希望观众看完后产生何种认知、情绪或行动。
2. **受众与平台**：明确核心受众、观看语境、发布平台、是否静音首播、是否需要前几秒抓取注意力。
3. **题材、基调与叙事视角**：明确作品类型、情绪温度、严肃度、幽默尺度，以及第一人称、第三人称或观察式视角。
4. **源材料**：收集文案、脚本、采访、产品资料、品牌规范、数据来源与素材授权状态；标记哪些内容必须原样保留。
5. **时长**：记录目标秒数、允许误差与平台上限；用户未限定时长时执行下节流程。
6. **画幅与交付**：明确 `aspect_ratio`、分辨率、帧率、字幕版本、语言版本、透明通道、首尾帧与文件格式。
7. **人物、地点、道具与参考**：确认角色数量、外观连续性、场景数量、关键道具、视觉参考和禁止参考。
8. **对白、旁白、音乐与口型**：区分同期对白、旁白、环境声、音效、音乐、静默与 lip-sync；确认声音版权和语言。
9. **可用模型**：记录用户可访问的生成模型、镜头长度限制、输入类型、音频能力、文字渲染能力和区域限制。
10. **预算、资源与难镜容忍度**：确认可用时间、算力或额度、真人拍摄素材、后期能力、返工轮次，以及对高失败率镜头的容忍度。

检查完毕后，将信息写入 `project_brief`；不要用会议记录替代字段化简报。

## 实质性提问规则

仅当答案会改变以下任一结果时提问：

- 故事内容、结局、叙事视角或角色关系；
- 目标受众、平台观看语境或期望观众反应；
- 总时长、节奏密度或交付规格；
- 真人肖像、版权、授权、商标或其他法律风险；
- 模型选择、制作路径、成本或失败率。

执行规则：

1. **完整且锁定**：当 `brief_status: locked` 且字段足以执行时，直接进入下一阶段；禁止重复询问。只有新指令引入实质冲突或新增风险时，才重新确认相关字段。
2. **缺失**：缺口符合实质性条件时，问一个优先级最高的问题。
3. **含义不清**：同一句话存在两种会导致不同成片的解释时，列出两种解释并只问用户选择哪一种。
4. **冲突**：指出冲突字段、各自后果和推荐解法，再请求一个明确选择。
5. **小缺失**：若不改变上述实质结果，给出可逆推荐并写入 `assumptions`，明确标注“制片建议、尚未批准、可逆”；继续推进，不追加问题。
6. **禁止连问**：同一消息中不得堆叠多个问题。可先提供当前摘要与建议，末尾只保留一个问题。

提问优先级为：合法与真人风险 > 目标与受众 > 时长与交付 > 模型与成本 > 美术偏好。

## 未限定时长的处理

用户未给出时长时，不要自行锁定秒数，也不要直接开始正式分镜。

1. 根据交付场景给出一个推荐值和一个可接受区间：
   - 社交信息流广告：推荐 15–30 秒，强调单一卖点与快速回报；
   - 产品或品牌说明：推荐 30–60 秒，容纳问题、证据与行动；
   - 知识口播：推荐 45–90 秒，容纳上下文、要点与例证；
   - 剧情短片：推荐 60–180 秒，容纳角色目标、转折与结局；
   - 音乐或概念片：根据曲段或视觉母题推荐 30–120 秒。
2. 解释节奏影响：时长越短，角色、地点和转折必须越少；时长越长，必须增加因果进展，不能只拉长氛围镜头。
3. 给出一个具体推荐，例如“建议 45 秒，因为需要 Hook、两项证据和结尾行动，每项至少占一个节拍”。
4. 标准流程在进入正式分镜前请用户确认 `target_duration_seconds`，不可由默认值替代。若用户明确启用 `one-pass draft`，可采用上一步的具体推荐值作为暂定正数时长，但必须写入 `assumptions`，标记 `approval_status: unapproved`、`reversible: true` 及改时长会影响的节拍、镜头与任务；进入执行编译前仍须确认。

## `project_brief` 字段契约

输出结构必须包含下列字段。字段没有信息时使用 `null`、空数组或键值完整的对象，并按实质性规则决定提问或建立可逆假设。以下是可解析的最小顶层片段，不使用未定义伪类型：

```json
{
  "project_brief": {
    "brief_status": "approved",
    "target_duration_seconds": 30,
    "aspect_ratio": "9:16",
    "platform": "竖屏社交信息流，默认静音首播",
    "audience": "首次接触产品、希望快速理解价值的成年用户",
    "objective": "用一次可见演示解释产品如何减少重复操作",
    "desired_response": "观众理解核心机制并点击了解详情",
    "genre": "产品演示广告",
    "tone": ["清晰", "克制", "可信"],
    "story_pov": "跟随使用者观察操作前后的变化",
    "characters": [{"character_id": "C01", "story_function": "演示者", "visible_traits": ["蓝色外套"], "continuity": ["外套与发型全片一致"], "person_status": "fictional", "authorization_status": "project_owned"}],
    "locations": [{"location_id": "L01", "story_function": "展示重复工作的办公室", "time": "白天", "spatial_relations": ["人物面对桌面终端"], "continuity": ["桌面道具位置保持一致"]}],
    "references": [{"reference_id": "REF01", "source": "用户自有产品照片", "borrow_attributes": ["产品配色"], "prohibited_copy_or_imitation": ["第三方标识"], "authorization_status": "confirmed"}],
    "rights_and_consents": [{"subject_id": "C01", "asset_type": "fictional_character_design", "rights_holder": "项目方", "consent_status": "confirmed", "usage_scope": "本项目宣传视频", "media": ["社交平台视频"], "territory": ["中国大陆"], "valid_from": "2026-07-18", "valid_until": "2027-07-17", "guardian_consent": "not_applicable", "voice_clone_consent": "not_applicable", "source_record": "脱敏资产登记 AR-01", "revocation_constraints": "发布前可撤回", "verification_status": "verified"}],
    "audio": {"dialogue": [], "narration": {"language": "zh-CN", "required": true}, "ambience": ["办公室底声"], "sfx": ["完成提示音"], "music": {"source": "licensed_library", "license_status": "confirmed"}, "silence": [{"purpose": "结尾回报", "duration_seconds": 1}], "lip_sync": {"required": false}},
    "models": [{"model_id": "unknown", "availability": "unknown", "capabilities": {"aspect_ratio": "unknown", "shot_duration_seconds": "unknown", "audio": "unknown", "text_rendering": "unknown"}, "capability_evidence": {"source": "unknown", "verified_at": null, "test_evidence": "unknown"}}],
    "resources": {"production_days": 3, "generation_credits": 50, "source_assets": ["产品照片"], "people": ["剪辑师"], "post_capabilities": ["字幕合成"], "revision_rounds": 2},
    "constraints": [{"constraint_id": "K01", "strength": "hard", "source": "平台交付", "rule": "9:16 竖屏", "acceptance": "1080x1920"}],
    "assumptions": [{"assumption_id": "A01", "field": "music", "recommendation": "使用已授权轻节奏器乐", "basis": "对白可读性优先", "reversible": true, "approval_status": "unapproved", "reversal_impact": "只需替换音乐轨"}],
    "risks": [{"risk_id": "R01", "trigger": "模型能力证据仍为 unknown", "probability": "medium", "impact": "长动作可能返工", "mitigation": "先生成 4 秒动作小样", "decision_owner": "用户"}]
  }
}
```

字段要求：

| 字段 | 要求 |
|---|---|
| `brief_status` | `draft` 表示仍可改；`approved` 表示内容获批但可通过新决策更新；`locked` 表示不重复询问并直接执行。 |
| `target_duration_seconds` | 使用正整数秒；标准流程正式分镜前须确认。`one-pass draft` 可使用明确标记为未批准、可逆并附影响说明的暂定值，但执行编译前必须确认。 |
| `aspect_ratio` | 使用明确比例，如 `9:16`、`16:9` 或 `1:1`，同时在约束中记录分辨率等交付条件。 |
| `platform` | 写平台和观看语境，不只写“线上”。 |
| `audience` | 写核心人群、已有认知与主要阻力。 |
| `objective` | 写视频要完成的单一首要任务。 |
| `desired_response` | 写观众看完后的可观察情绪、理解或行动。 |
| `genre` | 写作品类型；不要用单纯视觉风格代替题材。 |
| `tone` | 用可执行的基调词，并给边界，例如“克制幽默，不做嘲讽”。 |
| `story_pov` | 写谁在感知、知道和解释事件。 |
| `characters` | 每项至少含 `character_id`、角色功能、可见特征、连续性要求、真人或虚构状态、授权状态。 |
| `locations` | 每项至少含 `location_id`、叙事功能、时间、关键空间关系和连续性要求。 |
| `references` | 每项至少含 `reference_id`、来源、`borrow_attributes`、`prohibited_copy_or_imitation` 与授权状态；故事阶段原样继承这些键，引用不等于获权。 |
| `rights_and_consents` | 每项必须含 `subject_id`、`asset_type`、`rights_holder`、`consent_status`、`usage_scope`、`media`、`territory`、`valid_from`、`valid_until`、`guardian_consent`、`voice_clone_consent`、`source_record`、`revocation_constraints`、`verification_status`。只收集判断授权范围所需的最少信息，证明须脱敏；不要索取身份证件或完整合同。 |
| `audio` | 分列 dialogue、narration、ambience、sfx、music、silence、lip_sync 和语言要求。 |
| `models` | 每项记录 `model_id`、可用状态、能力与 `capability_evidence`。能力结论只依据用户提供的限制、当前官方文档或已测结果，并记录 `source`、`verified_at`、`test_evidence`；无法核实时三个证据字段写 `unknown` 或 `null`，并建议先做小样。 |
| `resources` | 记录预算或额度、工期、现有素材、人员、后期能力和允许返工轮次。 |
| `constraints` | 每项写 `constraint_id`、硬性或软性、来源、验收方式。 |
| `assumptions` | 每项写 `assumption_id`、相关字段、制片建议、依据、`reversible: true`、未批准状态与逆转影响。 |
| `risks` | 每项写 `risk_id`、触发条件、概率、影响、降低措施、需谁决定。 |

不得把 `brief_status` 自动提升为 `approved` 或 `locked`。只有用户明确批准、锁定，或原始简报已声明相同状态时才更新。

## 简短确认摘要

在需要批准简报时使用以下紧凑格式，不重抄所有字段：

```text
简报确认｜状态：draft
目标：让[受众]在看完后[期望反应]
交付：[平台]｜[时长]秒｜[画幅]
故事：[题材]｜[基调]｜[叙事视角]
制作边界：[最关键的资源或模型约束]
可逆假设：[assumption_id + 建议]；无则写“无”
首要风险：[risk_id + 后果]；无则写“无”
请确认：批准这份简报，还是修改[唯一一个实质字段]？
```

摘要末尾只能出现一个问题。用户回复“批准”后将状态改为 `approved`；用户明确要求锁定后改为 `locked`。

## 三个创意方向

标准流程在简报获批后输出顶层 `creative_directions` 数组；若用户明确启用 `one-pass draft`，则允许 brief 保持 `draft`，但必须先记录全部可逆假设与风险，再生成同样结构的草案方向。数组恰含三个实质不同的 direction 对象，每个对象含全部规定字段：

```json
{
  "creative_directions": [
    {"direction_id": "D1", "logline": "使用者把重复步骤压缩成一次动作", "audience_promise": "让首次接触产品的观众直观看见重复工作如何被减少", "hook": "同一任务为何做了第十遍？", "emotion": "疲惫到释然", "visual_concept": "堆积纸张随自动化完成逐层消失", "story_structure": "角色选择与后果", "recommended_duration_seconds": 30, "signature_image": "人物在清空的桌面前停下一秒", "difficulty": "medium", "model_risks": ["纸张数量连续性"], "fit": "适合强调可见效率变化"},
    {"direction_id": "D2", "logline": "用计时对照证明新流程的速度", "audience_promise": "让重视证据的观众通过可核验对照理解产品价值", "hook": "左右两块计时器同时启动", "emotion": "怀疑到信服", "visual_concept": "分屏实验与单一指标递进", "story_structure": "问题、证据与揭示", "recommended_duration_seconds": 20, "signature_image": "一侧计时仍在运行，另一侧已经完成", "difficulty": "low", "model_risks": ["精确数字须后期合成"], "fit": "适合重视证据的受众"},
    {"direction_id": "D3", "logline": "重复循环在关键一刻被打破", "audience_promise": "让偏好品牌感的观众记住从重复束缚到轻盈释放的视觉转变", "hook": "相同动作连续三次，但第四次世界改变", "emotion": "压迫到轻盈", "visual_concept": "循环构图逐次减少视觉负担", "story_structure": "视觉母题递进与反转", "recommended_duration_seconds": 30, "signature_image": "循环轨迹化成通往出口的一条线", "difficulty": "high", "model_risks": ["重复动作一致性"], "fit": "适合以视觉记忆点建立品牌感"}
  ]
}
```

每个方向都必须明确填写 `audience_promise`，说明该方案向目标受众承诺的理解、情绪或行动回报；同时填写正数 `recommended_duration_seconds`，并让推荐秒数与该方向的结构、节拍密度和制作风险相匹配。推荐时长是方向提案，不得静默覆盖已批准的 `project_brief.target_duration_seconds`；两者不同时必须在 Direction Gate 请求用户确认。

三个方向必须使用不同的叙事机制，例如：

- 方向一由角色选择与后果驱动；
- 方向二由问题、证据与揭示驱动；
- 方向三由视觉母题的递进与反转驱动。

至少在 `hook`、`story_structure`、`signature_image`、情绪路径或制作方法中的三项形成差异。禁止把同一概念换标题、换色调或换地点后冒充新方向。

每个方向只写足以做选择的提案，不写完整场景、完整对白或逐镜头列表。给出制片推荐及理由后，只问用户选择 D1、D2、D3 或要求定向混合。用户未选择前，禁止进入完整剧本。选中后把 `direction_id` 交给故事阶段；故事阶段统一输出并使用顶层 `selected_treatment`，不得改名为其他 treatment 键。

## 批准门

按以下顺序设置审批：

1. **Brief Gate**：确认目标、受众、时长、交付、关键约束与风险；输出 `approved` 或 `locked` 的 `project_brief`。
2. **Direction Gate**：展示三个机制不同的创意方向；记录用户选择的 `direction_id` 或明确的混合规则。
3. **Screenplay + Storyboard Gate**：`screenplay` 由故事导演产出，`storyboard` 由后续 `continuity-storyboard` 阶段产出；二者齐备后共同审批，再进入模型执行编译。

若用户明确要求 `one-pass draft`，可以跳过中间批准门，但必须：

- 将所有未经确认的信息列入 `assumptions`；
- 标明每项假设可逆，以及修改会影响哪些后续输出；
- 把结果标记为草案，不把自动选择表述为用户批准；
- 仍然执行版权、真人、法律与模型能力检查；
- 允许用户回到任一批准门修改。

`one-pass draft` 允许 `draft` 状态的 brief、treatment、screenplay 与 storyboard 继续向后组装，以便一次看到完整草案；这不是新增批准门，也不允许进入真实 API 执行。标准流程中，Direction Gate 后可把 draft treatment 与 screenplay 交给分镜共同迭代；只有最终 **Screenplay + Storyboard Gate** 才把共同审阅的故事对象与 storyboard 标成可执行批准状态。

## 约束冲突处理

发现冲突时，先展示检测证据、风险和可选路径，再一次只请求一个决定。

| 冲突 | 检测 | 风险 | 应对 |
|---|---|---|---|
| 故事超时 | 按对白朗读、动作、转场与尾帧估时后超过 `target_duration_seconds`。 | 节拍拥挤、对白听不清或镜头总时长不合规。 | 给出删节拍、压缩信息或增加时长三种影响，推荐一种并请求确认。 |
| 角色过多 | 短时长内每个角色没有可辨功能、出场时间或连续性资源。 | 观众识别失败，生成一致性和成本恶化。 | 合并功能相同角色、改为画外信息或增加时长；列出合并后损失。 |
| 一镜到底 | 对照用户提供的限制、当前官方文档或已测结果；逐项记录 `source`、`verified_at`、`test_evidence`，证据缺失时能力写 `unknown`。 | 连续长动作可能漂移、身份变化或动作断裂，局部错误可能要求整镜重做；未知能力会放大成本不确定性。 | 能力为 `unknown` 时先建议生成代表性小样；再提供“保留真实一镜到底”“使用隐藏剪辑保持连续感”“拆成明确镜头”三选一，必须请求用户选择。 |
| 真人肖像或授权 | 出现可识别真人、客户素材、未成年人、名人或声音克隆，而授权记录缺失、待处理、拒绝、未验证、已过期、被撤销、超出用途/媒介/地域/期限，或缺少监护人、声音克隆专项同意。 | 肖像权、隐私、冒用与平台合规风险。 | 将该授权视为不可用并暂停相关设计；请求最少且可脱敏的有效记录，或改用明确虚构角色、已授权素材。 |

只有 `consent_status` 已确认、`verification_status` 已验证、当前日期处于有效期内、用途/媒介/地域均覆盖本项目，且适用的监护人同意与声音克隆专项同意有效时，授权才可用于生产。任一条件为 `pending`、`denied`、`unverified`、`expired`、`revoked`、`unknown` 或范围不符，都必须保持阻断；不得因“已有一条记录”而视为获权。
| 在世艺术家风格或版权参考 | 指令要求直接复刻在世艺术家风格，或参考材料的角色、构图、音乐、商标受保护。 | 风格模仿、版权、商标或来源误认风险。 | 抽取非专属高层特征，如媒介、年代、色彩和构图原则；移除可识别受保护元素并记录来源。 |
| 口型 | 存在近景可见嘴部、精确台词、多语言或模型缺乏可靠 lip-sync。 | 口型错位、表演僵硬、返工增加。 | 缩短台词、改旁白或画外音、避免持续嘴部特写，或选用支持口型的流程；让用户确认内容与成本取舍。 |
| 屏幕精确文字 | 剧情依赖可读品牌名、数字、字幕、界面或法律文案，而生成模型文字不稳定。 | 错字导致信息错误、品牌损害或法律风险。 | 在画面生成阶段预留干净区域，精确文字由后期合成；把文案列为验收资产。 |
| 模型不支持 | 所选模型不支持所需画幅、时长、音频、输入参考、地区或输出格式。 | 任务无法执行，或隐性转码造成质量与成本损失。 | 更换已可用模型、拆分流程或降低要求；明确质量、工期、成本差异后请求决定。 |

### 一镜到底专门话术

```text
这条连续镜头包含[长度/动作/迁移/角色]。能力证据：source=[用户限制/当前官方文档/已测结果/unknown]，verified_at=[日期/null]，test_evidence=[证据/unknown]。若为 unknown，建议先做[代表性秒数与动作]小样；主要风险是[具体失败]，且任一局部错误都可能要求整镜重做。
请选择：A 保留真实一镜到底并接受高返工；B 用隐藏剪辑保留连续观感；C 拆成明确镜头以提高稳定性。
```

不得默认选择 B 或 C。用户选择前保持该约束未变。

## 常见错误

| 错误 | 为什么失败 | 修正 |
|---|---|---|
| 基线 A：把一句含义不清的想法直接扩写成完整故事 | 目标、受众和时长被代理自行决定，返工发生在最昂贵阶段。 | 先按实质性规则问一个关键问题，建立并批准 `project_brief`。 |
| 基线 B：只给一个方向，或把同一概念换三个标题 | 用户无法比较机制，选择只是措辞偏好。 | 输出三个含全部字段且叙事机制不同的方向；未选定前不写完整剧本。 |
| 基线 D：把高负载一镜到底静默拆镜，或不提示风险 | 违背用户约束，也隐藏模型失败率和返工成本。 | 先解释风险，提供真实一镜、隐藏剪辑、明确拆镜三选一，并等待选择。 |
| 对锁定简报重复盘问 | 浪费时间并削弱已经作出的决定。 | `brief_status: locked` 且可执行时直接推进，只处理新冲突。 |
| 一次发送完整问卷 | 用户难以判断优先级，回答容易互相冲突。 | 每次只问一个会改变结果的问题。 |
| 把小偏好当阻塞项 | 会议停滞，用户被迫做低价值决定。 | 写入标明未批准、可逆的 `assumptions`，并继续推进。 |
| 把参考图当授权证明 | 来源与使用权被混为一谈。 | 在 `references` 中分别记录来源、借鉴维度与授权状态。 |
| 方向阶段提前写模型提示词 | 创作决策被模型语法绑死。 | 只写方向提案；模型参数留给批准后的执行编译。 |

## 快速参考

| 当前状态 | 立即动作 | 禁止动作 |
|---|---|---|
| 想法短且关键含义不清 | 找出最高优先级实质缺口，只问一个问题 | 直接扩写完整故事 |
| 简报完整且 `locked` | 直接生成三个方向或执行已选方向 | 重复询问已锁字段 |
| 只有小缺失 | 给可逆推荐，写入 `assumptions` | 把小偏好变成阻塞问题 |
| 时长未限定 | 按场景推荐区间并解释节奏；标准流程确认具体秒数，`one-pass draft` 记录未批准暂定值与影响 | 未确认却进入执行编译 |
| 简报已批准、方向未选 | 给三个机制不同的方向 | 完整剧本与逐镜分镜 |
| 一镜到底与能力冲突 | 解释风险，给三选一并等待选择 | 擅自隐藏剪辑或拆镜 |
| 用户要求 `one-pass draft` | 标记草案、假设和可逆影响，执行风险检查 | 冒充已获批准 |
| 剧本与分镜已批准 | 交给后续执行编译 | 在制片会议重复设计故事 |
