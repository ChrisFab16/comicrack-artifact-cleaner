# Starting prompt — FBCNN JPEG artifact reduction toggle (reader)

**Use this** as the `$ARGUMENTS` / feature description for `/speckit-specify` on **ComicRackCE** (`development`), or paste into a new agent chat that must run full Spec Kit before code.

**Repo:** `ChrisFab16/ComicRackCE` (fork). Do **not** open PRs to `maforget/ComicRackCE` unless the operator asks.  
**Related:** plugin packaging / Host API patterns from `specs/006-plugin-webview-host`, `007-plugin-web-kind`, `008-webview-html-panels`.

---

## One-sentence product goal

Add a **user-facing toggle** (reader / plugin UI) that, when on, runs **FBCNN** on comic **reader page images** to reduce JPEG compression artifacts, with sensible performance defaults and an escape hatch back to raw pages.

---

## What FBCNN is (background for the plan)

- **Paper:** Jiang, Zhang, Timofte — *Towards Flexible Blind JPEG Artifacts Removal* (ICCV 2021).  
  - Open access: https://openaccess.thecvf.com/content/ICCV2021/html/Jiang_Towards_Flexible_Blind_JPEG_Artifacts_Removal_ICCV_2021_paper.html  
  - arXiv: https://arxiv.org/abs/2109.14573  
- **Official code:** https://github.com/jiaxi-jiang/FBCNN (PyTorch).  
- **Idea:** A *blind* CNN that estimates a JPEG quality factor (QF) and reconstructs the image; the QF can also be **manually overridden** to trade artifact removal vs detail preservation (“flexible” control).  
- **Pretrained weights (GitHub release `model_zoo`):**  
  - `fbcnn_color.pth` — color single-JPEG  
  - `fbcnn_gray.pth` — grayscale single-JPEG  
  - `fbcnn_gray_double.pth` — grayscale double-JPEG (paper FBCNN-A)  
- **Inference shape (from upstream test scripts):** load RGB/gray tensor → `model(img)` or `model(img, qf_input)` → restored image + predicted QF. Flexible control uses `qf_input = [[1 - QF/100]]`.  
- **License / packaging:** confirm FBCNN repo license and weight redistributability before bundling weights in the plugin zip; prefer download-on-first-enable if redistribution is unclear.

**Not the same as:** ComicRack’s existing `BitmapAdjustment` (saturation / brightness / contrast / gamma / sharpen / auto-contrast). FBCNN is a learned JPEG deblocker, not a color slider.

---

## ComicRackCE realities the plan MUST confront

### 1. There is no plugin hook today that transforms reader page bitmaps

Documented IronPython hooks (`PluginEngine.ValidHooks`) include among others:

| Hook | Useful for this feature? |
|------|--------------------------|
| `Books` / `Library` / `Editor` | Menu commands / toggle entry points |
| `ConfigScript` | Preferences “Configure…” for the plugin |
| `BookOpened` | Know when a book opens (not per page paint) |
| `ReaderResized` | Only `(width, height)` — sample in `ComicRack/Output/Scripts/Sample.py` adjusts `ComicDisplay` flags; **does not** receive page bitmaps |
| `DrawThumbnailOverlay` | GDI+ overlay on **library thumbnails**, not reader pages |
| `ComicInfoHtml` / `QuickOpenHtml` | Side panels (WebView2) — not page pipeline |

**Implication:** a pure IronPython plugin **cannot** inject FBCNN into the reader by itself. Spec Kit must treat this as **host + plugin** (or an explicit spike that proves an alternate path).

### 2. Where pages become display bitmaps (host insert point)

Reader pages flow through the image pool. Color adjustment is applied when materializing a page:

- `ComicRack.Engine/IO/Cache/ImagePool.cs` — `GetPage(...)` path uses `bitmap.CreateAdjustedBitmap(bitmapAdjustment, ...)`.  
- Adjustment model: `cYo.Common.Drawing.BitmapAdjustment` / `ImageProcessing.CreateAdjustedBitmap`.  
- Keys include adjustment in `PageKey` (`ComicBook.GetPageKey(page, bitmapAdjustment)`), so cache identity already depends on processing parameters.

**Plan should decide** among (non-exclusive) options:

1. **Preferred (clean):** Host API / engine hook — e.g. optional page post-process after decode (and after or before `BitmapAdjustment`), with cache key including “FBCNN on + QF mode + model id”.  
2. **Plugin-only dead end to reject unless spike succeeds:** overlay second window, rewrite CBZ on disk, etc.  
3. **Hybrid:** CE exposes `IPageImageFilter` (or Host API method) registered by a `kind: web|python` plugin; FBCNN runs out-of-process or via ONNX.

### 3. Runtime: IronPython ≠ PyTorch

ComicRack plugins run **IronPython 2.7** inside the .NET process. FBCNN upstream is **PyTorch**. Plan must pick an execution strategy:

