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

主题或章节序列由用户动态输入指定。不要强加固定的章节数或主题（如固定的 7 阶段安全演进），应完全根据用户的实际需求或上下文输入进行推演和拆分。

## XWorkmate/OpenClaw 交付目录

通过 OpenClaw 调用 Codex CLI/codecli 执行时，最终文件必须写入当前 run
的 prepared artifact scope。Bridge 会在本轮系统上下文中提供
`artifactDirectory` / `artifactScope`，并在可用时等价映射为环境变量。
目录解析优先级：

1. `$XWORKMATE_TASK_ARTIFACT_DIR`
2. `$XWORKMATE_ARTIFACT_DIRECTORY`
3. 本轮系统上下文里的 `artifactDirectory: ...`
4. 当前工作目录本身已经是形如 `.../tasks/<session>/<run>` 的目录

如果以上四项都不存在，必须先说明“缺少 XWorkmate prepared artifact
scope”，不要声称已经完成文件交付。

执行要求：

- 先确认目标目录是当前 run 的 `tasks/<session>/<run>` scope；不要使用
  `/owners/.../threads/<session>` 作为最终交付目录。
- `cd` 到选定目录，或所有写入都使用选定目录的绝对路径。
- 在选定目录下直接创建 `assets/images/` 和 `prompts/`。
- 禁止在选定目录内再创建 `task_artifacts/<session>/...`、`tasks/.../tasks/...`
  或其他二次嵌套导出目录。
- Codex 产图如果先落在 `~/.codex/generated_images/...`，必须复制到
  `assets/images/*.png`，不能只引用缓存路径。
- `assets/images/manifest.md`、`prompts/image-prompts.md` 和
  `series.config.json` 必须与 PNG 留在同一个 artifact scope。
- 完成前必须确认每个 PNG 都是非空文件，manifest 的文件数量与 PNG 数量一致。
- 最终回复列出 artifact scope 内的相对路径。不要把正文中的文件清单当作
  XWorkmate artifact 面板交付。

## 工作流

1. 读取用户输入：参考图、文件路径、主题清单、文字描述、目标数量和用途。
2. 抽取或套用统一风格规范，见 `references/style-spec.md`。
3. 生成系列配置，字段见 `templates/series.config.example.json`。
4. 为每张图生成独立 prompt，保证同一系列的布局、字体、色彩、底部总结条和视觉元素连续。
5. 逐张生成或编辑 PNG 图片。每次生成请求只描述一张目标图，避免模型把多张图拼进同一个画布。
6. 保存输出到选定 artifact scope 的 `assets/images/`；用户指定额外目录时，也复制一份到 artifact scope。
7. 写 artifact scope 下的 `assets/images/manifest.md`，供 `it-infra-evolution-video` 作为真实素材清单使用。
8. 写 artifact scope 下的 `prompts/image-prompts.md` 和 `series.config.json`。

## 多图输出规则

- `count=N` 表示输出 `N` 个独立文件：`001-*.png`、`002-*.png` ... `N-*.png`。如果用户提供了明确的演进主线，则应按各个阶段分别输出。
- 严禁把多个章节合成到一张 1024x1536 画布里。
- 严禁输出 collage、contact sheet、grid、storyboard sheet、overview board、multi-panel batch preview。
- 每张 PNG 内部可以有多个信息卡片，但只能围绕一个主题/章节。
- 批量生成时，先生成 `series.config.json`，再按 `images[]` 逐项生成。
- manifest 必须逐文件记录，行数应等于输出 PNG 数量。
- manifest 中的 `file` 必须是 artifact scope 内的相对路径，例如
  `assets/images/001-local-permission.png`。

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

当任务还选择了 `it-infra-evolution-video-v2` 时，本 skill 完成后必须停在清晰的交接点：

1. 确认 `assets/images/*.png` 的数量与 manifest 数据行数量一致。
2. 确认每个 `file` 指向真实 PNG 文件，而不是 SVG、空文件或占位路径。
3. 将下一步命令写给视频 skill：

```bash
python3 "${AI_VIDEO_SKILLS_HOME:-/home/ubuntu/ai-video-skills}/scripts/build_it_infra_video.py" \
  --project-dir . \
  --title "<用户主题>" \
  --audio-mode edge-tts \
  --run-acceptance \
  --output-name "<topic-slug>.mp4" \
  --require-task-scope \
  --session-key "$XWORKMATE_SESSION_KEY" \
  --run-id "$XWORKMATE_RUN_ID"
```

交接目录必须是 XWorkmate/OpenClaw 当前任务的
`tasks/<safe-session-key>/<safe-run-id>` artifact scope。不要把 manifest
和 PNG 留在 `owners/.../threads/<session>` 后再渲染；否则 Bridge 的当前 run
artifact 面板可能无法稳定收敛到同一 scope。

不要在本 skill 中生成 `index.html`、`video.config.json` 或 MP4；这些是视频 skill 的职责。

## 参考文件

- 风格规范：`references/style-spec.md`
- Prompt 模式：`references/prompt-patterns.md`
- 系列配置示例：`templates/series.config.example.json`
- manifest 模板：`templates/manifest.template.md`
