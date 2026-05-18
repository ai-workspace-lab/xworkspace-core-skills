# Prompt Patterns

Use these patterns to generate a consistent PNG series.

Important output contract: generate one image per prompt. Do not ask the image model for "a batch of N images" in a single prompt. For `N` outputs, run `N` separate image-generation prompts and save `N` separate PNG files.

## Base Style Prompt

```text
1024x1536 vertical Chinese technology infographic, blue and white AI infrastructure style, Apple Keynote enterprise tech poster, huge bold dark navy Chinese title at top-left, small blue rounded pill label "一图看懂", clean white to light-blue gradient background, soft futuristic city/datacenter background, glassmorphism cards, thin light-blue borders, soft shadows, cyan glow lines, structured technical diagram, readable Chinese labels, concise English technology keywords, bottom deep-blue trend summary bar, high-end clean UI, modern enterprise infrastructure illustration, no dark cyberpunk, no crowded tiny text, no photo realism, no CTA buttons unless requested
```

## Per-Image Prompt Shape

```text
Generate exactly one standalone 1024x1536 vertical PNG infographic.
This is image {index} of {count} in a continuous series.
Do not create a collage, grid, contact sheet, multi-image preview, storyboard board, or combined overview.

Topic: {topic}
Title: {title}
Subtitle: {subtitle}
Core visual: {main_visual}
Information structure: {layout_structure}
Required nodes/cards:
{nodes}
Bottom summary: {summary}

Apply the base style exactly. Keep the same family look as the reference IT infrastructure series. Use one 1024x1536 PNG composition for this single topic only. Use large readable Chinese text, blue-white palette, clean rounded infographic cards, and a bottom deep-blue summary strip.
```

## Batch Execution Pattern

For a 7-image series, do this:

1. Build `series.config.json` with 7 `images[]` entries.
2. Generate prompt for `images[0]`; run image generation once; save `001-{id}.png`.
3. Generate prompt for `images[1]`; run image generation once; save `002-{id}.png`.
4. Continue until `007-{id}.png`.
5. Write `manifest.md` with 7 rows.

Never use a single prompt such as "create 7 separate images" because many image models will merge the series into one canvas.

## Series Continuity Checklist

- Same canvas size.
- Same top-left `一图看懂` pill.
- Same title position and weight.
- Same blue-white background and rounded poster boundary.
- Same bottom summary strip.
- Same icon language.
- Same density level.
- Topic-specific main visual only changes by subject.
- Separate files for separate topics.

## Image-Input Mode

When users provide reference images:

- Treat them as style and structure references.
- Extract layout, colors, information hierarchy, and motif.
- Do not copy exact pixels, watermarks, or accidental artifacts.
- Preserve user-provided technical terms and topic names.
- If a reference image conflicts with this v1 style, prefer the 7-image IT infrastructure family style unless the user explicitly says otherwise.

## Description-Only Mode

When users provide only text:

- First create a series plan with `N` images.
- Assign each image a title, subtitle, main visual, node list, and bottom summary.
- Generate one prompt per image using the base prompt.
- Execute each prompt separately.
- Keep terminology consistent across the entire series.
