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
from System.IO import Path, File, Directory


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


def ArtifactCleaner(books):
    """Toggle artifact reduction for the current reader window."""
    try:
        from System.Windows.Forms import MessageBox, MessageBoxButtons, DialogResult
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

    ok = ComicRack.SetArtifactReductionEnabled(True, onnx)
    if ok:
        status = ""
        try:
            status = ComicRack.ArtifactReductionStatus or ""
        except Exception:
            pass
        msg = "Artifact reduction ON.\nModel: {0}\n{1}".format(onnx, status)
    else:
        status = ""
        try:
            status = ComicRack.ArtifactReductionStatus or ""
        except Exception:
            pass
        msg = (
            "Could not enable artifact reduction.\n{0}\n\n"
            "Reading continues unfiltered."
        ).format(status or "Unknown error")
    if MessageBox:
        MessageBox.Show(msg, "Artifact Cleaner")
    else:
        print(msg)
