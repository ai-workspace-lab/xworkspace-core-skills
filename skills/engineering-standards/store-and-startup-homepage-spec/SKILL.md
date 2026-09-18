---
name: store-and-startup-homepage-spec
description: 满足 Google、Apple、微软（三大应用商店与初创云计划）审核与上架要求的官网/产品主页设计与交付规范。涵盖品牌资产与官方徽标规范、UX/商业文案对齐、数据流与隐私合规、SEO 架构、GEO（大模型 AI 搜索优化）、全球多语言适配，以及生产交付自检清单（Production-Ready Checklist）。
---

# Store and Startup Homepage Specification

面向 **Google**（Google Play / Chrome Web Store / Google for Startups Cloud Program）、**Apple**（App Store / Safari 扩展 / Apple Developer Program）、**Microsoft**（Microsoft Store / Edge Add-ons / Microsoft for Startups Founders Hub）生态的产品官网与主页设计、工程交付与合规规范。

当产品需要上线官方网站、申请开发者计划/初创扶持、或准备提交应用商店审核时，使用本规范作为设计和交付基准。

---

## 1. 核心审核红线与准入原则（Golden Verification Rules）

三大巨头的人工/自动化审核团队（尤其是初创计划如 Google for Startups 与应用商店审核员）在核查官网时，严格执行以下 4 条底线原则：

### 1.1 域名与实体身份强对齐（Domain-Entity Alignment）
* **禁止免费公共子域名或裸外链**：严禁以 `*.notion.site`、`*.vercel.app`、`*.github.io`、`t.me/*` 或社交媒体主页作为主申请官网；必须绑定拥有自主所有权的独立一级/二级域名（如 `https://product.com`）。
* **企业邮箱同域验证**：申请所用的联系邮箱（如 `contact@product.com`、`support@product.com`）必须与官网域名主体保持 100% 一致。严禁使用 `@gmail.com` 或 `@outlook.com` 申请企业级/商业级开发者或初创项目。
* **SSL/TLS 证书健全**：必须全站强制 HTTPS（TLS 1.2+ / TLS 1.3），禁止混合内容（Mixed Content），证书主体必须有效且信任链完整。

### 1.2 全球可用性与 0 超时保障（Global High-Availability）
* **全球 CDN 加速**：欧美审核节点（加州山景城、西雅图、都柏林等）必须在 **1.5 秒内** 完成页面首包响应（TTFB < 800ms）。
* **防火墙与防护策略白名单**：接入 Cloudflare、Vercel Edge、AWS CloudFront 等全球边缘网络时，**绝对禁止**误将 Google/Apple/Microsoft 所在 IP 段或自动化审查爬虫识别为恶意请求并拦截（如误触发 Turnstile / Cloudflare 5 秒盾强验证）。

### 1.3 实质性产品信息原则（Substantive Product Information）
* **拒绝占位符与“即将推出”**：绝对禁止上线只有“Coming Soon”、“Under Construction”、单行宣传语或 Lorem Ipsum 假文的空洞页面。
* **三位一体产品呈现**：首屏向下滚动必须清晰展示：
  1. **真实产品界面与工作流**：高保真界面截图、交互式 Demo 演示或高清无损产品实机动图（WebM/MP4）。
  2. **核心业务价值与功能模块**：解决谁的什么问题，具体输入/输出是什么。
  3. **真实商业架构与公司主体**：包含清晰的定价方案（Pricing）、公司名称、注册实体、物理/联系地址及团队背景。

### 1.4 法律合规“四大入口”一等公民化
官网主导航或全局吸底页脚（Footer）必须直接包含以下 4 个永久存活的直达链接，且必须公网免密可访问：
1. **Privacy Policy（隐私政策）**：详述收集何种数据、为何收集、与谁共享。
2. **Terms of Service / EULA（服务条款与最终用户许可协议）**。
3. **Account Deletion Request（账户注销与数据删除通道）**：Apple Guideline 5.1.1 与 Google Play 核心强制项。如果产品支持注册，官网必须提供网页版注销指引或一键申请入口。
4. **Support & Contact Us（技术支持与联系我们）**：包含明确的工单入口或客服邮箱。

---

## 2. 品牌系统规范（Brand Identity & Store Badges）

