# God-Trial Cinematic Remake Storyboard and v003/v004 Plan

Date: 2026-07-21  
Status: dry-run creative package, no provider API invoked  
Skill: `aibiandao`  
Reference mode: public workflow inspiration only; no plot, character, frame, private API, cookie, or prompt text copied.

## Reference signals absorbed

The user pointed to two popular GitHub projects as workflow references:

- `xhongc/ai_story`: useful as a pipeline pattern: idea/theme -> script -> storyboard -> image -> camera movement -> video -> export, with stage status, pause/resume, retry/rollback, prompt/model management, and project templates.
- `XiakeMan777/seedance2.0_XYQ_APi`: useful as an operational adapter pattern: REST/OpenAI-like API wrapper, submit/poll/download task loop, retry/cancel, task IDs, provider status, credits, credential/cookie fragility, and truthful non-official-risk warnings.

What this remake does with those references:

- Keeps the director Canon above every platform.
- Treats Seedance/小云雀, Kling/可灵, HappyHorse, Jianying/CapCut, and future AI editors as adapters.
- Requires per-stage lifecycle, prompt/model versioning, provenance, retry/rollback, and export notes.
- Keeps all unverified provider fields in manual configuration; no private API schema or cookie workflow is fabricated.

## Creative boundary

Benchmark feeling requested by user: short-drama scale similar to a high-polish AI fantasy/action sample: urban supernatural trial, large-screen feeling, kinetic transitions, serial hook.

This is an original concept-mode remake draft, not an imitation package. The story below does not copy a known short drama’s characters, plot, names, dialogue, shot order, or exact images.

Working title: `EP01｜硬币不是神`  
Format: 60 seconds, rhythm preset A by default  
Delivery: dual version, 16:9 master and independent 9:16 recomposition  
Platforms: Kling/可灵, Seedance/小云雀, HappyHorse; editing handoff for Jianying/CapCut and future AI editor  
Execution status: non-executable until official schemas, credentials, credits, reference assets, and exact output directory are authorized.

## `project_brief.intent_contract`

Core message: 神性不是赐予力量，而是一个人看见代价之后，仍然选择替别人承担。  
Audience takeaway: 主角不是被选中的爽文英雄；他先做出选择，然后力量才被迫回应。  
Emotional destination: 从“规则碾压普通人”的冷感，转向“人性反过来审判神性”的震动。  
Must-show claims:

- `INT-001`: 试炼规则诱导主角把同伴当筹码。
- `INT-002`: 主角明确拒绝交易，选择让伤害落到自己身上。
- `INT-003`: 神性回应的原因是选择，不是天赋、血统或随机中奖。
- `INT-004`: 结尾留下可连环制作的下一集钩子：硬币背面出现新的神名。

Must-not-imply:

- 不暗示主角靠“天选血脉”直接开挂。
- 不把同伴拍成纯工具人；她必须有可见反应和记忆证据。
- 不用无关巨兽、宫殿、星球毁灭等漂亮但不服务意图的镜头。
- 不依赖生成画面里的可读 UI 字符；所有规则文字、字幕、神名进后期合成。

Metaphor policy: 硬币、水面倒影、黑色光环只用于表达“交易/审判/代价”，不能新增世界观事实。  
Source-fidelity rule: 如果后续用户提供完整剧本，保留用户锁定事件；本稿作为可回滚的原创机制草案。

## Character and model lock

| ID | Identity profile | Stable anchors | Reference requirement | Model-lock rule | Drift blocker |
|---|---|---|---|---|---|
| `C01` 林砚 | `IDP-C01-lin-yan-v003` | 23 岁男性，偏瘦，短黑发，左眉尾一条细疤，黑色连帽外套外穿灰色雨衣，右手虎口有旧伤 | 需要正脸、中景、侧脸、手部伤痕 4 张 approved refs；无 refs 时所有人物生成 job 只能 `non_executable` | 同一平台内固定 `model_family`、同一 reference set、同一 identity profile；跨平台迁移需 A/B 审核 | 脸型、发长、眉疤、雨衣颜色、旧伤、年龄感任一漂移即 block |
| `C02` 祁雨 | `IDP-C02-qi-yu-v003` | 22 岁女性，齐肩黑发，蓝白校队外套，左腕红绳，右膝有擦伤 | 需要正脸、中景、左腕红绳、外套 4 张 approved refs | 与 `C01` 分开绑定，不用“same girl/person”替代 ID | 红绳消失、外套换色、年龄漂移、脸变网红化即 block |
| `A01` 白面裁判 | `IDP-A01-white-judge-v003` | 无性别感人形，白色无五官面具，初始完整黑环悬在后脑，不直接接触地面；`SH011` 首次裂开 | 可用形象参考或纯提示词；但面具、黑环、悬浮状态必须固定 | 不允许每镜换成不同怪物、神、骑士或机器人 | 出现真实宗教符号、可识别品牌/文字、过度恐怖血腥即 block |
| `P01` 黑硬币 | `IDP-P01-black-coin-v003` | 哑黑硬币，边缘有一道银色缺口，落水时不沉，背面可后期合成神名 | 首尾帧或道具参考优先；文字进后期 | 道具 ID 全片固定，不变成宝石、钥匙、卡牌 | 变色、变形、出现乱码字、数量翻倍即 block |

