# Skills

本目录是仓库唯一的 Skill 入口，按能力域分类：

| Category | 用途 |
|---|---|
| `content-planning/` | 选题拆解、图文连载、内容排期 |
| `video-production/` | AI 新闻、产品介绍、IT 基础设施讲解视频 |
| `image-production/` | 连续风格 PNG / 信息图素材 |
| `audio-production/` | SFX、BGM、音频素材工作流 |
| `animation/` | HyperFrames 动效、简笔画动画、Anime.js 适配 |
| `workflows/` | 跨技能编排工作流、阶段验收、交付合同 |
| `workspace-core/` | OpenClaw/Codex runtime core skills |

Source-owned 内容生产技能和 runtime 同步技能使用目录边界隔离，不再使用并列顶层 `workspace-core-skills/`。

## Artifact Sync

- [`artifact-ignore.md`](artifact-ignore.md) 定义当前任务 artifact scope 中哪些中间产物可以不进入同步/导出结果。
- 该规则只用于跳过 scratch/build/cache/log 等中间文件；最终交付物、manifest、`DELIVERY.md` 不能通过 ignore 规避缺失或失败。
- 长任务完成后清理软件会话缓存和临时目录时，只清理 `.cache/`、`tmp/`、`scratch/`、浏览器截图缓存、模型下载缓存索引和渲染中间目录；不要删除当前 task scope 内的 `reports/`、`exports/`、`renders/`、`assets/images/`、manifest 或 `DELIVERY.md`。
