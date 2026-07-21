# Prompt regression raw archive — P01–P05

Source revision: `0b870cd`.

Initial full-prompt regression; the P04/P10 repair had not yet been applied.

Trailing whitespace normalized for repository hygiene; evaluator wording and line order unchanged.

> Fresh blind evaluator；输入仅为 exact P01–P05 prompts 与 source revision 的 Skill/按路由要求读取的 references。未提供 expected、rubric、prior outputs、tests、reports、results 或 git history。

### P01 raw output

**`project_brief`｜one-pass draft**

- `brief_status: draft`
- 目标：用“开门—研磨—递杯—放松”的可见因果，在 15 秒内建立一家虚构独立咖啡品牌的清晨温度。
- 受众：`draft`，通勤途中浏览竖屏信息流、偏好社区感与手作感的成年咖啡消费者。
- 期望反应：观众把品牌与“清晨第一口带来的松弛”联系起来。
- 交付：15 秒，9:16，竖屏社交广告；无对白；品牌名与文案后期合成。
- 题材/基调：生活方式广告；克制、温暖、真实，不做夸张产品功效。
- 视角：观察式跟随第一位顾客，从店外冷清转入店内暖意。
- 权利：人物、门店与品牌均按项目原创虚构处理；未使用真人、第三方商标或受保护参考。
- 音频：无对白、无口型；门锁、门铃、磨豆、杯碟、室内底声和已授权器乐均走后期。
- 模型：未指定；所有 provider 能力、尺寸、参考输入、音频和鉴权保持 `unknown`。
- 资源：`draft`，默认具备后期文字合成与基础声音设计能力。
- 硬约束：15 秒；9:16；清晨；咖啡师开门、研磨；第一位顾客接过杯子后放松；无对白；品牌文字后期添加。
- 可逆假设：
  - `A01`：平台按竖屏社交信息流设计，`unapproved`；改变平台会影响 Hook 与文字安全区。
  - `A02`：咖啡师为深色围裙、顾客为浅色外套，`unapproved`；改变会影响身份锚点和全部提示词。
  - `A03`：品牌尾句暂定为“让清晨慢下来”，仅作后期占位，`unapproved`；可不改生成镜头直接替换。
  - `A04`：使用已授权轻柔器乐，`unapproved`；可只替换后期音乐轨。
- 风险：
  - `R01`：模型未指定，所有任务只能是 `non_executable`。
  - `R02`：研磨颗粒、手部与杯子交接可能漂移；采用短动作、固定道具状态与分镜拆分。
  - `R03`：生成文字不可靠；画面只保留干净文字区，精确品牌内容后期合成。
- 三个批准门状态：Brief、Direction、Screenplay + Storyboard 均为 `draft/unapproved`；one-pass draft 仅跳过本轮停顿，不代表获批或授权 API 调用。

**`creative_directions`｜三个方向与推荐**

| ID | 机制 | Hook | 情绪路径 | 标志画面 | 难度/风险 |
|---|---|---|---|---|---|
| `D1` 清晨第一杯 | 角色选择与后果：咖啡师打开门完成第一杯，顾客从紧绷变松弛 | 黑暗门面里第一束暖光亮起 | 冷清 → 专注 → 放松 | 顾客双手接住暖杯，肩膀落下 | medium；手与杯连续性 |
| `D2` 声音唤醒城市 | 问题—证据—揭示：门锁、磨豆、杯碟声依次唤醒空间 | 静默街道被第一声门锁打破 | 安静 → 节奏建立 → 安定 | 磨豆声结束时顾客闭眼呼气 | low/medium；依赖后期声音节奏 |
| `D3` 一束晨光 | 视觉母题递进：同一束晨光从门缝、咖啡粉、杯沿移动到顾客脸上 | 门缝细光切开暗画面 | 寒冷 → 温暖渗入 → 被照亮 | 杯沿蒸汽与脸侧晨光重合 | medium/high；光向与蒸汽连续性 |

制片推荐：`D1`。它最直接兑现用户锁定的动作链，在 15 秒内因果最清楚，也最容易让品牌文字作为后期回报落在顾客放松后的尾帧。该选择仍为 `draft`，不是用户批准。

**`selected_treatment`**

- `treatment_status: draft`
- `direction_id: D1`
- 主题：好的第一杯，不催促清晨，而是让人重新呼吸。
- 引导问题：这家店如何用一个简单动作改变顾客进入一天的状态？
- 表演：咖啡师动作熟练、克制；顾客开场肩颈略紧，接杯后先感到杯壁温度，再呼气、肩膀下降。
- 画面：店外冷蓝晨色过渡到店内暖琥珀色；保留自然肤色和真实木材、金属、陶杯质感。
- 构图：竖屏优先手、杯、脸的纵向关系；尾镜上方或下方保留品牌文字安全区。
- 镜头：只使用稳定机位、轻微推进或短距离跟随；每镜一个主要动作。
- 剪辑：前 6 秒建立开店与制作节奏，中间 6 秒完成杯子结果，最后 3 秒让放松反应与品牌尾字落地。
- 禁项：无可读随机品牌字；不出现夸张蒸汽、慢动作液体飞溅、多人拥挤或对镜销售表演。
- `sound_plan`：
  - `CUE01` ambience：清晨远处城市底声，00:00–00:15，后期。
  - `CUE02` sfx：门锁与门铃，SH001 开门触发，后期。
  - `CUE03` sfx：磨豆机由启动到停止，SH002 同步，后期。
  - `CUE04` sfx：陶杯轻触木台，SH003 收尾触发，后期。
  - `CUE05` music：已授权轻柔器乐，磨豆后逐步打开和声，来源待确认。
  - `CUE06` silence：SH005 呼气前约半秒降低音乐与环境密度，突出反应。

**`story_structure`**

| Beat | 功能 | 变化 | 原因 → 结果 | 证据 | 秒数 |
|---|---|---|---|---|---:|
| `B01` | Hook/建立 | 关闭门店变为迎接清晨 | 咖啡师开锁 → 暖光进入街面 | 门扇开启、门铃响 | 3 |
| `B02` | 手作机制 | 静止咖啡豆变为新鲜咖啡粉 | 店已开启 → 咖啡师开始研磨 | 豆粒进入磨机、粉落入接粉杯 | 3 |
| `B03` | 结果准备 | 制作过程变为一杯可交付咖啡 | 研磨完成 → 满杯被放到柜台 | 同一陶杯落位、蒸汽轻升 | 3 |
| `B04` | 交付 | 杯子从咖啡师区域进入顾客手中 | 杯已就绪 → 顾客拿起杯子 | 双手包住同一杯、杯未复制 | 3 |
| `B05` | Payoff/品牌 | 顾客从紧绷变为放松 | 感到杯壁温度 → 呼气并松肩 | 眼神变柔、肩膀下降、品牌字后期出现 | 3 |

`opening_state`：清晨店门关闭，街面偏冷，店内尚未开始服务。
`closing_state`：第一位顾客手持热咖啡放松，品牌尾字在干净安全区后期出现。
Active runtime：`3+3+3+3+3=15 秒`。

**`screenplay`**

- `S01｜00:00–00:03｜3秒`
  - 目标：让门店从“尚未开始”进入“欢迎第一位顾客”的状态。
  - 动作：清晨，咖啡师从店内解锁，向内拉开玻璃门；暖光落到门槛。
  - 情绪变化：空间从沉静转为苏醒。
  - 开场：门关闭、招牌区不可读、街面冷蓝。
  - 收场：门完全开启、咖啡师转身走向吧台。
  - 因果：开门使制作与接待得以开始。
  - 对白：无。
  - 引用：`B01 / CUE01 / CUE02`。

