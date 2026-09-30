#@Name Artifact Cleaner (FBCNN)
#@Key ArtifactCleaner
#@Hook Books
#@Description Toggle FBCNN JPEG artifact reduction for the reader (display-only; never rewrites archives)
#@Enabled true
#@Image artifact_cleaner.png

# ASCII-safe entry (UTF-8 declared). Full toggle wires to host page filter in later tasks.
# -*- coding: utf-8 -*-

from version import PLUGIN_VERSION


def ArtifactCleaner(books):
    """Placeholder Books hook -- toggle UI lands in US1 (T019)."""
    try:
        from System.Windows.Forms import MessageBox
        MessageBox.Show(
            "Artifact Cleaner v{0}\n\n"
            "Host page-image filter required.\n"
            "Non-destructive: display cache only.".format(PLUGIN_VERSION),
            "Artifact Cleaner"
        )
    except Exception:
        print("Artifact Cleaner v{0} (host UI unavailable)".format(PLUGIN_VERSION))
