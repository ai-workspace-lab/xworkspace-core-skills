![XWorkspace Core Skills promotional poster](./assets/product.png)

[![License](https://img.shields.io/badge/license-MIT-2ea44f.svg)](./LICENSE) [![Python](https://img.shields.io/badge/Python-3.x-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/) [![HyperFrames](https://img.shields.io/badge/animation-HyperFrames-2563EB.svg)](./skills/animation) [![Agent Workflows](https://img.shields.io/badge/focus-Agent%20Workflows-7c3aed.svg)](./skills/workflows)

# XWorkspace Core Skills

一套面向 XWorkmate / OpenClaw / Codex workspace 的核心 Skill 集合。

本仓库现在使用单一 `skills/` 入口，下面按能力域分类：

- `skills/content-planning/`：选题拆解、图文连载和内容排期。
- `skills/video-production/`：AI 新闻、产品介绍和 IT 基础设施讲解视频生产。
- `skills/image-production/`：连续风格 PNG / 信息图素材生成。
- `skills/audio-production/`：视频音效、BGM 和音频素材工作流。
- `skills/animation/`：HyperFrames 动效、简笔画动画和 Anime.js 适配。
- `skills/workflows/`：跨技能编排工作流，定义阶段、下游产物、验收门和交付合同。
- `skills/workspace-core/`：从 OpenClaw/Codex runtime 同步回来的 workspace core skills。

其中 source-owned 内容生产技能基于 `HyperFrames` 工作流，目标是把“想法 -> 脚本 -> 画面 -> 音频 -> 成片”的流程沉淀成可复用方法。Workspace core skills 只作为 runtime 辅助技能归档，不与内容生产技能混放。

## 适合谁用

- 想批量做 AI 视频内容的创作者
- 想把视频生产流程标准化的团队
- 想把 Agent 工作流接入视频制作的开发者

## Skills 导航

| Skill | 说明 | 路径 |
|---|---|---|
| 选题拆解与图文连载 | 系列主题拆分、排期、图文提示词和内容规划 | `skills/content-planning/content_series_infographic/SKILL.md` |
| AI 信息差快报 | 新闻检索、素材匹配、口播字幕、视频渲染 | `skills/video-production/ai-tech-news-video/SKILL.md` |
| IT 基础设施长图讲解视频 | 基于长图素材生成 HyperFrames 讲解视频、口播、字幕和 timeline | `skills/video-production/it-infra-evolution-video/SKILL.md` |
| IT 基础设施长图讲解视频 v2 | 从 PNG manifest 强制生成配置、HTML、音频、验收和 MP4 | `skills/video-production/it-infra-evolution-video-v2/SKILL.md` |
| 产品介绍视频 | 官网信息提炼、叙事结构、成片节奏 | `skills/video-production/product-intro-video/SKILL.md` |
| IT 基础设施连续 PNG | 根据描述或参考图生成 1-N 张连续风格竖版 PNG 素材 | `skills/image-production/it-infra-continuous-png/SKILL.md` |
| 视频音效工作流 | 音效搜索、下载与合成、时间线接入 | `skills/audio-production/sound-fx-for-video/SKILL.md` |
| 简笔画动画视频 | 线稿风 + 短画面字；**主动网络搜参考图临摹**；逼真非抽象；GSAP 主时间线 + 可选 Anime.js；抽检闭环 | `skills/animation/sketch-animation-video/SKILL.md` |
| Anime.js（HyperFrames） | seek 驱动适配、`window.__hfAnime` 注册、与 GSAP 分工 | `skills/animation/animejs/SKILL.md` |
| 图文 PDF 工作流 | 主题拆章节、生成章节图、汇总排版为 PDF | `skills/workflows/content-pdf-with-images/SKILL.md` |
| 文章转图片系列 | 将文章、提纲或主题序列转成 manifest-backed 多图系列 | `skills/workflows/article-to-image-series/SKILL.md` |
| 图片系列转视频 | 从 PNG manifest 生成讲解视频并执行验收 | `skills/workflows/image-series-to-video/SKILL.md` |
| 研究到幻灯片 | 将研究资料、来源和主题 brief 转成可验证 slide deck | `skills/workflows/research-to-slide-deck/SKILL.md` |

## Workspace Core Skills

`skills/workspace-core/` 保存从 OpenClaw/Codex workspace runtime 同步回来的核心辅助技能。

- OpenClaw workspace 来源：`/home/ubuntu/.openclaw/workspace/skills`，本地路径为 `skills/workspace-core/openclaw/`。
- Codex system 来源：`/home/ubuntu/.codex/skills/.system`，本地路径为 `skills/workspace-core/codex-system/`。
- `/home/ubuntu/.agents/skills` 不纳入本仓库；它是更宽泛的用户/市场技能库，不属于 workspace core surface。

刷新时保留 `skills/workspace-core/openclaw/` 和 `skills/workspace-core/codex-system/` 两个来源边界。

## Examples

| Example | 说明 | 路径 |
|---|---|---|
| IT 基础设施演进视频模板 v1 | 轻量 HyperFrames 工程模板，只包含 HTML、配置、脚本与占位说明，不包含图片、音频、快照或渲染产物 | `example/it-infra-evolution-video/` |

## 预览

### ai-tech-news-video
![ai-tech-news-video preview](docs/assets/preview-ai-tech-news-video.gif)

### product-intro-video
![product-intro-video preview](docs/assets/preview-product-intro-video.gif)

### sound-fx-for-video
暂无预览

### sketch-animation-video
![sketch-animation-video preview](docs/assets/preview-sketch-animation-video.gif)

### animejs
暂无预览（配套 `sketch-animation-video` 与 HyperFrames 动效接入）

## 使用方式

1. 进入对应 Skill 目录并阅读 `SKILL.md`
2. 按文档准备素材、音频与脚本
3. 在项目中执行渲染与抽检流程

## Artifact Sync

任务 artifact scope 支持使用 `artifact-ignore.md` 描述无需同步的中间产物，
定义见 `skills/artifact-ignore.md`。它只适合排除 scratch/build/cache/log 等
运行过程文件，不能用于隐藏最终交付物、manifest 或失败状态。

### IT 基础设施 PNG -> 视频闭环

当一个任务同时需要 `it-infra-continuous-png` 和 `it-infra-evolution-video` 时，优先使用 v2 链路：

1. `it-infra-continuous-png` 先输出 `assets/images/*.png` 和 `assets/images/manifest.md`
2. `it-infra-evolution-video-v2` 读取 manifest，并调用 `scripts/build_it_infra_video.py`
3. 任务目录必须是 XWorkmate/OpenClaw 准备好的 `tasks/<session>/<run>` artifact scope
4. 任务目录中必须留下 `video.config.json`、`index.html`、`renders/*.mp4`、`ffprobe.json`、`DELIVERY.md`

示例：

```bash
python3 "${AI_VIDEO_SKILLS_HOME:-/home/ubuntu/ai-video-skills}/scripts/build_it_infra_video.py" \
  --project-dir /home/ubuntu/.openclaw/workspace/tasks/draft_1779524982823421-3/turn-1779685283403237342 \
  --title "云原生 Service Mesh 网络科普视频" \
  --audio-mode edge-tts \
  --run-acceptance \
  --output-name service-mesh-video.mp4 \
  --require-task-scope \
  --session-key "draft:1779524982823421-3" \
  --run-id "turn-1779685283403237342"
```

## 账号信息

- 名称：拓扑同学
- 平台：小红书
- 小红书号：`26431840972`

![小红书二维码](docs/assets/xiaohongshu-profile-qr.png)
