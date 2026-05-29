#!/usr/bin/env python3
"""Build an IT infrastructure explainer video project from a PNG manifest.

The runner is intentionally deterministic: it turns a manifest produced by
it-infra-continuous-png into one HyperFrames project, validates clip timing, and
optionally runs the HyperFrames/ffprobe acceptance chain.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


REQUIRED_MANIFEST_COLUMNS = [
    "chapter_id",
    "title",
    "file",
    "source_type",
    "video_usage",
    "scan_mode",
    "safe_focus",
]

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
HYPERFRAMES_VERSION = "0.6.15"
TASK_SCOPE_ROOT = "tasks"


class BuildError(RuntimeError):
    pass


@dataclass(frozen=True)
class ManifestRow:
    chapter_id: str
    title: str
    file: str
    source_type: str
    video_usage: str
    scan_mode: str
    safe_focus: str


@dataclass(frozen=True)
class Section:
    id: str
    start: float
    duration: float
    time_label: str
    timeline_label: str
    title: str
    subtitle: str
    tags: list[str]
    image: str
    image_fit: str
    voiceover: str
    caption: str
    source_type: str
    safe_focus: str


def fail(message: str) -> None:
    raise BuildError(message)


def run(cmd: list[str], cwd: Path, *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
    )


def slugify(value: str, fallback: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or fallback


def safe_scope_segment(value: str) -> str:
    value = value.strip()
    value = re.sub(r"[\\/]+", "_", value)
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = re.sub(r"^[._-]+|[._-]+$", "", value)
    return value[:96] or "scope"


def expected_task_scope(session_key: str, run_id: str) -> str:
    return f"{TASK_SCOPE_ROOT}/{safe_scope_segment(session_key)}/{safe_scope_segment(run_id)}"


def project_dir_from_env() -> Path:
    for name in ["XWORKMATE_TASK_ARTIFACT_DIR", "XWORKMATE_ARTIFACT_DIRECTORY"]:
        value = os.environ.get(name, "").strip()
        if value:
            return Path(value)
    return Path.cwd()


def validate_task_scope_project_dir(
    project_dir: Path,
    *,
    require_task_scope: bool,
    artifact_scope: str,
    session_key: str,
    run_id: str,
) -> str:
    expected_scope = artifact_scope.strip().strip("/")
    if not expected_scope and session_key.strip() and run_id.strip():
        expected_scope = expected_task_scope(session_key, run_id)
    if not expected_scope:
        expected_scope = str(Path(TASK_SCOPE_ROOT) / "*" / "*")

    normalized_parts = project_dir.resolve().parts
    is_task_scope_path = len(normalized_parts) >= 3 and normalized_parts[-3] == TASK_SCOPE_ROOT
    if expected_scope and "*" not in expected_scope:
        expected_parts = tuple(expected_scope.split("/"))
        is_task_scope_path = tuple(normalized_parts[-len(expected_parts) :]) == expected_parts

    if require_task_scope and not is_task_scope_path:
        fail(
            "Project directory must be the prepared XWorkmate task artifact scope. "
            f"Expected {expected_scope}, got {project_dir.resolve()}. "
            "Run this script from tasks/<session>/<run> or pass --project-dir to that directory."
        )
    return expected_scope


def parse_markdown_table(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        fail(f"Manifest not found: {path}")
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    table_lines = [line for line in lines if line.startswith("|") and line.endswith("|")]
    if len(table_lines) < 3:
        fail(f"Manifest must contain a markdown table with data rows: {path}")

    headers = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    missing = [column for column in REQUIRED_MANIFEST_COLUMNS if column not in headers]
    if missing:
        fail(f"Manifest missing required columns: {', '.join(missing)}")

    rows: list[dict[str, str]] = []
    for line in table_lines[2:]:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            fail(f"Manifest row has {len(cells)} cells but header has {len(headers)}: {line}")
        row = dict(zip(headers, cells, strict=True))
        if any(row[column] for column in REQUIRED_MANIFEST_COLUMNS):
            rows.append(row)
    if not rows:
        fail("Manifest has no image rows")
    return rows


def read_manifest(path: Path, project_dir: Path) -> list[ManifestRow]:
    rows = []
    for index, raw in enumerate(parse_markdown_table(path), start=1):
        row = ManifestRow(**{column: raw[column] for column in REQUIRED_MANIFEST_COLUMNS})
        if not row.chapter_id:
            fail(f"Manifest row {index} has an empty chapter_id")
        if row.scan_mode not in {"cover", "contain"}:
            fail(f"Manifest row {index} scan_mode must be cover or contain: {row.scan_mode}")
        image_path = project_dir / row.file
        if not image_path.exists():
            fail(f"Manifest row {index} image file not found: {row.file}")
        if image_path.read_bytes()[:8] != PNG_MAGIC:
            fail(f"Manifest row {index} image is not a real PNG: {row.file}")
        rows.append(row)
    return rows


def format_time(seconds: float) -> str:
    total = max(0, int(round(seconds)))
    return f"{total // 60}:{total % 60:02d}"


def build_sections(rows: list[ManifestRow], section_duration: float) -> list[Section]:
    sections: list[Section] = []
    for index, row in enumerate(rows):
        start = round(index * section_duration, 3)
        chapter_id = slugify(row.chapter_id, f"chapter-{index + 1}")
        title = row.title.strip()
        subtitle = row.video_usage.strip() or row.safe_focus.strip()
        caption = f"{title}: {subtitle}" if subtitle else title
        tags = [
            row.source_type.replace("_", " "),
            "long image",
            row.scan_mode,
        ]
        sections.append(
            Section(
                id=chapter_id,
                start=start,
                duration=section_duration,
                time_label=format_time(start),
                timeline_label=title or f"Chapter {index + 1}",
                title=title,
                subtitle=subtitle,
                tags=tags,
                image=row.file,
                image_fit=row.scan_mode,
                voiceover=f"assets/audio/vo-{index + 1:02d}-{chapter_id}.mp3",
                caption=caption,
                source_type=row.source_type,
                safe_focus=row.safe_focus,
            )
        )
    validate_non_overlapping("section", ((s.start, s.duration, s.id) for s in sections))
    return sections


def validate_non_overlapping(name: str, clips: Iterable[tuple[float, float, str]]) -> None:
    previous_end = -1.0
    previous_id = ""
    for start, duration, clip_id in sorted(clips):
        if duration <= 0:
            fail(f"{name} clip has non-positive duration: {clip_id}")
        if start < previous_end - 0.001:
            fail(f"{name} clips overlap: {previous_id} and {clip_id}")
        previous_end = start + duration
        previous_id = clip_id


def write_json_config(project_dir: Path, title: str, sections: list[Section]) -> dict:
    duration = round(max(s.start + s.duration for s in sections), 3)
    config = {
        "duration": duration,
        "timelineColumns": len(sections),
        "canvas": {"width": 1920, "height": 1080},
        "stylePreset": "it-infra-v2-blue-white-two-column-scan",
        "title": title,
        "sections": [
            {
                "id": section.id,
                "start": section.start,
                "duration": section.duration,
                "timeLabel": section.time_label,
                "timelineLabel": section.timeline_label,
                "title": section.title,
                "subtitle": section.subtitle,
                "tags": section.tags,
                "image": section.image,
                "imageFit": section.image_fit,
                "voiceover": section.voiceover,
                "caption": section.caption,
                "sourceType": section.source_type,
                "safeFocus": section.safe_focus,
            }
            for section in sections
        ],
        "inspectTimes": [round(section.start + section.duration / 2, 3) for section in sections],
    }
    (project_dir / "video.config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return config


def ensure_project_scaffold(project_dir: Path) -> None:
    for relative in ["assets/audio", "assets/images", "renders", "snapshots"]:
        (project_dir / relative).mkdir(parents=True, exist_ok=True)
    package_json = project_dir / "package.json"
    if not package_json.exists():
        package_json.write_text(
            json.dumps(
                {
                    "name": "it-infra-evolution-video-v2-project",
                    "private": True,
                    "type": "module",
                    "scripts": {
                        "lint": f"npx --yes hyperframes@{HYPERFRAMES_VERSION} lint",
                        "inspect": f"npx --yes hyperframes@{HYPERFRAMES_VERSION} inspect",
                        "snapshot": f"npx --yes hyperframes@{HYPERFRAMES_VERSION} snapshot",
                        "render": f"npx --yes hyperframes@{HYPERFRAMES_VERSION} render",
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    hyperframes_json = project_dir / "hyperframes.json"
    if not hyperframes_json.exists():
        hyperframes_json.write_text(
            json.dumps(
                {
                    "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
                    "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
                    "paths": {
                        "blocks": "compositions",
                        "components": "compositions/components",
                        "assets": "assets",
                    },
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )


def generate_tone_audio(project_dir: Path, sections: list[Section]) -> None:
    if not shutil.which("ffmpeg"):
        fail("ffmpeg is required for --audio-mode tone")
    for index, section in enumerate(sections, start=1):
        out = project_dir / section.voiceover
        out.parent.mkdir(parents=True, exist_ok=True)
        frequency = str(360 + index * 60)
        duration = str(max(0.4, section.duration - 0.4))
        run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency={frequency}:duration={duration}",
                "-q:a",
                "9",
                str(out),
            ],
            project_dir,
            capture=True,
        )
    bgm = project_dir / "assets/audio/bgm.wav"
    total_duration = str(max(s.start + s.duration for s in sections))
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=120:duration={total_duration}",
            "-filter:a",
            "volume=0.08",
            str(bgm),
        ],
        project_dir,
        capture=True,
    )


def generate_edge_tts_audio(project_dir: Path, sections: list[Section]) -> None:
    if not shutil.which("edge-tts"):
        fail("edge-tts is required for production voiceover generation")
    for section in sections:
        out = project_dir / section.voiceover
        out.parent.mkdir(parents=True, exist_ok=True)
        run(
            [
                "edge-tts",
                "--voice",
                "zh-CN-YunxiNeural",
                "--rate",
                "+20%",
                "--text",
                section.caption,
                "--write-media",
                str(out),
            ],
            project_dir,
        )
    bgm = project_dir / "assets/audio/bgm.wav"
    if not bgm.exists():
        generate_tone_bgm(project_dir, max(s.start + s.duration for s in sections))


def generate_tone_bgm(project_dir: Path, duration: float) -> None:
    if not shutil.which("ffmpeg"):
        fail("ffmpeg is required to synthesize fallback BGM")
    run(
        [
            "ffmpeg",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"sine=frequency=120:duration={duration}",
            "-filter:a",
            "volume=0.08",
            "assets/audio/bgm.wav",
        ],
        project_dir,
        capture=True,
    )


def css() -> str:
    return """
      :root { --timeline-columns: 1; }
      * { margin: 0; padding: 0; box-sizing: border-box; }
      html, body {
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background: #f3faff;
        font-family: Inter, "Noto Sans JP", Arial, sans-serif;
        color: #07194f;
      }
      #root {
        position: relative;
        width: 1920px;
        height: 1080px;
        overflow: hidden;
        background:
          radial-gradient(circle at 82% 16%, rgba(73,217,255,0.26), transparent 30%),
          radial-gradient(circle at 10% 92%, rgba(21,91,255,0.15), transparent 28%),
          linear-gradient(135deg, #ffffff 0%, #f3faff 46%, #dceeff 100%);
      }
      .clip { position: absolute; overflow: hidden; }
      .scene { inset: 0; opacity: 0; }
      .topbar {
        position: absolute; z-index: 40; top: 42px; left: 72px; right: 72px;
        display: flex; justify-content: space-between; align-items: center;
        font-size: 26px; font-weight: 850; color: rgba(7,25,79,0.82);
      }
      .brand-pill {
        display: inline-flex; gap: 14px; align-items: center; padding: 14px 24px;
        border-radius: 999px; color: #fff; background: linear-gradient(135deg, #155bff, #18bfa6);
        box-shadow: 0 16px 40px rgba(21,91,255,0.22);
      }
      .brand-dot { width: 14px; height: 14px; border-radius: 50%; background: #fff; box-shadow: 0 0 24px #49d9ff; }
      .scene-content {
        width: 100%; height: 100%; padding: 92px 104px 214px;
        display: grid; grid-template-columns: 0.96fr 1.04fr; gap: 58px; align-items: center;
      }
      .image-panel {
        position: relative; width: 100%; height: 760px; border-radius: 34px; overflow: hidden;
        background: #fff; border: 1px solid rgba(21,91,255,0.16);
        box-shadow: 0 34px 90px rgba(17,60,128,0.18);
      }
      .image-panel img {
        position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover;
        object-position: center top; filter: saturate(1.06) contrast(1.03);
      }
      .image-panel.contain img { object-fit: contain; padding: 20px; background: #fff; }
      .copy { position: relative; z-index: 2; display: flex; flex-direction: column; gap: 26px; }
      .kicker {
        width: max-content; max-width: 100%; color: #155bff; background: rgba(21,91,255,0.08);
        border: 1px solid rgba(21,91,255,0.22); border-radius: 999px; padding: 12px 22px;
        font-size: 27px; font-weight: 950;
      }
      h1, h2 { font-size: 64px; line-height: 1.08; font-weight: 950; letter-spacing: 0; }
      .lead { font-size: 32px; line-height: 1.55; font-weight: 760; color: rgba(7,25,79,0.78); }
      .tag-row { display: flex; gap: 14px; flex-wrap: wrap; }
      .tag {
        padding: 12px 16px; border-radius: 16px; color: #07194f; background: rgba(255,255,255,0.76);
        border: 1px solid rgba(73,217,255,0.34); box-shadow: 0 14px 30px rgba(17,60,128,0.08);
        font-size: 24px; font-weight: 900;
      }
      .caption {
        position: absolute; z-index: 55; left: 320px; right: 320px; bottom: 132px; min-height: 78px;
        display: grid; place-items: center; padding: 14px 32px; border-radius: 26px;
        background: rgba(7,25,79,0.88); color: #fff; font-size: 32px; line-height: 1.34;
        font-weight: 850; text-align: center; box-shadow: 0 20px 55px rgba(7,25,79,0.26); opacity: 0;
      }
      .timeline {
        position: absolute; z-index: 52; left: 70px; right: 70px; bottom: 28px; height: 88px;
        padding: 12px 14px 18px; display: grid; grid-template-columns: repeat(var(--timeline-columns), minmax(0, 1fr));
        gap: 10px; align-items: center; overflow: visible; border-radius: 30px;
        background: rgba(255,255,255,0.76); border: 1px solid rgba(21,91,255,0.15);
        box-shadow: 0 20px 60px rgba(17,60,128,0.14); backdrop-filter: blur(12px);
      }
      .timeline-fill { position: absolute; left: 22px; right: 22px; bottom: 8px; height: 8px; border-radius: 999px; background: rgba(7,25,79,0.12); overflow: hidden; }
      .timeline-progress { display: block; width: 0%; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #155bff, #49d9ff, #18bfa6); }
      .chapter-tag {
        position: relative; z-index: 2; min-width: 0; height: 50px; display: flex; align-items: center; justify-content: center;
        gap: 8px; padding: 0 10px; border-radius: 18px; background: rgba(255,255,255,0.72);
        border: 1px solid rgba(21,91,255,0.18); color: rgba(7,25,79,0.74); font-size: 20px;
        line-height: 1; font-weight: 900; white-space: nowrap; box-shadow: 0 12px 26px rgba(17,60,128,0.08);
      }
      .chapter-time { color: #155bff; font-variant-numeric: tabular-nums; }
      .chapter-title { overflow: hidden; text-overflow: ellipsis; }
      .chapter-tag.active { color: #fff; background: linear-gradient(135deg, #155bff, #18bfa6); border-color: rgba(255,255,255,0.62); box-shadow: 0 20px 42px rgba(21,91,255,0.28); }
      .chapter-tag.active .chapter-time { color: #fff; }
      .glow-line { position: absolute; width: 560px; height: 560px; border-radius: 50%; border: 2px solid rgba(73,217,255,0.34); right: -160px; top: -150px; }
    """


def js_array(values: list[str | float]) -> str:
    return json.dumps(values, ensure_ascii=False)


def ffmpeg_drawtext_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def display_units(value: str) -> float:
    units = 0.0
    for char in value:
        if char.isspace():
            units += 0.35
        elif ord(char) < 128:
            units += 0.55
        else:
            units += 1.0
    return units


def truncate_display(value: str, max_units: float) -> str:
    output: list[str] = []
    used = 0.0
    for char in value:
        char_units = display_units(char)
        if output and used + char_units > max_units:
            break
        output.append(char)
        used += char_units
    return "".join(output).strip()


def ffmpeg_timeline_label(section: dict, max_units: float) -> str:
    title = str(section.get("timelineLabel") or section.get("title") or "").strip()
    return truncate_display(title, max_units) or "章节"


def ffmpeg_visual_filter(config: dict, active_index: int) -> str:
    sections = config["sections"]
    duration = float(config["duration"])
    count = max(1, len(sections))
    slot = 1736 / count
    active = sections[active_index]
    active_start = float(active["start"])
    active_x = round(92 + active_index * slot, 2)
    active_w = max(140, round(slot - 12, 2))
    font_size = 23 if count <= 6 else max(15, int(23 - (count - 6) * 1.2))
    label_units = max(4.0, (slot - 82) / font_size)
    label_y = 1012
    progress_y = 1060
    font_file = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

    filters = [
        "[0:v]split=2[vb][vf]",
        "[vb]scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,boxblur=18:1,eq=brightness=-0.02:saturation=0.9[bg]",
        "[vf]scale=1760:810:force_original_aspect_ratio=decrease,pad=1760:810:(ow-iw)/2:(oh-ih)/2:white,setsar=1[fg]",
        "[bg][fg]overlay=(W-w)/2:88",
        "drawbox=x=0:y=0:w=1920:h=84:color=0xf8fbffff:t=fill",
        "drawbox=x=0:y=970:w=1920:h=110:color=0x061a3acc:t=fill",
        f"drawbox=x={active_x}:y=1002:w={active_w}:h=42:color=0x11b5d6cc:t=fill",
    ]

    for index, section in enumerate(sections):
        label_x = round(112 + index * slot, 2)
        text = ffmpeg_drawtext_text(f"{section['timeLabel']}  {ffmpeg_timeline_label(section, label_units)}")
        filters.append(
            "drawtext="
            f"fontfile='{font_file}':"
            f"text='{text}':"
            f"x={label_x}:y={label_y}:fontsize={font_size}:fontcolor=white:"
            "borderw=1:bordercolor=0x06205fcc"
        )

    progress_expr = (
        f"min(1736\\,max(0\\,(t+{active_start})/{duration}*1736))"
        if duration > 0
        else "0"
    )
    filters.extend(
        [
            f"drawbox=x=92:y={progress_y}:w=1736:h=8:color=0xffffff33:t=fill",
            f"drawbox=x=92:y={progress_y}:w='{progress_expr}':h=8:color=0x11b5d6ee:t=fill",
        ]
    )
    return ",".join(filters)


def write_ffmpeg_fallback_script(project_dir: Path, config: dict, output_name: str) -> None:
    sections = config["sections"]
    duration = float(config["duration"])
    segment_dir = "build_segments"
    output_path = f"renders/{output_name}"
    script_lines = [
        "#!/usr/bin/env bash",
        "set -euo pipefail",
        f"mkdir -p {segment_dir} renders",
    ]
    concat_lines = []
    for index, section in enumerate(sections):
        image = shlex.quote(str(section["image"]))
        segment_path = f"{segment_dir}/seg_{index:02d}.mp4"
        section_duration = float(section["duration"])
        visual_filter = ffmpeg_visual_filter(config, index)
        script_lines.extend(
            [
                f"ffmpeg -y -hide_banner -loop 1 -i {image} -t {section_duration:g} \\",
                f"  -filter_complex {shlex.quote(visual_filter)} \\",
                f"  -r 30 -c:v libx264 -preset veryfast -crf 21 -pix_fmt yuv420p {shlex.quote(segment_path)}",
            ]
        )
        concat_lines.append(f"file '{project_dir / segment_path}'")

    script_lines.extend(
        [
            f"cat > {segment_dir}/concat.txt <<'EOF'",
            *concat_lines,
            "EOF",
            f"ffmpeg -y -hide_banner -f concat -safe 0 -i {segment_dir}/concat.txt -c copy {segment_dir}/video_silent.mp4",
        ]
    )

    audio_inputs = ["-stream_loop -1 -i assets/audio/bgm.wav"]
    audio_filters = [f"[1:a]volume=0.08,atrim=0:{duration:g}[bgm]"]
    mix_inputs = ["[bgm]"]
    for index, section in enumerate(sections):
        input_index = index + 2
        voiceover = shlex.quote(str(section["voiceover"]))
        audio_inputs.append(f"-i {voiceover}")
        delay_ms = max(0, int(round((float(section["start"]) + 0.2) * 1000)))
        audio_filters.append(f"[{input_index}:a]adelay={delay_ms}|{delay_ms},volume=1.8[a{index}]")
        mix_inputs.append(f"[a{index}]")

    audio_filter = ";".join(audio_filters + [f"{''.join(mix_inputs)}amix=inputs={len(mix_inputs)}:duration=first:normalize=0[a]"])
    script_lines.extend(
        [
            "ffmpeg -y -hide_banner -i build_segments/video_silent.mp4 \\",
            *[f"  {line} \\" for line in audio_inputs],
            f"  -filter_complex {shlex.quote(audio_filter)} \\",
            f"  -map 0:v -map '[a]' -t {duration:g} -c:v copy -c:a aac -b:a 160k -movflags +faststart {shlex.quote(output_path)}",
            f"ffprobe -v quiet -show_entries format=duration,size:stream=codec_type,width,height,r_frame_rate -of json {shlex.quote(output_path)} > ffprobe.json",
        ]
    )

    script_path = project_dir / "build_ffmpeg_video.sh"
    script_path.write_text("\n".join(script_lines) + "\n", encoding="utf-8")
    script_path.chmod(0o755)


def write_html(project_dir: Path, title: str, config: dict) -> None:
    sections = config["sections"]
    duration = config["duration"]
    timeline_columns = config["timelineColumns"]

    scene_html = []
    caption_html = []
    chapter_html = []
    audio_html = [
        f'<audio id="bgm" class="clip" data-start="0" data-duration="{duration}" data-track-index="20" data-volume="0.10" src="assets/audio/bgm.wav"></audio>'
    ]

    for index, section in enumerate(sections):
        scene_id = f"scene-{section['id']}"
        cap_id = f"cap-{index + 1:02d}-{section['id']}"
        vo_id = f"vo-{index + 1:02d}-{section['id']}"
        image_panel_class = "image-panel contain" if section["imageFit"] == "contain" else "image-panel"
        tags = "".join(f'<span class="tag">{html.escape(tag)}</span>' for tag in section["tags"])
        heading_tag = "h1" if index == 0 else "h2"
        caption_start = round(section["start"] + 0.2, 3)
        caption_duration = round(max(0.4, section["duration"] - 0.4), 3)
        scene_html.append(
            f"""
      <section id="{scene_id}" class="clip scene" data-start="{section['start']}" data-duration="{section['duration']}" data-track-index="1">
        <div class="scene-content">
          <div class="{image_panel_class}"><img data-layout-allow-overflow src="{html.escape(section['image'])}" alt="{html.escape(section['title'])}" /></div>
          <div class="copy">
            <div class="kicker">{html.escape(section['timeLabel'])} / {html.escape(section['timelineLabel'])}</div>
            <{heading_tag}>{html.escape(section['title'])}</{heading_tag}>
            <p class="lead">{html.escape(section['subtitle'])}</p>
            <div class="tag-row">{tags}</div>
          </div>
        </div>
      </section>"""
        )
        caption_html.append(
            f'<div class="caption clip" id="{cap_id}" data-start="{caption_start}" data-duration="{caption_duration}" data-track-index="10">{html.escape(section["caption"])}</div>'
        )
        chapter_html.append(
            f'<div class="chapter-tag" id="chapter-{index}"><span class="chapter-time">{html.escape(section["timeLabel"])}</span><span class="chapter-title">{html.escape(section["timelineLabel"])}</span></div>'
        )
        audio_html.append(
            f'<audio id="{vo_id}" class="clip" data-start="{section["start"]}" data-duration="{caption_duration}" data-track-index="5" data-volume="0.92" src="{html.escape(section["voiceover"])}"></audio>'
        )

    starts = [section["start"] for section in sections]
    durations = [section["duration"] for section in sections]
    scenes = [f"#scene-{section['id']}" for section in sections]
    captions = [f"#cap-{index + 1:02d}-{section['id']}" for index, section in enumerate(sections)]
    chapters = [f"#chapter-{index}" for index in range(len(sections))]

    index_html = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1920, height=1080" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js"></script>
    <style>{css()}</style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{duration}" data-width="1920" data-height="1080" style="--timeline-columns: {timeline_columns}">
      <div class="glow-line" data-layout-ignore></div>
      <div class="topbar" data-layout-ignore>
        <div class="brand-pill"><span class="brand-dot"></span><span>{html.escape(title)}</span></div>
        <div>PNG manifest -> HyperFrames -> MP4</div>
      </div>
      {''.join(scene_html)}
      {''.join(caption_html)}
      <div class="timeline" data-layout-ignore>
        {''.join(chapter_html)}
        <div class="timeline-fill"><div class="timeline-progress"></div></div>
      </div>
      {''.join(audio_html)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      const rootDuration = Number(document.querySelector("#root").dataset.duration || {duration});
      const tl = gsap.timeline({{ paused: true }});
      const scenes = {js_array(scenes)};
      const starts = {js_array(starts)};
      const durations = {js_array(durations)};
      const captions = {js_array(captions)};
      const chapters = {js_array(chapters)};

      scenes.forEach((scene, index) => {{
        const start = starts[index];
        const duration = durations[index];
        tl.set(scene, {{ opacity: 1 }}, start);
        tl.to(scene, {{ opacity: 0, duration: 0.28, ease: "power1.in" }}, start + duration - 0.28);
        tl.from(`${{scene}} .image-panel`, {{ x: -78, opacity: 0, scale: 0.96, duration: 0.72, ease: "power3.out" }}, start + 0.08);
        tl.from(`${{scene}} .kicker`, {{ y: 28, opacity: 0, duration: 0.42, ease: "power2.out" }}, start + 0.18);
        tl.from(`${{scene}} h1, ${{scene}} h2`, {{ y: 46, opacity: 0, duration: 0.62, ease: "power3.out" }}, start + 0.3);
        tl.from(`${{scene}} .lead`, {{ y: 36, opacity: 0, duration: 0.54, ease: "power2.out" }}, start + 0.58);
        tl.from(`${{scene}} .tag`, {{ y: 24, opacity: 0, scale: 0.94, duration: 0.42, stagger: 0.06, ease: "power2.out" }}, start + 0.82);
        tl.to(`${{scene}} .image-panel img`, {{ y: -70, scale: 1.1, duration: Math.max(4, duration - 1), ease: "none" }}, start + 0.4);
      }});

      captions.forEach((caption, index) => {{
        const start = starts[index] + 0.2;
        const duration = Math.max(0.4, durations[index] - 0.4);
        tl.to(caption, {{ opacity: 1, y: 0, duration: 0.16, ease: "power1.out" }}, start);
        tl.to(caption, {{ opacity: 0, y: 14, duration: 0.16, ease: "power1.in" }}, start + duration - 0.16);
      }});

      chapters.forEach((chapter, index) => {{
        const start = starts[index];
        const duration = durations[index];
        tl.to(chapter, {{ y: -8, scale: 1.04, duration: 0.18, ease: "power1.out" }}, start);
        tl.set(chapter, {{ className: "chapter-tag active" }}, start);
        tl.set(chapter, {{ className: "chapter-tag" }}, start + duration - 0.1);
        tl.to(chapter, {{ y: 0, scale: 1, duration: 0.18, ease: "power1.in" }}, start + duration - 0.28);
      }});

      tl.to(".timeline-progress", {{ width: "100%", duration: rootDuration, ease: "none" }}, 0);
      tl.from(".topbar", {{ y: -28, opacity: 0, duration: 0.5, ease: "power2.out" }}, 0.1);
      tl.to(".glow-line", {{ scale: 1.18, rotation: 20, duration: rootDuration, ease: "none" }}, 0);
      tl.to("#root", {{ opacity: 0, duration: 0.65, ease: "power2.in" }}, Math.max(0, rootDuration - 0.75));
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""
    (project_dir / "index.html").write_text(index_html, encoding="utf-8")


def doctor(audio_mode: str, run_acceptance: bool) -> None:
    required = ["ffmpeg", "ffprobe", "npx"]
    if audio_mode == "edge-tts":
        required.append("edge-tts")
    missing = [tool for tool in required if not shutil.which(tool)]
    if missing:
        fail(f"Missing required tool(s): {', '.join(missing)}")
    if run_acceptance and not shutil.which("npx"):
        fail("npx is required to run HyperFrames acceptance")


def run_acceptance(project_dir: Path, config: dict, output_name: str) -> None:
    inspect_at = ",".join(str(value) for value in config["inspectTimes"])
    output_path = f"renders/{output_name}"
    run(["npx", "--yes", f"hyperframes@{HYPERFRAMES_VERSION}", "lint"], project_dir)
    run(["npx", "--yes", f"hyperframes@{HYPERFRAMES_VERSION}", "inspect", "--at", inspect_at], project_dir)
    run(["npx", "--yes", f"hyperframes@{HYPERFRAMES_VERSION}", "snapshot", "--at", inspect_at], project_dir)
    run(["npx", "--yes", f"hyperframes@{HYPERFRAMES_VERSION}", "render", "--output", output_path, "--quality", "standard"], project_dir)
    probe = run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-show_entries",
            "format=duration,size:stream=codec_type,width,height,r_frame_rate",
            "-of",
            "json",
            output_path,
        ],
        project_dir,
        capture=True,
    )
    probe_json = json.loads(probe.stdout or "{}")
    streams = probe_json.get("streams", [])
    has_video = any(stream.get("codec_type") == "video" for stream in streams)
    has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    if not has_video or not has_audio:
        fail("ffprobe acceptance failed: rendered MP4 must contain video and audio streams")
    if video_stream.get("width") != 1920 or video_stream.get("height") != 1080:
        fail(f"ffprobe acceptance failed: expected 1920x1080, got {video_stream.get('width')}x{video_stream.get('height')}")
    actual_duration = float(probe_json.get("format", {}).get("duration", 0) or 0)
    expected_duration = float(config["duration"])
    tolerance = max(3.0, expected_duration * 0.15)
    if abs(actual_duration - expected_duration) > tolerance:
        fail(
            "ffprobe acceptance failed: "
            f"expected duration near {expected_duration:.3f}s, got {actual_duration:.3f}s"
        )
    (project_dir / "ffprobe.json").write_text(json.dumps(probe_json, indent=2) + "\n", encoding="utf-8")


def write_delivery_report(project_dir: Path, title: str, output_name: str, expected_scope: str, rendered: bool) -> None:
    lines = [
        f"# {title}",
        "",
        "## XWorkmate Artifacts",
        "",
        f"- Artifact scope: `{expected_scope}`",
        "- `index.html`",
        "- `video.config.json`",
        "- `assets/images/manifest.md`",
        "- `assets/audio/`",
    ]
    if rendered:
        lines.extend(
            [
                f"- `renders/{output_name}`",
                "- `ffprobe.json`",
            ]
        )
    else:
        lines.append("- Render not executed; run again with `--run-acceptance` before reporting completion.")
    (project_dir / "DELIVERY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-dir",
        type=Path,
        default=None,
        help="HyperFrames project directory. Defaults to XWORKMATE_TASK_ARTIFACT_DIR, XWORKMATE_ARTIFACT_DIRECTORY, or cwd.",
    )
    parser.add_argument("--manifest", type=Path, default=None, help="PNG manifest path")
    parser.add_argument("--title", default="IT 基础设施长图讲解视频", help="Video title")
    parser.add_argument("--section-duration", type=float, default=8.0, help="Seconds per manifest row")
    parser.add_argument("--audio-mode", choices=["edge-tts", "tone", "none"], default="edge-tts")
    parser.add_argument("--run-acceptance", action="store_true", help="Run lint/inspect/snapshot/render/ffprobe")
    parser.add_argument("--output-name", default="it-infra-evolution.mp4", help="Rendered MP4 file name")
    parser.add_argument(
        "--require-task-scope",
        action="store_true",
        help="Fail unless project-dir is the prepared tasks/<session>/<run> artifact scope.",
    )
    parser.add_argument("--artifact-scope", default=os.environ.get("XWORKMATE_ARTIFACT_SCOPE", ""), help="Expected artifact scope")
    parser.add_argument("--session-key", default=os.environ.get("XWORKMATE_SESSION_KEY", ""), help="Expected XWorkmate session key")
    parser.add_argument("--run-id", default=os.environ.get("XWORKMATE_RUN_ID", ""), help="Expected XWorkmate/OpenClaw run id")
    args = parser.parse_args(argv)

    try:
        project_dir = (args.project_dir or project_dir_from_env()).resolve()
        expected_scope = validate_task_scope_project_dir(
            project_dir,
            require_task_scope=args.require_task_scope,
            artifact_scope=args.artifact_scope,
            session_key=args.session_key,
            run_id=args.run_id,
        )
        manifest = (args.manifest or project_dir / "assets/images/manifest.md").resolve()
        ensure_project_scaffold(project_dir)
        doctor(args.audio_mode, args.run_acceptance)
        rows = read_manifest(manifest, project_dir)
        sections = build_sections(rows, args.section_duration)
        config = write_json_config(project_dir, args.title, sections)
        if args.audio_mode == "edge-tts":
            generate_edge_tts_audio(project_dir, sections)
        elif args.audio_mode == "tone":
            generate_tone_audio(project_dir, sections)
        elif not (project_dir / "assets/audio/bgm.wav").exists():
            fail("--audio-mode none requires existing assets/audio/bgm.wav")
        write_html(project_dir, args.title, config)
        write_ffmpeg_fallback_script(project_dir, config, args.output_name)
        if args.run_acceptance:
            run_acceptance(project_dir, config, args.output_name)
        write_delivery_report(project_dir, args.title, args.output_name, expected_scope, args.run_acceptance)
        print("Build complete. Required task artifacts: index.html, video.config.json, assets/images/manifest.md, assets/audio/, renders/ or run with --run-acceptance.")
        return 0
    except (BuildError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