## Series continuity handoff

`series_context` remains draft until an external series/project controller exists.

- `series_project_id`: `SER-urban-god-trial-original`
- `episode_id`: `EP01`
- `series_snapshot_id`: `SNAP-EP01-v003-draft`
- `asset_registry_version`: `assets-v003-draft`
- `episode_opening_state_ref`: 普通城市夜雨，主角尚未知道试炼存在。
- `foreshadow_refs`: `P01` 缺口、`A01` 黑环、`C02` 左腕红绳、硬币背面神名。
- `payoff_refs`: EP02 可回收“神名回应主角选择”、C02 保留记忆、裁判第一次失控。
- `commit_eligibility`: `external_series_controller_required`

Draft `quality_report.series_handoff`:

- `handoff_status`: `draft`
- `episode_closing_state_delta`: 林砚右手出现硬币形烧痕；祁雨保留记忆；裁判黑环首次裂开；`P01` 背面出现新神名。
- `continuity_evidence_refs`: `SH009` 伤害转移、`SH010` 祁雨见证、`SH011` 黑环裂开、`SH012` 硬币回掌。
- `foreshadow_status_changes`: `P01` 从试炼道具升级为回应载体；`C02` 从被标记者变成记忆见证者。
- `payoff_status_changes`: EP02 必须解释“第二局”和神名回应，不能重置主角伤痕或祁雨记忆。
- `commit_eligibility`: `external_series_controller_required`

## Scene directing plans

### `S01` 试炼降临，0-18s

POV: 观众与林砚同步理解规则，只比他早半秒看见硬币异常。  
Dramatic turn: 城市不是变大，而是时间突然停止；普通夜晚变成试炼场。  
Blocking map: 林砚在屋顶排水沟旁，祁雨在天台玻璃门另一侧，裁判先只出现在水面倒影。  
Camera rule: 先用可触摸的小物件进入，再扩展城市尺度；每次变大必须回到人物选择。  
Reveal strategy: 硬币 -> 水面倒影 -> 眼睛反射 -> 全景冻结，避免开场就堆特效。  
Editorial consequence: 镜头之间用硬币声、水纹、眼神方向做匹配转场，不用硬切 PPT。

### `S02` 规则诱捕，18-38s

POV: 观众知道交易诱惑，祁雨不知道自己被标记；林砚必须先看懂代价。  
Dramatic turn: “获得神力”被揭示为“献出同伴”。  
Blocking map: 裁判站在前景左侧，伸手递光；祁雨在后景右侧被玻璃门影子困住；林砚夹在两者中间。  
Camera rule: 任何壮观光效都必须显示权力关系：谁逼近、谁退后、谁被隔离。  
Rejected choices: 不拍无意义怪兽降临，不拍主角摆 pose 变身，不拍三连静态大景。

### `S03` 代价选择，38-60s

POV: 观众先看到林砚决定，再看到力量回应；祁雨看到伤口，从而成为下一集记忆锚点。  
Dramatic turn: 林砚不是接受神力，而是把交易硬币按进自己掌心，规则被迫改写。  
Blocking map: 林砚横穿裁判与祁雨之间，身体挡住神火；硬币落入水面又回到掌心。  
Camera rule: 镜头必须跟随选择造成的空间改变，不靠粒子乱飞证明“大片”。  
Hook: 硬币背面的神名由后期字幕/图层合成，最后 0.5s 只给声音和刻痕。

## 60-second active storyboard

All active shot durations sum to exactly 60 seconds. Each shot carries `intent_refs`; if a generated clip cannot prove its refs, regenerate or cut it.

