# Launch ComicRack CE (FBCNN) with script console + debug log tail.
# Usage (Git Bash):  bash scripts/launch-fbcnn-debug.sh
# Flags: -ssc = ShowScriptConsole (PythonCommand.EnableLog), -dso = DisableScriptOptimization

set -euo pipefail

EXE="${COMICRACK_FBCNN_EXE:-$LOCALAPPDATA/ComicRackCE-FBCNN/ComicRack.exe}"
# Git Bash: LOCALAPPDATA may be unset
if [[ ! -f "$EXE" ]]; then
  EXE="/c/Users/chris/AppData/Local/ComicRackCE-FBCNN/ComicRack.exe"
fi
WORKDIR="$(dirname "$EXE")"
LOG="/c/Users/chris/AppData/Roaming/cYo/ComicRack Community Edition/Scripts/ArtifactCleaner/artifact_cleaner_debug.log"
INI_DIR="/c/Users/chris/AppData/Roaming/cYo/ComicRack Community Edition"
INI="$INI_DIR/ComicRack.ini"

mkdir -p "$(dirname "$LOG")"
mkdir -p "$INI_DIR"

# Persist console for future launches without -ssc
if [[ ! -f "$INI" ]] || ! grep -q '^ShowScriptConsole' "$INI" 2>/dev/null; then
  {
    echo "; Auto-written by launch-fbcnn-debug.sh for Artifact Cleaner debugging"
    echo "ShowScriptConsole = true"
    echo "DisableScriptOptimization = true"
  } >> "$INI"
  echo "Updated $INI"
fi

# Fresh log for this session
: > "$LOG"
echo "Debug log: $LOG"
echo "Starting: $EXE -ssc -dso"
echo "After CE is up: open a book, then Preferences > Scripts > Artifact Cleaner > Configure"
echo "  or reader toolbar split-button Configure..."
echo "---"

# Kill stock/FBCNN if already running (optional quiet)
taskkill //IM ComicRack.exe //F >/dev/null 2>&1 || true
sleep 1

cd "$WORKDIR"
"$EXE" -ssc -dso &
CE_PID=$!
echo "ComicRack PID=$CE_PID"

# Tail log (also mirrors Script Console print lines we write)
echo "Tailing $LOG (Ctrl+C stops tail only; CE keeps running)"
# wait for file
for i in 1 2 3 4 5 6 7 8 9 10; do
  [[ -f "$LOG" ]] && break
  sleep 0.5
done
tail -n +1 -f "$LOG"
