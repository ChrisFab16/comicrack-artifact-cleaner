#!/usr/bin/env bash
# Build ArtifactCleaner.crplugin from the plugin folder.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python - "$ROOT" <<'PY'
import os, sys, zipfile
root = sys.argv[1]
src = os.path.join(root, "ArtifactCleaner")
out_dir = os.path.join(root, "crplugin")
os.makedirs(out_dir, exist_ok=True)
out = os.path.join(out_dir, "ArtifactCleaner.crplugin")
skip = {"config.xml"}
skip_dirs = {"__pycache__", "cache", "weights", "models"}
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zf:
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for name in filenames:
            if name.endswith(".pyc") or name in skip:
                continue
            full = os.path.join(dirpath, name)
            if "__pycache__" in full:
                continue
            rel = os.path.relpath(full, src)
            zf.write(full, rel.replace("\\", "/"))
print("Wrote", out)
PY
