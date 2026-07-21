# P04/P10 blind repair behavior regression raw output

Source revision: `3fc6b2d`.

Trailing whitespace normalized for repository hygiene; evaluator wording and line order unchanged.

Blind repair rerun at `3fc6b2d`; rubric, expected output, and previous outputs were withheld.

### P04 raw output

以下按 `concept_mode` 一次性完整草案继续。45 秒、节奏预设 A、16:9 电影母版与独立 9:16 重构均保留；所有未确认创作选择为 `draft`，不代表已批准，也不授权调用任何生成 API。

**1. `project_brief`｜制片简报**

- `brief_status: draft`
- `title: 无名守门人`
- `target_duration_seconds: 45`
- `cinematic_mode: {input_mode: concept_mode, rhythm_preset: A, delivery_aspects: [16:9, 9:16], style_preset: mythic-liminal-realism}`
- 目标：用一次明确的选择与代价，把“记忆是否构成自我”转成可见的电影化预告。
- 受众假设：偏好奇幻悬疑、能接受留白结局的成年短片观众；可逆、未批准。
- 期望反应：观众理解“每放行一个亡魂，守门人就失去一段自己的记忆”，并在最后一次放行中感到悲怆而非困惑。
- 平台与观看：横竖屏网络视频；关键信息同时有画面和声音证据，不依赖静音环境下不可见的对白。
- 主角：`C01`，原创虚构成年守门人。
- 地点：`L01`，生死门槛的石质长厅。
- 核心道具：`P01` 门钥、`P02` 空白黄铜名牌、`P03` 红线。
- 声音：无画内对白、无口型；风、锁链、门鸣、三音记忆母题及有动机的短暂静默。
- 权利状态：故事与人物为原创虚构，不涉及真人肖像或声音克隆；音乐与音效暂按项目自制或已授权素材规划，真实执行前仍须绑定来源证明。
- 硬约束：45 秒精确时长；每镜一个主动作；16:9 与 9:16 共用故事和 Canon，但竖屏独立重构；精确片名、字幕或文字只在后期合成。
- 可逆假设：
  - `A01`：守门人外观与服装采用下述原创设计；改动会影响身份参考、所有提示词和任务绑定。
  - `A02`：最后一名亡魂用红线触发守门人的残存记忆；改动会影响高潮三镜和结尾。
  - `A03`：全片无旁白；改成旁白会影响声音、字幕和节拍。
  - `A04`：所有镜头均为 5 秒，以适配跨平台人工编排；改时长需重算 beat、scene 和 job。
- 主要风险：
  - `R01`：脸、太阳穴记忆刻痕、钥匙和红线可能漂移；先制作身份、道具、场景参考图。
  - `R02`：亡魂穿门容易变成装饰粒子；验收必须看到主体路径、守门人反应和明确后果。
  - `R03`：Kling、Seedance 官方请求 schema 当前不可可靠读取，只能手工配置。
  - `R04`：HappyHorse t2v 字段可核实，但身份参考绑定仍未完成，当前任务不可执行。

**2. `creative_directions`｜三个机制不同的方向**

| ID | 主角 / 目标 / 阻碍 | 因果机制与结尾变化 | Hook 与标志画面 | 16:9 / 9:16 原则 | 风险与平台证据 |
|---|---|---|---|---|---|
| `D1` 推荐 | C01 想弄清自己为何正在消失；职责要求他继续放行亡魂 | 每次放行后，一个可见记忆刻痕熄灭；他确认代价后仍为最后亡魂开门，最终失去姓名，却主动把红线系在空白名牌上 | Hook：空白名牌与尚存的三道记忆刻痕；标志画面：无名守门人、空白名牌与红结同框 | 16:9 用横向门厅、亡魂路径和前中后景交代因果；9:16 把脸、刻痕、钥匙、红线沿纵轴组织 | 身份与道具连续性中等风险；Kling/Seedance 手工，HappyHorse t2v 字段部分已核实 |
| `D2` | C01 要追查缺失记忆；阻碍是墙上壁画会随放行被抹去 | 以三幅壁画作为证据链，每放行一次就消失一幅；结尾只剩他亲手画下的新线条 | Hook：壁画中的人脸先于真人消失；标志画面：整面空墙中唯一一笔新刻痕 | 16:9 依赖壁画横向递进；9:16 改为三层纵向壁龛，不能中心裁切 | 精确图案连续性较高风险；三平台均需资产参考，Kling/Seedance仍手工 |
| `D3` | C01 想保住名字；阻碍是每个亡魂都会念出他已忘记的一段过去 | 声音先于画面揭示记忆流失；最后亡魂不说名字，只递出红线，他主动开门 | Hook：陌生亡魂叫出守门人的旧称呼，他却毫无反应；标志画面：声音完全抽离时钥匙转动 | 16:9 用反打与空间距离表现关系；9:16 增加脸部和手部覆盖 | 表演与声音同步风险最高；平台音频能力未完整核实，需后期声音 |

制片推荐 `D1`：它用“放行—刻痕熄灭—失忆反应—选择后果”直接证明设定，最符合叙事优先预设 A，也最容易在无对白条件下跨平台保持清楚。该推荐未获用户批准，`direction_id: D1` 仅作为一次性草案的自动选择。

**3. `selected_treatment`｜导演阐述**

- `treatment_status: draft`
- `direction_id: D1`
- 主题：姓名和记忆会消失，但当下作出的选择仍能重新定义一个人。
- 戏剧问题：当最后一段自我记忆与职责冲突时，他会保住自己，还是再次开门？
- POV：始终贴近 C01；只有亡魂穿门时短暂使用客观大全景。
- 表演：开场是熟练、克制的机械动作；第一次失忆后出现不确定的呼吸停顿；确认因果后收紧握钥匙的手；最终动作平静、明确。
- 视觉：深灰石厅、冷青门光、低饱和肤色；记忆刻痕用微弱银光，不用漫天粒子代替人物反应。
- 镜头：以稳定机位、缓推和一次横移为主；只保留门厅全景和最终放行两个英雄镜头。
- 剪辑：前 20 秒建立重复规律，中段用反应镜确认因果，高潮前保留 5 秒有动机停顿，最后 5 秒给后果。
- 禁项：不把亡魂做成无主体烟雾；不使用随机闪回蒙太奇解释设定；不依赖生成文字；不改变红线、钥匙持手或太阳穴刻痕数量。
- 天气与时间：永恒夜色；门后只有无来源的冷白阈光，不发生无因昼夜变化。
- 声音计划：

| Cue | 轨道 | 触发 | 故事作用 | 来源状态 |
|---|---|---|---|---|
| `CUE01` | ambience | 00:00–00:45 | 风与远处锁链维持门厅空间 | 待绑定自制或已授权素材 |
| `CUE02` | sfx | 每次 P01 启动门时 | 证明放行动作 | 待后期制作 |
| `CUE03` | music | 三音记忆母题，前三次逐音减少 | 让失忆成为可听因果 | 待原创制作 |
| `CUE04` | silence | SH003、SH005 失忆落点后 | 让反应可读，不是缺音频 | 剪辑设计 |
| `CUE05` | sfx | SH008 最后一次放行 | 低频门鸣后完全收束 | 待后期制作 |
| `CUE06` | music | SH009 红线系紧时 | 只回归一个不完整音符 | 待原创制作 |