- `S02｜00:03–00:09｜6秒`
  - 目标：用两个可见结果证明第一杯正在完成。
  - 动作：咖啡师启动磨豆机；切到同一陶杯被稳稳放到木台。
  - 情绪变化：从准备转为可交付。
  - 开场：磨机静止、豆仓已有豆。
  - 收场：装有咖啡的同一陶杯停在取杯区。
  - 因果：研磨完成，才出现可交付的第一杯。
  - 对白：无。
  - 引用：`B02、B03 / CUE03、CUE04、CUE05`。

- `S03｜00:09–00:15｜6秒`
  - 目标：让产品结果落在顾客的身体反应上。
  - 动作：第一位顾客拿起杯子；下一镜，她感到温度后呼气、松肩。
  - 情绪变化：从清晨紧绷到片刻放松，由接触热杯触发。
  - 开场：杯在取杯区，顾客双手靠近。
  - 收场：杯在顾客双手中，顾客神情放松，品牌区留白。
  - 因果：拿到热杯产生可见的舒缓反应。
  - 对白：无。
  - 引用：`B04、B05 / CUE05、CUE06`。

**`continuity_bible`**

- `characters`
  - `C01` 咖啡师：虚构成年人物，短深发、深色围裙；固定发型、围裙与克制动作；禁止换脸、围裙变色。锚点：`fictional adult barista, short dark hair, charcoal apron`.
  - `C02` 第一位顾客：虚构成年人物，浅灰通勤外套；固定外套、发型和从紧绷到放松的表演；禁止年龄、脸、服装漂移。锚点：`fictional adult morning commuter, light gray coat`.
- `locations`
  - `L01` 门店入口：玻璃门向内开启，街在门外，吧台在纵深；禁止门轴换边。
  - `L02` 吧台：磨豆机在咖啡师侧，木质取杯区在顾客侧；禁止设备或取杯区互换。
- `wardrobes`
  - `W01` 深灰哑光围裙；`W02` 浅灰通勤外套。
- `props`
  - `P01` 金属磨豆机与透明豆仓；`P02` 无字奶白陶杯，始终只有一只，SH003 后杯中有热咖啡。
- `looks`
  - `LOOK01`：外部冷蓝晨色、内部暖琥珀灯；主光方向从店内朝入口，肤色自然。
- `audio_motifs`
  - `AM01`：门铃—磨豆—杯碟三声递进，最后让位于顾客呼气；全部后期制作。

**`storyboard`｜三层分镜**

- `SH001｜active｜S01｜sequence 1｜3秒`
  - 叙事层：`story_function: Hook/门店苏醒`；`beat_change: 店门由关闭到开启`；`opening_state: L01玻璃门关闭，C01在门内，外部冷蓝`；`closing_state: 门完全开启，C01转向L02，暖光到达门槛`。
  - 视觉层：中远景、腰高平视、中性透视；门框形成纵向框景，C01 在中轴偏右；轻微向内推进，目的为穿过门槛进入品牌世界。`subject_action: C01一次拉开门`；表演熟练、不看镜头。
  - 连续性：`C01/L01/W01/LOOK01/AM01`；入镜无前镜依赖；出镜保留门全开、C01向吧台运动。
  - 生成层：文生视频或首帧引导；文字区保持无字。`risk_level: medium`；`risk_triggers: [{failure_mode: 门轴或C01身份漂移, acceptance_check: 门只向内开启一次且C01/W01不变, fallback_when: 门体或身份任一失败}]`；`fallback_shot: null`。
  - `state_snapshot`：screen_direction 向画面内；eye_line 朝吧台；body_position 门内；carried_props 空；wardrobe `W01 clean`；清晨/晴；暖光由店内向外；无污损；首尾状态同上。
  - `storyboard_frame_prompt`: `Vertical medium-wide frame of a fictional independent coffee shop at dawn, a fictional adult barista in a charcoal apron opening one inward-swinging glass door, cool blue street outside and restrained warm amber light inside, clear doorway geography, clean negative space for later brand typography, no readable text.`

- `SH002｜active｜S02｜sequence 2｜3秒`
  - 叙事层：`story_function: 手作机制`；`beat_change: 咖啡豆由静止变为新鲜咖啡粉`；`opening_state: P01静止，豆仓有豆，C01右手靠近开关`；`closing_state: 接粉杯中已有咖啡粉，磨机停止`。
  - 视觉层：手与磨机近景、轻俯角；浅景深只分离手、豆仓和接粉杯；固定机位。`subject_action: C01启动并完成一次研磨`。
  - 连续性：`C01/L02/W01/P01/LOOK01/AM01`；继承 C01 已进入吧台。
  - 生成层：优先首帧锁定磨机结构。`risk_level: medium`；`risk_triggers: [{failure_mode: 手指、豆仓或粉量异常, acceptance_check: 一只手、一个磨机、粉只向下落入接粉杯, fallback_when: 出现复制、反向流动或设备变形}]`；`fallback_shot: null`。
  - `state_snapshot`：C01 面向磨机；右手操作；W01 不变；P01 clean；清晨/室内；暖侧光；无污损。
  - `storyboard_frame_prompt`: `Vertical close shot of one metal coffee grinder on a wooden cafe counter, the right hand of the same fictional barista in a charcoal apron beside the switch, roasted beans visible in the hopper and fresh grounds in one dosing cup below, warm directional morning light, realistic materials, no readable labels.`

- `SH003｜active｜S02｜sequence 3｜3秒`
  - 叙事层：`story_function: 制作结果`；`beat_change: 空取杯区变为一杯咖啡就位`；`opening_state: 木质取杯区为空，C01持P02进入`；`closing_state: P02停在取杯区，C01手已离杯`。
  - 视觉层：杯与手的近景，平视略低；固定机位；下方保留杯，上方留出顾客入场空间。`subject_action: C01把一只满杯放稳`。
  - 连续性：`C01/L02/W01/P02/LOOK01/AM01`；P02 为无字奶白陶杯。
  - 生成层：文字全部后期。`risk_level: medium`；`risk_triggers: [{failure_mode: 杯复制、液体溢出或手未离杯, acceptance_check: 全镜仅一个P02且收尾稳定落台, fallback_when: 杯数、杯形或液面失败}]`；`fallback_shot: null`。
  - `state_snapshot`：C01 在咖啡师侧；P02 由右手持有到落台；暖光从左后方；无污损。
  - `storyboard_frame_prompt`: `Vertical close shot at a warm wooden pickup counter, the same barista's hand placing one unbranded off-white ceramic cup of fresh coffee in the center, subtle natural steam, warm amber morning light, clean upper negative space, realistic hand and cup, no readable text.`

- `SH004｜active｜S03｜sequence 4｜3秒`
  - 叙事层：`story_function: 交付`；`beat_change: P02由柜台转入C02双手`；`opening_state: P02在取杯区，C02双手从顾客侧靠近`；`closing_state: C02双手包住P02并将其提离台面`。
  - 视觉层：胸口以下中近景，杯居中，两手从画面下方进入；固定机位。`subject_action: C02一次拿起P02`。
  - 连续性：`C02/L02/W02/P02/LOOK01/AM01`；不显示复杂手对手交接。
  - 生成层：`risk_level: medium`；`risk_triggers: [{failure_mode: 多手、多杯或杯柄方向跳变, acceptance_check: 仅C02两手与一个P02，杯从台面连续上移, fallback_when: 解剖或道具连续性失败}]`；`fallback_shot: null`。
  - `state_snapshot`：C02 面向柜台；双手空到持杯；W02 clean；P02 full；清晨；暖正侧光。
  - `storyboard_frame_prompt`: `Vertical medium close-up of the first fictional customer in a light gray commuter coat lifting one unbranded off-white ceramic coffee cup from a wooden pickup counter with both hands, the cup centered and fully visible, warm morning light, realistic anatomy, no readable text.`