### 2.1 官方商店徽标（Store Badges）合规
产品主页中引导用户下载/安装应用时，必须严格遵守各官方徽标使用指南：

| 平台 | 官方徽章文本标准 | 核心设计约束 | 违规风险（严禁） |
|---|---|---|---|
| **Apple App Store** | "Download on the App Store" | 黑色/白色背景两种官方矢量 asset；角半径为固定比例；留白区（Clear space）至少为徽标高度的 1/4。 | 禁止自行重绘、禁止修改字体、禁止歪斜投影、禁止将 "App Store" 拼写为 "Apple Store" 或 "AppStore"。 |
| **Google Play** | "Get it on Google Play" | 仅使用 Google 官方提供的双色或单色资产；留白区至少为三角形图标宽度的 1/2。 | 禁止使用旧版 “Android Market” 标、禁止剥离 Play 三角形单用文字、禁止拉伸变形。 |
| **Microsoft Store** | "Get it from Microsoft" | 采用标准徽标黑/白版本；与周围元素保持与徽标高度相同的间距。 | 禁止使用旧版 “Windows Store” 徽标、禁止擅自更换 Windows 徽标底色。 |
| **Chrome Web Store** | "Available in the Chrome Web Store" | 必须使用 Chrome 官方 Extension Badge 矢量图；图标保持标准四色。 | 禁止将 Chrome 标放在不符合规范的背景上或改写为 "Google Store"。 |

> [!IMPORTANT]
> 商店徽标下载链接必须携带官方营销追踪参数（如 Apple Campaign Links、Google Play UTM Referrer），便于在商店后台归因转化率。

### 2.2 视觉系统与排版标准
* **真机外壳与截图比例**：主页展示 iOS/Android/Windows 客户端截图时，必须使用对应系统的**官方最新设计外壳规范**（Apple Human Interface Guidelines / Material Design 3 / Windows Fluent Design），严禁使用已淘汰的机型或过时的系统刘海/物理键。
* **深色模式（Dark Mode）友好**：提供系统级 `prefers-color-scheme` 自动跟随与手动切换开关，确保品牌主视觉在深色与浅色环境下均具备高对比度。
* **商标侵权防火墙（Trademark Boundaries）**：
  * 主页标题、宣传语中不得将自身产品表述为“Google 官方推荐”、“Apple 认证”或“Microsoft 专属”，除非拥有正式的书面授权文件。
  * 可以在兼容性说明中使用规范的修饰词，例如：“Designed for macOS”、“Available on Chrome Web Store”、“Compatible with Windows 11”。

---

## 3. 文案与微文案系统（UX Writing & Messaging）

文案直接决定了潜在客户的转化率，也是破除 Google for Startups “did not contain enough information about your company” 拒信的关键。

### 3.1 首屏价值主张（The 5-Second Rule）
首屏必须遵循三段式黄金结构：
1. **主标题（H1 - 结果导向 Hook）**：8-15 个词，清晰说明产品给用户带来的终极价值。
   * *差*：“下一代智能化综合协作平台”
   * *优*：“专为研发团队打造的自动化 API 测试与监控平台”
2. **副标题（Subtitle - 说明交付机制）**：1-2 句话，说明“如何做到”以及“为谁而做”。
   * *示例*：“自动同步 OpenAPI 规范，一键生成全链路断言与告警，无需编写繁重脚本。”
3. **行动按钮（Primary CTA + Friction Reducer）**：
   * 按钮文案：“免费开始使用”、“安装浏览器插件”。
   * 阻力消除文案：“无需绑定信用卡”、“30 秒完成初始化”、“开源且数据本地存储”。

### 3.2 商业模式与功能实质呈现
* **定价与套餐清晰透明（Transparent Pricing）**：
  * 即使当前完全免费，也应标明 “Free Plan / Community Tier”，说明所包含的资源配额与服务边界。
  * 涉及付费订阅时，明确标出月付/年付价格、折扣比例及计费周期。
  * 移动端与桌面端内购严格遵循 Apple 3.1.2 自动续订条款：必须在购买或说明文案中明确标注**扣款时间、续订机制与取消方式**。
