# Feature Specification: FBCNN JPEG Artifact Reader Toggle

**Feature Branch**: `001-fbcnn-reader-toggle`

**Created**: 2026-09-30

**Status**: Draft

**Input**: User description: "Reader toggle for FBCNN JPEG artifact reduction on ComicRack CE. When enabled, reader page images are processed with FBCNN (flexible blind JPEG artifact removal) so block noise and ringing are reduced. When disabled, behavior matches today's display pipeline. Non-destructive: display/render path only — never rewrite comic archives. Host page-image filter required (IronPython hooks alone cannot transform reader bitmaps). Default OFF; performance policy and loading feedback required."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Toggle artifact reduction while reading (Priority: P1)

While reading a JPEG-heavy comic in ComicRack CE, the user turns on an **FBCNN / artifact reduction** control for that reader window. Subsequent page displays look less blocky and ringy. Turning the control off restores the same rendering the user would get without the feature (existing color/brightness adjustments only). The comic file on disk and inside its archive is never modified.

**Why this priority**: This is the core product value — live, reversible cleanup of compressed page images during reading.

**Independent Test**: Open a known heavily JPEG-compressed sample book (gitignored / external testdata), enable the toggle, flip pages, confirm pages look cleaner; disable the toggle and confirm pages match the pre-enable look; verify the archive file size and contents are unchanged (e.g. same hash before/after the session).

**Acceptance Scenarios**:

1. **Given** a comic open in the reader with the feature available and weights ready, **When** the user enables artifact reduction, **Then** newly shown pages (and pages reloaded after enable) display with reduced JPEG blocking/ringing compared to the same pages with the feature off.
2. **Given** artifact reduction is enabled, **When** the user disables it, **Then** pages show the unfiltered display path again (existing image adjustments only), without requiring the user to close the book or restart ComicRack.
3. **Given** the user has toggled the feature on and off while reading, **When** they inspect the comic archive on disk, **Then** the archive bytes are identical to before the reading session (no rewrite, no sidecar overwrite of page files).

---

### User Story 2 - Safe default and first enable (Priority: P1)

On a fresh install, artifact reduction is **off**. Opening comics does not download models, initialize GPU/accelerator resources, or add processing delay until the user explicitly enables the feature (or opens Configure and triggers an explicit download/setup action). If enable fails (missing model, unsupported hardware, load error), the user sees a clear message and reading continues on the unfiltered path.

**Why this priority**: Trust and usability — the feature must not punish users who never turn it on, and must fail visibly rather than hang.

**Independent Test**: Fresh install; open a book and turn pages with the feature never enabled — no model download and no extra processing delay attributable to FBCNN; then enable without weights present and confirm a visible error and continued unfiltered reading.

**Acceptance Scenarios**:

1. **Given** a fresh install (or reset preferences), **When** the user opens a book without enabling artifact reduction, **Then** page turns behave like the stock display pipeline and no model download or accelerator init occurs for this feature.
2. **Given** the user enables artifact reduction when required resources are missing or fail to load, **When** the failure occurs, **Then** a user-visible error explains the problem, the toggle does not leave the reader in a hung state, and pages continue to display unfiltered.
3. **Given** long-running first-time setup (e.g. weight download) after the user opts in, **When** setup is in progress, **Then** the UI shows visible progress/wait feedback and the user can cancel or keep reading unfiltered.

---

### User Story 3 - Strength / quality control (Priority: P2)

The user can leave artifact reduction in automatic (blind) mode, or adjust a strength / quality control that trades artifact removal against detail preservation (matching FBCNN’s flexible quality-factor idea). Changing the control updates subsequent page displays without rewriting the archive.

**Why this priority**: Improves results on varied scan quality, but is not required for a usable MVP toggle.

**Independent Test**: Enable the feature, switch between automatic and a manual strength setting on the same sample page, and confirm the displayed result changes while the archive remains unchanged.

**Acceptance Scenarios**:

1. **Given** artifact reduction is on, **When** the user leaves strength on automatic, **Then** processing uses blind estimation without requiring a manual quality value.
2. **Given** artifact reduction is on, **When** the user sets a manual strength/quality value, **Then** subsequent page displays reflect that setting, and turning the feature off still restores the unfiltered path.

---

### User Story 4 - Configure models and performance options (Priority: P2)

From plugin Configure (or equivalent settings UI), the user can see model/status information, trigger weight download when redistribution requires it, and choose documented performance-related options (e.g. CPU vs accelerator preference, cache behavior) without editing files by hand. Configure remains available after first run (ongoing control).

**Why this priority**: Operators need ongoing control for install size, hardware, and troubleshooting; not required to prove the P1 toggle once defaults work.