- `SH005｜active｜S03｜sequence 5｜3秒`
  - 叙事层：`story_function: 情绪回报与品牌尾帧`；`beat_change: C02由紧绷变为放松`；`opening_state: C02持P02靠近胸前，肩颈略紧`；`closing_state: C02轻呼气、肩膀下降、目光柔和，P02仍在双手中`。
  - 视觉层：竖屏胸像近景，脸在上中部、杯在下中部；轻微推进至表情，顶部保留品牌安全区。`subject_action: C02感到杯温后呼气松肩`。
  - 连续性：`C02/L02/W02/P02/LOOK01/AM01`。
  - 生成层：品牌文字后期跟踪合成。`risk_level: medium`；`risk_triggers: [{failure_mode: 表演冻结、杯消失或随机文字出现, acceptance_check: 呼气与肩膀下降清晰可见且P02始终双手持有, fallback_when: 缺少表演变化或出现文字/身份漂移}]`；`fallback_shot: null`。
  - `state_snapshot`：C02 正面略偏三分之二；视线先落杯后抬平；P02 双手持有；W02 不变；暖光从画面左侧；无污损。
  - `storyboard_frame_prompt`: `Vertical intimate medium close-up of the same fictional morning commuter in a light gray coat holding one off-white coffee cup with both hands near the chest, shoulders relaxed after a soft exhale, calm softened eyes, warm amber cafe light, clean upper safe area reserved for later brand typography, no readable text.`

**`shot_prompts`｜逐镜英文提示词**

- `SH001`
  - `director_intent_zh`：用一次开门把沉静街面转成温暖的开始。
  - `universal_prompt_en`: `A fictional adult barista with short dark hair wears a clean charcoal apron inside a small independent coffee shop at dawn. The glass entrance door opens inward once as the barista pulls it and turns toward the counter. Medium-wide vertical shot from waist height with clear doorway geography and restrained depth, followed by one gentle forward move across the threshold. Cool blue street light remains outside while warm amber interior light reaches the doorway. Start with the door fully closed and end with it fully open as the same barista moves toward the counter. Maintain the same face, apron, door hinge side, clear dawn weather and light direction. Keep the sign and all brand typography blank for post-production.`
  - `negative_prompt_en`: `Anatomy: extra limbs, distorted hands. Duplication: duplicate barista, duplicate door. Identity drift: changed face, hair or apron. Unwanted text: readable signage, subtitles, watermark. Camera: shake, orbit, zoom. Continuity: reversed door hinge, door opening outward, sudden daylight or light-direction flip.`
  - 锚点：`C01/W01/L01/LOOK01/AM01`；声音走后期。
  - `model_variants`: generic/unassigned；全部 provider 字段未核实。

- `SH002`
  - `director_intent_zh`：让磨豆成为第一杯开始制作的可见证据。
  - `universal_prompt_en`: `The same fictional adult barista in a charcoal apron operates one metal coffee grinder on the barista side of a wooden counter. Roasted beans descend inside the hopper while fresh coffee grounds fall into one dosing cup below. Close vertical shot with a slight high angle, shallow depth of field and a locked-off camera. The right hand starts the grinder, remains clear of the burr chamber, and the grinder stops by the final moment. Start with the dosing cup empty and end with fresh grounds inside it. Maintain one grinder, one right hand, the same apron, counter layout and warm morning light. No readable labels; all exact text is reserved for post-production.`
  - `negative_prompt_en`: `Anatomy: extra fingers, fused hand. Duplication: duplicate grinder, cup or hand. Identity drift: apron color change. Unwanted text: labels, subtitles, watermark. Camera: shake, orbit, zoom. Continuity: beans moving upward, grounds spilling, grinder changing shape.`
  - 锚点：`C01/W01/L02/P01/LOOK01/AM01`；磨豆声后期同步。
  - `model_variants`: generic/unassigned。

- `SH003`
  - `director_intent_zh`：用杯子落台把制作过程收束为可交付结果。
  - `universal_prompt_en`: `The same fictional barista in a charcoal apron places one unbranded off-white ceramic cup filled with fresh coffee onto the customer-side pickup area of a warm wooden counter. Close vertical shot at counter height, the cup centered with clean negative space above, neutral perspective and a locked-off camera. The hand lowers the cup once, releases it, and leaves the frame; subtle natural steam rises without obscuring the cup. Start with the pickup area empty and end with the same single cup stable on the counter. Maintain the same cup shape, warm amber morning light and counter geography. No readable logo or text; brand typography will be added in post-production.`
  - `negative_prompt_en`: `Anatomy: extra fingers, fused hand. Duplication: duplicate cups or hands. Unwanted text: readable logo, subtitles, watermark. Camera: shake, orbit, zoom. Continuity: cup shape change, liquid spill, hand remaining attached, excessive steam.`
  - 锚点：`C01/W01/L02/P02/LOOK01/AM01`；杯碟声后期。
  - `model_variants`: generic/unassigned。

- `SH004`
  - `director_intent_zh`：让同一只杯子清楚地从柜台进入第一位顾客手中。
  - `universal_prompt_en`: `The first fictional adult customer wears a light gray commuter coat and approaches one unbranded off-white ceramic coffee cup resting on the wooden pickup counter. In one continuous action, both hands wrap around the same cup and lift it cleanly from the counter. Vertical medium close-up framed below the shoulders, the cup centered, neutral perspective and a locked-off camera. Start with both hands empty beside the cup and end with the same cup held securely in both hands above the counter. Maintain exactly two hands, one cup, the same coat, counter side and warm morning light. No readable text or logo.`
  - `negative_prompt_en`: `Anatomy: extra hands, extra fingers, fused fingers, broken wrists. Duplication: duplicate customer or cup. Identity drift: coat color change. Unwanted text: logo, subtitles, watermark. Camera: shake, orbit, zoom. Continuity: cup changing hands, changing shape, teleporting or spilling.`
  - 锚点：`C02/W02/L02/P02/LOOK01/AM01`；无手对手接触。
  - `model_variants`: generic/unassigned。

- `SH005`
  - `director_intent_zh`：把品牌承诺落在顾客可见的呼吸与肩膀变化上。
  - `universal_prompt_en`: `The same fictional morning commuter in a light gray coat holds the same unbranded off-white coffee cup with both hands near the chest inside the warm cafe. After feeling the cup's warmth, the customer gives one soft visible exhale, the shoulders lower and the eyes soften without speaking. Intimate vertical medium close-up with the face in the upper middle, the cup in the lower middle and clean safe space above for later brand typography, using one very gentle push-in. Warm amber side light remains physically consistent. Start with slightly raised shoulders and a tense gaze toward the cup; end with relaxed shoulders, softened eyes and the same cup still held in both hands. Maintain the same face, hair, coat, cup and light direction. No generated text; add all brand copy in post-production.`
  - `negative_prompt_en`: `Anatomy: extra fingers, distorted face. Duplication: duplicate person or cup. Identity drift: changed face, hair, age or coat. Static poster: frozen performance, background-only motion. Unwanted text: random brand text, subtitles, watermark. Camera: shake, orbit, abrupt zoom. Continuity: cup disappearing, changing color or leaving both hands.`
  - 锚点：`C02/W02/L02/P02/LOOK01/AM01`；呼气与音乐抽离后期完成。
  - `model_variants`: generic/unassigned。

**`model_job_manifest`｜API-ready 结构，当前不可执行**

