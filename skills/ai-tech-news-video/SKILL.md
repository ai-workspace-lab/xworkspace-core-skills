---
name: ai-tech-news-video
description: "用于制作 AI 科技资讯快报视频。包含：新闻检索与筛选、真实素材下载、edge-tts 口播、HyperFrames 画面编排、音频与字幕同步、最终渲染导出。触发词：AI快报、科技资讯视频、AI新闻视频、news flash video、weekly AI digest。"
---

# AI 科技资讯快报视频 Skill

使用 `HyperFrames + edge-tts + 素材检索` 生产专业 AI 资讯快报视频。

## 流程总览

```
1. 新闻检索与筛选 → 2. 素材获取 → 3. 口播生成 → 4. 编写 HyperFrames 页面 → 5. 渲染导出
```

## 默认规格

- **默认比例：16:9 横屏**，使用 `1920x1080`，适合 B 站、YouTube、网页内嵌、横屏播放器和演示场景。
- **不要默认做 3:4 或 9:16**。只有用户明确说“抖音 / 小红书 / 视频号 / Shorts / Reels / 竖屏 / 手机端优先”时，才改用 `1080x1920`。
- 信息差视频的默认画面语言是**新闻图或视频素材 + 生动解释动画 + 字幕**，不要把整段新闻文案铺成 PPT。
- **必须添加逐句口播字幕。**每段配音都要有对应的可读字幕，字幕要跟随口播出现，不能只用标题、信息条、画面文案或卡片摘要代替。
- 字幕默认放在底部安全区，使用半透明深色底或描边保证可读性；不要遮住新闻截图的核心标题、产品界面、表格和人物脸部。
- 字幕文案可以比配音略短，但必须覆盖每段口播的关键信息。每屏建议 1-2 行，每行不超过 22 个中文字符。
- **开头口播固定短句式**：`X月X日的 AI 信息差来了。` 然后立刻开始播第一条内容，不要铺垫、不要自我介绍、不要解释栏目。
- **不讲无关总结**：最后一条讲完就结束或做 0.5-1 秒视觉收束，不要再补“以上就是本期”“总结一下”“关注我”等无关口播。
- **硬性要求：每条新闻必须出现真实素材。**真实素材包括新闻网页截图、官方博客/公告截图、产品官网截图、发布会画面、公司/产品官方图片、媒体配图、公开授权照片或可核实的真实界面截图。不能只用自制假 Logo、假产品界面、纯图标、纯抽象几何图或 AI 编造截图代替真实素材。
- **素材优先级：官方截图/公告页 > 新闻报道截图 > 真实产品界面/公司图片 > 授权图库辅助图。**图库图只能做背景或补充氛围，不能作为该新闻的唯一画面证据。
- **没有真实素材就不能直接渲染最终版。**如果某条新闻找不到可用真实素材，必须先换题、继续找，或明确告诉用户这条无法做成合格新闻卡，不能悄悄用假界面糊弄过去。
- 每条新闻优先用不同视觉结构和动画隐喻，让观众一眼看懂变化：例如 Agent 搬进电脑，可以用小 Agent 从网页窗口移动到本地文件、桌面窗口、任务卡片之间，而不是只放一张配图和大段文字。
- **不要默认做片尾总结、关注引导或自我介绍**。信息差视频讲完信息差就结束；最后一条新闻结束后可直接淡出、硬切或用 0.5-1 秒视觉收束。

## Step 1：检索并筛选 AI 新闻

### 推荐信息源（按 `web_fetch` 可用性排序）

| Source | URL | Fetchable? | Best For |
|--------|-----|-----------|----------|
| The Verge AI | theverge.com/ai-artificial-intelligence | ✅ Yes | Comprehensive AI coverage |
| Hacker News | news.ycombinator.com | ✅ Yes | Tech community trending |
| GitHub trending | github.com/trending | ✅ Yes | Dev tools & open source |
| Ars Technica | arstechnica.com/ai | ❌ JS-rendered | Skip unless using browser |
| 36kr | 36kr.com/information/AI | ❌ JS-rendered | Skip unless using browser |
| TechCrunch | techcrunch.com/category/artificial-intelligence | ❌ JS-rendered | Skip unless using browser |