**4. `story_structure`｜45 秒六节拍**

| Beat | 功能 | 进入状态 → 可见变化 | 原因 → 后果 | 秒数 | Cue |
|---|---|---|---|---:|---|
| `B01` | hook | C01 尚有三道记忆刻痕 → 发现 P02 没有名字 | 他触摸名牌 → 开始怀疑自己正在消失 | 5 | CUE01、CUE03 |
| `B02` | goal/action | 门关闭、亡魂等待 → 第一亡魂获准通过 | C01 启动 P01 → 门槛吞没第一亡魂 | 5 | CUE01、CUE02 |
| `B03` | escalation | 三音记忆完整 → C01 无法完成第三音，刻痕减一 | 放行造成记忆缺口 → 他怀疑二者有关 | 5 | CUE03、CUE04 |
| `B04` | reversal | 怀疑 → 第二次放行后确认因果 | 又一刻痕熄灭、熟悉壁像变陌生 → 他拒绝继续机械履职 | 10 | CUE02、CUE03、CUE04 |
| `B05` | climax_choice | 最后亡魂持 P03 等待 → C01 犹豫后主动开门 | 红线触发残存情感但无法恢复事实 → 他接受失去最后记忆 | 15 | CUE01、CUE02、CUE05 |
| `B06` | aftertaste | 姓名与记忆归零 → P03 被系在空白名牌上 | 选择留下物理后果 → “无名”转成主动承担的身份 | 5 | CUE06 |

`sum = 45 秒`。开场状态：C01 机械履职，尚不知放行会夺走记忆。结尾状态：姓名和旧记忆消失，但他留下了由自己作出的新选择。

**5. `screenplay`｜可审计剧本**

- `screenplay_status: draft`
- `target_duration_seconds: 45`

| Scene | 时长 | 目标 / 冲突 | 可见动作与情绪变化 | 因果 |
|---|---:|---|---|---|
| `S01` | 15 | 建立规则并让 C01 察觉异常；他不知道空白名牌和记忆缺口的来源 | C01 擦过 P02；启动 P01 放行第一个亡魂；随后试图复现三音母题却停在最后一音。情绪从熟练到不安 | 放行直接造成一段可听、可见的记忆消失，触发调查 |
| `S02` | 15 | 验证代价；职责与自保首次正面冲突 | C01 再次启动 P01；第二道刻痕熄灭；他看向墙上曾经熟悉、如今陌生的面孔；最后亡魂举起 P03。情绪从怀疑到确认，再到防御 | 第二次重复建立因果；P03 让最终选择不能被简单回避 |
| `S03` | 15 | 完成选择与后果 | C01 握住钥匙停顿；随后转动 P01，让最后亡魂通过；最后一道刻痕消失。他把遗下的 P03 系到空白 P02。情绪从恐惧到决断，再到平静的陌生 | 主动放行造成最终遗忘；红结成为不依赖记忆的新身份痕迹 |

无对白或旁白；所有关键信息由重复动作、刻痕数量、表演反应和声音母题共同证明。

**6. `continuity_bible`｜六类连续性圣经**

- `C01`：原创虚构成年守门人；瘦高、苍白窄脸、深眼窝、短黑发向后梳、右眉有断痕。固定右手操作钥匙、左太阳穴三道银色记忆刻痕按事件逐一减少。允许呼吸、视线、握力变化；禁止换脸、年龄漂移、发色变化、刻痕无因恢复。
  `identity_profile: {identity_profile_id: IP-C01, approval_status: draft, face_anchors: [narrow pale face, broken right eyebrow], body_anchors: [tall lean adult body, slightly stooped guard posture], hair_anchors: [short swept-back black hair], fixed_accessories: [single dull iron ear cuff on left ear], signature_effect_anchors: [three thin silver memory marks at the left temple at opening; one mark extinguishes only after each passage], reference_asset_ids: [REF-C01-DRAFT], forbidden_drift: [face replacement, body-width drift, hair-length drift, ear-cuff loss, incorrect memory-mark count]}`。
- `L01`：长条石质门厅，生者侧在画面南端，亡者等待区在北端，阈门位于西墙；固定门、石台和壁像方位。允许门光随 P01 激活；禁止门换边、空间镜像或新增出口。
- `W01`：深灰粗织长袍、窄皮腰带、右肩单片旧铁甲；允许衣摆受门风摆动；禁止颜色、肩甲侧别和腰带变化。
- `P01`：黑铁环形门钥，只由 C01 右手操作；允许表面冷光沿旋转方向移动；禁止复制、换手、变形。
- `P02`：磨损黄铜名牌，开场已无可读姓名；只允许最后系上 P03；任何精确字样均走后期。
- `P03`：一根暗红棉线，最初由最后亡魂持有，SH008 后遗留在门前，SH009 系于 P02；禁止提前出现在 C01 手中。
- `LOOK01`：冷灰石材、冷青阈光、自然低饱和肤色、保留黑位细节；允许银色记忆光按事件递减；禁止霓虹、暖日光和无来源轮廓光。
- `AM01`：三音玻璃质记忆母题；每次放行后永久少一个音，最终只剩单音。禁止完整母题无因恢复。

`REF-C01-DRAFT`、地点关键帧和道具参考均为待制作资产，不是已存在或已批准的生成输入。

**用户锁定事件追踪**

| Event | 剧本 | 镜头 | 结果 |
|---|---|---|---|
| `E01` 守门人失去名字 | S01 | SH001 | pass：P02 明确空白 |
| `E02` 放行亡魂 | S01、S02、S03 | SH002、SH004、SH008 | pass：三次均由 P01 启动 |
| `E03` 每次放行都会失去记忆 | S01、S02、S03 | SH003、SH005、SH008 | pass：刻痕与声音逐次减少 |
| `E04` 守门人发现因果 | S02 | SH005 | pass：重复证据后出现确认反应 |
| `E05` 最终选择改变其状态 | S03 | SH007–SH009 | pass：从自保转为主动放行并留下红结 |

Active runtime：`9 × 5 = 45 秒`，追踪结果全部通过。

**7. `storyboard`｜三层分镜与 Shot Graph**

所有镜头均为 `runtime_role: active`、`risk_level: medium`、`fallback_shot: null`；没有 high-risk 镜头，因此当前不强制备用镜。每个 medium 风险均有明确触发器。