| Shot | Time | Intent | Story function | Action -> reaction -> consequence | Camera and blocking | Motion layers | Transition and edit note |
|---|---:|---|---|---|---|---|---|
| `SH001` | 0-4 | `INT-001` | Hook by object | `P01` rolls through rainwater, hits Lin Yan’s boot -> he looks down -> the coin stops standing upright | Macro low-angle dolly beside puddle; boot enters frame from right | coin roll, rain ripples, boot splash | Sound prelap of a coin spin; cut on metallic stop, not a static object insert |
| `SH002` | 4-9 | `INT-001` | World freeze reveal | Lin Yan bends to pick it up -> rooftop rain freezes midair -> distant city traffic becomes still light trails | Crane-pull from hand to wide rooftop; Lin Yan stays foreground small | hand reach, suspended rain, distant lights | Match the coin circle to a frozen traffic loop |
| `SH003` | 9-13 | `INT-001` | Rule appears without generated text reliance | Coin levitates to eye level -> unreadable glyph light reflects in his pupil -> he recoils half a step | Extreme close-up eye reflection; glyph layer planned in post | eyelid flinch, coin hover, light sweep | Eye blink hides cut to reflection world |
| `SH004` | 13-18 | `INT-001` | Antagonist reveal | Water reflection shows `A01` behind him -> Lin Yan turns but the roof is empty -> the reflection smiles without a mouth | Over-shoulder to puddle reflection; rack focus between real roof and reflection | head turn, ripple distortion, black halo drift | Ripple wipe into the judge’s hand, preserving screen direction |
| `SH005` | 18-23 | `INT-001`, `INT-002` | Stakes attach to companion | Glass door behind Lin Yan lights up around `C02` -> she pounds once, unheard -> Lin Yan sees her trapped | Long-lens two-plane shot: Lin Yan foreground left, Qi Yu background right behind glass | palm impact, breath fog, glass cracks of light | Cut on Qi Yu’s hand impact to judge’s offered hand |
| `SH006` | 23-29 | `INT-001`, `INT-002` | Temptation diagram | `A01` extends a small sun-like coin-light -> Qi Yu’s mark brightens -> Lin Yan’s shadow splits toward both | Lateral tracking, judge foreground, Lin Yan center, Qi Yu background | hand extension, light pulse, shadow split | L-cut with judge voice/text handled in post; no generated mouth text |
| `SH007` | 29-34 | `INT-002` | Refusal made visible | Lin Yan opens his palm toward the offer -> then closes his fist around the black coin -> bloodless burn mark appears | Tight hand close-up with face blurred behind, then focus racks to his eyes | fingers close, ember under skin, focus shift | Match-on-action from closed fist to body crossing frame |
| `SH008` | 34-40 | `INT-002` | Choice changes space | Lin Yan runs across the judge-Qi Yu line -> shoulder hits invisible pressure -> he plants himself in front of the glass | Handheld controlled side-track; camera dragged by his motion, not shaky chaos | run, impact compression, rain resumes around him | Whip pan must land on Qi Yu’s reaction, not on abstract light |
| `SH009` | 40-45 | `INT-002`, `INT-003` | Cost lands on protagonist | Godfire strikes where Qi Yu was marked -> Lin Yan takes it through his right hand -> the glass mark dies | Slow push-in from Qi Yu side, Lin Yan back to camera, fire impact on hand | impact flare, coat snap, mark extinguish | Sound drops to muffled heartbeat; avoid music-only climax |
| `SH010` | 45-50 | `INT-002`, `INT-003` | Witness memory | Qi Yu sees Lin Yan’s wound reflected in glass -> she remembers the coin shape -> fear changes to recognition | Close two-shot through cracked glass, Qi Yu foreground reflection and Lin Yan beyond | breath fog clearing, eye movement, reflected wound | Motivated hold on her breath, then cut when she exhales |
| `SH011` | 50-56 | `INT-003`, `INT-004` | Rule forced to answer | Lin Yan throws the coin into the puddle -> city lights blink like watching eyes -> black halo around judge fractures | Low wide with puddle foreground; Lin Yan silhouette; judge reflection breaks first | coin splash, city blink, halo crack | Water splash becomes vertical black frame for 9:16 recomposition |
| `SH012` | 56-60 | `INT-004` | Serial hook | Coin rises back into Lin Yan’s burned palm -> back face reveals a new engraved god-name in post -> judge whispers “第二局” | Extreme close-up palm, coin fills safe title area; no face change | palm tremor, coin rotation, final rain drop | End on hard sound cut; freeze only the final 6 frames as a deliberate hook |

## Formal storyboard gate addendum

This addendum turns the human-readable storyboard into a gate-ready draft. It is still not an executable ten-object JSON package, but every active shot now names the fields that prevent PPT drift.

