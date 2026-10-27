#!/usr/bin/env bash
# 用法: ./compose.sh samples/<episode>   (需先 make_refs.py + 生成 clips/)
set -e; cd "$(dirname "$0")"
PY=/workspace/ai-ti-wo-shuo/v2/.venv/bin/python
"$PY" compose.py "$1"
