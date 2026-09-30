<!--
Sync Impact Report
- Version change: template → 1.0.0
- Modified principles: placeholders → FBCNN artifact cleaner principles
- Added sections: Plugin Constraints, Workflow Expectations
- Removed sections: none
- Templates requiring updates: ✅ constitution filled; plan/spec/tasks templates remain generic Spec Kit defaults (compatible)
- Follow-up TODOs: none
-->

# ComicRack Artifact Cleaner Constitution

## Core Principles

### I. Non-Destructive Display Only
The plugin and any companion host filter MUST operate only on the **rendered
display image** (reader page bitmap / display cache). They MUST NOT rewrite,
repack, or mutate the comic archive, page files on disk, or any other
persistent book source. Toggle off MUST restore the unfiltered display path
(existing `BitmapAdjustment`-only pipeline). Batch CBZ/CBR rewriting and
offline "optimize library files" modes are out of scope unless the operator
explicitly expands a future feature with its own Spec Kit gate.

### II. Host-Compatible Filter Surface
IronPython hooks alone cannot transform reader page bitmaps today. Features
that affect page pixels MUST include an explicit host insert point (e.g.
`ImagePool` / page post-process / registered page-image filter) plus a
plugin or settings toggle. Plugin-only workarounds that rewrite files or
overlay a second viewer MUST be rejected unless a documented spike proves
otherwise. Plugin scripts MUST use documented ComicRack CE directives and
hooks; IronPython sources MUST be ASCII-safe (or declare UTF-8 encoding).

### III. Safe Runtime Defaults
FBCNN MUST NOT run as PyTorch inside IronPython. Preferred path is ONNX
Runtime (or a research-spiked sidecar) after export of official weights.
Filter MUST default **OFF**. Model download / GPU init MUST NOT run until
first enable or explicit Configure. Failures (missing weights, load errors)
MUST surface in the UI — never hang silently. Performance policy
(async/tile/downscale) MUST be specified before shipping full-page inference.

### IV. Self-Contained Packaging
The deliverable MUST install as a ComicRack script/plugin package
(`Package.ini` / `plugin.json`, entry scripts, assets). Users MUST NOT be
required to copy ML runtimes into ad-hoc paths without documented install.
Weight redistributability MUST be confirmed before bundling; otherwise use
download-on-first-enable. Version metadata MUST stay accurate.

### V. Spec-Driven, Verifiable Delivery
Feature work MUST follow Spec Kit: specify → plan → tasks → **analyze** →
implement. Analyze is mandatory before implementation. Changes MUST be
verifiable with harness/spike evidence (pipeline + latency) plus an operator
quickstart that proves toggle on cleans a sample JPEG page and toggle off
restores original rendering without touching the archive.

## Plugin Constraints

- Runtime target is ComicRack Community Edition (IronPython 2.7 plugins;
  host filter may be C# / ONNX).
- Prefer fork-only work on `ChrisFab16/ComicRackCE` for host hooks; do not
  open PRs to `maforget/ComicRackCE` unless the operator asks.
- Configure UI (WinForms or WebView2) MUST expose ongoing controls when
  settings exist — not setup-only.
- Sample/copyrighted comic pages for validation MUST stay outside the repo
  or under a gitignored `testdata/` path.

## Workflow Expectations

- Active feature directory is recorded in `.specify/feature.json`.
- `spec.md`, `plan.md`, and `tasks.md` under that directory are the source of
  truth for slash-command workflows.
- Git feature branches use sequential numbering (`NNN-short-name`) via the git
  extension.
- Auto-commit after constitution / specify / clarify / plan / tasks /
  checklist / analyze; not after implement unless reconfigured.

## Governance

This constitution supersedes informal practice for this repository. Amendments
require updating `.specify/memory/constitution.md`, bumping the version per
semver (MAJOR for incompatible principle changes, MINOR for new principles,
PATCH for clarifications), and aligning Spec Kit artifacts before further
implementation. Compliance is checked during `/speckit-analyze` and review
before release packaging. Principle I (non-destructive display only) is
non-negotiable for v1 product scope.

**Version**: 1.0.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-09-30
