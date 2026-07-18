# Model Adapters

- Verified: 2026-07-18
- Rule: preserve the approved story and storyboard; adapt only prompt formatting, supported references, clip duration, resolution, aspect ratio, audio fields, and documented request parameters.

本参考只负责把唯一 canonical prompt 与获批镜头映射成 provider job。它不是能力宣传页，也不授权调用 API。每次实际执行前都应重新打开相同官方入口，因为模型、字段、枚举值、区域和发布阶段会变化。

## 全局安全规则

1. `screenplay`、`continuity_bible`、`storyboard` 和 `shot_id` 在切换模型时保持不变。
2. 每个 job 的 `prompt_source` 指向该镜唯一的 `universal_prompt_en`；不得在 job 中另写剧情版提示词。
3. `documented_parameters` 只放所选 provider 当前官方一手文档明确出现的请求字段。路由字段、项目 ID、鉴权、文件路径和未核实能力不得伪装成已核实请求参数。
4. `requires_manual_configuration` 始终是数组。任何未核实或依赖账户、区域、模型版本、输入资产的项都进入该数组。
5. adapter-only 输入若只有已锁定镜头的自然语言，不得用“同一人物/同一道具”代替连续性引用。仅为用户明确出现的实体建立最小不透明 ID 索引，未给出的外观与资产保持 `unresolved`；每个 job 通过 `reference_inputs` 或手动配置审计携带相关 ID，不得借此补写故事事实。
5. provider 不支持镜头时长、参考输入、首尾帧、画幅、音频或分辨率时，不得静默改故事或镜头。返回分镜阶段选择已批准 fallback、拆分方案或请求用户决定。
6. `model_variants` 只做格式和已支持能力映射，不增删人物、地点、道具、动作、台词、产品主张或结局。
7. 精确品牌字、数字、字幕和法律文字默认后期合成；除非官方文档与项目测试均证明可靠，否则不设为生成验收条件。
8. 官方页面不可访问、返回空壳、重定向到非等价产品或字段含义冲突时，能力写入 `unsupported_or_unverified`，不使用博客、聚合站、社区 SDK 或记忆补齐。

## Adapter 记录字段

每个 provider 记录都必须保留以下字段，即使值为空或未知：

- `official_docs`
- `verified_at`
- `verified_models`
- `supported_generation_modes`
- `prompt_language`
- `reference_inputs`
- `first_last_frame_support`
- `audio_support`
- `documented_durations`
- `documented_aspect_ratios_or_sizes`
- `documented_parameters`
- `async_job_model`
- `result_expiry`
- `unsupported_or_unverified`
- `requires_manual_configuration`
- `adaptation_notes`

电影化模式还要记录异步与留存语义：

- `async_job_model`：同步、创建后轮询或未核实。
- `result_expiry`：官方明确的结果有效期；未明确时记为 `unsupported_or_unverified`。

这两个字段只描述任务交接，不授权 Skill 提交、轮询或下载任务。

## Sora / OpenAI Videos API

**official_docs**

- https://platform.openai.com/docs/api-reference/videos
- https://developers.openai.com/api/reference/resources/videos/methods/create

**verified_at**：2026-07-18

**verified_models**

- `sora-2`
- `sora-2-pro`
- 官方 schema 还列出带日期的版本字符串；除非项目明确要求固定版本，不自动替换默认别名。

**supported_generation_modes**

- `POST /videos`：从文本 prompt 创建视频，可带一个可选 `input_reference`。
- 官方 Videos API 索引还列出 edit、extension 与 remix 端点；只有 job purpose 明确对应这些操作并再次读取其专用 schema 时才使用。

**prompt_language**

- create schema 只把 `prompt` 定义为字符串，未声明支持语言清单。canonical 英文提示词可以直接提交，但语言能力仍视为 `unsupported_or_unverified`，不推断多语言等价性。

**reference_inputs**

- `input_reference` 是可选对象；必须且只能提供 `image_url` 或 `file_id` 之一。
- create schema 未记录多个同时输入的 reference，因此多参考图不得拼成未文档化字段。

**first_last_frame_support**

- `POST /videos` create schema 未提供独立 first-frame 与 last-frame 字段。`input_reference` 只能记录为通用引导图，不能宣称是首帧或尾帧约束。

