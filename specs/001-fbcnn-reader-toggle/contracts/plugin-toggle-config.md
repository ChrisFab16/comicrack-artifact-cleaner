# Contract: Plugin toggle and Configure

**Feature**: `001-fbcnn-reader-toggle` | **Owner**: this repo (IronPython plugin)

## Purpose

Expose user-facing enable/disable (per reader window), optional QF/strength, and ongoing Configure for model/download/performance — without rewriting comics.

## Hooks / entry points

| Surface | Role |
|---------|------|
| Reader / Books / menu command (exact hook chosen in implement) | Toggle enable for **current reader window** |
| `ConfigScript` | Ongoing settings UI (not setup-only) |
| Optional WebView2 configure | Allowed if host supports `plugin.json` UI; WinForms OK |

Scripts MUST be ASCII-safe or declare UTF-8 encoding (FR-015).

## Toggle behavior

1. Resolve current reader window context.
2. If enabling: ask host whether filter + weights are ready; if not, show error and leave disabled.
3. Set `ReaderWindowFilterState.enabled` via host API.
4. Trigger display refresh / cache invalidation for that window.
5. Never mutate archive paths.

Disabling always restores stock display path for that window only (other windows unchanged).

## Configure fields (v1)

- Model status (installed / missing / hash)
- Download weights action + progress
- Execution provider preference (CPU / accelerator after spike)
- Optional max long-edge / performance policy (after spike)
- Link to FBCNN attribution (Apache-2.0)

Defaults: feature off; no download until user action.

## Errors (user-visible)

| Event | Message intent |
|-------|----------------|
| Host filter missing | “This ComicRack build does not support page filters; update fork build …” |
| Weights missing | “Model not installed; download from Configure or cancel” |
| Load/inference fail | Short reason; reading continues unfiltered |

## Out of scope

- Batch “optimize library”
- Replacing global color-adjustment dialogs
- Training UI
