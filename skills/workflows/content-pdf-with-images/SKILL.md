---
name: content-pdf-with-images
description: "图文 PDF 工作流：将主题或文章拆成章节，为每章生成配图，并汇总排版为真实 PDF。Workflow skill for turning a topic or article request into a chaptered PDF with one image per chapter; use for illustrated PDF reports, chapter images, and final PDFs assembled from text plus generated images."
---

# Content PDF With Images Workflow

This is an orchestration skill. It does not replace planning, image, or PDF skills. It forces a staged handoff so the final artifact is a real PDF with real image inputs, not a placeholder file.

## Output Contract

Final deliverables must stay inside the current XWorkmate/OpenClaw task artifact scope:

- `workflow.plan.md`
- `article.md`
- `assets/images/*.png`
- `assets/images/manifest.md`
- `prompts/image-prompts.md`
- `series.config.json`
- `exports/final.pdf`
- `DELIVERY.md`

## Phase 1: Plan

Create `workflow.plan.md` before writing final content. It must include:

- topic and audience
- chapter list
- target word or character count
- one image concept per chapter
- downstream skill sequence
- final acceptance checklist

If the user gives an explicit chapter sequence, preserve it literally.

## Phase 2: Article

Write `article.md` with:

- title
- one section per planned chapter
- concise intro and closing summary
- total length matching the user request

Do not claim completion after this phase.

## Phase 3: Images

Use the image-series skill path for one standalone PNG per chapter.

Required checks before continuing:

- PNG count equals chapter count.
- Every `assets/images/*.png` is a real non-empty PNG.
- `assets/images/manifest.md` exists and references only relative paths inside the artifact scope.
- `prompts/image-prompts.md` and `series.config.json` exist.

If any check fails, stop and report the missing image artifact. Do not generate a placeholder PDF.

## Phase 4: PDF

Use the PDF creation path to assemble `article.md` plus image manifest into `exports/final.pdf`.

The PDF must contain:

- title page
- chapter text
- matching chapter image near each section
- closing summary

Use a PDF library such as reportlab when available. The file must be large enough to plausibly contain text and images; a tiny one-page placeholder PDF is a failure.

## Phase 5: Delivery Check

Before final response, run equivalent checks:

```bash
find . -maxdepth 4 -type f | sort
file exports/final.pdf
pdfinfo exports/final.pdf
pdftotext exports/final.pdf - | head -40
```

Only report success if `exports/final.pdf` exists and the expected source files are present.
