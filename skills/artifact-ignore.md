# Artifact Ignore

`artifact-ignore.md` defines files in a task artifact scope that are useful while
working but should not be synced as user-visible artifacts.

## File Location

Place `artifact-ignore.md` at the root of the current XWorkmate/OpenClaw artifact
scope:

```text
tasks/<session>/<run>/artifact-ignore.md
```

Rules are evaluated relative to that artifact scope. They do not apply to files
outside the current run directory.

## Contract

- The file controls artifact sync/export only. It must not delete files or hide
  required final deliverables from validation.
- Final deliverables must stay syncable. Do not ignore files the user asked for,
  files listed in `DELIVERY.md`, or required manifests such as
  `assets/images/manifest.md`.
- A failed or missing required deliverable is still a failure even when an ignore
  rule would match another intermediate file.
- The ignore file itself should not be shown as a final artifact.

## Rule Format

Use one rule per line in a fenced `artifact-ignore` block:

```artifact-ignore
# comments are allowed
tmp/
cache/
*.log
*.tmp
**/.DS_Store
```

Rule syntax:

| Rule | Meaning |
|---|---|
| `path/to/file.ext` | Ignore one file relative to the artifact scope |
| `dir/` | Ignore a directory and its contents |
| `*.ext` | Ignore matching files in the artifact scope root |
| `**/*.ext` | Ignore matching files at any depth |
| `# comment` | Comment |
| blank line | Ignored |

Keep the rule set small and explicit. Prefer listing known intermediate
directories over broad patterns such as `**/*`.

## Recommended Intermediate Rules

These paths are normally safe to ignore when they exist only as build or scratch
outputs:

```artifact-ignore
tmp/
cache/
.cache/
work/
scratch/
logs/
*.log
*.tmp
*.part
*.download
**/.DS_Store
```

Video workflows can additionally ignore transient render inputs when final MP4
and validation files remain syncable:

```artifact-ignore
frames/
snapshots/
assets/audio/raw/
assets/audio/tmp/
renders/tmp/
*.wav.tmp
```

Image workflows can ignore generation scratch state when the final PNG/JPG files
and manifest remain syncable:

```artifact-ignore
prompts/tmp/
assets/images/tmp/
assets/images/raw/
*.seed.json
```

PDF/document workflows can ignore converter scratch files when the final
document remains syncable:

```artifact-ignore
build/
latex.out/
*.aux
*.toc
*.synctex.gz
```

## Minimal Example

````markdown
# Artifact Ignore

```artifact-ignore
tmp/
cache/
*.log
renders/tmp/
frames/
```
````

With this example, `renders/final.mp4`, `ffprobe.json`, `DELIVERY.md`, and
`assets/images/manifest.md` remain eligible for sync, while scratch files under
`tmp/`, `cache/`, `renders/tmp/`, and `frames/` are skipped.
