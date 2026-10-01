# -*- coding: utf-8 -*-
"""FR-015: IronPython plugin sources must be ASCII-safe (or coding cookie on line 1-2)."""
from __future__ import annotations

from pathlib import Path

from conftest import REPO_ROOT

PLUGIN_DIR = REPO_ROOT / "ArtifactCleaner"


def _coding_cookie_ok(lines: list[bytes]) -> bool:
    cookie = b"coding"
    for line in lines[:2]:
        if cookie in line and (b"utf-8" in line.lower() or b"utf8" in line.lower()):
            return True
    return False


def test_plugin_py_files_ascii_or_coding_cookie_line_1_or_2():
    files = sorted(PLUGIN_DIR.glob("*.py"))
    assert files, "no ArtifactCleaner/*.py"
    failures = []
    for path in files:
        raw = path.read_bytes()
        lines = raw.splitlines()
        non_ascii = any(b > 127 for b in raw)
        if non_ascii and not _coding_cookie_ok(lines):
            failures.append(
                "{0}: non-ASCII bytes without # coding cookie on line 1-2".format(path.name)
            )
        # Prefer pure ASCII even with cookie (IronPython/CE lesson 2026-10-01)
        if non_ascii:
            bad_lines = [
                i
                for i, line in enumerate(lines, 1)
                if any(b > 127 for b in line)
            ]
            failures.append(
                "{0}: non-ASCII on lines {1} (use ASCII punctuation)".format(
                    path.name, bad_lines
                )
            )
    assert not failures, "\n".join(failures)


def test_plugin_entry_has_coding_cookie_on_line_1():
    """Match comicwiki pattern: cookie before #@ directives."""
    entry = PLUGIN_DIR / "artifact_cleaner.py"
    first = entry.read_bytes().splitlines()[0]
    assert b"coding" in first and b"utf-8" in first.lower()
