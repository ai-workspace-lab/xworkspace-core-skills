---
name: product-intro-video
description: "制作产品介绍视频。默认使用中文介绍产品，除非用户明确要求其他语言。流程：访问官网→获取素材(VL验证)→Web搜索补充→用户确认→HyperFrames渲染。支持任意比例。触发：产品视频、product video、官网视频、intro video、产品介绍。"
---

# 产品介绍视频制作 Skill

根据官网信息制作产品介绍视频，使用 `HyperFrames + GSAP` 渲染。

## 默认语言规则（中文优先）

**默认用中文介绍产品。** 只要用户没有明确指定其他语言，旁白、画面主文案、说明性字幕、分镜说明和交付总结都使用中文。

如果官网原文是英文，也不要直接把英文官网文案当成旁白。应先理解产品，再改写成自然中文，保留必要的英文品牌名、产品名、技术名和短 CTA，例如 `HyperFrames`、`HTML`、`CSS`、`GSAP`、`MP4`。

只有在以下情况才使用非中文：

1. 用户明确说要英文、双语或某种具体语言。
2. 品牌口号必须保留原文，并且原文比翻译更像品牌资产。
3. 代码片段、命令、API 名称、产品专有名词需要保持英文。

## 中文旁白与音频规则

### 先判断是否需要旁白

广告片不是每个画面都必须有旁白。开始写脚本前，先判断这条视频到底需不需要旁白，以及哪些段落需要旁白。

必须在 `SCRIPT.md` 或 `STORYBOARD.md` 里写清楚：

1. **旁白段落**：哪些场景需要旁白说明产品、卖点、差异化或 CTA。
2. **无旁白段落**：哪些场景只保留原素材声音、音乐、音效、产品画面或情绪停顿。
3. **素材优先段落**：如果用户提供了视频素材、产品演示、访谈、实拍、屏幕录制或官网 demo，要先判断这些素材本身是否已经能讲清楚内容，不要强行盖上旁白。
4. **留白段落**：品牌露出、视觉冲击、转场、产品界面细节展示，可以留 0.5-2 秒给音乐和画面呼吸。

判断原则：

| 情况 | 旁白策略 |
|------|----------|
| 产品概念复杂、观众不容易一眼看懂 | 用短旁白解释“这是什么”和“为什么有用” |
| 画面是完整产品演示或用户提供素材 | 优先让素材自己说话，旁白只补充必要上下文 |
| 模板、界面、操作流程正在快速展示 | 可用少量关键词旁白，不要逐项念屏幕内容 |
| 情绪高潮、品牌片尾、视觉转场 | 可以无旁白，只用音乐、音效和视觉停顿 |
| 用户明确要求无旁白 | 不生成旁白，只做字幕、音乐和音效 |

旁白密度建议：

- 15 秒广告：通常 1-3 句旁白即可。
- 30 秒广告：通常 4-8 句旁白，中间要留音乐和画面呼吸。
- 60 秒产品介绍：可以有完整旁白，但仍应保留关键无旁白展示段。

不要为了“填满音轨”而写旁白。旁白过多会让广告片像说明书，削弱画面和产品素材的说服力。

### 中文旁白默认使用 Edge TTS

默认使用 `edge-tts` 生成中文旁白，不使用 macOS `say`、系统朗读声或低质量离线 TTS，除非 Edge TTS 确认不可用。

推荐中文声音：

| 声音 | 适合场景 | 说明 |
|------|----------|------|
| `zh-CN-YunyangNeural` | 产品介绍、技术产品、企业宣传 | 专业、可靠，默认优先选这个 |
| `zh-CN-YunxiNeural` | 节奏更轻快的产品视频 | 年轻、有活力 |
| `zh-CN-XiaoxiaoNeural` | 亲和、温暖、轻柔产品 | 女声，温暖自然 |

先检查本机可用声音：

```bash
edge-tts --list-voices | rg 'zh-CN.*Neural'
```

生成中文旁白：

```bash
edge-tts --voice zh-CN-YunyangNeural --rate +6% \
  --text "中文旁白内容" \
  --write-media narration.mp3
```

转成 HyperFrames 稳定使用的 wav：

```bash
ffmpeg -y -i narration.mp3 -ar 48000 -ac 2 narration.wav
```

### 旁白时长处理

