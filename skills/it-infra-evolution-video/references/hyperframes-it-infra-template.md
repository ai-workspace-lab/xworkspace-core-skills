# HyperFrames IT Infrastructure Template

这个模板来自 `/Users/shenlan/workspaces/cloud-neutral-toolkit/docs/it-infra-evolution-video` 的样片，适合把竖版技术长图改成 16:9 横屏讲解视频。默认目标是让新视频与样片 `it-infra-evolution.mp4` 的观感一致。

样片里的 `8 段完整结构`、`82 秒`、`8 列 timeline` 是默认配置和可复用结构特征，不是硬编码限制。实际项目必须先从用户输入生成配置，再把配置渲染成 scene、caption、timeline tag、audio clip 和校验时间点。

## Visual Identity

- 背景：白到浅蓝渐变，少量 cyan 光环。
- 主色：`#07194F` 深蓝、`#155BFF` 基础设施蓝、`#49D9FF` cyan、`#18BFA6` AI 绿色。
- 字体：中文系统 sans。标题大而紧，说明文字中等，tag 小而清晰。
- 画面气质：技术纪录片、架构简报、清爽图解，不做暗色科幻仪表盘。

## Layout

- 根合成：`data-width="1920"`、`data-height="1080"`，`data-duration` 来自配置。
- 每个章节一个 `.scene.clip`，同一 track 顺序播放；章节数来自配置。
- timeline 列数默认等于章节数，用 `grid-template-columns: repeat(var(--timeline-columns), minmax(0, 1fr))` 或生成后的 `repeat(N, minmax(0, 1fr))` 表达。
- 样片默认时间轴：
  - `0.0s` 引言，`12.0s`
  - `12.2s` 基础设施主线，`8.6s`
  - `21.0s` 账户与安全，`9.8s`
  - `31.0s` 监控与可观测性，`9.2s`
  - `40.4s` 网络与协议，`10.0s`
  - `50.6s` 存储服务，`9.4s`
  - `60.2s` 平台工程，`9.0s`
  - `69.4s` 与 AI 共同进化，`11.6s`
- 内容区使用双栏：
  - 左栏是 `.image-panel`，放真实长图。
  - 右栏是 `.copy`，放 kicker、标题、说明、关键词 tags。
- 内容区 padding 必须保持接近样片：`92px 104px 214px`。
- `.image-panel` 必须保持：`height: 760px`、`border-radius: 34px`、白底、淡蓝边框和大阴影。
- 底部固定 `.timeline`：
  - `grid-template-columns` 按 `timelineColumns` 生成；样片是 `repeat(8, minmax(0, 1fr))`
  - 左右 `70px`，底部 `28px`，高 `88px`
  - 每个 `.chapter-tag` 包含时间和标题。
  - 当前章节加 `.active`，蓝绿渐变背景、白字、轻微上浮。
- 字幕 `.caption` 放在 timeline 上方，深蓝半透明背景；保持 `left/right: 320px`、`bottom: 132px`。

## Motion

- 每个 scene 入场：
  - image panel: `x: -78, opacity: 0, scale: 0.96`
  - kicker/title/lead/tags 顺序上浮。
- 每个长图做慢速扫描：
  - `tl.to("${scene} .image-panel img", { y: -70, scale: 1.1, duration: ... })`
  - 裁切 warning 是预期行为，需人工看 snapshot 确认主体可见。
- 章节 tag：
  - 在章节 start 设置 `.active`
  - 在章节结束前移除 `.active`
  - 同步 `y: -8, scale: 1.04` 到 `y: 0, scale: 1`
- 总进度条用真实 DOM 元素 `.timeline-progress`，不要直接动画伪元素。
- 根节点在 `duration - 0.75s` 左右开始淡出，`0.65s` 完成。

## Audio

- 所有音频都必须是 `<audio class="clip">`。
- BGM 使用高 track，例如 `data-track-index="20"`。
- 口播使用固定 track，例如 `data-track-index="5"`。
- SFX 使用 `6` 和 `7`。

## Validation

```bash
npx --yes hyperframes@0.6.15 lint
npx --yes hyperframes@0.6.15 inspect --at 2,14,24,34,44,54,64,74
npx --yes hyperframes@0.6.15 snapshot --at 2,14,24,34,44,54,64,74
```

Expected acceptable warnings:

- repeated source images when the same asset appears in multiple chapters
- dense single-file track if the project is intentionally small
- image overflow when zooming/scanning inside clipped panels

Errors or visible overlap must be fixed before render.

## Template Use

Use `templates/index.html` as the visual source of truth. It is intentionally a full working sample, not a shortened snippet. When adapting it:

- Replace `assets/images/*.png` with the user's real images.
- Build a `sections` config first, then generate exactly one scene, one caption, and one timeline tag per section.
- Set root `data-duration` from config, not from the sample duration.
- Set timeline columns from config, usually `sections.length`.
- Regenerate voiceover, then update all audio `data-duration` values from `ffprobe`.
- Keep the same track layout: scenes on track `1`, captions on `10`, BGM on `20`, SFX on `6/7`.
- Keep the same timeline tag interaction and progress bar.
- Recompute validation timestamps from each section midpoint whenever duration or chapter count changes.