**Independent Test**: Open Configure, change a documented option, enable the feature, and confirm behavior matches the saved setting across a ComicRack restart.

**Acceptance Scenarios**:

1. **Given** the plugin is installed, **When** the user opens Configure, **Then** current options and model/status info are shown and can be saved.
2. **Given** weights are not bundled and download-on-enable is the packaging choice, **When** the user triggers download from Configure or first enable, **Then** progress is visible and success/failure is reported clearly.

---

### User Story 5 - Optional JPEG-only scope (Priority: P3)

Optionally, the user (or a documented default) can limit processing to pages that appear to be JPEG sources, skipping formats where the cost is high and benefit is low (e.g. PNG/WebP), without changing those files on disk.

**Why this priority**: Performance refinement; MVP can process all reader pages when enabled if cost is acceptable after spikes.

**Independent Test**: Enable JPEG-only mode with a mixed-format book; confirm JPEG pages are filtered and non-JPEG pages remain on the unfiltered path; archive unchanged.

**Acceptance Scenarios**:

1. **Given** JPEG-only scope is enabled, **When** the reader shows a non-JPEG page, **Then** that page is not run through artifact reduction and still displays correctly.
2. **Given** JPEG-only scope is disabled (or MVP default processes all pages), **When** the feature is on, **Then** eligible pages follow the normal enable path.

---

### Edge Cases

- Toggle enabled mid-book → already-cached unfiltered pages MUST be invalidated or rebuilt so subsequent views use the filtered path; no archive rewrite.
- Toggle disabled mid-book → filtered cache entries MUST be invalidated or bypassed so the unfiltered path is shown again.
- Very large pages (e.g. 2000–4000+ px on a side) → system MUST follow the documented performance policy (async and/or tile/downscale) with loading feedback; MUST NOT freeze the UI indefinitely without feedback.
- Page turn while processing is still running → user MUST still be able to navigate; incomplete filtered results MUST NOT permanently replace the ability to see the unfiltered page when the feature is off.
- Missing or corrupt model/weights → clear error; unfiltered reading continues.
- Accelerator unavailable → fall back to CPU path if supported, or fail with a clear message; never silent hang.
- Feature unavailable because host filter is missing (plugin alone) → install/docs MUST state host dependency; enabling MUST fail closed with explanation rather than claiming success while doing nothing.
- Multiple reader windows → toggle state is **per reader window** (see Assumptions); enabling in one window MUST NOT force enable in another.
- Color vs grayscale comics → both MUST be supported for display filtering in v1, or unsupported cases MUST be documented and fail closed with a message.
- Existing color/brightness/contrast adjustments → when the feature is off, results MUST match today’s adjustment-only path; when on, filtering MUST compose with those adjustments in a documented order (plan decision) without rewriting the archive.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Users MUST be able to enable and disable FBCNN-based JPEG artifact reduction for comic **reader** page displays via a user-facing control.
- **FR-002**: When enabled, page images shown in the reader MUST be processed to reduce JPEG compression artifacts (blocking/ringing) using FBCNN (or an equivalent export of the same model lineage approved in plan research).
- **FR-003**: When disabled, reader page display MUST match the stock ComicRack CE display pipeline (existing image adjustments only) for the same book and settings.
- **FR-004**: The feature MUST be **non-destructive**: it MUST NOT rewrite, repack, or mutate comic archives, extracted page files, or other persistent book sources. Only the rendered/display path (and its volatile display cache) may be affected.
- **FR-005**: After any reading session that used the feature, archive integrity MUST be unchanged (operator can verify via file hash or equivalent).
- **FR-006**: Artifact reduction MUST default to **OFF** on fresh install and MUST remain off until the user explicitly enables it.
- **FR-007**: Model download, weight load, and accelerator initialization for this feature MUST NOT run until first enable or an explicit Configure action.
- **FR-008**: The system MUST provide a host-level page-image filter (or equivalent insert in the reader page materialization path). A plugin-only approach that cannot transform reader bitmaps MUST NOT be treated as a complete solution.
- **FR-009**: The toggle control MAY be provided by a plugin UI and/or host settings, but enablement MUST actually engage the host filter (no silent no-op enable).
- **FR-010**: Full-page processing MUST follow a documented performance policy (asynchronous processing and/or tiling and/or downscale-process-upscale) chosen after research spikes; the UI MUST show loading/processing feedback for non-instant work.
- **FR-011**: Failures (missing weights, load errors, unsupported path) MUST present user-visible diagnostics; the reader MUST remain usable on the unfiltered path.
- **FR-012**: Toggle state MUST apply **per reader window** for v1.
- **FR-013**: Users MUST be able to use automatic (blind) quality estimation; users SHOULD be able to override with a manual strength/quality control (P2).
- **FR-014**: Configure (or equivalent) MUST expose ongoing settings when options exist (model/status, download, performance preferences) — not setup-only.
- **FR-015**: Plugin scripts shipped for ComicRack MUST be ASCII-safe (or declare an explicit encoding) so Configure/hooks do not fail silently on punctuation.
- **FR-016**: Training new weights, batch library-wide archive rewriting, and replacing ComicRack’s global color-adjustment UI are OUT OF SCOPE for v1.
- **FR-017**: Upstream PRs to `maforget/ComicRackCE` MUST NOT be opened unless the operator explicitly requests them; host work targets the operator’s fork workflow.
- **FR-018**: Implementation planning MUST schedule pipeline + model spikes before polishing product UI, and MUST confirm weight license/redistribution before bundling.
- **FR-019**: Before creating an ONNX Runtime session for artifact reduction, the host MUST verify the model file’s SHA-256 digest against the pinned digests for known FBCNN artifacts (`contracts/model-package.md`). Mismatch, unrecognized filename, or disallowed path MUST fail closed (feature stays off; user-visible error). Integrity MUST apply on **every** enable/load — not only after download.
- **FR-020**: An automated **representative** test suite MUST cover: (a) model integrity fail-closed, (b) display-path inference changes pixels without mutating a comic archive file, (c) cache-key / fingerprint participation for on vs off. Operator Scenario A (T021) remains required for visual UI sign-off but MUST NOT be the first integrity/non-destructive proof.

