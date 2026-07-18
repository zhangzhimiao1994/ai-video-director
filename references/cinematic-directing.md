# AI Video Director：通用电影化模式

本参考是现有十对象制作包上的可选导演层。它不创建第十一个顶层对象，不调用 API，也不改变三个批准门。

## Activation

适用于 30–90 秒电影级片段或预告。启用后，在 `project_brief.cinematic_mode` 中显式记录输入模式、节奏预设、双画幅和视觉预设。

## Input modes

- `concept_mode`：用户提供一句故事、主题、人物或冲突；先补全可审计因果，再进入三个创意方向。
- `screenplay_mode`：用户提供完整或部分剧本；保留核心事实、人物动机和因果，压缩为目标时长。
- `novel_mode_reserved`：仅为未来扩展保留。首版遇到长篇小说时说明边界，请用户选择一个自包含片段或提供剧本，不宣称已经完成章节拆解。

## Hard gates

- `narrative_clarity`：必须明确主角、目标、阻碍、因果和结尾变化。
- `continuity_integrity`：不得存在未解决的角色 ID、服装、道具、人物状态、空间方向或镜头依赖冲突。

任一硬门失败时，`quality_report.ready` 必须为 `false`。镜头震撼度是建议项，不得覆盖硬门。

## Rhythm presets

- `A narrative-first cinematic`：默认。远景建立尺度，近景、双人、反应和插入镜头讲清关系，只保留 1–2 个英雄镜头。
- `B spectacle-heavy`：增加大全景、动态构图、复杂特效和运镜；参考资产不足时降级为 A。
- `C performance-first`：增加近景、特写、双人覆盖、停顿和微表情，减少复杂场景切换。

切换 A/B/C 不得改变剧情事实、角色 ID、事件顺序或结局。

## Shot design

30–90 秒通常使用 7–12 个 active 镜头，但以因果和可生成性为准。每镜只保留一个主要动作、一个主要运镜、一个情绪转折和一个视觉关注点。镜头必须声明叙事功能、边界状态、状态依赖和平台能力需求。

`style_preset` 是可切换数据，不是暗黑西幻硬编码。它可以表达东方玄幻、科幻、末世、写实或用户定义视觉规则，但不能改变已锁定剧情事实。

## Dual aspect

- 16:9 是电影母版，使用横向调度、前中后景和环境尺度。
- 9:16 是独立重构，重新安排人物、视线、字幕安全区和纵向景深。
- 无法安全重构时使用 `independent_generation`，不得伪装成机械裁切。

两种画幅共享同一故事、Canon 事实和状态，只改变构图、调度与平台编译。

## Prompt order

电影化提示词保持三层语义：`global_lock_block`、`shot_direction_block`、`platform_compile_block`。平台层只做格式和已核实能力映射，不得新增剧情事实。

## key_shot_review

只对世界建立、剧情反转、英雄镜头、双画幅困难镜头或重复连续性失败镜头启用额外评审。编剧、导演、摄影和连续性监督只能给出局部修改，不得重写已锁定故事。普通镜头不运行反复评审。

## local_repair

- 剧情不清时返回 Beat Map，不靠新增旁白掩盖。
- 连续性失败时冻结剧情和无关镜头，只修复问题镜头及其依赖。
- 关键资产不足时先交付角色、服装、道具和场景参考图提示词。
- 平台能力不足时按 `reference_video → multi_reference_images → first_last_frames → first_frame → text_only → manual_job` 降级，并说明一致性影响。
- API 执行不在 Skill 范围内；任务失败处理只能写入交接建议。

## Logical delivery

默认以 Markdown 分节交付导演摘要、剧本、Canon 与资产圣经、Shot Graph、关键帧提示词、平台提示词包、双画幅方案和质检报告。只有用户明确要求保存文件时，才把这些逻辑部分写成目录。
