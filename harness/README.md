# FBCNN ONNX export / latency harness

Offline CPython tools for Phase 2 model spike (T009–T010). **Not** loaded by ComicRack IronPython.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
pip install -r harness/requirements.txt
```

## Weights

Download upstream `fbcnn_color.pth` from [FBCNN releases](https://github.com/jiaxi-jiang/FBCNN/releases) into gitignored `weights/` (see root `.gitignore`).

## Commands (implemented in spike tasks)

- `python harness/export_fbcnn_onnx.py` — export `.pth` → `.onnx`
- Latency notes → `specs/001-fbcnn-reader-toggle/spike-model.md`

Place copyrighted sample crops under gitignored `testdata/`.
