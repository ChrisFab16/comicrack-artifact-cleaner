# -*- coding: utf-8 -*-
"""FR-019 / SC-008: integrity pins and fail-closed without loading ORT."""
from __future__ import annotations

import re
from pathlib import Path

from conftest import CONTRACT_PIN, REPO_ROOT, sha256_file

CONTRACT = REPO_ROOT / "specs" / "001-fbcnn-reader-toggle" / "contracts" / "model-package.md"
PLUGIN = REPO_ROOT / "ArtifactCleaner" / "artifact_cleaner.py"


def test_contract_pin_matches_documented_blind_onnx():
    text = CONTRACT.read_text(encoding="utf-8")
    m = re.search(
        r"`fbcnn_color\.onnx` \(blind\):\s*`([0-9a-f]{64})`",
        text,
    )
    assert m, "blind onnx pin missing from model-package.md"
    assert m.group(1) == CONTRACT_PIN


def test_plugin_pins_match_contract():
    text = PLUGIN.read_text(encoding="utf-8")
    assert CONTRACT_PIN in text
    assert "fbcnn_color.onnx" in text


def test_weights_file_matches_pin_when_present():
    w = REPO_ROOT / "weights" / "fbcnn_color.onnx"
    if not w.is_file():
        import pytest

        pytest.skip("weights not present")
    assert sha256_file(w) == CONTRACT_PIN


def test_corrupt_file_does_not_match_pin(tmp_path):
    fake = tmp_path / "ArtifactCleaner" / "fbcnn_color.onnx"
    fake.parent.mkdir(parents=True)
    fake.write_bytes(b"not-an-onnx-model")
    assert sha256_file(fake) != CONTRACT_PIN


def test_path_allowlist_shape():
    """Mirror host FbcnnModelIntegrity.IsAllowedModelPath rules."""

    def allowed(p: str) -> bool:
        n = p.replace("/", "\\")
        marker = "\\ArtifactCleaner\\"
        end = "\\ArtifactCleaner"
        return marker.lower() in n.lower() or n.lower().endswith(end.lower())

    assert allowed(r"C:\Scripts\ArtifactCleaner\weights\fbcnn_color.onnx")
    assert allowed(r"C:\AppData\ArtifactCleaner\fbcnn_color.onnx")
    assert not allowed(r"C:\Temp\fbcnn_color.onnx")
    assert not allowed(r"C:\weights\fbcnn_color.onnx")
