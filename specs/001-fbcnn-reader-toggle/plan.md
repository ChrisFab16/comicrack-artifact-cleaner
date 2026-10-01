# Implementation Plan: FBCNN JPEG Artifact Reader Toggle

**Branch**: `001-fbcnn-reader-toggle` | **Date**: 2026-09-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-fbcnn-reader-toggle/spec.md`

## Summary

Deliver a **non-destructive** reader toggle that runs FBCNN JPEG artifact reduction on **display bitmaps only** (never archives). Because IronPython hooks cannot transform reader pages, v1 is a **dual deliverable**: (1) a ComicRackCE fork host page-image filter in the `ImagePool.GetPage` materialization path with cache-key participation, and (2) a plugin in this repo that exposes per-reader-window toggle + Configure, wiring into that host filter. Inference uses **ONNX Runtime in-process** (preferred after spike); PyTorch-in-IronPython is rejected. Spikes (pipeline, ONNX, API, legal) precede product UI polish.

## Technical Context

**Language/Version**: C# / .NET Framework (ComicRackCE host filter + ONNX); IronPython 2.7 (plugin toggle/Config); Python 3.x (offline ONNX export harness only)

**Primary Dependencies**: ComicRackCE engine (`ImagePool`, `PageKey`, `BitmapAdjustment`); `Microsoft.ML.OnnxRuntime.DirectML` (GPU via DirectML + CPU fallback; FR-021); FBCNN pretrained weights (`fbcnn_color` / `fbcnn_gray`); plugin packaging (`Package.ini` / `plugin.json`)

**Storage**: Volatile display cache only for filtered bitmaps; plugin `config.xml` (or host prefs) for defaults; model weights under user/plugin data dir (download-on-first-enable preferred). **No** writes to CBZ/CBR/page files.

**Testing**: Console/harness latency + visual crop tests for ONNX; CE unit/integration for cache-key invalidation; plugin ASCII/hook smoke; operator quickstart (toggle on/off + archive hash)

**Target Platform**: Windows desktop — ComicRack Community Edition (`ChrisFab16/ComicRackCE` fork for host; this repo for plugin)

**Project Type**: Hybrid — CE host engine feature + installable ComicRack plugin package

**Performance Goals**: Async display with processing feedback; default downscale long edge ≤1024 before infer (see `spike-perf.md`). CPU p95 filtered-ready ≤25 s after downscale (spike-measured); GPU stretch ≤8 s. Cached revisits instant. Hard gate: no silent UI freeze without feedback. Full-res CPU sync page turns are out of budget (~22 s @ ~1K in spike-model).

**Constraints**: Non-destructive (constitution Principle I); default OFF; no model init until first enable/Configure; fail closed with UI; **IronPython FR-015** (pure ASCII preferred; coding cookie only counts on line 1–2; no `#@` in comments — constitution II); no maforget PR unless operator asks; Apache-2.0 attribution for FBCNN; **ONNX load gated by pinned SHA-256 + ArtifactCleaner path allowlist (FR-019)**

**Scale/Scope**: v1 = host filter hook + ONNX inference path + per-window toggle plugin + Configure (model status/download + CPU/GPU preference) + blind QF; P2 manual QF slider; P3 JPEG-only scope optional after spikes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Non-Destructive Display Only | PASS | Filter only in display/cache path; FR-004/005 + SC-003 in quickstart |
| II. Host-Compatible Filter Surface | PASS | `IPageImageFilter` (or equivalent) in `ImagePool.GetPage`; plugin-only rewrite rejected |
| III. Safe Runtime Defaults | PASS | ONNX not PyTorch-in-IPY; default OFF; lazy load; visible errors |
| IV. Self-Contained Packaging | PASS | Plugin package + download-on-enable weights; Apache NOTICE |
| V. Spec-Driven, Verifiable Delivery | PASS | Spikes → tasks → analyze → implement; quickstart with hash proof |

Post-design: unchanged — contracts encode display-only filter + host registration; no archive APIs.

## Project Structure

### Documentation (this feature)

```text
specs/001-fbcnn-reader-toggle/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── host-page-image-filter.md
│   ├── plugin-toggle-config.md
│   └── model-package.md
└── tasks.md                 # /speckit-tasks (not this command)
```

### Source Code (planned)

```text
# This repo (plugin + harness + Spec Kit)
ArtifactCleaner/             # IronPython plugin package root
├── Package.ini
├── artifact_cleaner.py      # Books/Reader toggle entry (ASCII-safe)
├── config_script.py         # ConfigScript
├── version.py
└── ...
harness/                     # Offline ONNX export + latency CLI (CPython)
tests/
testdata/                    # gitignored sample pages

# ChrisFab16/ComicRackCE (host — separate repo/PR on fork)
ComicRack.Engine/IO/Cache/ImagePool.cs          # filter insert
ComicRack.Engine/IO/PageKey.cs or filter key    # cache identity
ComicRack.Engine/.../IPageImageFilter.cs        # registration surface
ComicRack/...                                   # reader-window filter state
# ONNX runner service (engine or app assembly)
```

**Structure Decision**: Spec Kit and plugin live in `comicrack-artifact-cleaner`. Host filter + ONNX runner live in `ChrisFab16/ComicRackCE` (`development` base). Tasks will tag `plugin` vs `host` ownership. No archive rewriter module exists by design.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| Dual-repo (CE fork + plugin) | Reader bitmaps are not reachable from IronPython hooks | Plugin-only overlay/rewrite violates Principle I and FR-008 |
| ONNX Runtime in host process | Need live filter without PyTorch-in-IPY | Sidecar adds IPC/lifecycle/security cost; defer unless ONNX spike fails |

## Phase 0 / Phase 1 outputs

See [research.md](./research.md), [data-model.md](./data-model.md), [contracts/](./contracts/), [quickstart.md](./quickstart.md).