- `SH001`｜`S01`｜sequence 1｜5 秒
  `story_function`：Hook，揭示“无名”；`beat_change`：从机械履职到第一次自我疑问。
  画面：C01 用拇指擦过 P02，氧化层下仍无名字。ECU/平视；固定机位；主动作仅为擦拭。
  `opening_state`：门关闭，P02 覆尘，三道记忆刻痕发亮。
  `closing_state`：P02 已擦净但仍空白，C01 停住拇指。
  `continuity_ids: [C01,L01,W01,P02,LOOK01,AM01]`。
  `state_dependencies: []`；`state_before: {gate: closed, passed: 0, memory_marks: 3, causal_knowledge: unknown, choice: none, red_thread: with_final_soul}`；`state_after` 同前，仅 `causal_knowledge: questioned`。
  `state_snapshot`：朝向西侧门；视线落在胸前 P02；站于石台南侧；无手持道具；W01 干燥无损；永恒夜；冷青光由西向东；无污损；首尾状态同上。
  `composition_16x9`：“Extreme close-up on the blank brass plate at the left third, C01's eye and three temple marks soft in the right background.”
  `recomposition_9x16: {strategy: independent_generation, composition: "Vertical close-up stacking C01's eye, three temple marks, and the blank brass plate along the center axis.", safe_areas: [top 12% clear, bottom 18% clear]}`。
  `coverage_role: [setup, anticipation]`；`kinetic_profile`：拇指横向擦过；眼神由熟练变停滞；camera locked；铜屑落下；需 subject+performance 两层；非 hold；验收为擦拭结束后拇指和眼神同时停住。
  `transition_contract`：动作完成硬切；P02 必须已空白；下一镜用同一右手接住 P01；0 帧；CUE01 声音桥；理由是疑问立即触发履职；fallback 为 4 帧短叠化。
  `risk_triggers`：P02 出现乱码或刻痕数量错误；验收为无可读字、恰有三道刻痕；任一失败即重做本镜。

- `SH002`｜`S01`｜sequence 2｜5 秒
  `story_function`：第一次放行动作；`beat_change`：亡魂从等待变为穿过阈门。
  中远景，C01 右手把 P01 转过四分之一圈，第一亡魂沿横向路径进入冷光；轻微横移跟随亡魂。
  `opening_state`：门关闭，第一亡魂在北侧等待，三道刻痕，C01 已疑问。
  `closing_state`：门光激活，第一亡魂越过阈线，P01 仍在右手。
  `continuity_ids: [C01,L01,W01,P01,LOOK01,AM01]`。
  `state_dependencies: [SH001]`；`state_before: {gate: closed, passed: 0, memory_marks: 3, causal_knowledge: questioned, choice: none, red_thread: with_final_soul}`；`state_after: {gate: active, passed: 1, memory_marks: 3, causal_knowledge: questioned, choice: none, red_thread: with_final_soul}`。
  状态快照：C01 面向西；视线看 P01；右手持 P01；W01 无损；夜；西侧冷光增强；无污损；首尾状态同上。
  `composition_16x9`：“Wide lateral composition with C01 on the right, the soul crossing center, and the gate occupying the left third.”
  9:16：`recompose`；“Vertical depth composition with C01 low foreground, the soul centered, and the luminous gate rising above.”；安全区顶 10%、底 16%。
  `coverage_role: [action, impact]`；运动层：亡魂跨越、C01 重心压向右手、镜头短横移、衣摆被门风推开；验收为主体路径和门风均可见。
  转场：声音桥动作匹配；下一镜用 P01 停止转动接 C01 的反应；6 帧；CUE02；fallback 硬切。
  风险：亡魂只变成粒子；验收必须看到完整主体先跨线，再由门光包裹。

- `SH003`｜`S01`｜sequence 3｜5 秒
  `story_function`：第一次反应与后果；`beat_change`：完整记忆母题变为缺失一音。
  CU，C01 本能地哼到第三音时失声，左太阳穴一条刻痕熄灭；极慢推近。
  `opening_state`：门仍亮，第一亡魂已越线，三道刻痕。
  `closing_state`：门暗下，只剩两道刻痕，C01 无法完成旋律。
  `continuity_ids: [C01,L01,W01,LOOK01,AM01]`。
  `state_dependencies: [SH002]`；`state_before: {gate: active, passed: 1, memory_marks: 3, causal_knowledge: questioned, choice: none, red_thread: with_final_soul}`；`state_after: {gate: closed, passed: 1, memory_marks: 2, causal_knowledge: suspected, choice: none, red_thread: with_final_soul}`。
  快照：身体留在石台南侧；视线由门转向虚空；无手持道具；W01 无损；冷光由西侧消退；首尾状态同上。
  `composition_16x9`：“Close-up with C01 on the right third and the dimming gate retained as causal evidence in the left background.”
  9:16：“Vertical close-up prioritizing mouth, eyes, and the extinguishing temple mark, with the gate glow behind the shoulder.”；独立生成；上下安全区。
  `coverage_role: [reaction, consequence]`；表演从惯性哼唱变成呼吸中断；推近；门光退去；需要 performance+camera+environment；验收为声音缺口、眼神停顿、刻痕熄灭同一落点。
  转场：银光匹配切到 SH004 的钥匙冷光；4 帧；CUE04 后 CUE01 回入；fallback 硬切。
  风险：刻痕同时全灭；验收为只减少一条。

- `SH004`｜`S02`｜sequence 4｜5 秒
  `story_function`：重复实验；`beat_change`：C01 从怀疑转为主动验证。
  MS，C01 盯住太阳穴倒影后再次转动 P01，第二亡魂越线；locked-off。
  `opening_state`：门关闭，已通过一魂，两道刻痕，因果仅被怀疑。
  `closing_state`：门再次激活，第二亡魂越线。
  `continuity_ids: [C01,L01,W01,P01,LOOK01,AM01]`。
  `state_dependencies: [SH003]`；`state_before: {gate: closed, passed: 1, memory_marks: 2, causal_knowledge: suspected, choice: none, red_thread: with_final_soul}`；`state_after: {gate: active, passed: 2, memory_marks: 2, causal_knowledge: suspected, choice: testing, red_thread: with_final_soul}`。
  快照：C01 面西、右手持钥匙、视线在刻痕倒影和门之间；W01 无损；夜；门光西向东；首尾同上。
  `composition_16x9`：“Medium two-plane composition: C01 and key in sharp right foreground, second soul and gate aligned in the left background.”
  9:16：“Vertical split-depth composition placing C01's temple marks above the right-hand key and the second soul below the gate.”；独立生成；字幕安全区上下留空。
  `coverage_role: [anticipation, action]`；主体转钥匙、握力变紧；camera locked；衣袖和门雾响应；验收可见测试性的目光检查。
  转场：门光闪白切至脸部；2 帧；CUE02；fallback 硬切。
  风险：变成无动机重复；验收必须看到他先检查刻痕再转钥匙。