* **实体背书与信任模块（About & Social Proof）**：
  * 团队介绍或创始人背景（附真实 LinkedIn/GitHub 主页）。
  * 真实公司名称、注册国家/注册编号、支持邮箱（如 `support@company.com`）。
  * 知名客户 Logo、行业认证或测试用户的真实评语。

### 3.3 权限与数据使用正当性说明（Permission Justification）
若产品是浏览器插件或桌面应用，主页的技术特性或安全说明板块中，必须有显眼的文案解释**为什么需要这些敏感权限**：
* 解释为何需要读取剪贴板、文件系统或特定域名的网络访问，消除用户和审查员的疑虑。

---

## 4. 数据流架构与隐私安全合规（Data Flow & Privacy）

三大应用商店均建立了严格的数据安全透明度审查（Apple Privacy Nutrition Labels、Google Play Data Safety Section、Microsoft App Compliance）。官网展示的信息必须与产品行为完全咬合。

### 4.1 隐私政策与数据收集“三位一体”对齐
* **严格一致性**：官网隐私协议所列的数据收集类别（如设备 ID、位置、账号、支付信息）必须与应用商店后台提交的“数据安全标签”**完全一致**。
* **严禁虚假承诺**：若官网声称“Zero-Log（零日志）”或“End-to-End Encrypted（端到端加密）”，实际网络请求却在向服务端上传明文分析数据，一旦被审核团队网络抓包，将导致全平台下架。

### 4.2 网页端数据收集与 Cookie Consent
* **合规 Consent 管理（CMP）**：
  * 面向欧盟（GDPR）或美国加州（CCPA）访客，必须提供清晰的 Cookie 同意弹窗。
  * **在用户点击“同意”前，严禁静默预加载第三方分析/广告追踪脚本**（如 Google Analytics、Meta Pixel、Microsoft Clarity）。
* **可观测性数据流隔离**：
  * 区分产品业务数据（Business Data）与遥测数据（Telemetry/Metrics）。
  * 提供遥测退出机制（Opt-out Telemetry），在产品设置及官网 FAQ 中公开文档。

### 4.3 账户注销与删除闭环（Account Deletion Workflow）
* 依据 Apple Guideline 5.1.1 与 Google Play 政策，若产品允许用户在线创建账户，官网必须提供：
  1. 公开的永久链接：`https://yourdomain.com/account/delete` 或在个人中心提供直观的“Delete Account”入口。
  2. 明确说明删除范围：身份凭证、历史数据、付费记录的处理时限（如 30 天内彻底抹除）。
  3. 提供无前端客户端情况下的邮件申请渠道（如直接向 `privacy@yourdomain.com` 提交工单）。

---

## 5. 现代 SEO 规范（搜索引擎与自然流量联动）

官网不仅是审查的窗口，更是公网自然流量（Organic Search）与商店 ASO（App Store Optimization）的联动枢纽。

### 5.1 渲染架构原则（SSR / SSG 优先）
* **禁止纯客户端单页白屏（No Client-Side Only Landing Page）**：
  * 官网落地页、博客、功能介绍、定价页**必须采用 SSR（服务端渲染）或 SSG（静态预渲染）**（如 Next.js、Nuxt、Astro）。
  * 确保当禁用浏览器 JavaScript 时，核心 HTML 内容、产品描述、定价文字依然完整可见。

### 5.2 结构化数据标注（JSON-LD Schema.org）
在主页 `<head>` 中注入结构化数据，让 Google / Bing / Apple 抓取并呈现富文本摘要（Rich Snippets）：

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "SoftwareApplication",
      "name": "YourProductName",
      "operatingSystem": "iOS, macOS, Windows, Android, Chrome",
      "applicationCategory": "DeveloperApplication",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "description": "精确且详尽的产品功能定位与价值描述，与主页 H1 和商店 Listing 描述一致。"
    },
    {
      "@type": "Organization",
      "name": "YourCompanyName Inc.",
      "url": "https://yourdomain.com",
      "logo": "https://yourdomain.com/assets/logo.png",
      "sameAs": [
        "https://twitter.com/yourhandle",
        "https://github.com/yourorg",
        "https://linkedin.com/company/yourcompany"
      ],
      "contactPoint": {
        "@type": "ContactPoint",
        "email": "support@yourdomain.com",
        "contactType": "customer service"
      }
    }
  ]
}
</script>
```

### 5.3 社交预览与 Open Graph 卡片
* **规范元标签**：提供标准的 `og:title`, `og:description`, `og:image`, `twitter:card="summary_large_image"`。
* **高精度 OG 图**：尺寸统一为 **1200 x 630 px**，图片上必须清晰包含：**产品 Logo + 核心界面截图 + 强吸引力价值主张**。
* **规范化链接（Canonical Link）**：防止 `https://yourdomain.com` 与 `https://yourdomain.com/?ref=producthunt` 产生内容冲突惩罚。

