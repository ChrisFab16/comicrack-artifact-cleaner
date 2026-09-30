# Quickstart: FBCNN reader toggle validation

**Feature**: `001-fbcnn-reader-toggle` | **Date**: 2026-09-30

Operator validation after spikes + implement. Sample pages are copyrighted — use gitignored `testdata/` or external files; do not commit them.

## Prerequisites

- ComicRack CE build from `ChrisFab16/ComicRackCE` that includes the host page-image filter (see [contracts/host-page-image-filter.md](./contracts/host-page-image-filter.md))
- Plugin installed from this repo’s package
- One heavily JPEG-compressed sample CBZ/CBR
- Optional: ONNX weights installed via Configure (or harness export)

## Scenario A — Non-destructive toggle (P1 / SC-001–003)

1. Compute archive hash before opening: `sha256sum "sample.cbz"` (or Windows equivalent); record it.
2. Open the book in CE; leave artifact reduction **off**; capture a screenshot of a known blocky page (baseline).
3. Enable the reader toggle; wait for processing feedback if shown; capture the same page (filtered).
4. Confirm filtered page looks cleaner (less blocking/ringing) than baseline (SC-001).
5. Disable the toggle; confirm the page matches baseline look (SC-002).
6. Close the book; recompute archive hash — MUST equal step 1 (SC-003).

**Pass**: Visual on/off difference + identical archive hash.

## Scenario B — Safe default / failure (P1 / SC-004, SC-006, SC-008)

1. Fresh plugin settings (or new install); do not enable the feature.
2. Open a book and turn several pages — no model download dialog; no hung UI from this feature (SC-004).
3. Remove/rename weights (or use install without weights); attempt enable.
4. Expect visible error within a few seconds; reading continues unfiltered; app does not require restart (SC-006).
5. (SC-008) Place a wrong-sized/corrupt file named `fbcnn_color.onnx` under `ArtifactCleaner/weights/`; attempt enable — expect SHA-256 mismatch error; filter stays off.

**Pass**: No surprise download when off; fail-closed enable with continued reading; integrity mismatch fails closed.

## Scenario C — Performance usability (SC-005)

1. Enable filter with weights present on a large page (~2000px+ wide).
2. Turn pages while processing may still run.
3. Confirm: navigation remains possible; feedback appears for non-instant work; no silent multi-second UI freeze beyond the documented policy.

**Pass**: Operator can finish a short multi-page read without force-killing CE.

## Scenario D — Configure ongoing control (P2)

1. Open plugin Configure; confirm model status and download/EP options.
2. Change a supported option; restart CE; confirm persistence.
3. Confirm Configure remains reachable after first run (not setup-only).

## Scenario E — Host missing filter (fail closed)

1. Install plugin on a CE build **without** the host filter (if available) OR simulate registration failure.
2. Attempt enable → must explain host dependency; must not claim success while leaving pages unchanged.

## Automated / harness (dev)

- Export + latency: run `harness/` against `testdata/` crops; record CPU (± GPU) ms in spike notes under `specs/001-fbcnn-reader-toggle/` (or validation-results later).
- Spec Kit: `/speckit-analyze` CRITICAL=0 before treating implement complete (SC-007).

## Out of scope for quickstart

- Training weights
- Batch library rewrite
- Upstream PR to maforget
