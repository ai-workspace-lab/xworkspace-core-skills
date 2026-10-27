# Skills

本目录是仓库唯一的 Skill 入口，共收录 **80 个 Skill**，按 10 大能力域分类管理。

> [!IMPORTANT]
> ### 核心自研验证资产 vs 上游引用技能包
> - ⭐ **核心自研资产（实践·总结·验证）**：
>   - `engineering-standards/`：包含 14 项自研工程研发与交付规范（Harness 工作流、Issue/PR 溯源、四仓执行归属、多环境发布、GitOps 等）。
>   - `operations-management/`：包含 10 项自研运维标准（真实灾备演练、统一可观测性架构、故障变更管理、Vault 凭据零落盘、DNS 边缘平滑切流、SLO 告警等）。
> - 📦 **上游引用与镜像生态**：其余分类（多模态内容生产链路、Marketplace 市场技能、Workspace Core 运行时镜像、开源 Vendored 技能）均为引用或镜像自上游社区与运行时的生态包。

| Category | 性质归属 | 用途说明 |
|---|---|---|
| ⭐ `engineering-standards/` | **作者实战验证核心** | 研发交付规范、发布治理、多环境隔离、代际升级与合规标准（14 项规约） |
| ⭐ `operations-management/` | **作者实战验证核心** | 容灾备份、变更管理、Vault 凭据与 OIDC 治理、网络边缘与 SLO（10 项标准，含系统/DB 三权分立、统一可观测性架构） |
| `content-planning/` | 上游引用（HyperFrames） | 选题拆解、图文连载、内容排期 |
| `video-production/` | 上游引用（HyperFrames） | AI 新闻快报、长图讲解视频、产品介绍视频与爆款视频逐镜理解 |
| `image-production/` | 上游引用（HyperFrames） | 连续风格科技长图 PNG / 信息图素材生成 |
| `audio-production/` | 上游引用（Web Audio / SFX） | 视频音效（SFX）、Web Audio API 合成、BGM 与时间线集成 |
| `animation/` | 上游引用（GSAP / Anime.js） | HyperFrames 动效、简笔画手绘动画、Anime.js 适配 |
| `workflows/` | 上游引用（HyperFrames） | 跨技能编排工作流、阶段验收、交付合同 |
| `marketplace/` | 上游引用（市场与社区） | Agent 市场精选技能（Office 文档处理、安全审查、搜索与 Wan 多模态） |
| `workspace-core/` | 上游镜像（运行时归档） | OpenClaw / Codex runtime 核心辅助技能（详见 `workspace-core/README.md`） |

另有两个外部标准来源 Skill 以整仓 vendored 形式直接放在本目录下（锁定 commit 引入）：

- `image-svg-pptx-pro-skill/` — 图片 -> SVG -> 可编辑 PPTX（来源：`kongzhecn/image-svg-pptx-pro-skill`）
- `xiaobei-skill-image-to-vba/` — 图片 -> VBA Office Shapes 重建（来源：`xiao24bei/xiaobei-skill-image-to-vba`）

## Artifact Sync

- [`artifact-ignore.md`](artifact-ignore.md) 定义当前任务 artifact scope 中哪些中间产物可以不进入同步/导出结果。
- 该规则只用于跳过 scratch/build/cache/log 等中间文件；最终交付物、manifest、`DELIVERY.md` 不能通过 ignore 规避缺失或失败。
- 长任务完成后清理软件会话缓存和临时目录时，只清理 `.cache/`、`tmp/`、`scratch/`、浏览器截图缓存、模型下载缓存索引和渲染中间目录；不要删除当前 task scope 内的 `reports/`、`exports/`、`renders/`、`assets/images/`、manifest 或 `DELIVERY.md`。

## 功能泳道发布（新增规范）

- 工程入口：[feature-lane-release-workflow](engineering-standards/feature-lane-release-workflow/SKILL.md)，定义关联 PR、固定候选、SIT/UAT、组合验证与合并。
- 运维入口：[功能泳道生命周期](operations-management/capacity-cost-and-resource-lifecycle/references/feature-lane-lifecycle.md)，定义资源隔离、租约、证据归档及回收。

该规范已形成可复用契约，实际部署与业务验收尚未执行。
