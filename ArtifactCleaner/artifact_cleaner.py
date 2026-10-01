# -*- coding: utf-8 -*-
#@Name Artifact Cleaner (FBCNN)
#@Key ArtifactCleaner
#@Hook Reader
#@Description Toggle FBCNN JPEG artifact reduction for the reader (display-only; never rewrites archives)
#@Enabled true
#@Image artifact_cleaner.png

# ASCII-safe source (IronPython 2.7). Reader toggle; host shows [ON]/[OFF].
# Never put "#@" sequences in comments: CE's Python parser matches them anywhere
# on the line and overwrites metadata (breaks Hook / HookType).

from version import PLUGIN_VERSION
import System
from System.IO import Path, File, FileStream, FileMode, FileAccess, FileShare
from System.Security.Cryptography import SHA256

try:
    import debug_log as _dbg
except Exception:
    _dbg = None


def _log(level, msg):
    try:
        if _dbg is not None:
            _dbg.write(level, msg)
            return
    except Exception:
        pass
    try:
        print("[{0}] {1}".format(level, msg))
    except Exception:
        pass


# Pins must match contracts/model-package.md (host FbcnnModelIntegrity is authoritative).
_PINNED_SHA256 = {
    "fbcnn_color.onnx": "a2b46206f6e705bc83dbc5641029b982e3d1ae0af1b1369f3792bee42088c9be",
    "fbcnn_color_manual.onnx": "a6a7d028232f4510d052f520c64e6c76a40e6a29e60ea16549322d80c9a1b206",
}

_log("LOAD", "artifact_cleaner.py execute begin file={0}".format(__file__))


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


def _app():
    """IApplication host surface (Library Organizer / Amazon pattern: ComicRack.App)."""
    try:
        return ComicRack.App
    except Exception as ex:
        _log("WARN", "ComicRack.App unavailable: {0}".format(ex))
        return None


def _host_supports_filter():
    try:
        app = _app()
        return app is not None and hasattr(app, "SetArtifactReductionEnabled")
    except Exception:
        return False


def _is_enabled():
    try:
        app = _app()
        return bool(app.IsArtifactReductionEnabled) if app is not None else False
    except Exception:
        return False


def _status_text():
    try:
        app = _app()
        return (app.ArtifactReductionStatus or "") if app is not None else ""
    except Exception:
        return ""


def _set_enabled(enabled, onnx_path):
    app = _app()
    if app is None:
        return False
    return bool(app.SetArtifactReductionEnabled(enabled, onnx_path))


def _sha256_hex(path):
    """SHA-256 hex (lowercase). Use :02x — IronPython rejects/misreads :x2."""
    fs = None
    sha = None
    try:
        fs = File.OpenRead(path)
        sha = SHA256.Create()
        digest = sha.ComputeHash(fs)
        parts = []
        for b in digest:
            parts.append("{0:02x}".format(int(b) & 0xFF))
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
        _log(
            "WARN",
            "SHA mismatch name={0} expected={1} actual={2}".format(
                name, expected.lower(), actual.lower()
            ),
        )
        return False, "Model SHA-256 mismatch (corrupt or untrusted file)"
    return True, ""


def _owner_window():
    """Dialog owner so MessageBox is not hidden behind CE / Preferences."""
    try:
        w = ComicRack.MainWindow
        _log("DEBUG", "MainWindow={0}".format(w))
        return w
    except Exception as ex:
        _log("WARN", "MainWindow unavailable: {0}".format(ex))
        return None


def _show(msg, title="Artifact Cleaner"):
    _log("UI", "MessageBox begin title={0} chars={1}".format(title, len(msg or "")))
    try:
        import clr
        clr.AddReference("System.Windows.Forms")
        from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon

        owner = _owner_window()
        if owner is not None:
            MessageBox.Show(owner, msg, title, MessageBoxButtons.OK, MessageBoxIcon.Information)
        else:
            MessageBox.Show(msg, title, MessageBoxButtons.OK, MessageBoxIcon.Information)
        _log("UI", "MessageBox returned OK title={0}".format(title))
    except Exception as ex:
        _log("ERROR", "MessageBox failed: {0}".format(ex))
        if _dbg is not None:
            try:
                _dbg.write_exception("MessageBox", ex)
            except Exception:
                pass
        try:
            print(msg)
        except Exception:
            pass