### Key Entities

- **Reader window**: An open comic reading view; owns per-window toggle state for v1.
- **Display page image**: The bitmap shown to the user after decode and optional adjustments/filtering; not the on-disk archive entry.
- **Artifact-reduction setting**: On/off plus optional strength/quality mode; never implies archive mutation.
- **Model package**: FBCNN weights (color/gray as applicable) and runtime needed to run inference; may be bundled or downloaded on demand per legal packaging decision.
- **Host page filter**: The CE insert point that applies (or skips) artifact reduction when materializing reader pages and participates in display-cache identity so on/off invalidates correctly.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: With the feature on, a known heavily JPEG-compressed sample page is visibly cleaner (less blocking/ringing) than the same page with the feature off (operator screenshot comparison acceptable).
- **SC-002**: With the feature off, displayed pages are visually identical to the stock ComicRack CE display path for the same book and adjustment settings (operator side-by-side check).
- **SC-003**: After enabling and disabling the feature during a reading session, the comic archive file hash (or equivalent integrity check) matches the pre-session hash — zero durable mutation of the book source.
- **SC-004**: Fresh install with the feature never enabled: opening and paging through a book incurs no first-run model download for this feature and no user-visible hung state attributable to it.
- **SC-005**: Page navigation remains usable under the documented performance budget after spikes (target refined in plan; operator can finish a multi-page read without an unresponsive UI and without silent freezes longer than the stated feedback policy).
- **SC-006**: When weights are missing or load fails, the user sees an error within a few seconds of enable attempt and can continue reading unfiltered without restarting the app.
- **SC-007**: Spec Kit analyze reports CRITICAL=0 before implementation is treated as done; quickstart documents weight install/first enable and the archive-integrity check.
- **SC-008**: Enabling with a model file whose SHA-256 does not match the pinned digest (or an unrecognized/disallowed path) fails within a few seconds with a clear error; the filter stays off and reading continues unfiltered.
- **SC-009**: `scripts/run-representative-tests.sh` (plugin pytest + CE `ComicRack.Tests` FBCNN subset) exits 0 on a machine with `weights/fbcnn_color.onnx` present; integrity-negative cases pass without weights.

## Assumptions

- “Per reader window” matches the operator’s preferred toggle scope; a global preference may be added later without changing FR-004.
- Host filter work may live in the ComicRackCE fork while this repository owns the plugin package, packaging, and Spec Kit artifacts; both are in scope for the feature’s acceptance criteria.
- Official FBCNN pretrained weights are the intended model lineage; exact runtime (in-process vs sidecar) is a plan/research decision, not a user-visible requirement beyond FR-002/FR-010/FR-011.
- Sample validation pages are copyrighted and live outside git or under gitignored `testdata/`.
- Existing ComicRack image adjustments remain available; this feature does not replace them.
- MVP may process all pages when enabled; JPEG-only scoping (User Story 5) can ship later if spikes show unacceptable cost on non-JPEG pages.
- Color and grayscale models from the FBCNN release set are preferred; if one cannot be shipped legally or technically, Configure/docs MUST disclose the limitation.