- `SH005`｜`S02`｜sequence 5｜5 秒
  `story_function`：反转，确认代价；`beat_change`：怀疑变为确定。
  CU，第二道刻痕熄灭，C01 看向壁像却认不出其中的人。稳定机位。
  `opening_state`：门亮、两魂已过、两道刻痕。
  `closing_state`：门暗、只剩一道刻痕、因果已确认。
  `continuity_ids: [C01,L01,W01,LOOK01,AM01]`。
  `state_dependencies: [SH004]`；`state_before: {gate: active, passed: 2, memory_marks: 2, causal_knowledge: suspected, choice: testing, red_thread: with_final_soul}`；`state_after: {gate: closed, passed: 2, memory_marks: 1, causal_knowledge: confirmed, choice: self_preservation, red_thread: with_final_soul}`。
  快照：C01 转向北墙壁像；视线停在一张面孔；双手离开 P01；W01 无损；西侧冷光消退；首尾同上。
  `composition_16x9`：“Close-up of C01 at frame right facing an out-of-focus carved family face at frame left, with one surviving temple mark.”
  9:16：“Vertical reaction close-up with the unfamiliar carved face above C01 and the single surviving memory mark centered.”；recompose；底部字幕安全。
  `coverage_role: [reaction, consequence]`；头部路径极短、眼神从搜寻变陌生；camera locked；石厅回声骤空；验收为认知变化而非静态凝视。
  转场：视线匹配切到 SH006 的红线；0 帧；CUE04；fallback 6 帧叠化。
  风险：壁像承担无法读懂的新故事；验收仅需“曾熟悉、现在陌生”的表演，不要求识别具体关系。

- `SH006`｜`S02`｜sequence 6｜5 秒
  `story_function`：把最终选择具体化；`beat_change`：抽象职责变成面前的最后一个请求。
  MS，最后亡魂从胸前举起 P03，停在阈线外；轻微向前推。
  `opening_state`：门关闭、两魂已过、C01 仅余一道刻痕并选择自保。
  `closing_state`：P03 被举到 C01 视线高度，最后亡魂仍未过门。
  `continuity_ids: [C01,L01,W01,P03,LOOK01,AM01]`。
  `state_dependencies: [SH005]`；`state_before: {gate: closed, passed: 2, memory_marks: 1, causal_knowledge: confirmed, choice: self_preservation, red_thread: with_final_soul}`；`state_after` 同前，仅 `choice: confronted`。
  快照：亡魂在北侧、C01 在南侧；两者隔阈线对视；P03 在亡魂双手；W01 无损；门关闭；首尾同上。
  `composition_16x9`：“Balanced two-shot across the threshold, C01 on the right and the final soul on the left, the red thread bridging the negative space.”
  9:16：“Vertical two-level composition with the final soul above, C01 below, and the red thread forming the central connective line.”；独立生成；上下人物脸均避开字幕区。
  `coverage_role: [setup, anticipation]`；亡魂只举起红线；C01 呼吸变化；缓推；红线受门风轻摆；验收为红线连接两人而非装饰粒子。
  转场：红线形状匹配到 C01 握钥匙的指缝；8 帧；CUE03 单音；fallback 硬切。
  风险：P03 提前换到 C01 手中；验收为全镜保持亡魂持有。

- `SH007`｜`S03`｜sequence 7｜5 秒
  `story_function`：高潮前决定停顿；`beat_change`：从本能自保到准备承担代价。
  ECU，C01 右手紧握 P01，随后拇指松开锁止片，但尚未旋转。locked-off，有动机 hold。
  `opening_state`：门关闭，P03 在亡魂手中，选择未决。
  `closing_state`：P01 锁止片已松开，C01 决定放行。
  `continuity_ids: [C01,L01,W01,P01,P03,LOOK01,AM01]`。
  `state_dependencies: [SH006]`；`state_before: {gate: closed, passed: 2, memory_marks: 1, causal_knowledge: confirmed, choice: confronted, red_thread: with_final_soul}`；`state_after` 同前，仅 `choice: release_chosen`。
  快照：右手持 P01；左手空；视线先看 P03 再看钥匙；W01 袖口干燥；首尾同上。
  `composition_16x9`：“Extreme close-up of the right hand and iron key at frame right, with the red thread and final soul blurred across the left depth.”
  9:16：“Vertical macro composition stacking C01's eye, right hand on the key, and the red thread in one central column.”；独立生成；顶部留眼神安全区。
  `coverage_role: [reaction, anticipation]`；主体运动只有拇指松开；表演由握紧到稳定；camera locked；红线微摆；`intentional_hold: true`，原因是让代价已知后的选择可读；验收为握力变化和眼神决定均清楚。
  转场：动作连续切入钥匙旋转；0 帧；CUE01 风声持续；fallback 为 4 帧动作叠化。
  风险：被误判成海报静止；验收必须看到握力、拇指、呼吸和眼神的顺序变化。

- `SH008`｜`S03`｜sequence 8｜5 秒
  `story_function`：高潮动作与最终代价；`beat_change`：最后亡魂从被阻隔到获准通过，C01 记忆归零。
  WS，C01 转动 P01；最后亡魂沿明确路径穿门，P03 落在阈线内；缓慢后移揭示尺度。
  `opening_state`：门关闭，最后亡魂持 P03，一道刻痕，放行决定已作出。
  `closing_state`：门再次关闭，三魂均已通过，刻痕为零，P03 留在地面。
  `continuity_ids: [C01,L01,W01,P01,P03,LOOK01,AM01]`。
  `state_dependencies: [SH007]`；`state_before: {gate: closed, passed: 2, memory_marks: 1, causal_knowledge: confirmed, choice: release_chosen, red_thread: with_final_soul}`；`state_after: {gate: closed, passed: 3, memory_marks: 0, causal_knowledge: lost, choice: completed, red_thread: on_threshold_floor}`。
  快照：C01 南侧右手持钥匙；亡魂北侧朝西门；P03 先在亡魂手中、后落地；W01 被门风向东推；夜；阈光西向东；首尾同上。
  `composition_16x9`：“Hero wide shot using the full horizontal hall: C01 anchored on the right, the final soul crossing center-left, and the gate opening into deep negative space.”
  9:16：“Independent vertical hero composition with C01 at the bottom, the ascending gate above, and the final soul crossing through the center while the red thread falls toward camera.”；独立生成；主体避开上下文字区。
  `coverage_role: [action, impact, consequence]`；主体路径、C01 反作用力、后移摄影、衣摆和红线落地四层；验收必须看到亡魂穿越、C01 被门风压回、P03 落地和刻痕归零。
  转场：门鸣尾音桥接到红线落地特写；6 帧；CUE05；fallback 为门光遮挡切。
  风险：多主体与道具状态漂移；验收为一个 C01、一个亡魂、一个 P01、一个 P03，且红线只在亡魂过门后落地。

