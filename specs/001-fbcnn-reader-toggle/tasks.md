# Tasks: FBCNN JPEG Artifact Reader Toggle

**Input**: Design documents from `/specs/001-fbcnn-reader-toggle/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Offline harness latency/export checks in `harness/` + `tests/`; operator ComicRack validation via `quickstart.md` (manual). Spec does not require full TDD for host UI.

**Organization**: Tasks grouped by user story. Tag ownership: **host** = `ChrisFab16/ComicRackCE`; **plugin** = this repo.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete work)
- **[Story]**: US1–US5 maps to spec user stories
- Include exact file paths (CE paths are under sibling `ComicRackCE/` checkout)

## Path Conventions

```text
# This repo
ArtifactCleaner/          # plugin package
harness/                  # ONNX export + latency CLI
tests/
specs/001-fbcnn-reader-toggle/

# Host fork (separate git repo)
../ComicRackCE/ComicRack.Engine/IO/Cache/ImagePool.cs
../ComicRackCE/ComicRack.Engine/IO/PageKey.cs
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Plugin + harness scaffolding in this repo; document CE fork workflow

- [X] T001 Create `ArtifactCleaner/` package tree (`Package.ini`, placeholder entry `.py`, `version.py`) per `plan.md`
- [X] T002 [P] Create `harness/` skeleton (`requirements.txt`, README for export/latency) and `tests/` directory
- [X] T003 [P] Add root `README.md` describing dual-repo layout (plugin here, host filter in ComicRackCE fork) and non-destructive guarantee
- [X] T004 [P] Add `scripts/package-crplugin.sh` (or `.ps1`) to zip `ArtifactCleaner/` as `.crplugin`
- [X] T005 [P] Ensure `.gitignore` covers `testdata/`, `*.onnx`, `*.pth`, `models/`, `weights/` (confirm existing entries)
- [X] T006 Document CE feature-branch naming for host work in `specs/001-fbcnn-reader-toggle/host-branch.md` (fork-only; no maforget PR)

---

## Phase 2: Foundational Spikes (Blocking Prerequisites)

**Purpose**: Prove pipeline, ONNX, API, and legal packaging before product UI polish

**CRITICAL**: No US1–US5 product implementation until spike exit criteria in `research.md` R8 are met (or explicitly waived with recorded evidence)

- [X] T007 [host] Pipeline spike: add gated post-process hook in `ComicRackCE/ComicRack.Engine/IO/Cache/ImagePool.cs` (`GetPage`) that can no-op or identity-copy a bitmap behind a settings/dev flag
- [X] T008 [host] Extend display-cache identity for filter fingerprint (extend `ComicRackCE/ComicRack.Engine/IO/PageKey.cs` or equivalent wrapper) and prove invalidate on flag toggle
- [X] T009 [P] [harness] Model spike: export `fbcnn_color.pth` → ONNX in `harness/export_fbcnn_onnx.py`; write notes to `specs/001-fbcnn-reader-toggle/spike-model.md`
- [X] T010 [P] [harness] Run latency on gitignored `testdata/` crop + full page (CPU; GPU if available); record ms/VRAM in `spike-model.md`
- [X] T011 [P] Legal spike: pin FBCNN Apache-2.0 + release asset attribution; decide download-vs-bundle in `specs/001-fbcnn-reader-toggle/spike-legal.md` (update `contracts/model-package.md` if needed)
- [X] T012 [host] API spike: sketch `IPageImageFilter` (or equivalent) in `ComicRackCE/ComicRack.Engine/` per `contracts/host-page-image-filter.md`; document registration in `specs/001-fbcnn-reader-toggle/spike-api.md`
- [X] T013 Confirm compose order decode → FBCNN → `BitmapAdjustment` (or spike-chosen alternative) in `spike-api.md` / `research.md` amendment
- [X] T014 Choose performance policy from spike numbers (async + optional downscale/tile); write **final** p95/feedback budgets into `specs/001-fbcnn-reader-toggle/spike-perf.md` and update `plan.md` Performance Goals (resolves SC-005 provisional ambiguity)

