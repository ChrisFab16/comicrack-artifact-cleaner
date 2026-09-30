# -*- coding: utf-8 -*-
"""Shared fixtures for representative FBCNN tests (display-only, non-destructive)."""
from __future__ import annotations

import hashlib
import io
import os
import shutil
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
WEIGHTS = REPO_ROOT / "weights" / "fbcnn_color.onnx"
CONTRACT_PIN = "a2b46206f6e705bc83dbc5641029b982e3d1ae0af1b1369f3792bee42088c9be"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


@pytest.fixture(scope="session")
def onnx_path():
    if not WEIGHTS.is_file():
        pytest.skip(f"missing {WEIGHTS} (gitignored) — export via harness first")
    return WEIGHTS


@pytest.fixture
def artifact_cleaner_onnx(tmp_path, onnx_path):
    """Copy pinned model under an ArtifactCleaner path (host allowlist shape)."""
    dest_dir = tmp_path / "Scripts" / "ArtifactCleaner" / "weights"
    dest_dir.mkdir(parents=True)
    dest = dest_dir / "fbcnn_color.onnx"
    shutil.copy2(onnx_path, dest)
    assert sha256_file(dest) == CONTRACT_PIN
    return dest


@pytest.fixture
def fake_cbz(tmp_path):
    """Minimal CBZ-like zip with one JPEG page (not a real comic; disposable)."""
    from PIL import Image

    page = Image.new("RGB", (64, 64), (40, 40, 40))
    # Add mild block structure so filter has something to change
    for y in range(0, 64, 8):
        for x in range(0, 64, 8):
            c = 80 + ((x + y) % 16) * 4
            for dy in range(8):
                for dx in range(8):
                    page.putpixel((x + dx, y + dy), (c, c // 2, c // 3))
    buf = io.BytesIO()
    page.save(buf, format="JPEG", quality=30)
    jpeg_bytes = buf.getvalue()

    cbz = tmp_path / "sample.cbz"
    with zipfile.ZipFile(cbz, "w", zipfile.ZIP_STORED) as zf:
        zf.writestr("000.jpg", jpeg_bytes)
    return cbz, jpeg_bytes