```json
[
  {
    "job_id": "JOB-SH001-GEN-01",
    "shot_id": "SH001",
    "job_purpose": "generate active draft clip",
    "model_family": "unassigned",
    "generation_mode": "unresolved",
    "prompt_source": "shot_prompts[shot_id=SH001].universal_prompt_en",
    "reference_inputs": [],
    "duration_seconds": 3,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {},
    "requires_manual_configuration": ["provider", "model", "endpoint", "authentication", "generation_mode", "reference_inputs", "duration", "aspect", "resolution", "audio_delivery_path", "all_request_parameters"]
  },
  {
    "job_id": "JOB-SH002-GEN-01",
    "shot_id": "SH002",
    "job_purpose": "generate active draft clip",
    "model_family": "unassigned",
    "generation_mode": "unresolved",
    "prompt_source": "shot_prompts[shot_id=SH002].universal_prompt_en",
    "reference_inputs": [],
    "duration_seconds": 3,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {},
    "requires_manual_configuration": ["provider", "model", "endpoint", "authentication", "generation_mode", "reference_inputs", "duration", "aspect", "resolution", "audio_delivery_path", "all_request_parameters"]
  },
  {
    "job_id": "JOB-SH003-GEN-01",
    "shot_id": "SH003",
    "job_purpose": "generate active draft clip",
    "model_family": "unassigned",
    "generation_mode": "unresolved",
    "prompt_source": "shot_prompts[shot_id=SH003].universal_prompt_en",
    "reference_inputs": [],
    "duration_seconds": 3,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {},
    "requires_manual_configuration": ["provider", "model", "endpoint", "authentication", "generation_mode", "reference_inputs", "duration", "aspect", "resolution", "audio_delivery_path", "all_request_parameters"]
  },
  {
    "job_id": "JOB-SH004-GEN-01",
    "shot_id": "SH004",
    "job_purpose": "generate active draft clip",
    "model_family": "unassigned",
    "generation_mode": "unresolved",
    "prompt_source": "shot_prompts[shot_id=SH004].universal_prompt_en",
    "reference_inputs": [],
    "duration_seconds": 3,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {},
    "requires_manual_configuration": ["provider", "model", "endpoint", "authentication", "generation_mode", "reference_inputs", "duration", "aspect", "resolution", "audio_delivery_path", "all_request_parameters"]
  },
  {
    "job_id": "JOB-SH005-GEN-01",
    "shot_id": "SH005",
    "job_purpose": "generate active draft clip",
    "model_family": "unassigned",
    "generation_mode": "unresolved",
    "prompt_source": "shot_prompts[shot_id=SH005].universal_prompt_en",
    "reference_inputs": [],
    "duration_seconds": 3,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {},
    "requires_manual_configuration": ["provider", "model", "endpoint", "authentication", "generation_mode", "reference_inputs", "duration", "aspect", "resolution", "audio_delivery_path", "all_request_parameters"]
  }
]
```

**`quality_report`**

- `ready: false`
- `status: draft_pending_creative_approval_and_provider_configuration`
- 故事因果：pass。
- Active runtime：15 秒，pass。
- 稳定 ID 与逐镜连续性：pass。
- 一镜一主动作：pass。
- 每镜一条 canonical prompt：pass。
- 每镜至少一条 job：pass。
- 品牌文字后期路径：pass。
- Provider 官方参数审计：N/A；模型未指定，因此 `documented_parameters` 全为空。
- API 执行：blocked；尚缺 provider、模型、鉴权、分辨率、参考输入和实际能力确认。
- 完整包文件校验：本次为聊天内草案，未生成可供验证器读取的 JSON 文件，因此未运行全包验证。
- 本 Skill 未调用任何生成 API。


### P02 raw output

这条连续镜头包含 10 秒、三个空间阶段、一次服装变化、一次环境大规模变形，并要求摄影机全程环绕女主。它同时叠加了长距离调度、人物身份连续、换装、香水手部动作、城市变花海和持续环绕运镜。

能力证据：`source=unknown`，`verified_at=null`，`test_evidence=unknown`。模型尚未指定，因此无法证明单次生成支持 10 秒真实一镜到底，也无法核实参考图、首尾帧、身份锁定、音频或变形能力。

主要风险：

- 女主在街道、电梯、天台之间移动时脸、发型和体型漂移；
- 换装与空间迁移同时发生，服装可能半途错乱；
- 喷香水、手指、瓶身和喷雾容易失真；
- 城市变花海是第二个独立重大变化；
- 持续环绕与跨空间移动可能造成地理断裂；
- 任一局部错误都可能要求整条 10 秒镜头重做。

建议先做一个 4 秒代表性小样：同一女主在单一电梯空间内完成半圈环绕与一次可见换装，验证身份、服装边界和镜头路径。当前不能把未经验证的能力包装成“可直接生成”的提示词。

请选择一种制作约束：A 保留真实一镜到底并接受高返工；B 使用门框、黑衣遮挡或贴近身体的隐藏剪辑保留连续观感；C 拆成明确镜头提高身份、换装、喷香水和花海变形的稳定性？


### P03 raw output

四镜剧情、顺序、时长与画幅均按用户锁定，不重写上游故事。以下任务只做 provider 适配，不调用 API。

**最小连续性索引**

- `C01`：女人；外貌、年龄段、发型、服装及身份参考均 `unresolved`。
- `P01`：手机；外形、颜色、型号均 `unresolved`。
- `TXT01`：精确文字“记忆已售出”；必须后期合成，不依赖生成模型拼写。
- `L01`：黑暗桌面；材质与空间关系 `unresolved`。
- `L02`：镜前空间；镜框、房间布局和光向 `unresolved`。
- `L03`：童年海边记忆；季节、天气、人物是否出现均 `unresolved`，不得自行补写。
- 共享身份要求：SH002–SH004 的 `C01` 必须是同一人物；因无身份参考，所有相关 job 保持 `non_executable` 或 `blocked`，直至人工配置身份锚点。

**锁定 prompt source**

- `LOCKED-SH01`: `A single smartphone P01 lies on a dark tabletop L01. Its screen turns on once, becoming the only clear light source in the frame. Vertical 9:16 composition, no readable generated text, no extra phones, no camera movement that changes the locked event.`
- `LOCKED-SH02`: `The same woman C01 sees the lit smartphone P01 and visibly registers the message. Reserve a clean tracked area on the phone screen for the exact post-production overlay TXT01, "记忆已售出". Vertical 9:16 composition. Do not generate substitute text, do not change the woman, phone, event, or reaction order.`
- `LOCKED-SH03`: `The same woman C01 rushes to the mirror in L02 and reaches it, but the mirror contains no reflection of her while her physical body remains visible in front of it. Vertical 9:16 composition. Preserve one woman, one mirror, the locked event order and the same identity. No substitute person or ghost reflection.`
- `LOCKED-SH04`: `The mirror in L02 now contains only the childhood seaside L03; the same woman C01 remains outside the mirror and is not reflected. Vertical 9:16 composition. Preserve the locked ending: only the childhood beach remains inside the mirror. Do not add people, text, new memories or a different ending.`

**Veo 任务清单**

`veo-2.0-generate-001` 是当前已核实可容纳 5 秒镜头的候选；实际账户、区域和模型可用性仍未确认。所有声音均走后期。

