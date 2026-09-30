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

Pinned sha256 (FBCNN release v1.0 / local export 2026-09-30):

- `fbcnn_color.pth`: `8b0e4ef23d59cf7ac934a342cb31a17619e4fa4a0b3374a9d78c5174312387e8`
- `fbcnn_color.onnx` (blind): `a2b46206f6e705bc83dbc5641029b982e3d1ae0af1b1369f3792bee42088c9be`
- `fbcnn_color_manual.onnx`: `a6a7d028232f4510d052f520c64e6c76a40e6a29e60ea16549322d80c9a1b206`

| `fbcnn_gray` | `fbcnn_gray.pth` | `fbcnn_gray.onnx` | Optional gray path |

If `fbcnn_gray` is not shipped, Configure and enable MUST fail closed with a clear message for gray-only pages (or disclose limitation) — see tasks T032b.

Double-JPEG gray variant (`fbcnn_gray_double`) is out of v1 unless spike shows need.

## Flexible QF mapping

Upstream flexible control uses quality-factor input compatible with FBCNN test scripts (`qf_input = [[1 - QF/100]]` pattern). Plugin `qualityMode=Automatic` omits override (blind). `Manual` supplies QF 0–100 per data model.

## Distribution

1. **Preferred**: Download ONNX (or export locally then cache) on first enable / Configure, into plugin/user data directory.
2. Ship Apache-2.0 LICENSE + NOTICE / attribution in plugin docs.
3. **Integrity (FR-019)**: Before `InferenceSession` / enable succeeds, verify `sha256` of the on-disk file against the pinned digests above (by recognized filename). Applies to **manual placement and download**. Fail closed on mismatch.
4. **Path allowlist**: Model paths MUST resolve under an `ArtifactCleaner` directory (plugin Scripts tree or `%AppData%\cYo\ComicRack Community Edition\ArtifactCleaner\`). Reject other locations even if the hash would match.
5. Do not store models inside comic library folders.

## Export harness (dev only)

`harness/` (CPython + PyTorch) exports `.pth` → `.onnx`, runs latency on gitignored `testdata/` crops. Not required on end-user machines if pre-exported ONNX is downloaded.

## Runtime

Host loads ONNX via ONNX Runtime; IronPython MUST NOT load PyTorch.
