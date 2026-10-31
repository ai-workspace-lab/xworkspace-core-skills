---
name: swimlane-video
description: >-
  Use when someone wants a short static hand-drawn swimlane flowchart video
  (workflow explainer, XHS/X/Douyin style): portrait 9:16 or landscape or custom
  size, light-to-dark cut, background music by default, optional icons/outro.
---
# 手绘泳道图工作流视频

风格：一张静态的手绘风（Excalidraw 感）自上而下泳道图。顶部是标题和副标题，下面是触发节点，再往下是若干条彩色泳道（通常 3 条）。节点有卡片和菱形判断两种，判断分支标 Yes/No，回路用红色回箭头，卡片可配小图标。画面不动，按时间从浅色硬切到深色（默认各 18 秒），最后是署名卡（默认 2 秒）。没有旁白，**默认带背景音乐**。

## 工具
- 共享机器上的生成器：`/workspace/workflow-videos/`；可移植的包：`/workspace/workflow-videos/dist/swimlane-video.tar.gz`（解压后得到 `swimlane-video/`）。
- 依赖：在 Debian/Ubuntu 上运行 `./install.sh`，会装好 ffmpeg、fonts-noto-cjk、Pillow 和 numpy（合成配乐要用；scipy 可选，用于低通滤波）。
- 每个字段的说明都在 `schema.md`，最小示例在 `episodes/_template.json`。

## 步骤
1. 先把工作流拆成分镜：标题、副标题、触发节点、每条泳道的名字和节点（卡片或判断）、回路、备注、署名。只写真实的事实，不要编。如果是帮别人做，先把分镜发给对方确认。
2. 复制 `episodes/_template.json`，写成这一集的配置：
   - `canvas`：`portrait`（1080x1920，默认）、`landscape`（1920x1080），或 `{"width":W,"height":H}`。
   - `timing`：`{"light":18,"dark":18,"outro":2}`。
   - `music`：默认 `"synth"`，用 numpy 自己合成的免版权配乐，是柔和铺底加拨弦琶音，C–G–Am–F，84 bpm。浅色段明亮，切到深色后降八度、更低沉，署名卡落在一个 C 和弦上。音量归一到约 −19 dB RMS，带软限幅，淡入 1.5 秒、淡出 2.5 秒。`null` 表示静音轨，也可以填一个有授权的音频文件路径。不要下载受版权保护的音乐。
   - 节点 `icon`：内置图标有 git、pr、ci、check、robot、person、doc、drive、cloud、clock、chat、x，也可以填一个 .png 文件路径。
   - `outro`：署名卡的文字，一行一项。
3. 先用 `./render.sh <config.json> --no-video` 只出图片，亲自看 `light.png` 和 `dark.png`，确认文字没有重叠、截断或异常换行，有问题就改配置重跑。泳道里节点太多时，就拆行或者精简文字。
4. 正式出片：`./render.sh <config.json> [--out DIR]`，得到 mp4（H.264、yuv420p、AAC 44.1 kHz 立体声）。用 ffprobe 核对分辨率、时长，确认有音轨；用 `ffmpeg -af volumedetect` 核对音量，平均值约 −20 dB、峰值不超过 −1 dB。测量只能说明音量正常，好不好听要发给对方试听。
5. 交付时把 mp4 作为附件发出去，说明有哪些地方需要对方确认。如果要发布到社交平台，只在对方明确要求时才发。注意很多发布工具（比如 Buffer）只接受公开的直链视频，而且帖子发出去之后不能换视频，所以要先确认成片（包括配乐），再发。

## 注意
- 画面里不要出现本机路径、主机名、邮箱、密钥；如果要发到禁止外链的平台，画面里也不要放链接。
- 品牌图标只用用户提供的或允许使用的图片。
- 一个系列就是多个配置文件，每个单独跑一次 render，编号（例如 1/4）要和发布的集数一致。
- 输出写成新文件，不要覆盖已经交付或发布过的成片。
