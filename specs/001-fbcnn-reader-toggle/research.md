# Research: FBCNN JPEG Artifact Reader Toggle

**Feature**: `001-fbcnn-reader-toggle` | **Date**: 2026-09-30

## R1 — Host insert point

**Decision**: Add an optional page post-process in ComicRackCE `ImagePool.GetPage` after decode and **before** `CreateAdjustedBitmap`, gated by a registered `IPageImageFilter` (name TBD) whose parameters participate in display-cache identity (extend `PageKey` or wrap key with filter fingerprint).

**Rationale**: Today `GetPage` decodes then applies `BitmapAdjustment` (`ImagePool.cs` ~254–323). IronPython hooks (`ReaderResized`, `DrawThumbnailOverlay`, etc.) never receive page bitmaps. Inserting before color adjustment keeps deblocking closer to the JPEG decode and preserves “toggle off = today’s path” by skipping the filter entirely.

**Alternatives considered**:
- Plugin-only overlay / second window — rejected (poor UX, not true page pipeline).
- Rewrite CBZ on disk — rejected (violates constitutive non-destructive rule).
- Filter after `BitmapAdjustment` — workable fallback if insert before adjustment proves awkward with disk partial-page cache; spike may choose after-adjust if simpler, but must still skip entirely when off.

## R2 — Inference runtime

**Decision**: Prefer **ONNX Runtime in-process** in the CE host (C#). Export `fbcnn_color.pth` (and gray as needed) to ONNX in an offline harness. Do **not** run PyTorch inside IronPython.

**Rationale**: Fits .NET host, avoids IronPython ML stack, keeps lifecycle inside the app. Sidecar Python reserved as contingency if ONNX export/accuracy/latency spike fails.

**Alternatives considered**:
- Sidecar PyTorch process — higher fidelity to upstream, worse install/IPC/security.
- Offline batch preprocess — not a live reader toggle.

## R3 — Performance policy (provisional)

**Decision**: **Async display**: when filter is on, show the unfiltered (or last-good) page immediately if filtered result is not ready; show non-blocking “processing” feedback; swap in filtered bitmap when complete; cancel/ignore stale work on page turn or toggle-off. After model spike, if full-res CPU p95 ≫ 2s, enable **downscale→infer→upscale** and/or **tiling** with documented quality tradeoff. Provisional budget: p95 filtered-ready ≤ 2000 ms on CPU for ~2000px-wide page under chosen policy; refine numbers in tasks after spike evidence.

**Rationale**: Full comic pages (2000–4000+ px) will hitch naïve sync CPU inference. Spec FR-010/SC-005 require usable navigation + feedback, not a hard sync budget before measurement.

**Alternatives considered**: Sync-only gate (enable only if &lt; N ms) — too brittle for first ship; idle-only apply — weaker UX for “toggle while reading.”

## R4 — Plugin ↔ host API

**Decision**: Hybrid: CE exposes `IPageImageFilter` (or Host API registration) implemented by a host-side ONNX runner; IronPython plugin (or thin host menu) sets **per-reader-window** enable + QF mode and calls into host to attach filter state to the open display. Plugin Configure owns download path, EP preference (CPU/GPU), and status.

**Rationale**: Matches FR-008/009; keeps ML out of IronPython; toggle UX can live in plugin while pixels stay in engine.

**Alternatives considered**:
- Settings-only host feature with no plugin — less flexible packaging/branding.
- JSON-RPC Host API only — possible later; start with in-process interface for latency.

## R5 — Legal / packaging

**Decision**: FBCNN upstream is **Apache License 2.0** (code + project). Redistribution of weights is permitted under Apache-2.0 terms with LICENSE/NOTICE attribution. Prefer **download-on-first-enable** (or Configure download) for large `.pth`/`.onnx` files to keep the plugin zip small; bundling remains legally OK if NOTICE is shipped. Confirm release asset terms once more when pinning a specific GitHub release hash during implement.

**Rationale**: Satisfies FR-018; avoids shipping tens/hundreds of MB in the initial package while staying compliant.

**Alternatives considered**: Always-bundle weights — simpler offline UX, larger package.

## R6 — Compose order with BitmapAdjustment

**Decision**: Default compose: **decode → FBCNN (if on) → BitmapAdjustment → rotation**. When FBCNN off, path is unchanged from current CE. Cache key MUST include filter fingerprint (on/off, model id, QF mode/value) in addition to existing `BitmapAdjustment`.

**Rationale**: Toggle-off identity with today’s pipeline; cache correctness prevents stale filtered/unfiltered pages.

## R7 — Color / gray models

**Decision**: v1 targets `fbcnn_color` primarily; add `fbcnn_gray` if spike shows color model mishandles gray pages. Fail closed with UI if required model missing.

## R8 — Spikes (must precede UI polish)

| Spike | Goal | Exit criteria |
|-------|------|----------------|
| Pipeline | Minimal CE flag post-process in `GetPage` + cache invalidation | Toggle-equivalent flag changes displayed page; off restores prior path; no file writes |
| Model | Export color weights → ONNX; run crop + full page | Visual cleanup on sample JPEG; latency/VRAM table CPU (± GPU) |
| API | Sketch `IPageImageFilter` + per-window state | Plugin can enable/disable without silent no-op |
| Legal | Pin LICENSE + release NOTICE requirements | Written packaging decision (download vs bundle) |

## Open items resolved by defaults

| Topic | Default |
|-------|---------|
| Per-window vs global | Per reader window (spec FR-012) |
| Manual QF | P2 after blind mode works |
| JPEG-only scope | P3; MVP may process all pages when on |
| maforget PR | Not in scope unless operator asks |