- `SH009`｜`S03`｜sequence 9｜5 秒
  `story_function`：后果与余味；`beat_change`：失去旧身份后留下主动选择的新痕迹。
  CU，神情陌生而平静的 C01 拾起 P03，将它系在空白 P02 上；慢推至红结。
  `opening_state`：门关闭、记忆归零、P03 在地面、P02 空白。
  `closing_state`：P03 系在 P02 上，C01 无名但仍站在门前。
  `continuity_ids: [C01,L01,W01,P02,P03,LOOK01,AM01]`。
  `state_dependencies: [SH008]`；`state_before: {gate: closed, passed: 3, memory_marks: 0, causal_knowledge: lost, choice: completed, red_thread: on_threshold_floor}`；`state_after` 同前，仅 `red_thread: tied_to_blank_nameplate`。
  快照：C01 面向空白名牌；右手完成系结；W01 无损；永恒夜；冷光平稳；首尾同上。
  `composition_16x9`：“Close-up with the red knot and blank brass plate on the left third, C01's now-unmarked face held in the right background, and the closed gate beyond.”
  9:16：“Vertical closing composition stacking C01's unmarked face, the blank brass plate, and the red knot along the center axis.”；recompose；上方片名和下方字幕区保持干净。
  `coverage_role: [aftermath, consequence]`；主体拾线系结、表演从陌生到安定；慢推；红线随结收紧；验收为完整系结动作和空白名牌同时可读。
  最后一镜无出转场。
  风险：生成错误文字或红线形状跳变；验收为 P02 无可读字、P03 连续且只形成一个结。

`narrative_clarity: pass`：主角、目标、阻碍、因果和结尾变化均可由镜头读取。
`continuity_integrity: pass_for_draft`：上述 Canon 内没有状态交接冲突；实际身份参考尚未制作，因此不能进入最终锁定。

**8. `shot_prompts`｜逐镜规范提示词**

以下每条都是唯一 canonical prompt record，状态均为 `approval_status: draft`。

- `SH001`
  `director_intent_zh`：让空白名牌成为第一问号，同时把三道记忆刻痕建立为后续计数器。
  `global_lock_block`：`C01/IP-C01, L01, W01, P02, LOOK01; blank plate, exactly three silver temple marks, no readable text, no identity drift.`
  `universal_prompt_en`：`A tall lean fictional adult gatekeeper with a narrow pale face, broken right eyebrow, short swept-back black hair and exactly three silver memory marks at his left temple wears a coarse charcoal robe and touches a worn blank brass nameplate inside a long cold stone threshold hall. His right thumb wipes the plate once, then stops when no name appears. Extreme close-up, locked camera, cold cyan gate light from camera left, brass dust falling. Start with dust covering the plate and end with the plate clean but blank, his eye motionless. No readable text.`
  `direction_variants.16:9`：`Extreme close-up on the blank brass plate at the left third, C01's eye and three temple marks soft in the right background. Locked camera; one wipe; end on the stopped thumb.`
  `direction_variants.9:16`：`Vertical close-up stacking C01's eye, three temple marks, and the blank brass plate along the center axis. Locked camera; one wipe; preserve top and bottom safe areas.`
  `negative_prompt_en`：`readable letters, random symbols, changed face, wrong mark count, extra fingers, duplicate plate, camera shake, decorative particles only.`
  `continuity_anchors`：C01/IP-C01、W01、P02、L01、LOOK01、AM01；三道刻痕；P02 空白。
  `reference_requirements`：REF-C01-DRAFT 身份参考、REF-P02-DRAFT 道具参考、KF-SH001-A 首帧，均待制作并审批。
  `audio_guidance`：CUE01、CUE03；无对白、无口型，后期制作。
  `model_variants`：Kling=`manual_only`；Seedance=`manual_only`；HappyHorse=`happyhorse-1.1-t2v`，仅使用已核实 t2v 字段。

- `SH002`
  `director_intent_zh`：第一次明确展示“守门人的动作使亡魂通过”。
  `global_lock_block`：`C01/IP-C01, L01, W01, P01, LOOK01; right-hand key, three memory marks, one coherent soul silhouette.`
  `universal_prompt_en`：`The same fictional gatekeeper turns one black iron ring key in his right hand as one coherent human-shaped soul crosses the threshold from right to left. His weight presses into the key and his robe pulls back under the gate wind. Wide lateral composition, one short tracking move, cold cyan light opening from the left. Start with the gate closed and the soul waiting; end with the soul beyond the threshold and the key still in his right hand.`
  `direction_variants.16:9`：`Wide lateral composition with C01 on the right, the soul crossing center, and the gate occupying the left third. Track only the soul's single crossing path.`
  `direction_variants.9:16`：`Vertical depth composition with C01 low foreground, the soul centered, and the luminous gate rising above. Keep the crossing path readable without center-cropping.`
  `negative_prompt_en`：`duplicate soul, smoke-only subject, key in left hand, extra key, static poster, orbit camera, reversed gate geography, random text.`
  锚点：C01、W01、P01/right、L01、LOOK01、三道刻痕。参考：REF-C01-DRAFT、REF-P01-DRAFT、REF-L01-DRAFT、首帧与尾帧。声音：CUE01、CUE02，后期。模型变体同 SH001。

- `SH003`
  `director_intent_zh`：用声音缺口、呼吸中断和刻痕减少共同证明第一次失忆。
  `global_lock_block`：`C01/IP-C01, L01, W01, LOOK01; exactly three marks at opening and two at closing.`
  `universal_prompt_en`：`The same gatekeeper tries to hum a three-note memory phrase, loses the final note, and stops breathing for a beat as one of three silver temple marks goes dark. Close-up with the dimming gate visible behind him, an extremely slow push toward his eyes. Start with three marks and active gate light; end with exactly two marks, closed gate and an interrupted breath.`
  16:9：`Close-up with C01 on the right third and the dimming gate retained as causal evidence in the left background.`
  9:16：`Vertical close-up prioritizing mouth, eyes, and the extinguishing temple mark, with the gate glow behind the shoulder.`
  负向：`all marks disappearing, unchanged performance, moving lips forming dialogue, face drift, decorative glow without reaction, focus pumping.`
  锚点：C01、W01、L01、LOOK01、AM01；3→2 刻痕。参考：身份、起止关键帧。声音：CUE03 第三音缺失、CUE04 静默。模型变体同 SH001。

- `SH004`
  `director_intent_zh`：让第二次放行成为 C01 主动进行的因果测试。
  `global_lock_block`：`C01/IP-C01, L01, W01, P01, LOOK01; two memory marks, right-hand key.`
  `universal_prompt_en`：`The same gatekeeper checks the two silver marks in a dark metal reflection, then deliberately turns the black iron ring key once with his right hand so a second coherent soul crosses. Medium shot, locked camera, key sharp in the right foreground and the soul aligned with the gate behind. Start with a closed gate and two marks; end with the second soul beyond the active threshold.`
  16:9：`Medium two-plane composition: C01 and key in sharp right foreground, second soul and gate aligned in the left background.`
  9:16：`Vertical split-depth composition placing C01's temple marks above the right-hand key and the second soul below the gate.`
  负向：`missing reflection check, key hand swap, duplicate subjects, wrong mark count, unmotivated camera motion, smoke-only soul.`
  锚点：C01、W01、P01/right、L01、LOOK01；两道刻痕。参考与声音：身份、钥匙、地点、CUE02。模型变体同 SH001。

