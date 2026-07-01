# Editable PDF Visual Reconstruction

Use this workflow to rebuild scanned PDFs, PDF page screenshots, flattened documents, or image-only pages while preserving their appearance and restoring a real text layer.

Read [../pptx/editable-reconstruction.md](../pptx/editable-reconstruction.md) first and reuse its image provider selection, masking, generative inpainting, prohibited cleanup methods, and residue QA rules.

## Provider Priority

Use the first image editor that is genuinely callable, not merely installed:

1. Use Codex GPT image2 or the currently exposed GPT image editing model.
2. Otherwise use Gemini CLI with Google Banana 2 or its current image editing equivalent.
3. Otherwise use the best available default content-aware or generative inpainting workflow.

If one provider fails because of authentication, model access, input format, or execution, record the failure and continue to the next provider.

## Required Page Structure

Each reconstructed PDF page must contain only these visible content classes:

1. One full-page PNG with every original word, number, label, page number, percentage, annotation, and text glyph removed.
2. Native PDF text objects containing every extracted word and number.

Keep backgrounds, cards, buttons, charts, axes, lines, icons, diagrams, illustrations, product images, 3D objects, gradients, textures, lighting, and shadows in the single text-free PNG. Do not rebuild those visuals as separate PDF shapes.

Native text must remain selectable, searchable, copyable, and editable in PDF editors that support content editing. Match the original position, bounding box, font or closest embedded substitute, size, weight, color, alignment, rotation, line spacing, and transparency.

If the requested final output is PPTX, use the PPTX requirement instead: one full-slide text-free PNG plus editable PowerPoint text boxes.

## Per-Page Workflow

1. Render each source page at high resolution and preserve its exact trim size and aspect ratio.
2. Extract all text using embedded text extraction, OCR, and visual inspection. Include fine print, chart labels, axis text, page numbers, logo-adjacent text, percentages, and annotations.
3. Create and save a text mask that includes antialiasing, outlines, glow, and text shadows.
4. Inpaint the source page into a complete text-free PNG. Never use white rectangles, solid patches, translucent overlays, blur, or cloning residue.
5. Inspect the PNG at full size and repeat until it contains no original strokes, fake writing, residual numbers, gray dirt, black trails, white patches, or blurred text regions.
6. Place the PNG once as a full-page image object.
7. Add all OCR content as native PDF text objects above the image.
8. Keep the original page only under `reference/`; never use it as the final visible background.

## Deliverables

```text
output/
├── reconstructed.pdf
├── assets/
│   └── page-NNN-background.png
├── reference/
│   └── page-NNN-reference.png
├── masks/
│   └── page-NNN-text-mask.png
├── manifest.json
└── preview/
    └── contact-sheet.png
```

Record the source path, text-free background path, mask path, provider/model and fallback, OCR reading order, and every text object's content and typography geometry in `manifest.json`.

## Required QA

1. Render the reconstructed PDF and compare every page with the source.
2. Inspect every text-free PNG independently at full resolution.
3. Produce a debug render with the PDF text layer omitted; it must show only a natural, complete, text-free page.
4. Run `pdftotext` and confirm every OCR item is represented in reading order.
5. Inspect page resources/content streams and confirm one full-page image object plus native text operators. Fonts and non-visible PDF metadata are allowed.
6. Select and copy representative text in a PDF viewer, then verify the copied content.
7. Build and inspect `preview/contact-sheet.png`.

Do not declare completion until at least one defect has been corrected and the affected page has passed a second render-and-inspect cycle.
