# Prompts for creating layout_plan.json

## Full reconstruction prompt

Analyze the source slide image and create a precise `layout_plan.json` for image-to-SVG-to-editable-PPT reconstruction.

Requirements:

1. Use the preprocessed image coordinate system in pixels.
2. Identify background, title, subtitle, body text, cards, lines, tables, charts, icons, photos, screenshots, and logos.
3. Main text must be editable. Preserve exact wording and line breaks.
4. Complex visual regions must be marked as crop assets instead of redrawn.
5. Use z-order.
6. Use `needs_review: true` for uncertain text.
7. Use `editability: editable`, `asset`, or `fallback`.
8. Output valid JSON only.

## Correction prompt after QA

Compare the generated SVG/PPT preview with the source image. Update `layout_plan.json` only where necessary:

- adjust x/y/w/h coordinates;
- adjust font size/weight/color;
- correct text;
- fix asset crop regions;
- fix z-order;
- convert broken vector regions into cropped assets.

Return the corrected full JSON.