| Shot | `coverage_role` | `dramatic_question` | Delta evidence | State dependency | `state_before` -> `state_after` | Director fields | `kinetic_profile.acceptance_evidence` |
|---|---|---|---|---|---|---|---|
| `SH001` | `action` | 为什么一枚普通硬币能打断夜雨？ | information: coin is abnormal; spatial: coin reaches C01 boot | none | `P01 rolling, rain active, C01 unaware` -> `P01 upright, rain around coin disturbed, C01 looks down` | blocking_change: boot enters coin path; camera_necessity: macro makes the rule tactile before spectacle; performance_verb: notice; shot_relation: object hook into world reveal; director_rejection_reason: rejects opening with abstract god palace | coin visibly rolls, boot splash changes water, coin stops upright without becoming static title card |
| `SH002` | `consequence` | 硬币异常会把城市变成什么？ | information: trial freezes city; emotion: C01 confusion; spatial: hand-to-sky scale shift | `SH001.P01 upright` | `C01 bends, rain active` -> `rain suspended, city lights frozen, C01 isolated` | blocking_change: C01 bends then freezes under vast sky; camera_necessity: crane pull proves scale while keeping him small; performance_verb: recoil; shot_relation: expands SH001 object into world rule; director_rejection_reason: rejects empty skyline beauty | hand reach, suspended rain, distant frozen light trails all visible in one continuous move |
| `SH003` | `reaction` | 主角是否理解规则在看着他？ | information: rule reflection appears; emotion: shock; power: unseen system enters his body space | `SH002.rain suspended` | `P01 near hand, C01 confused` -> `P01 eye-level, C01 flinches, rule text reserved for post` | blocking_change: coin invades eye line; camera_necessity: eye reflection ties rule to perception; performance_verb: flinch; shot_relation: subjective bridge to antagonist; director_rejection_reason: rejects unreadable generated UI as plot evidence | eyelid movement, reflected coin/glyph light, half-step recoil or head snap |
| `SH004` | `reaction` | 裁判是真在身后，还是只存在于规则倒影里？ | information: A01 first appears; emotion: dread; spatial: real roof/reflection contradiction | `SH003.C01 flinch` | `puddle empty, C01 turns attention` -> `A01 visible only in reflection, real roof empty, black halo stable` | blocking_change: C01 turns away from coin to reflection; camera_necessity: reflection makes the judge uncanny without adding lore; performance_verb: search; shot_relation: antagonist reveal; director_rejection_reason: rejects random monster entrance | puddle ripple, rack focus, C01 head turn, A01 mask/halo remain stable; fallback splits into puddle insert + C01 turn |
| `SH005` | `consequence` | 规则把代价绑到了谁身上？ | information: C02 is marked; emotion: C01 alarm; power: C02 loses agency behind glass | `SH004.A01 reveal` | `C02 outside C01 awareness, glass unmarked` -> `C02 trapped, red wrist visible, mark active, C01 sees her` | blocking_change: two planes connect C01 foreground and C02 background; camera_necessity: telephoto compresses moral distance; performance_verb: register; shot_relation: stakes after antagonist; director_rejection_reason: rejects companion as faceless victim | C02 hand impact, breath fog, mark brightening, C01 eye-line lands on her |
| `SH006` | `action` | 主角会不会接受用同伴交换力量？ | information: offer terms become visible; emotion: temptation vs refusal beginning; power: judge controls frame geometry | `SH005.C02 mark active` | `A01 present, C02 marked, C01 between` -> `offer light extended, C01 hand pulled but not closed, shadow splits` | blocking_change: C01 is physically centered between A01 and C02; camera_necessity: lateral track diagrams choice without speech; performance_verb: resist; shot_relation: temptation before refusal; director_rejection_reason: rejects concept-poster light show | A01 hand extension, C01 hand micro-move then resistance, C02 mark pulse, shadow split all readable |
| `SH007` | `action` | 拒绝是否发生在身体上，而不是台词里？ | information: C01 chooses coin not offer; emotion: resolve; power: transaction route breaks | `SH006.offer light extended` | `C01 hand open near offer, P01 unclaimed` -> `C01 fist closed around P01, right-hand burn begins` | blocking_change: open palm becomes closed fist; camera_necessity: close-up proves decision; performance_verb: choose; shot_relation: refusal before crossing; director_rejection_reason: rejects heroic pose without choice evidence | fingers close over exact coin, old scar visible, burn appears under skin, focus rack to eyes |
| `SH008` | `action` | 他会不会真的把身体放进代价路径？ | information: C01 breaks the judge-C02 line; emotion: panic becomes action; spatial: body crosses pressure barrier | `SH007.fist closed` | `C01 beside offer line, C02 exposed` -> `C01 planted between fire path and C02, pressure ripple around shoulder` | blocking_change: C01 moves from center gap to shield position; camera_necessity: side-track proves body path; performance_verb: cross/protect; shot_relation: refusal becomes physical cost; director_rejection_reason: rejects camera shake as fake movement | full body start/run/impact/plant path, shoulder compression, Qi Yu reaction in whip-pan landing |
| `SH009` | `consequence` | 代价有没有真的落在主角身上？ | information: C02 mark extinguishes; emotion: pain restrained; power: rule forced to reroute | `SH008.C01 planted` | `C02 mark active, C01 hand burned-start` -> `C02 mark off, C01 right-hand wound active, coat snapped by impact` | blocking_change: C01 blocks line of force; camera_necessity: push from C02 side proves he intercepts what targeted her; performance_verb: absorb; shot_relation: cost after protection; director_rejection_reason: rejects particle-only climax | godfire contact on C01 right hand, C02 mark visibly dies, C01 body reacts, no random explosion replaces causality |
| `SH010` | `reaction` | 祁雨有没有成为下一集的记忆证人？ | information: C02 sees wound and coin shape; emotion: fear -> recognition; power: witness memory escapes reset | `SH009.C01 wound active, C02 mark off` | `C02 frightened behind glass, breath fog heavy` -> `C02 recognizes wound, breath clears, red wrist still visible` | blocking_change: C02 moves from pounding to still witness; camera_necessity: glass reflection connects her memory to his wound; performance_verb: recognize; shot_relation: witness after cost; director_rejection_reason: rejects pretty crying close-up without memory evidence | eye movement to wound reflection, breath fog clears, hand lowers, red string remains stable |
| `SH011` | `consequence` | 人的选择能不能让规则第一次失控？ | information: judge halo fractures; emotion: awe replaces dread; power: rule responds to C01 | `SH010.C02 recognizes` | `P01 in C01 burned fist, A01 halo whole` -> `P01 thrown into puddle, city blink motif, A01 halo cracked` | blocking_change: C01 throws P01 down, judge reflection breaks before real world reacts; camera_necessity: low wide ties object, city, judge into consequence; performance_verb: defy; shot_relation: rule answer before hook; director_rejection_reason: rejects new gods/worldbuilding montage | coin splash, city light blink, halo fracture, C01 silhouette all visible; motif only, no new deity |
| `SH012` | `reaction`, `consequence` | 第二局为什么不可避免？ | information: new god-name appears; emotion: dreadful invitation; power: coin returns despite refusal | `SH011.P01 in puddle, halo cracked` | `P01 underwater, C01 palm wounded` -> `P01 back in palm, post-layer god-name, final hook freeze` | blocking_change: object returns upward into still hand; camera_necessity: close-up makes serial object contract readable; performance_verb: endure; shot_relation: hook after consequence; director_rejection_reason: rejects static logo ending | palm tremor, coin rotation, rain drop hit, final freeze limited to last 6 frames and motivated by hook |