def ArtifactCleaner(books):
    """Toggle artifact reduction for the current reader window."""
    _log("ENTER", "ArtifactCleaner (Reader toggle) books={0}".format(
        None if books is None else getattr(books, "Length", len(books) if hasattr(books, "__len__") else "?")
    ))
    try:
        _log("DEBUG", "host_supports={0} enabled={1}".format(
            _host_supports_filter(), _is_enabled()
        ))
        if not _host_supports_filter():
            _show(
                "Artifact Cleaner v{0}\n\n"
                "This ComicRack build does not expose SetArtifactReductionEnabled.\n"
                "Install ChrisFab16/ComicRackCE with the page-image filter "
                "(branch 001-fbcnn-reader-toggle)."
                .format(PLUGIN_VERSION)
            )
            return

        if _is_enabled():
            ok = _set_enabled(False, None)
            _log("DEBUG", "SetArtifactReductionEnabled(False) -> {0}".format(ok))
            _show("Artifact reduction OFF." if ok else "Failed to disable artifact reduction.")
            return

        onnx = _default_onnx_path()
        _log("DEBUG", "onnx_path={0} exists={1}".format(
            onnx, bool(onnx and File.Exists(onnx))
        ))
        if not onnx or not File.Exists(onnx):
            _show(
                "Artifact Cleaner v{0}\n\n"
                "ONNX model not found.\n"
                "Place fbcnn_color.onnx under:\n"
                "  Scripts/ArtifactCleaner/weights/\n"
                "or AppData/.../ArtifactCleaner/\n\n"
                "Expected:\n{1}"
                .format(PLUGIN_VERSION, onnx or "(no path)")
            )
            return

        ok_hash, hash_err = _verify_model_integrity(onnx)
        _log("DEBUG", "integrity ok={0} err={1}".format(ok_hash, hash_err))
        if not ok_hash:
            _show(
                "Artifact Cleaner v{0}\n\n"
                "Model integrity check failed.\n{1}\n\n"
                "Reading continues unfiltered."
                .format(PLUGIN_VERSION, hash_err)
            )
            return

        ok = _set_enabled(True, onnx)
        status = _status_text()
        _log("DEBUG", "SetArtifactReductionEnabled(True) -> {0} status={1}".format(ok, status))
        if ok:
            # Host status includes active EP, e.g. "Artifact reduction on (DirectML)"
            _show(
                "Artifact reduction ON.\n"
                "Model: {0}\n"
                "{1}\n\n"
                "GPU (DirectML) is used when available; otherwise CPU."
                .format(onnx, status)
            )
        else:
            _show(
                "Could not enable artifact reduction.\n{0}\n\n"
                "Reading continues unfiltered."
                .format(status or "Unknown error")
            )
    except Exception as ex:
        _log("ERROR", "ArtifactCleaner crashed: {0}".format(ex))
        if _dbg is not None:
            try:
                _dbg.write_exception("ArtifactCleaner", ex)
            except Exception:
                pass
        _show("Artifact Cleaner error:\n{0}".format(ex))
        raise


#
# Configure (same Key as toggle so Preferences / menu Configure link works)
#
#@Name Artifact Cleaner Config
#@Key ArtifactCleaner
#@Hook ConfigScript
#@Description Configure Artifact Cleaner (model path, status)
#@Enabled true
def ConfigScript():
    """Minimal Configure until US4 UI (T031). Must not fail silently."""
    _log("ENTER", "ConfigScript begin")
    try:
        _log("DEBUG", "ComicRack type={0}".format(type(ComicRack)))
        try:
            attrs = []
            for name in (
                "MainWindow",
                "App",
                "ShowWebConfigure",
            ):
                attrs.append("{0}={1}".format(name, hasattr(ComicRack, name)))
            app = _app()
            if app is not None:
                for name in (
                    "SetArtifactReductionEnabled",
                    "IsArtifactReductionEnabled",
                    "ArtifactReductionStatus",
                ):
                    attrs.append("App.{0}={1}".format(name, hasattr(app, name)))
            _log("DEBUG", "host attrs: {0}".format(", ".join(attrs)))
        except Exception as ex:
            _log("WARN", "attr probe failed: {0}".format(ex))

        lines = [
            "Artifact Cleaner Config v{0}".format(PLUGIN_VERSION),
            "",
            "Display-only FBCNN JPEG artifact reduction (never rewrites archives).",
            "Accelerator: DirectML GPU when available, else CPU (host chooses on enable).",
            "",
            "Status: {0}".format("ON" if _is_enabled() else "OFF"),
        ]
        st = _status_text()
        if st:
            lines.append("Detail: {0}".format(st))
        onnx = _default_onnx_path()
        lines.append("")
        lines.append("Model path:")
        lines.append("  {0}".format(onnx or "(not found)"))
        if onnx and File.Exists(onnx):
            ok_hash, hash_err = _verify_model_integrity(onnx)
            lines.append(
                "Integrity: {0}".format("OK" if ok_hash else "FAIL - " + hash_err)
            )
        else:
            lines.append("Integrity: (no file)")
        lines.append("")
        lines.append("Host API: {0}".format(
            "available" if _host_supports_filter() else "MISSING - wrong CE build"
        ))
        lines.append("")
        lines.append("Toggle from the reader page context menu.")
        lines.append("Full settings UI (download / EP) lands in US4.")
        body = "\n".join(lines)
        _log("DEBUG", "ConfigScript about to _show chars={0}".format(len(body)))
        _show(body, "Artifact Cleaner Config")
        _log("EXIT", "ConfigScript end OK")
    except Exception as ex:
        _log("ERROR", "ConfigScript crashed: {0}".format(ex))
        if _dbg is not None:
            try:
                _dbg.write_exception("ConfigScript", ex)
            except Exception:
                pass
        try:
            _show("Artifact Cleaner Config error:\n{0}".format(ex), "Artifact Cleaner Config")
        except Exception:
            pass
        raise


_log("LOAD", "artifact_cleaner.py defs ready ConfigScript={0} ArtifactCleaner={1}".format(
    ConfigScript.__name__, ArtifactCleaner.__name__
))