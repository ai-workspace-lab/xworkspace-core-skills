---
name: image-svg-pptx-pro
version: 1.0.0
description: Convert PPT screenshots, academic images, UI mockups, and report pages into a high-fidelity SVG intermediate, then reconstruct a mixed editable PowerPoint file with SVG/PNG fallbacks and optional VBA helpers.
---

# Image → SVG → Editable PPTX Pro Skill

Use this skill when the user wants to turn a raster image, PPT screenshot, academic figure, UI screen, poster, report page, or AI-generated PPT image into a PowerPoint file that is as editable as possible while preserving visual fidelity.

The core route is:

`source image → normalized image → semantic layout plan → high-fidelity SVG → editable PPTX reconstruction → QA comparison → correction pass`

This skill is intentionally **not** a naive OCR-to-PPT workflow. It uses SVG as the stable intermediate representation because SVG can encode precise geometry, typography, image crops, vector primitives, and fallbacks before converting to Office shapes.

## Output targets

Always produce, when possible:

1. `reconstructed.pptx` — main deliverable; editable PowerPoint.
2. `reconstruction.svg` — high-fidelity intermediate source.
3. `layout_plan.json` — editable semantic layout plan.
4. `assets/` — cropped image/logo/icon/screenshot regions.
5. `qa_report.md` — visual and editability assessment.
6. Optional `macros/insert_svg_fallback.bas` — VBA helper for inserting SVG or fallback objects.

## Operating principle

Prioritize final usefulness, not theoretical editability.

- Convert text, headings, cards, boxes, dividers, simple charts, arrows, bullets, tables, and simple icons into editable PowerPoint elements.
- Preserve complex photos, dense screenshots, logos, decorative illustrations, complex icons, gradients, and complicated path art as cropped image assets or SVG fallback groups.
- Never redraw a complex logo/icon if it will visibly degrade. Crop it from the source image and position it precisely.
- Never stretch text horizontally to match a screenshot. Use font size, letter spacing approximation, box width, and line breaks instead.
- For Chinese slides, prefer legibility and correct text over forced font matching.

## Quality modes

When the user does not specify a mode, use `balanced`.

### balanced
Best default. Core text and structure editable; complex visual regions preserved as cropped assets.

### max_editable
Use when the user explicitly wants more editable elements. Vectorize more lines, charts, and simple icons. Still keep complex logos/photos as assets.

### visual_locked
Use when fidelity is more important than editing. Put a full-slide image/SVG fallback underneath or as grouped locked visual, then overlay editable text and key elements.

## Workflow

### 1. Normalize the source

Run:

```bash
python scripts/preprocess_image.py input.png --out work/normalized.png --meta work/source_meta.json
```

If the input is a phone photo of a screen, deskew/crop it first if needed. Keep the original file unchanged.

### 2. Build `layout_plan.json`

Use visual reasoning to decompose the normalized image into semantic layers. Follow `references/layout_plan_schema.md`.

The plan must include:

- canvas width and height in pixels.
- slide aspect ratio.
- background color or background image.
- text elements with exact text, x/y/w/h, font size, weight, color, alignment, line breaks.
- vector elements: rectangles, rounded rectangles, lines, arrows, circles, charts, tables.
- asset crop regions: photos, logos, screenshots, complex icons, decorative art.
- z-order.
- editability intent: `editable`, `asset`, or `fallback`.

Do not invent unreadable text. Mark uncertain text as `needs_review: true`.

### 3. Crop assets

Run:

```bash
python scripts/crop_assets.py work/normalized.png work/layout_plan.json --out work/assets
```

Complex image regions referenced in the plan must point to these cropped files.

### 4. Generate SVG

Run:

```bash
python scripts/plan_to_svg.py work/layout_plan.json --assets work/assets --out work/reconstruction.svg
```

The SVG is the canonical visual intermediate. Inspect or render it before generating PPTX.

### 5. Convert SVG/plan into editable PPTX

Prefer plan-based PPTX generation, because it preserves semantics better than arbitrary SVG parsing.

```bash
python scripts/plan_to_pptx.py work/layout_plan.json --assets work/assets --out work/reconstructed.pptx
```

If the plan is unavailable but an SVG exists, use the SVG parser fallback:

```bash
python scripts/svg_to_pptx_editable.py work/reconstruction.svg --out work/reconstructed.pptx
```

### 6. QA and correction pass

Create `qa_report.md` using `references/quality_checklist.md`.

Check:

- title hierarchy and position.
- text correctness, especially Chinese characters and numbers.
- margins and card alignment.
- colors and background balance.
- line thickness and rounded corner radius.
- whether logos/icons degraded.
- whether generated PPTX is actually editable for the main elements.

If the visual mismatch is obvious, update `layout_plan.json` and regenerate. Do not present the first broken result as final.

## Recommended user-facing command

When the user gives an image and asks for conversion, proceed without asking follow-up unless required files are missing. Say briefly what files were produced and link the PPTX/ZIP.

## Failure handling

If exact text is unreadable, do not hallucinate it. Use cropped image fallback for the region and flag it in `qa_report.md`.

If SVG-to-PPTX direct conversion loses filters, masks, gradients, or paths, keep those regions as cropped assets and overlay editable text/shapes.

If the user needs a fully editable corporate deck, tell them which elements remain image-based and why.