`coverage_role` union: `action`, `reaction`, and `consequence` are all covered repeatedly; no shot is only a decorative establishing image.

## Formal transition contracts

Frame durations assume a 24 fps edit base; if export fps changes, recalculate frames without changing story reason.

| Boundary | Declared type | `duration_frames` | Story reason | Visual precondition | Incoming match | Audio bridge | Fallback if dropped |
|---|---:|---:|---|---|---|---|---|
| `SH001->SH002` | match cut | 0 | object anomaly expands into world anomaly | coin upright in puddle | coin circle to frozen traffic loop | metallic coin ring continues | hard cut allowed only on same coin ring tail |
| `SH002->SH003` | scale compression cut | 0 | city rule enters personal perception | suspended rain and C01 looking down/up | frozen raindrop glint to eye highlight | city ambience sucks out | insert coin hover before eye if match fails |
| `SH003->SH004` | blink/ripple bridge | 4 | subjective rule reveals hidden judge | eye reflection contains abstract glyph light | eyelid dark frame to puddle dark ripple | low reversed chime | eye close-up to puddle insert hard cut with chime |
| `SH004->SH005` | impact cue cut | 6 | antagonist reveal attaches stakes to C02 | A01 reflection visible, real roof empty | ripple bright edge to glass mark edge | water ripple becomes muffled thump | direct cut to C02 palm hit if ripple fails |
| `SH005->SH006` | action match | 0 | victim mark becomes offer diagram | C02 palm impact and mark active | C02 hand impact to A01 offered hand | muffled impact under judge tone | hard cut on impact transient |
| `SH006->SH007` | L-cut | 0 | temptation pressure continues into decision | A01 offer light extended, C01 hand pulled | offer glow to coin ember | judge line/text-card tail continues | cut to hand close-up with lingering offer glow |
| `SH007->SH008` | match-on-action | 0 | refusal becomes body movement | C01 fist closed, eyes resolved | fist exits frame to shoulder/body crossing | heartbeat starts | fist close-up to side-track start frame |
| `SH008->SH009` | impact continuation | 2 | protection causes cost | C01 planted between path and C02 | pressure ripple to godfire contact | heartbeat peaks then muffles | hold one extra frame on C01 planted if contact continuity fails |
| `SH009->SH010` | reaction cut | 0 | cost must be witnessed | C01 wound active, C02 mark off | wound flare to glass reflection | muffled heartbeat to breath | insert wound reflection before C02 face |
| `SH010->SH011` | breath-to-water cut | 4 | witness memory lets rule answer begin | C02 breath clears, eyes on wound | exhale fog edge to puddle mist | exhale becomes rain splash | hard cut on exhale if visual match fails |
| `SH011->SH012` | object return match | 6 | defiance creates next-game hook | coin splash and halo crack | black water circle to black coin in palm | low choir cuts to single whisper | black-frame cut with coin ring, not a slideshow dissolve |

## Formal kinetic profile split

Each shot’s `kinetic_profile` must be expanded into these fields when converting this dry-run storyboard into a strict JSON package:

- `subject_motion`: the character or object path that carries the causal action.
- `performance_change`: observable face, breath, posture, hand, or eye-line change.
- `camera_motion`: why the camera moves or why it is locked.
- `environment_motion`: rain, water, glass, city lights, pressure, or halo motion that supports but never replaces subject action.
- `motion_layers_required`: minimum visible layers; non-hold cinematic shots require at least two distinct layers.
- `intentional_hold`: true only for the final 6-frame hook or a motivated recognition beat.
- `hold_reason`: required whenever `intentional_hold` is true.
- `acceptance_evidence`: what reviewers must see before accepting the generated clip.

## Structured `scene_directing_plan` expansion notes

The prose scene plans above must become objects before a validator-bound package:

