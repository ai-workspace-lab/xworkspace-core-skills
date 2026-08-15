---
name: video-understanding
version: "v1"
description: "拉取一条 TikTok / 抖音短视频，逐镜识别画面内容、镜头运动、转场与音画节奏，产出带时间戳的脚本与高光节点时间轴（beat sheet）。只做理解，不做生成；供 XWorkmate「爆款视频复刻」插件的 ingest / beat-sheet 步骤消费。触发：拆解爆款视频、beat sheet、逐镜理解、视频脚本提取、竞品视频分析。"
---

# 短视频理解（video-understanding）

拉取一条公开短视频，把它变成一份结构化文档：**在第几秒发生了什么、镜头怎么运动、为什么这个节点有效**。
这份文档是后续「照着结构改写成别的商品」的唯一输入——本 skill 本身不生成任何画面、不改写脚本、
不合成视频，那些是消费方（例如 `builtin.ecommerce.video` 插件）的下一步。

## 边界（先说清楚不做什么）

- **只输出结构化描述，不输出可再分发的原始素材。** 产物是文字时间轴与关键帧截图（仅用于本地 VL 识别参考），
  不产出可直接使用的完整原片文件、不产出原片音轨的可用副本、不把源视频转存到会被当作交付物导出的目录。
- **不做批量爬取、不做账号内容采集。** 每次调用只处理用户显式提供的一个链接，用于「照着这条视频的结构改写成
  我自己的内容」这一具体需求，不用于抓取他人账号的内容库。
- **消费方必须只复刻结构，不得复制画面或音轨。** 这是下游插件（`docs/plans/2026-08-03-ecommerce-plugin-group.md`
  §2.3）的合规要求，本 skill 的输出格式（纯文字时间轴 + 极少数缩略截图）是为了让这条约束在事实上可执行——
  下游拿到的东西本身就不含可复用的原始素材。

如果任务要求"直接把这条视频转发/搬运/去水印保存"，这不是本 skill 的用途，应当拒绝。

## 前置条件

- 一个公开可访问的 TikTok 或抖音视频链接。私密/需要登录态的内容不处理。
- 运行环境已安装 `yt-dlp` 与 `ffmpeg`。缺一即失败，不要退化成"凭标题/封面猜内容"。

```bash
yt-dlp --version && ffmpeg -version >/dev/null && echo ok
```

## 标准调用

在 Bridge 预先准备的当前任务 artifact scope 中执行，目录解析规则与本仓库其它 video-production
skill 一致：优先 `$XWORKMATE_TASK_ARTIFACT_DIR` / `$XWORKMATE_ARTIFACT_DIRECTORY`，其次系统上下文里的
`artifactDirectory: ...`，只有当前 `pwd` 已经是 `.../tasks/<session>/<run>` 时才直接用 `.`。

```bash
cd "${XWORKMATE_TASK_ARTIFACT_DIR:-${XWORKMATE_ARTIFACT_DIRECTORY:-.}}"
mkdir -p analysis/frames

python3 "$(dirname "$0")/scripts/analyze_video.py" \
  --url "<视频链接>" \
  --workdir analysis \
  --max-frames 24 \
  --min-scene-diff 0.35
```

`analyze_video.py` 做三件事：

1. 用 `yt-dlp` 下载视频到 `analysis/source.mp4`（仅本地临时使用，不作为最终制品）。
2. 用 `ffmpeg` 场景检测抽取关键帧到 `analysis/frames/shot-XXX.jpg`（默认按画面切换抽帧，
   而不是固定间隔抽帧，这样一个镜头只出现一张代表帧）。
3. 输出 `analysis/shots.json`：每个镜头的起止时间、代表帧路径、`ffprobe` 得到的基础信息
   （分辨率、总时长、是否有音轨）。

脚本不做画面语义识别——那一步必须由 Agent 自己用多模态能力逐帧看图完成（见下一节），
不要用脚本猜测画面内容。

## 逐镜理解与脚本产出

拿到 `analysis/shots.json` 后，Agent 依次对每个 `frames/shot-XXX.jpg` 做视觉识别，
补全画面内容、镜头运动（固定/推/拉/摇/跟随/手持晃动）、转场方式（硬切/叠化/擦除/匹配剪辑）。
同时结合音频（若可听，转写或概括口播/字幕内容）还原节奏。

产出两份文件，schema 见 [references/beat-sheet-schema.md](references/beat-sheet-schema.md)：

- `analysis/script.md`：完整脚本，逐镜列出时间区间、画面描述、口播/字幕文字、镜头运动、转场。
- `analysis/beat-sheet.md`：高光节点时间轴——钩子、痛点、卖点展示、转折、行动号召分别落在
  第几秒，以及**每个节点为什么有效**（这一条是后续改写时唯一有价值的部分，不能省略）。

## 验收标准

- `analysis/shots.json` 存在，且每个镜头都有 `start`、`end`、`frame` 三个字段。
- `analysis/script.md` 覆盖了 `shots.json` 里的每一个镜头，没有跳过。
- `analysis/beat-sheet.md` 至少标出钩子（通常在前 3 秒）与结尾的行动号召/收尾节点。
- `analysis/source.mp4` 与 `analysis/frames/*.jpg` 只作为中间产物，最终报告与制品同步范围
  只包含 `script.md` 与 `beat-sheet.md`。这一条与本仓库其它 video-production skill
  的「只导出终产物、中间文件仅供调试」约定一致。

拉取失败（链接失效、地区限制、需要登录）时，直接报告失败原因，要求用户改为直接上传视频文件，
不要用标题或封面图编造画面内容。

## 输出契约（下游怎么用）

`builtin.ecommerce.video` 插件的 `ingest` 步骤消费本 skill 的产物：`script.md` 进入
`beat-sheet` 步骤，`beat-sheet.md` 直接作为该插件下一步 `rewrite` 的输入锚点。
下游改写时只能引用节点结构（时长分配、节点顺序、节点作用），不得引用 `script.md`
里的具体台词或画面描述作为自己的输出内容。
