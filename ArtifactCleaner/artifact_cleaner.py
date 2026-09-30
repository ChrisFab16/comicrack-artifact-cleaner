#@Name Artifact Cleaner (FBCNN)
#@Key ArtifactCleaner
#@Hook Books
#@Description Toggle FBCNN JPEG artifact reduction for the reader (display-only; never rewrites archives)
#@Enabled true
#@Image artifact_cleaner.png

# -*- coding: utf-8 -*-
# ASCII-safe. Calls host SetArtifactReductionEnabled (CE fork with page filter).

from version import PLUGIN_VERSION
import System
from System.IO import Path, File, FileStream, FileMode, FileAccess
from System.Security.Cryptography import SHA256


# Pins must match contracts/model-package.md (host FbcnnModelIntegrity is authoritative).
_PINNED_SHA256 = {
    "fbcnn_color.onnx": "a2b46206f6e705bc83dbc5641029b982e3d1ae0af1b1369f3792bee42088c9be",
    "fbcnn_color_manual.onnx": "a6a7d028232f4510d052f520c64e6c76a40e6a29e60ea16549322d80c9a1b206",
}


def _plugin_dir():
    try:
        return Path.GetDirectoryName(__file__)
    except Exception:
        return None


def _default_onnx_path():
    """Prefer weights beside plugin, then under AppData ArtifactCleaner."""
    base = _plugin_dir()
    candidates = []
    if base:
        candidates.append(Path.Combine(base, "weights", "fbcnn_color.onnx"))
        candidates.append(Path.Combine(base, "fbcnn_color.onnx"))
    try:
        appdata = System.Environment.GetFolderPath(
            System.Environment.SpecialFolder.ApplicationData
        )
        candidates.append(
            Path.Combine(
                appdata,
                "cYo",
                "ComicRack Community Edition",
                "ArtifactCleaner",
                "fbcnn_color.onnx",
            )
        )
    except Exception:
        pass
    for p in candidates:
        if p and File.Exists(p):
            return p
    return candidates[0] if candidates else None


def _host_supports_filter():
    try:
        return hasattr(ComicRack, "SetArtifactReductionEnabled")
    except Exception:
        return False


def _sha256_hex(path):
    fs = None
    sha = None
    try:
        fs = FileStream(path, FileMode.Open, FileAccess.Read)
        sha = SHA256.Create()
        digest = sha.ComputeHash(fs)
        parts = []
        for b in digest:
            parts.append("{0:x2}".format(int(b) & 0xFF))
        return "".join(parts)
    finally:
        if sha is not None:
            try:
                sha.Dispose()
            except Exception:
                pass
        if fs is not None:
            try:
                fs.Dispose()
            except Exception:
                pass


def _verify_model_integrity(path):
    """Pre-check (T047). Host still verifies. Returns (ok, error_message)."""
    if not path or not File.Exists(path):
        return False, "ONNX model file not found"
    name = Path.GetFileName(path)
    expected = _PINNED_SHA256.get(name)
    if not expected:
        return False, "Unrecognized model file name: {0}".format(name)
    try:
        actual = _sha256_hex(path)
    except Exception as ex:
        return False, "Could not hash model: {0}".format(ex)
    if actual.lower() != expected.lower():
        return False, "Model SHA-256 mismatch (corrupt or untrusted file)"
    return True, ""


def ArtifactCleaner(books):
    """Toggle artifact reduction for the current reader window."""
    try:
        from System.Windows.Forms import MessageBox
    except Exception:
        MessageBox = None

    if not _host_supports_filter():
        msg = (
            "Artifact Cleaner v{0}\n\n"
            "This ComicRack build does not expose SetArtifactReductionEnabled.\n"
            "Install a ChrisFab16/ComicRackCE build with the page-image filter."
        ).format(PLUGIN_VERSION)
        if MessageBox:
            MessageBox.Show(msg, "Artifact Cleaner")
        else:
            print(msg)
        return

    try:
        enabled = bool(ComicRack.IsArtifactReductionEnabled)
    except Exception:
        enabled = False

    if enabled:
        ok = ComicRack.SetArtifactReductionEnabled(False, None)
        msg = "Artifact reduction OFF." if ok else "Failed to disable artifact reduction."
        if MessageBox:
            MessageBox.Show(msg, "Artifact Cleaner")
        return

    onnx = _default_onnx_path()
    if not onnx or not File.Exists(onnx):
        msg = (
            "Artifact Cleaner v{0}\n\n"
            "ONNX model not found.\n"
            "Place fbcnn_color.onnx under:\n"
            "  Scripts/ArtifactCleaner/weights/\n"
            "or AppData/.../ArtifactCleaner/\n\n"
            "Expected:\n{1}"
        ).format(PLUGIN_VERSION, onnx or "(no path)")
        if MessageBox:
            MessageBox.Show(msg, "Artifact Cleaner")
        return

    ok_hash, hash_err = _verify_model_integrity(onnx)
    if not ok_hash:
        msg = (
            "Artifact Cleaner v{0}\n\n"
            "Model integrity check failed.\n{1}\n\n"
            "Reading continues unfiltered."
        ).format(PLUGIN_VERSION, hash_err)
        if MessageBox:
            MessageBox.Show(msg, "Artifact Cleaner")
        return

    ok = ComicRack.SetArtifactReductionEnabled(True, onnx)
    status = ""
    try:
        status = ComicRack.ArtifactReductionStatus or ""
    except Exception:
        pass
    if ok:
        msg = "Artifact reduction ON.\nModel: {0}\n{1}".format(onnx, status)
    else:
        msg = (
            "Could not enable artifact reduction.\n{0}\n\n"
            "Reading continues unfiltered."
        ).format(status or "Unknown error")
    if MessageBox:
        MessageBox.Show(msg, "Artifact Cleaner")
    else:
        print(msg)
