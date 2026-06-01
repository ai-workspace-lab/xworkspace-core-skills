---
name: research-to-slide-deck
description: "研究到幻灯片工作流：将研究资料、来源和主题 brief 转成可验证的演示文稿。Workflow skill for turning research notes, sources, or a topic brief into a verified slide deck; use for PPT, PPTX, slides, research presentations, briefing decks, or source-backed presentations."
---

# Research To Slide Deck Workflow

This workflow converts research into a presentation with explicit source, outline, slide, and verification phases.

## Output Contract

Final deliverables must stay inside the current task artifact scope:

- `research/sources.md`
- `deck-outline.md`
- `slides/slide-notes.md`
- `exports/deck.pptx` or `exports/deck.pdf`
- `DELIVERY.md`

When a PPTX writer is unavailable, produce a PDF deck and state that format clearly.

## Phase 1: Research

Gather or parse source material into `research/sources.md`.

Each source note should capture:

- title
- URL or local path when available
- date if relevant
- key facts
- how it supports the deck

For current facts, live sources, pricing, market data, product specs, or recent events, verify against live sources before writing the deck.

## Phase 2: Deck Outline

Write `deck-outline.md` before creating slides.

The outline must include:

- audience and purpose
- 6-12 slide titles unless the user specifies otherwise
- one message per slide
- required charts, screenshots, tables, or diagrams
- source mapping per slide

Do not begin slide generation until the outline is coherent.

## Phase 3: Slide Production

Create the deck from the outline:

- title slide
- agenda or context slide when useful
- evidence slides with concise headings
- visual slides for comparisons, timelines, architecture, or workflow
- closing recommendation or next steps

Use charts, tables, diagrams, or screenshots only when they support the message. Avoid decorative filler.

## Phase 4: Verification

Before final response:

- confirm `exports/` contains the final deck
- render or inspect the deck when tooling is available
- check slide count
- check that source-backed claims map to `research/sources.md`
- check text does not overflow obvious slide containers

If verification cannot run, report the missing verifier and keep the generated deck plus source files.
