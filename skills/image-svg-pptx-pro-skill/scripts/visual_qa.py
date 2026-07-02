#!/usr/bin/env python3
"""Create a lightweight QA report for the reconstruction.

This script validates files and optionally compares two raster previews if the
agent/user provides them. It does not render PPTX itself.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, Any

from PIL import Image, ImageChops, ImageStat


def rms_diff(a: Path, b: Path) -> float | None:
    if not a.exists() or not b.exists():
        return None
    im1 = Image.open(a).convert("RGB")
    im2 = Image.open(b).convert("RGB").resize(im1.size)
    diff = ImageChops.difference(im1, im2)
    stat = ImageStat.Stat(diff)
    return sum(v ** 2 for v in stat.rms) ** 0.5


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, default=Path("work/layout_plan.json"))
    parser.add_argument("--svg", type=Path, default=Path("work/reconstruction.svg"))
    parser.add_argument("--pptx", type=Path, default=Path("work/reconstructed.pptx"))
    parser.add_argument("--source-preview", type=Path)
    parser.add_argument("--generated-preview", type=Path)
    parser.add_argument("--out", type=Path, default=Path("work/qa_report.md"))
    args = parser.parse_args()

    lines = ["# Reconstruction QA Report", ""]
    for label, path in [("layout_plan.json", args.plan), ("reconstruction.svg", args.svg), ("reconstructed.pptx", args.pptx)]:
        lines.append(f"- {label}: {'OK' if path.exists() else 'MISSING'}")

    if args.plan.exists():
        plan: Dict[str, Any] = json.loads(args.plan.read_text(encoding="utf-8"))
        elements = plan.get("elements", [])
        assets = plan.get("assets", [])
        text_count = sum(1 for e in elements if e.get("type") == "text")
        editable_count = sum(1 for e in elements if e.get("editability", "editable") == "editable")
        asset_count = sum(1 for e in elements if e.get("editability") == "asset")
        needs_review = [e.get("id") for e in elements if e.get("needs_review")]
        lines += [
            "",
            "## Plan summary",
            f"- Elements: {len(elements)}",
            f"- Text elements: {text_count}",
            f"- Editable elements: {editable_count}",
            f"- Asset-based elements: {asset_count}",
            f"- Cropped assets declared: {len(assets)}",
            f"- Needs review: {', '.join(map(str, needs_review)) if needs_review else 'None'}",
        ]

    if args.source_preview and args.generated_preview:
        score = rms_diff(args.source_preview, args.generated_preview)
        lines += ["", "## Raster preview comparison"]
        if score is None:
            lines.append("- Preview comparison unavailable.")
        else:
            lines.append(f"- RMS pixel difference: {score:.2f}")
            if score < 18:
                lines.append("- Visual match: strong")
            elif score < 35:
                lines.append("- Visual match: acceptable; inspect typography and small icons")
            else:
                lines.append("- Visual match: weak; do a correction pass")

    lines += [
        "",
        "## Manual checks still required",
        "- Verify Chinese text, names, dates, units, and numbers.",
        "- Confirm logos and complex icons were not redrawn incorrectly.",
        "- Open the PPTX and test that main titles/body text are editable.",
        "- Check that cropped image assets are not stretched.",
    ]

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(lines), encoding="utf-8")
    print(str(args.out))


if __name__ == "__main__":
    main()