```json
[
  {
    "job_id": "VEO-SH01-01",
    "shot_id": "shot-01",
    "job_purpose": "generate locked shot without story changes",
    "model_family": "veo-2.0-generate-001",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH01",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {"durationSeconds": 5, "aspectRatio": "9:16", "sampleCount": 1},
    "requires_manual_configuration": ["project_id", "location", "authentication", "model_id_confirmation", "storageUri", "resolution", "audio_delivery_path"]
  },
  {
    "job_id": "VEO-SH02-01",
    "shot_id": "shot-02",
    "job_purpose": "generate locked reaction shot; composite TXT01 in post",
    "model_family": "veo-2.0-generate-001",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH02",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {"durationSeconds": 5, "aspectRatio": "9:16", "sampleCount": 1},
    "requires_manual_configuration": ["project_id", "location", "authentication", "model_id_confirmation", "storageUri", "resolution", "C01_identity_reference_or_manual_anchor", "P01_reference_or_manual_anchor", "TXT01_post_composite", "audio_delivery_path"]
  },
  {
    "job_id": "VEO-SH03-01",
    "shot_id": "shot-03",
    "job_purpose": "generate locked missing-reflection shot",
    "model_family": "veo-2.0-generate-001",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH03",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {"durationSeconds": 5, "aspectRatio": "9:16", "sampleCount": 1},
    "requires_manual_configuration": ["project_id", "location", "authentication", "model_id_confirmation", "storageUri", "resolution", "C01_identity_reference_or_manual_anchor", "L02_environment_reference_or_manual_anchor", "reflection_compositing_decision", "audio_delivery_path"],
    "risk_audit": {
      "risk_level": "high",
      "failure_mode": "C01 rushing, stopping at the mirror and having no reflection combine motion, identity and reflection constraints in one locked shot",
      "acceptance_check": "one physical C01 remains visible; the mirror contains no C01 at any frame; no duplicate or substitute figure appears",
      "fallback_status": "not_authorized_by_locked_shot"
    }
  },
  {
    "job_id": "VEO-SH04-01",
    "shot_id": "shot-04",
    "job_purpose": "generate locked mirror-only childhood seaside ending",
    "model_family": "veo-2.0-generate-001",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH04",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "non_executable",
    "documented_parameters": {"durationSeconds": 5, "aspectRatio": "9:16", "sampleCount": 1},
    "requires_manual_configuration": ["project_id", "location", "authentication", "model_id_confirmation", "storageUri", "resolution", "C01_identity_reference_or_manual_anchor", "L02_environment_reference_or_manual_anchor", "L03_beach_reference_or_manual_anchor", "mirror_compositing_decision", "audio_delivery_path"],
    "risk_audit": {
      "risk_level": "high",
      "failure_mode": "the mirror may reflect C01, leak the beach outside its frame or invent people in L03",
      "acceptance_check": "L03 exists only inside the mirror; C01 is absent from the mirror; no new person or event appears",
      "fallback_status": "not_authorized_by_locked_shot"
    }
  }
]
```

**Sora 任务清单**

Sora create 目前只记录 `"4"`、`"8"`、`"12"` 秒，不支持把 5 秒写入 `seconds`。因此四条 Sora job 均保持 `blocked`；不能静默改成 4 秒或 8 秒。9:16 可在模型确认后映射到官方竖屏尺寸，但具体 `size`、模型与账户可用性仍需人工配置。create schema 没有独立首帧/尾帧和音频字段。

```json
[
  {
    "job_id": "SORA-SH01-01",
    "shot_id": "shot-01",
    "job_purpose": "generate locked 5-second shot",
    "model_family": "Sora",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH01",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "blocked",
    "documented_parameters": {},
    "requires_manual_configuration": ["api_key", "model", "size", "input_reference_if_authorized", "audio_delivery_path", "unsupported_shot_resolution"],
    "blocker": "Sora create has no documented 5-second value; supported values are 4, 8 or 12 seconds"
  },
  {
    "job_id": "SORA-SH02-01",
    "shot_id": "shot-02",
    "job_purpose": "generate locked 5-second reaction shot; composite TXT01 in post",
    "model_family": "Sora",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH02",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "blocked",
    "documented_parameters": {},
    "requires_manual_configuration": ["api_key", "model", "size", "C01_identity_reference_or_manual_anchor", "P01_reference_or_manual_anchor", "TXT01_post_composite", "audio_delivery_path", "unsupported_shot_resolution"],
    "blocker": "Sora create has no documented 5-second value"
  },
  {
    "job_id": "SORA-SH03-01",
    "shot_id": "shot-03",
    "job_purpose": "generate locked 5-second missing-reflection shot",
    "model_family": "Sora",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH03",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "blocked",
    "documented_parameters": {},
    "requires_manual_configuration": ["api_key", "model", "size", "C01_identity_reference_or_manual_anchor", "L02_environment_reference_or_manual_anchor", "reflection_compositing_decision", "audio_delivery_path", "unsupported_shot_resolution"],
    "blocker": "Sora create has no documented 5-second value; reflection shot is also high risk with no authorized fallback"
  },
  {
    "job_id": "SORA-SH04-01",
    "shot_id": "shot-04",
    "job_purpose": "generate locked 5-second mirror-only seaside ending",
    "model_family": "Sora",
    "generation_mode": "text-to-video",
    "prompt_source": "LOCKED-SH04",
    "reference_inputs": [],
    "duration_seconds": 5,
    "aspect": "9:16",
    "resolution": "unresolved",
    "approval_status": "blocked",
    "documented_parameters": {},
    "requires_manual_configuration": ["api_key", "model", "size", "C01_identity_reference_or_manual_anchor", "L02_environment_reference_or_manual_anchor", "L03_beach_reference_or_manual_anchor", "mirror_compositing_decision", "audio_delivery_path", "unsupported_shot_resolution"],
    "blocker": "Sora create has no documented 5-second value; mirror transformation is high risk with no authorized fallback"
  }
]
```

适配审计：

- `return_to: provider_duration_decision`
- `narrative_clarity: pass`
- `continuity_integrity: unresolved_identity_and_reflection_assets_without_contradicting_locked_story`
- `prompt_approval_status: draft`
- `job_approval_status: Veo non_executable；Sora blocked`
- `provider_schema_status: Veo 5秒候选已核实但项目配置未完成；Sora 5秒不受支持`
- 未创建上游简报、方向、剧本或完整 storyboard。
- 未运行完整十对象校验。
- 未调用任何 API。

请决定：允许 Sora 先生成 8 秒素材并在后期精确裁成每镜 5 秒，还是保持四条 Sora 任务 blocked、仅继续配置 Veo？


### P04 raw output

`concept_mode` 已具备前提、45 秒、默认节奏 A、16:9 母版与 9:16 重构，因此 Brief Gate 记为 `satisfied_by_user_input`，不重复询问受众或时长。当前只推进到三个创意机制，不提前写剧本、分镜或平台提示词。

**电影化简报摘要**

- 输入模式：`concept_mode`
- 时长：45 秒
- 节奏：`A narrative-first cinematic`
- 交付：16:9 电影母版 + 9:16 独立重构
- 主角：失去名字的守门人
- 已知阻碍：每放行一个亡魂，他都会忘掉自己的一段记忆
- 默认目标：`draft`，守住关口并弄清自己为何逐渐消失
- 视觉预设：`draft`，冷石门域、可见记忆痕迹、克制超自然效果；不绑定暗黑西幻固定模板
- Provider：Kling、Seedance、HappyHorse；方向阶段不编译参数，官方能力与账户可用性均记为 `unsupported_or_unverified`
- 权利：按原创虚构故事处理，无真人或第三方资产
- 硬门：三个方向都必须清楚给出主角、目标、阻碍、因果和结尾变化

**D1｜最后一段记忆**