### 5.4 Core Web Vitals 门禁
* **LCP（Largest Contentful Paint）** < 2.0s（首屏主视觉图加 `fetchpriority="high"`，禁止懒加载）。
* **CLS（Cumulative Layout Shift）** < 0.05（所有图片/视频外层容器写死 `aspect-ratio`，杜绝载入抖动）。
* **INP（Interaction to Next Paint）** < 150ms（优化事件响应与主线程阻塞）。

---

## 6. GEO 规范：大模型 AI 搜索优化（Generative Engine Optimization）

随着 ChatGPT Search、Perplexity、Google AI Overviews、Microsoft Copilot 成为重要流量入口，官网必须针对大模型索引进行针对性优化。

### 6.1 机器极速解析协议：`llms.txt`
在网站根目录下提供标准 `/llms.txt` 和 `/llms-full.txt`，供 AI 检索爬虫（如 GPTBot、PerplexityBot、ClaudeBot）以近乎零成本的 Token 消耗提取核心产品信息：

```markdown
# YourProductName

> 专为 [目标用户] 设计的 [核心功能定义]。解决 [核心业务痛点]，提供 [核心指标/结果]。

## 核心功能与特性
- 特性 1：说明与优势
- 特性 2：说明与优势

## 平台与生态支持
- iOS & macOS: 支持 App Store 下载
- Windows: 支持 Microsoft Store 安装
- 浏览器插件: 支持 Chrome Web Store 与 Edge Add-ons

## 官方链接与资源
- 官网: https://yourdomain.com
- 文档: https://docs.yourdomain.com
- 隐私政策: https://yourdomain.com/privacy
- 服务条款: https://yourdomain.com/terms
- 联系支持: support@yourdomain.com
```

### 6.2 权威定义与数据矩阵（BLUF 原则）
* **结论前置句式**：在产品功能介绍页的第一段，使用标准的直述句：“**[产品名] 是由 [公司名] 研发的 [品类]，主要特性包括 A、B、C。**”——这种句式极易被大模型抓取为直接回答引用源。
* **语义化比较表格（`<table>`）**：在展示功能版本（Free vs Pro vs Enterprise）或竞品差异时，必须使用标准语义 HTML 表格，而非纯 Canvas 或图片。大模型能直接读取表格并生成对比摘要。

---

## 7. GEO 规范：全球化多语言与区域合规（Localization）

面向全球市场或跨国团队审核时，多语言与地域适配是企业级专业度的体现。

### 7.1 多语言路径与 `hreflang` 标头
* **路径规范**：推荐使用子目录模式（如 `yourdomain.com/en/`、`yourdomain.com/zh/`、`yourdomain.com/ja/`），避免子域名权重分散。
* **双向自指 `hreflang`**：
  ```html
  <link rel="alternate" hreflang="en" href="https://yourdomain.com/en/" />
  <link rel="alternate" hreflang="zh-CN" href="https://yourdomain.com/zh/" />
  <link rel="alternate" hreflang="ja" href="https://yourdomain.com/ja/" />
  <link rel="alternate" hreflang="x-default" href="https://yourdomain.com/en/" />
  ```
* **禁止暴力强制跳转**：根据 Geo-IP 识别访客国家时，**仅在界面顶部弹出语言建议横幅**，切勿强行 302 重定向覆盖，否则会导致搜索引擎爬虫只能索引单一语言，并引发用户反感。