**Checkpoint**: Spikes done — host can toggle a flag affecting display only; ONNX runs offline; packaging decision recorded; API sketch exists

---

## Phase 3: User Story 1 - Toggle artifact reduction while reading (Priority: P1) MVP

**Goal**: Per-reader-window on/off runs FBCNN on display pages; off restores stock path; archive untouched

**Independent Test**: Quickstart Scenario A (screenshots + archive hash SC-001–003)

### Implementation for User Story 1

- [X] T015 [host] [US1] Implement `IPageImageFilter` + ONNX runner stub/service in `ComicRackCE` (e.g. `ComicRack.Engine/.../FbcnnPageImageFilter.cs`) per `contracts/host-page-image-filter.md`
- [X] T015b [host] [US1] Add `Microsoft.ML.OnnxRuntime` (and chosen EP) NuGet/package reference to the CE project that hosts the runner; document in fork README that ORT ships with the build (no ad-hoc DLL copy) per constitution IV
- [X] T016 [host] [US1] Wire filter into `ImagePool.GetPage` with fingerprint in cache key; ensure disabled path is bitwise/behaviorally stock
- [ ] T017 [host] [US1] Implement async pending/ready path + cancel on page-turn/toggle-off per `research.md` R3 and `spike-perf.md` — **reopened 2026-09-30**: US1 MVP still runs **sync** `Apply` on the GetPage factory (UI hitch). Cancel replaces CTS but cannot abort in-flight ORT `Run`. True async → **T044**
- [ ] T017b [host] [US1] Surface user-visible processing feedback when `processingStatus=PendingFilter` (reader overlay/status text) per FR-010; clear on Ready/Failed/cancel — **reopened**: `StatusText` exists for plugin MessageBox only; no reader overlay yet (depends on T044 pending state)
- [X] T018 [host] [US1] Add per-reader-window `ReaderWindowFilterState` storage on display/session object in ComicRackCE per `data-model.md` (window dict + `SetCurrentWindow` in `ComicDisplayControl.GetPageKey`; `ApplyForFingerprint` prefetch-safe)
- [X] T019 [P] [plugin] [US1] Implement toggle command entry in `ArtifactCleaner/artifact_cleaner.py` (ASCII-safe directives) calling host enable/disable API per `contracts/plugin-toggle-config.md`
- [X] T020 [plugin] [US1] On enable failure (no host filter / no weights), show error and keep disabled (no silent no-op)
- [ ] T021 [US1] Operator run quickstart Scenario A; record results in `specs/001-fbcnn-reader-toggle/validation-results.md` (include archive hash proof)
- [ ] T044 [host] [US1] Async filter pipeline: return unfiltered/pending without blocking GetPage; background FBCNN; cache+`RefreshPage` on ready; cancel abandons result (ORT Run still non-abortable mid-call); wire reader overlay for PendingFilter (completes T017+T017b)
- [X] T045 [host] [US1] [security] Before `InferenceSession`, verify ONNX SHA-256 against pinned digests in `contracts/model-package.md` and reject unrecognized filenames; fail closed with error string (FR-019 / SC-008) in `FbcnnOnnxRunner.TryLoad` (or shared helper)
- [X] T046 [host] [US1] [security] Allowlist model paths to directories containing `ArtifactCleaner` (plugin Scripts tree or AppData `...\ArtifactCleaner\`); reject other paths even if hash matches (FR-019)
- [X] T047 [P] [plugin] [US1] [security] Optional pre-check: refuse enable if local file hash ≠ pin (same digests); host remains authoritative

**Checkpoint**: MVP — toggle visibly cleans JPEG pages; off restores; hash unchanged. **Async/feedback (T017/T017b/T044) required before claiming FR-010 / spike-perf budgets met.** **Integrity (T045–T047) required before treating enable path as security-complete.**

---

## Phase 4: User Story 2 - Safe default and first enable (Priority: P1)

**Goal**: Default off; no model init until enable/Configure; failures visible; progress on download

**Independent Test**: Quickstart Scenario B (SC-004, SC-006)

### Implementation for User Story 2

- [ ] T022 [P] [plugin] [US2] Persist `PluginSettings` with `defaultEnabled=false` in `ArtifactCleaner/config.py` (or `config.xml` schema) per `data-model.md`
- [ ] T023 [host] [US2] Lazy-load ONNX session only on first successful enable (no load at CE startup) in FBCNN runner
- [ ] T024 [P] [plugin] [US2] Implement weight download-on-enable/Configure with progress UI **and Cancel** in `ArtifactCleaner/` per `contracts/model-package.md` and `spike-legal.md`; on cancel keep feature off and continue unfiltered reading
- [ ] T025 [plugin] [US2] After download, verify sha256 before enabling; surface corrupt/missing errors (complements host T045; download path MUST NOT bypass host verify)
- [ ] T026 [US2] Operator validate Scenario B in `validation-results.md`

**Checkpoint**: Fresh install idle path clean; fail-closed enable

---

## Phase 5: User Story 3 - Strength / quality control (Priority: P2)

**Goal**: Automatic (blind) QF plus optional manual strength mapped to FBCNN flexible control

**Independent Test**: Spec US3 — same page changes with manual vs automatic; archive unchanged

### Implementation for User Story 3

- [ ] T027 [host] [US3] Pass automatic vs manual QF into ONNX runner (`qf_input` mapping) per `contracts/model-package.md`
- [ ] T028 [P] [plugin] [US3] Expose quality mode + QF control in toggle UI or reader menu in `ArtifactCleaner/`
- [ ] T029 [host] [US3] Include `qualityMode`/`qualityFactor` in filter fingerprint; invalidate cache on change
- [ ] T030 [US3] Operator validate manual vs automatic visual difference; note in `validation-results.md`

**Checkpoint**: Blind works; manual override optional but functional

---

## Phase 6: User Story 4 - Configure models and performance options (Priority: P2)

**Goal**: Ongoing ConfigScript (or Web configure) for model status, download, EP preference

**Independent Test**: Quickstart Scenario D

### Implementation for User Story 4

- [ ] T031 [P] [plugin] [US4] Implement `ArtifactCleaner/config_script.py` + WinForms (or WebView2) configure UI per `contracts/plugin-toggle-config.md`
- [ ] T032 [plugin] [US4] Show model status, download action, execution-provider preference, attribution text (Apache-2.0)
- [ ] T032b [plugin] [US4] Grayscale support: either install/select `fbcnn_gray` ONNX **or** document fail-closed in Configure + enable error when gray pages cannot be filtered (spec edge / research R7)
- [ ] T033 [plugin] [US4] Ensure Configure reachable after first run (ongoing control); reload settings on next enable
- [ ] T034 [US4] Operator validate Scenario D in `validation-results.md`

**Checkpoint**: Settings not setup-only

---

## Phase 7: User Story 5 - Optional JPEG-only scope (Priority: P3)

**Goal**: Skip non-JPEG pages when `jpegOnly` is enabled

**Independent Test**: Spec US5 mixed-format book

### Implementation for User Story 5

- [ ] T035 [host] [US5] Detect JPEG vs other page source in filter gate; skip Apply for non-JPEG when `jpegOnly`
- [ ] T036 [P] [plugin] [US5] Add `jpegOnly` checkbox to Configure / toggle UI bound to `ReaderWindowFilterState`
- [ ] T037 [US5] Operator validate mixed-format book; record in `validation-results.md`

**Checkpoint**: P3 complete or explicitly deferred if spike cost acceptable without it

---

## Phase 8: Polish & Cross-Cutting

**Purpose**: Performance gate, docs, Spec Kit analyze, packaging

- [ ] T038 [P] Add Apache-2.0 NOTICE/attribution files under `ArtifactCleaner/licenses/` (FBCNN + ONNX runtime as applicable)
- [ ] T039 [P] Update root `README.md` with install, weight download, and non-destructive warning
- [ ] T040 Run quickstart Scenarios C (perf usability) and E (host missing filter); append `validation-results.md`
- [ ] T041 Package `.crplugin` via `scripts/package-crplugin.sh` and verify install under ComicRack Scripts path
- [X] T042 Pre-implement `/speckit-analyze` CRITICAL=0 recorded in `specs/001-fbcnn-reader-toggle/analyze-report.md` (SC-007). **Re-run analyze** only if spec/plan/tasks change materially after this gate; do not treat polish-phase analyze as the first gate
- [ ] T043 [P] Mark completed tasks `[X]` and ensure `specs/001-fbcnn-reader-toggle/` docs (`spec.md`/`plan.md`/`quickstart.md`) match shipped behavior

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup** → no deps
- **Phase 2 Spikes** → depends on Setup; **blocks all user stories**
- **US1 (Phase 3)** → after spikes; MVP
- **US2 (Phase 4)** → after US1 host filter exists (lazy load + download build on toggle)
- **US3 (Phase 5)** → after US1 ONNX path works
- **US4 (Phase 6)** → can start after US2 settings skeleton; polish parallel with US3
- **US5 (Phase 7)** → after US1 filter gate; optional defer
- **Polish (Phase 8)** → after desired stories; analyze before claiming done

### User Story Dependencies

| Story | Depends on | Independently testable? |
|-------|------------|-------------------------|
| US1 Toggle | Spikes | Yes — core MVP |
| US2 Safe default | US1 enable path | Yes — fresh install + missing weights |
| US3 QF control | US1 ONNX Apply | Yes — mode switch on sample page |
| US4 Configure | US2 settings/download | Yes — Config UI alone |
| US5 JPEG-only | US1 gate | Yes — mixed book |

### Parallel Opportunities

- T002–T005 (setup docs/scripts) in parallel
- T009–T011 (harness/legal) in parallel with T007–T008 (host pipeline) after T006
- T019 plugin toggle UI in parallel with T015–T018 host once API spike (T012) lands
- T027 host QF vs T028 plugin QF UI in parallel
- T031 configure UI parallel with US3 if settings schema stable

---

## Parallel Example: After spikes

```text
# Host track
T015 IPageImageFilter + ONNX runner
T015b ORT NuGet + ship-with-build docs
T016 ImagePool wire + cache key
T017 async pending/cancel          # open — sync MVP until T044
T017b processing feedback UI       # open — until T044
T018 per-window state
T044 async pipeline + overlay      # completes T017/T017b
T045 host SHA-256 pin verify       # FR-019
T046 host ArtifactCleaner path allowlist
T047 plugin pre-check hash (optional)

# Plugin track (after T012 API shape known)
T019 artifact_cleaner.py toggle
T020 fail-closed errors
```

---

## Implementation Strategy

### MVP First (US1 only)

1. Phase 1 Setup
2. Phase 2 Spikes (do not skip)
3. Phase 3 US1 → Quickstart Scenario A
4. **STOP and VALIDATE** before P2 UI polish

### Incremental Delivery

1. US2 fail-closed + lazy load
2. US3 manual QF
3. US4 Configure
4. US5 JPEG-only if needed
5. Phase 8 analyze + packaging

### Dual-repo note

Host commits stay on `ChrisFab16/ComicRackCE` feature branch; plugin/Spec Kit commits stay on this repo’s `001-fbcnn-reader-toggle`. Do not open maforget PRs unless operator asks (FR-017).

---

## Notes

- Non-destructive (constitution I): no task may add archive rewrite paths
- Spike evidence files under `specs/001-fbcnn-reader-toggle/spike-*.md` are required exit artifacts for Phase 2
- Operator tasks (T021, T026, T030, T034, T037, T040) stay open until live CE validation is recorded
- **2026-09-30 code-review remediation**: P1 ORT serialize + BGR24 convert + `RemoveKeys` (mem+disk) invalidation; P2 per-window ApplyForFingerprint + host quiet fail; P3 ArrayPool CHW + unused import cleanup. T017/T017b reopened; async → T044. Cancel does not abort mid-ORT Run (accepted until T044 abandon-result).
