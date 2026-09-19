---
name: store-and-startup-homepage-spec
description: 公司官网与产品主页的审核就绪规范。用于面向 Google for Startups / Google Play / Apple Developer / Microsoft for Startups 等公司或应用审核的官网设计、改版、排障与上线自检；也用于审核被拒（如 "did not match your company domain"、"insufficient company information"）后的根因定位。覆盖品牌域名边界、30 秒审核事实、首页与产品页结构、真实性红线、单一身份配置源、合规入口、SSR/结构化数据与自动化自检。
---

# Store and Startup Homepage Spec

目标：审核员（人工或爬虫）打开品牌域名首页 30 秒内，不离开该域名，就能确认"公司真实、产品真实、可以使用、仍在开发"。

## 1. 30 秒审核事实

首页首屏加一次滚动内必须回答以下问题，每个问题都要有**同域可点击的证据**：

| 问题 | 首页必须出现的证据 |
| :--- | :--- |
| Who are you? | 法人全称（与申请表一致），出现在首屏或紧邻区块及页脚 `© {year} {Legal Name}` |
| What are you building? | H1 = 主产品名 + 一句话价值；只有一个主推产品 |
| Is there a real product? | 真实界面截图 / 演示入口 / 文档，链接到 `/products/<slug>` |
| Can I use it? | 主 CTA（Start free / Download），目标页可匿名打开 |
| Is the company real? | About / Contact / Terms / Privacy + 同域邮箱 |
| Is development active? | 公开 GitHub 仓库、最新 Release、Changelog / Blog |

## 2. 域名边界（被拒最常见的根因）

- **品牌域名承载全部公开页面**：首页、`/products/*`、定价、下载、文档、博客、支持、法务都必须在品牌域名直接返回 200，不得 3xx 到平台或服务域名。
- **只有账户、在线应用与 API 可留在平台域名**：登录、注册、控制台、在线工作空间应用（浏览器内同源调用 `/api/*`）以及 `/api/*` 本身，其 Cookie、OAuth 回调和 CORS 都绑定在平台主机上，可以跳转；营销导航、产品介绍、定价、下载、文档则不行。放开品牌域名路由前，先确认平台侧现有的边界校验（如发布流水线里的 public-chain 检查）锁定了哪些路径必须跳转。
- **先查边缘层**：跳转常来自 CDN Worker / 边缘路由的"品牌域名白名单"（只放行少数路径，其余一律 302 到平台），而不是应用代码。排查方法：对首页每个导航链接执行 `curl -sI`，看 `Location`，并看响应头是否来自应用（如 `x-powered-by`）。
- **WAF 不得拦截公开页**：对公开路径关闭 Managed Challenge / Under Attack / Bot Fight；已知合规爬虫走 Bypass。被拦截时爬虫只拿到 403 + `noindex` 的质询页。
- **Apex 与 www 都要解析**：`www` 301 到 Apex（或相反），两者都有证书。
- **遗留域名 = 死链**：已无 DNS 的旧域名（含 `www.` 变体）不得出现在 canonical、sitemap、JSON-LD 或任何链接中。

## 3. 真实性红线（不得夸大）

审核对"不实"比对"简陋"更敏感：

- 不自称 "Verified / 官方认证"，除非第三方确实授予过。
- 概念图、设计稿不得标注为"真实界面 / Real UI"；标注为 "Overview / 预览"，并尽量补真实截图。
- 平台可用性矩阵只列已发布制品实际覆盖的平台和格式（以 Release 资产清单为准，如 `.dmg / .zip / .deb / .rpm / .apk`）。
- JSON-LD、`llms.txt` 中的平台、价格、描述必须与页面一致。
- 公开邮箱只用已确认能收信的同域邮箱，不要为了"好看"新造 `contact@` / `legal@`。
- 不删除现有产品页来"变干净"；修正其死链即可（除非业务方明确下线）。

## 4. 首页结构

按顺序，一页一个主叙事：

1. **Header**：品牌 Logo（链接 `/`）、产品、定价、文档、About；右侧 Sign in（可跨到平台域名）+ 主 CTA。
2. **Hero**：主产品名 H1、一句价值主张、主 CTA + 次 CTA（下载 / 查看源码）、真实产品图、一行公司归属 "by {Legal Name}"。
3. **Proof**：真实截图或短演示；可用平台（与第 3 节一致）。
4. **Product matrix**：每个产品一张卡片，一律链接站内 `/products/<slug>`。
5. **Pricing teaser**：链接 `/prices`（或站点实际定价路由）。
6. **Company block**：`Built by {Legal Name}` + About / Contact / GitHub。
7. **Footer**：产品、资源、公司、法务列；`© {year} {Legal Name}`；GitHub。

## 5. 产品页结构（`/products/<slug>`）

Hero → What it is → Problem（3 条）→ How it works（3–4 步）→ Screenshots → Availability → Source & Downloads（公开仓库 + `releases/latest`）→ Get started。每一段都要由服务端渲染出正文。

## 6. 单一身份配置源

- 法人全称、站点 URL、支持邮箱、GitHub 组织、产品→仓库/Release 映射集中在一个模块中（如 `src/lib/company.ts`），组件、元数据、JSON-LD 统一从这里读取。
- 站内链接一律用根相对路径；绝对 URL 只用于 canonical、sitemap、OG 等要求绝对地址的字段，且域名取自配置。
- 路由以代码为准：链接只能指向实际存在的路由（如定价是 `/prices` 就不能出现 `/pricing/...`）。

## 7. 合规入口

页脚常驻：Privacy、Terms、Contact/Support（同域邮箱）；支持注册的产品还需提供账户删除入口（Apple 5.1.1、Google Play 要求）。

## 8. 可抓取性

- 首页、产品页、定价、文档采用 SSR/SSG；禁用 JS 时核心文字、公司名、联系方式仍然可见。
- 根布局注入 `@graph` JSON-LD：`Organization`（name、url、logo、sameAs、contactPoint）+ 主产品 `SoftwareApplication` + `WebSite`。
- sitemap 只列品牌域名上的公开页面；可选提供 `/llms.txt` 事实摘要。

## 9. 自动化自检（上线门禁）

仓库内附带两层检查，并接入 CI：

**本地守卫测试**（单元测试扫描公开源码目录）：无个人邮箱（`@gmail.com` 等）、无遗留品牌 / 版权主体、无遗留或无 DNS 的域名、无已知死链模式；每个产品都登记了仓库和下载。

**线上探针**（脚本，`--remote`）：

```bash
UA="Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
for p in / /about /contact /terms /privacy /products/<slug> /prices /download /docs; do
  curl -sS -o /dev/null -A "$UA" -w "%{http_code} %{redirect_url}  $p\n" "https://<brand-domain>$p"
done   # 期望全部 200；任何跳出品牌域名的 3xx 都算失败
curl -sSL -A "$UA" https://<brand-domain>/ | grep -c "Just a moment"      # 期望 0
curl -sSL -A "$UA" https://<brand-domain>/ | grep -c "<Legal Name>"       # 期望 >0
curl -sI https://www.<brand-domain>/ | grep -iE "^HTTP/.* 30[18]|^location"
```

## 10. 被拒后的处理顺序

1. 用第 9 节的探针复现审核员路径，找出所有跳出品牌域名的链接和 403。
2. 先修边缘路由 / WAF / DNS，再修页面内容和身份一致性。
3. 探针全部通过后，**回复原审核邮件请求重新处理**已有申请，而不是重复提交新申请。
