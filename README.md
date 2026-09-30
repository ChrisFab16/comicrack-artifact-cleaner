# ComicRack Artifact Cleaner

ComicRack Community Edition plugin for **FBCNN** JPEG artifact reduction on **reader display images only**.

**Non-destructive:** never rewrites CBZ/CBR or page files on disk — only the rendered/display cache.

## Dual-repo layout

| Piece | Repo |
|-------|------|
| Plugin package + Spec Kit | This repo (`ChrisFab16/comicrack-artifact-cleaner`) |
| Host page-image filter + ONNX runner | [`ChrisFab16/ComicRackCE`](https://github.com/ChrisFab16/ComicRackCE) fork (`development`) |

IronPython hooks alone cannot transform reader bitmaps. A CE host filter is required (see Spec Kit plan).

## Spec Kit

Active feature: `specs/001-fbcnn-reader-toggle/`  
Workflow: specify → plan → tasks → **analyze** (CRITICAL=0) → implement.

## Install (plugin)

1. Build package: `bash scripts/package-crplugin.sh`
2. Copy `crplugin/ArtifactCleaner.crplugin` into ComicRack CE Scripts (or unzip `ArtifactCleaner/` under Scripts)
3. Use a CE build from branch `001-fbcnn-reader-toggle` (host page filter + ORT)
4. Place `fbcnn_color.onnx` at `Scripts/ArtifactCleaner/weights/fbcnn_color.onnx` (export via `harness/export_fbcnn_onnx.py`)
5. Automation menu → **Artifact Cleaner (FBCNN)** toggles filter on/off

## Weights

Download-on-first-enable (preferred). Large `.onnx` / `.pth` files are gitignored. Apache-2.0 attribution for FBCNN — see `ArtifactCleaner/licenses/` (added in polish).

## Development

- Harness (ONNX export/latency): `harness/README.md`
- **Representative automated tests** (before manual Scenario A):
  ```bash
  bash scripts/run-representative-tests.sh
  ```
  Plugin: CPython pytest (`tests/`). Host: CE `ComicRack.Tests` FBCNN filter (no IronPython).
- Operator validation: `specs/001-fbcnn-reader-toggle/quickstart.md`
