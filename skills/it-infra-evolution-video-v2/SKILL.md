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

在当前任务工作目录或视频项目目录执行：

```bash
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
`owners/.../threads/<session>` 工作区直接渲染；如果只知道
`artifactScope`，可用 `--artifact-scope "tasks/<safe-session-key>/<safe-run-id>"`
代替 `--session-key/--run-id`。

OpenClaw 任务中如果同时选择了 `it-infra-continuous-png` 和 `it-infra-evolution-video-v2`，必须按以下顺序执行：

1. 先用 `it-infra-continuous-png` 生成多张 PNG 和 manifest。
2. 再用本 skill 的 runner 读取 manifest。
3. 最后把 `renders/service-mesh-video.mp4`、`video.config.json`、`assets/images/manifest.md`、`ffprobe.json`、`DELIVERY.md` 留在当前 `tasks/<session>/<run>` workspace。

## Runner 合同

runner 负责：

- 解析并校验 manifest。
- 拒绝缺失图片、伪 PNG、缺失列、非法 `scan_mode`。
- 生成唯一 ID 的 `index.html`。
- 保证 scene、caption、voiceover 在各自 track 上不重叠。
- 只保留一个全局 BGM 音轨。
- 生成 `video.config.json` 和 `inspectTimes`。
- 执行 `lint -> inspect -> snapshot -> render -> ffprobe`。

生产模式默认 `--audio-mode edge-tts`。本地测试或无网络 dry-run 可以使用 `--audio-mode tone`，但不能把 tone 输出当作正式口播成片。

## 验收标准

只有以下文件都存在，才能在 XWorkmate/OpenClaw 中报告完成：

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
