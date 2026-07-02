#!/usr/bin/env python3
"""Crop asset regions listed in layout_plan.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("image", type=Path)
    parser.add_argument("plan", type=Path)
    parser.add_argument("--out", type=Path, default=Path("work/assets"))
    args = parser.parse_args()

    img = Image.open(args.image).convert("RGBA")
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    args.out.mkdir(parents=True, exist_ok=True)

    assets = plan.get("assets", [])
    written = []
    for asset in assets:
        if asset.get("type") != "crop":
            continue
        crop = asset.get("crop", {})
        x = int(round(crop.get("x", 0)))
        y = int(round(crop.get("y", 0)))
        w = int(round(crop.get("w", 0)))
        h = int(round(crop.get("h", 0)))
        if w <= 0 or h <= 0:
            continue
        x2 = min(img.width, x + w)
        y2 = min(img.height, y + h)
        x = max(0, x)
        y = max(0, y)
        crop_img = img.crop((x, y, x2, y2))
        filename = asset.get("file") or f"{asset.get('id', 'asset')}.png"
        out_path = args.out / filename
        crop_img.save(out_path)
        asset["file"] = filename
        written.append(str(out_path))

    # Write a resolved plan next to assets for convenience.
    resolved = args.out.parent / "layout_plan.resolved.json"
    resolved.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"written": written, "resolved_plan": str(resolved)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