**JS 渲染站点**：优先使用 `browser` 工具，不要只用 `web_fetch`。

### 新闻筛选规则

- Pick **4-5 items** per video (sweet spot for 60-90s)
- Each item needs: **headline (≤20 chars)** + **one-line summary** + **category tag**
- Balance categories: mix of features, company moves, infrastructure, legal, societal impact
- Verify recency: all items should be from the **past 7 days**
- Include at least one **China/domestic AI** item if audience is Chinese

### 分类标签

| Tag | Emoji | Color | CSS Class |
|-----|-------|-------|-----------|
| 新功能 | 🧠 | Yellow | `tag-feature` |
| 公司动态 | 🚀 | Indigo | `tag-company` |
| 基础设施 | ⚡ | Green | `tag-infra` |
| 法律 | ⚖️ | Red | `tag-legal` |
| 能源/社会 | 💡 | Blue | `tag-energy` |
| 开源 | 📦 | Purple | `tag-opensource` |
| 研究 | 🔬 | Cyan | `tag-research` |

## Step 2：获取并下载真实新闻素材

<HARD-GATE>
Before writing HyperFrames HTML or rendering the final MP4, create an `assets/images/` folder and save at least one real, topic-matched visual asset for every selected news item. Also write an `assets/images/manifest.md` file that maps each news item to:

- asset filename
- source page URL or citation label
- asset type: official screenshot, news screenshot, product screenshot, public photo, or licensed stock support
- why this asset proves or supports this specific news item

If any selected item has no real asset, stop and replace that news item or ask the user how to proceed. Do not substitute fake logos, fake dashboards, fake screenshots, generic icon cards, abstract AI art, or purely CSS-drawn panels as the only visual for a news item.

Before final render, add timed subtitles for every voiceover clip. If there is narration audio without corresponding visible subtitle text, stop and add subtitles before rendering.
</HARD-GATE>

### 素材来源

| Source | URL | License | Notes |
|--------|-----|---------|-------|
| Official announcement/blog | company site | Varies | Best source for product/news screenshots |
| News article screenshot | The Verge / TechCrunch / Reuters / 36kr / etc. | Editorial fair use considerations | Use as visual proof of a reported item |
| Product website/app screenshot | official product page/app | Varies | Best for feature and launch stories |
| Unsplash | unsplash.com | Free | Best quality, use `?w=640&q=80` for optimized downloads |
| Pexels | pexels.com | Free | Good variety |
| Wikimedia | commons.wikimedia.org | Varies | Logos, diagrams |

### 真实素材硬性规则

- **One real asset per news card, minimum.** A 5-item video needs at least 5 downloaded images/screenshots, one for each story.
- **Every real asset must be visible in the video.** It can be cropped, masked, color-graded, blurred slightly behind text, or combined with explanatory animation, but it must appear on-screen long enough for viewers to recognize it.
- **Use screenshots for web-only sources.** If the story is from a web page and no downloadable image is available, capture the article/announcement/product page as an image and use it in the card.
- **遇到 Cloudflare 或类似人机验证时，必须先点验证再截图。** 如果截图画面出现 “Verify you are human”“Performing security verification” 或验证码框，不能把这个验证页当新闻素材保存。要用可交互浏览器打开页面，点击验证框，等真实文章或官方页面加载出来后再截图；如果验证后仍然进不去，就换来源或换新闻。
- **Do not invent brand visuals.** Homemade “OpenAI Ads Manager” panels, fake product windows, fake legal files, fake company logos, and fake charts are allowed only as secondary explanation layers, never as the main news visual.
- **Do not use generic stock as proof.** A data-center stock photo can support an infrastructure story, but if the story is about a specific company deal, also include the article/official page screenshot or a real company/product image.
- **Keep a source manifest.** Future maintainers must be able to open `assets/images/manifest.md` and understand where each image came from.

### 下载示例

```bash
cd assets/images
curl -sL -o ai-brain.jpg "https://images.unsplash.com/photo-XXXXXXXXX?w=640&q=80"
```

### 截图示例

Use a browser or Playwright screenshot when an official/news page is the best available visual:

```bash
mkdir -p assets/images
# Example filename convention:
# assets/images/01-perplexity-official-page.png
# assets/images/02-anthropic-announcement.png
```

