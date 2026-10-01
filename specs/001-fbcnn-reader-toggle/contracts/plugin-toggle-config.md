# Contract: Plugin toggle and Configure

**Feature**: `001-fbcnn-reader-toggle` | **Owner**: this repo (IronPython plugin)

## Purpose

Expose user-facing enable/disable (per reader window), optional QF/strength, and ongoing Configure for model/download/performance — without rewriting comics.

## Hooks / entry points

| Surface | Role |
|---------|------|
| **`Reader`** (CE page context menu) | Toggle for **current reader window**; host shows `[ON]`/`[OFF]` + checkmark |
| `ConfigScript` (same `#@Key` as toggle) | Preferences → Plugins → Configure, or Configure… submenu under Reader item |
| `Books` / library Automation | **Not used** — this feature is reader-only |

### IronPython source rules (FR-015 / constitution II)

Same host trap as comicwiki and Library Organizer:

| Rule | Why |
|------|-----|
| Prefer **pure ASCII** in shipped `.py` | Unicode punctuation (em dash `\xe2\x80\x94`, smart quotes) → `Non-ASCII character ... no encoding declared` |
| Coding cookie on **line 1 or 2 only** if non-ASCII needed | IronPython ignores `# -*- coding: utf-8 -*-` on line 8+ |
| Cookie on **line 1**, then `#@` directives | Matches comicwiki entry scripts |
| Never put `#@Hook` / `#@Name` / other `#@…` in comments | CE `PythonPluginInitializer` `Regex.Match` matches anywhere on the line and overwrites metadata |

Automated gate: `tests/test_ironpython_ascii.py`.

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
| Download in progress | Progress UI with **Cancel**; cancel leaves feature off and reading unfiltered |
| Load/inference fail | Short reason; reading continues unfiltered |
| Pending filter (page) | Host shows non-blocking processing feedback while `PendingFilter`; clears on Ready/Failed/cancel |

## Out of scope

- Batch “optimize library”
- Replacing global color-adjustment dialogs
- Training UI