**audio_support**

- create 请求 schema 未列出音频输入、音频开关、对白或口型字段。所有声音与 lip-sync 保持为后期指导，除非另一个当前官方端点明确支持且经过单独适配。

**documented_durations**

- `seconds`: `"4"`、`"8"`、`"12"`。

**documented_aspect_ratios_or_sizes**

- `size`: `"720x1280"`、`"1280x720"`、`"1024x1792"`、`"1792x1024"`。
- create 请求没有独立 `aspect_ratio` 字段；只能通过受支持的 `size` 选择方向与尺寸。

**documented_parameters**

- `prompt`
- `input_reference`
- `model`
- `seconds`
- `size`

**unsupported_or_unverified**

- 独立 negative-prompt 请求字段
- seed、运动强度、采样器、帧率和任意分辨率
- 多参考图、独立首帧和独立尾帧
- create 请求中的音频生成、对白、口型或音轨控制
- 任意秒数、任意宽高比和不同尺寸的隐式兼容
- 各模型别名在用户账户、区域和配额中的实际可用性

**requires_manual_configuration**

- `api_key`
- `model`
- `seconds`
- `size`
- `input_reference`（仅在有已授权资产且确需使用时）
- `audio_delivery_path`
- `unsupported_shot_resolution`（镜头时长或尺寸不匹配时）

**adaptation_notes**

- 将 `universal_prompt_en` 映射到 `prompt`，将经过审计的单张参考映射到 `input_reference`。
- 只有镜头时长恰为 4、8 或 12 秒时，才可把 `seconds` 写入 `documented_parameters`。例如 5 秒镜头不能伪装成 4 秒或 8 秒；应回到时长/剪辑决策。
- 将获批画幅映射到一个官方 `size`。若没有等价 size，保持 `resolution` 未决并请求决定。
- `negative_prompt_en` 不得擅自映射到未文档化字段；可在不与正向要求冲突时把最关键排除项压缩进 `prompt`，并在 job 中记录该适配。

## Veo on Google Cloud / Vertex AI

**official_docs**

- https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/veo-video-generation
- https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-text
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-0-generate-001
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/veo/3-1-generate
- https://docs.cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos-from-first-and-last-frames

**verified_at**：2026-07-18

**verification note**

- 指定的 `generate-videos-from-text` 入口在本次核实时返回 404，`model-reference` 入口出现产品重定向；因此只采用仍能从 Google Cloud 官方页面直接核对的字段，并把冲突能力留给手动配置。

**verified_models**

- `veo-2.0-generate-001`
- `veo-3.0-generate-001`
- `veo-3.0-fast-generate-001`
- `veo-3.1-generate-001`
- `veo-3.1-fast-generate-001`

**supported_generation_modes**

- 官方 API reference 记录文本生视频与图生视频请求形态。
- Veo 3.1 当前官方 model page 明确记录 text-to-video、image-to-video、first-to-last-frame 和 extension。
- first/last-frame 官方页面明确列出 `veo-2.0-generate-001`、`veo-3.1-generate-001` 与 `veo-3.1-fast-generate-001`；不得把该支持外推到未列出的模型。

**prompt_language**

- Veo 3.0 与 3.1 当前官方 model pages 记录 English。其他语言不得自动声明等价支持。

**reference_inputs**

- 通用请求结构可包含 `instances[].image`；first/last-frame 流程使用 `image` 与 `lastFrame`。
- Veo 3.1 官方 model page 记录 asset reference images；具体数量、reference type、时长和模型限制必须由所选模型的当前 API 页面再次确认。

**first_last_frame_support**

- 上述三个明确列出的模型支持 first/last-frame 官方流程。
- `lastFrame` 只在已核实模型、图像 MIME 类型和模式下使用；其他模型进入未核实列表。

**audio_support**

- 官方页面显示明显的模型/版本差异：Veo 3.0 页面记录 sound generation，而当前 Veo 3.1 standard/fast 页面记录 sound generation unavailable。`generateAudio` 只可在所选精确模型的当前 API schema 与 model page 一致时进入请求；否则声音走后期。

**documented_durations**

