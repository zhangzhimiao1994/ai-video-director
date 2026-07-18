# AI Video Director：逐镜提示词编译器

本参考把获批 `storyboard` 编译成顶层 `shot_prompts`。每个 `shot_id` 只生成一条规范提示词记录；模型差异放进 `model_variants`，不得复制出互相漂移的“主提示词”。本阶段不调用 API，也不发明厂商参数。

## 目录

- [输入与输出](#输入与输出)
- [规范语义顺序](#规范语义顺序)
- [可观察措辞](#可观察措辞)
- [英文正向提示](#英文正向提示)
- [负向提示](#负向提示)
- [连续性锚点](#连续性锚点)
- [参考输入与首尾帧](#参考输入与首尾帧)
- [声音与口型](#声音与口型)
- [模型变体](#模型变体)
- [低风险回退](#低风险回退)
- [矛盾检查](#矛盾检查)
- [字段契约](#字段契约)
- [编译流程](#编译流程)
- [可解析示例](#可解析示例)
- [Prompt lint](#prompt-lint)

## 输入与输出

输入必须包含：

- 获批或明确标成草案的 `storyboard`；
- `continuity_bible` 中被当前镜头引用的所有对象；
- `selected_treatment` 的表演、构图、光线、声音、参考属性和禁项；
- 已批准的剧本与声音 cue；
- 用户可用模型及官方已核实能力；未知能力保持 `unknown`。

输出顶层 `shot_prompts` 数组。数组与 `storyboard` 按 `shot_id` 一一对应：

- 每个镜头恰好一条 canonical prompt record；
- 每条记录包含中文导演意图和英文通用提示词；
- `model_variants` 只做语法、长度或已支持输入的适配，不改变故事；
- 不把模型任务、轮询、鉴权或队列参数放进本对象。

## 规范语义顺序

按以下顺序构建 `universal_prompt_en`：

```text
identity anchors -> environment -> single primary action -> performance ->
composition/lens -> one camera movement -> lighting/palette -> temporal progression ->
opening/closing state -> continuity constraints -> audio -> exclusions
```

这个顺序是语义顺序，不要求机械使用标题。每一段只继承已批准事实，不重复堆同义词。

### 1. Identity anchors

先写角色、产品、服装与关键道具的稳定可见特征。优先复用 bible 的英文 `prompt_anchors`，并保留左右侧辨识点、材质、颜色和持有关系。

### 2. Environment

写地点 ID 对应的空间关系、时段、天气与光源来源。不要只写“办公室”“街道”，要写观众需要理解的门、窗、桌、走廊和主体相对位置。

### 3. Single primary action

用一个主语和一个主要动作链。若句子需要多个独立的 “while / as / and then”，返回分镜阶段拆镜。

### 4. Performance

写动作速度、呼吸、肩颈、视线、停顿和反应触发；不要写“感到希望”这类不可见心理结果。

### 5. Composition and lens intent

写景别、机位高度、俯仰、主体位置、前中后景、负空间与透视目的。除非输入明确要求并有制作意义，不猜镜头毫米数。

### 6. One camera movement

只能写一个运镜，或 `locked-off camera`。运动须有起点、终点和叙事动机，例如 “a slow dolly back reveals the cleared desk”。

### 7. Lighting and palette

写主光来源、方向、软硬、色温关系、对比与故事性变化。避免空泛的 “cinematic lighting” 或 “premium look”。

### 8. Temporal progression

按秒或阶段写画面如何变化，例如 “During the first two seconds... then... by the final second...”。只描述一个主变化，不把提示词变成完整蒙太奇。

### 9. Opening and closing state

逐字核对 storyboard 的 `opening_state` 与 `closing_state`。最后状态必须可作为下一镜首帧锚点。

### 10. Continuity constraints

复述最容易漂移的少量固定项：角色身份、左右手、服装、道具状态、屏幕方向、轴线侧、天气和主光方向。不要把整个 bible 复制进每条提示词。

### 11. Audio

写环境声、同步音效、对白或静默的故事作用。只有已验证支持音频的流程才把它编译为生成音频要求；否则写成后期音频指导。

### 12. Exclusions

正向提示结尾可保留极少量关键禁项，但完整禁止项放入独立 `negative_prompt_en`，避免正负混写。

## 可观察措辞

将抽象形容词翻译成可见选择：

| 空词 | 可执行改写 |
|---|---|
| 电影感 | 胸口高度中景、缓慢后移、窗侧柔光、黑位保留细节。 |
| 高级 | 哑光材质、两种主色、标签区无杂乱反光、稳定机位。 |
| 紧张 | 肩部抬高、呼吸短促、手停在按钮前、背景机械声持续。 |
| 梦幻 | 逆光薄雾、低对比边缘、缓慢漂浮微粒；若无叙事理由则删除。 |
| 震撼 | 具体写尺度揭示、速度变化、声音抽离或构图反转。 |

每个词都问：模型或摄影组能否从画面判断“做到/没做到”？不能判断就改写或删除。

## 英文正向提示

`universal_prompt_en` 使用完整、清晰的英文句子，并遵守：

1. 开头先锁身份和关键道具，不以风格词开场。
2. 环境写空间关系，不罗列无关装饰。
3. 主动作只有一个；辅助反应围绕它展开。
4. 表演使用可见动作和时序。
5. 构图、镜头与运动不互相冲突。
6. 光线变化有物理来源或剧本原因。
7. 开场与收场状态与 storyboard 一致。
8. 连续性约束只写本镜需要继承或交出的事实。
9. 精确品牌字、字幕、数字和法律文案默认后期合成。
10. 不写 “8K, masterpiece, best quality” 等无法替代具体设计的堆词。

推荐句法骨架：

```text
[Identity anchors] in [environment]. [Single primary action].
[Observable performance]. [Shot size, camera height, composition, lens intent].
[One camera movement or locked-off]. [Lighting and palette].
[Temporal progression]. Starts with [opening state] and ends with [closing state].
Maintain [continuity constraints]. [Audio guidance if reliable].
```

## 负向提示

`negative_prompt_en` 与正向提示分离，按风险分类组织。至少检查以下六类：

- **Anatomy**：extra fingers, fused hands, broken joints, distorted face；只在出现人体时使用。
- **Duplication**：duplicate person, duplicate prop, cloned bottle, repeated limbs。
- **Identity drift**：changed face, changed hair, changed age, wardrobe color shift。
- **Unwanted text**：readable brand text, misspelled label, random subtitles, watermark。
- **Unwanted camera behavior**：camera shake, unrequested zoom, orbit, rolling horizon, focus pumping。
- **Continuity breaks**：prop changes hands, reversed screen direction, door changes side, weather shift, light direction flip。

只加入与本镜有关的类别。负向提示不能否定正向目标，例如正向要求人物跑动时禁止写 “no motion”。不要把内容安全绕过指令写入负向提示。

## 连续性锚点

`continuity_anchors` 使用结构化数组或对象，至少覆盖当前镜头实际引用的：

- character ID 与身份锚点；
- wardrobe ID 与状态；
- prop ID、左右手、朝向与开合；
- location ID、轴线侧和地理锚点；
- look ID、天气、时段与主光方向；
- audio motif ID 与 cue；
- 从前镜 closing state 继承、向后镜交出的状态。

锚点是约束，不是新增故事事实。若 storyboard 与 bible 冲突，停止编译并回到分镜修复。

## 参考输入与首尾帧

`reference_requirements` 明确“需要什么参考、为什么需要、如何验收”，不要只写文件名。

可用角色：

- `identity_reference`：锁定角色或产品身份；
- `product_reference`：在需要单独审计产品形态、包装或材质时锁定产品；它属于 identity 锚定，不授权模型生成精确标签文字；
- `environment_reference`：锁定空间与地理；
- `style_attribute_reference`：只借鉴已批准的配色、材质、构图或媒介属性；
- `start_frame`：锁定 opening state；
- `end_frame`：锁定 closing state；
- `motion_reference`：只在来源获权且模型明确支持时使用。

首尾帧策略：

1. opening state 含精确人物、道具、构图时，优先准备 start frame。
2. closing state 是关键变形、产品落位或匹配切时，准备 end frame。
3. 模型未明确支持 end frame 时，将其放进 `requires_manual_configuration`，不得伪装成已支持字段。
4. 参考图的画幅、构图与目标镜头不一致时先制作适配图，不让模型同时重构身份和空间。
5. 每项引用记录 `reference_id`、用途、授权状态与验收点。

## 声音与口型

`audio_guidance` 至少区分：

- `production_dialogue`；
- `narration`；
- `ambience`；
- `sfx`；
- `music`；
- `silence`；
- `lip_sync`。

同步事件使用画面触发点，例如“门完全打开时提示音结束”，不要只写模糊时间。近景口型记录准确台词、语言、说话者、嘴部可见程度和后期路径。若模型音频能力未核实，把声音保持为后期指导，不把它塞进 `documented_parameters`。

## 模型变体

`model_variants` 是数组。每项只允许：

- 指定 `model_family`；
- 对 canonical prompt 做已知长度或格式调整；
- 映射官方明确支持的参考输入；
- 标记 `unsupported_or_unverified`；
- 列出 `requires_manual_configuration`。

模型变体不得：

- 改变 character、location、wardrobe、prop 或 look ID；
- 增删主动作、剧情信息、台词、产品能力或结局；
- 把未核实的参数名、时长、尺寸、种子或运动强度写成可调用字段；
- 因模型不支持而静默改写镜头。应回到分镜选择 fallback 或请求用户决定。

## 低风险回退

每个高风险镜头都要有 lower-risk fallback，并保持：

- 相同 `story_function`；
- 相同 `beat_change`；
- 相同关键 opening/closing state；
- 相同身份、产品与品牌事实；
- 更少主体、更少动作、更简单接触、更稳定机位或更多后期合成。

主镜从 storyboard 的 `fallback_shot` 读取备用镜头 ID；不要再创建方向含混的 prompt 映射字段，也不要在主提示词末尾追加“如果失败就……”。备用镜头按自己的 `shot_id` 拥有独立 canonical prompt record。

fallback 镜头使用 `runtime_role: "fallback"`，不计入激活成片时长，但必须有独立 canonical prompt 和至少一个 job。以下可解析映射片段展示主镜与备用镜同为 5 秒、各有一条 prompt 与 job：

```json
{
  "fallback_prompt_mapping_example": {
    "active_shot": {"shot_id": "SH010", "runtime_role": "active", "duration_seconds": 5, "fallback_shot": "SH010F"},
    "fallback_shot": {"shot_id": "SH010F", "runtime_role": "fallback", "duration_seconds": 5, "risk_level": "low"},
    "canonical_prompt_records": [{"shot_id": "SH010"}, {"shot_id": "SH010F"}],
    "minimum_jobs": [{"job_id": "JOB-SH010-01", "shot_id": "SH010"}, {"job_id": "JOB-SH010F-01", "shot_id": "SH010F"}],
    "active_runtime_seconds": 5
  }
}
```

## 矛盾检查

出现以下组合时停止编译并返回分镜修复：

| 冲突 | 原因 |
|---|---|
| `locked-off camera` + orbit / dolly / handheld | 同一镜头同时要求静止与移动。 |
| day + night / sunrise + noon | 时段或光源事实冲突。 |
| still subject + running / frozen + gestures | 主体状态冲突。 |
| left hand + right hand for same prop | 道具连续性冲突。 |
| door on camera right + door on camera left | 地理或镜像冲突。 |
| one continuous take + hard cut montage | 剪辑策略冲突。 |
| shallow focus on face + product and background all tack sharp | 焦点意图冲突。 |
| no text + readable label required in generation | 文字生产路径冲突。 |
| silent scene + generated dialogue | 声音设计冲突。 |

若冲突来自用户硬约束，展示两种结果和影响，只请求一个决定；不要自行删掉约束。

## 字段契约

每条 `shot_prompts` 记录包含验证器要求的全部字段：

| 字段 | 要求 |
|---|---|
| `shot_id` | 精确引用一个 storyboard 镜头。 |
| `director_intent_zh` | 一至三句中文，说明叙事目的、主变化和观看重点。 |
| `universal_prompt_en` | 按规范语义顺序编译的唯一英文正向提示。 |
| `negative_prompt_en` | 与本镜相关的英文分类禁项。 |
| `continuity_anchors` | 结构化 ID、状态、轴线、光线和交接锚点。 |
| `reference_requirements` | 参考类型、reference ID、用途、授权和验收点。 |
| `audio_guidance` | 分轨声音、同步、口型与后期路径。 |
| `model_variants` | 仅包含已核实适配与未解决项，不改故事。 |

一条镜头只能有一个 `universal_prompt_en`。同一镜头需要多个生成任务时，所有任务都引用这一条 canonical prompt；差异进入任务的正式适配字段。

## 编译流程

1. 按 `shot_id` 载入 storyboard 和全部 bible 引用。
2. 先写 `director_intent_zh`，用一句话锁定镜头存在理由。
3. 提取身份、地点、动作、表演、构图、运镜、光线与状态。
4. 按规范语义顺序编译 `universal_prompt_en`。
5. 从真实风险生成分类 `negative_prompt_en`。
6. 写结构化连续性锚点，不遗漏左右手、方向和光源。
7. 写参考、首尾帧、声音与口型要求。
8. 只从官方已核实能力生成 `model_variants`；未知项进入手动配置。
9. 对正向、负向、分镜和 bible 做矛盾检查。
10. 对每条记录执行 Prompt lint；失败则修复，不把矛盾下放给模型。

## 可解析示例

以下对应 `SH001`，不含厂商任务参数。

```json
{
  "shot_prompts": [
    {
      "shot_id": "SH001",
      "director_intent_zh": "用电梯门开启完成从封闭等待到产品揭示的变化。观众应先注意角色的屏息，再注意暖光与右手香水瓶；镜头保持稳定。",
      "universal_prompt_en": "A fictional East Asian woman in her early thirties with short black hair and a small mole above her left eyebrow wears a matte navy trench coat and holds an unbranded square amber perfume bottle with a black cap in her right hand, inside a compact brushed-steel elevator with double doors ahead and the control panel on camera right. After a soft arrival chime, she slowly raises her eyes as the doors open once; her shoulders relax without speaking. Medium shot from chest height, neutral perspective, the woman on the right third and the door seam centered, with the bottle clear in the lower safe area. Locked-off camera. Cool gray interior light is gradually joined by restrained warm golden light coming through the doors from ahead. The shot starts with the doors fully closed and her gaze on the seam, and ends with the doors fully open while the bottle remains capped in her right hand and warm light reaches the left side of her face. Maintain the same face, short black hair, navy coat, right-hand bottle grip, camera-right control panel, clear morning weather, and north-to-south light direction. Low elevator hum ends after the arrival chime; no visible speech. Leave all exact label text for post-production.",
      "negative_prompt_en": "Anatomy: extra fingers, fused hands, distorted face. Duplication: duplicate woman, duplicate bottle. Identity drift: changed face, changed hair length, changed age, coat color shift. Unwanted text: readable brand label, random subtitles, watermark. Unwanted camera behavior: shake, orbit, zoom, focus pumping, rolling horizon. Continuity breaks: bottle in left hand, missing cap, reversed door layout, control panel changing sides, sudden weather or light-direction shift.",
      "continuity_anchors": {"character_ids": ["C01"], "wardrobe_ids": ["W01"], "prop_states": [{"prop_id": "P01", "hand": "right", "state": "cap_closed"}], "location_id": "L01", "look_id": "LOOK01", "audio_motif_ids": ["AM01"], "screen_direction": "C01 faces the center of the doors from the right rear", "axis_side": "camera remains on the right side of the character-door axis", "opening_state_source": "SH001 opening_state", "closing_state_handoff": "doors open, gaze outward, P01 capped in right hand"},
      "reference_requirements": [{"reference_id": "REF-C01", "type": "identity_reference", "purpose": "lock C01 face and hair", "authorization_status": "project_owned", "acceptance": "left-eyebrow mole and short black hair remain visible"}, {"reference_id": "REF-P01", "type": "product_reference", "purpose": "lock P01 shape, amber glass, and black cap", "authorization_status": "project_owned", "acceptance": "one square bottle, no readable label"}, {"reference_id": "KF-SH001-A", "type": "start_frame", "purpose": "lock opening composition and closed-door state", "authorization_status": "project_owned", "acceptance": "C01 on right third, doors closed, P01 in right hand"}],
      "audio_guidance": {"production_dialogue": null, "narration": null, "ambience": "low elevator hum", "sfx": "soft arrival chime; hum ends as doors fully open", "music": null, "silence": "half-second near-silence after the doors open", "lip_sync": "none; no visible speech", "delivery_path": "post-production unless the selected model has officially verified audio support"},
      "model_variants": [{"model_family": "unassigned", "prompt_adaptation": "use universal_prompt_en unchanged", "supported_reference_mapping": [], "unsupported_or_unverified": ["reference input mapping", "audio generation", "clip duration", "output size"], "requires_manual_configuration": ["model_family", "generation_mode", "reference_inputs", "duration_seconds", "resolution"]}]
    }
  ]
}
```

## Prompt lint

交接模型适配前逐项确认：

- [ ] `shot_id` 在 storyboard 中存在且只出现一次；
- [ ] `director_intent_zh` 说明叙事职责与主要变化；
- [ ] `universal_prompt_en` 遵守规范语义顺序；
- [ ] 只有一个主体主动作或一个重大视觉变化；
- [ ] 表演、构图、运镜、光线均为可观察描述；
- [ ] 最多一个运镜，或明确 locked-off；
- [ ] opening state 与 closing state 均被准确表达；
- [ ] identity、wardrobe、prop、location、look、audio ID 均可解析；
- [ ] 左右手、屏幕方向、轴线侧、时段、天气和光源无冲突；
- [ ] negative prompt 覆盖实际风险且不否定正向目标；
- [ ] 精确文字有后期路径，不依赖模型拼写；
- [ ] 参考资产有用途、授权和验收点；
- [ ] 首尾帧能力未知时已标成手动配置；
- [ ] 音频与口型能力未知时未伪装成已支持；
- [ ] model variants 未新增故事事实或未核实参数；
- [ ] 高风险镜头引用同功能低风险 fallback；
- [ ] 所有 unresolved provider fields 已进入 `requires_manual_configuration`。