生成旁白后必须检查时长：

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 narration.wav
```

如果旁白超过视频时长，优先压缩脚本，不要大幅加速音频。只有在只差一点点时才允许轻微加速，建议不超过 `+8%` 或 `atempo=1.08`。大幅加速会让中文旁白变尖、赶、僵硬，成片听感会很差。

### 视频时序必须跟随音频

**先确认旁白真实长度，再制作视频时间线。** 不要先固定 30 秒画面再把音频塞进去，否则很容易出现前面还正常、最后几个片段音频提前结束或画面拖尾的问题。

正确流程：

1. 先写中文旁白脚本。
2. 用 Edge TTS 生成旁白音频。
3. 用 `ffprobe` 读取旁白真实时长。
4. 根据旁白内容把脚本拆成场景，并给每个场景分配时间。
5. `STORYBOARD.md`、`index.html`、`data-duration`、转场时间、BGM 时长都跟随这个真实音频长度。
6. 渲染后再次用 `ffprobe` 确认成片时长和音频时长一致。

如果旁白真实长度是 `31.2s`，视频就应该做成约 `31.2s`；除非用户明确要求必须 30 秒，此时应该先压缩旁白脚本，而不是强行让画面和音频互相错位。

检查命令：

```bash
ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 narration.wav
ffprobe -v error -show_entries stream=codec_type,duration -show_entries format=duration -of json renders/final.mp4
```

交付前必须抽查：

1. 开头第一句是否和第一幕同步。
2. 中段核心卖点是否和对应画面同步。
3. 最后一句 CTA 是否落在片尾品牌画面上，而不是提前几秒读完。

### 背景音乐规则

如果需要 BGM，优先使用无版权风险方案：用 Web Audio API 或等价离线合成脚本生成背景音乐，再作为独立音轨插入 HyperFrames。

BGM 必须比旁白低很多，建议：

```html
<audio
  id="bgm"
  data-start="0"
  data-duration="30"
  data-track-index="20"
  src="assets/audio/bgm-webaudio.wav"
  data-volume="0.12"
></audio>
```

BGM 设计原则：

1. 不要有人声，避免和中文旁白冲突。
2. 音量只做氛围层，通常 `0.08-0.18`。
3. 科技产品适合低频脉冲、柔和和弦、轻微扫频和转场 whoosh。
4. 每次渲染前确认旁白和 BGM 都是本地文件，并且音频时长覆盖完整视频。

## 整体流程（中文工作流）

```
1. 访问官网 → 2. 获取素材(VL验证) → 3. Web搜索补充 → 4. 用户确认 → 5. 写HTML → 6. 渲染
```

**关键：Step 4 必须等用户确认后才能进入创作！**

---

## Step 1: 访问官网 & 获取素材

### 抓取方式

| 网站类型 | 方式 | 说明 |
|---------|------|------|
| 静态 HTML | web_fetch | 直接抓文本内容 |
| JS 渲染 | browser 工具 | 打开页面→snapshot→screenshot |
| API 文档 | web_fetch | 通常可抓 |

### 素材获取清单

1. **Logo** — 官网头部/导航栏，右键保存或截图
2. **产品截图** — Hero 区域、功能展示、界面截图
3. **品牌色** — 从 CSS 变量、Logo 颜色中提取
4. **核心文案** — 标语、功能描述、CTA 按钮文字
5. **产品图片** — 功能展示区的配图/截图
6. **视频预览** — 如果有 demo 视频，记录 URL

### 截图流程

```bash
# 用 browser 工具截图（全页 + 首屏）
browser(screenshot, fullPage=true) → 保存全页截图
browser(screenshot, fullPage=false) → 保存首屏截图
# 复制到项目目录
cp /path/to/screenshot.jpg <project>/assets/images/
```

### VL 验证素材

对每张截图用 image 工具验证：

```python
image(
  image="assets/images/hero-screenshot.jpg",
  prompt="描述这张截图的内容。是否包含：1)产品Logo 2)产品界面 3)品牌色 4)核心功能展示？列出可用于视频的元素。"
)
```

---

## Step 2: Web 搜索补充信息

### 搜索内容

1. **产品新闻** — 最新发布、融资、用户评价
2. **竞品对比** — 同类产品有哪些，差异化是什么
3. **社区讨论** — Hacker News / Reddit 反馈
4. **技术细节** — GitHub star 数、开源协议、API 功能
5. **使用案例** — 谁在用，怎么用的

### 搜索关键词模板

```
"<产品名> review"
"<产品名> vs <竞品名>"
"<产品名> site:news.ycombinator.com"
"<产品名> site:reddit.com"
"<产品名> open source" / "<产品名> API"
```

---

## Step 3: 用户确认

### 输出格式

```
📋 产品信息确认

