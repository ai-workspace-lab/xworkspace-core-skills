#!/usr/bin/env python3
"""Convenience wrapper for the deterministic parts of the workflow.

This does not create layout_plan.json automatically; the agent must generate or
edit the plan after visual analysis.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("+", " ".join(map(str, cmd)))
    subprocess.check_call([sys.executable if str(cmd[0]).endswith('.py') else cmd[0], *map(str, cmd[1:])])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--work", type=Path, default=Path("work"))
    parser.add_argument("--plan", type=Path, default=None)
    args = parser.parse_args()

    scripts = Path(__file__).parent
    work = args.work
    work.mkdir(parents=True, exist_ok=True)

    normalized = work / "normalized.png"
    meta = work / "source_meta.json"
    run([scripts / "preprocess_image.py", args.input, "--out", normalized, "--meta", meta, "--sharpen"])

    plan = args.plan or work / "layout_plan.json"
    if not plan.exists():
        print(f"\nStop: create {plan} from the normalized image, then rerun with --plan {plan}.")
        return

    assets = work / "assets"
    run([scripts / "validate_plan.py", plan])
    run([scripts / "crop_assets.py", normalized, plan, "--out", assets])
    run([scripts / "plan_to_svg.py", plan, "--assets", assets, "--out", work / "reconstruction.svg"])
    run([scripts / "plan_to_pptx.py", plan, "--assets", assets, "--out", work / "reconstructed.pptx"])
    run([scripts / "visual_qa.py", "--plan", plan, "--svg", work / "reconstruction.svg", "--pptx", work / "reconstructed.pptx", "--out", work / "qa_report.md"])
    print(f"\nDone. See {work}")


if __name__ == "__main__":
    main()
