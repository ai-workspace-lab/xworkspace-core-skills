---
name: it-infra-evolution-video
version: "v1"
description: "制作 IT 基础设施系列长图讲解视频。适用于 IT基础设施演进史、一图看懂视频、长图讲解视频、平台工程视频、网络/存储/安全/监控演进视频。默认使用 HyperFrames + edge-tts + 真实用户图/信息图素材，生成 1920x1080 横屏视频、中文口播、逐句字幕、BGM、章节 timeline tag，并完成 lint/inspect/snapshot/render/ffprobe 验证。"
---

# IT 基础设施系列长图讲解视频 Skill

## Version Lock

- Version: `v1`
- Status: read-only frozen template
- Do not mutate this skill in-place for v2 work. Create a new copy instead.
- XWorkmate/OpenClaw task runs that must sync artifacts to `tasks/<session>/<run>`
  should use `it-infra-evolution-video-v2`, because v2 has the deterministic
  runner and task-scope guard. Do not report completion from v1 unless the final
  MP4 is actually present in the current prepared task artifact scope.

使用 `HyperFrames + edge-tts + 用户长图/信息图素材` 制作中文技术讲解视频。默认效果必须对齐样片 `/Users/shenlan/workspaces/cloud-neutral-toolkit/docs/it-infra-evolution-video` 的合成风格：蓝白技术纪录片视觉、双栏长图扫描、底部章节 timeline tag、高亮当前章节、深蓝字幕条和本地合成 BGM/SFX。样片里的 `8 段完整结构`、`82 秒`、`8 列 timeline` 是可提取的结构特征和默认配置，不是固定限制；实际章节数、总时长、timeline 列数必须由用户输入或生成配置决定。这个 skill 是 `ai-tech-news-video` 的独立派生副本，**不要修改原始 `ai-tech-news-video` skill**。

## 适用场景

触发词包括：

- `IT基础设施演进史`
- `一图看懂视频`
- `长图讲解视频`
- `平台工程视频`
- `网络演进视频`
- `存储演进视频`
- `账户与安全体系视频`
- `监控的前生今世`
- `与 AI 共同进化`

适合把用户提供的一组小红书/海报/架构图/信息图，转成横屏讲解视频。

## 默认规格

- 默认画布：`1920x1080`，16:9 横屏。
- 默认时长：用户未指定时使用样片配置 `82s` 左右；用户指定时以用户配置为准。
- 默认语言：中文。
- 默认 voice：`zh-CN-YunxiNeural`，`--rate="+20%"` 到 `"+30%"`。
- 默认结构：用户未指定时使用样片配置 8 个章节；用户指定时以用户的章节配置为准。
- 默认 timeline：列数等于章节数；用户未指定时使用样片配置 8 列。
- 必须包含：
  - 真实素材清单：`assets/images/manifest.md`
  - 每段口播音频
  - 每段可读字幕
  - BGM
  - 章节 timeline tag，当前章节高亮
  - HyperFrames `lint`、`inspect`、`snapshot`
  - 最终 MP4
  - `ffprobe` 分辨率、时长、音视频流校验

## 工作流

1. 收集用户给定的长图/信息图素材。
2. 建立 HyperFrames 项目，创建 `assets/images/`、`assets/audio/`、`assets/audio/sfx/`。
3. 复制或引用素材，并写 `assets/images/manifest.md`。
4. 产出章节配置：标题、口播、字幕、章节 tag、素材文件、`start`、`duration`。章节数、总时长和 timeline 列数必须来自用户输入或生成配置。
5. 用 `edge-tts` 生成每段口播。
6. 用 `scripts/render_audio_bed.py` 生成 BGM 和转场音效，或接入用户提供 BGM。
7. 基于 `templates/index.html` 生成 HyperFrames 合成页面；默认不要重写视觉系统，按配置增删 scene、caption、timeline tag，并替换素材、标题、文案、音频时长和章节 tag。
8. 运行：

```bash
npx --yes hyperframes@0.6.15 lint
npx --yes hyperframes@0.6.15 inspect --at 2,14,24,34,44,54,64,74
npx --yes hyperframes@0.6.15 snapshot --at 2,14,24,34,44,54,64,74
npx --yes hyperframes@0.6.15 render --output renders/it-infra-evolution.mp4 --quality standard
ffprobe -v quiet -show_entries format=duration,size:stream=codec_type,width,height,r_frame_rate -of json renders/it-infra-evolution.mp4
```

## 素材硬门槛

每个章节必须有真实素材。真实素材可以是：

- 用户提供的小红书/海报/信息图
- 官方页面截图
- 产品界面截图
- 架构图或技术图谱
- 公开资料截图

不要用纯 CSS 卡片、假界面、抽象图标或 AI 编造截图替代主素材。

`assets/images/manifest.md` 必须记录：

- 章节编号和标题
- 素材文件名
- 原始来源或用户提供路径
- 素材类型
- 该素材支撑哪段叙事

## 配置规则

先把用户输入沉淀成一个视频配置，再生成 HyperFrames 页面。配置字段至少包含：

