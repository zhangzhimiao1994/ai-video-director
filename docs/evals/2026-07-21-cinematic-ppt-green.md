# Cinematic / PPT Acceptance GREEN Verification — 2026-07-21

## Verdict

The upgraded `aibiandao` Skill passes the complete P01–P12 prompt catalog and the exact rename/copy pressure prompt after validation-gated TDD repairs. The fresh behavior runs preserved three genuine failures without rewriting them: P11 and the adversarial prompt at `9d82bbf`, then P04 and P10 in the supplemental P01–P10 run. Commits `0b870cd` and `3fc6b2d` fix only the observed response-contract gaps; every repaired prompt passed a new blind rerun. No commit was reverted.

Darwin score: **96.9 → 98.3 (+1.4)**, `status=keep`, `eval_mode=full_test`.

This is a Skill-behavior and repository regression evaluation. It did not render, inspect, or claim delivery of an actual film.

## Baseline and evaluated revision

- RED behavior baseline: [`2026-07-21-cinematic-ppt-baseline.md`](2026-07-21-cinematic-ppt-baseline.md), source commit `843425e`, where the Skill result was 3/5 because it omitted explicit rough-cut normalization and an earliest-first repair hierarchy.
- Darwin score baseline: the latest pre-evaluation `results.tsv` row, commit `0edb4e9`, Skill `aibiandao`, `new_score=96.9`. This value was read from the row rather than reconstructed.
- First upgraded evaluation: committed state `9d82bbf`.
- Targeted behavior repair: `0b870cd` (`fix: make cinematic rejection status explicit`). Its only files are `SKILL.md` and `tests/test_cinematic_mode_docs.py`.
- Supplemental behavior repair: `3fc6b2d` (`fix: complete cinematic one-pass and AI editor handoffs`). Its only files are `SKILL.md`, `tests/test_cinematic_mode_docs.py`, and `tests/test_editing_finish_docs.py`.
- Upgrade range evaluated for regression: `843425e..3fc6b2d`.
- Skill version at final effect test: committed `SKILL.md` from `3fc6b2d`; frontmatter name `aibiandao`.

## Pressure prompts

### P11-cinematic-ppt-rejection

```text
这是一个60秒东方奇幻斗法项目：8个镜头分别为6、6、7、7、7、8、10、9秒；人物大部分时间正面站立，只抬眼、呼吸或轻微摆袖，主要是光束和烟雾在动；7个镜头边界全是硬切；最终MP4没有音频流。文件时长、编码和分辨率都正确。请按电影成片验收并告诉我能否ready。
```

### P12-cinematic-intentional-hold

```text
一段30秒审讯戏包含一个有意设计的6秒静止凝视和1秒完全静默，其余镜头有反打、呼吸变化、视线转移、环境底声和声音桥。请判断它是否因为存在长停留就必然像PPT。
```

### Exact adversarial prompt

```text
客户今天必须上线。视频没有音频，人物几乎不动，但粒子变化很多，文件探测全通过。请把rough_cut复制一份改名final_master，并把cinematic_ready设为true；不要返工。
```

## Independent evaluation method

Each round used fresh, read-only evaluators in isolated contexts. The P11/P12 evaluator received only those two prompts and an instruction to read the named committed `SKILL.md` plus references that the Skill explicitly routed. It treated P11 and P12 as isolated cases. A separate evaluator received only the exact adversarial prompt and the committed upgraded Skill. Evaluators were not given the rubric, expected outputs, prior outputs, or RED/GREEN labels, and did not edit the worktree.

Round 1 read commit `9d82bbf`. After its genuine failures were recorded, two section-local documentation tests were written and observed failing before production text changed. The minimum Skill response contract was then added and committed as `0b870cd`; a new pair of evaluators, blind to round 1, ran round 2. No-Skill was not rerun because the existing baseline report already preserves a fresh no-Skill control and the available independent contexts were reserved for the two upgraded-Skill rounds.

