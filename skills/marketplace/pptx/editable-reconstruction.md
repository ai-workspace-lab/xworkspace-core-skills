# Editable Visual Reconstruction

Use this workflow to reconstruct PPT screenshots, PNG/JPEG images, PDF pages, or flattened/original slides as editable PPTX files while preserving the source appearance.

Other image-producing skills may reference this file as the canonical image-generation policy. For non-PPT outputs, apply **Image Provider Selection**, text-free image generation, and residue QA; keep titles, captions, labels, and numbers in the output format's native text/animation layer instead of baking them into generated images.

## Required Slide Structure

Each slide must contain only these visible content classes:

1. **Image layer:** one full-slide PNG with all source text and numbers removed. Keep the complete non-text composition in this single image.
2. **Text layer:** editable PowerPoint text boxes for all words, numbers, labels, and text-like symbols.

The image layer must retain backgrounds, cards, color blocks, icons, frames, chart geometry, axes and grid lines, process shapes, chat bubbles, button shapes, illustrations, product images, 3D objects, lighting, gradients, texture, shadows, and decoration. Do not recreate these as separate PowerPoint objects.

The original page is reference material only. Keep it outside the visible slide layers and copy it to `reference/` in the deliverable.

## Image Provider Selection

Select the first provider that is genuinely callable in the current runtime. A CLI executable existing on disk does not by itself prove that its image-editing model is usable.

1. **Codex available:** use the Codex image generation/editing capability with GPT image2 or the currently exposed GPT image editing model. Perform generative erase/inpainting from the source page plus a text-region mask.
2. **Otherwise, Gemini CLI available:** use Gemini CLI with Google Banana 2 or its current image editing equivalent. Perform generative erase/inpainting from the source page plus a text-region mask.
3. **Otherwise:** use the best available default content-aware or generative inpainting path. Manually reconstruct affected background details where necessary.

If a preferred provider is present but authentication, model access, input format, or execution fails, record the failure briefly and continue to the next provider. Never stop merely because the preferred provider is unavailable.

For newly generated illustrations without a source page, use the same provider order. Ask the model to generate the complete visual without words, letters, numbers, labels, pseudo-text, signatures, or watermarks; add required text later in the native editable layer.

Use a provider prompt equivalent to:

> Remove every visible word, letter, number, percentage, page number, logo-adjacent caption, chart label, axis label, button label, annotation, and text glyph. Reconstruct the underlying design naturally from surrounding visual context. Preserve the exact composition, geometry, visual style, colors, lighting, texture, shadows, illustrations, charts, cards, and decorative elements. Do not add replacement text, pseudo-text, glyphs, patches, blur, or new objects.

## Per-Slide Workflow

1. Render the source page at high resolution and preserve its exact aspect ratio.
2. Extract all text with OCR and visual inspection. Include titles, subtitles, body copy, card headings, descriptions, IDs, data values, percentages, chart and axis labels, page numbers, English labels, logo-adjacent text, button text, annotations, and fine print.
3. Create a mask covering every text and numeric glyph. Expand masks enough to remove antialiasing, outlines, glow, shadows, and residual strokes without erasing adjacent non-text geometry unnecessarily.
4. Generate the complete text-free page with the selected image provider. Use the source only as a visual reference/input, never as the final visible background.
5. Inspect the generated image at full size. Repeat masking and inpainting until no original text, number, residue, pseudo-text, dirty patch, blur, drag mark, or replacement glyph remains.
6. Save the result as `assets/slide-NNN-background.png`.
7. Recreate every extracted text item as an editable text box. Match position, bounding box, font family or closest available substitute, size, weight, color, line spacing, alignment, rotation, and transparency.
8. Place the single background image at the bottom, sized to cover the slide exactly. Place all text boxes above it.
9. Do not add visible shapes, charts, icons, lines, or decorative objects outside these two content classes.

## Prohibited Cleanup Methods

Do not cover text with white rectangles, solid-color patches, translucent blocks, blur, cloning artifacts, or approximate overlays. Do not leave original strokes, shadows, glow, gray dirt, black trails, white patches, or generated fake writing. Do not alter the page composition or visual style to make cleanup easier.

## Deliverables

Produce this structure unless the user requests a different location:

```text
output/
├── reconstructed.pptx
├── assets/
│   └── slide-NNN-background.png
├── reference/
│   └── slide-NNN-reference.png
├── masks/
│   └── slide-NNN-text-mask.png
├── manifest.json
└── preview/
    └── contact-sheet.png
```

In `manifest.json`, record for each slide:

- source reference path
- text-free background path
- text mask path
- image provider/model and fallback used
- original OCR text in reading order
- each text box's text, position, size, font, point size, color, weight, alignment, rotation, and z-order
- layer statement confirming one background image plus editable text boxes

## Required QA

Perform the general PPTX QA in `SKILL.md`, then verify all of the following:

1. Render the finished PPTX and compare it with the source at slide and pixel-detail scale.
2. Inspect each text-free PNG independently at full resolution. It must look complete, natural, and contain no text or number.
3. Temporarily hide or remove all text boxes and render again. The slide must show only the clean full-slide background, with no original text, residue, patch, or blur.
4. Move representative text boxes away from their original positions and render again. Nothing text-like may be revealed underneath.
5. Unpack the PPTX and inspect slide XML. Each slide must contain exactly one visible full-slide picture plus editable text shapes; allow only non-visible package metadata required by PowerPoint.
6. Confirm every OCR item appears as editable text and that no text has been flattened into the final background.
7. Build `preview/contact-sheet.png` from the final rendered slides and inspect the deck for visual consistency.

Do not declare completion until at least one defect has been corrected and the affected slides have passed a second render-and-inspect cycle.
