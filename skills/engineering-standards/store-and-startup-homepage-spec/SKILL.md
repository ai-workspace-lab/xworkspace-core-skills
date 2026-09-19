---
name: store-and-startup-homepage-spec
description: 公司官网与产品主页的审核就绪规范（项目级标准）。凡修改公开官网、产品页、页脚/联系方式、边缘路由（CDN Worker/WAF/DNS）或发布流水线，都必须满足 Google（Startups / Play / Android）、Apple（Developer / App Store）、Microsoft 的公司与应用审核对官网的要求；也用于审核被拒（"did not match your company domain"、"insufficient company information"）后的根因定位。覆盖品牌域名边界、30 秒审核事实、真实性红线、首页/产品页结构、单一身份配置源、合规入口、可抓取性、商店对照表、部署后 post-check 清单与自动化自检。
---

# Store and Startup Homepage Spec

目标：审核员（人工或爬虫）打开品牌域名首页 30 秒内，**不离开该域名**，就能确认"公司真实、产品真实、可以使用、仍在开发"。本规范是项目标准：相关改动的 PR 必须过第 8 节自检，发布流水线必须带第 9 节 post-check。

## 1. 30 秒审核事实

首屏加一次滚动内回答以下问题，每个都要有**同域可点击的证据**：

| 问题 | 首页必须出现的证据 |
| :--- | :--- |
| Who are you? | 法人全称（与申请表一致）：首屏或紧邻区块 + 页脚 `© {year} {Legal Name}` |
| What are you building? | H1 = 主产品名 + 一句话价值；只有一个主推产品 |
| Is there a real product? | 真实界面截图 / 演示 / 文档，链接到 `/products/<slug>` |
| Can I use it? | 主 CTA（Start free / Download），目标页可匿名打开 |
| Is the company real? | About / Contact / Terms / Privacy + 同域邮箱 |
| Is development active? | 公开 GitHub 仓库、最新 Release、Changelog / Blog |

## 2. 域名边界（被拒最常见的根因）

- **品牌域名承载全部公开页面**：首页、`/products/*`、定价、下载、文档、博客、支持、法务都在品牌域名直接返回 200，**不得任何 3xx**（跳到平台域名固然不行，跳到自己的别的页面也让"文档"入口变成假入口）。
- **只有账户、在线应用与 API 可留在平台域名**：登录、注册、控制台、在线工作空间应用（浏览器内同源调用 `/api/*`）与 `/api/*` 本身，其 Cookie、OAuth 回调、CORS 都绑定在平台主机上，可以跳转。放开品牌域名路由前，先看平台侧已有的边界校验（如发布流水线的 public-chain 检查）锁定了哪些路径必须跳转。
- **先查边缘层**：跳转常来自 CDN Worker / 边缘路由的"品牌域名白名单"，而非应用代码。对首页每个导航链接 `curl -sI`，看 `Location` 与响应头来源。
- **WAF 不得拦截公开页**：公开路径关闭 Managed Challenge / Under Attack / Bot Fight；已知合规爬虫（Googlebot、Applebot、bingbot）走 Bypass。被拦时爬虫只拿到 403 + `noindex` 的质询页。
- **Apex 与 www 都要解析**并各有证书，其中一个 301 到另一个。
- **遗留域名 = 死链**：已无 DNS 的旧域名（含 `www.` 变体）不得出现在 canonical、sitemap、JSON-LD 或任何链接里。

## 3. 真实性红线

审核对"不实"比对"简陋"更敏感：

- 不自称 "Verified / 官方认证"，除非第三方确实授予。
- 概念图、设计稿标 "Overview / 预览"，不得标"真实界面 / Real UI"；尽量补真实截图。
- 可用性矩阵只列已发布制品实际覆盖的平台与格式（以 Release 资产清单为准）。
- JSON-LD、`llms.txt` 的平台、价格、描述必须与页面一致。
- 公开邮箱只用已确认能收信的同域邮箱，不要为了"好看"新造 `legal@` 之类。
- 不删现有产品页来"变干净"；修正死链即可（业务方明确下线除外）。

## 4. 页面结构

**首页**（一页一个主叙事）：Header（Logo、产品、定价、文档、About、Sign in + 主 CTA）→ Hero（主产品名 H1、价值主张、主/次 CTA、真实产品图、"by {Legal Name}"）→ Proof（真实截图 + 可用平台）→ 产品矩阵（每个产品链接站内 `/products/<slug>`）→ 定价入口 → Company block（Built by + About/Contact/GitHub）→ Footer（产品/资源/公司/法务列，`© {year} {Legal Name}`，GitHub）。

**产品页** `/products/<slug>`：Hero → What it is → Problem（3 条）→ How it works（3–4 步）→ Screenshots → Availability → Source & Downloads（公开仓库 + `releases/latest`）→ Get started。每段由服务端渲染出正文。

**文档入口** `/docs`：必须是渲染真实内容的页面（文档集合 + 仓库/README 入口），且在文档服务不可达时仍有兜底内容；不得重定向。

## 5. 单一身份配置源