- `duration`: 总时长，秒。
- `sections`: 章节数组。每个章节包含 `id`、`start`、`duration`、`timeLabel`、`timelineLabel`、`title`、`subtitle`、`tags`、`image`、`voiceover`、`caption`。
- `timelineColumns`: timeline 列数。默认等于 `sections.length`，除非用户明确要求分组显示。
- `inspectTimes`: 每个章节中点时间，用于 `inspect` 和 `snapshot`。

配置示例见 `templates/video.config.example.json`。这个文件只表达字段形状；正式项目应根据用户素材和节奏生成自己的配置。

结构参数优先级：

1. 用户明确给出的时长、章节和节奏。
2. 用户素材数量和叙事需要推导出的配置。
3. 样片默认配置：8 段、82 秒、8 列 timeline。

详细模板见 `references/storyboard-pattern.md`。

## 叙事模板

用户未指定结构时，使用样片同款 8 段默认结构：

1. 引言：这不是单点升级，而是一组能力共同进化。
2. 基础设施主线：硬件、虚拟化、云、容器、治理、AI 原生。
3. 账户与安全：边界从网络迁移到身份。
4. 监控与可观测性：从事后告警到预测、定位、自愈。
5. 网络与协议：从连接一切到理解一切。
6. 存储服务：从存下来到高效流动。
7. 平台工程：从人肉运维到平台化交付。
8. 与 AI 共同进化：从工具系统到 AI 协同系统。

用户素材不足 8 张时，合并章节；用户素材更多时，按主题拆成 6-10 个章节，或按用户指定的章节数执行。总时长以用户配置为准；未指定时保持在 60-90 秒。

## 画面模板

默认使用样片同款蓝白技术纪录片风格：

- 左侧展示真实长图，右侧显示章节 kicker、标题、短说明和关键词 tags。
- 画布背景是白到浅蓝渐变，并带右上角 cyan 圆环装饰。
- 长图放在 760px 高、34px 圆角、白底阴影的 `.image-panel` 内，默认 `object-fit: cover`，需要完整展示时用 `.contain`。
- 每段长图做 `y: -70`、`scale: 1.1` 的缓慢扫描。
- 底部固定半透明 timeline tag，列数由 `timelineColumns` 或 `sections.length` 决定，当前章节蓝绿渐变高亮并轻微上浮。
- 字幕位于 timeline 上方安全区，深蓝半透明底，左右 `320px`，底部 `132px`。
- 不加关注、点赞、收藏等 CTA，除非用户明确要求。

实现细节见 `references/hyperframes-it-infra-template.md`，可从 `templates/index.html` 开始改。

## 样片一致性要求

当用户要求“和 `it-infra-evolution.mp4` 效果一致”或未指定其他风格时：

- 使用 `templates/index.html` 的视觉和动效作为母版；其中 8 段/82 秒/8 列 timeline 是默认样片配置。
- 如果用户给出其他章节数、时长或 timeline 数量，按用户配置重排 scene、caption、timeline tag 和校验时间点。
- 保留 CSS 尺寸、颜色、圆角、阴影、caption、timeline、GSAP 动效参数。
- 只替换素材路径、章节文案、tag、音频文件名、`data-start` 和 `data-duration`。
- 不改成深色 dashboard、三图并列、纯生成海报轮播或营销片风格。
- 如果用户提供的是 1-2 张总览长图，也仍然用双栏长图扫描和章节 tag 组织，不要退化成静态 PPT。

## 口播规则

- 每段 1-2 句，尽量 8-12 秒。
- 不说“第一条、第二条”。
- 不说无关自我介绍。
- 字幕可以略短于口播，但必须覆盖关键含义。
- 每个 `<audio>` clip 必须有对应字幕 clip。
- 生成后用 `ffprobe` 读取音频时长，再把 `data-start` / `data-duration` 写入 HTML。

示例：

```bash
edge-tts --voice zh-CN-YunxiNeural --rate='+20%' \
  --text 'IT 基础设施演进史，不只是服务器升级。它是一组能力的共同进化。' \
  --write-media assets/audio/intro.mp3
```

## BGM 与音效

- 先检查项目是否已有 `assets/audio/bgm.mp3` 或 `assets/audio/bgm.wav`。
- 若没有，可使用本 skill 的 `scripts/render_audio_bed.py` 生成本地合成 BGM 和转场音效。
- BGM 音量建议 `data-volume="0.08"` 到 `0.12`。
- 口播音量建议 `data-volume="0.90"` 到 `0.95`。
- Web Audio API 不会进入 HyperFrames MP4，所有音频必须使用 `<audio class="clip">`。

## 验收标准

- `npx hyperframes lint` 无 error。
- `npx hyperframes inspect` 无布局 error；图片 zoom 裁切 warning 可接受。
- `snapshot` 至少覆盖每个章节的中间时刻。
- 最终 MP4 使用 `ffprobe` 确认为 `1920x1080`、有 video stream、有 audio stream、时长符合预期。
- 原始 `ai-tech-news-video` skill 未被修改。
