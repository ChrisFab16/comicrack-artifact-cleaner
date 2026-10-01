# Analyze Report: FBCNN (FR-021 DirectML GPU EP)

**Feature**: `specs/001-fbcnn-reader-toggle`  
**Date**: 2026-10-01  
**Constitution**: `.specify/memory/constitution.md` **v1.1.0** (loaded)

## Verdict

| Metric | Value |
|--------|-------|
| **CRITICAL** | **0** |
| **HIGH** | **0** (open product work T017/T021/T044 unchanged) |
| Gate for T057–T059 | **PASS** |

## Scope of this analyze

Artifact consistency after FR-021 / SC-011 (prefer DirectML GPU EP; CPU fallback; surface active EP in status/Configure). Prior FR-015 ASCII analyze remains valid; this pass adds GPU EP coverage.

## Coverage

| Requirement | Spec / plan / contract | Tasks |
|-------------|------------------------|-------|
| FR-021 | `spec.md`, `plan.md` Primary Dependencies, `contracts/model-package.md` | T057, T058, T059 `[X]` |
| SC-011 | `spec.md` Success Criteria | T057, T058 |
| FR-007 (no GPU init until enable) | unchanged | T057 (session only on TryLoad) |
| Constitution II (ASCII) | v1.1.0 | T054–T056 prior |

## Checks

- Spec ↔ plan ↔ contract agree: `Microsoft.ML.OnnxRuntime.DirectML`, `AppendExecutionProvider_DML`, CPU fallback, EP in status.
- CUDA toolkit not required for v1 (DirectML).
- No constitution conflicts: accelerator still deferred until first enable (Principle / FR-007).
- Implementation: host `FbcnnOnnxRunner` + plugin status text; NuGet DirectML; Engine `PlatformTarget=AnyCPU` so native `onnxruntime.dll` copies.

## Out of scope / still open

- T017 / T017b / T044 (async filter)
- T021 operator quickstart visual sign-off (confirm status shows `DirectML` on a DX12 GPU machine)
- US2–US5 Configure UI / download / QF / JPEG-only (T032 EP preference UI remains P2)

## Remediation

None for CRITICAL/HIGH from this pass.
