---
name: ai-news-md-digest
description: "采集最新 AI 资讯并输出 Markdown 文件。Use when the user asks to collect recent AI/AI Agent/news items and save them as md artifacts."
---

# AI News Markdown Digest Workflow

Use this workflow for requests like "采集最新AI资讯，保存在md文件".

## Output Contract

Final deliverables must stay inside the current XWorkmate/OpenClaw task artifact scope:

- `reports/ai-news-digest.md`
- `reports/sources.md`
- `DELIVERY.md`

Do not report success unless `reports/ai-news-digest.md` exists and contains dated source links.

## Workflow

1. Verify the current date and collect recent AI news from reliable sources.
2. Prefer primary or reputable sources: official announcements, research labs, major tech media, GitHub releases, and company blogs.
3. Write `reports/ai-news-digest.md` with headline, date, source URL, summary, and why it matters.
4. Write `reports/sources.md` with all source links and access dates.
5. Keep browser caches, downloaded screenshots, and scratch JSON outside final artifacts unless the user asks for evidence files.

## Validation

Before final response:

```bash
test -s reports/ai-news-digest.md
test -s reports/sources.md
find . -maxdepth 3 -type f | sort
```

