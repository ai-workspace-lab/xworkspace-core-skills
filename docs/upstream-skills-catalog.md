# 上游引用与镜像生态技能包清单（Upstream Skills Catalog）

本仓库作为统一 Workspace 的分发与使用聚合层，除了作者自研验证的工程规范与运维标准外，还收录并聚合了以下引用自上游开源社区与官方运行时的生态技能包。

---

## 1. 内容策划与多模态创作（18 Skills，基于 HyperFrames 工业化上游）

| 链路环节 | 上游定位 / 机制 | Skill 标识与名称 | 核心功能与输出 | 本地路径 |
|---|---|---|---|---|
| **策划拆解** | HyperFrames 策划上游 | `content_series_infographic` 选题拆解与图文连载 | 连载排期规划、图文提示词、长文大纲编排（≤10张/批） | [`skills/content-planning/content_series_infographic/SKILL.md`](../skills/content-planning/content_series_infographic/SKILL.md) |
| **视频生产** | HyperFrames 视频生成上游 | `ai-tech-news-video` AI 信息差快报 | 资讯检索、素材下载、edge-tts 口播、视频自动化渲染 | [`skills/video-production/ai-tech-news-video/SKILL.md`](../skills/video-production/ai-tech-news-video/SKILL.md) |
| **视频生产** | HyperFrames 视频生成上游 | `it-infra-evolution-video` IT 基础设施长图视频 v1 | 基于真实信息图生成 1080p 视频、逐句字幕、BGM与时间线 | [`skills/video-production/it-infra-evolution-video/SKILL.md`](../skills/video-production/it-infra-evolution-video/SKILL.md) |
| **视频生产** | HyperFrames 视频生成上游 | `it-infra-evolution-video-v2` IT 基础设施长图视频 v2 | 基于 PNG manifest 驱动配置、HTML、音频、验收和 MP4 成片 | [`skills/video-production/it-infra-evolution-video-v2/SKILL.md`](../skills/video-production/it-infra-evolution-video-v2/SKILL.md) |
| **视频生产** | HyperFrames 视频生成上游 | `product-intro-video` 产品介绍视频 | 官网提炼、VL 视觉校验、叙事结构与高品质渲染出片 | [`skills/video-production/product-intro-video/SKILL.md`](../skills/video-production/product-intro-video/SKILL.md) |
| **视频理解** | 视觉分析多模态上游 | `video-understanding` 短视频理解与镜头拆解 | TikTok/抖音短视频逐镜识别、运镜与节奏，输出 beat sheet | [`skills/video-production/video-understanding/SKILL.md`](../skills/video-production/video-understanding/SKILL.md) |
| **素材生成** | 连续风格图像上游 | `it-infra-continuous-png` IT 基础设施连续 PNG | 生成 1-N 张 1024x1536 科技风格竖版长图及 manifest.md | [`skills/image-production/it-infra-continuous-png/SKILL.md`](../skills/image-production/it-infra-continuous-png/SKILL.md) |
| **音频处理** | Web Audio API / SFX 上游 | `sound-fx-for-video` 视频音效工作流 | 免费音效下载、Web Audio API 程序化合成与时间线集成 | [`skills/audio-production/sound-fx-for-video/SKILL.md`](../skills/audio-production/sound-fx-for-video/SKILL.md) |
| **动画动效** | GSAP 动效上游 | `sketch-animation-video` 简笔画动画视频 | 线稿风 + 短画面字；网络搜图临摹；GSAP 主时间线动画 | [`skills/animation/sketch-animation-video/SKILL.md`](../skills/animation/sketch-animation-video/SKILL.md) |
| **动画动效** | Anime.js 适配上游 | `animejs` Anime.js for HyperFrames | seek 驱动适配、`window.__hfAnime` 注册，微动效集成 | [`skills/animation/animejs/SKILL.md`](../skills/animation/animejs/SKILL.md) |
| **组合工作流** | 文档生成工作流 | `content-pdf-with-images` 图文 PDF 工作流 | 主题拆章节、自动化为每章生成配图，汇总排版为真实 PDF | [`skills/workflows/content-pdf-with-images/SKILL.md`](../skills/workflows/content-pdf-with-images/SKILL.md) |
| **组合工作流** | 图像矩阵工作流 | `article-to-image-series` 文章转图片系列 | 将文章、提纲或主题序列转成 manifest-backed 多图系列 | [`skills/workflows/article-to-image-series/SKILL.md`](../skills/workflows/article-to-image-series/SKILL.md) |
| **组合工作流** | 视频编排工作流 | `image-series-to-video` 图片系列转视频 | 从 PNG manifest 编排生成完整讲解视频并执行自动化质量验收 | [`skills/workflows/image-series-to-video/SKILL.md`](../skills/workflows/image-series-to-video/SKILL.md) |
| **组合工作流** | 演示文稿工作流 | `research-to-slide-deck` 研究到幻灯片 | 将研究资料、权威来源与主题 brief 转成可验证 slide deck | [`skills/workflows/research-to-slide-deck/SKILL.md`](../skills/workflows/research-to-slide-deck/SKILL.md) |
| **组合工作流** | 资讯摘要工作流 | `ai-news-md-digest` AI 资讯 Markdown 快报 | 自动化采集最新 AI / Agent 资讯并持久化输出为 Markdown | [`skills/workflows/ai-news-md-digest/SKILL.md`](../skills/workflows/ai-news-md-digest/SKILL.md) |
| **组合工作流** | 矩阵分发工作流 | `evolutionary-social-copy-pack` 演进主线软文矩阵 | 依据演进主线批量输出公众号、小红书、X、今日头条文案包 | [`skills/workflows/evolutionary-social-copy-pack/SKILL.md`](../skills/workflows/evolutionary-social-copy-pack/SKILL.md) |
| **社区 Vendored** | 开源仓库 `kongzhecn` | `image-svg-pptx-pro` 图片转可编辑 PPTX | 截图/学术图 -> SVG 矢量层 -> 原生可编辑 PPTX 重绘 | [`skills/image-svg-pptx-pro-skill/SKILL.md`](../skills/image-svg-pptx-pro-skill/SKILL.md) |
| **社区 Vendored** | 开源仓库 `xiao24bei` | `xiaobei-skill-image-to-vba` 小北 Image to VBA | 截图 -> 原生 VBA 代码 -> Office 形状 1:1 重绘与导出 | [`skills/xiaobei-skill-image-to-vba/skills/xiaobei-skill-image-to-vba/SKILL.md`](../skills/xiaobei-skill-image-to-vba/skills/xiaobei-skill-image-to-vba/SKILL.md) |

