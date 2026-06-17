---
name: security-evolution-social-copy-pack
description: "围绕单机权限到 AI 模型与知识保护的安全演进主线，输出公众号、小红书、X、头条号等 Markdown 软文矩阵。"
---

# Security Evolution Social Copy Pack Workflow

Use this workflow for content-pack requests around:

`从单机权限 → 网络边界 → Web安全 → 云身份 → Zero Trust → AI Agent 身份 → AI模型与知识保护`

## Output Contract

Final deliverables must stay inside the current XWorkmate/OpenClaw task artifact scope:

- `reports/wechat-short.md`，微信公众号短图文，400-600 中文字，插入关键词软文
- `reports/xiaohongshu.md`，小红书风格，600-800 中文字，插入钩子话题
- `reports/x-thread.md`，English X copy thread，每条小于 144 characters，观点鲜明
- `reports/wechat-article.md`，微信公众号文章，800-1200 中文字
- `reports/toutiao-long.md`，头条号长文，800-1200 中文字
- `DELIVERY.md`

Do not combine the five outputs into one Markdown file. Each platform gets one standalone `.md` file.

## Writing Rules

- Keep the same core thesis across all files: security boundaries keep moving closer to identity, agents, models, and knowledge.
- Weave in soft keywords naturally: `Zero Trust`, `AI Agent 身份`, `模型保护`, `知识资产保护`, `云身份`, `Web安全`.
- For Xiaohongshu, start with a strong hook and include 3-5 topic tags.
- For X, write in English and keep every post under 144 characters.
- Avoid fake citations and avoid claiming current news unless sources were collected in the same run.

## Validation

Before final response:

```bash
test -s reports/wechat-short.md
test -s reports/xiaohongshu.md
test -s reports/x-thread.md
test -s reports/wechat-article.md
test -s reports/toutiao-long.md
find reports -maxdepth 1 -type f | sort
```

