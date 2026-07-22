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
- 第三方 Playwright/Cookie wrapper 只能作为运行风险参考：可借鉴 submit/poll/download、retry/cancel、credits 与 credential-risk 这些 `operation_state` 概念；不得把 cookie、session、private/internal endpoint 或非官方字段写入 `documented_parameters`。

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

## ToAPIs Video Gateway

**official_docs**

- https://docs.toapis.com/docs/en/api-reference/videos/veo3-official/generation
- https://docs.toapis.com/docs/en/api-reference/videos/kling-v3/generation
- https://docs.toapis.com/docs/en/api-reference/videos/happyhorse/generation
- https://docs.toapis.com/docs/cn/api-reference/videos/seedance-2/generation
- https://docs.toapis.com/docs/cn/api-reference/videos/doubao-seedance-1-5/generation
- https://docs.toapis.com/docs/cn/api-reference/videos/sora-2-official/generation
- https://docs.toapis.com/docs/cn/api-reference/videos/minimax-hailuo-2.3/generation
- https://docs.toapis.com/docs/cn/api-reference/videos/wan2.6/generation
- https://docs.toapis.com/docs/en/api-reference/videos/viduq3/generation
- https://docs.toapis.com/docs/en/api-reference/videos/gemini-omni-flash/generation
- https://docs.toapis.com/docs/en/api-reference/tasks/video-status
- https://docs.toapis.com/docs/cn/api-reference/uploads/images

**verified_at**: 2026-07-22

**verified_models**

- `Veo3.1-quality-official`
- `Veo3.1-fast-official`
- `kling-v3`
- `happyhorse-1.1`
- `seedance-2`
- `seedance-2-fast`
- `seedance-2-mini`
- `doubao-seedance-1-5-pro`
- `sora-2-official`
- `MiniMax-Hailuo-2.3`
- `MiniMax-Hailuo-2.3-Fast`
- `wan2.6`
- `viduq3-pro`
- `viduq3-turbo`
- `viduq3`
- `gemini_omni_flash`

**supported_generation_modes**

- Shared video gateway: submit async jobs with `POST /v1/videos/generations`, then poll with `GET /v1/videos/generations/{task_id}`.
- Veo3 Official: text-to-video, image-to-video, and keyframe-style generation only through the documented Veo3 Official fields.
- Kling v3: text-to-video, image-to-video, explicit first/last frame control, and audio-video generation only through the documented Kling v3 fields.
- HappyHorse 1.1: `text-to-video`, `image-to-video`, `reference-to-video`, and `video-edit` through the documented HappyHorse `action` field.
- Seedance 2: text-to-video, first-frame, first/last-frame, and multi-modal reference generation through `image_with_roles`, `video_with_roles`, and `audio_with_roles`.
- Doubao Seedance 1.5 Pro: text-to-video and first/last-frame image-to-video; do not use reference-image mode because the official page directs that use case to Seedance 2.
- Sora 2 Official: text-to-video and one-image image-to-video through `image_urls`.
- MiniMax Hailuo 2.3: text-to-video and image-to-video; `MiniMax-Hailuo-2.3-Fast` requires `image_urls`.
- Wan2.6: text-to-video, one-image image-to-video, and reference-video routing through `metadata.reference_urls`.
- Vidu Q3: text-to-video, image-to-video, first/last-frame, and reference-to-video through Vidu Q3 model-specific image counts and `metadata.generation_type`.
- Gemini Omni Flash: text-to-video, single-image video, and three-image reference fusion through `image_urls`.

**prompt_language**

- Compile the director-approved `universal_prompt_en` into `prompt`. Do not translate story facts at adapter time. If the user requires another language, keep it as a provider-specific prompt variant with the same `intent_refs`.

**reference_inputs**

- ToAPIs video endpoints require URL references. Local reference images must be uploaded first with `POST /v1/uploads/images` or left in `requires_manual_configuration`.
- Do not place base64 image data in `image_urls`.
- Veo3 Official uses `image_urls` for image inputs and `metadata.referenceImages` / `referenceImages` for reference image metadata.
- Kling v3 uses `reference_images` and `image_with_roles` for documented reference and first/last-frame control.
- HappyHorse 1.1 uses `image_urls` for image-to-video inputs and `reference_images` for reference-to-video or video-edit inputs.
- Seedance 2 uses `image_with_roles` for `first_frame`, `last_frame`, and `reference_image`; `video_with_roles` for `reference_video`; and `audio_with_roles` for `reference_audio`.
- Doubao Seedance 1.5 Pro uses `image_with_roles` or compatible `image_urls` for first/last-frame inputs; `reference_image` is not supported by that 1.5 Pro page.
- Sora 2 Official uses `image_urls` and only the first image is used as the reference.
- MiniMax Hailuo 2.3 uses `image_urls` for first-frame image-to-video.
- Wan2.6 uses `image_urls` for one-image i2v, or `metadata.reference_urls` for reference-video r2v; do not mix those two modes.
- Vidu Q3 uses `image_urls`: 0 images for t2v, 1 image for i2v, 2 images for first/last-frame with `viduq3-pro` or `viduq3-turbo`, and up to 7 reference images for `viduq3`.
- Gemini Omni Flash uses `image_urls`: omit/empty for t2v, 1 image for single-image video, 3 images for reference-image fusion; 2 images is unsupported.