After every screenshot, quickly inspect the saved image. If it captured a Cloudflare/security verification page instead of the real article, discard it and redo the capture through an interactive browser after clicking the human verification checkbox. The manifest should cite the real source page, not the verification page.

Crop or resize screenshots only after saving the original. Keep names numbered by card order so it is obvious which asset belongs to which news item.

### 选图原则

- **Match the topic**: AI → neural/brain visuals, SpaceX → rockets/space, legal → courthouse/gavel, data centers → servers
- **Prefer real/news-specific visuals over abstract/tech images.** Abstract images are only allowed as background texture, not as the primary evidence for the story.
- **Dark backgrounds** work best with the dark UI theme
- **Optimize size**: download at 640px width, quality 80 — sufficient for 1920px video

### 按主题的搜索关键词

| Topic | Unsplash Search Terms |
|-------|----------------------|
| AI/ML | artificial intelligence, neural network, machine learning, brain digital |
| Space | rocket launch, space, nasa, spacex |
| Legal | law, courtroom, gavel, justice |
| Infrastructure | server room, data center, technology, network |
| Energy | power lines, electricity, energy, solar panels |
| Open source | code, programming, developer, github |
| Research | laboratory, science, microscope, quantum |

## Step 3：使用 edge-tts 生成口播

### 安装

```bash
pip3 install --break-system-packages edge-tts
```

### 推荐音色

| Voice | Language | Style | Best For |
|-------|----------|-------|----------|
| zh-CN-YunxiNeural | Chinese | Young male, energetic | Tech news, dynamic delivery |
| zh-CN-XiaoxiaoNeural | Chinese | Female, professional | Formal news, corporate |
| zh-CN-YunjianNeural | Chinese | Male, deep | Dramatic reveals, impacts |
| en-US-GuyNeural | English | Male, mature | English news |

### 生成示例

```bash
cd assets/audio

# Intro (brief, punchy)
edge-tts --voice zh-CN-YunxiNeural --rate="+30%" \
  --text "AI快报，5月7日，本周最热资讯。" \
  --write-media intro.mp3

# News cards — 直接说内容，不说"第X条"
edge-tts --voice zh-CN-YunxiNeural --rate="+30%" \
  --text "Anthropic 让 Claude 学会了做梦。Claude 可在会话间隙回顾历史，发现错误模式并自我改进。" \
  --write-media card1.mp3

# No default outro
# 信息差视频默认不生成“以上就是本期/关注我/下期见”这类片尾口播。
```

### 口播文案规则

- **语速快**：必须加 `--rate="+30%"` 参数加速，默认语速太慢，不适合快节奏资讯
- **不说"第X条"**：直接讲内容，不要"第一条""第二条"这种废话，紧凑不啰嗦
- **不说"本周""今天"等时间词**：视频本身就是快报，观众知道是最新资讯
- **开头只说日期信息差**：第一句必须是 `X月X日的 AI 信息差来了。`，例如 `5月9日的 AI 信息差来了。` 后面直接进入新闻内容。
- **不说片尾 CTA**：不要默认说“以上就是本期”“我是 XXX”“关注我”“下期见”。用户明确要求账号口播时才加。
- **不讲无关总结**：默认不加片尾总结、观点升华、账号人设口播；信息差讲完就结束。
- **headline + 1 sentence max**：每条新闻标题 + 一句话解释，不超过 40 字中文
- **字幕同步**：每个 `intro.mp3`、`card*.mp3` 都要在 HTML 里有对应字幕 clip；字幕起止时间以配音时长为准，允许比配音前后各多留 0.1-0.2 秒。
- Duration target: **8-12 seconds per card**（加速后）
- Check duration: `ffprobe -v quiet -show_entries format=duration -of csv=p=0 card1.mp3`

### BGM（背景音乐）

**必须添加背景音乐。** 没有BGM的视频感觉空、不专业。

#### BGM 获取规则（改为本地优先）

1. **先从当前项目目录查找本地 BGM**，优先检查：
   - `assets/audio/bgm.mp3`
   - `assets/audio/bgm.wav`
   - `assets/audio/` 下其他可用音乐文件（`.mp3/.wav/.m4a`）
