#!/usr/bin/env bash
# Representative automated gate (FR-020 / SC-009) before operator Scenario A.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CE_ROOT="${COMICRACK_CE_ROOT:-$(cd "$ROOT/../ComicRackCE" 2>/dev/null && pwd || true)}"

echo "== Plugin pytest (integrity + display-path / archive hash) =="
cd "$ROOT"
python -m pip install -q -r tests/requirements.txt
python -m pytest tests/ -v --tb=short

if [[ -n "${CE_ROOT}" && -f "$CE_ROOT/ComicRack.Tests/ComicRack.Tests.csproj" ]]; then
  echo "== CE xUnit (FBCNN integrity + PageKey) =="
  export FBCNN_ONNX_PATH="${FBCNN_ONNX_PATH:-$ROOT/weights/fbcnn_color.onnx}"
  cd "$CE_ROOT"
  dotnet test ComicRack.Tests/ComicRack.Tests.csproj -c Debug --filter "FullyQualifiedName~Fbcnn|FullyQualifiedName~PageKeyFilter" --verbosity minimal
else
  echo "WARN: ComicRackCE not found beside plugin repo; skipped host xUnit"
fi

echo "OK: representative automated suite passed"
