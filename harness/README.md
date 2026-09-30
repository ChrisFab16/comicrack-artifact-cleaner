# FBCNN ONNX export / latency harness

Offline CPython tools for Phase 2 model spike (T009–T010). **Not** loaded by ComicRack IronPython.

## Setup

```bash
python -m venv .venv
source .venv/Scripts/activate   # Git Bash on Windows
pip install -r harness/requirements.txt
```

Clone upstream once (gitignored):

```bash
git clone --depth 1 https://github.com/jiaxi-jiang/FBCNN.git third_party/FBCNN
```

## Weights

Download upstream `fbcnn_color.pth` from [FBCNN releases](https://github.com/jiaxi-jiang/FBCNN/releases) into gitignored `weights/`.

## Commands

```bash
python harness/export_fbcnn_onnx.py --device cpu
python harness/bench_fbcnn_onnx.py --height 256 --width 256
```

Notes → `specs/001-fbcnn-reader-toggle/spike-model.md` / `spike-perf.md`.

Place copyrighted sample crops under gitignored `testdata/`.
