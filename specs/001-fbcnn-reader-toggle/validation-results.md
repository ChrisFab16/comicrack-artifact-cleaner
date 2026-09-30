# Validation results: 001-fbcnn-reader-toggle

## Build

- [X] `dotnet build ComicRack/ComicRack.csproj -c Debug -p:GenerateResourceUsePreserializedResources=true` succeeded (2026-09-30)
- [X] `Microsoft.ML.OnnxRuntime` 1.19.2 referenced from `ComicRack.Engine`
- [ ] Operator install of Debug CE + plugin + `fbcnn_color.onnx` under Scripts/ArtifactCleaner/weights/

## US1 — Quickstart Scenario A (T021)

| Check | Result |
|-------|--------|
| SC-001 filtered looks cleaner | _pending operator_ |
| SC-002 off matches stock | _pending operator_ |
| SC-003 archive hash unchanged | _pending operator_ |

### Notes

- Enable path: Automation → Artifact Cleaner (FBCNN) → host `SetArtifactReductionEnabled`
- First filtered page may hitch several seconds on CPU (downscale long-edge 1024; sync Apply in ImagePool). Status via page-activity indicator / WaitCursor on enable.
- True non-blocking swap-in (background + RefreshPage) is a follow-up if hitch is unacceptable.

## Non-destructive reminder

Never rewrite CBZ/CBR; only display cache.