2. **如果找不到本地 BGM，不要自动联网下载或生成。**
3. **必须询问用户是否需要添加 BGM。**
4. 用户确认需要后，**请用户提供音频文件**（或给出其在本地项目中的路径），再接入时间线。

示例检查命令：

```bash
ls assets/audio
```

#### BGM 选择建议

- **风格**：科技感/电子/Minimal / Synthwave / Ambient Tech
- **节奏**：中等偏快（110-130 BPM），和快资讯节奏匹配
- **不要人声**：纯音乐，避免和配音冲突
- **音量**：BGM track 的 `data-volume` 设 **0.08-0.12**，远低于配音（0.85），作为氛围层
- **关键词搜索**：tech ambient, synthwave minimal, future bass, corporate tech, digital pulse

#### 在 HyperFrames 中使用 BGM

```html
<audio id="bgm" class="clip"
  data-start="0" data-duration="86"
  data-track-index="20" data-volume="0.10"
  src="assets/audio/bgm.mp3"></audio>
```

- BGM 放在**高号 track**（如 track 20），避免和配音 track 冲突
- 全程播放，`data-start="0"`，`data-duration` 等于视频总时长

## Step 4：编写 HyperFrames 合成页面

### 项目结构

```
tech-news-flash/
├── index.html          # Main composition
├── assets/
│   ├── images/         # Downloaded images
│   │   ├── ai-brain.jpg
│   │   ├── spacex-rocket.jpg
│   │   └── ...
│   └── audio/          # Voiceover files
│       ├── intro.mp3
│       ├── card1.mp3
│       └── ...
├── hyperframes.json
├── meta.json
└── package.json
```

### 默认画布

```html
<meta name="viewport" content="width=1920, height=1080" />
<div
  id="root"
  data-composition-id="main"
  data-start="0"
  data-duration="86"
  data-width="1920"
  data-height="1080"
>
```

横屏渲染命令：

```bash
npx hyperframes render --resolution landscape -o renders/ai-tech-news.mp4
```

只有明确要求竖屏时再使用：

```bash
npx hyperframes render --resolution portrait -o renders/ai-tech-news-portrait.mp4
```

### 卡片布局：图文分栏

```
┌─────────────────────────────────────────────────┐
│  ┌──────────────┐  ┌──────────────────────────┐ │
│  │              │  │ NO. 01                   │ │
│  │   IMAGE      │  │ 🧠 新功能                │ │
│  │   (45%)      │  │                          │ │
│  │              │  │ Headline Text            │ │
│  │              │  │                          │ │
│  │              │  │ Description text...      │ │
│  └──────────────┘  └──────────────────────────┘ │
│  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░ progress bar   │
└─────────────────────────────────────────────────┘
```

### 关键设计原则

1. **16:9 横屏优先** — 充分利用左右空间：一侧放新闻图/视频/产品截图，另一侧放关键词、动画解释或少量标题。
2. **字幕承载完整口播** — 画面不要重复展示整段新闻文案；只放短标题、关键词、数字和视觉隐喻。
3. **每条新闻要有不同动画点** — 不要 5 条都套同一个卡片模板。每条至少有一个贴合新闻的动态隐喻或素材切换。
4. **真实素材是主画面的一部分** — 每张卡至少 35% 画面面积来自真实素材、官网截图、新闻截图或真实照片；解释动画可以覆盖在上面，但不能完全替代它。
5. **Progress bar at card bottom** — shows reading progress, adds motion
6. **Numbered cards (01-05)** — creates sequence feel
7. **Category-colored tags** — visual scanning aid
8. **Subtle image overlay** — gradient from image edge to dark background
9. **Card watermark number** — large transparent number on image for depth

### 渲染前检查清单

Before `npx hyperframes render`, verify:

- `assets/images/` contains one real asset per news item.
- `assets/images/manifest.md` maps every card to a source and asset file.
- Every card's HTML references its real asset with an `<img>` or visible background image.
- Fake UI, fake logos, CSS diagrams, generated abstract art, or stock photos are not the only visual for any news card.
- `npx hyperframes inspect` has no layout errors.

### 音频集成（关键）

**Web Audio API does NOT render into HyperFrames MP4.** Always use `<audio>` tags:

