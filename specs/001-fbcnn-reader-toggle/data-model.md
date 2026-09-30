# Data Model: FBCNN JPEG Artifact Reader Toggle

**Feature**: `001-fbcnn-reader-toggle` | **Date**: 2026-09-30

## Entities

### ReaderWindowFilterState

Per open reader window (not global for v1).

| Field | Type | Rules |
|-------|------|-------|
| `enabled` | bool | Default `false`. When false, host MUST skip filter (stock path). |
| `qualityMode` | enum: `Automatic` \| `Manual` | Default `Automatic`. |
| `qualityFactor` | int? 0–100 | Required when `Manual`; maps to FBCNN flexible QF control. Ignored when `Automatic`. |
| `jpegOnly` | bool | Default `false` (MVP). When true, skip non-JPEG sources (P3). |
| `modelId` | string | e.g. `fbcnn_color` / `fbcnn_gray`; included in cache fingerprint. |

**Transitions**:
- `enabled false → true`: validate model ready; on failure keep `enabled=false` and surface error; on success invalidate display cache for this window’s book pages under old keys.
- `enabled true → false`: invalidate filtered cache entries; subsequent `GetPage` uses stock path.
- `qualityMode` / `qualityFactor` / `modelId` change while enabled: update fingerprint; invalidate affected cache entries.

### DisplayPageImage

Volatile bitmap shown to the user. **Not** an archive entity.

| Field | Notes |
|-------|-------|
| `pageIndex` | Book page index |
| `adjustment` | Existing `BitmapAdjustment` |
| `filterFingerprint` | Derived from `ReaderWindowFilterState` when enabled; empty/absent when off |
| `processingStatus` | `Ready` \| `PendingFilter` \| `Failed` (for async UI) |

### ModelPackage

| Field | Rules |
|-------|-------|
| `id` | Stable id (`fbcnn_color`, …) |
| `format` | `onnx` (runtime) / source `pth` (export only) |
| `path` | Under plugin/user data dir — never inside the comic archive |
| `sha256` | Verify after download |
| `licenseNotice` | Apache-2.0 attribution present in package docs |

### PluginSettings (persisted)

Ongoing Configure defaults (may seed new windows; does not force other open windows).

| Field | Rules |
|-------|-------|
| `defaultEnabled` | Always `false` for v1 fresh install |
| `executionProvider` | `CPU` \| `DirectML` \| … (after spike) |
| `weightsDirectory` | Writable path outside library |
| `downloadUrl` / release pin | Documented in model-package contract |
| `maxLongEdge` | Optional downscale cap after spike |

## Validation rules

- Enabling with missing/corrupt weights → fail closed; do not set `enabled=true`.
- No entity may reference “write back to archive” or “replace page bytes on disk.”
- Cache identity MUST change when `filterFingerprint` changes so on/off cannot serve the wrong bitmap.

## Relationships

```text
ReaderWindow 1──1 ReaderWindowFilterState
ReaderWindowFilterState ──uses── ModelPackage
DisplayPageImage ──keyed by── (pageIndex, adjustment, filterFingerprint)
PluginSettings ──seeds── new ReaderWindowFilterState (defaults only)
```