- Veo 2：`5` 到 `8` 秒；官方 API 页面记录默认 8 秒。
- Veo 3：`4`、`6` 或 `8` 秒；官方 API 页面记录默认 8 秒。
- 使用 `referenceImages` 的官方 API 说明记录为 8 秒；不要将此约束外推到所有单图或首尾帧模式。

**documented_aspect_ratios_or_sizes**

- `aspectRatio`: `"16:9"`、`"9:16"`。
- `resolution`: `"720p"`、`"1080p"` 只在官方说明的 Veo 3 模型上使用。
- Veo 3.1 model page 还显示模型特定分辨率差异；实际 job 必须按精确 model ID 重新核实，不跨模型复制 4K 等能力。

**documented_parameters**

官方 Veo API reference 列出的请求字段如下；每个 job 必须按精确模型和模式过滤，不代表所有字段可同时使用：

- instance fields: `prompt`、`image`、`lastFrame`、`referenceImages`、`mask`
- parameter fields: `aspectRatio`、`compressionQuality`、`durationSeconds`、`enhancePrompt`、`generateAudio`、`negativePrompt`、`personGeneration`、`resizeMode`、`resolution`、`sampleCount`、`seed`、`storageUri`

**unsupported_or_unverified**

- 指定的 text-generation 指南入口当前 404 后，其旧示例与当前产品重定向是否完全等价
- 用户项目所在区域、配额、发布阶段和精确模型可用性
- 所有模型共享相同 audio、reference、first/last-frame、extension 或 resolution 能力
- 任意时长、任意画幅、任意输出分辨率和帧率
- asset/style reference 的数量与类型在所有 GA 模型上的统一限制
- 模型生成精确品牌文字或可靠口型

**requires_manual_configuration**

- `project_id`
- `location`
- `authentication`
- `model_id`
- `storageUri`
- `generation_mode`
- `reference_inputs`
- `durationSeconds`
- `aspectRatio`
- `resolution`
- `generateAudio`
- `audio_delivery_path`

**adaptation_notes**

- 将 canonical prompt 映射到 `instances[].prompt`，将 `negative_prompt_en` 映射到 `negativePrompt` 前先检查所选精确模型/模式的 schema。
- 只在 storyboard 时长落入所选模型官方范围时写 `durationSeconds`；否则请求拆镜、fallback 或剪辑方案决定。
- 5 秒香水电梯示例选择 `veo-2.0-generate-001` 的 text-to-video 路径，并只使用已核实的 `durationSeconds: 5`、`aspectRatio: "9:16"`、`sampleCount: 1`。项目、鉴权、存储和分辨率仍为手动配置。
- 需要首尾帧时，先验证 model ID 在官方 first/last 列表中，再映射 `image` 与 `lastFrame`；不要把普通 asset reference 当作尾帧。

## Kling Open Platform

**official_docs**

- https://kling.ai/document-api/apiReference/model/textToVideo
- https://kling.ai/document-api/apiReference/model/imageToVideo

**verified_at**：2026-07-18

**verified_models**

- 空。本次官方页面只返回无法可靠解析的应用壳，未能从页面正文核实 model ID。

**supported_generation_modes**

- `unsupported_or_unverified`。URL 名称暗示 text-to-video 与 image-to-video，但 URL 路径本身不作为能力或请求 schema 证据。

**prompt_language**

- `unsupported_or_unverified`

**reference_inputs**

- `unsupported_or_unverified`

**first_last_frame_support**

- `unsupported_or_unverified`

**audio_support**

- `unsupported_or_unverified`

**documented_durations**

- 空；不从记忆、博客、社区 SDK 或第三方示例补数字。

**documented_aspect_ratios_or_sizes**

- 空；不从非官方来源补枚举。

**documented_parameters**

- 空对象。页面正文可验证前，不写任何请求字段。

**unsupported_or_unverified**

- model ID、endpoint、鉴权格式、prompt 字段名
- generation mode、参考输入、首尾帧、音频、口型
- duration、aspect、resolution、seed、camera controls、callback 和任务状态字段
- 区域、账户权限、配额和价格

**requires_manual_configuration**

- `official_schema_access`
- `model_id`
- `endpoint`
- `authentication`
- `generation_mode`
- `prompt_field`
- `reference_inputs`
- `first_last_frame_support`
- `audio_support`
- `duration`
- `aspect`
- `resolution`
- `all_request_parameters`

