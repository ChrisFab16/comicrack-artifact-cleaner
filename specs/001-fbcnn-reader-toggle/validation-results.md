# Validation results — FBCNN reader toggle

**Feature**: `001-fbcnn-reader-toggle`  
**Date**: 2026-09-30

## Automated representative suite (T048–T050 / SC-009) — PASS

### Plugin pytest (CPython — no IronPython)

```bash
cd comicrack-artifact-cleaner
python -m pip install -r tests/requirements.txt
python -m pytest tests/ -v
```

**Result**: 7 passed (2026-09-30)

| Test | Covers |
|------|--------|
| `test_archive_hash_unchanged_while_display_filter_runs` | FR-004/005: ORT mutates page pixels; CBZ hash unchanged |
| `test_mismatch_model_rejected_before_session` | FR-019: corrupt model ≠ pin |
| `test_contract_pin_matches_documented_blind_onnx` | Contract pin sync |
| `test_plugin_pins_match_contract` | Plugin pins sync |
| `test_weights_file_matches_pin_when_present` | Local weights integrity |
| `test_corrupt_file_does_not_match_pin` | Negative hash |
| `test_path_allowlist_shape` | ArtifactCleaner path rule |

### Host xUnit (`ComicRack.Tests`)

```bash
export FBCNN_ONNX_PATH=.../comicrack-artifact-cleaner/weights/fbcnn_color.onnx
cd ComicRackCE
dotnet test ComicRack.Tests/ComicRack.Tests.csproj -c Debug --filter "FullyQualifiedName~Fbcnn|FullyQualifiedName~PageKeyFilter"
```

**Result**: 7 passed (2026-09-30)

| Test | Covers |
|------|--------|
| `FbcnnModelIntegrityTests.*` | FR-019 allowlist + SHA-256 |
| `PageKeyFilterFingerprintTests.*` | Cache key on/off |
| `FbcnnOnnxRunnerSmokeTests.Apply_ChangesPixels_DoesNotRequireArchive` | Host ORT apply without archive |

### Runner script

`scripts/run-representative-tests.sh` — runs both tiers.

## Operator Scenario A (T021) — pending

Automated gate is green. Manual CE UI sign-off (screenshots + live archive hash) still open.

## FR-021 DirectML (T057–T059) — 2026-10-01

- Host NuGet: `Microsoft.ML.OnnxRuntime.DirectML` 1.19.2 (replaces CPU-only package)
- `FbcnnOnnxRunner.TryLoad`: DirectML first, CPU fallback; `ActiveExecutionProvider` exposed
- Status text: `Artifact reduction on (DirectML|CPU)`; Configure/enable MessageBox shows status
- Deploy: `%LOCALAPPDATA%\ComicRackCE-FBCNN` with DirectML-flavored `onnxruntime.dll` (~14.3 MB)
- xUnit Fbcnn filter: **5 passed** after rebuild