- 法人全称、站点 URL、支持邮箱、GitHub 组织、产品→仓库/Release 映射集中在一个模块（如 `src/lib/company.ts`），组件、元数据、JSON-LD 都从这里读。
- 站内链接用根相对路径；绝对 URL 只用于 canonical、sitemap、OG，域名取自配置。
- 链接只能指向实际存在的路由。

## 6. 合规入口与可抓取性

- 页脚常驻 Privacy、Terms、Contact/Support（同域邮箱）；支持注册的产品提供网页版账户删除说明/入口。
- 首页、产品页、定价、文档用 SSR/SSG；禁用 JS 时核心文字、公司名、联系方式仍可见。
- 根布局注入 `@graph` JSON-LD：`Organization`（name、url、logo、sameAs、contactPoint）+ 主产品 `SoftwareApplication` + `WebSite`。
- `robots.txt` 不得 `Disallow: /`；`sitemap.xml` 只列品牌域名上的公开页面；可选 `/llms.txt`。

## 7. 商店与账号审核对照（Google / Apple / Android）

各平台细则会变，提交前以官方最新要求为准；下表是官网侧通常被检查的点，以及本规范对应位置。

| 平台 | 通常检查的官网侧要求 | 对应 |
| :--- | :--- | :--- |
| Google for Startups / Cloud | 官网可直接访问、公司身份与申请一致、同域联系邮箱、有实质产品内容 | §1、§2、§3 |
| Google Play / Android | 组织开发者账号的法人名称与官网一致；商品页填写的开发者网站、联系邮箱可公开访问；隐私政策为公开网页（非 PDF、不需登录）；支持注册的应用提供网页版账户删除入口并与 Data safety 声明一致 | §1、§6 |
| Apple Developer / App Store | 组织注册的法人实体与官网、同域邮箱匹配；App 的 Support URL（含真实联系方式）与 Privacy Policy URL 必填，Marketing URL 可选；支持注册的应用需账户删除（Guideline 5.1.1） | §1、§6 |
| Microsoft Founders Hub / Store | 官网与公司信息一致，产品页有实质内容 | §1、§3 |

商店后台里填写的 Website / Support / Privacy URL 必须与官网现有路径逐字一致（人工核对，部署后每次变更路由都要重查）。

## 8. 自检（PR 门禁）

仓库内附带两层检查，并接入 CI：

- **守卫测试**（单元测试扫描公开源码目录）：无个人邮箱、无遗留品牌/版权主体、无遗留或无 DNS 的域名、无已知死链模式；每个产品登记了仓库与下载。
- **线上探针脚本**（`--remote`）：按第 9 节清单探测已部署站点。

## 9. 部署后 Post-check 清单（流水线）

每次部署品牌域名所在的边界（边缘路由、SSR 公共/内容边界、Pages）后，流水线的 post-check 必须逐条通过；失败阻断发布，Cloudflare 质询这类"runner 视角"的项只告警（严格模式可转为失败）：

| # | 检查 | 失败含义 |
| :-: | :--- | :--- |
| 1 | `/ /about /contact /terms /privacy /support /products/* /prices /download /docs /blogs` 全部 200，无任何 3xx | 页面跳出品牌域名或入口是假入口 |
| 2 | 首页含法人全称，页脚无遗留版权主体 | 身份与申请不一致 |
| 3 | `/contact`、`/support` 只出现同域邮箱，无个人邮箱；`/contact` 至少有一个同域地址 | 邮箱与公司域名"对不上" |
| 4 | `robots.txt` 200 且不 `Disallow: /`；`sitemap.xml` 有 `<loc>` | 爬虫无法收录 |
| 5 | 公开路径无 Cloudflare 质询（爬虫 UA 探测） | 审核程序只拿到 403 空壳（默认告警） |
| 6 | `www.<apex>` 有解析并跳转 | 申请表填 `www` 时打不开（默认告警） |
| 7 | 商店后台 Website/Support/Privacy URL 与官网路径一致 | 人工核对，非自动 |

实现：`platform-ops-toolkit` 的 `scripts/serverless_uat/verify_brand_site_review_readiness.sh`（serverless 编排 `serverless_domains` 之后运行，契约测试见 `.github/scripts/tests/serverless_brand_site_review_readiness_test.sh`）；本地/手动用 portal 的 `scripts/verify-company-site.sh --remote`。可用环境变量覆盖：`BRAND_LEGAL_NAME`、`BRAND_EMAIL_DOMAIN`、`BRAND_PUBLIC_PATHS`、`BRAND_CHECK_STRICT`。

手工探针：

```bash
UA="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
for p in / /about /contact /terms /privacy /products/<slug> /prices /download /docs; do
  curl -sS -o /dev/null -A "$UA" -w "%{http_code} %{redirect_url}  $p\n" "https://<brand-domain>$p"
done   # 期望全部 200 且无 Location
curl -sSL -A "$UA" https://<brand-domain>/ | grep -c "Just a moment"   # 期望 0
```

## 10. 被拒后的处理顺序

1. 用第 9 节探针复现审核员路径，找出所有跳出品牌域名的链接和 403。
2. 先修边缘路由 / WAF / DNS，再修页面内容和身份一致性。
3. 探针全部通过后，**回复原审核邮件请求重新处理**已有申请，而不是重复提交新申请。
