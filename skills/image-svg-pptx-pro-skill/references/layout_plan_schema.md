# layout_plan.json schema

This is a practical schema for image-to-SVG-to-PPT reconstruction.

## Top-level fields

```json
{
  "version": "1.0",
  "canvas": {
    "width": 1920,
    "height": 1080,
    "aspect": "16:9",
    "background": "#FFFFFF"
  },
  "quality_mode": "balanced",
  "assets": [],
  "elements": []
}
```

## Coordinate system

All coordinates are in source-image pixels after preprocessing. Origin is top-left.

## Asset object

```json
{
  "id": "asset_logo_01",
  "type": "crop",
  "source": "normalized.png",
  "crop": {"x": 120, "y": 60, "w": 180, "h": 80},
  "file": "asset_logo_01.png",
  "reason": "logo fidelity"
}
```

## Element types

### rect

```json
{
  "id": "card_01",
  "type": "rect",
  "x": 100,
  "y": 120,
  "w": 520,
  "h": 260,
  "rx": 24,
  "fill": "#FFFFFF",
  "stroke": "#E5E7EB",
  "stroke_width": 2,
  "opacity": 1,
  "z": 10,
  "editability": "editable"
}
```

### text

```json
{
  "id": "title_01",
  "type": "text",
  "text": "项目简介",
  "x": 120,
  "y": 80,
  "w": 800,
  "h": 70,
  "font_family": "Microsoft YaHei",
  "font_size": 42,
  "font_weight": 700,
  "color": "#111827",
  "align": "left",
  "valign": "top",
  "line_spacing": 1.1,
  "z": 20,
  "editability": "editable"
}
```

### line

```json
{
  "id": "divider_01",
  "type": "line",
  "x1": 100,
  "y1": 200,
  "x2": 1820,
  "y2": 200,
  "stroke": "#111827",
  "stroke_width": 2,
  "z": 15,
  "editability": "editable"
}
```

### image

```json
{
  "id": "screenshot_01",
  "type": "image",
  "asset_id": "asset_screenshot_01",
  "x": 980,
  "y": 200,
  "w": 780,
  "h": 520,
  "z": 12,
  "editability": "asset"
}
```

### table

```json
{
  "id": "table_01",
  "type": "table",
  "x": 120,
  "y": 240,
  "w": 900,
  "h": 420,
  "rows": 4,
  "cols": 3,
  "cell_text": [["指标", "现状", "优化方向"]],
  "font_size": 20,
  "border_color": "#D1D5DB",
  "z": 20,
  "editability": "editable"
}
```

## Required reconstruction notes

- Put `needs_review: true` on uncertain text.
- Use `editability: asset` for complex images and logos.
- Use `editability: fallback` for complicated vector effects.
- Sort elements by `z` before drawing.
