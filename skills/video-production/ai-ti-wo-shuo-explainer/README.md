# AI替我说 · Grok 图生视频工作流模版

新一期只需要：**一张产品页截图 + 一个 shots.json**。

## 目录
```
grok-i2v-template/
  make_refs.py    # 第 1 步：打码 + 按镜头裁图 → 9:16 白底参考图，并把 GenerateVideo 调用参数写回 shots.json
  compose.sh/.py  # 第 3 步：TTS 配音 + Grok 片段/兜底推拉 + 字幕 + 头像徽章 + 轻音乐 → 成片
  samples/xworkmate-matrix/   # 样片（XWorkmate 产品矩阵）
    source.png  shots.json  refs/  clips/  review/  build/
    AI替我说-XWorkmate产品矩阵.mp4  voice.mp3  cover.png
```

## shots.json 字段
| 字段 | 说明 |
|---|---|
| title / tags / slug / output | 标题（`AI替我说 · 短标题`）、话题、文件名 |
| source | 截图文件名（放在本期目录） |
| masks[] | `{box:[x0,y0,x1,y1], mode:"cover"/"blur", why}`，**原图像素坐标**；域名、邮箱、二维码、价格一律在这里遮掉 |
| voice / rate | edge-tts 音色（zh-CN-YunxiNeural）与语速（样片 +22%） |
| avatar | 用户真实头像（圆形 PNG），只做徽章，不生成人脸、不对口型 |
| music / music_db | `"pad"` 自动合成柔和和弦铺底，`"none"` 关闭；音量 dB |
| grok_defaults | aspect_ratio 9:16、resolution 720p、prompt_suffix（保持 UI 文字不变/无人物/无新 logo/白底简洁） |
| shots[].id / duration | 镜头号、计划时长（实际时长 = max(计划, 配音+0.35s)） |
| shots[].crop | 一个框，或多个框（纵向堆叠，适合横向很宽的区域） |
| shots[].vo | 口播句，同时作为字幕 |
| shots[].grok_prompt | 本镜运动描述（会自动拼上 prompt_suffix） |
| shots[].grok_call | make_refs.py 自动生成：GenerateVideo 的完整参数 |
| shots[].clip / use | Grok 片段路径；`grok` 用片段，`fallback` 用静帧 Ken Burns |
| shots[].review_note | 抽帧审核结论 |

## 步骤
1. 建目录 `samples/<slug>/`，放 `source.png`，写 `shots.json`（复制样片改即可）。坐标用原图像素。
2. `python3 make_refs.py samples/<slug>` → 生成 `refs/masked-source.png` 与 `refs/shot-XX.png`。**先打开 masked-source.png 确认域名/邮箱已遮住。**
3. 逐镜调用 Grok（GenerateVideo，cursor 命名空间），参数直接取 `shots[].grok_call`：
   `image_path`=refs/shot-XX.png（首帧）、`prompt`、`duration`（1–15s，建议比镜头长 1–2s）、`aspect_ratio`="9:16"、`resolution`="720p"、`filename`。
   8 个镜头可并行调用。返回的 mp4 复制为 `clips/grok-shot-XX.mp4`。
4. **抽帧审核**：每个片段取首/中/尾三帧（见样片 review/*-sheet.png），检查：文字乱码、凭空出现的 logo/箭头/人物、残留域名邮箱。不合格 → 改 prompt 重生成，或把 `use` 设为 `fallback`。
5. `./compose.sh samples/<slug>` → 成片（1080x1920）、`voice.mp3`、`cover.png`、`build/timeline.json`。
   片段短于镜头：先放慢（最多 1.5x）再定格末帧；`fallback` 镜头用静帧缓推。
6. 再抽帧审核成片（review/final/）。不上传、不发布，交给用户确认。

## 规则
- 不 AI 生成用户本人形象、不对口型；头像只用真实照片。
- 画面不出现网址、二维码、价格；不编造产品事实，口播只用产品页上的说法。
- Grok 擅长"已有画面轻微动起来"，对密集小字 UI（如整个应用窗口、长流程条）容易重绘出乱码 —— 这类镜头直接用 fallback 更稳。

## 小技巧：首尾帧锁定
Grok 片段里文字被光效盖住或消失时，把 `last_frame_path` 设为和 `image_path` 同一张参考图再生成一次，画面会回到原图，内容不会漂。

## 动画科普模式（看看知识怎么变成动画）

不靠截图/Grok，用 `anim.py` 逐帧手绘示意动画讲清"一个机制怎么运作"。示例：`samples/grokbot-desktop-anim/`。

**anim.py 原语**：`ease/seg/mix/lerp`（时间与颜色插值）、`text`、`box`（缩放+淡入）、`arrow`（从起点生长）、`flow`（光点沿折线流动）、`badge`（步骤编号）、`pulse`（扩散波纹）、`cloud`、`monitor`、`chat`（气泡）、`typing`（终端逐字）、`paste`（淡入真实素材，如截图/图标）、`render(scene,L,out,still)`（ffmpeg 出片并存末帧）。

**做一期新主题只需两件事**：
1. `scenes.py`：每个镜头一个函数 `def sX(d, t, L)`（d=ImageDraw，t=秒，L=镜头时长），内容画在安全区 y 260–1330（标题栏 110–200、字幕 1390 起、头像 1700 不要碰）。
2. `shots.json`：`"mode":"anim"`，每个 shot 写 `"use":"anim","scene":"函数名","vo":"旁白"`，可选 `cover_ref`。镜头时长自动取 max(duration, 旁白+0.35s)。

**脚本结构**：钩子问题 → 类比（"就像……"）→ 3–4 个机制步骤（带 badge 编号）→ 一句话总结 → 结尾提问。只讲已证实的事实；字幕≤2 行（约 18 字/行，`wrap()` 已防标点打头、英文断词）。

运行：`./compose.sh samples/<topic>`，然后抽帧拼图逐帧审查。