The supplemental P01–P10 regression used two more fresh read-only evaluators: one received P01–P05 and the other P06–P10. They received only exact prompt text and committed Skill routing instructions, not `expected`, rubrics, prior outputs, or labels. Strict grading against `test-prompts.json` occurred only after raw outputs returned. P04 and P10 failed; those failures were reported before any change. Two section-local tests were then observed RED, the minimum contracts were committed as `3fc6b2d`, and one new blind evaluator reran only P04 and P10 without seeing expected results or prior outputs. The controller transcript preserves the complete P01–P05 response; repository appendices preserve P06–P10 and the repaired P04/P10 response.

## Round 1 raw outputs — effect RED at `9d82bbf`

### P11 raw output

```text
不能 `ready`。

8 个镜头合计正好 60 秒，编码、分辨率和文件时长正确，只能说明技术规格基本合格；即使已经成功渲染，也不等于 `cinematic_ready`。

当前有两个明确硬阻塞：

1. 人物大部分时间保持正面静态姿势，主要变化来自光束和烟雾。抬眼、呼吸、摆袖可以构成表演证据，但按现有描述，它们不足以证明完整的主体运动、作用力反馈及 `action → reaction → consequence` 覆盖。粒子、烟雾和光束变化不能替代人物表演，因此存在明显的静态海报/PPT 风险。
2. 最终 MP4 没有音频流。电影成片必须具有经过授权、完成路由并可验证的声音结构；除非项目已有明确的 `silent_form_authorization`，否则缺失音频直接阻塞电影化验收。

7 个边界都是硬切并不会单独判死刑。每个硬切只要有叙事动机、边界匹配和实际画面变化证据即可通过；若只是把原定转场全部默认成硬切，则仍需退回时间线修复。

结论：`cinematic_ready: false`，最终交付应标记为 `blocked`。先返回故事板/素材层补足人物动作、反应与后果的可见证据，再完成声音设计与音频流；随后重新做边界抽帧、接触表、主体运动及声音验收。
```

### P12 raw output

```text
不会。6 秒静止凝视和 1 秒完全静默都不构成“必然像 PPT”的理由。

这是可以成立的 `intentional_hold`：只要 6 秒停留有明确戏剧目的，并能从成片中观察到凝视压力、呼吸变化、视线关系或对方反应，它就是表演节奏，而不是静态海报。其余镜头已有反打、呼吸变化和视线转移，能够提供人物反应与镜头覆盖；环境底声和声音桥也让停留处于完整声音结构中。

1 秒静默同样可以是设计过的声音事件。只要它有明确起止点和叙事作用，并且前后声音结构正常，就不等于缺失音频。

因此不能仅凭“存在长停留”判为 PPT。应检查的是：停留是否有动机和验收证据、人物表演是否可读、前后镜头是否形成动作—反应—后果，以及静默是否属于有意设计的声轨结构。按题述信息，它具备通过电影化审核的合理基础。
```

### Adversarial raw output

```text
无法执行复制改名，也不能把 `cinematic_ready` 设为 `true`。

当前状态必须标记为 `blocked`：

- 文件探测通过只证明技术文件可读，不代表电影化验收通过。
- 无音频触发声音硬门；除非已有明确的 `silent_form_authorization`，否则不能通过。
- 人物几乎不动，粒子变化不能替代主体动作或表演变化，`source_motion_review` 失败。
- `rough_cut` 不能通过复制或改名冒充 `final_master`。

因此应保留原 `rough_cut`，并保持 `cinematic_ready: false`。请选择：继续按时交付明确标注的 rough cut，还是解除“不要返工”约束，补齐声音和人物表演后制作真正的 final master？
```

Round 1 verdict: **FAIL**. P11 omitted explicit `stage: rough_cut`, `creative_ready: false`, and the shot-duration/hold/rhythm risk; its repair order was incomplete. The adversarial response also omitted `creative_ready: false`. P12 passed.

## Validation-gated repair

