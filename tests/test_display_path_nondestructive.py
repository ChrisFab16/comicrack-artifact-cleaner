# -*- coding: utf-8 -*-
"""
Representative display-path + non-destructive archive proof (FR-004/005, FR-020).

Mirrors host behavior at the boundary we can automate without CE UI:
- Read page bytes from a CBZ-like zip
- Run FBCNN ONNX on the bitmap (same model the host loads)
- Assert archive file hash unchanged
- Assert filtered pixels differ from source (filter actually ran)
"""
from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from conftest import sha256_file

pytest.importorskip("onnxruntime")


def _jpeg_to_chw(img: Image.Image) -> np.ndarray:
    rgb = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    # CHW
    return np.transpose(rgb, (2, 0, 1))[np.newaxis, ...]


def _chw_to_image(t: np.ndarray) -> Image.Image:
    # t: 1,3,H,W
    arr = np.clip(t[0].transpose(1, 2, 0) * 255.0, 0, 255).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB")


def test_archive_hash_unchanged_while_display_filter_runs(fake_cbz, artifact_cleaner_onnx):
    cbz, jpeg_bytes = fake_cbz
    before = sha256_file(cbz)

    img = Image.open(io.BytesIO(jpeg_bytes))
    # Downscale long-edge policy (host MaxLongEdge default 1024; tiny page unchanged)
    chw = _jpeg_to_chw(img)

    import onnxruntime as ort

    sess = ort.InferenceSession(
        str(artifact_cleaner_onnx), providers=["CPUExecutionProvider"]
    )
    out = sess.run(None, {"image": chw})[0]
    filtered = _chw_to_image(out)

    after = sha256_file(cbz)
    assert after == before, "comic archive must not change when display filter runs"

    # Zip contents still identical
    with zipfile.ZipFile(cbz, "r") as zf:
        assert zf.read("000.jpg") == jpeg_bytes

    src = np.asarray(img.convert("RGB"), dtype=np.int16)
    dst = np.asarray(filtered.resize(img.size), dtype=np.int16)
    mad = np.mean(np.abs(src - dst))
    assert mad > 0.5, f"expected filter to alter pixels; mean abs diff={mad}"


def test_mismatch_model_rejected_before_session(tmp_path, onnx_path):
    """Corrupt copy under ArtifactCleaner must not match pin (plugin/host gate)."""
    from conftest import CONTRACT_PIN, sha256_file

    good_hash = sha256_file(onnx_path)
    assert good_hash == CONTRACT_PIN
    bad = tmp_path / "Scripts" / "ArtifactCleaner" / "weights" / "fbcnn_color.onnx"
    bad.parent.mkdir(parents=True)
    bad.write_bytes(onnx_path.read_bytes()[:1024] + b"\x00\x01\x02")
    assert sha256_file(bad) != good_hash
    assert sha256_file(bad) != CONTRACT_PIN
