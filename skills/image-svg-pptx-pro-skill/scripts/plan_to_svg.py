#!/usr/bin/env python3
"""Generate a high-fidelity SVG from layout_plan.json.

This generator intentionally supports a controlled subset of SVG so the result
can later be mapped to PowerPoint native objects. Unsupported effects should be
represented as image assets or fallback groups.
"""
from __future__ import annotations

import argparse
import base64
import html
import json
from pathlib import Path
from typing import Any, Dict, Iterable


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def attrs(data: Dict[str, Any]) -> str:
    return " ".join(f'{k}="{esc(v)}"' for k, v in data.items() if v is not None)


def style_common(el: Dict[str, Any]) -> Dict[str, Any]:
    d: Dict[str, Any] = {}
    if "fill" in el:
        d["fill"] = el["fill"]
    if "stroke" in el:
        d["stroke"] = el["stroke"]
    if "stroke_width" in el:
        d["stroke-width"] = el["stroke_width"]
    if "opacity" in el:
        d["opacity"] = el["opacity"]
    return d


def image_href(path: Path) -> str:
    data = path.read_bytes()
    mime = "image/png"
    if path.suffix.lower() in [".jpg", ".jpeg"]:
        mime = "image/jpeg"
    if path.suffix.lower() == ".webp":
        mime = "image/webp"
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def render_text(el: Dict[str, Any]) -> str:
    x = float(el.get("x", 0))
    y = float(el.get("y", 0))
    w = float(el.get("w", 0))
    font_size = float(el.get("font_size", 24))
    line_spacing = float(el.get("line_spacing", 1.15))
    lines = str(el.get("text", "")).split("\n")
    color = el.get("color", "#000000")
    family = el.get("font_family", "Microsoft YaHei")
    weight = el.get("font_weight", 400)
    align = el.get("align", "left")
    anchor = {"left": "start", "center": "middle", "right": "end"}.get(align, "start")
    tx = x if align == "left" else x + w / 2 if align == "center" else x + w
    tattrs = attrs({
        "id": el.get("id"),
        "x": tx,
        "y": y + font_size,
        "font-family": family,
        "font-size": font_size,
        "font-weight": weight,
        "fill": color,
        "text-anchor": anchor,
        "data-editability": el.get("editability", "editable"),
    })
    tspans = []
    for i, line in enumerate(lines):
        dy = 0 if i == 0 else font_size * line_spacing
        tspans.append(f'<tspan x="{esc(tx)}" dy="{esc(dy)}">{html.escape(line)}</tspan>')
    return f"<text {tattrs}>" + "".join(tspans) + "</text>"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    parser.add_argument("--assets", type=Path, default=Path("work/assets"))
    parser.add_argument("--out", type=Path, default=Path("work/reconstruction.svg"))
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    canvas = plan["canvas"]
    width = canvas["width"]
    height = canvas["height"]
    bg = canvas.get("background", "#FFFFFF")

    asset_map = {a.get("id"): a for a in plan.get("assets", [])}
    elements = sorted(plan.get("elements", []), key=lambda e: e.get("z", 0))

    chunks = [
        f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect id="_background" x="0" y="0" width="{width}" height="{height}" fill="{esc(bg)}"/>'
    ]

    for el in elements:
        t = el.get("type")
        common = {"id": el.get("id"), "data-editability": el.get("editability", "editable")}
        if t == "rect":
            a = {
                **common,
                "x": el.get("x", 0), "y": el.get("y", 0),
                "width": el.get("w", 0), "height": el.get("h", 0),
                "rx": el.get("rx", 0), "ry": el.get("rx", 0),
                **style_common(el),
            }
            chunks.append(f"<rect {attrs(a)}/>")
        elif t == "circle":
            a = {**common, "cx": el.get("cx", el.get("x", 0)), "cy": el.get("cy", el.get("y", 0)), "r": el.get("r", 0), **style_common(el)}
            chunks.append(f"<circle {attrs(a)}/>")
        elif t == "line":
            a = {**common, "x1": el.get("x1", 0), "y1": el.get("y1", 0), "x2": el.get("x2", 0), "y2": el.get("y2", 0), **style_common(el)}
            chunks.append(f"<line {attrs(a)}/>")
        elif t == "text":
            chunks.append(render_text(el))
        elif t == "image":
            asset = asset_map.get(el.get("asset_id"), {})
            file = asset.get("file") or el.get("file")
            href = ""
            if file:
                path = args.assets / file
                if path.exists():
                    href = image_href(path)
                else:
                    href = file
            a = {
                **common,
                "x": el.get("x", 0), "y": el.get("y", 0),
                "width": el.get("w", 0), "height": el.get("h", 0),
                "href": href,
                "preserveAspectRatio": el.get("preserveAspectRatio", "none"),
            }
            chunks.append(f"<image {attrs(a)}/>")
        elif t == "path":
            a = {**common, "d": el.get("d", ""), **style_common(el)}
            chunks.append(f"<path {attrs(a)}/>")
        elif t == "table":
            # Draw table grid and text as simple SVG. PPT generation handles tables separately.
            x, y, w, h = [float(el.get(k, 0)) for k in ["x", "y", "w", "h"]]
            rows, cols = int(el.get("rows", 1)), int(el.get("cols", 1))
            border = el.get("border_color", "#D1D5DB")
            chunks.append(f'<g id="{esc(el.get("id", "table"))}" data-editability="editable">')
            for r in range(rows + 1):
                yy = y + h * r / rows
                chunks.append(f'<line x1="{x}" y1="{yy}" x2="{x+w}" y2="{yy}" stroke="{esc(border)}" stroke-width="1"/>')
            for c in range(cols + 1):
                xx = x + w * c / cols
                chunks.append(f'<line x1="{xx}" y1="{y}" x2="{xx}" y2="{y+h}" stroke="{esc(border)}" stroke-width="1"/>')
            cell_text = el.get("cell_text", [])
            fs = float(el.get("font_size", 18))
            for r, row in enumerate(cell_text):
                for c, text in enumerate(row):
                    tx = x + w * c / cols + 8
                    ty = y + h * r / rows + fs + 8
                    chunks.append(f'<text x="{tx}" y="{ty}" font-family="Microsoft YaHei" font-size="{fs}" fill="#111111">{html.escape(str(text))}</text>')
            chunks.append("</g>")
        else:
            # Unknown element types are ignored in SVG generation to avoid breaking output.
            chunks.append(f"<!-- skipped unsupported element: {html.escape(str(el.get('id', 'unknown')))} type={html.escape(str(t))} -->")

    chunks.append("</svg>")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(chunks), encoding="utf-8")
    print(str(args.out))


if __name__ == "__main__":
    main()