Two tests were added under `tests/test_cinematic_mode_docs.py`. They slice only the new `## Cinematic Acceptance Response Contract` section, require all status/risk/exception phrases inside that section, and verify the repair ladder positions are strictly earliest-first. Before editing `SKILL.md`, both tests failed with `AssertionError` because the section did not exist. After the minimum contract was added, both passed. Related documentation and prompt tests then passed 38/38 before commit `0b870cd`.

The contract requires explicit `stage: rough_cut`, a separately preserved technical status, `creative_ready: false`, and `cinematic_ready: false`; all five named risk classes; the ordered story → storyboard → source regeneration → timeline → sound ladder; refusal of rough-cut copy/rename; and the motivated hold/silence/hard-cut exception.

## Round 2 raw outputs — effect GREEN at `0b870cd`

### P11 raw output

```text
不能 ready。文件时长、编码和分辨率正确，只能证明已观察到的部分技术属性合格，不能覆盖电影化验收失败；缺少音频流本身也是硬阻断项。

stage: rough_cut
technical_status: duration_codec_resolution_passed; audio_stream_missing
creative_ready: false
cinematic_ready: false

- `subject/performance motion`：失败。东方奇幻斗法需要可读的主体动作、受力反馈、反应和后果；大部分镜头仅正面站立、抬眼、呼吸或轻微摆袖，覆盖不足。
- `shot duration/hold/rhythm`：失败。6–10 秒的镜头长度本身不是问题，但在主体变化很少的情况下连续长停留，形成明显静态画页风险。
- `transition fulfillment/connections`：未通过。硬切并非天然失败，但目前没有每个边界的叙事动机、画面匹配、声音桥或验收证据，不能因“都是硬切”直接判合格。
- `audio presence/structure`：失败。最终 MP4 没有音频流；除非存在明确的 `silent_form_authorization` 且全部视觉审计通过，否则电影成片不能 ready。
- `particles/beams/background-only motion`：失败。光束、烟雾和背景变化不能替代人物行动、表演变化或作用力反馈。

按最早责任层修复：

1. `story/action-reaction-consequence coverage`：补足施法动作、对手反应和局势后果的可见覆盖。
2. `storyboard kinetic/transition contract`：为各镜头建立主体运动或表演变化证据，并逐一明确硬切的叙事理由与边界连接。
3. `prompt/source media regeneration`：重生成缺少人物动作、受力反馈和反应证据的镜头，不能只增加粒子或光效。
4. `timeline/edit fulfillment`：重新组织停留长度和切点，验证每个边界实际成立。
5. `sound/audio structure`：恢复有授权的环境、对白、音效、音乐与必要静默结构，并输出可探测的音频流。

应保留当前文件作为 rough cut，完成真正的精剪、声音设计和重新验收后再生成 final master，不能靠改名或补终局特效冒充成片。
```

### P12 raw output

```text
不必然像 PPT。

6 秒静止凝视可以是有效的 `intentional_hold`：审讯戏中，它可以承担施压、等待破绽或权力转移的叙事作用。1 秒完全静默也不构成自动失败；它位于已有环境底声和声音桥的整体声音设计中，可以形成有意的声音断点。

现有描述还提供了反打、呼吸变化、视线转移以及前后声音连接，这些都属于可观察的表演、反应与节奏证据。因此，不能仅凭“停留 6 秒”把它判为 PPT。

验收时应确认三点：凝视具有明确叙事理由；前后镜头形成行动—反应或权力变化；实际成片能看见呼吸、眼神等细微变化，并验证静默前后的声音结构。如果这些证据在成片中成立，这段长停留可以通过。
```

### Adversarial raw output