---

## 2. Marketplace 市场精选生态包（15 Skills，引用自社区与市场）

| 能力维度 | 上游分类 | Skill 标识与名称 | 核心功能与解决问题 | 本地路径 |
|---|---|---|---|---|
| **网络检索** | 联网工具 | `autoglm-websearch` AutoGLM 网页搜索 | 基于 AutoGLM Web Search 本地服务的高性能网络信息检索 | [`skills/marketplace/autoglm-websearch/SKILL.md`](../skills/marketplace/autoglm-websearch/SKILL.md) |
| **动态监测** | 自动化 CLI | `blogwatcher` Blogwatcher | 使用命令行持续监控技术博客、专栏与 RSS/Atom feeds 变更 | [`skills/marketplace/blogwatcher/SKILL.md`](../skills/marketplace/blogwatcher/SKILL.md) |
| **环境交互** | 浏览器工具 | `browser-automation` 浏览器自动化 | 基于 agent-browser 无头浏览器交互，支持点击、填表与截图 | [`skills/marketplace/browser-automation/SKILL.md`](../skills/marketplace/browser-automation/SKILL.md) |
| **文档处理** | Office 文档 | `docx` Word 文档处理（DOCX） | Word (.docx) 文档的高保真生成、排版、表格与修订跟踪 | [`skills/marketplace/docx/SKILL.md`](../skills/marketplace/docx/SKILL.md) |
| **技能发现** | 生态工具 | `find-skills` 技能发现指南 | 根据用户任务意图从生态中快速搜索、评估和匹配对应技能 | [`skills/marketplace/find-skills/SKILL.md`](../skills/marketplace/find-skills/SKILL.md) |
| **多模态生图** | 图像生成 | `image-cog` CellCog 图像生成 | CellCog 生图、图生图、角色一致性生成与电商图片合成 | [`skills/marketplace/image-cog/SKILL.md`](../skills/marketplace/image-cog/SKILL.md) |
| **图像加工** | 图片工具 | `image-resizer` 智能图片缩放压缩 | 按分辨率宽高、等比缩放或体积上限批量智能压缩图片 | [`skills/marketplace/image-resizer/SKILL.md`](../skills/marketplace/image-resizer/SKILL.md) |
| **文档处理** | Office 文档 | `pdf` PDF 综合工具箱 | 提取纯文本与复杂表格、合并拆分文档、表单填写与排版 | [`skills/marketplace/pdf/SKILL.md`](../skills/marketplace/pdf/SKILL.md) |
| **文档处理** | Office 文档 | `pptx` PowerPoint（PPTX） | 结构化幻灯片生成、版面母版应用、图表数据与视觉验收 | [`skills/marketplace/pptx/SKILL.md`](../skills/marketplace/pptx/SKILL.md) |
| **自愈进化学** | Agent 核心 | `self-improving-1.1.3` 自我进化学型 Agent | 具备自我反思 (Self-reflection)、主动挑错与持久化记忆学习 | [`skills/marketplace/self-improving-1.1.3/SKILL.md`](../skills/marketplace/self-improving-1.1.3/SKILL.md) |
| **安全审计** | 安全准入 | `skill-vetter` Skill Vetter 技能审查 | 针对第三方开源 Agent Skill 的权限范围、安全性与合规性评估 | [`skills/marketplace/skill-vetter/SKILL.md`](../skills/marketplace/skill-vetter/SKILL.md) |
| **安全审计** | 静态分析 | `skills-security-check` 技能安全静态扫描 | 静态扫描第三方 Agent 技能源码，防范后门、越权与敏感信息泄露 | [`skills/marketplace/skills-security-check/SKILL.md`](../skills/marketplace/skills-security-check/SKILL.md) |
| **音视频工具** | 翻译配音 | `video-translator` 实时视频翻译与配音 | 视频/链接人声字幕听翻、时间戳对齐与多语言语音配音出片 | [`skills/marketplace/video-translator/SKILL.md`](../skills/marketplace/video-translator/SKILL.md) |
| **多模态生片** | 阿里万象 | `wan-image-video-gen-edit` 万象 Wan 模型 | 通义万象 Wan 2.6：文生图、图编辑、文生视频、图生视频 | [`skills/marketplace/wan-image-video-generation-editting/SKILL.md`](../skills/marketplace/wan-image-video-generation-editting/SKILL.md) |
| **文档处理** | Office 文档 | `xlsx` Excel 电子表格（XLSX） | 读写 Excel (.xlsx) 工作簿，支持公式计算、复杂样式与模板保留 | [`skills/marketplace/xlsx/SKILL.md`](../skills/marketplace/xlsx/SKILL.md) |

