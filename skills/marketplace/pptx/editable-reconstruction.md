# Editable Visual Reconstruction

Use this workflow to reconstruct PPT screenshots, PNG/JPEG images, PDF pages, or flattened/original slides as editable PPTX files while preserving the source appearance.

Use the two-layer reconstruction rules only when the user explicitly requests editable reconstruction, text removal, or separation of a flattened source into background and editable text. Do not apply the text-free background requirement to normal PPT illustrations, newly generated slide artwork, or ordinary image generation.

Other image-producing skills may reference **Image Provider Selection** without inheriting the reconstruction structure.

## Required Slide Structure

Each slide must contain only these visible content classes:

1. **Image layer:** one full-slide PNG with all source text and numbers removed. Keep the complete non-text composition in this single image.
2. **Text layer:** editable PowerPoint text boxes for all words, numbers, labels, and text-like symbols.

The image layer must retain backgrounds, cards, color blocks, icons, frames, chart geometry, axes and grid lines, process shapes, chat bubbles, button shapes, illustrations, product images, 3D objects, lighting, gradients, texture, shadows, and decoration. Do not recreate these as separate PowerPoint objects.

The original page is reference material only. Keep it outside the visible slide layers and copy it to `reference/` in the deliverable.

## Image Provider Selection

1. **If Codex CLI is available:** invoke the `codex` CLI and use GPT image2 to generate or edit the image.
2. **Otherwise, if Gemini CLI is available:** invoke the `gemini` CLI and use Google Banana 2 to generate or edit the image.
3. **Otherwise:** fall back to the skill's default image output method.

Treat a CLI as available only when its command can actually start. Do not merely mention the provider in a prompt; execute the selected CLI image-generation path and use its resulting image artifact.

For newly generated illustrations without a source page, use the same provider order and follow the user's requested visual composition. Do not force a text-free image or separate editable text layer unless the user asks for editable reconstruction.

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