- `S01`: `audience_knowledge_before`: no one knows the rule; `audience_knowledge_after`: coin and frozen rain prove trial entry; `character_objectives`: C01 wants to understand/escape; `subtext_and_playable_actions`: notice, recoil, search; `coverage_strategy`: object macro -> human reaction -> scale reveal; `visual_motif_progression`: coin/water/eye; `intent_refs`: `INT-001`.
- `S02`: `audience_knowledge_before`: C02 is present but unmarked; `audience_knowledge_after`: offer requires sacrificing C02; `character_objectives`: A01 tempts, C01 evaluates, C02 tries to reach him; `subtext_and_playable_actions`: resist pull, pound glass, offer power; `coverage_strategy`: two-plane moral diagram; `visual_motif_progression`: mark/offer/shadow split; `intent_refs`: `INT-001`, `INT-002`.
- `S03`: `audience_knowledge_before`: C01 can refuse but cost is unresolved; `audience_knowledge_after`: choice forces rule response and seeds EP02; `character_objectives`: C01 protects, C02 witnesses, A01 contains the breach; `subtext_and_playable_actions`: cross, absorb, recognize, defy; `coverage_strategy`: body path -> impact -> witness -> object hook; `visual_motif_progression`: wound/black water/coin return; `intent_refs`: `INT-002`, `INT-003`, `INT-004`.

## Per-shot prompt compiler notes

Global positive anchor for all active shots:

```text
cinematic anime short film, original urban supernatural trial, rainy city rooftop at night, grounded human performance before spectacle, volumetric rain, wet concrete reflections, dramatic but readable blocking, 35mm film language, controlled camera movement, motivated transitions, consistent fictional characters and props, no readable generated text, no logos
```

Global negative anchor:

```text
static poster, slideshow, PowerPoint-like tableau, unrelated monsters, random palace, random sci-fi armor, face drift, hair drift, costume drift, duplicate character, duplicate coin, unreadable UI text, watermark, overbright particles without subject action, unmotivated hard cut, mechanical equal-duration grid
```

| Shot | `universal_prompt_en` seed | Provider caution |
|---|---|---|
| `SH001` | `Macro low-angle tracking shot of one matte black coin with a silver nick rolling through rainwater toward a young man’s boot on a wet rooftop; the coin stops upright by itself, rain ripples freeze around it.` | Use if provider handles macro object motion; fallback is first-frame coin already rolling plus last-frame upright. |
| `SH002` | `A young man in a gray raincoat bends toward the black coin as the rooftop rain freezes midair and distant city traffic turns into still light trails; crane pullback from hand to wide skyline.` | Avoid static skyline; require protagonist hand motion and frozen rain evidence. |
| `SH003` | `Extreme close-up of the young man’s eye reflecting the hovering black coin and abstract trial glyph light; he flinches backward, no readable text, post-production adds rule overlay.` | Do not ask the model to render exact words. |
| `SH004` | `Over-shoulder shot into a puddle reflection where a faceless white-masked judge with a cracked black halo appears behind the young man; he turns and the real rooftop is empty.` | Reflection continuity is high-risk; fallback is mirror-like puddle insert plus separate turn reaction. |
| `SH005` | `Two-plane telephoto rooftop shot: young man foreground left, young woman behind a glass rooftop door background right, her left wrist red string visible as a light mark traps her; she pounds once unheard.` | Identity refs required for both C01 and C02. |
| `SH006` | `Lateral tracking shot, white-masked judge foreground extending a small sun-like coin light, young man center, trapped young woman background; shadows split toward the offer and the victim.` | No extra deities; the blocking must show the moral diagram. |
| `SH007` | `Tight close-up of the young man's right hand with old scar closing around the matte black coin; a bloodless ember burn appears under skin, focus racks to his determined eyes behind the fist.` | Must preserve right-hand scar and coin shape. |
| `SH008` | `Controlled side-tracking action shot as the young man crosses the line between judge and trapped woman, hits invisible pressure, then plants himself between godfire and glass door.` | Motion must be character-driven, not camera shake. |
| `SH009` | `Slow push-in from behind the trapped woman as supernatural fire strikes the young man’s right hand instead of her mark; the glass mark extinguishes while his raincoat snaps from impact.` | Require consequence: C02 mark disappears, C01 hand takes cost. |
| `SH010` | `Close two-shot through cracked wet glass: the young woman sees the burned coin-shaped wound reflected on the young man's hand; her fear shifts into recognition as breath fog clears.` | A motivated hold is allowed only if eye/breath/reflection changes occur. |
| `SH011` | `Low wide rooftop shot with puddle foreground as the young man throws the black coin into water; city lights blink like watching eyes and the judge's black halo fractures in reflection.` | City blink is motif, not new gods entering the story. |
| `SH012` | `Extreme close-up of burned palm as the matte black coin rises back and slowly rotates; the back face is reserved for a post-production engraved god-name, final rain drop hits the coin.` | Exact god-name added in edit, not generated pixels. |

## Platform job lifecycle template

For a production package, expand this into one job per `shot_id`, `aspect`, and selected provider. These are lifecycle records, not authorization to call APIs.

