"""Latency / smoke run for exported FBCNN ONNX (T010).

Creates a synthetic JPEG-like crop if testdata/ is empty, runs ORT CPU inference,
prints ms and peak RSS notes.
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def make_jpegish(h: int, w: int) -> np.ndarray:
    """Synthetic RGB float CHW in [0,1] with blocky pattern."""
    img = np.zeros((3, h, w), dtype=np.float32)
    for y in range(0, h, 8):
        for x in range(0, w, 8):
            v = ((x // 8) + (y // 8)) % 2
            img[:, y : y + 8, x : x + 8] = 0.3 + 0.4 * v
    noise = np.random.RandomState(0).randn(3, h, w).astype(np.float32) * 0.05
    return np.clip(img + noise, 0.0, 1.0)


def load_image_chw(path: Path, max_long: int | None) -> np.ndarray:
    from PIL import Image

    im = Image.open(path).convert("RGB")
    w, h = im.size
    if max_long and max(h, w) > max_long:
        scale = max_long / float(max(h, w))
        im = im.resize((max(1, int(w * scale)), max(1, int(h * scale))), Image.BICUBIC)
    arr = np.asarray(im).astype(np.float32) / 255.0
    return np.transpose(arr, (2, 0, 1))


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--onnx", type=Path, default=ROOT / "weights" / "fbcnn_color.onnx")
    p.add_argument("--image", type=Path, default=None, help="Optional RGB image under testdata/")
    p.add_argument("--height", type=int, default=256)
    p.add_argument("--width", type=int, default=256)
    p.add_argument("--max-long", type=int, default=0, help="Downscale long edge before infer (0=off)")
    p.add_argument("--runs", type=int, default=3)
    p.add_argument("--provider", default="CPUExecutionProvider")
    args = p.parse_args(argv)

    if not args.onnx.is_file():
        print("Missing ONNX: {0}".format(args.onnx), file=sys.stderr)
        return 1

    import onnxruntime as ort

    if args.image and args.image.is_file():
        chw = load_image_chw(args.image, args.max_long or None)
    else:
        chw = make_jpegish(args.height, args.width)

    batch = chw[np.newaxis, ...]
    print("input shape", batch.shape, "onnx", args.onnx)

    sess = ort.InferenceSession(str(args.onnx), providers=[args.provider])
    # warmup
    sess.run(None, {"image": batch})

    times = []
    for i in range(args.runs):
        t0 = time.perf_counter()
        outs = sess.run(None, {"image": batch})
        dt = (time.perf_counter() - t0) * 1000.0
        times.append(dt)
        qf = float(outs[1].reshape(-1)[0]) if len(outs) > 1 else float("nan")
        print("run {0}: {1:.1f} ms  qf_pred~{2:.3f}  out={3}".format(i + 1, dt, qf, outs[0].shape))

    times.sort()
    print(
        "summary: min={0:.1f} med={1:.1f} max={2:.1f} ms  provider={3}".format(
            times[0], times[len(times) // 2], times[-1], args.provider
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
