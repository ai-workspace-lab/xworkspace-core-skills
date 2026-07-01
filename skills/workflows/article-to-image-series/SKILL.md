---
name: article-to-image-series
description: "文章转图片系列工作流：将文章、提纲或主题序列转成风格一致的多图系列。Workflow skill for converting an article, outline, or topic sequence into a coherent multi-image series; use for one image per chapter, article illustrations, infographic series, Xiaohongshu-style cards, or manifest-backed image sets."
---

# Article To Image Series Workflow

This workflow turns text structure into a validated image series. It is intentionally staged so the agent plans image count and prompts before generating assets.

Before generating, extending, repairing, or repainting any image, read [../../marketplace/pptx/editable-reconstruction.md](../../marketplace/pptx/editable-reconstruction.md) and apply its provider order, text-free generation, and residue QA rules. Image models must not render titles, labels, numbers, signatures, watermarks, or pseudo-text. Keep chapter titles and captions outside the generated bitmap; if final cards require embedded typography, typeset it in an editable HTML/SVG source and render the composed PNG deterministically.

## Output Contract

Final deliverables must stay inside the current task artifact scope:

- `workflow.plan.md`
- `series.config.json`
- `prompts/image-prompts.md`
- `assets/images/*.png`
- `assets/images/manifest.md`
- `DELIVERY.md`

## Phase 1: Parse Source

Read the user input and identify:

- topic or article title
- narrative line
- target audience
- chapter or card count
- style requirements
- any required reference images or source URLs

If no count is given, choose a compact 3-7 image series based on the narrative.

## Phase 2: Series Plan

Write `workflow.plan.md` and `series.config.json`.

Each image entry must define:

- `chapter_id`
- `title`
- `subtitle`
- core message
- visual metaphor
- key labels
- output path under `assets/images/`

Do not ask an image model for a batch collage. One entry means one standalone output file.

## Phase 3: Prompt Pack

Write `prompts/image-prompts.md` with one prompt per image.

Prompts must keep a consistent family style while preserving per-chapter meaning. Avoid generic cyberpunk, stock-style, and unreadable text-heavy visuals.

## Phase 4: Generate Images

Generate or edit images one by one. Save each final PNG under `assets/images/`.

Generate the visual plate without text. If the output format requires text inside the final card, add it only through the deterministic editable layout source after the text-free plate passes inspection.

If an image tool writes to a cache directory, copy the final image into the artifact scope. Do not leave final outputs in `Downloads`, model cache, `/tmp`, or global media folders.

## Phase 5: Manifest And Validation

Write `assets/images/manifest.md` with one row per image.

Required checks:

- PNG count equals manifest row count.
- Every manifest `file` exists and is a real PNG.
- No manifest file path points outside the artifact scope.
- No generated image is a combined grid, contact sheet, or storyboard unless explicitly requested.

Stop on validation failure and report the missing or invalid image file.
