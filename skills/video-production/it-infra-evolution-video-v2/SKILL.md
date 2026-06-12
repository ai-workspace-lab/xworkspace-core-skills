---
name: it-infra-evolution-video-v2
version: "v2"
description: "从 it-infra-continuous-png 的真实 PNG manifest 生成 IT 基础设施长图讲解视频。强制执行 manifest -> video.config.json -> index.html -> audio -> HyperFrames acceptance -> MP4 -> ffprobe 的闭环。"
---

# IT 基础设施长图讲解视频 v2

本 skill 是 `it-infra-evolution-video` 的可执行 v2 路径。v1 模板保持 frozen；v2 的主路径必须通过仓库 runner 完成，不再让 Agent 临时手写 `generate_index.py` 或自由拼接模板片段。

## 调用前置条件

必须先完成 `it-infra-continuous-png`：

- `assets/images/*.png` 存在，且每个文件是真实 PNG。
- `assets/images/manifest.md` 存在。
- manifest 每一行都包含 `chapter_id`、`title`、`file`、`source_type`、`video_usage`、`scan_mode`、`safe_focus`。

缺少这些输入时，不要继续生成视频，不要用 CSS 卡片、假截图或 SVG 冒充 PNG。

## 标准调用

在 Bridge 预先准备的当前任务 artifact scope 中执行。目录解析优先使用
`$XWORKMATE_TASK_ARTIFACT_DIR` / `$XWORKMATE_ARTIFACT_DIRECTORY`，其次使用
本轮系统上下文里的 `artifactDirectory: ...`；只有当前 `pwd` 已经是
`.../tasks/<session>/<run>` 时才可直接使用 `.`。

```bash
cd "${XWORKMATE_TASK_ARTIFACT_DIR:-${XWORKMATE_ARTIFACT_DIRECTORY:-.}}"
python3 "${AI_VIDEO_SKILLS_HOME:-/home/ubuntu/ai-video-skills}/scripts/build_it_infra_video.py" \
  --project-dir . \
  --title "云原生 Service Mesh 网络科普视频" \
  --audio-mode edge-tts \
  --run-acceptance \
  --output-name service-mesh-video.mp4 \
  --require-task-scope \
  --session-key "$XWORKMATE_SESSION_KEY" \
  --run-id "$XWORKMATE_RUN_ID"
```

在 XWorkmate/OpenClaw 中，`.` 必须是 Bridge 预先准备的
`tasks/<safe-session-key>/<safe-run-id>` artifact scope。不能在
`owners/.../threads/<session>` 工作区直接渲染，也不能在 scope 内再创建
`task_artifacts/<session>/...` 二次嵌套目录；如果只知道
`artifactScope`，可用 `--artifact-scope "tasks/<safe-session-key>/<safe-run-id>"`
代替 `--session-key/--run-id`。

OpenClaw 任务中如果同时选择了 `it-infra-continuous-png` 和 `it-infra-evolution-video-v2`，必须按以下顺序执行：

1. 先用 `it-infra-continuous-png` 生成多张 PNG 和 manifest。
2. 再用本 skill 的 runner 读取 manifest。
3. 最后只把最终 MP4 作为 XWorkmate 制品输出。`video.config.json`、`assets/images/manifest.md`、`ffprobe.json`、`DELIVERY.md`、音频、snapshot、HTML 等中间/验收文件可以留在当前 `tasks/<session>/<run>` workspace 内供调试，但不得作为最终制品同步或报告。

## XWorkmate 制品输出约定

本 skill 的 XWorkmate 最终制品只允许包含一个 MP4：

- 最终 MP4 必须写入 `renders/<output-name>.mp4`，推荐默认 `renders/service-mesh-video.mp4`。
- 完成回复只报告这个 MP4 的相对路径和简短说明，不要列出 `video.config.json`、`ffprobe.json`、`index.html`、音频、snapshot、manifest、`DELIVERY.md` 或其他中间文件作为制品。
- 不要为了同步中间产物而把它们复制到 `deliverables/`、`reports/`、`artifacts/` 或任务 scope 根目录。
- 如果运行环境提供制品过滤、manifest 或导出列表，只把 `renders/<output-name>.mp4` 标记为 final/exportable；其他文件标记为 intermediate/debug 或完全不列入导出列表。
- 如果最终 MP4 不存在或 `ffprobe` 不通过，任务必须失败，不要用中间产物替代交付。

## Runner 合同

runner 负责：

- 解析并校验 manifest。
- 拒绝缺失图片、伪 PNG、缺失列、非法 `scan_mode`。
- 生成唯一 ID 的 `index.html`。
- 保证 scene、caption、voiceover 在各自 track 上不重叠。
- 只保留一个全局 BGM 音轨。
- 生成 `video.config.json` 和 `inspectTimes`。
- 生成 `build_ffmpeg_video.sh` 作为 HyperFrames 之外的应急合成路径；该脚本必须从 `video.config.json` 的 `sections` 动态生成章节标签、时间、active marker、总进度条和音频 delay，禁止手写固定 6 段、固定 25 秒、固定标题。
- 执行 `lint -> inspect -> snapshot -> render -> ffprobe`。

生产模式默认 `--audio-mode edge-tts`。本地测试或无网络 dry-run 可以使用 `--audio-mode tone`，但不能把 tone 输出当作正式口播成片。

## 验收标准

只有以下文件都存在，才能在 XWorkmate/OpenClaw 中报告完成；但除最终 MP4 外，这些文件只是验收证据，不是最终制品：

- `index.html`
- `video.config.json`
- `assets/images/manifest.md`
- `assets/audio/*.mp3`
- `assets/audio/bgm.wav`
- `renders/<output-name>.mp4`
- `ffprobe.json`
- `DELIVERY.md`

`ffprobe.json` 必须显示：

- 分辨率为 `1920x1080`
- 有 video stream
- 有 audio stream
- 时长接近 `video.config.json` 的 `duration`

如果 HyperFrames 或 ffprobe 任一阶段失败，只输出失败阶段和原因，不输出“完成”。

完成时的制品同步范围必须仍然只包含 `renders/<output-name>.mp4`。

## FFmpeg fallback timeline text

如果因为长版、快速修复或 HyperFrames 之外的 fallback 路径使用 FFmpeg 直接合成 timeline，不能只用 `drawbox` 绘制底部色块。必须同时绘制可见章节文字：

- 优先使用 `/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc` 或 `fc-match "Noto Sans CJK SC"` 返回的中文字体。
- 优先使用 runner 生成的 `build_ffmpeg_video.sh`，不要在任务现场临时手写 `build_long_video.sh` 或固定数组脚本。
- 每个章节 marker 必须包含时间和短标题，例如 `0:25  服务器是一座孤岛`。
- 必须保留 v1/HyperFrames 风格的底部总进度条：一条低透明底线加一条随全片时间推进的高亮进度线。
- 修复后必须从最终 MP4 抽帧确认底部 timeline 文字和总进度条都可见，不能只依赖脚本执行成功。