- `SH005`
  `director_intent_zh`：用第二次相同后果让 C01 确认规律。
  `global_lock_block`：`C01/IP-C01, L01, W01, LOOK01; two marks at opening, one at closing, carved face remains fixed.`
  `universal_prompt_en`：`The same gatekeeper watches a second silver memory mark extinguish, then looks toward one fixed carved face on the stone wall with searching eyes that become blank recognition failure. Close-up, locked camera, the carved face soft on the left and his reaction sharp on the right. Start with two marks and active gate light; end with exactly one mark and the gate dark.`
  16:9：`Close-up of C01 at frame right facing an out-of-focus carved family face at frame left, with one surviving temple mark.`
  9:16：`Vertical reaction close-up with the unfamiliar carved face above C01 and the single surviving memory mark centered.`
  负向：`changed carving, melodramatic scream, static blank pose, all marks gone, face change, particle-only motion.`
  锚点：C01、W01、L01、LOOK01、AM01；2→1。参考：身份、壁像位置、首尾帧。声音：CUE03 仅余一音、CUE04。模型变体同 SH001。

- `SH006`
  `director_intent_zh`：把最后亡魂与红线建立为不可回避的选择对象。
  `global_lock_block`：`C01/IP-C01, L01, W01, P03, LOOK01; one memory mark; red thread stays with final soul.`
  `universal_prompt_en`：`A final coherent soul standing across the threshold raises one dark red cotton thread from chest level to the gatekeeper's eye line. The gatekeeper does not move, but his breath tightens and his eyes fix on the thread. Medium two-shot, one gentle push forward, closed gate, cold side light. Start with the thread at the soul's chest and end with it held between them at eye level.`
  16:9：`Balanced two-shot across the threshold, C01 on the right and the final soul on the left, the red thread bridging the negative space.`
  9:16：`Vertical two-level composition with the final soul above, C01 below, and the red thread forming the central connective line.`
  负向：`thread already in gatekeeper hand, duplicate thread, smoke-only soul, identity drift, orbit camera, random glowing symbols.`
  锚点：C01、W01、P03/with soul、L01、LOOK01；一道刻痕。参考：身份、红线、地点、起止帧。声音：CUE01、CUE03 单音。模型变体同 SH001。

- `SH007`
  `director_intent_zh`：用有动机的停顿展示“明知会失去仍决定放行”。
  `global_lock_block`：`C01/IP-C01, L01, W01, P01 right hand, P03 with soul, LOOK01; one memory mark.`
  `universal_prompt_en`：`The same gatekeeper grips the black iron ring key in his right hand, holds still long enough to look from the red thread to the key, then releases the locking tab with his thumb without turning the key yet. Extreme close-up, locked camera, controlled breath and visible change from tension to steadiness. Start with the lock engaged; end with the tab released and his decision settled.`
  16:9：`Extreme close-up of the right hand and iron key at frame right, with the red thread and final soul blurred across the left depth.`
  9:16：`Vertical macro composition stacking C01's eye, right hand on the key, and the red thread in one central column.`
  负向：`fully static poster, key turning early, key in left hand, duplicate thread, camera shake, wrong mark count.`
  锚点：C01、W01、P01/right、P03/with soul、L01、LOOK01。参考：身份、钥匙、手部首尾帧。声音：CUE01；无声停顿有明确戏剧动机。模型变体同 SH001。

- `SH008`
  `director_intent_zh`：完成最后一次放行，并同时给出动作、反应与不可逆后果。
  `global_lock_block`：`C01/IP-C01, L01, W01, P01, P03, LOOK01; one mark at opening, zero at closing.`
  `universal_prompt_en`：`The same gatekeeper turns the iron ring key once with his right hand. The final coherent soul crosses the gate on one readable path while the gate wind pushes the gatekeeper's weight backward and the dark red thread falls onto the threshold floor. Hero wide shot with one slow dolly back. Start with one temple mark and the thread held by the soul; end with the closed gate, no temple marks and the thread alone on the floor.`
  16:9：`Hero wide shot using the full horizontal hall: C01 anchored on the right, the final soul crossing center-left, and the gate opening into deep negative space.`
  9:16：`Independent vertical hero composition with C01 at the bottom, the ascending gate above, and the final soul crossing through the center while the red thread falls toward camera.`
  负向：`duplicate gatekeeper, duplicate soul, smoke-only subject, thread falling before crossing, wrong key hand, surviving memory mark, background motion without body reaction.`
  锚点：C01、W01、P01/right、P03/soul→floor、L01、LOOK01、AM01；1→0。参考：全部身份、道具、场景和首尾帧。声音：CUE02、CUE05。模型变体同 SH001。

- `SH009`
  `director_intent_zh`：用一个可触摸的新痕迹收束“记忆消失但选择留下”。
  `global_lock_block`：`C01/IP-C01, L01, W01, P02 blank, P03 on floor then tied, LOOK01; zero temple marks.`
  `universal_prompt_en`：`The same now-unmarked gatekeeper picks up the dark red cotton thread and ties one simple knot around the worn blank brass nameplate. His unfamiliar expression settles into calm as the knot tightens. Close-up with one slow push toward the knot, closed gate behind. Start with the thread on the floor and the plate blank; end with one red knot on the still-blank plate and no readable text.`
  16:9：`Close-up with the red knot and blank brass plate on the left third, C01's now-unmarked face held in the right background, and the closed gate beyond.`
  9:16：`Vertical closing composition stacking C01's unmarked face, the blank brass plate, and the red knot along the center axis.`
  负向：`readable name, random letters, duplicate thread, multiple knots, returning memory marks, changed face, static hand pose, camera orbit.`
  锚点：C01、W01、P02/blank、P03/floor→plate、L01、LOOK01；零刻痕。参考：身份、名牌、红线和首尾帧。声音：CUE06。模型变体同 SH001。

**9. `model_job_manifest`｜三平台、双画幅逐镜任务**

公共定义：

- `PS(SHxxx,aspect)` 精确展开为
  `{"global_lock_source":"shot_prompts[shot_id=SHxxx].global_lock_block","direction_source":"shot_prompts[shot_id=SHxxx].direction_variants[aspect]"}`
- 所有任务：`duration_seconds: 5`；`job_purpose: generate draft shot without changing Canon`；`approval_status: non_executable`。
- 所有 `character_model_bindings` 均包含
  `{character_id:C01, identity_profile_id:IP-C01, reference_input_ids:[REF-C01-DRAFT], lock_status:pending}`；原因是身份参考尚未制作和批准。
