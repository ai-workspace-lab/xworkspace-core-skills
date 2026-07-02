# image-svg-pptx-pro

A Codex/agent skill for converting raster PPT screenshots or AI-generated slide images into a high-fidelity SVG intermediate and then into an editable PowerPoint deck.

## Install

Copy the folder to one of these locations:

```text
~/.agents/skills/image-svg-pptx-pro
```

or inside a project:

```text
<project>/.agents/skills/image-svg-pptx-pro
```

The first-level folder must contain `SKILL.md`.

## Use

Example prompt:

```text
$image-svg-pptx-pro

把这张PPT截图按 SVG 中间层路线转成高保真可编辑 PPT。
要求：文字、卡片、线条、表格尽量可编辑；复杂截图、图标、Logo 保留高清裁剪；输出 pptx、svg、layout_plan.json 和 QA 报告。
```

## Route

1. Normalize input image.
2. Create semantic `layout_plan.json`.
3. Crop complex asset regions.
4. Generate canonical SVG.
5. Generate editable PPTX.
6. Run visual/editability QA and correction.

## Dependencies

Install:

```bash
pip install -r requirements.txt
```

Optional system dependency for advanced rendering/preview: LibreOffice or Inkscape.
