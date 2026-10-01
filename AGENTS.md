# comicrack-artifact-cleaner — project briefings

Global agent rules live in [`../AGENTS.md`](../AGENTS.md) (Codesync). This file adds **this-repo** context only.

## Repository identity

Dual deliverable: IronPython **Artifact Cleaner** plugin (this repo) + host page-image filter in fork **`ChrisFab16/ComicRackCE`** (FBCNN ONNX, display-only).

| Item | Value |
| ---- | ----- |
| Plugin package | `ArtifactCleaner/` (`Package.ini`, `artifact_cleaner.py`, weights) |
| Host | FBCNN build under `%LOCALAPPDATA%\ComicRackCE-FBCNN\` — **not** stock Program Files CE |
| Runtime | IronPython 2.7 inside ComicRack CE |
| Spec Kit feature | `.specify/feature.json` → `specs/001-fbcnn-reader-toggle` |

## Spec Kit

**ALWAYS use Spec Kit before editing product code** (plugin, host fork work tracked here, tests, packaging). Order: spec → plan → tasks → **analyze** → implement (Codesync `AGENTS.md` §5b / §24).

## IronPython / CE plugin source rules (FR-015)

Same failure class as **comicrack-comicwiki** and Library Organizer:

1. **Prefer pure ASCII** in all shipped `ArtifactCleaner/*.py` (no em dashes `—`, smart quotes, etc.).
2. If non-ASCII is unavoidable, put `# -*- coding: utf-8 -*-` on **line 1 or 2 only** — IronPython ignores a cookie later (Configure → `Non-ASCII character '\xe2' ... no encoding declared`).
3. Prefer cookie on **line 1**, then `#@Name` / `#@Hook` / … (comicwiki pattern).
4. **Never** put `#@Hook`, `#@Name`, or other `#@` sequences in comments — CE `PythonPluginInitializer` uses `Regex.Match` (anywhere on the line) and overwrites metadata (breaks HookType / Available Scripts / toolbar).

Gate: `tests/test_ironpython_ascii.py` (SC-010).

## Launch / install

- Operator must run **ComicRack CE (FBCNN)**, not Start Menu *ComicRack Community Edition* → Program Files (stock has no `#@Hook Reader` / no toolbar host).
- Scripts install: `%APPDATA%\cYo\ComicRack Community Edition\Scripts\ArtifactCleaner\`
- **Script Packages** listing ≠ **Available Scripts** — packages scan `Package.ini`; Available Scripts needs the host to accept the hook (`Reader` only in FBCNN build).

## Validation

- Plugin: `pytest` / `scripts/run-representative-tests.sh`
- Host: CE `ComicRack.Tests` FBCNN subset + operator quickstart (T021 still open for visual sign-off)