**adaptation_notes**

- 保留 canonical prompt、storyboard 和空 `documented_parameters`；不得生成看似可调用的 Kling 请求体。
- 用户若能提供当前官方 schema 或可访问文档，再逐字段核实并更新 `verified_at`；在此之前选 generic/manual job 或另一个已核实 provider。

**cinematic_adapter_status**：`manual_only_until_official_request_schema_is_readable`。

## Seedance / Volcano Engine

**official_docs**

- https://www.volcengine.com/docs/6492/2192001?lang=en
- https://www.volcengine.com/docs/82379/2315856?lang=en

**verified_at**：2026-07-18

**verified_models**

- 空。本次官方页面只返回无法可靠解析的应用壳/重定向，未能从正文核实 model ID。

**supported_generation_modes**

- `unsupported_or_unverified`

**prompt_language**

- `unsupported_or_unverified`

**reference_inputs**

- `unsupported_or_unverified`

**first_last_frame_support**

- `unsupported_or_unverified`

**audio_support**

- `unsupported_or_unverified`

**documented_durations**

- 空；不从记忆、营销页或第三方 SDK 补数字。

**documented_aspect_ratios_or_sizes**

- 空；不从非官方来源补枚举。

**documented_parameters**

- 空对象。官方正文可验证前，不写 endpoint、model、content、callback 或其他猜测字段。

**unsupported_or_unverified**

- product/model ID、endpoint、鉴权、请求与响应 schema
- text-to-video、image-to-video、reference、first/last-frame 和 extension 的精确支持
- prompt language、audio、lip-sync、duration、aspect、resolution、seed 与 camera controls
- 区域、账户权限、配额和价格

**requires_manual_configuration**

- `official_schema_access`
- `product_or_model_id`
- `endpoint`
- `authentication`
- `generation_mode`
- `prompt_field`
- `reference_inputs`
- `first_last_frame_support`
- `audio_support`
- `duration`
- `aspect`
- `resolution`
- `all_request_parameters`

**adaptation_notes**

- 保留 canonical prompt 和已批准镜头；`documented_parameters` 使用空对象，并把所有 provider 配置列入手动数组。
- 只有能从当前官方页面逐字段读取 schema 后，才创建 Seedance/Volcano 专用 job；不得用二手文章或旧记忆回填。

**cinematic_adapter_status**：`manual_only_until_official_request_schema_is_readable`。

## HappyHorse on Alibaba Cloud Model Studio

**official_docs**

- https://www.alibabacloud.com/help/en/model-studio/video-generate-edit-model
- https://www.alibabacloud.com/help/en/model-studio/happyhorse-text-to-video-api-reference

**verified_at**：2026-07-18

**verified_models**

- `happyhorse-1.1-t2v`
- `happyhorse-1.1-i2v`
- `happyhorse-1.1-r2v`

**supported_generation_modes**

- text-to-video：`happyhorse-1.1-t2v`
- first-frame image-to-video：`happyhorse-1.1-i2v`
- reference-image-to-video：`happyhorse-1.1-r2v`

**prompt_language**

- text-to-video 官方字段 `input.prompt` 支持任意语言。

**reference_inputs**

- `t2v` 不需要图像参考。
- `i2v` 与 `r2v` 的模型和用途已由官方模型表核实，但本次没有从独立 API 正文逐字段读取输入 schema；job 中保留 Canon 资产引用，并把 `i2v_request_schema` 和 `r2v_request_schema` 放入手动配置。

**first_last_frame_support**

- `unsupported_or_unverified`；不得把其他阿里云视频模型的首尾帧能力写成 HappyHorse 能力。

**audio_support**

- 官方模型表将 HappyHorse 1.1 的 t2v、i2v、r2v 标记为音画输出。自定义音频输入方式未在所选 HappyHorse 正文中核实。

**documented_durations**

- 3–15 秒。

**documented_aspect_ratios_or_sizes**

- t2v 比例：`16:9`、`9:16`、`1:1`、`4:3`、`3:4`、`4:5`、`5:4`、`9:21`、`21:9`。
- 分辨率：`720P`、`1080P`。
- i2v 与 r2v 的比例控制方式需按各自请求 schema 再核实。

