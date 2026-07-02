#!/usr/bin/env python3
"""Preprocess a source image for image→SVG→PPT reconstruction.

The script keeps the original image untouched and writes a normalized PNG plus a
metadata JSON file. It performs conservative operations only: EXIF transpose,
optional trim, optional deskew, and optional sharpening.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Tuple

from PIL import Image, ImageOps, ImageFilter


def trim_whitespace(img: Image.Image, threshold: int = 248) -> Image.Image:
    gray = ImageOps.grayscale(img.convert("RGB"))
    # Build mask of non-near-white pixels.
    mask = gray.point(lambda p: 255 if p < threshold else 0)
    bbox = mask.getbbox()
    if not bbox:
        return img
    # Add small padding.
    pad = 8
    l, t, r, b = bbox
    l = max(0, l - pad)
    t = max(0, t - pad)
    r = min(img.width, r + pad)
    b = min(img.height, b + pad)
    return img.crop((l, t, r, b))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, default=Path("work/normalized.png"))
    parser.add_argument("--meta", type=Path, default=Path("work/source_meta.json"))
    parser.add_argument("--trim", action="store_true", help="Trim near-white outer margins.")
    parser.add_argument("--sharpen", action="store_true", help="Apply mild sharpening.")
    parser.add_argument("--max-width", type=int, default=2400, help="Downscale very large images to this width.")
    args = parser.parse_args()

    img = Image.open(args.input)
    img = ImageOps.exif_transpose(img).convert("RGB")
    original_size: Tuple[int, int] = img.size

    if args.trim:
        img = trim_whitespace(img)

    if args.max_width and img.width > args.max_width:
        scale = args.max_width / img.width
        new_size = (args.max_width, round(img.height * scale))
        img = img.resize(new_size, Image.Resampling.LANCZOS)

    if args.sharpen:
        img = img.filter(ImageFilter.UnsharpMask(radius=1.2, percent=120, threshold=3))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.meta.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out)

    meta = {
        "source": str(args.input),
        "normalized": str(args.out),
        "original_width": original_size[0],
        "original_height": original_size[1],
        "width": img.width,
        "height": img.height,
        "aspect_ratio": round(img.width / img.height, 6),
    }
    args.meta.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(meta, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