**first_last_frame_support**

- Veo3 Official: use `image_urls` plus documented `metadata.lastFrame` only when the selected shot explicitly needs a last-frame lock.
- Kling v3: use `image_with_roles` when first/last frame roles are required.
- HappyHorse 1.1: first-frame image-to-video can use `image_urls`; last-frame control is not promoted unless the selected action and official fields support it.
- Seedance 2: use `image_with_roles` with `first_frame` and `last_frame`.
- Doubao Seedance 1.5 Pro: use `image_with_roles` with `first_frame` and `last_frame`; `image_urls` compatibility may infer roles but should not be preferred.
- Sora 2 Official, MiniMax Hailuo 2.3, Wan2.6, and Gemini Omni Flash: no first/last-frame capability is promoted beyond documented image-reference behavior.
- Vidu Q3: `viduq3-pro` and `viduq3-turbo` can use two `image_urls` as first and last frame.

**audio_support**

- Veo3 Official: `metadata.generateAudio`.
- Kling v3: `audio`.
- HappyHorse 1.1: `audio_setting` only where its selected action supports it.
- Seedance 2: `generate_audio`; Seedance 2 mini can also use `audio_with_roles` in the documented multi-modal reference flow.
- Doubao Seedance 1.5 Pro: `metadata.audio`.
- Wan2.6: `audio`.
- Vidu Q3: `audio` for `viduq3-pro` and `viduq3-turbo`.
- Do not promise lip-sync, dialogue fidelity, music licensing, or finished-film sound design from model audio alone; keep final sound obligations in the edit plan.

**documented_durations**

- Veo3 Official: `4`, `6`, or `8` seconds.
- Kling v3: `3` to `15` seconds.
- HappyHorse 1.1: `3` to `15` seconds.
- Seedance 2 / Fast / Mini: `4` to `15` seconds; `0` or `-1` auto-duration only for `seedance-2` and `seedance-2-fast`.
- Doubao Seedance 1.5 Pro: `4` to `12` seconds.
- Sora 2 Official: `4`, `8`, or `12` seconds.
- MiniMax Hailuo 2.3: `6` or `10` seconds; `1080P` only supports `6` seconds.
- Wan2.6: `5`, `10`, or `15` seconds.
- Vidu Q3: `viduq3-pro` / `viduq3-turbo` support `1` to `16` seconds; `viduq3` supports `3` to `16` seconds.
- Gemini Omni Flash: `4`, `6`, or `10` seconds.

**documented_aspect_ratios_or_sizes**

- Veo3 Official uses `size`: `16:9` or `9:16`, with `resolution` such as `720p`, `1080p`, or documented preview options.
- Kling v3 uses `aspect_ratio`; `mode` controls documented quality tier such as `std` or `pro`.
- HappyHorse 1.1 uses `aspect_ratio`: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, with `resolution` such as `720P` or `1080P`.
- Seedance 2 uses `aspect_ratio`: `21:9`, `16:9`, `4:3`, `1:1`, `3:4`, `9:16`, or `adaptive`, plus documented `resolution`.
- Doubao Seedance 1.5 Pro uses `aspect_ratio`: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, `21:9`, with `metadata.resolution`: `480p`, `720p`, or `1080p`.
- Sora 2 Official uses `aspect_ratio`: `16:9` or `9:16`; image references must match the documented 1280x720 or 720x1280 frame size.
- MiniMax Hailuo 2.3 uses `resolution`: `768P` or `1080P`; `1080P` only supports 6 seconds.
- Wan2.6 uses `aspect_ratio`: `16:9`, `9:16`, `1:1`, `4:3`, `3:4`, and `resolution`: `720p` or `1080p`.
- Vidu Q3 uses `aspect_ratio` for text-to-video and `resolution`: `540p`, `720p`, or `1080p`.
- Gemini Omni Flash uses `aspect_ratio`: `16:9` or `9:16`; `resolution`: `720P` or `1080p` where documented.

**documented_parameters**