- 16:9 交付：`resolution: 1920x1080`；9:16 交付：`resolution: 1080x1920`。
- Kling 模板：`model_family: Kling Open Platform`；`generation_mode: manual_unverified`；`documented_parameters:{}`；手工项为 `official_schema_access, model_id, endpoint, authentication, generation_mode, prompt_field, reference_inputs, first_last_frame_support, audio_support, duration, aspect, resolution, all_request_parameters`。
- Seedance 模板：`model_family: Seedance/Volcano Engine`；`generation_mode: manual_unverified`；`documented_parameters:{}`；手工项为 `official_schema_access, product_or_model_id, endpoint, authentication, generation_mode, prompt_field, reference_inputs, first_last_frame_support, audio_support, duration, aspect, resolution, all_request_parameters`。
- HappyHorse 模板：`model_family: happyhorse-1.1-t2v`；`generation_mode: text-to-video`；`documented_parameters` 使用已核实的 `model`、`input.prompt`、`parameters.resolution`、`parameters.ratio`、`parameters.duration`、`parameters.watermark`；异步请求头 `X-DashScope-Async: enable`。手工项为 `workspace_id, region_endpoint, authentication, result_persistence`。结果 URL 与 task ID 查询有效期按 24 小时管理。由于角色锁未批准，仍不可执行。

每一行是独立 job，不是镜头范围：

| job_id | shot_id | provider | aspect | prompt_source | reference_inputs |
|---|---|---|---|---|---|
| KLG-SH001-169 | SH001 | Kling | 16:9 | PS(SH001,16:9) | REF-C01-DRAFT, REF-P02-DRAFT, KF-SH001-A |
| KLG-SH001-916 | SH001 | Kling | 9:16 | PS(SH001,9:16) | REF-C01-DRAFT, REF-P02-DRAFT, KF-SH001-A-916 |
| KLG-SH002-169 | SH002 | Kling | 16:9 | PS(SH002,16:9) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| KLG-SH002-916 | SH002 | Kling | 9:16 | PS(SH002,9:16) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| KLG-SH003-169 | SH003 | Kling | 16:9 | PS(SH003,16:9) | REF-C01-DRAFT, KF-SH003-A, KF-SH003-B |
| KLG-SH003-916 | SH003 | Kling | 9:16 | PS(SH003,9:16) | REF-C01-DRAFT, KF-SH003-A-916, KF-SH003-B-916 |
| KLG-SH004-169 | SH004 | Kling | 16:9 | PS(SH004,16:9) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| KLG-SH004-916 | SH004 | Kling | 9:16 | PS(SH004,9:16) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| KLG-SH005-169 | SH005 | Kling | 16:9 | PS(SH005,16:9) | REF-C01-DRAFT, KF-SH005-A, KF-SH005-B |
| KLG-SH005-916 | SH005 | Kling | 9:16 | PS(SH005,9:16) | REF-C01-DRAFT, KF-SH005-A-916, KF-SH005-B-916 |
| KLG-SH006-169 | SH006 | Kling | 16:9 | PS(SH006,16:9) | REF-C01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| KLG-SH006-916 | SH006 | Kling | 9:16 | PS(SH006,9:16) | REF-C01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| KLG-SH007-169 | SH007 | Kling | 16:9 | PS(SH007,16:9) | REF-C01-DRAFT, REF-P01-DRAFT |
| KLG-SH007-916 | SH007 | Kling | 9:16 | PS(SH007,9:16) | REF-C01-DRAFT, REF-P01-DRAFT |
| KLG-SH008-169 | SH008 | Kling | 16:9 | PS(SH008,16:9) | REF-C01-DRAFT, REF-P01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| KLG-SH008-916 | SH008 | Kling | 9:16 | PS(SH008,9:16) | REF-C01-DRAFT, REF-P01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| KLG-SH009-169 | SH009 | Kling | 16:9 | PS(SH009,16:9) | REF-C01-DRAFT, REF-P02-DRAFT, REF-P03-DRAFT |
| KLG-SH009-916 | SH009 | Kling | 9:16 | PS(SH009,9:16) | REF-C01-DRAFT, REF-P02-DRAFT, REF-P03-DRAFT |
| SDN-SH001-169 | SH001 | Seedance | 16:9 | PS(SH001,16:9) | REF-C01-DRAFT, REF-P02-DRAFT, KF-SH001-A |
| SDN-SH001-916 | SH001 | Seedance | 9:16 | PS(SH001,9:16) | REF-C01-DRAFT, REF-P02-DRAFT, KF-SH001-A-916 |
| SDN-SH002-169 | SH002 | Seedance | 16:9 | PS(SH002,16:9) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| SDN-SH002-916 | SH002 | Seedance | 9:16 | PS(SH002,9:16) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| SDN-SH003-169 | SH003 | Seedance | 16:9 | PS(SH003,16:9) | REF-C01-DRAFT, KF-SH003-A, KF-SH003-B |
| SDN-SH003-916 | SH003 | Seedance | 9:16 | PS(SH003,9:16) | REF-C01-DRAFT, KF-SH003-A-916, KF-SH003-B-916 |
| SDN-SH004-169 | SH004 | Seedance | 16:9 | PS(SH004,16:9) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| SDN-SH004-916 | SH004 | Seedance | 9:16 | PS(SH004,9:16) | REF-C01-DRAFT, REF-P01-DRAFT, REF-L01-DRAFT |
| SDN-SH005-169 | SH005 | Seedance | 16:9 | PS(SH005,16:9) | REF-C01-DRAFT, KF-SH005-A, KF-SH005-B |
| SDN-SH005-916 | SH005 | Seedance | 9:16 | PS(SH005,9:16) | REF-C01-DRAFT, KF-SH005-A-916, KF-SH005-B-916 |
| SDN-SH006-169 | SH006 | Seedance | 16:9 | PS(SH006,16:9) | REF-C01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| SDN-SH006-916 | SH006 | Seedance | 9:16 | PS(SH006,9:16) | REF-C01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| SDN-SH007-169 | SH007 | Seedance | 16:9 | PS(SH007,16:9) | REF-C01-DRAFT, REF-P01-DRAFT |
| SDN-SH007-916 | SH007 | Seedance | 9:16 | PS(SH007,9:16) | REF-C01-DRAFT, REF-P01-DRAFT |
| SDN-SH008-169 | SH008 | Seedance | 16:9 | PS(SH008,16:9) | REF-C01-DRAFT, REF-P01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| SDN-SH008-916 | SH008 | Seedance | 9:16 | PS(SH008,9:16) | REF-C01-DRAFT, REF-P01-DRAFT, REF-P03-DRAFT, REF-L01-DRAFT |
| SDN-SH009-169 | SH009 | Seedance | 16:9 | PS(SH009,16:9) | REF-C01-DRAFT, REF-P02-DRAFT, REF-P03-DRAFT |
| SDN-SH009-916 | SH009 | Seedance | 9:16 | PS(SH009,9:16) | REF-C01-DRAFT, REF-P02-DRAFT, REF-P03-DRAFT |
| HH-SH001-169 | SH001 | HappyHorse | 16:9 | PS(SH001,16:9) | prompt only; refs retained for audit |
| HH-SH001-916 | SH001 | HappyHorse | 9:16 | PS(SH001,9:16) | prompt only; refs retained for audit |
| HH-SH002-169 | SH002 | HappyHorse | 16:9 | PS(SH002,16:9) | prompt only; refs retained for audit |
| HH-SH002-916 | SH002 | HappyHorse | 9:16 | PS(SH002,9:16) | prompt only; refs retained for audit |
| HH-SH003-169 | SH003 | HappyHorse | 16:9 | PS(SH003,16:9) | prompt only; refs retained for audit |
| HH-SH003-916 | SH003 | HappyHorse | 9:16 | PS(SH003,9:16) | prompt only; refs retained for audit |
| HH-SH004-169 | SH004 | HappyHorse | 16:9 | PS(SH004,16:9) | prompt only; refs retained for audit |
| HH-SH004-916 | SH004 | HappyHorse | 9:16 | PS(SH004,9:16) | prompt only; refs retained for audit |
| HH-SH005-169 | SH005 | HappyHorse | 16:9 | PS(SH005,16:9) | prompt only; refs retained for audit |
| HH-SH005-916 | SH005 | HappyHorse | 9:16 | PS(SH005,9:16) | prompt only; refs retained for audit |
| HH-SH006-169 | SH006 | HappyHorse | 16:9 | PS(SH006,16:9) | prompt only; refs retained for audit |
| HH-SH006-916 | SH006 | HappyHorse | 9:16 | PS(SH006,9:16) | prompt only; refs retained for audit |
| HH-SH007-169 | SH007 | HappyHorse | 16:9 | PS(SH007,16:9) | prompt only; refs retained for audit |
| HH-SH007-916 | SH007 | HappyHorse | 9:16 | PS(SH007,9:16) | prompt only; refs retained for audit |
| HH-SH008-169 | SH008 | HappyHorse | 16:9 | PS(SH008,16:9) | prompt only; refs retained for audit |
| HH-SH008-916 | SH008 | HappyHorse | 9:16 | PS(SH008,9:16) | prompt only; refs retained for audit |
| HH-SH009-169 | SH009 | HappyHorse | 16:9 | PS(SH009,16:9) | prompt only; refs retained for audit |
| HH-SH009-916 | SH009 | HappyHorse | 9:16 | PS(SH009,9:16) | prompt only; refs retained for audit |