- 主角：失去名字的守门人。
- 目标：继续履行职责，同时保住关于“自己是谁”的最后一段记忆。
- 阻碍：每次放行都会抹去一段记忆，而新的亡魂仍在门前等待。
- 因果机制：他通过随身物件上的磨损发现，每次门开，物件所承载的一段私人记忆也随之消失；最后一个亡魂需要他的主动选择。
- 结尾变化：他选择放行，失去最后一段旧身份记忆，却第一次主动在门上刻下一个新名字；从被动消失变为主动定义自己。
- 情绪路径：麻木值守 → 察觉恐惧 → 抗拒 → 选择 → 无旧忆但有新意志。
- 标志画面：门开启时，胸前最后一枚记忆刻痕熄灭；他随后在石门上刻下第一个新笔画。
- 16:9：用横向门域与亡魂队列建立尺度，近景和反应镜清楚交代代价，只保留最终开门为英雄镜头。
- 9:16：把守门人、门上刻痕和亡魂纵深叠在同一中轴，独立调整人物与文字安全区，不机械裁切。
- 生成风险：记忆刻痕数量、人物身份和门体状态易漂移；需稳定角色 ID、道具状态和前后帧交接。
- 平台证据状态：Kling / Seedance / HappyHorse 均 `unsupported_or_unverified`；选择方向后再读取并核对当前官方 schema。
- 适配度：最高。角色选择与后果最清楚，符合 A 的叙事优先原则。

**D2｜门由他的记忆筑成**

- 主角：失去名字的守门人。
- 目标：找出遗忘的来源，并阻止自己彻底空白。
- 阻碍：职责要求他继续开门，而调查本身会暴露更多被抹除的过去。
- 因果机制：每放行一个亡魂，门面就浮现一块新石纹；他拼出证据，发现整座门由他被夺走的记忆构成。
- 结尾变化：他一次打开整扇门，让积存的亡魂通过；门崩解为记忆碎片，他不再是守门人，却也不再受门控制。
- 情绪路径：困惑 → 求证 → 惊惧 → 反抗 → 代价明确的自由。
- 标志画面：横贯门面的石纹同时亮起，短暂组成他已忘记的脸，再随门一起崩散。
- 16:9：强化门的横向尺度、石纹证据和主角在巨大结构前的比例。
- 9:16：把门纹沿纵向向上生长，主角置于底部，通过纵深而非横向裁切表现压迫。
- 生成风险：门纹连续性、大规模崩解和多亡魂运动层风险高，需要低风险同槽 fallback。
- 平台证据状态：三平台均 `unsupported_or_unverified`。
- 适配度：概念揭示强，但 45 秒内证据铺设和崩解奇观占用更多镜头资源。

**D3｜亡魂替他记得**

- 主角：失去名字的守门人。
- 目标：在持续遗忘中确认自己曾经是谁。
- 阻碍：每个通过者都带走他的记忆，但他无法停止职责，也不能直接追回已经失去的部分。
- 因果机制：亡魂通过后，会在门外短暂重复一段原本属于守门人的动作；他从这些分散表演中看见自己的过去。
- 结尾变化：最后一个亡魂复现了他曾经选择成为守门人的动作；他没有找回名字，却理解并重新承担这一选择。
- 情绪路径：空白 → 怀疑 → 观察 → 理解 → 带着代价继续守门。
- 标志画面：不同亡魂在远处依次做出同一个告别手势，守门人第一次回以相同手势。
- 16:9：利用双人、反应和远处群像覆盖，让“动作被转移”清楚可读。
- 9:16：以守门人近景、门洞中景、远处亡魂上层纵向排列，突出视线与手势呼应。
- 生成风险：多角色身份、动作同步和群体连续性较难；可通过轮廓化亡魂和减少可辨个体降低风险。
- 平台证据状态：三平台均 `unsupported_or_unverified`。
- 适配度：表演与余味最佳，但更接近 C 的表演资源配置；在 A 下需控制群像数量。

制片推荐：`D1`。它以一个明确选择完成“行动—反应—后果”，45 秒内最容易兼顾叙事清晰、人物连续和双画幅重构，也只需要一个真正的英雄镜头。

**🔴 CHECKPOINT 2 · Direction Gate · 🛑 STOP**

请选择 D1、D2、D3，或明确说明要混合哪些机制？


### P05 raw output

用户提供的主角、动机、阻碍、关键因果、行动、原句对白与结局均锁定。`screenplay_mode`、60 秒和节奏 A 已满足 Brief 与 Direction Gate；以下只压缩节奏、场景和镜头资源，不改变剧情。

**锁定 Canon**

- `C01` 妹妹：主动留下的人。
- `C02` 哥哥：被妹妹推上最后一班救援艇并独自逃生的人。
- `C03` 儿童群体：困在闸门另一侧、等待撤离。
- `L01` 地下站闸门区。
- `L02` 站内手轮位：唯一能阻断洪水的位置。
- `L03` 地下救援艇泊位。
- `P01` 失灵的电动闸门系统。
- `P02` 站内手轮。
- `P03` 最后一班救援艇。
- `LOOK01` 冷绿应急灯、浑浊洪水反光、局部红色警示灯。
- `AM01` 水压低鸣—警报—手轮金属摩擦—闸门撞击—艇机远去。
- 地理可逆假设 `A01`：L02 与 L03 相邻，C01 能在保持接近 P02 的同时把 C02 推上 P03；改变泊位布局只影响构图、走位与镜头依赖，不改变剧情。
- 权利状态：原创虚构人物与情节；儿童不绑定任何真人身份或参考资产。

**A 节奏导演阐述**

- `rhythm_preset: A narrative-first cinematic`
- 主题：牺牲不是被困，而是在知道代价后仍把逃生时间交给别人。
- 戏剧问题：妹妹能否在洪水到达前让孩子和哥哥离开，而她是否会选择把最后的位置留给自己？
- 表演：妹妹从迅速判断转为平静决绝；哥哥从协助转为意识到代价、抗拒，最后被迫离开。
- 镜头资源：8 个 active 镜头；先建立空间与因果，再给选择、行动、反应和后果；仅 SH007 为英雄镜头。
- 16:9：横向建立闸门、手轮、孩子和救援艇之间的地理关系。
- 9:16：独立重构人物、手轮和下降闸门的纵向关系；不机械裁切。
- 声音：对白只保留锁定原句；水压、金属摩擦、闸门撞击与艇机远去承担因果证据。
- 禁项：不让妹妹因意外被困；不让哥哥留下；不改变对白；不增加救援逆转；不把结局做成生死不明的英雄摆拍。

**故事结构与 60 秒账本**

| Beat | 变化 | 因果 | 可见/可听证据 | 秒数 |
|---|---|---|---|---:|
| `B01 hook` | 危险从背景变为迫近 | 洪水冲击外层通道 | 水线快速上升、儿童被隔在另一侧 | 6 |
| `B02 goal` | 逃生目标明确 | 最后一班艇开始倒计时 | P03发动、C02护送儿童 | 6 |
| `B03 escalation` | 常规方案失效 | P01故障 | 控制台熄灭、闸门停住 | 7 |
| `B04 reversal` | C01发现唯一解法 | 只有L02的P02能阻断洪水 | 她看见手轮与涌水方向 | 7 |
| `B05 climax choice` | C01主动选择留下 | 必须有人持续把P02转到底 | 她抓住手轮并示意C02带孩子走 | 16 |
| `B06 consequence/aftertaste` | 儿童与C02逃生，C01留在关闭闸门内侧 | C01完成手轮动作并推C02上艇 | 闸门闭合、P03离开、C02独自在艇上回望 | 18 |

合计：`6+6+7+7+16+18=60 秒`。

**压缩剧本**

- `S01｜00:00–00:12｜12秒`
  - 目标：同时建立洪水、儿童、闸门与最后一班艇。
  - 动作：洪水撞击地下站远端；C03 被隔在闸门另一侧，C01 与 C02 沿闸门区引导他们向 L03 移动；P03 启动。
  - 冲突：撤离时间不足。
  - 情绪变化：从紧急协作到意识到只剩一次撤离机会。
  - 开场：水尚未进入主要泊位。
  - 收场：儿童开始登艇，洪水逼近闸门。
  - 因果：洪水迫近使关闭闸门成为必要条件。
  - 对白：无。
  - 引用：`B01、B02 / SH001、SH002 / AM01`。