- Shared submit route: `POST /v1/videos/generations`; common fields include `model`, `prompt`, and model-specific duration fields.
- Shared status route: `GET /v1/videos/generations/{task_id}`; status values include queued, in_progress, completed, and failed.
- Shared image upload route: `POST /v1/uploads/images`; use the returned URL for video reference fields.
- Veo3 Official: `model`, `prompt`, `duration`, `size`, `resolution`, `image_urls`, `metadata.generateAudio`, `metadata.negativePrompt`, `metadata.personGeneration`, `metadata.lastFrame`, `metadata.referenceImages`, `metadata.compressionQuality`, `metadata.resizeMode`.
- Kling v3: `model`, `prompt`, `mode`, `duration`, `aspect_ratio`, `reference_images`, `image_with_roles`, `audio`, `metadata.negative_prompt`, `metadata.watermark`.
- HappyHorse 1.1: `model`, `action`, `prompt`, `image_urls`, `reference_images`, `url`, `audio_setting`, `duration`, `resolution`, `aspect_ratio`, `seed`, `watermark`.
- Seedance 2: `model`, `client_business_id`, `prompt`, `duration`, `aspect_ratio`, `resolution`, `generate_audio`, `image_with_roles`, `video_with_roles`, `audio_with_roles`.
- Doubao Seedance 1.5 Pro: `model`, `prompt`, `duration`, `aspect_ratio`, `image_urls`, `image_with_roles`, `metadata.resolution`, `metadata.seed`, `metadata.audio`, `metadata.camerafixed`.
- Sora 2 Official: `model`, `prompt`, `duration`, `aspect_ratio`, `image_urls`.
- MiniMax Hailuo 2.3: `model`, `prompt`, `duration`, `resolution`, `image_urls`, `metadata.prompt_optimizer`, `metadata.fast_pretreatment`.
- Wan2.6: `model`, `prompt`, `image_urls`, `aspect_ratio`, `resolution`, `duration`, `negative_prompt`, `seed`, `prompt_extend`, `audio`, `shot_type`, `watermark`, `metadata.reference_urls`.
- Vidu Q3: `model`, `prompt`, `duration`, `resolution`, `aspect_ratio`, `image_urls`, `audio`, `metadata.generation_type`, `metadata.seed`.
- Gemini Omni Flash: `model`, `prompt`, `duration`, `aspect_ratio`, `resolution`, `image_urls`.

**async_job_model**: `submit_then_poll_then_download`

- `operation_state` is the required lifecycle container for every executable ToAPI job.
- `operation_state.submit.endpoint`: `POST /v1/videos/generations`.
- `operation_state.poll.endpoint`: `GET /v1/videos/generations/{task_id}`.
- `operation_state.upload_image.endpoint`: `POST /v1/uploads/images` when local image references must become URLs.
- `operation_state.status`: pending authorization, credential_check, uploaded_references, submitted, queued, in_progress, completed, failed, canceled, downloaded, or blocked.
- `operation_state.credential_env`: default `TOAPIS_API_KEY`; aliases may be added only by user instruction.
- `operation_state.credential_status`: present, missing, or unreadable. Never print or persist the secret value.
- `TOAPIS_API_KEY` must be read from the process or user environment when execution is authorized; the Skill must not ask the user to paste the API key.
- The authorization header is constructed only at execution time from the environment value. Any preview, log, manifest, or error report may show only `Authorization: Bearer <redacted>`.

**result_expiry**

- Veo3 Official states generated video links are valid for 24 hours.
- Status responses can include `expires_at`; persist results promptly after authorized download.
- For other ToAPIs model families, record the returned expiry if present instead of assuming a universal expiry window.

**unsupported_or_unverified**

- A single universal ToAPI request body across all video models.
- Mixing Veo3 Official `size` with Kling/HappyHorse `aspect_ratio` in one job.
- Mixing `metadata.negativePrompt` and `metadata.negative_prompt` without selecting the model family.
- Using base64 image data in `image_urls`, except where a selected model page explicitly allows base64 inside role-based asset fields; prefer upload URLs or `asset://` records.
- Treating Seedance 2 role-based fields, Wan2.6 reference-video routing, Vidu image-count routing, or Gemini image-count routing as interchangeable.
- Arbitrary durations, aspect ratios, resolutions, audio promises, lip-sync, model availability, pricing, credits, or account quotas.
- Reading or displaying API keys; only environment-variable presence may be checked.
- Uploading, submitting, polling, downloading, overwriting, or publishing without explicit operation authorization.

**requires_manual_configuration**

- `toapis_api_key_env`: default `TOAPIS_API_KEY`
- `selected_toapis_model`
- `toapis_model_family`: `veo3_official`, `kling_v3`, `happyhorse_1_1`, `seedance_2`, `doubao_seedance_1_5`, `sora_2_official`, `minimax_hailuo_2_3`, `wan_2_6`, `vidu_q3`, or `gemini_omni_flash`
- `generation_mode`
- `duration`
- `size_or_aspect_ratio`
- `resolution_or_mode`
- `reference_image_uploads`
- `audio_generation_policy`
- `negative_prompt_policy`
- `result_download_path`
- `operation_authorization`

**adaptation_notes**

- ToAPI/ToAPIs is a gateway, not a director. The story, identity locks, and shot intent must come from Canon before adapter compilation.
- Select the exact `toapis_model_family` before emitting provider JSON. If the family is unknown, emit a generic/manual job and mark the ToAPI job manual-only.
- Map `universal_prompt_en` to `prompt`; never let adapter fields add new story facts.
- If the storyboard supplies local reference images, prepare upload-image tasks first or block execution until public URLs exist.
- Keep every job non-executable until `credential_status` is present and the user gives operation authorization for the exact manifest.

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