**documented_parameters**

- t2v：`model`、`input.prompt`、`parameters.resolution`、`parameters.ratio`、`parameters.duration`、`parameters.watermark`、`parameters.seed`。
- 异步请求头：`X-DashScope-Async: enable`。
- 状态流转：`PENDING`、`RUNNING`、`SUCCEEDED`、`FAILED`、`CANCELED`、`UNKNOWN`。

**async_job_model**：`create_task_then_poll`

**result_expiry**：`result_url_valid_for_24_hours`；任务 ID 查询有效期同为 24 小时，应提示用户的编排程序及时归档。

**unsupported_or_unverified**

- i2v 和 r2v 的精确 endpoint、输入字段与参考数量。
- 自定义音频、首尾帧、相机控制和编辑字段。
- 用户账户对应的区域、workspace domain、配额和价格。

**requires_manual_configuration**

- `workspace_id`
- `region_endpoint`
- `authentication`
- `input_asset_urls`
- `i2v_request_schema`
- `r2v_request_schema`
- `result_persistence`

**adaptation_notes**

- 有稳定角色参考资产时，优先建议 r2v；只有首帧时建议 i2v；素材未完成时保留 t2v 或 generic/manual job。
- 只有 t2v 正文中逐字段核实的字段可以进入可执行 `documented_parameters`。i2v/r2v job 在独立 schema 核实前保持 manual-only。
- Skill 只交付任务清单，不提交、轮询或下载真实任务。

## Generic fallback

**official_docs**：空；它不是 provider API，而是安全的未绑定任务格式。

**verified_at**：2026-07-18

**verified_models**：空。

**supported_generation_modes**：由 storyboard 的 `generation_strategy` 保留为导演意图，但未映射为任何 provider 能力。

**prompt_language**：使用 canonical `universal_prompt_en`，provider 接受性未核实。

**reference_inputs**：保留 `reference_requirements`，不生成 provider 字段。

**first_last_frame_support**：`unsupported_or_unverified`。

**audio_support**：`unsupported_or_unverified`，默认后期。

**documented_durations**：空。

**documented_aspect_ratios_or_sizes**：空。

**documented_parameters**：空对象。

**unsupported_or_unverified**：所有 provider 能力、字段、枚举、限制和执行状态。

**requires_manual_configuration**：`provider`、`model`、`endpoint`、`authentication`、`generation_mode`、`reference_inputs`、`duration`、`aspect`、`resolution`、`audio_delivery_path`、`all_request_parameters`。

**adaptation_notes**：当目标 provider 未指定或官方 schema 不可验证时输出 generic job。它是待配置任务，不是假装可直接调用的请求。

## Job 编译流程

1. 按 `shot_id` 读取 storyboard 与唯一 canonical prompt。
2. 读取用户真实可访问的 provider/model；没有则使用 Generic fallback。
3. 打开本页记录的官方入口，确认页面与 `verified_at` 后是否变化。
4. 选择精确 model ID 和 generation mode，并逐项核对时长、画幅、尺寸、reference、首尾帧与 audio。
5. 只把核实字段写入 `documented_parameters`；其余写入 `requires_manual_configuration`。
6. 检查 job 时长、shot ID、prompt source、reference 与 storyboard 一致，且 job 没有新增故事事实。
7. 若 provider 无法实现镜头，返回用户选择 fallback、拆分或更换 provider；不得静默改镜头。

## 交付检查

- [ ] provider 记录包含全部规定字段；
- [ ] `verified_at` 为本次核实日期；
- [ ] 每项数字限制与参数名可追溯到当前官方一手文档；
- [ ] 官方页面不可访问或互相冲突的项均标成 `unsupported_or_unverified`；
- [ ] `documented_parameters` 是对象，且没有猜测字段；
- [ ] `requires_manual_configuration` 是数组；
- [ ] job 与 shot 的 ID、时长、画幅、reference 和 prompt source 一致；
- [ ] 切换 provider 没有改变故事、分镜或连续性；
- [ ] 无法支持的镜头已经请求决定或选择获批 fallback；
- [ ] Skill 只交付任务清单，没有调用 API。