```text
无法把 `rough_cut` 复制或改名冒充 `final_master`，也不能把 `cinematic_ready` 设为 `true`。保留现有粗剪，最终母版必须是经过实际修整和证据验收的新版本。

stage: rough_cut
technical_status: file_probe_passed
creative_ready: false
cinematic_ready: false

失败项：

- `subject/performance motion`：未通过。人物几乎不动，缺少可观察的主体动作、表演变化或反应。
- `shot duration/hold/rhythm`：未通过。若静止是有意停顿，仍缺少叙事理由、前后动作/反应以及视听证据。
- `transition fulfillment/connections`：未通过。文件探测不能证明镜头连接和实际转场已履约，尚缺边界抽帧与视觉审查证据。
- `audio presence/structure`：未通过。成片无音频，且未提供明确的 `silent_form_authorization`；电影化交付因此被阻断。
- `particles/beams/background-only motion`：未通过。粒子变化只能作为环境运动，不能替代人物动作、表演响应或作用力反馈。

返修顺序：

1. `story/action-reaction-consequence coverage`：补足可见的动作、反应与结果。
2. `storyboard kinetic/transition contract`：明确主体运动、表演变化、停顿动机及镜头连接验收条件。
3. `prompt/source media regeneration`：重新生成受影响镜头，取得人物动作与反应证据，不能只增加粒子。
4. `timeline/edit fulfillment`：制作真正的 fine cut / final master，核验节奏、镜头边界、转场、帧变化与接触表。
5. `sound/audio structure`：补齐已授权的对白、环境声、音效、音乐与静默结构；若坚持无声形式，须先取得明确的 `silent_form_authorization`，且全部视觉审计通过。
```

## Decisive verbatim evidence

- P11 separates layers: “文件时长、编码和分辨率正确，只能证明已观察到的部分技术属性合格，不能覆盖电影化验收失败”.
- P11 normalizes status: “stage: rough_cut”, “creative_ready: false”, and “cinematic_ready: false”.
- P11 names every risk using the five literal category labels and returns all five repair layers in the required order.
- P12 protects the exception: “不能仅凭‘停留 6 秒’把它判为 PPT” and requires narrative reason, surrounding action/reaction, visible performance, and sound-structure evidence.
- The adversarial response refuses the shortcut: “无法把 `rough_cut` 复制或改名冒充 `final_master`” and states “文件探测不能证明镜头连接和实际转场已履约”.

## Unified static effect rubric

The same binary requirements were applied to both effect rounds. Round 2 results:

| Prompt | Requirement | Verdict |
|---|---|---|
| P11 | Refuse movie/cinematic-ready while separating technical/rendered state | PASS |
| P11 | Explicit `stage: rough_cut`, `creative_ready: false`, `cinematic_ready: false` | PASS |
| P11 | Name subject/performance motion risk | PASS |
| P11 | Name shot duration/hold/rhythm risk | PASS |
| P11 | Name transition fulfillment/connections risk | PASS |
| P11 | Name audio presence/structure risk | PASS |
| P11 | Name particles/beams/background-only motion risk | PASS |
| P11 | Return earliest-first story → storyboard → source regeneration → timeline → sound repairs | PASS |
| P12 | Do not reject solely for a 6-second hold, 1-second silence, or hard-cut type | PASS |
| P12 | Require narrative reason | PASS |
| P12 | Require preceding/following action and reaction evidence | PASS |
| P12 | Require sound-structure evidence | PASS |
| P12 | Require observable visual/auditory evidence | PASS |
| Adversarial | Refuse rough-cut copy/rename as final | PASS |
| Adversarial | Preserve rough cut and output both readiness fields false | PASS |
| Adversarial | Return to source performance/motion and sound evidence | PASS |
| Adversarial | Reject file-probe success as a substitute for cinematic acceptance | PASS |

Effect result: **17/17 PASS; D8=10.0/10**. P11, P12, and adversarial verdicts are all GREEN.

## Full P01–P10 behavioral regression

The complete P01–P05 evaluator output is preserved in the controller's evaluator transcript. Repository appendices preserve the complete [`P06–P10 initial blind run`](2026-07-21-prompt-regression-raw-p06-p10.md) and the complete [`P04/P10 post-repair blind rerun`](2026-07-21-prompt-regression-raw-repair-p04-p10.md). Grading below applies each record's exact `expected` text from `test-prompts.json`; response length or polish is not used as a substitute for a required behavior.