| Provider | Job purpose | Lifecycle | Required evidence before executable | Manual-only risk |
|---|---|---|---|---|
| Seedance / 小云雀 | High-motion cinematic shots, especially `SH008-SH011` | `draft -> submit_ready -> submitted(task_id) -> polling(provider_status) -> downloaded(local_file) -> reviewed -> accepted_or_retry` | current official/public schema, credentials, credit balance, accepted reference inputs, output path, task ID, result URL/file, review notes | cookie/private web API volatility, credit use, account risk, changing internal fields |
| Kling / 可灵 | Identity/reference-heavy alternates for `C01/C02`, first/last-frame attempts | same lifecycle as above | official model/mode/aspect/duration/reference docs, model-family lock, reference binding evidence | undocumented params, model migration, reference-count limits |
| HappyHorse | Fallback or batch provider where verified fields are available | same lifecycle as above | only verified adapter fields, cost/limit note, result binding | unknown capability must stay in `requires_manual_configuration` |
| Jianying / CapCut | Assembly, subtitles, overlays, sound, color, export handoff | `construction_sheet -> manual_import_or_ai_editor_plan -> dry_run_review -> authorized_execution -> rendered -> probe -> creative_review` | exact media files, SRT, overlays, music/SFX rights, timeline spec, output dir authorization | no fabricated private project schema |
| Future AI editor | Edit automation derivative | `ai_editor_plan.json -> tool_dry_run -> authorization -> execution_evidence` | same Canon IDs, exact edit units, transition/audio/text/look specs, evidence | AI editor may not obey transitions; failed fulfillment returns to timeline/storyboard |

Example non-executable job record:

```json
{
  "job_id": "JOB-seedance-SH008-16x9-v003",
  "shot_id": "SH008",
  "job_purpose": "primary_generation",
  "model_family": "seedance-manual",
  "generation_mode": "text_to_video_or_reference_to_video_unverified",
  "prompt_source": {
    "shot_prompt_id": "PROMPT-SH008-v003",
    "global_lock_source": "project_brief.intent_contract",
    "direction_source": "storyboard.SH008"
  },
  "reference_inputs": [
    "REF-C01-profile-approved",
    "REF-C02-profile-approved",
    "REF-P01-coin-approved"
  ],
  "duration_seconds": 6,
  "aspect": "16:9",
  "resolution": "requires_manual_configuration",
  "documented_parameters": {},
  "requires_manual_configuration": [
    "official_schema_current",
    "credentials_or_cookie_risk_decision",
    "credit_balance",
    "model_version",
    "aspect_mapping",
    "reference_binding_mode",
    "submit_endpoint",
    "poll_endpoint",
    "download_binding"
  ],
  "approval_status": "non_executable",
  "operation_state": {
    "execution_mode": "non_executable",
    "submit_status": "blocked_until_authorized",
    "poll_status": "not_started",
    "download_status": "not_started",
    "task_id": null,
    "provider_status": null,
    "result_url_or_file_ref": null,
    "retry_policy": "retry only after identity/action/transition review names the failure",
    "retry_count": 0,
    "cancel_status": "not_requested",
    "cost_credit_notes": "not executed; credits unknown",
    "credential_risk": "third-party cookie/private web API risk is manual-only",
    "provider_evidence_refs": []
  }
}
```

## Jianying/CapCut and AI-editor construction sheet

The edit must not feel like PPT. The timeline below tells the editor what to cut on, what to bridge with sound, and what must be added in post.

| Edit unit | Timeline | Source shot | V1 picture action | V2/V3 overlays | A1/A2 sound | Transition rule |
|---|---:|---|---|---|---|---|
| `EU001` | 00:00-00:04 | `SH001` | coin roll macro | none | coin spin + rain close | cut on metallic stop |
| `EU002` | 00:04-00:09 | `SH002` | crane pull to frozen city | subtle rain freeze glints | coin resonance continues under ambience | match coin circle to traffic loop |
| `EU003` | 00:09-00:13 | `SH003` | eye reflection flinch | rule glyph graphic, no generated text | short sub-bass inhale | blink cut |
| `EU004` | 00:13-00:18 | `SH004` | puddle judge reveal | black halo accent | water ripple + distant reversed chime | ripple wipe |
| `EU005` | 00:18-00:23 | `SH005` | Qi Yu trapped behind glass | mark graphic on glass | muffled hand impact | impact to offered hand |
| `EU006` | 00:23-00:29 | `SH006` | judge offers light | optional rule subtitle in post | judge line or text card, low voice | L-cut into decision |
| `EU007` | 00:29-00:34 | `SH007` | fist closes around coin | burn mark composited if needed | skin ember hiss, heartbeat starts | match fist to body crossing |
| `EU008` | 00:34-00:40 | `SH008` | Lin Yan crosses pressure line | pressure distortion | heartbeat rises, rain tears open | whip pan must land on Qi Yu |
| `EU009` | 00:40-00:45 | `SH009` | godfire hits Lin Yan | impact flash, mark extinguish | sound muffles, heartbeat dominates | audio drop, not random flash cut |
| `EU010` | 00:45-00:50 | `SH010` | Qi Yu recognizes wound | none or tiny reflection polish | breath, glass creak | cut on exhale |
| `EU011` | 00:50-00:56 | `SH011` | coin splash, halo fractures | city blink motif | low choir swell, no lyrics | water splash to black vertical band |
| `EU012` | 00:56-01:00 | `SH012` | coin returns to palm | engraved god-name, episode hook subtitle | whisper “第二局”, final hard cut | final 6-frame freeze is motivated hook only |