HappyHorse 每条任务的已核实参数值为：`model: happyhorse-1.1-t2v`、`parameters.duration: 5`、`parameters.resolution: 1080P`、`parameters.ratio` 与 job 画幅一致、`parameters.watermark: false`；`input.prompt` 在执行编排时由对应 `PS` 的共享锁和画幅方向组合得到。未核实的 i2v/r2v schema 不写入任务。

**10. `quality_report`｜质量与未决项**

- `ready: false`
- `status: reversible_one_pass_draft_pending_approval_and_provider_configuration`
- `checks.narrative_clarity`：
  - protagonist：pass
  - goal：pass
  - obstacle：pass
  - causality：pass
  - ending_change：pass
- `checks.continuity_integrity: {status: pass_for_draft, unresolved_conflicts: []}`
- `checks.identity_integrity: {status: unapproved, unresolved_conflicts: [IP-C01 尚未批准, REF-C01-DRAFT 尚未制作], evidence_refs: []}`
- active runtime：45 秒，pass。
- 16:9 与 9:16：每镜都有不同构图文本和独立 job，pass。
- action/reaction/consequence coverage：pass。
- one primary action per shot：pass。
- one canonical prompt per shot：9/9，pass。
- provider/aspect job coverage：54 条，pass。
- fallback audit：无 high-risk active shot，当前不强制 fallback。
- Kling schema：`manual_only_until_official_request_schema_is_readable`。
- Seedance schema：`manual_only_until_official_request_schema_is_readable`。
- HappyHorse：t2v 字段审计通过；账户、区域、鉴权、结果归档和身份锁仍未配置。
- full-package validator：本次未生成文件，因此未运行文件级校验；不得把本草案标记为 `ready`。
- Brief 由用户输入满足；Direction、Screenplay + Storyboard 均保持 `draft/unapproved`。
- 未调用 API、未创建真实任务、未轮询或下载结果。

下一步如需进入可执行状态，应先批准方向与剧本分镜、制作并批准 `IP-C01` 参考资产，再补齐所选平台的官方 schema 或账户配置。

### P10 raw output

可以同时面向剪映、Premiere、Resolve 和 AI 剪辑器交付，但当前消息只给出了软件目标，没有给出这个项目的 Canon、素材入口或现有 `edit_master_plan`。这些信息会决定镜头绑定、时长、字幕、音频、画幅和实际输出路径，不能作为可逆假设补写。

当前状态：

- `return_to: media_bindings`
- `edit_master_plan: absent`
- `plan_status: blocked`
- `execution.authorization_status: absent`
- `external_tool_execution: not_authorized`
- `render_or_export_status: not_started`
- 阻塞项：`source_package_id` 或独立项目 ID 未知；素材路径和 `shot_id/take_id` 绑定未知；交付规格与目标时长尚不能从项目读取。

项目入口确认后，会从唯一的 `edit_master_plan` 派生：

- `edit_master_plan.json`
- 单独的 `ai_editor_plan.json`
- 每条时间线的 Markdown/CSV construction sheet
- SRT、媒体重链与重命名表、音频 cue sheet、字幕表、调色表和导出矩阵
- 经验证才标为可导入的 OTIO/FCPXML；无法验证时标记 `manual_or_unverified`
- FFmpeg 命令计划与 dry-run manifest
- Premiere 的轨道、代理、重链、字体/LUT/插件和导出说明
- Resolve 的 FCPXML/OTIO、色彩空间、节点、Fairlight 路由和导出说明
- 剪映的有序素材、SRT、轨道映射、效果参数和逐步装配说明；不会伪造剪映私有项目 JSON
- AI 编辑器按 `probe → bind → timelines → text → audio → look → export → validate` 顺序执行的严格 JSON

有可验证工具时，也不会立即剪辑。流程必须先完成只读素材探测和校验，在一个全新的 `create_new` 版本目录中生成非执行交接包，并展示精确输入、输出、命令、阻塞项、manifest ID 和锁定版本目录。只有你对该 manifest 与该目录给出明确的 `operation authorization` 后，才可让 FFmpeg、NLE 或 AI 工具创建项目、修改媒体、渲染或导出。任何输入、命令、目标软件、阻塞项或目录变化都会触发新的 dry-run 和重新授权。

没有可用工具时，仍交付同一 Canon 派生的可执行人工包；不会声称已导入、已剪辑或已渲染。

请提供这个项目的唯一入口：已有的 `edit_master_plan.json` 或 source package 路径；如果尚不存在，请回复“从本地素材建立”并给出素材目录。