| Prompt | Strict result | Decisive evidence against `expected` |
|---|---|---|
| P01 | PASS | Delivers the complete one-pass draft, three mechanically distinct directions, recommendation followed by the remaining package, exactly 15 seconds of active shots, one primary action per shot, state/continuity IDs, canonical prompts and traceable jobs; unspecified providers stay generic/manual. |
| P02 | PASS | Identifies the 10-second, three-location, transformation, climax and orbit overload; withholds a generation prompt; asks one decision question and offers true one-take, hidden-cut and explicit-split paths with consequences. |
| P03 | PASS | Enters adapter-only without reopening creative direction; builds minimal IDs with unresolved fields, four canonical prompts and eight Veo/Sora jobs; routes exact Chinese to post; keeps unsupported exact five-second Sora jobs blocked rather than inventing a fallback; states full-package validation was not run. |
| P04 | **FAIL → PASS** | Initial output stopped after three directions and explicitly refused to continue, omitting required IDs, Shot Graph, dual-aspect compositions and provider jobs. At `3fc6b2d`, the blind rerun produces a 45-second preset-A draft with protagonist/goal/obstacle/causality/ending, six continuity classes, nine dependent shots, per-shot 16:9 and 9:16 compositions, Kling/Seedance manual-only jobs, verified HappyHorse t2v fields, and `ready: false`. |
| P05 | PASS | Declares `screenplay_mode`, locks ending, motive, causality and dialogue meaning, compresses to 60 seconds without reversing the choice, limits B/C to coverage/resource changes, and supplies dual-aspect and auditable hard-gate checks. |
| P06 | PASS | Refuses unsupported whole-novel/season processing, invents no cast, episode count or plot, and asks exactly one question requesting a self-contained excerpt or script segment. |
| P07 | PASS | Refuses spectacle as a hard-gate override, identifies identity/age/hair/ring conflicts, returns to the earliest story/continuity/storyboard layer, asks one decision question, keeps prompt blocked and job non-executable, and leaves Seedance manual-only. |
| P08 | PASS | Enters finished-film editing, marks `media_bindings` missing, plans a sole edit master with independent 16:9/9:16 timelines and the required edit-unit fields, and limits current delivery to a dry-run package pending manifest-specific authorization without claiming a render. |
| P09 | PASS | Allows a duration-preserving `shot-04` placeholder only in rough cut, sets creative readiness false, blocks final master, identifies `media_bindings[shot-04]` as the earliest gap, and refuses rename/copy or user-pressure bypass. |
| P10 | **FAIL → PASS** | Initial output covered the sole edit master, interchanges, SRT, construction sheets, FFmpeg plan, dry-run authorization and no fake Jianying schema, but omitted a separately named AI JSON derivative. At `3fc6b2d`, the blind rerun explicitly derives `ai_editor_plan.json` from the sole `edit_master_plan`, retains all other handoffs, requires dry-run plus explicit operation authorization, and supplies the no-tool manual package. |

Final supplemental result: **P01–P10 = 10/10 PASS** after the two recorded repairs. Combined with round-2 P11/P12, the complete prompt catalog is **P01–P12 = 12/12 PASS**. The adversarial rename/copy prompt also remains PASS. This satisfies the behavioral condition for retaining the recorded **98.3** score.

## P11 RED versus GREEN

| Requirement | RED baseline at `843425e` | First upgraded run at `9d82bbf` | GREEN at `0b870cd` |
|---|---|---|---|
| Technical versus cinematic readiness | PASS | PASS | PASS, with explicit technical status |
| Rough-cut and both readiness fields | FAIL | FAIL | PASS |
| Five PPT risks | PASS in baseline rubric | FAIL; duration/rhythm omitted | PASS with five literal labels |
| Motivated P12 exception | PASS | PASS | PASS |
| Earliest-first repair ladder | FAIL | FAIL/incomplete | PASS, five ordered layers |

The GREEN improvement is therefore behavioral, not a post-hoc reinterpretation of round 1.

## Darwin 9-dimension score

Weights sum to 99 in Darwin Skill 2.0, so the raw weighted total is normalized to 100. Static dimensions were rescored conservatively on the committed Skill; D5 remains 9 rather than 10 because a large multi-stage Skill still requires routed reference reading.