【基本信息】
产品名：HyperFrames
公司：HeyGen
定位：Open-source, agent-native HTML-to-video 渲染框架
品牌色：#00D9A5 (薄荷绿) + #000000 (纯黑)
Logo：抽象几何播放图标

【核心卖点】
1. HTML → Video — 用 Web 技术栈写视频
2. Agent-Native — AI Agent 可直接生成/修改视频
3. Open Source — 开源框架，本地渲染
4. 51+ 模板目录 — Notion/Stripe/Raycast Showcase 等

【视频规格】
比例：3:4 竖版 (1080×1440)
风格：深色科技风
重点突出：AI Agent 可直接生成和修改视频

【已有素材】
✅ 官网全页截图
✅ 社区 Playground 截图
✅ 本地 CLI 环境可用

确认信息准确？需要修改什么？
```

### 规格选项

| 项目 | 选项 |
|------|------|
| 比例 | 16:9 (1920×1080) / 9:16 (1080×1920) / 3:4 (1080×1440) / 1:1 (1080×1080) |
| 风格 | 跟随品牌色 / 深色科技 / 温暖治愈 / 浅色极简 / 渐变流光 |
| 配音 | 有旁白 / 无旁白 |
| BGM | 用户提供 / 搜索免费 / Web Audio API 合成 |

---

## Step 4: HyperFrames HTML 编写

### 项目初始化

```bash
source ~/.nvm/nvm.sh && nvm use 22
npx hyperframes init <product-name> --width 1080 --height 1440
cd <product-name>
mkdir -p assets/images assets/audio/sfx
```

### 视频结构（产品介绍）

```
1. Logo 入场（0-2s）— 品牌 Logo 动画
2. 产品名+定位（2-4s）— 一句话说明是什么
3. 核心卖点展示（4-Ns）— 2-4 个功能点，每个 3-5s
   - 每个卖点：图标/关键词 → 细节展开 → 过渡