```html
<audio id="voice1" class="clip"
  data-start="6" data-duration="17"
  data-track-index="5" data-volume="0.85"
  src="assets/audio/card1.mp3"></audio>
```

### 时序策略

| Element | Duration | Notes |
|---------|----------|-------|
| Intro | 5-6s | Title + date animation |
| News Card | voice_duration + 1s | Let voice finish, then transition |
| Card Transition | 0.3s | Fade/slide out |
| End beat | 0.5-1s | Last news finishes, then fade/hard cut. No CTA unless requested |

**Always check voice duration first**, then set card `data-duration` to match.

### HyperFrames 常见坑位

- **No `Math.random()`** — use `mulberry32` seeded PRNG
- **Track indices**: persistent elements (header/ticker) on track 10+, cards on track 1, voice on track 5, SFX on track 6-7, BGM on track 20
- **`class="clip"`** required on all timed elements
- **Audio must be `<audio>` tags** with `data-track-index` — not Web Audio API

## Step 5：将音效合成为 WAV 文件

**Web Audio API 合成的音效不会渲染进 HyperFrames 的 MP4 输出。**

解决方案：用 Python 脚本把音效预渲染成 WAV 文件，然后用 `<audio>` 标签引入。

### 生成音效文件

```bash
python3 scripts/render_sfx.py assets/audio/sfx
```

默认会先产出 6 种常用音效（**基础参考包**）：

| 文件 | 时长 | 用途 |
|------|------|------|
| whoosh.wav | 350ms | 卡片转场 |
| impact.wav | 400ms | 卡片揭示/重音 |
| pop.wav | 150ms | 通知/轻反馈 |
| click.wav | 100ms | UI 点击 |
| sparkle.wav | 600ms | 揭晓/成就/片尾 |
| rise.wav | 1000ms | 紧张/铺垫 |

这 6 种只是默认参考，不是上限。  
如果分镜需要其他声音（例如机械启动、扫描、故障告警、数据流、倒计时、转场吸附、胜利提示等），应在 `scripts/render_sfx.py` 里新增对应合成函数并输出新的 WAV 文件，再按时间线接入。

新增音效建议遵循：

- 先定义用途（在哪个镜头触发、要表达什么情绪/动作）
- 再确定参数（时长、基频、包络、滤波、音量）
- 最后统一命名（如 `scan.wav`、`alarm.wav`、`countdown.wav`）并写入音效映射注释

### 在 HyperFrames 中使用

```html
<!-- 卡片入场音效：whoosh + impact 组合 -->
<audio id="sfx-card1" class="clip"
  data-start="4.0" data-duration="0.5"
  data-track-index="6" data-volume="0.4"
  src="assets/audio/sfx/whoosh.wav"></audio>
<audio id="sfx-card1b" class="clip"
  data-start="4.1" data-duration="0.5"
  data-track-index="7" data-volume="0.35"
  src="assets/audio/sfx/impact.wav"></audio>
```

### 自定义音效

修改 `scripts/render_sfx.py` 中的合成函数即可。每个函数是纯数学（正弦波+噪声+包络），无需外部依赖。

## Step 6：渲染导出

```bash
source ~/.nvm/nvm.sh && nvm use 22
cd tech-news-flash
npx hyperframes lint      # Check for errors
npx hyperframes snapshot --at 3,8,25,42,58,82  # Verify key frames
npx hyperframes render -o output.mp4           # Render final video
```

## 全流程速查

```bash
# 1. Init project
source ~/.nvm/nvm.sh && nvm use 22
npx hyperframes init ai-news-$(date +%Y%m%d)
cd ai-news-$(date +%Y%m%d)

# 2. Create asset directories
mkdir -p assets/images assets/audio

# 3. Download images (edit URLs for your news)
curl -sL -o assets/images/topic1.jpg "https://images.unsplash.com/photo-XXX?w=640&q=80"

# 4. Generate voiceover
edge-tts --voice zh-CN-YunxiNeural --text "..." --write-media assets/audio/card1.mp3

# 5. Write index.html (use the card layout template)

# 6. Lint, preview, render
npx hyperframes lint
npx hyperframes preview
npx hyperframes render -o output.mp4
```