### 7.2 排版弹性与 RTL 镜像适配
* **文字长度伸缩**：不同语言翻译后长度剧烈变化（德语、法语、俄语常比英语长 25%~35%）。主页导航栏、按钮、卡片标题严禁设置定宽 `width` 或粗暴的 `overflow: hidden`，必须使用弹性自适应（`flex-wrap` 或 `min-width`）。
* **CSS 逻辑属性替代物理属性**：为支持阿拉伯语、希伯来语等从右向左（RTL）阅读的语种：
  * 用 `margin-inline-start / margin-inline-end` 替代 `margin-left / margin-right`。
  * 用 `padding-inline` 替代 `padding-left / padding-right`。
  * 浮动图标与箭头根据 `dir="rtl"` 自动 CSS 镜像翻转（`transform: scaleX(-1)`）。

---

## 8. Production-Ready Checklist（交付与上线自检清单）

在将官网 URL 填入 Google for Startups 申请表、Apple App Store Connect、Google Play Console 或 Microsoft Partner Center 之前，必须逐一验证以下验收项：

### 8.1 资质与审核硬性门禁（Verification & Anti-Rejection）
- [ ] **域名主体对齐**：使用独立域名，绝非免费二级域名或 Notion 页面；申请人邮箱为 `@yourdomain.com` 域名企业邮箱。
- [ ] **全球直连畅通**：使用境外 VPN/测试节点模拟欧美访问，页面在 2 秒内完整呈现，无 5 秒盾强拦截或 CDN 误封。
- [ ] **实质性内容验证**：绝无 "Coming Soon" 或 Lorem Ipsum；首屏有直观的高保真界面、交互动图或试用入口。
- [ ] **法律四件套常驻**：Privacy Policy、Terms of Service、Account Deletion、Support 链接在页脚 100% 存活且内容完备。
- [ ] **公司实体真实存在**：包含公司正式名称、注册编号、物理或联系地址，以及真实团队或创始人资料背书。

### 8.2 品牌与应用商店徽标门禁（Brand & Store Badges）
- [ ] **官方徽标零修改**：App Store、Google Play、Microsoft Store 徽标使用官方最新原版矢量，尺寸与留白达标。
- [ ] **跳转与追踪对齐**：点击商店徽标能正确跳转至已发布或预购状态的商店页面，附带 UTM 归因参数。
- [ ] **无越权商标声明**：没有在未经授权的情况下声称获得 Google/Apple/Microsoft 官方背书或认证。
- [ ] **真机比例正确**：截图模型遵循 Apple HIG、Material Design 3 或 Windows Fluent 最新外壳与交互元素。

### 8.3 文案与商业对齐门禁（UX Writing & Business）
- [ ] **首屏 5 秒法则**：主标题直击价值，副标题说明机制，行动按钮（CTA）清晰且包含强动词。
- [ ] **订阅/内购透明公示**：定价清晰展示，遵循自动续订条例（标明计费周期、金额、续订时机与取消指引）。
- [ ] **敏感权限正当性说明**：清晰解释产品所申请系统/浏览器敏感权限的具体用途。

### 8.4 数据流与隐私门禁（Data Flow & Privacy）
- [ ] **三位一体对齐**：官网隐私政策所披露的数据采集项与商店后台 Privacy Nutrition Labels / Data Safety 完全吻合。
- [ ] **真实零欺诈**：未虚构“端到端加密”或“零日志”；遥测行为公开并支持 Opt-out。
- [ ] **Cookie CMP 机制**：欧盟/加州 IP 下，未点击同意前不静默发起第三方追踪。
- [ ] **注销闭环完备**：具备公开的账户与数据删除流程指引或一键申请通道。

### 8.5 SEO、GEO 与全球化门禁（SEO, GEO & i18n）
- [ ] **服务端直出（SSR/SSG）**：禁用 JS 后核心文字、定价、功能介绍依然可完整阅读。
- [ ] **结构化数据生效**：`SoftwareApplication` 与 `Organization` 的 JSON-LD 经 Google 富媒体测试工具检验无错误。
- [ ] **Open Graph 卡片就绪**：1200x630 动态 OG 图片包含 Logo、标语与高保真产品图。
- [ ] **大模型检索友好**：根目录提供规范的 `/llms.txt`，功能列表采用标准语义 HTML 表格。
- [ ] **多语言与 RTL**：多语言配置正确的 `hreflang`，不搞暴力 302 重定向，支持 CSS 逻辑属性。
- [ ] **Web Vitals 全绿**：PageSpeed Insights 移动端与桌面端体验指标达标（LCP < 2.0s, CLS < 0.05）。
