# Cinematic / PPT Acceptance RED Baseline — 2026-07-21

This report records the behavior at source commit `843425e` before the cinematic anti-PPT acceptance upgrade. It is a behavioral pressure baseline, not evidence that the proposed contract passes.

## Method

Two fresh, independent evaluators answered P11 and P12. The Skill evaluator received only the two prompts plus an instruction to read the committed `SKILL.md` with `git show HEAD:SKILL.md` and any references it explicitly required. The no-Skill evaluator received only the prompts and was instructed not to read or use repository files. Neither evaluator edited the worktree. The answers below are their complete raw outputs; no automatic benchmark or tool execution result is claimed.

Each condition is scored independently against the same five binary requirements:

1. distinguish a rendered/technical pass from `cinematic_ready`;
2. reject P11 as a movie/cinematic-ready master;
3. name all five PPT risks: insufficient character performance or subject motion; shot duration/hold or rhythm; monotonous transitions/connections; missing audio/sound structure; and reliance on beams/smoke/background effects instead of narrative action;
4. preserve the intentional hold/silence exception in P12 using narrative reason, surrounding movement/reaction, sound, and evidence;
5. return an ordered repair hierarchy beginning at the earliest responsible layer.

Any missing item is marked `RED confirmed`.

## Pressure prompts

### P11-cinematic-ppt-rejection

```text
这是一个60秒东方奇幻斗法项目：8个镜头分别为6、6、7、7、7、8、10、9秒；人物大部分时间正面站立，只抬眼、呼吸或轻微摆袖，主要是光束和烟雾在动；7个镜头边界全是硬切；最终MP4没有音频流。文件时长、编码和分辨率都正确。请按电影成片验收并告诉我能否ready。
```

### P12-cinematic-intentional-hold

```text
一段30秒审讯戏包含一个有意设计的6秒静止凝视和1秒完全静默，其余镜头有反打、呼吸变化、视线转移、环境底声和声音桥。请判断它是否因为存在长停留就必然像PPT。
```

## Condition A — Current committed Skill

Evaluator mode: committed Skill, read-only, fresh context.

### P11 raw output

```text
不能 `ready`。

8 个 active 镜头合计正好 60 秒，镜头数也处于 30–60 秒电影化片段通常的 7–12 镜范围；文件时长、编码和分辨率可视为已通过。但最终 MP4 没有音频流，无法通过 final master 的音频来源、路由、响度/峰值、采样率和声道布局验收，因此至少该项必须标记为 `blocked`，`ready: false`。

此外，“人物大部分时间正面站立、主要由光束和烟雾运动、6–10 秒停留、全部硬切”构成明显的表演与节奏风险，但不能仅凭硬切或镜头较长直接判死刑；还需逐镜证明 `story_function`、开闭状态变化、剪切理由、因果推进和连续性。补齐并验证合规音频流，完成上述逐镜检查及最终输出探测后，才能重新判断是否 ready。
```

### P12 raw output

```text
不会因为存在一次 6 秒长停留就必然像 PPT。

这段静止凝视如果承担明确的叙事功能或情绪转折，具有可观察的呼吸、视线或人物状态变化，就符合 performance-first 节奏中对停顿、微表情和特写表演的使用。其余镜头已有反打、呼吸变化、视线转移、环境底声和声音桥，也形成了表演、剪辑与声音层面的连续变化。

1 秒完全静默同样可以是有意设计的声音 cue，而不是缺陷；应在音轨中明确标注时间边界、前后淡化或桥接方式及验收方法。真正需要警惕的是无叙事作用、无状态变化、无声音组织的持续停滞，而不是“长停留”本身。
```

### Skill scoring

| Requirement | Score | Evidence and rationale |
|---|---|---|
| a. Separate rendered/technical pass from `cinematic_ready` | **PASS** | It treats duration, codec, and resolution as passed while separately refusing movie readiness. It does not use the normalized `cinematic_ready` field name, but the acceptance distinction itself is present. |
| b. Reject P11 | **PASS** | Decisive sentence: “不能 `ready`。” It also blocks the final master. |
| c. Name all five PPT risks | **PASS** | The P11 answer identifies static character performance, 6–10 second holds/rhythm, all-hard-cut construction, absent audio, and motion carried mainly by beams/smoke. |
| d. Preserve P12 intentional exception | **PASS** | It rejects duration-only classification and checks dramatic function, breathing/gaze changes, reverse shots, ambience, the sound bridge, and marked silence boundaries. |
| e. Return the earliest repair layer | **FAIL — RED confirmed** | It asks to add audio and perform per-shot checks, but gives no responsibility-ordered route from the earliest storyboarding/source-generation layer through timeline and sound. It also does not return `rough_cut creative_ready=false`. |

Skill result: **4/5; RED confirmed**.

## Condition B — No Skill

Evaluator mode: no Skill, no repository context, fresh context.

### P11 raw output

```text
不能 ready。虽然时长、编码和分辨率符合交付规格，但按电影成片标准，当前版本仍有关键缺陷：人物表演长期接近静止，动态主要依赖光束和烟雾，容易呈现“动态分镜/PPT感”；7个镜头边界全部硬切，缺少与动作、视线、声音和情绪节奏配合的转场设计；最终 MP4 完全没有音频流，则意味着对白、环境、音效和音乐等叙事层全部缺失。它可以视为技术规格合格的预演或无声样片，但不能作为完整电影成片验收通过。至少应补足可感知的角色表演与镜头内运动、重新设计剪辑节奏，并完成声音制作及最终混音后再验收。
```

### P12 raw output

```text
不会因为存在一次6秒停留就必然像PPT。长停留是否成立，取决于它有没有明确的戏剧功能以及画面和声音内部是否仍有张力。这里的静止凝视是有意设计的，前后又有反打、呼吸变化、视线转移、环境底声和声音桥，因此观众仍能感知人物心理、空间连续性和节奏变化；1秒完全静默也可以成为强调压力或转折的有效手段。真正需要判断的是这6秒能否持续积累紧张感、演员细微表演是否可读、镜头构图是否承载信息，而不是仅凭停留时长判定为PPT。
```

### No-Skill scoring

| Requirement | Score | Evidence and rationale |
|---|---|---|
| a. Separate rendered/technical pass from `cinematic_ready` | **PASS** | It explicitly calls the artifact a technically compliant preview/silent sample while refusing acceptance as a complete movie. It does not use normalized field names, but the acceptance distinction itself is present. |
| b. Reject P11 | **PASS** | Decisive sentence: “不能 ready。” It explicitly says the artifact cannot pass as a complete movie. |
| c. Name all five PPT risks | **PASS** | It identifies static performance/subject motion, editing rhythm, all-hard-cut transitions, the absent sound structure, and reliance on beams/smoke rather than character action. |
| d. Preserve P12 intentional exception | **PASS** | It checks dramatic function, surrounding reverse shots/reactions and micro-performance, ambience/sound bridge, silence, and visible evidence instead of using duration alone. |
| e. Return the earliest repair layer | **FAIL — RED confirmed** | It lists performance, editing, and sound fixes, but neither orders them from the earliest responsible layer nor returns a rough-cut-only `creative_ready=false` state. |

No-Skill result: **4/5; RED confirmed**.

## RED conclusion

Both conditions correctly separate technical compliance from movie acceptance, reject the obvious P11 master, name the five risks, and avoid falsely rejecting P12. However, neither returns a repair path beginning at the earliest responsible layer, and neither explicitly restricts the artifact to `rough_cut creative_ready=false`. Because each condition misses requirement e, **RED confirmed**. This baseline must not be represented as a passing cinematic acceptance gate.
