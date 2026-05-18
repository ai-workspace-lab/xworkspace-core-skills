---
name: it-infra-continuous-png
version: "v1"
description: "生成 IT 基础设施系列连续风格 PNG 图片。适用于一图看懂、长图信息图、IT基础设施演进、平台工程、网络/存储/安全/监控/AI 共进化主题；支持根据用户输入图片或详细描述输出 1-N 张独立的 1024x1536 蓝白科技风竖版 PNG，并产出可供 it-infra-evolution-video skill 消费的素材 manifest。"
---

# IT 基础设施连续风格 PNG Skill

为 `it-infra-evolution-video` 提供输入素材：根据用户给定的参考图片、主题规划或详细描述，生成 `1-N` 张风格连续的竖版 PNG 长图。`N` 张图必须输出为 `N` 个独立 PNG 文件，不能合并成一张总览图、拼图、宫格、联系表或多页预览。

## 适用场景

触发词包括：

- `连续风格 PNG`
- `一图看懂长图`
- `IT 基础设施长图`
- `小红书科技长图`
- `给 it-infra-evolution-video 做素材`
- `网络/存储/安全/监控/平台工程/AI 共进化 图片`
- `根据这些图生成同风格图片`

## 默认规格

- 默认输出格式：`PNG`
- 默认尺寸：`1024x1536`，2:3 竖版长图。
- 默认数量：用户指定 `N`；未指定时按主题拆成 `1-7` 张。
- 输出颗粒度：每个主题/章节一个独立 PNG 文件；`count=7` 就必须有 7 个 PNG 文件。
- 默认语言：中文为主，英文技术词作为辅助标签。
- 默认风格：蓝白科技信息图，Apple Keynote + 企业科技宣传片 + AI Infra 系列统一视觉。
- 默认交付：
  - `assets/images/*.png`，一张图一个文件
  - `assets/images/manifest.md`
  - `prompts/image-prompts.md`
  - 每张图的主题、标题、副标题、结构块、关键词、生成提示词。

## 工作流

1. 读取用户输入：参考图、文件路径、主题清单、文字描述、目标数量和用途。
2. 抽取或套用统一风格规范，见 `references/style-spec.md`。
3. 生成系列配置，字段见 `templates/series.config.example.json`。
4. 为每张图生成独立 prompt，保证同一系列的布局、字体、色彩、底部总结条和视觉元素连续。
5. 逐张生成或编辑 PNG 图片。每次生成请求只描述一张目标图，避免模型把多张图拼进同一个画布。
6. 保存输出到用户指定目录；未指定时放在当前项目的 `assets/images/`。
7. 写 `assets/images/manifest.md`，供 `it-infra-evolution-video` 作为真实素材清单使用。

## 多图输出规则

- `count=N` 表示输出 `N` 个独立文件：`001-*.png`、`002-*.png` ... `N-*.png`。
- 严禁把多个章节合成到一张 1024x1536 画布里。
- 严禁输出 collage、contact sheet、grid、storyboard sheet、overview board、multi-panel batch preview。
- 每张 PNG 内部可以有多个信息卡片，但只能围绕一个主题/章节。
- 批量生成时，先生成 `series.config.json`，再按 `images[]` 逐项生成。
- manifest 必须逐文件记录，行数应等于输出 PNG 数量。

## 风格硬约束

- 画布必须是 `1024x1536`，除非用户明确要求其他尺寸。
- 主色必须是白、浅蓝、深蓝，少量青色、绿色、紫色、橙色用于分类强调。
- 顶部必须有系列标识胶囊，如 `一图看懂`，并保持统一位置和样式。
- 标题必须是超大深蓝中文标题，左上优先。
- 主视觉必须与主题强相关：道路、城市、服务器、盾牌、监控屏、网络地球、存储阵列、机器人/AI 芯片等。
- 信息结构必须清晰：阶段卡片、路线节点、中心图解、Checklist、核心趋势、底部总结条至少使用其中两种。
- 底部必须保留深蓝总结条，用于视频扫描时形成稳定视觉锚点。
- 不生成纯海报、纯插画、纯 UI mockup、暗色仪表盘、复杂低可读文字墙。
- 不生成多张图合并预览、宫格合集或一张图承载整个系列。
- 不加入点赞收藏 CTA，除非用户明确要求。

## 与视频 Skill 的衔接

输出给 `it-infra-evolution-video` 时，每张图必须在 manifest 中记录：

- `chapter_id`
- `title`
- `file`
- `source_type`: `generated_from_description`、`generated_from_reference_image` 或 `user_provided`
- `prompt`
- `video_usage`: 建议用于哪个视频章节
- `scan_mode`: `cover` 或 `contain`
- `safe_focus`: 建议视频双栏扫描时优先保留的主体区域

`it-infra-evolution-video` 不应重新发明这些图片的风格，只读取 manifest 并作为真实长图素材使用。

## 参考文件

- 风格规范：`references/style-spec.md`
- Prompt 模式：`references/prompt-patterns.md`
- 系列配置示例：`templates/series.config.example.json`
- manifest 模板：`templates/manifest.template.md`