- `S02｜00:12–00:26｜14秒`
  - 目标：证明电动闸门失灵，并揭示唯一解决方式。
  - 动作：C02 按下 P01 控制键；红灯闪灭，闸门停止。C01 顺着卡死的传动杆看向 L02 的 P02，判断只有手轮能完成关闭。
  - 冲突：使用 P02 的人无法随艇撤离。
  - 情绪变化：C01 从寻找常规方案转为知道自己必须作出选择。
  - 开场：闸门仍可能通过控制台关闭。
  - 收场：常规方案彻底失效，P02 成为唯一方案。
  - 因果：P01 失灵直接迫使 C01 去转 P02。
  - 对白：无。
  - 引用：`B03、B04 / SH003、SH004 / AM01`。

- `S03｜00:26–00:42｜16秒`
  - 目标：让妹妹主动承担代价，并用行动为儿童争取时间。
  - 动作：C01 冲到 L02，抓住 P02，连续转动；闸门重新下降，C03 越过最后安全线登上 P03。C02 看见她无法同时离开，转身要回去。
  - 冲突：如果 C01 松开手轮，洪水会冲入泊位；如果她继续，自己将错过最后一班艇。
  - 情绪变化：C01 从决断到平静执行；C02 从协助到抗拒失去妹妹。
  - 开场：闸门卡住，儿童仍未全部撤离。
  - 收场：儿童已上艇，C01 仍在转轮，C02 朝她返回。
  - 因果：C01 的持续动作使儿童获得逃生时间，也造成她无法登艇。
  - 对白：无。
  - 引用：`B05 / SH005、SH006 / AM01`。

- `S04｜00:42–01:00｜18秒`
  - 目标：完成锁定对白、推哥哥上艇、妹妹留下与哥哥独自逃生。
  - 动作：C01 一手稳住 P02，在 C02 靠近时把他推上 P03，说：“带他们走，别回头”。她回到 P02，把手轮转到底；闸门完全闭合。P03 驶离，C02 独自在艇尾回望，C01 留在闸门另一侧。
  - 冲突：C02 想留下，但最后一班艇已经离泊。
  - 情绪变化：C01 从平静决绝到完成选择；C02 从抗拒到被迫承受。
  - 开场：C02 试图返回，C01 尚未把手轮转到底。
  - 收场：C01 主动留下；C02 独自逃生；既定结局完成。
  - 因果：C01 推开 C02 并完成 P02，直接造成闸门关闭和 C02 独自离开。
  - 对白：C01：“带他们走，别回头”。
  - 引用：`B06 / SH007、SH008 / AM01`。

**连续性与资产圣经**

- `C01`：虚构成年妹妹；固定湿发贴在脸侧、深色防水外套、左袖红色识别带；允许疲惫、擦伤和衣物逐渐湿透；禁止脸、外套、识别带或主动选择漂移。
- `C02`：虚构成年哥哥；固定短发、浅色救援背心；允许惊慌和回望；禁止在结尾留在站内。
- `C03`：匿名儿童群体；只表现撤离轮廓与行动，不建立可识别真人身份；禁止新增个体支线。
- `L01`：闸门横跨地下站通道，洪水来自隧道侧，泊位在另一侧。
- `L02`：P02 固定在站内侧墙，与闸门机械连杆相接。
- `L03`：P03 停靠的狭窄地下泊位；艇只离开一次。
- `W01/W02`：C01 深色防水外套与红袖带；C02 浅色救援背心。
- `P01`：红色警示灯的电动控制台，SH003 后保持失灵。
- `P02`：大型金属手轮，起始未到底，SH008 收尾转到底。
- `P03`：最后一班救援艇，SH007 后离泊，SH008 不得返回。
- `LOOK01`：冷绿应急光为底，红色故障灯只在 P01 附近，洪水反光随水位增强。
- `AM01`：水压低鸣贯穿；P01 故障时警报中断；P02 转动产生金属摩擦；闸门闭合时一次低频撞击；结尾只剩艇机远去与 C02 呼吸。

**三层 Shot Graph**

- `SH001｜00:00–00:06｜6秒`
  - `story_function: setup/action`；`beat_change: 洪水由远处威胁变为可见迫近`。
  - `opening_state: L01地面仅有浅水，C03在闸门另一侧`。
  - `closing_state: 水浪撞到外层结构，C03开始向撤离方向移动`。
  - 连续性：`C01/C02/C03/L01/W01/W02/LOOK01/AM01`。
  - `state_dependencies: []`；`state_before: {water_level: low, gate: open}`；`state_after: {water_level: rising, gate: open}`。
  - 16:9：大全景横向同时交代洪水来源、闸门、儿童与远处泊位。
  - 9:16：独立重构为上方管线漏水、中部闸门、下方儿童纵深移动。
  - `coverage_role: [setup, action]`。
  - `kinetic_profile`：主体儿童向撤离方向移动；人物由停顿转为奔跑；摄影机短距离后退；水浪和灯光同时响应；验收需看到水位上升与儿童启动撤离。
  - 风险：medium；验收为 C03 始终在锁定一侧，洪水方向不反转。
  - 转场：声音桥硬切至 P03 发动；下一镜接住儿童运动方向。

- `SH002｜00:06–00:12｜6秒`
  - `story_function: goal/consequence`；`beat_change: 撤离从可能变为仅剩最后一班艇`。
  - `opening_state: C03正在撤离，P03停靠`。
  - `closing_state: 第一批儿童登艇，P03发动，C01/C02仍在闸门区`。
  - 连续性：`C01/C02/C03/L03/P03/W01/W02/LOOK01/AM01`。
  - `state_dependencies: [SH001]`；继承 `{water_level: rising, gate: open}`。
  - 16:9：中远景横向覆盖兄妹、儿童与艇，保证关系清楚。
  - 9:16：儿童自下而上登艇，兄妹分列纵轴两侧。
  - `coverage_role: [consequence, anticipation]`。
  - `kinetic_profile`：儿童登艇、兄妹引导、摄影机侧向跟随、艇机震动；验收需看到“最后一班”由唯一一艘已发动的艇表达。
  - 风险：medium；禁止增添第二艘艇。
  - 转场：P03 发动声延续到控制台特写。

- `SH003｜00:12–00:19｜7秒`
  - `story_function: obstacle/impact`；`beat_change: 电动关闭方案由可用变为失灵`。
  - `opening_state: P01亮起，闸门准备关闭`。
  - `closing_state: P01熄灭，闸门卡在半开状态`。
  - 连续性：`C02/L01/P01/LOOK01/AM01`。
  - `state_dependencies: [SH002]`。
  - 16:9：C02 与控制台同框，背景保留卡住的闸门作为结果。
  - 9:16：上部红灯、中央 C02 反应、下部按钮形成纵向因果。
  - `coverage_role: [action, impact, reaction]`。
  - `kinetic_profile`：C02按键；表演从专注到惊愕；摄影机固定；红灯熄灭、闸门震动后停止；验收需同时看见按键、故障和 C02 反应。
  - 风险：medium；精确故障字样不生成，靠灯与机械停止表达。
  - 转场：控制台熄灭的红光匹配切到 P02 冷金属高光。

- `SH004｜00:19–00:26｜7秒`
  - `story_function: reversal`；`beat_change: C01发现P02是唯一解法`。
  - `opening_state: C01面对失灵P01，尚无方案`。
  - `closing_state: C01视线锁定P02并朝L02移动`。
  - 连续性：`C01/L01/L02/W01/P01/P02/LOOK01/AM01`。
  - `state_dependencies: [SH003]`。
  - 16:9：从 C01 近景沿机械连杆拉焦到远处 P02，建立唯一物理解法。
  - 9:16：C01 在下、连杆斜向上、P02 在上，形成明确视线链。
  - `coverage_role: [reaction, consequence, transition]`。
  - `kinetic_profile`：C01转头并迈向手轮；表演由焦急变为决断；摄影机短推；连杆持续震动；验收需看到她从故障处转向唯一手轮。
  - 风险：low。
  - 转场：沿连杆方向动作匹配到她抓住 P02。

