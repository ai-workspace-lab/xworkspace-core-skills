---
name: image-series-to-video
description: "图片系列转视频工作流：将带 manifest 的 PNG 图片系列转成带讲解、字幕和验收的 MP4 视频。Workflow skill for converting a manifest-backed image series into a narrated video; use when generated PNGs or an image manifest should become an MP4, long-image explanation video, chapter video, narrated walkthrough, or social video."
---

# Image Series To Video Workflow

This workflow starts only after a real image series exists. It prevents the video stage from inventing fake screenshots, CSS cards, or placeholder images.

## Required Inputs

The current artifact scope must contain:

- `assets/images/*.png`
- `assets/images/manifest.md`

The manifest must describe one row per image with title, file, usage, scan mode, and focus guidance.

## Output Contract

Final deliverables must stay inside the current task artifact scope:

- `video.config.json`
- `index.html`
- `assets/audio/*.mp3`
- `assets/audio/bgm.wav`
- `renders/*.mp4`
- `ffprobe.json`
- `DELIVERY.md`

## Phase 1: Input Gate

Validate before building video:

```bash
find assets/images -maxdepth 1 -type f -name '*.png' | sort
test -f assets/images/manifest.md
```

Reject the task if images are missing, empty, non-PNG, or not referenced by manifest.

## Phase 2: Video Plan

Create or update `video.config.json` from the manifest:

- one scene per image or chapter
- title and caption per scene
- scan mode and safe focus from manifest
- voiceover text
- inspect timestamps
- output file name

Do not hand-write fixed scene arrays unrelated to the manifest.

## Phase 3: Build

Use the repository video runner when available. Otherwise create the minimal equivalent pipeline:

- generate `index.html`
- generate voiceover audio
- run visual acceptance snapshots
- render MP4
- run ffprobe

## Phase 4: Acceptance

Only report completion if:

- `renders/*.mp4` exists and is non-empty.
- `ffprobe.json` shows video and audio streams.
- duration is plausible for the number of scenes.
- sampled frames show real source images, visible captions, and no obvious overlap.

If any step fails, report the failing phase and keep partial artifacts for diagnosis.