| Approach | Pros | Cons |
|----------|------|------|
| **ONNX Runtime (C#)** in CE or a native helper | Fits .NET host; no IronPython ML | Export FBCNN → ONNX; ship `Microsoft.ML.OnnxRuntime` (+ GPU optional) |
| **Sidecar Python process** (PyTorch) | Closest to official weights | Process life-cycle, IPC latency, install burden, security |
| **Preprocess offline** | Simple | Not a live reader toggle |

Default recommendation for Spec Kit **research.md**: spike ONNX export of `fbcnn_color` on a few comic JPEG pages; measure ms/page on CPU vs GPU; decide gating (enable only if &lt; N ms or async with placeholder).

### 4. Performance / UX constraints (must be FRs)

- Full comic pages are often **2000–4000+ px** on a side. Naïve full-res FBCNN on CPU will hitch page turns.  
- Spec should require one of: tile inference, downscale→process→upscale policy (document quality tradeoff), async process with “processing…” state, or “apply only when idle / on demand”.  
- Toggle **per reader window** (user ask) vs global setting — clarify in specify:  
  - **Per window** implies state on `IComicDisplay` / open book view.  
  - Global is easier (Preferences + plugin Config).  
- Prefer **non-destructive**: never rewrite the archive; only affect display cache.  
- Toggle off must restore unfiltered pages (invalidate/rebuild page cache keys).

### 5. ASCII / packaging lessons (this fork)

- IronPython sources: **ASCII-only** (or `# -*- coding: utf-8 -*-`); Unicode punctuation has already caused silent ConfigScript failures (Library Organizer).  
- Plugin zip: nested `ui/dist` paths must survive `PackageManager.UnzipFile` (006).  
- Configure UI: can be classic WinForms **or** WebView2 SPA via `plugin.json` `ui.configure` + `ShowWebConfigure` (006).  
- Loading feedback: long ops need a visible wait/overlay (operator requirement from LO Configure work).

### 6. Spec Kit process (mandatory on this repo)

Order: `/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → **`/speckit-analyze`** (CRITICAL=0) → checklist-pre-implement → `/speckit-implement`.  
No silent hotfixes. Feature branch via Spec Kit git extension from `development`.

---

## Suggested user stories (for specify to refine)

1. **P1 — Toggle in reader:** While reading a JPEG-heavy comic, user turns **FBCNN** on; subsequent page displays look less blocky/ringy; turning off restores original rendering.  
2. **P1 — Safe default off:** Fresh install: filter off; no model download / GPU init until first enable (or explicit Configure).  
3. **P2 — Strength / QF control:** User can leave QF automatic (blind) or set a strength/QF slider (maps to FBCNN flexible control).  
4. **P2 — Configure:** Plugin Configure explains model path, CPU/GPU, cache, and “download weights”.  
5. **P3 — Scope limit:** Optional “only when page looks JPEG” heuristic (e.g. source ext `.jpg` / mime) — do not run on PNG/WebP if cost is high.

## Explicit non-goals (unless operator expands)

- Replacing ComicRack’s global color adjustment UI.  
- Training new FBCNN weights.  
- Batch library-wide CBZ rewriting.  
- Upstream PR to maforget without operator OK.  
- Running full PyTorch inside IronPython.

## Success criteria sketches

- SC-1: With toggle on, a known heavily JPEG’d sample page is visibly cleaner than toggle off (operator screenshot OK).  
- SC-2: Page turn remains usable (define budget in plan after spike, e.g. p95 &lt; 250 ms cached / async).  
- SC-3: Toggle off shows bitwise-or visually identical pipeline to today’s `BitmapAdjustment`-only path.  
- SC-4: Spec Kit analyze CRITICAL=0; quickstart documents weight install + first enable.  
- SC-5: Failure modes show UI (missing weights, ONNX load fail) — never silent hang.

## Research spikes the plan should schedule first

1. **Pipeline spike:** Minimal CE change that post-processes one `Bitmap` in `ImagePool.GetPage` behind a settings flag; prove cache key invalidation.  
2. **Model spike:** Export `fbcnn_color.pth` → ONNX; run on a comic page crop in a console harness; record latency/VRAM.  
3. **API spike:** Design plugin registration surface (C# interface vs Host JSON-RPC vs settings-only host feature with thin IronPython toggle).  
4. **Legal spike:** FBCNN license + weight redistribution.

## Prompt for `/speckit-specify` (copy-paste)

```text
Feature: Reader toggle for FBCNN JPEG artifact reduction on ComicRack CE.

Build a fork-only feature (ChrisFab16/ComicRackCE development) that lets the user
toggle FBCNN-based JPEG artifact reduction for comic reader windows. When enabled,
page images shown in the reader are processed with FBCNN (ICCV 2021 flexible blind
JPEG artifact removal; official repo https://github.com/jiaxi-jiang/FBCNN) so block
noise and ringing are reduced. When disabled, behavior matches today’s display
pipeline (existing BitmapAdjustment only).

Constraints and facts the spec must respect:
- IronPython hooks today cannot transform reader page bitmaps (ReaderResized is
  size-only; DrawThumbnailOverlay is library thumbs only). Expect a host page-image
  filter hook or equivalent in ImagePool/GetPage, plus a plugin or settings toggle.
- Do not run PyTorch inside IronPython; prefer ONNX Runtime in-process or a
  well-specified sidecar after a research spike.
- Non-destructive: display-cache only; do not rewrite comic archives.
- Performance: full-page CNN is expensive — specify async/tile/downscale policy
  and loading feedback; toggle default OFF.
- Optional flexible QF/strength control matching FBCNN’s adjustable quality factor.
- ASCII-safe plugin scripts; Spec Kit full gate (specify→plan→tasks→analyze→
  checklist→implement). No maforget upstream PR unless operator asks.

Out of scope v1: training weights, batch CBZ rewrite, replacing color-adjustment UI.

Write FR/SC/edge cases suitable for a Spec Kit plan that starts with pipeline +
ONNX spikes before product UI.
```

---

## Operator notes

- Preferred next command after pasting: `/speckit-specify` with the copy-paste block (or attach this file).  
- If the agent proposes plugin-only without a host filter hook, reject and point at §“ComicRackCE realities”.  
- Sample JPEG pages for validation should live outside the repo or under a gitignored `testdata/` path (copyright).
