#!/usr/bin/env python3
"""Fetch a public short video and split it into scene-boundary keyframes.

This script does the mechanical half of video-understanding: download,
probe, and scene-detect. It never guesses what is *in* a frame — semantic
description is an Agent's job (see ../SKILL.md). Output is shots.json, a
list of {index, start, end, frame} the Agent then walks frame by frame.

Usage:
    analyze_video.py --url <link> --workdir analysis \
        [--max-frames 24] [--min-scene-diff 0.35]
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kwargs)


def require_tool(name: str) -> None:
    if shutil.which(name) is None:
        sys.exit(
            f"error: {name} not found on PATH. Install it before running "
            "this skill — do not fall back to guessing shot content."
        )


def download(url: str, dest: Path) -> Path:
    """Download the source video. Kept as an intermediate artifact only —
    do not sync analysis/source.mp4 as a final deliverable (see SKILL.md
    acceptance criteria)."""
    out_template = str(dest / "source.%(ext)s")
    run(
        [
            "yt-dlp",
            "--no-playlist",
            "-f",
            "mp4/best",
            "-o",
            out_template,
            url,
        ]
    )
    matches = sorted(dest.glob("source.*"))
    if not matches:
        sys.exit("error: yt-dlp reported success but produced no source file")
    return matches[0]


def probe_duration(video: Path) -> float:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=nw=1:nk=1",
            str(video),
        ]
    )
    return float(result.stdout.strip())


def has_audio_stream(video: Path) -> bool:
    result = run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a",
            "-show_entries",
            "stream=index",
            "-of",
            "csv=p=0",
            str(video),
        ]
    )
    return bool(result.stdout.strip())


def detect_scene_cuts(video: Path, min_diff: float) -> list[float]:
    """Return cut timestamps via ffmpeg's scene-change filter. Falls back to
    an empty list (caller then samples fixed intervals) if the filter finds
    nothing usable — a very static video (e.g. one long static shot) is a
    real case, not an error."""
    cmd = [
        "ffmpeg",
        "-i",
        str(video),
        "-filter:v",
        f"select='gt(scene,{min_diff})',showinfo",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    timestamps: list[float] = []
    for line in result.stderr.splitlines():
        if "pts_time:" not in line:
            continue
        try:
            token = line.split("pts_time:")[1].split()[0]
            timestamps.append(float(token))
        except (IndexError, ValueError):
            continue
    return sorted(set(timestamps))


def build_shot_ranges(
    cuts: list[float], duration: float, max_frames: int
) -> list[tuple[float, float]]:
    boundaries = [0.0, *cuts, duration]
    boundaries = sorted(set(round(b, 3) for b in boundaries if 0.0 <= b <= duration))
    ranges = list(zip(boundaries[:-1], boundaries[1:]))
    ranges = [r for r in ranges if r[1] - r[0] > 0.15]  # drop noise-thin slivers
    if not ranges:
        ranges = [(0.0, duration)]
    if len(ranges) > max_frames:
        # Too many cuts for a short clip (fast-cut edits): keep evenly spaced
        # ranges instead of the first N, so coverage stays representative.
        step = len(ranges) / max_frames
        ranges = [ranges[int(i * step)] for i in range(max_frames)]
    return ranges


def extract_frame(video: Path, timestamp: float, out_path: Path) -> None:
    run(
        [
            "ffmpeg",
            "-y",
            "-ss",
            f"{timestamp:.3f}",
            "-i",
            str(video),
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(out_path),
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--workdir", default="analysis")
    parser.add_argument("--max-frames", type=int, default=24)
    parser.add_argument("--min-scene-diff", type=float, default=0.35)
    args = parser.parse_args()

    require_tool("yt-dlp")
    require_tool("ffmpeg")
    require_tool("ffprobe")

    workdir = Path(args.workdir)
    frames_dir = workdir / "frames"
    workdir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    video = download(args.url, workdir)
    duration = probe_duration(video)
    audio = has_audio_stream(video)

    cuts = detect_scene_cuts(video, args.min_scene_diff)
    ranges = build_shot_ranges(cuts, duration, args.max_frames)

    shots = []
    for index, (start, end) in enumerate(ranges, start=1):
        frame_name = f"shot-{index:03d}.jpg"
        frame_path = frames_dir / frame_name
        mid = start + (end - start) / 2
        extract_frame(video, mid, frame_path)
        shots.append(
            {
                "index": index,
                "start": round(start, 2),
                "end": round(end, 2),
                "frame": f"frames/{frame_name}",
            }
        )

    manifest = {
        "source_url": args.url,
        "duration": round(duration, 2),
        "has_audio": audio,
        "shot_count": len(shots),
        "shots": shots,
    }
    (workdir / "shots.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"ok: {len(shots)} shots, duration={duration:.1f}s, audio={audio}")
    print(f"next: read {workdir}/shots.json and write script.md + beat-sheet.md")
    print("      (see ../references/beat-sheet-schema.md for the format)")


if __name__ == "__main__":
    main()
