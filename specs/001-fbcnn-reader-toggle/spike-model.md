# Spike: Model / ONNX (T009–T010)

**Date**: 2026-09-30  
**Status**: Scaffold only — blocked on local weights + FBCNN network code

## Done

- [X] `harness/export_fbcnn_onnx.py` stub + `harness/requirements.txt` + `harness/README.md`

## Remaining (operator / next implement session)

1. Download `fbcnn_color.pth` from FBCNN GitHub releases into gitignored `weights/`
2. Vendor or clone network definition needed for `torch.onnx.export`
3. Export ONNX; record sha256 in this file and `contracts/model-package.md`
4. Latency table on `testdata/` crop + full page (CPU ± GPU) → fills T010 and unlocks T014 `spike-perf.md`

## Provisional (until measured)

See `plan.md` Performance Goals: p95 filtered-ready ≤ 2000 ms target under downscale/tile policy.
