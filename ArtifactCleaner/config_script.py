#@Name Artifact Cleaner Config
#@Key ArtifactCleaner
#@Hook ConfigScript
#@Description Configure Artifact Cleaner (models, download, performance)
#@Enabled true

# -*- coding: utf-8 -*-

from version import PLUGIN_VERSION


def ConfigScript():
    """Placeholder ConfigScript -- full UI in US4 (T031)."""
    try:
        from System.Windows.Forms import MessageBox
        MessageBox.Show(
            "Artifact Cleaner Config v{0}\n\n"
            "Settings UI not implemented yet.\n"
            "Default: filter OFF; no archive writes.".format(PLUGIN_VERSION),
            "Artifact Cleaner Config"
        )
    except Exception:
        print("Artifact Cleaner Config v{0}".format(PLUGIN_VERSION))
