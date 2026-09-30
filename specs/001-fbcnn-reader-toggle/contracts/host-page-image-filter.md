# Contract: Host page-image filter

**Feature**: `001-fbcnn-reader-toggle` | **Owner**: `ChrisFab16/ComicRackCE` (host)

## Purpose

Allow an optional, registered filter to transform **reader display bitmaps** during `ImagePool.GetPage` materialization without mutating comic archives.

## Interface (conceptual)

```text
IPageImageFilter
  bool IsEnabled(IComicDisplayContext ctx)
  FilterFingerprint GetFingerprint(IComicDisplayContext ctx)
  Bitmap Apply(Bitmap source, IComicDisplayContext ctx, out FilterStatus status)
  void Cancel(IComicDisplayContext ctx)   # optional; page-turn / toggle-off
```

Names are illustrative; implement may use Host API JSON-RPC equivalents if in-process interface is deferred — behavior MUST match.

## Pipeline contract

1. Decode page bytes → `Bitmap` (existing provider path).
2. If filter registered and `IsEnabled` → `Apply` (may be async at higher layer; see Performance).
3. Apply existing `BitmapAdjustment` / rotation as today.
4. Wrap as `PageImage` for display cache.

When filter disabled or absent: steps MUST match pre-feature CE behavior (SC-002).

## Cache identity

Display cache keys MUST include `FilterFingerprint` (or equivalent) when enabled:

- `enabled`, `modelId`, `qualityMode`, `qualityFactor` (if manual), policy version (downscale/tile id)

Toggle off or fingerprint change MUST invalidate or bypass stale entries (no mixed filtered/unfiltered hits).

## Non-destructive guarantee

`Apply` MUST operate only on in-memory bitmaps (and volatile caches). Implementations MUST NOT open comic archives for write, replace page files, or enqueue library “convert/optimize” jobs.

## Errors

| Condition | Behavior |
|-----------|----------|
| Weights missing / ONNX load fail | `FilterStatus.Failed`; caller shows UI error; display unfiltered |
| Apply throws | Catch at pool boundary; unfiltered fallback; log |
| Cancelled | Discard result; do not publish to cache as success |

## Performance

- MUST NOT block the UI thread for unbounded inference without feedback.
- Preferred: async completion with `PendingFilter` then cache publish.
- Provisional budget documented in [research.md](../research.md) R3; finalize after spike.

## Registration

Host discovers at most one active artifact-reduction filter for v1 (plugin or built-in runner). Silent no-op when plugin claims enable but no filter is registered is **forbidden** — enable MUST fail closed with explanation (FR-009).