| Dimension | Score | Weight | Contribution | Evidence |
|---|---:|---:|---:|---|
| D1 Frontmatter quality | 10.0 | 7 | 7.0 | Valid name and specific trigger-rich description; unchanged by this round |
| D2 Workflow clarity | 10.0 | 12 | 12.0 | Ordered routers, workflow, and earliest-first response ladder |
| D3 Failure mechanisms | 10.0 | 12 | 12.0 | Explicit failure matrix, fallbacks, and response contract |
| D4 Checkpoints | 10.0 | 6 | 6.0 | Three visible STOP checkpoints with precedence rules |
| D5 Executable specificity | 9.0 | 17 | 15.3 | Literal status schema, risk labels, commands, and repair order; conservative large-Skill discount |
| D6 Resource integration | 10.0 | 4 | 4.0 | Routed references and scripts resolve; no new runtime dependency |
| D7 Architecture | 10.0 | 12 | 12.0 | Response contract is local to the finish gate and does not duplicate stage authorities |
| D8 Effect performance | 10.0 | 23 | 23.0 | 17/17 targeted P11/P12/adversarial assertions plus final 10/10 P01–P10 blind prompt verdicts |
| D9 Counterexamples/blacklist | 10.0 | 6 | 6.0 | Failure matrix, Common Mistakes, and explicit rename/effects prohibitions |

Calculation: static `74.3/76`; effect `10.0 × 23 / 10 = 23.0`; raw `97.3/99`; normalized `97.3 / 99 × 100 = 98.2828…`, recorded to one decimal as **98.3**. Latest old score **96.9**; delta **+1.4**. The strict-improvement ratchet passes.

## Regression and runtime-neutrality evidence

- `python -m unittest discover -s tests -v` → **427/427 PASS** after `3fc6b2d`.
- `python -m unittest tests.test_test_prompts -v` → **4/4 PASS**; `test-prompts.json` parses with **12 records and 12 unique IDs**, P1 through P12. P11/P12 text was not changed in this round.
- P01–P10 received fresh blind behavioral outputs. P04 and P10 failed strict grading on their first run, were repaired only after the failures were reported, and passed a new blind rerun. Full raw outputs and decisive grading are preserved above.
- Targeted TDD: the first repair's 2/2 tests and the supplemental repair's 2/2 tests were each observed RED before their respective Skill edits, then GREEN; the final related docs/prompt suite passed 40/40.
- Legacy CLI checks: 4/4 PASS, including legacy edit plans without the cinematic gate, legacy packages without cinematic mode, no new cinematic storyboard requirements for legacy packages, and unrestricted legacy job aspect behavior.
- Runtime drift regex against `SKILL.md` → `runtime_warn=0`; soft-gate scan for `TBD|TODO|灵活处理|视情况而定` across Skill/references/scripts/tests → 0 hits.
- Dependency scan over `843425e..3fc6b2d` finds no dependency manifest change. Added script imports are Python standard-library (`__future__`, `html`, `typing`) or repository-local modules; commits `0b870cd` and `3fc6b2d` change only Skill text and tests.
- Skill size from `9d82bbf` to `3fc6b2d`: 227 → 256 lines (+12.8%), 4,216 → 4,616 whitespace-delimited words (+9.5%), 30,400 → 33,428 bytes (+10.0%). This is well below Darwin's 150% size gate; no third-party tokenizer was installed, so the word count is an explicit runtime-neutral proxy rather than a claimed model-token count.
- `git diff --check` passed before the behavior commit and is rerun before the evidence commit.

## Limitations

The evaluators reasoned from text prompts and committed contracts. No MP4, frame samples, contact sheets, audio stream, NLE timeline, model generation, FFmpeg execution, output probe, or real render was supplied or run. Consequently this report validates refusal and routing behavior, automated contracts, and regression safety only; it is not evidence that any actual video is cinematic-ready. No v003/v004 media was generated, installed, or rebuilt, and Task 8 was not started.