Required tracks:

- `V1`: generated active clips in shot order.
- `V2`: post text/glyphs; all exact rules, numbers, subtitles, god-names live here.
- `V3`: transition mattes, water/black-frame accents, optional light polish.
- `A1`: atmosphere and music bed.
- `A2`: object/impact/heartbeat/breath SFX.
- `A3`: voice/dialogue, if authorized; otherwise text card/SRT.
- `S1`: SRT subtitles and hook text.

Export notes:

- Build `v003` as `rough/fine candidate`, not final.
- Build `v004` only after failed shots are regenerated or explicitly accepted.
- Probe file duration, fps, resolution, audio channel layout, and black-frame gaps before any final claim.
- `cinematic_ready` remains false until `intent_fidelity`, `director_quality`, `identity_integrity`, `transition_fulfillment`, `audio_presence_and_structure`, and rendered review pass.

## v003 remake plan

Purpose: replace the PPT-like attempt with a true cinematic reconstruction while preserving earlier versions.

Inputs:

- Prior v001/v002 artifacts are preserved as references only; do not overwrite or relabel them.
- Approved or newly created identity references for `C01`, `C02`, `A01`, `P01`.
- This storyboard as `STORYBOARD-v003-draft`.

Steps:

1. Freeze Canon: `intent_contract`, `scene_directing_plan`, identity profiles, prop/location/look IDs, and shot durations.
2. Generate or select reference stills for C01/C02/P01; approve before any video job.
3. Compile per-shot prompts and fallback shots for high-risk shots `SH004`, `SH008`, `SH009`, `SH011`.
4. Create non-executable multi-platform job manifest for 12 shots x 2 aspects x selected providers.
5. Run provider tests on 3 representative shots first: `SH004` reflection, `SH008` body action, `SH010` emotional recognition.
6. If identity or action fails twice on one provider, migrate that shot to fallback provider or first/last-frame workflow.
7. Build Jianying/CapCut construction sheet and `ai_editor_plan.json` from the same edit units.
8. Dry-run bundle into a new `v003` directory; no FFmpeg/NLE/API execution without exact authorization.

v003 acceptance:

- Can be accepted as a reconstructed rough/fine candidate if all shot-level review items are present.
- Cannot be called final if any clip is placeholder, any transition is unfulfilled, or any audio/text overlay is missing.
- Must output failure ladder in this order: story/action -> storyboard kinetic contract -> prompt/media regeneration -> timeline/edit -> sound.

## v004 remake plan

Purpose: final candidate after v003 review, not a simple copy.

Allowed changes:

- Regenerate only failed shots or failed identity/action variants.
- Re-time transitions by story motivation, not by making every shot equal length.
- Add final SRT, rule overlays, god-name graphic, sound mix, color pass, and 16:9/9:16 separate export settings.
- Preserve `shot_id`, identity profile IDs, prop IDs, and intent refs unless the user approves a story-level change.

Hard requirements:

- Each rendered edit unit has local media binding, duration evidence, and review note.
- Package-level `quality_report.checks.intent_fidelity.status == "pass"` and `quality_report.checks.director_quality.status == "pass"`.
- Edit-level `cinematic_validation.intent_fidelity.status == "passed"` and `cinematic_validation.director_quality.status == "passed"` with empty unresolved rejected-pattern flags.
- Identity/model locks pass on C01, C02, A01, P01.
- No unresolved `image_slide_only`, `mechanical_equal_duration_grid`, `unrelated_spectacle`, or `hard_cut_without_motivated_transition` flags.

v004 can become final only after technical probe and creative review both pass. If it merely renders successfully, it is still not automatically cinematic.

## Specific anti-PPT rules for this remake

- No shot exists just because it is cool; every shot must answer what changed.
- No equal-duration grid: 4/5/4/5/5/6/5/6/5/5/6/4 creates pressure waves around choices.
- No unmotivated hard cuts: every boundary has sound bridge, match action, ripple, blink, impact, or breath motivation.
- No text-in-pixels dependency: exact rules and god-name are post layers.
- No particle-only climax: `SH008-SH010` require body crossing, wound, and witness reaction.
- No character/model drift: if `C01` or `C02` changes face/hair/wardrobe, the clip is rejected even if the action is beautiful.
- No short-drama dead end: `SH010-SH012` preserve memory and object hooks for EP02.

## Open items before execution

1. User approval of this original story mechanism or replacement with a complete script.
2. Authorized identity reference images or a decision to create them first.
3. Provider choice per shot: Seedance primary, Kling primary, HappyHorse fallback, or mixed.
4. Exact aspect/resolution/duration limits from current official/provider docs.
5. Credentials, credits, output directory, and explicit operation authorization.
6. Audio rights and whether “第二局” is voice, subtitle, or both.
