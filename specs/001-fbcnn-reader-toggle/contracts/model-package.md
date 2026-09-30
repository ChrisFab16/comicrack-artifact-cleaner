# Contract: Model package (FBCNN → ONNX)

**Feature**: `001-fbcnn-reader-toggle`

## Upstream

- Paper: Jiang, Zhang, Timofte — *Towards Flexible Blind JPEG Artifacts Removal* (ICCV 2021)
- Code: https://github.com/jiaxi-jiang/FBCNN
- License: **Apache License 2.0**

## Artifacts

| Id | Source weight (upstream) | Runtime artifact | Use |
|----|--------------------------|------------------|-----|
| `fbcnn_color` | `fbcnn_color.pth` | `fbcnn_color.onnx` | Primary color pages |
| `fbcnn_gray` | `fbcnn_gray.pth` | `fbcnn_gray.onnx` | Optional gray path |

If `fbcnn_gray` is not shipped, Configure and enable MUST fail closed with a clear message for gray-only pages (or disclose limitation) — see tasks T032b.

Double-JPEG gray variant (`fbcnn_gray_double`) is out of v1 unless spike shows need.

## Flexible QF mapping

Upstream flexible control uses quality-factor input compatible with FBCNN test scripts (`qf_input = [[1 - QF/100]]` pattern). Plugin `qualityMode=Automatic` omits override (blind). `Manual` supplies QF 0–100 per data model.

## Distribution

1. **Preferred**: Download ONNX (or export locally then cache) on first enable / Configure, into plugin/user data directory.
2. Ship Apache-2.0 LICENSE + NOTICE / attribution in plugin docs.
3. Verify `sha256` after download before enable succeeds.
4. Do not store models inside comic library folders.

## Export harness (dev only)

`harness/` (CPython + PyTorch) exports `.pth` → `.onnx`, runs latency on gitignored `testdata/` crops. Not required on end-user machines if pre-exported ONNX is downloaded.

## Runtime

Host loads ONNX via ONNX Runtime; IronPython MUST NOT load PyTorch.
