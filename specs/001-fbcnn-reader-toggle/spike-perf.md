# Spike: Performance policy (T014)

**Date**: 2026-09-30  
**Input**: [spike-model.md](./spike-model.md) CPU ORT numbers

## Decision

Full-res CPU inference is **too slow for sync page turns** (~4 s at 256², ~22 s at ~1K page). v1 policy:

1. **Always async** when filter is on: show unfiltered (or last-good) page immediately; non-blocking “processing” feedback (T017/T017b); swap when ready; cancel on page-turn / toggle-off.
2. **Default downscale** before infer: long edge **≤ 1024** (configurable in Configure later); upscale result to display size with high-quality resize. Document quality tradeoff in Configure copy.
3. **Optional tiling** deferred unless downscale+async still fails operator usability on target machines.
4. **GPU EP** (DirectML) enabled when available after T015b; CPU remains fallback.

## Budgets (operator / SC-005)

| Metric | Target |
|--------|--------|
| UI freeze without feedback | **Never** |
| Time-to-first-paint (unfiltered) when enabling | Immediate (stock path) |
| p95 filtered-ready after downscale (long edge ≤1024) on CPU | **≤ 25 s** first page (honest given spike); goal **≤ 8 s** with GPU or further downscale |
| Cached filtered revisit | Feels instant (memory cache hit) |
| Toggle-off | Immediate stock path; cancel in-flight work |

Plan.md provisional “≤2000 ms at 2000px” is **not** met on CPU full-res; supersede with the table above until GPU numbers land.

## plan.md Performance Goals (amendment)

Replace provisional 2000 ms full-page CPU goal with: async + long-edge≤1024 downscale; CPU p95 filtered-ready ≤25 s; GPU stretch goal ≤8 s; never block UI without feedback.