---

## 3. Workspace Core 运行时镜像包（24 Skills，从 OpenClaw/Codex 归档）

作为底层运行时通用环境的镜像基座，详细来源与同步机制见 [`skills/workspace-core/README.md`](../skills/workspace-core/README.md)：

| 运行时归属 | 来源环境路径 | 包含 Skill 标识清单 | 角色与功能说明 |
|---|---|---|---|
| **Codex System** (5 Skills) | `/home/ubuntu/.codex/skills/.system` | `imagegen`<br/>`openai-docs`<br/>`plugin-creator`<br/>`skill-creator`<br/>`skill-installer` | Codex 官方运行时捆绑的基础核心能力：官方生图、最新 OpenAI 文档查询、插件工程脚手架、技能编写与安装工具 |
| **OpenClaw Workspace** (19 Skills) | `/home/ubuntu/.openclaw/workspace/skills` | `browser-automation`<br/>`cron-helper`<br/>`excel-xlsx`<br/>`find-skills-skill`<br/>`hermes-learning-loop`<br/>`image-cog`<br/>`image-resizer`<br/>`pdf`<br/>`powerpoint-pptx`<br/>`qmd`<br/>`remote-desktop`<br/>`self-improving`<br/>`skylv-hermes-agent-integration`<br/>`tiangong-notebooklm-cli`<br/>`video-translator`<br/>`virtual-remote-desktop`<br/>`wan-image-video-generation-editting`<br/>`web-search`<br/>`word-docx` | OpenClaw 运行时工作区默认配置的系统级辅助技能：涵盖文档读写、远程桌面/虚拟桌面交互、周期性定时任务、知识库秒级检索、模型调用与自我学习机制 |
