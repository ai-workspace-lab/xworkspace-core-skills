#!/usr/bin/env python3
"""Lightweight validator for layout_plan.json."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_TOP = ["canvas", "elements"]
REQUIRED_CANVAS = ["width", "height"]


def fail(msg: str) -> None:
    raise SystemExit(f"ERROR: {msg}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("plan", type=Path)
    args = parser.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    for key in REQUIRED_TOP:
        if key not in plan:
            fail(f"missing top-level key: {key}")
    for key in REQUIRED_CANVAS:
        if key not in plan["canvas"]:
            fail(f"missing canvas key: {key}")
    if not isinstance(plan["elements"], list):
        fail("elements must be a list")

    ids = set()
    warnings = []
    for i, el in enumerate(plan["elements"]):
        if "id" not in el:
            warnings.append(f"element {i} missing id")
        elif el["id"] in ids:
            warnings.append(f"duplicate id: {el['id']}")
        else:
            ids.add(el["id"])
        if "type" not in el:
            warnings.append(f"element {el.get('id', i)} missing type")

    result = {"ok": True, "warnings": warnings, "element_count": len(plan["elements"])}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