4. 产品界面/效果展示（Ns-Ms）— 截图或 Demo 预览
5. CTA 收尾（Ms-end）— 官网链接 / 下载 / 试用
```

### 品牌色提取规则

从官网提取后写入 CSS 变量。根据选择的视觉风格，变量体系完全不同：

#### 深色科技风色板

```css
:root {
  --brand-primary: #00D9A5;    /* 主品牌色 */
  --brand-secondary: #00B886;  /* 深一级 */
  --brand-glow: rgba(0,217,165,0.15); /* 光晕 */
  --bg-primary: #000000;       /* 背景色 */
  --bg-card: rgba(20,20,20,0.95);
  --text-primary: #ffffff;
  --text-secondary: rgba(255,255,255,0.55);
}
```

#### 温暖治愈风色板

```css
:root {
  --peach: #FFD4C2;            /* 蜜桃 */
  --cream: #FFF8F0;            /* 奶油白 */
  --warm-bg: #FFF1E6;          /* 暖杏背景 */
  --coral: #E8785A;            /* 珊瑚橘（主强调） */
  --coral-soft: rgba(232,120,90,0.15);
  --amber: #FFB347;            /* 琥珀金 */
  --amber-soft: rgba(255,179,71,0.12);
  --rose: #F4A0A0;             /* 玫瑰粉 */
  --rose-soft: rgba(244,160,160,0.18);
  --lavender: #C9B1FF;         /* 薰衣草 */
  --lavender-soft: rgba(201,177,255,0.12);
  --text: #3D2C2C;             /* 深炭棕（不用纯黑！） */
  --text-dim: #8B7B75;         /* 浅棕灰 */
  --text-light: #B5A8A3;
  --card: rgba(255,255,255,0.65);
  --card-border: rgba(255,255,255,0.8);
  --shadow: 0 8px 40px rgba(180,130,110,0.12);
}
```

---

### 视觉风格指南（重点！扁平=无聊）

**核心原则：产品视频不能是会动的 PPT。要有纵深、光效、质感、温度。**

#### ❌ 所有风格都要避免的

- 纯色背景 + 文字（像 Keynote 幻灯片）
- 简单的淡入淡出（无质感）
- 扁平色块堆叠（无纵深）
- 静态文字一直显示（无聊）
- Emoji 当图标（廉价感）
- 纯黑 + 纯蓝 + 冷色 = 硬、冷、像 PPT

---

### 风格 A：深色科技风

适合：开发者工具、SaaS、AI 产品。参考：Linear、Stripe Showcase、Raycast。

| 技法 | 实现方式 | 效果 |
|------|---------|------|
| **玻璃拟态** | `backdrop-filter: blur(20px); background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.1)` | 半透明毛玻璃卡片 |
| **光晕/发光** | `box-shadow: 0 0 60px 20px var(--brand-glow);` | 品牌色向外扩散 |
| **渐变网格** | 多个 `radial-gradient` 叠加 + `mix-blend-mode: screen` | Apple 多彩渐变 |
| **3D 倾斜** | `transform: perspective(1000px) rotateY(-5deg)` | 截图有立体感 |
| **浮动动画** | GSAP `yoyo: true, repeat: N, y: -8` | 微微漂浮 |

深色风背景层叠（最少三层）：

```css
.bg-base { background: #000; }
.bg-glow { /* 品牌色径向渐变 + blur(100px) */ }
.bg-grid { /* 细线网格 60px 间距 */ }
```

深色风卡片：

```css
.feature-card {
  background: rgba(18, 18, 22, 0.7);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
}
```

---

### 风格 B：温暖治愈风 ⭐推荐

适合：所有想让人"觉得舒服"的产品。参考：Notion、Figma、日系文具品牌、Calm/Headspace。

**核心感受：清晨透过纱帘的自然光。像被温柔对待。**

#### 色彩哲学

- **零冷色** — 不用蓝、紫、绿做主色。锁定在暖黄→米白→浅驼→陶土红区间
- **文字不用纯黑** — 用深炭棕 `#3D2C2C`，像墨水渗入宣纸
- **低饱和度** — 所有颜色经过"去锐化"，对比度控制在 1:4~1:6
- **强调色** — 珊瑚橘 `#E8785A`，如同指尖温度

#### 背景层叠（温暖版，最少四层）

```css
/* Layer 1: 暖色渐变底色 */
.bg-base { background: linear-gradient(160deg, #FFF8F0 0%, #FFE8D6 40%, #FFF0E8 100%); }

/* Layer 2-4: 有机色斑（像阳光下的色散） */
.bg-blob1 {
  width: 900px; height: 900px; border-radius: 50%;
  background: radial-gradient(circle, rgba(232,120,90,0.15) 0%, transparent 70%);
  filter: blur(80px); /* 大模糊 = 柔和扩散 */
}
.bg-blob2 { /* 琥珀色斑 */ }
.bg-blob3 { /* 玫瑰色斑 */ }
.bg-blob4 { /* 薰衣草色斑 */ }
```

色斑要有缓慢漂移动画（GSAP `sine.inOut`，7-10s 周期），像阳光在移动。

#### 暖色粒子（像阳光浮尘）

不用科技感的网格/点阵。用 20+ 个小圆点，暖色调，在画面中缓慢上浮：

```css
.warm-particle {
  position: absolute; border-radius: 50%; opacity: 0;
  /* 每个粒子不同大小(4-10px)、不同暖色、不同位置 */
}
```

```js
// GSAP: 从底部浮起 → 消失 → 循环
tl.fromTo("#wp1", { opacity: 0, scale: 0.3, y: 0 },
  { opacity: 0.7, scale: 1, y: -60, duration: 1.8, ease: "sine.inOut" }, 0.5)
  .to("#wp1", { y: -120, opacity: 0, duration: 1.8, ease: "sine.in" }, 2.3);
```

⚠️ 粒子必须写在静态 HTML 中（不能用 JS 动态创建），否则 HyperFrames 编译时 GSAP 找不到 target。

#### 卡片：奶油毛玻璃

```css
.soft-card {
  background: rgba(255,255,255,0.65);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.8);
  border-radius: 28px;
  box-shadow: 0 8px 40px rgba(180,130,110,0.12), 0 2px 12px rgba(255,200,180,0.08);
}
```

比深色风的玻璃拟态更透、更柔。圆角更大（28px vs 20px）。

#### 功能图标：渐变暖色底

```css
.feat-icon {
  width: 48px; height: 48px; border-radius: 16px;
  background: linear-gradient(135deg, rgba(232,120,90,0.12), rgba(255,179,71,0.12));
  /* 每个图标用不同的暖色渐变组合 */
}
```

#### 终端窗口：暖棕底

```css
.terminal {
  background: rgba(61,44,44,0.92);  /* 深炭棕，不是纯黑 */
  color: #F5E6E0;                    /* 暖白，不是冷白 */
  border: 1px solid rgba(180,130,110,0.15);
  border-radius: 24px;
}
/* 提示符用琥珀色，成功输出用珊瑚色（不是冷绿） */
.tp { color: var(--amber); }
.ts { color: var(--coral); }
```

#### CTA 按钮：珊瑚渐变 + 光扫

```css
.cta-btn {
  background: linear-gradient(135deg, var(--coral), #E06848);
  color: #fff;
  border-radius: 18px;
  box-shadow: 0 8px 28px rgba(232,120,90,0.25);
}
/* 光扫用真实子元素（不是 ::after 伪元素，GSAP 无法动画伪元素） */
.cta-sweep {
  position: absolute; inset: 0;
  background: linear-gradient(105deg, transparent 35%, rgba(255,255,255,0.25) 50%, transparent 65%);
  transform: translateX(-100%);
}
```

#### 字体选择

- **温暖风 → Nunito**（圆润、友善、温暖）
- **深色风 → Inter**（几何、理性、专业）
- **代码 → JetBrains Mono**（两种风格通用）

#### 动效缓动函数

| 风格 | 推荐 ease | 感受 |
|------|----------|------|
| 深色科技 | `back.out(1.7)` | 弹性、有力、干脆 |
| 温暖治愈 | `sine.out` | 柔滑、缓缓、不急 |
| 深色科技 | `power3.out` | 快速到位 |
| 温暖治愈 | `sine.inOut` | 呼吸般的均匀节奏 |

温暖风的动效要慢：入场 0.5-1.0s（深色风 0.3-0.5s），出场 0.5s。

#### Logo 出场动画

深色风：弹性放大 `scale: 0.5→1.0 + back.out`
温暖风：柔和浮现 `scale: 0.6→1.0 + sine.out`，配合呼吸缩放 `scale: 1.0↔1.05 + sine.inOut`

---

### 通用动效规则（两种风格共用）

#### 文字不能一次性全出现

- 标题：从下方滑入 + 淡入（`y: 20-40, opacity: 0→1`）
- 副标题：延迟 0.3s 后出现
- 细节：再延迟 0.5s，逐行出现

#### 产品截图要"浮起来"

```css
.product-screenshot {
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0,0,0,0.15);  /* 浅色风用低透明度阴影 */
}
```

#### 纵深

每个画面至少 2 层（前景+背景），不能全部平面。

#### 呼吸感

文字出现后留 0.5-1s 让观众消化，不要连续轰炸。

#### 品牌光效/色效

每次关键元素出现时，品牌色光晕/色斑脉冲一次。

#### 光扫效果

按钮、卡片入场时可以加一道光扫。⚠️ 用真实 DOM 子元素实现（如 `<span class="sweep">`），不能用 CSS `::after` 伪元素（GSAP 无法动画伪元素）。

#### 数字跳动

如果有数字（用户数/GitHub star），用 GSAP countTo 动画。

#### 代码打字

如果是开发者工具，终端逐行显示 + 光标闪烁。

### 音频

#### BGM

搜索顺序：
1. 搜索 Pixabay/Mixkit 免费 BGM
2. 搜索不到 → 用 Web Audio API 合成（见 sound-fx-for-video Skill）
3. 用户提供 → 直接使用

```bash
# 搜索 Pixabay
web_fetch("https://pixabay.com/music/search/tech%20background/")
# 下载
curl -sL -o assets/audio/bgm.mp3 "<URL>"
```

#### 音效

使用 sound-fx-for-video Skill 生成：
- 产品名出现 → sparkle
- 卖点展开 → whoosh
- 数字增长 → rise
- CTA 出现 → impact

### HyperFrames 踩坑

同 ai-info-gap-video Skill 中的踩坑清单。额外注意：
- **3:4 比例** — init 时指定 `--width 1080 --height 1440`
- **竖版布局** — 文字竖向排列空间更窄，字号适当放大
- **手机端预览** — 竖版视频主要在手机播放，确保文字够大

---

## Step 5: 渲染

```bash
source ~/.nvm/nvm.sh && nvm use 22
npx hyperframes lint
npx hyperframes snapshot --at 1,3,5,10,15  # 验证关键帧
npx hyperframes render -o output.mp4
```