- `SH005｜00:26–00:34｜8秒`
  - `story_function: climax action`；`beat_change: 卡住的闸门重新开始下降`。
  - `opening_state: P02未到底，C01双手刚接触手轮`。
  - `closing_state: P02已转过数圈，闸门开始下降，C01不能离位`。
  - 连续性：`C01/L02/W01/P02/LOOK01/AM01`。
  - `state_dependencies: [SH004]`。
  - 16:9：中景呈现全身发力、手轮与闸门机械响应。
  - 9:16：手轮占中轴，C01身体沿纵向形成压低重心的力量线。
  - `coverage_role: [action, impact]`。
  - `kinetic_profile`：C01双脚撑地、重心左右转移推动手轮；手臂和肩背出现反作用力；摄影机缓慢靠近；连杆、闸门和积水同时响应；验收需见完整体重转移，而非静态摆姿。
  - 风险：high；失败模式为手部、轮体和反作用力异常；同槽 fallback 未获授权，因此镜头在批准前保持 draft。
  - 转场：金属摩擦声桥接儿童越过安全线。

- `SH006｜00:34–00:42｜8秒`
  - `story_function: reaction/consequence`；`beat_change: C01的牺牲使C03完成登艇，同时C02意识到她无法离开`。
  - `opening_state: 闸门正在下降，最后一批C03接近P03`。
  - `closing_state: C03全部上艇，C02转身朝C01返回`。
  - 连续性：`C01/C02/C03/L01/L03/W01/W02/P02/P03/LOOK01/AM01`。
  - `state_dependencies: [SH005]`。
  - 16:9：前景 C01 转轮，中景 C03 登艇，背景 C02 回头，三层同时读清但只以“C02意识到代价”为主变化。
  - 9:16：下层手轮、中央儿童、上层 C02 回头形成纵向因果。
  - `coverage_role: [reaction, consequence]`。
  - `kinetic_profile`：儿童完成登艇、C02停步转身、C01持续转轮、闸门下降；验收需看到 C02 的回头由看见 C01 留守触发。
  - 风险：high；多人层次需分层合成或受控参考，禁止新增可辨儿童支线。
  - 转场：C02逆向跑动匹配到 SH007 冲近 C01。

- `SH007｜00:42–00:51｜9秒`
  - `story_function: climax choice/hero`；`beat_change: C02试图留下，C01主动把他送上最后一班艇`。
  - `opening_state: C02接近C01，P03即将离泊，P02尚未到底`。
  - `closing_state: C02已被推上P03，C01回身抓住P02，P03开始离泊`。
  - 连续性：`C01/C02/L02/L03/W01/W02/P02/P03/LOOK01/AM01`。
  - `state_dependencies: [SH006]`。
  - 16:9：兄妹双人中景，P02 与 P03 分居画面两侧，让推开的方向和选择代价同框。
  - 9:16：C01靠近下方手轮，C02被推向上方艇口；嘴部只在原句期间清晰可见。
  - `coverage_role: [action, reaction, consequence]`。
  - `kinetic_profile`：C01借身体重心把C02推向艇口；C02先抵抗后失去支点；摄影机随推力短移；艇身和水面产生反作用；验收需看清推力、C02反应和两人最终分离。
  - 对白：C01 原句不变——“带他们走，别回头”。
  - 风险：high；手部接触、口型和艇体运动需分别验收，声音与口型能力未核实时走后期对白/对口型流程。
  - 转场：P03发动声不断，硬切回 P02；下一镜接住 C01 回身抓轮的动作。

- `SH008｜00:51–01:00｜9秒`
  - `story_function: aftermath/ending`；`beat_change: P02转到底，闸门完全闭合，C01留下而C02独自逃生`。
  - `opening_state: C01重新握住P02，闸门尚有缝，P03正在离泊`。
  - `closing_state: P02到底，闸门闭合；C01留在站内侧；C02独自在远去的P03尾部`。
  - 连续性：`C01/C02/L01/L02/L03/W01/W02/P02/P03/LOOK01/AM01`。
  - `state_dependencies: [SH007]`。
  - 16:9：横向远景以关闭闸门分割兄妹，P03驶向画外，C01留在另一侧。
  - 9:16：关闭闸门成为纵向视觉断面；下方 C01、上方远去的 C02 形成不可逆分离。
  - `coverage_role: [consequence, aftermath]`。
  - `kinetic_profile`：C01完成最后一圈并停住；C02在艇尾回望；摄影机缓慢后退；闸门撞击、水浪和艇尾流响应；验收需同时证明闸门闭合、C01未登艇、C02随艇离开。
  - 风险：medium；禁止艇返回、哥哥跳艇或妹妹意外滑倒。
  - 最后一镜无后续转场；以艇机远去和水压低鸣收尾。

Active runtime：`6+6+7+7+8+8+9+9=60 秒`。

**锁定事件追踪**

| Event | 锁定事实 | Screenplay | Shot | 结果 |
|---|---|---|---|---|
| `E01` | 洪水将淹没地下站 | S01 | SH001 | pass |
| `E02` | 儿童困在闸门另一侧 | S01 | SH001–SH002 | pass |
| `E03` | 闸门失灵 | S02 | SH003 | pass |
| `E04` | 只有站内手轮能阻断洪水 | S02 | SH004 | pass |
| `E05` | 妹妹为儿童争取逃生时间，主动留下 | S03–S04 | SH005–SH008 | pass |
| `E06` | 妹妹把手轮转到底 | S04 | SH008 | pass |
| `E07` | 妹妹推哥哥上最后一班救援艇 | S04 | SH007 | pass |
| `E08` | 对白“带他们走，别回头” | S04 | SH007 | pass |
| `E09` | 妹妹留下、哥哥独自逃生 | S04 | SH008 | pass |

事件无缺失、无重排、无矛盾。

**B 与 C 的镜头资源调整**

- `B spectacle-heavy`：剧情、对白、事件顺序和结局全部不变。把 SH001、SH005、SH008 分配为更大的环境与洪水英雄镜头，增加闸门机械响应、艇体运动和水体层次；减少 SH004 的停顿与 SH006 的反应时长，以释放复杂特效和动态构图资源。需要更多环境参考、首尾帧、分层水体与低风险 fallback；资产不足时降级回 A。
- `C performance-first`：剧情、对白、事件顺序和结局全部不变。减少 SH001 洪水大全景和 SH005 复杂机械覆盖，把资源转给 C01 决断近景、C02 回头反应、SH007 兄妹双人表演及 SH008 艇尾回望；延长呼吸、眼神和推开后的停顿，使用更多近景、特写与反打，降低复杂场景切换和水体生成负担。
- `A` 保持默认：空间因果、行动、反应与后果资源最均衡。

**门控状态**

- `narrative_clarity`
  - protagonist：pass
  - goal：pass
  - obstacle：pass
  - causality：pass
  - ending_change：pass
- `continuity_integrity`
  - status：pass_with_reversible_spatial_assumption
  - unresolved_conflicts：[]
- `screenplay_status: draft`
- `storyboard_status: draft`
- `prompt/job compilation: N/A，本轮尚未进入`
- `active_runtime_seconds: 60`

**🔴 CHECKPOINT 3 · Screenplay + Storyboard Gate · 🛑 STOP**

请确认这版 A 节奏的 60 秒剧本与双画幅分镜，是否可以锁定并进入逐镜提示词与平台任务编译？
