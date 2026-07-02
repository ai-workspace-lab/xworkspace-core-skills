# Optimized Technical Route: Image → SVG → Editable PPTX

## Why SVG intermediate works better

A direct image-to-PPT workflow often fails because the agent has to decide visual reconstruction and PowerPoint implementation at the same time. SVG separates the problem into two layers:

1. **Visual reconstruction layer**: represent the slide accurately with coordinates, text, fills, strokes, clipped assets, and z-order.
2. **Office reconstruction layer**: map supported SVG/layout elements to native PowerPoint shapes.

This reduces layout drift and makes debugging easier. If the PPTX is wrong, inspect the SVG first. If the SVG is right but PPTX is wrong, fix the converter. If the SVG is wrong, fix the layout plan.

## Recommended architecture

```text
source.png
  ↓ preprocess_image.py
normalized.png + source_meta.json
  ↓ visual/semantic reasoning
layout_plan.json
  ↓ crop_assets.py
assets/*.png
  ↓ plan_to_svg.py
reconstruction.svg
  ↓ plan_to_pptx.py / svg_to_pptx_editable.py
reconstructed.pptx
  ↓ QA
qa_report.md + corrected layout_plan.json
```

## Three-layer reconstruction strategy

### Layer A — editable structure

Use native PPT shapes for:

- background rectangles and bands.
- title/subtitle/body text.
- card containers.
- dividers and connector lines.
- tables.
- simple bar/line charts.
- simple icons made from circles/rectangles/lines.

### Layer B — SVG vector fidelity

Use SVG for:

- precise decorative vector patterns.
- simple but tedious icon/path art.
- mask/clip-path regions where PowerPoint approximation is acceptable.

### Layer C — cropped asset fidelity

Use cropped PNG assets for:

- photographs.
- screenshots.
- logos.
- dense charts.
- complex icons.
- AI-generated illustration fragments.
- unreadable or uncertain text blocks that should not be hallucinated.

## Quality policy

Best result usually comes from **mixed editability**, not maximum editability.

- A 90% editable slide that looks correct is better than a 100% editable slide that looks cheap.
- Main narrative text must be editable.
- Complex image/logo regions should stay visually faithful.
- If a chart is too dense, use image fallback and optionally rebuild the key labels as editable overlay.
