---
name: evolutionary-social-copy-pack
description: "根据用户指定的任意演进主线，输出公众号、小红书、X、头条号等 Markdown 软文矩阵。"
---

# Security Evolution Social Copy Pack Workflow

Use this workflow for content-pack requests around user-provided evolutionary paths or thematic series.

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

- Keep the same core thesis across all files based on the user-provided theme or sequence.
- Weave in relevant soft keywords naturally depending on the theme context.
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

