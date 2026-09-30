# Spike: Model / ONNX (T009–T010)

**Date**: 2026-09-30  
**Status**: Complete (CPU ORT measurements)

## Artifacts (gitignored under `weights/`)

| File | sha256 | Size |
|------|--------|------|
| `fbcnn_color.pth` (upstream v1.0) | `8b0e4ef23d59cf7ac934a342cb31a17619e4fa4a0b3374a9d78c5174312387e8` | ~275 MiB |
| `fbcnn_color.onnx` (blind) | `a2b46206f6e705bc83dbc5641029b982e3d1ae0af1b1369f3792bee42088c9be` | ~274 MiB |
| `fbcnn_color_manual.onnx` | `a6a7d028232f4510d052f520c64e6c76a40e6a29e60ea16549322d80c9a1b206` | ~274 MiB |

Upstream: FBCNN release `v1.0` / Apache-2.0. Clone: `third_party/FBCNN` (gitignored).

## Export

```bash
python harness/export_fbcnn_onnx.py --device cpu
```

Uses legacy TorchScript ONNX export (`dynamo=False`). Internal pad-to-multiple-of-8 is traced at export size; runtime tested successfully at 256², 512², and 1024×768.

## Latency (CPUExecutionProvider, synthetic JPEG-like input)

| Size | Runs | Median ms | Notes |
|------|------|-----------|-------|
| 256×256 | 3 | **~3930** | Warm runs ~3.4–4.1 s |
| 512×512 | 2 | **~6500** | |
| 1024×768 | 1 | **~22100** | Comic-page-ish long edge |

GPU EP not measured in this session (CPU-only run).

## Exit criteria

- [X] Export color ONNX
- [X] Record sha256
- [X] Latency table CPU
- [ ] GPU latency (optional follow-up when DirectML/CUDA EP available)
