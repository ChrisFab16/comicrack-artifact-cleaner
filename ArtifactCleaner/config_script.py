# -*- coding: utf-8 -*-
# config_script.py - Configure entry lives in artifact_cleaner.py (same Key).
# Kept so older installs that only copied this file still load a stub.
#@Name Artifact Cleaner Config
#@Key ArtifactCleaner
#@Hook ConfigScript
#@Description Configure Artifact Cleaner (models, download, performance)
#@Enabled true

from version import PLUGIN_VERSION

try:
    import debug_log as _dbg
except Exception:
    _dbg = None


def ConfigScript():
    """Fallback if artifact_cleaner.ConfigScript is not linked; prefer that entry."""
    try:
        if _dbg is not None:
            _dbg.write("ENTER", "config_script.py stub ConfigScript (fallback)")
    except Exception:
        pass
    try:
        import clr
        clr.AddReference("System.Windows.Forms")
        from System.Windows.Forms import MessageBox, MessageBoxButtons, MessageBoxIcon
        enabled = False
        status = ""
        try:
            enabled = bool(ComicRack.App.IsArtifactReductionEnabled)
            status = ComicRack.App.ArtifactReductionStatus or ""
        except Exception:
            pass
        owner = None
        try:
            owner = ComicRack.MainWindow
        except Exception:
            owner = None
        msg = (
            "Artifact Cleaner Config v{0}\n\n"
            "Status: {1}\n{2}\n\n"
            "Accelerator: DirectML GPU when available, else CPU.\n"
            "Toggle from the reader page context menu.\n"
            "Place fbcnn_color.onnx under Scripts/ArtifactCleaner/weights/."
            .format(PLUGIN_VERSION, "ON" if enabled else "OFF", status)
        )
        if owner is not None:
            MessageBox.Show(owner, msg, "Artifact Cleaner Config", MessageBoxButtons.OK, MessageBoxIcon.Information)
        else:
            MessageBox.Show(msg, "Artifact Cleaner Config", MessageBoxButtons.OK, MessageBoxIcon.Information)
        if _dbg is not None:
            _dbg.write("EXIT", "config_script.py stub MessageBox OK")
    except Exception as ex:
        try:
            if _dbg is not None:
                _dbg.write_exception("config_script.ConfigScript", ex)
        except Exception:
            pass
        try:
            from System.Windows.Forms import MessageBox
            MessageBox.Show("Config error: {0}".format(ex), "Artifact Cleaner Config")
        except Exception:
            print("Artifact Cleaner Config error: {0}".format(ex))
