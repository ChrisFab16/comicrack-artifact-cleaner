<!--
Sync Impact Report
- Version change: 1.0.0 → 1.1.0
- Modified principles: II (IronPython ASCII / encoding / #@ directive rules expanded)
- Added sections: none (Plugin Constraints bullets expanded)
- Removed sections: none
- Templates requiring updates: plan/spec/tasks/contracts for FR-015 clarification; AGENTS.md created
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
hooks.

**IronPython source rules (CE host, same class of failures as comicwiki /
Library Organizer):**

1. Prefer **pure ASCII** in all shipped `.py` under `ArtifactCleaner/` (no
   em dashes, smart quotes, or other Unicode punctuation).
2. If any non-ASCII is unavoidable, a PEP 263 coding cookie
   (`# -*- coding: utf-8 -*-`) MUST appear on **line 1 or 2** — IronPython
   ignores a cookie later in the file (Configure then fails with
   `Non-ASCII character '\xe2' ... no encoding declared`).
3. Put the coding cookie on **line 1** (comicwiki pattern), then `#@`
   directives.
4. Never put `#@Name` / `#@Hook` / other `#@` sequences in comments: CE’s
   `PythonPluginInitializer` uses `Regex.Match` (anywhere on the line) and
   will overwrite metadata.

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
- Automated tests MUST gate FR-015 (ASCII / coding-cookie) for
  `ArtifactCleaner/*.py` so Configure regressions are caught without a host
  click-through.

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

**Version**: 1.1.0 | **Ratified**: 2026-09-30 | **Last Amended**: 2026-10-01
