# Spike: Pipeline (T007–T008) + API sketch (T012–T013)

**Host branch**: `ChrisFab16/ComicRackCE` → `001-fbcnn-reader-toggle`  
**Date**: 2026-09-30

## Changes

| File | Role |
|------|------|
| `ComicRack.Engine/IO/IPageImageFilter.cs` | Filter contract |
| `ComicRack.Engine/IO/PageImageFilterHost.cs` | Registration + `EnableDevIdentityFilter` |
| `ComicRack.Engine/IO/PageKey.cs` | `FilterFingerprint` in Equals/GetHashCode; ctor reads `PageImageFilterHost.CurrentFingerprint` |
| `ComicRack.Engine/IO/Cache/ImagePool.cs` | Apply filter after decode, before `CreateAdjustedBitmap`; skip raw-byte fast path when fingerprint set |

## Compose order (T013)

**Decision**: decode → **page filter** → `BitmapAdjustment` → rotation.

When filter off / fingerprint empty: identical to prior stock path (including byte-image fast path).

## How to exercise spike

```csharp
PageImageFilterHost.EnableDevIdentityFilter(true);
// open/navigate pages — cache keys include "dev-identity:1"
PageImageFilterHost.EnableDevIdentityFilter(false);
// RefreshPage / reopen — stock keys again
```

No archive writes. Dev filter clones bitmap only (identity).

## API sketch (T012)

See `IPageImageFilter` + `PageImageFilterHost`. v1: single active filter. Plugin/US1 will set a real FBCNN ONNX filter instead of `DevIdentityPageImageFilter`.

## Exit criteria

- [X] Gated post-process in `GetPage`
- [X] Cache identity includes fingerprint
- [ ] Operator/build verify EnableDevIdentityFilter on/off (pending CE rebuild on workstation)
- [X] Compose order documented
