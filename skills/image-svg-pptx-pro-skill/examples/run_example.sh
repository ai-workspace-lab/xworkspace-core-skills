#!/usr/bin/env bash
set -e

# 1. Preprocess input image.
python scripts/preprocess_image.py examples/source.png --out work/normalized.png --meta work/source_meta.json --sharpen

# 2. Create work/layout_plan.json manually or with the agent's vision analysis.
cp examples/layout_example.json work/layout_plan.json

# 3. Run deterministic generation.
python scripts/crop_assets.py work/normalized.png work/layout_plan.json --out work/assets
python scripts/plan_to_svg.py work/layout_plan.json --assets work/assets --out work/reconstruction.svg
python scripts/plan_to_pptx.py work/layout_plan.json --assets work/assets --out work/reconstructed.pptx
python scripts/visual_qa.py --plan work/layout_plan.json --svg work/reconstruction.svg --pptx work/reconstructed.pptx --out work/qa_report.md
